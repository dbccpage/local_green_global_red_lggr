"""Bounded laboratory host, causal evidence collection and deterministic replay.

Controller inputs are explicit public views. Evaluation-only truth is sent to
the independent judge AFTER the terminal decision. This is inspectable data
access separation, not an OS sandbox against malicious Python code.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from contextlib import closing
import json
from pathlib import Path
import threading
import time
import sqlite3
from .common import SharedBudget, BudgetExhausted, canonical, digest
from .evidence import EvidenceBook, EvidenceError, branch_event, verify_chain
from . import controller, tools

class Host:
    def __init__(self, case: dict, mode: str, development=None, native=None):
        self.case, self.mode = deepcopy(case), mode
        self.development, self.native = deepcopy(development), deepcopy(native)
        self.contract = deepcopy(case["public"]["contract"])
        self.active_versions = deepcopy(self.contract.get("required_versions",{}))
        self.budget = SharedBudget(self.contract["resource_limit"])
        self.plan = deepcopy((native or {}).get("plan",case["scenario"]["worker_proposals"]))
        self.initial_plan = deepcopy(self.plan)
        self.events, self.artifacts, self.decisions = [], {}, []
        self.observations, self.observation_records = {}, []
        self.exhausted_probes, self.failed_probes = set(), {}
        self.branch_outputs, self.arrival_events = {}, []
        self.state_path = [self.contract.get("baseline",0)]
        self.state_db = sqlite3.connect(":memory:")
        self.state_db.execute("CREATE TABLE laboratory_state(value INTEGER, effects INTEGER)")
        self.state_db.execute("INSERT INTO laboratory_state VALUES (?,0)",(self.state_path[0],))
        self.obligations, self.obligation_events = set(), []
        self.samples, self.transitions, self.unsupported_samples = [], [], []
        self.transition = deepcopy(case["scenario"].get("transition",{"kind":"none"}))
        self.event_error = None
        self.branches_executed = False
        self.missing_branches = []
        self.terminal = False
        self.blocked = False
        self.finished = False
        self.canary_effects = 0
        self.repair_attempts = 0
        self.probe_attempts = 0
        self.certificate_ns = 0
        self.branch_timings = []
        self.action, self.status, self.residual = "defer", "unknown", "unfinished"
        self.candidate = None
        self.local_verdicts = []
        self.run_id = digest({"input":case,"mode":mode})[:16]
        self.record("start","host",{"initial_report":self.initial_report(),"execution":"native-proposals" if native else "deterministic-fixture"})

    def initial_report(self):
        return {"operation":"ledger","schema":"coarse.v1",
                "orders":len(self.case["source"]["orders"]),"refunds":len(self.case["source"]["refunds"])}

    def artifact(self, name, data, source):
        key = f"artifact-{len(self.artifacts):03d}-{name}"
        self.artifacts[key] = {"data":deepcopy(data),"sha256":digest(data),"source":source}
        return {"id":key,"sha256":digest(data)}

    def record(self, kind, role, observed, *, inputs=(), outputs=(), consumption=0, signed_delta=0):
        seq = len(self.events)
        data = {"schema":"swarm-lab.event.v1","run_id":self.run_id,"event_id":f"event-{seq:04d}","seq":seq,
                "causal_parents":[self.events[-1]["event_id"]] if seq else [],
                "previous_sha256":self.events[-1]["event_sha256"] if seq else "0"*64,
                "kind":kind,"role":role,"agent_execution_mode":"native_codex_proposal" if self.native and kind in ("native-planner-response","native-worker-proposal") else "deterministic_fixture_or_host",
                "input_artifacts":list(inputs),"output_artifacts":list(outputs),
                "policy":self.contract.get("policy_version","policy.v1"),
                "versions":deepcopy(self.active_versions),"protected_contract_sha256":digest(self.contract),
                "report_schema":"refined.v2" if "semantics" in self.observations else "coarse.v1",
                "query":{"query_id":self.contract.get("query_id","ledger_reconciliation"),"scope":self.contract["query_scope"],"baseline":self.contract.get("baseline",0),"terminal":self.terminal},
                "observed":deepcopy(observed),"global_verdict":None,"global_verdict_source":None,
                "signed_state_change":signed_delta,"irreversible_consumption":consumption,
                "branch_attribution":role,"deduplication_rule":"issued attempt IDs once; retries new IDs",
                "retained_obligations":sorted(self.obligations),"authority_effect":"None",
                "coverage":"observed-so-far; application contract checked separately"}
        data["event_sha256"] = digest(data)
        self.events.append(data)
        return data

    def view(self):
        return {"contract":deepcopy(self.contract),"initial_report":self.initial_report(),
                "plan":deepcopy(self.plan),"observations":deepcopy(self.observations),
                "allowed_probes":list(self.case["public"]["allowed_probes"]),
                "state_path":list(self.state_path),"terminal":self.terminal,
                "obligations":sorted(self.obligations),"transition":deepcopy(self.transition),
                "global_samples":deepcopy(self.samples),"unsupported_samples":deepcopy(self.unsupported_samples),
                "branches_executed":self.branches_executed,"missing_branches":list(self.missing_branches),
                "event_error":self.event_error,"remaining_attempts":self.budget.remaining,
                "exhausted_probes":sorted(self.exhausted_probes)}

    def issue(self, kind, effect, branch="shared"):
        if self.blocked or self.finished:
            raise BudgetExhausted("host is blocked; next tool effect prevented")
        attempt = self.budget.reserve(kind,branch)
        self.record("attempt",branch,{"attempt":attempt},consumption=1)
        return effect()

    def probe(self, name):
        if name not in self.case["public"]["allowed_probes"]:
            raise ValueError("observation is not in this case's permitted tool set")
        self.probe_attempts += 1
        failure_count = self.case["scenario"].get("probe_failures",{}).get(name,0)
        def effect():
            # A failed tool still executed a SQLite query and consumed a permit.
            if self.failed_probes.get(name,0) < failure_count:
                with closing(tools.connection(self.case["source"])) as con:
                    con.execute("SELECT count(*) FROM orders").fetchone()
                self.failed_probes[name] = self.failed_probes.get(name,0)+1
                return {"tool_error":"fixture transient 503","attempt":self.failed_probes[name]}
            return tools.probe(name,self.case,self.branch_outputs)
        result = self.issue("probe:"+name,effect)
        ref = self.artifact(name,result,"sqlite.named_probe")
        self.record("observation","observer",{"probe":name,"result":result,"source":"sqlite.named_probe"},outputs=[ref])
        self.observation_records.append({"probe":name,"result":result,"source":"sqlite.named_probe"})
        if "tool_error" in result:
            if self.failed_probes[name] >= 3:
                self.exhausted_probes.add(name)
            return
        self.observations[name] = result
        if name == "migration":
            self.transitions.append({"from_version":self.transition.get("from_version","v1"),
                                     "to_version":self.transition.get("to_version","v1"),
                                     "evidence":result,"validated":result["validated"]})
            if result["validated"] and self.transition.get("kind") != "none":
                self.active_versions[self.transition["dimension"]] = self.transition["to_version"]
        if name == "obligation_evidence":
            for oid, evidence in result.items():
                if evidence["verified"] and oid in self.obligations:
                    self.obligations.remove(oid)
                    self.obligation_events.append({"op":"discharge","id":oid,"evidence":evidence})
                    self.record("discharge","host",{"id":oid,"evidence":evidence})

    def control(self):
        # Bounded by both attempt limit and decision limit. There is no unbounded
        # refinement retry when all available observations have been exhausted.
        for _ in range(self.contract["resource_limit"]+4):
            view = self.view()
            started = time.perf_counter_ns()
            decision = controller.decide(view,self.mode,controller.development_evidence(self.development))
            self.certificate_ns += time.perf_counter_ns()-started
            vref = self.artifact("controller-input",view,"explicit public controller view")
            dref = self.artifact("controller-output",decision,"controller.decide")
            self.decisions.append({"view":view,"decision":decision})
            self.record("decision","controller",{"action":decision["action"],"reason":decision["reason"],
                        "phase":"integrator-to-verifier" if self.terminal else "workers-to-integrator" if self.branches_executed else "orders-to-host" if self.branch_outputs else "planner-to-workers",
                        "findings":decision["findings"],"certificates":decision["certificates"],
                        "host_decision_scope":"local laboratory only"},inputs=[vref],outputs=[dref])
            act = decision["action"]
            if act == "proceed":
                return True
            if act == "probe":
                self.probe(decision["probe"])
                continue
            if act == "repair_plan":
                self.repair_attempts += 1
                old = self.artifact("prior-plan",self.plan,"retained proposal")
                self.issue("repair-plan",lambda: tools.probe("source_counts",self.case,self.branch_outputs))
                self.plan = deepcopy(decision["plan"])
                new = self.artifact("repaired-plan",self.plan,"observed metadata and declared contract")
                self.record("repair","planner",{"old_plan_retained":True,"contract_version":"refined.v2"},inputs=[old],outputs=[new])
                continue
            self.action = act
            self.status = "unknown" if act == "defer" else next((f["status"] for f in decision["findings"] if f["status"] != "unknown"),"obstructed")
            self.residual = decision["reason"]
            self.blocked = act == "block"
            return False
        self.action,self.status,self.residual = "defer","unknown","decision bound exhausted"
        return False

    def _branch_source(self, branch):
        keys = ("orders","customers") if branch == "orders" else ("refunds",)
        return {key:deepcopy(self.case["source"][key]) for key in keys}

    def _worker(self, branch, barrier=None):
        if barrier:
            barrier.wait(timeout=10)
        start = time.perf_counter_ns()
        output = tools.execute_branch(branch,self._branch_source(branch),self.plan)
        return output,{"branch":branch,"thread_id":threading.get_ident(),"started_ns":start,"finished_ns":time.perf_counter_ns()}

    def _accept_worker(self, branch, output, timing, step):
        self.canary_effects += 1
        self.branch_timings.append(timing)
        self.branch_outputs[branch] = output
        self.local_verdicts.append(int(output["local_pass"]))
        inp = self.artifact(branch+"-input",{"source":self._branch_source(branch),"planner":self.plan},"planner->worker")
        out = self.artifact(branch+"-output",output,"sqlite worker")
        path = self.case["scenario"].get("drift_path",[0,0,0])
        target_state = path[min(step,len(path)-1)]
        self.state_db.execute("UPDATE laboratory_state SET value=?,effects=effects+1",(target_state,))
        next_state = self.state_db.execute("SELECT value FROM laboratory_state").fetchone()[0]
        delta = next_state-self.state_path[-1]
        self.state_path.append(next_state)
        for ob in self.case["scenario"].get("obligations",[]):
            if ob.get("branch","orders") == branch:
                self.obligations.add(ob["id"])
                self.obligation_events.append({"op":"open","id":ob["id"],"evidence":None})
        self.record("worker-result",branch,{"local_verdict":output["local_pass"],"state":next_state,
                    "source":"sqlite.execute","source_slice":sorted(self._branch_source(branch))},inputs=[inp],outputs=[out],signed_delta=delta)

    def workers(self):
        path = self.case["scenario"].get("drift_path",[0,0,0])
        if len(set(path)) == 1 and self.budget.remaining >= 2:
            # Both permits reserved in stable order, both effects start behind a
            # barrier. Trace arrival order is separately exercised at the join.
            for branch in ("orders","refunds"):
                attempt = self.budget.reserve("worker",branch)
                self.record("attempt",branch,{"attempt":attempt},consumption=1)
            barrier = threading.Barrier(2)
            with ThreadPoolExecutor(max_workers=2) as pool:
                fs = {b:pool.submit(self._worker,b,barrier) for b in ("orders","refunds")}
                for i,b in enumerate(("orders","refunds"),1):
                    output,timing = fs[b].result()
                    self._accept_worker(b,output,timing,i)
        else:
            # A nonzero shared state transition is causally ordered. A prefix
            # failure stops before the next worker/tool, tested by the canary.
            for i,b in enumerate(("orders","refunds"),1):
                if i>1 and self.mode != "A" and self.contract["query_scope"] == "every_prefix" and any(abs(x-self.state_path[0])>self.contract["max_total"] for x in self.state_path):
                    self.control()
                    return False
                output,timing = self.issue("worker",lambda:self._worker(b),b)
                self._accept_worker(b,output,timing,i)
        self.branches_executed = True
        return True

    def merge(self):
        scenario = self.case["scenario"]
        samples = []
        for raw in scenario.get("negative_evidence",[]):
            # Materialize the auxiliary fixture contract in SQLite. This is a
            # constructed negative observation, NOT hidden ledger correctness.
            def aux_effect(raw=raw):
                con = tools.connection({})
                try:
                    con.execute("CREATE TABLE auxiliary(query_id TEXT, verdict INTEGER)")
                    con.execute("INSERT INTO auxiliary VALUES (?,?)",(raw["query_id"],int(raw.get("global_verdict",False))))
                    return bool(con.execute("SELECT verdict FROM auxiliary").fetchone()[0])
                finally:
                    con.close()
            verdict = self.issue("auxiliary-query",aux_effect,"refunds")
            sample = {"query_id":raw["query_id"],"scope":raw.get("scope","endpoint"),"baseline":raw.get("baseline",0),
                      "verdict":verdict,"source":"sqlite.branch_contract","terminal":raw.get("terminal",True)}
            samples.append(sample)
            if raw.get("obligation_id"):
                self.obligations.add(raw["obligation_id"])
                self.obligation_events.append({"op":"open","id":raw["obligation_id"],"evidence":None})
        for extra in scenario.get("extra_branch_costs",[]):
            count = extra.get("attempts",extra.get("cost",1)) if isinstance(extra,dict) else int(extra)
            branch = extra.get("branch","refunds") if isinstance(extra,dict) else "refunds"
            for _ in range(count):
                self.issue("branch-extra-query",lambda:tools.probe("source_counts",self.case,self.branch_outputs),branch)
        policy = self.contract.get("policy_version","policy.v1")
        root = branch_event("plan",{"attempts":[a for a in self.budget.attempts if a["branch"] == "shared"]},policy_version=policy,role="planner")
        branch_events = {}
        for b in ("orders","refunds"):
            branch_obligations = [o["id"] for o in scenario.get("obligations",[]) if o.get("branch","orders")==b]
            branch_events[b] = branch_event(b,{"artifact":self.branch_outputs[b],"obligations":branch_obligations,
                  "global_samples":samples if b=="refunds" else [],"attempts":[a for a in self.budget.attempts if a["branch"]==b]},
                  parents=["plan"],policy_version=policy,role=b)
        arrivals = [root]
        for label in scenario.get("arrival_plan",["orders","refunds"]):
            # Duplicate labels are repeated delivery, not duplicate execution.
            if label in branch_events:
                arrivals.append(deepcopy(branch_events[label]))
            elif label in ("plan","planner"):
                arrivals.append(deepcopy(root))
            elif label.startswith("tamper"):
                bad = deepcopy(branch_events["orders"])
                bad["payload"]["artifact"]["local_pass"] = False
                arrivals.append(bad)
        if scenario.get("empty_later_obligation_report"):
            parents = sorted({e["event_id"] for e in arrivals if e["event_id"] in ("orders","refunds")})
            arrivals.append(branch_event("later-empty-report",{"obligations":[]},parents=parents,policy_version=policy,role="integrator"))
        self.arrival_events = [{"event_id":e["event_id"],"parent_ids":e["parent_ids"],"payload_hash":e["payload_hash"],"role":e["role"]} for e in arrivals]
        book = EvidenceBook(self.contract)
        try:
            merged = book.merge(arrivals)
            seen = {e["event_id"] for e in merged["ordered"]}
            self.missing_branches = [b for b in ("orders","refunds") if b not in seen]
            self.obligations |= set(merged["obligations"])
            self.samples = merged["global_samples"]
            self.unsupported_samples = merged.get("unsupported",[])
            self.record("branch-merge","integrator",{"merged":merged,"arrival_order":[e["event_id"] for e in arrivals],
                        "global_sample_interpretation":"retained original query, scope and baseline; no ledger verdict inferred"})
        except EvidenceError as error:
            self.event_error = str(error)
            self.record("merge-rejected","integrator",{"error":str(error)})

    def run(self, before_workers=None):
        started = time.perf_counter_ns()
        try:
            self.issue("planner",lambda:tools.probe("source_counts",self.case,{}))
            if self.native:
                planner_input, planner_response = self.native["planner_input"], self.native["planner_response"]
                if planner_response.get("input_sha256") != digest(planner_input):
                    raise EvidenceError("native planner did not bind its actual input")
                if planner_response.get("plan") != self.plan:
                    raise EvidenceError("native planner response and proposed plan differ")
                iref = self.artifact("planner-native-input",planner_input,"host planner handoff")
                oref = self.artifact("planner-native-response",planner_response,"native agent raw response")
                self.record("native-planner-response","planner",{"raw_response":planner_response},inputs=[iref],outputs=[oref])
            plan_ref = self.artifact("planner",self.plan,"native proposal" if self.native else "deterministic fixture planner")
            self.record("proposal","planner",{"bounded_operations":self.plan,"original_source_access":"planner sees counts; workers receive their source slice and this artifact"},outputs=[plan_ref])
            ready = self.control()
            if ready and self.native:
                responses = before_workers(self) if before_workers else self.native.get("worker_responses")
                if responses:
                    self.native["worker_responses"] = deepcopy(responses)
                    handoff_plan = deepcopy(self.plan)
                    for branch in ("orders","refunds"):
                        response = responses[branch]
                        public_input = {"branch":branch,"source":self._branch_source(branch),"planner":handoff_plan,
                                        "observed_semantics":self.observations.get("semantics"),"task":self.case["public"]["task"]}
                        if response.get("input_sha256") != digest(public_input):
                            raise EvidenceError("native worker did not bind its actual upstream artifact")
                        iref = self.artifact(branch+"-native-input",public_input,"host handoff")
                        oref = self.artifact(branch+"-native-response",response,"native agent raw response")
                        self.record("native-worker-proposal",branch,{"raw_response":response},inputs=[iref],outputs=[oref])
                        self.plan[branch] = deepcopy(response["operation"])
                    ready = self.control()
            if ready and self.workers():
                self.merge()
                if self.control():
                    self.candidate = self.issue("integrate",lambda:tools.integrate(self.branch_outputs,self.plan["integrator"]),"integrator")
                    self.canary_effects += 1
                    ref = self.artifact("candidate-ledger",self.candidate,"sqlite.integrate")
                    self.record("candidate","integrator",{"local_verdict":True,"rows":len(self.candidate)},outputs=[ref])
                    self.local_verdicts.append(1)
                    self.terminal = True
                    if self.control():
                        self.action,self.status,self.residual = "commit",("observed-so-far" if self.mode=="A" else "verified-on-declared-domain"),"none"
        except BudgetExhausted as error:
            self.action,self.status,self.residual = "defer","unknown",str(error)
            self.record("budget-stop","host",{"reason":str(error),"next_tool_prevented":True})
        except (EvidenceError,ValueError,KeyError,TypeError,sqlite3.Error,OverflowError) as error:
            self.action,self.status,self.residual = "block","malformed",str(error)
            self.blocked = True
            self.record("malformed-stop","host",{"reason":str(error)})
        self.record("terminal-decision","host",{"action":self.action,"status":self.status,"residual":self.residual,"lab_only":True})
        self.finished = True
        summary = {"action":self.action,"state_path":self.state_path,"attempts":self.budget.attempts,
                   "observations":self.observation_records,"obligation_events":self.obligation_events,
                   "transitions":self.transitions,"arrival_events":self.arrival_events,
                   "negative_evidence":self.samples,"candidate_rows":self.candidate}
        # First evaluation-only import/use occurs AFTER the host's decision.
        from .oracle import judge
        judgment = judge(self.case,self.candidate if self.action=="commit" else None,summary)
        eg = judgment["task_correct"]
        local_product = int(all(self.local_verdicts)) if self.local_verdicts else None
        defect = eg-local_product if eg is not None and local_product is not None else None
        first_event = next((e for e in self.events if e["kind"]=="decision" and
                          (e["observed"]["action"]=="repair_plan" or any(f["status"] in ("obstructed","malformed","unsupported") for f in e["observed"]["findings"]))),None)
        first = first_event["seq"] if first_event else None
        run = {"schema":"swarm-lab.run.v1","run_id":self.run_id,"mode":self.mode,
               "execution_mode":"native-proposals-host-executed" if self.native else "deterministic-fault-injection",
               "input":self.case,"input_sha256":digest(self.case),"development":self.development,"native":self.native,
               "events":self.events,"artifacts":self.artifacts,"decisions":self.decisions,"summary":summary,
               "action":self.action,"status":self.status,"residual":self.residual,"output":self.candidate if self.action=="commit" else None,
               "candidate":self.candidate,"judgment":judgment,"local_verdicts":self.local_verdicts,"global_verdict":eg,
               "defect":defect,"defect_kind":{None:"UNKNOWN",-1:"NGD",0:"ZDR",1:"PGD"}[defect],
               "metrics":{"attempts":len(self.budget.attempts),"probe_attempts":self.probe_attempts,"repair_attempts":self.repair_attempts,
                          "successful_repairs":int(self.repair_attempts>0 and eg is True),"canary_effects":self.canary_effects,
                          "detection_step":first,"first_faulty_handoff":None,
                          "first_detecting_boundary":first_event["observed"]["phase"] if first_event else None,
                          "localization_status":"detecting boundary measured; first causal fault origin unmeasured",
                          "first_evidence_request_step":next((e["seq"] for e in self.events if e["kind"]=="decision" and e["observed"]["action"]=="probe"),None),
                          "certificate_consumed_decisions":sum(bool(d["decision"].get("certificate_consumed")) for d in self.decisions),
                          "elapsed_ns":time.perf_counter_ns()-started,"controller_and_certificate_ns":self.certificate_ns,
                          "model_tokens":None,"model_cost":None,"model_usage_status":"unmeasured"},
               "branch_execution":self.branch_timings,
               "authority_effect":"None","evaluation_access":"judge called after terminal host decision; not in any controller view"}
        run["metrics"]["evidence_bytes"] = len(canonical({"events":self.events,"artifacts":self.artifacts}).encode())
        run["metrics"]["initial_report_bytes"] = len(canonical(self.initial_report()).encode())
        run["metrics"]["final_report_bytes"] = len(canonical({"base":self.initial_report(),"semantics":self.observations.get("semantics")}).encode())
        self.state_db.close()
        run["replay_fingerprint"] = replay_fingerprint(run)
        return run

def replay_fingerprint(run):
    return digest({k:run[k] for k in ("input_sha256","mode","events","artifacts","decisions","summary","action","status","residual","output","judgment","local_verdicts","global_verdict","defect")})

def run_case(case: dict, mode: str, development=None, native=None) -> dict:
    return Host(case,mode,development,native).run()

def replay(run_or_path) -> dict:
    run = json.loads(Path(run_or_path).read_text(encoding="utf-8")) if isinstance(run_or_path,(str,Path)) else deepcopy(run_or_path)
    verify_chain(run)
    if replay_fingerprint(run) != run["replay_fingerprint"]:
        raise EvidenceError("stored decision content changed")
    regenerated = run_case(run["input"],run["mode"],run.get("development"),run.get("native"))
    if regenerated["replay_fingerprint"] != run["replay_fingerprint"]:
        raise EvidenceError("fresh tool/decision/oracle replay differs")
    return {"replayed":True,"action":run["action"],"admitted":run["action"]=="commit","run_id":run["run_id"],
            "meaning":"successful replay preserves negative/deferred decisions; it does not grant admission"}
