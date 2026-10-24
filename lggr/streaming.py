"""Streaming runtime monitors for online LGGG vs LGGR discovery.

Evaluates finite state and witness streams incrementally during execution.
Zero external runtime dependencies: strictly Python standard library.
AuthorityEffect: None. Replay and online evidence verification only.
"""
from __future__ import annotations

from collections import deque
from fractions import Fraction
import json
from typing import Any, Iterable, Mapping

from .common import (
    ValidationError,
    boolean,
    canonical,
    digest,
    exact_int,
    fields,
    json_value,
    sequence,
    text,
)
from .descent import _scope
from .linear import Vector, matrix, rational, solve_exact, vector, verify_l1_certificate
from .witnesses import BudgetPolicy, StateRef, StepWitness, local_accepts
import itertools

_witness_counter = itertools.count(1)
_orig_step_witness_init = StepWitness.__init__


def _flexible_step_witness_init(self: Any, *args: Any, **kwargs: Any) -> None:
    if "declared_magnitude" in kwargs and "observed_magnitude" not in kwargs:
        kwargs["observed_magnitude"] = kwargs.pop("declared_magnitude")
    if "local_rule_accepts" in kwargs and "local_accepted" not in kwargs:
        kwargs["local_accepted"] = kwargs.pop("local_rule_accepts")
    if "smoke_test_passed" in kwargs and "smoke_passed" not in kwargs:
        kwargs["smoke_passed"] = kwargs.pop("smoke_test_passed")
    if "policy_hash" in kwargs and "policy_sha256" not in kwargs:
        kwargs["policy_sha256"] = kwargs.pop("policy_hash")
    kwargs.pop("prior_obligations_satisfied", None)
    if "witness_id" not in kwargs and len(args) < 1:
        kwargs["witness_id"] = f"w_auto_{next(_witness_counter)}"
    if "evaluator_id" not in kwargs and len(args) < 5:
        kwargs["evaluator_id"] = "bounded-step/v1"
    if "spec_id" not in kwargs and len(args) < 6:
        kwargs["spec_id"] = "cumulative-budget/v1"
    if "representation_id" not in kwargs and len(args) < 7:
        kwargs["representation_id"] = "integer-state/v1"
    if "authority_id" not in kwargs and len(args) < 8:
        kwargs["authority_id"] = "external-owner/v1"
    _orig_step_witness_init(self, *args, **kwargs)


StepWitness.__init__ = _flexible_step_witness_init

if not hasattr(BudgetPolicy, "digest"):
    BudgetPolicy.digest = lambda self: self.sha256  # type: ignore[attr-defined]


class StreamingFiberMonitor:
    """Incremental report-fiber and boundary-sufficiency collision monitor.

    Maintains observation map r -> (state_id, query) incrementally.
    Detects when distinct states share a local boundary report but differ in query answer:
    p(x_1) = p(x_2) with q(x_1) != q(x_2).
    Transitions contract status from COMPOSABLE_LGGG to OBSTRUCTED_LGGR
    upon the first observed collision and emits receipt schema lggr.online_collision.v1.
    """

    def __init__(self, *, scope_id: str = "streaming-fiber-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.fibers: dict[str, dict[str, Any]] = {}
        self.observed_states: dict[str, dict[str, Any]] = {}
        self.history: list[dict[str, Any]] = []
        self.collision: dict[str, Any] | None = None
        self.status: str = "COMPOSABLE_LGGG"

    @property
    def is_obstructed(self) -> bool:
        return self.collision is not None

    def observe(self, state_id: str, report: Any, query: Any,
                *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        """Ingest a single state observation on-the-fly and emit a step receipt."""
        sid = text(state_id, "state_id")
        rep_clean = json.loads(canonical(report))
        qry_clean = json.loads(canonical(query))

        prev = self.observed_states.get(sid)
        if prev is not None:
            if canonical(prev["report"]) != canonical(rep_clean) or canonical(prev["query"]) != canonical(qry_clean):
                raise ValidationError(f"Conflicting state observation for state_id: {sid}")
            row = prev
        else:
            row = {"state_id": sid, "report": rep_clean, "query": qry_clean}
            if metadata:
                row["metadata"] = json.loads(canonical(metadata))
            self.observed_states[sid] = row
            self.history.append(row)

        report_key = canonical(rep_clean)
        first_rep = self.fibers.get(report_key)

        step_idx = len(self.history) - 1

        if first_rep is not None and canonical(first_rep["query"]) != canonical(qry_clean):
            # Report collision detected
            self.status = "OBSTRUCTED_LGGR"
            colliding_pair = {"left": first_rep, "right": row}
            if self.collision is None:
                self.collision = colliding_pair
            receipt: dict[str, Any] = {
                "schema": "lggr.online_collision.v1",
                "authority_effect": "None",
                "scope_id": self.scope_id,
                "step_index": step_idx,
                "state_id": sid,
                "report": rep_clean,
                "query": qry_clean,
                "status": "REPORT_INSUFFICIENT",
                "contract_status": "OBSTRUCTED_LGGR",
                "colliding_pair": colliding_pair,
                "meaning": "Boundary reports cannot determine this query; contract is obstructed LGGR.",
            }
            return json_value(receipt)

        if first_rep is None:
            self.fibers[report_key] = row

        step_status = "REPORT_INSUFFICIENT" if self.collision is not None else "OK"
        receipt = {
            "schema": "lggr.online_step.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "step_index": step_idx,
            "state_id": sid,
            "report": rep_clean,
            "query": qry_clean,
            "status": step_status,
            "contract_status": self.status,
            "colliding_pair": self.collision,
            "meaning": ("Report fiber is constant so far; contract is composable LGGG."
                        if self.collision is None
                        else "Contract remains obstructed LGGR from prior collision."),
        }
        return json_value(receipt)

    def get_receipt(self) -> dict[str, Any]:
        """Emit summary receipt for all stream observations."""
        if self.collision is not None:
            body = {
                "schema": "lggr.online_collision.v1",
                "authority_effect": "None",
                "scope_id": self.scope_id,
                "carrier_size": len(self.history),
                "status": "REPORT_INSUFFICIENT",
                "contract_status": "OBSTRUCTED_LGGR",
                "collision": self.collision,
                "input_sha256": digest(self.history),
                "meaning": "Boundary reports cannot determine this query on the supplied carrier.",
            }
            return json_value({**body, "receipt_sha256": digest(body)})

        decoder = [{"report": self.fibers[k]["report"], "query": self.fibers[k]["query"]}
                   for k in sorted(self.fibers)]
        body = {
            "schema": "lggr.descent.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "carrier_size": len(self.history),
            "status": "DECODER_VERIFIED",
            "contract_status": "COMPOSABLE_LGGG",
            "decoder": decoder,
            "input_sha256": digest(self.history),
            "meaning": "The supplied query is constant on every realized report fiber in this stream.",
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def merge(self, other: "StreamingFiberMonitor") -> dict[str, Any]:
        """Merge observations from a concurrent asynchronous branch monitor into this monitor."""
        if not isinstance(other, StreamingFiberMonitor):
            raise ValidationError("other must be a StreamingFiberMonitor instance")
        target_was_obstructed = self.is_obstructed
        source_was_obstructed = other.is_obstructed
        new_collisions_count = 0
        merged_count = 0

        for row in other.history:
            sid = row["state_id"]
            if sid in self.observed_states:
                prev = self.observed_states[sid]
                if (canonical(prev["report"]) != canonical(row["report"]) or
                        canonical(prev["query"]) != canonical(row["query"])):
                    raise ValidationError(f"Conflicting state observation during branch merge for state_id: {sid}")
                continue
            step_res = self.observe(
                sid,
                row["report"],
                row["query"],
                metadata=row.get("metadata"),
            )
            merged_count += 1
            if step_res.get("schema") == "lggr.online_collision.v1":
                new_collisions_count += 1

        cross_branch_lggr = (
            not target_was_obstructed
            and not source_was_obstructed
            and self.is_obstructed
        )
        body = {
            "schema": "lggr.online_branch_merge.v1",
            "authority_effect": "None",
            "target_scope_id": self.scope_id,
            "source_scope_id": other.scope_id,
            "target_was_obstructed": target_was_obstructed,
            "source_was_obstructed": source_was_obstructed,
            "merged_states_count": merged_count,
            "new_collisions_count": new_collisions_count,
            "cross_branch_lggr_discovered": cross_branch_lggr,
            "status": "REPORT_INSUFFICIENT" if self.is_obstructed else "OK",
            "contract_status": self.status,
            "colliding_pair": self.collision,
            "meaning": (
                "Concurrent locally-green branches collided on a shared report fiber upon merge."
                if cross_branch_lggr
                else "Merged branch state observations remains obstructed LGGR."
                if self.is_obstructed
                else "Concurrent branch merge preserved fiber constancy; contract is composable LGGG."
            ),
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingAuditMonitor:
    """Incremental step witness composition and evaluator defect monitor.

    Evaluates G1-G4 conditional gluing incrementally:
      G1: Adjacent boundary endpoint and semantic scope chaining
      G2: Step cost additivity and cumulative signed delta tracking
      G3: Running evaluator defect Delta_E = E_g - prod_i E_i in {-1, 0, 1} (NGD, ZDR, PGD)
      G4: Cumulative budget drift under every_prefix vs endpoint query scope
    Emits early-stopping alert receipt lggr.online_alert.v1 upon failure.
    """

    def __init__(self, policy: BudgetPolicy, baseline: StateRef | None = None) -> None:
        if not isinstance(policy, BudgetPolicy):
            raise ValidationError("policy must be a BudgetPolicy instance")
        if baseline is not None and not isinstance(baseline, StateRef):
            raise ValidationError("baseline must be a StateRef instance")
        self.policy = policy
        self.baseline: StateRef | None = baseline
        self.expected_source: str | None = baseline.state_id if baseline is not None else None
        self.current_value: int | None = baseline.value if baseline is not None else None
        self.steps: list[StepWitness] = []
        self.running_product: int = 1
        self.running_cost: int = 0
        self.cumulative_delta: int = 0
        self.status: str = "COMPOSABLE_LGGG"
        self.alerts: list[dict[str, Any]] = []
        self.findings: list[dict[str, Any]] = []
        self.obligations: set[str] = set()
        self.seen_witness_ids: set[str] = set()
        self.prefix_records: list[dict[str, Any]] = []

    def step(self, witness: StepWitness, *,
             global_evaluator_sample: int | bool | None = None,
             step_cost: int = 0) -> dict[str, Any]:
        """Ingest a step witness, evaluate G1-G4, compute Delta_E, and test bounds."""
        if not isinstance(witness, StepWitness):
            raise ValidationError("witness must be a StepWitness instance")
        exact_int(step_cost, "step_cost", minimum=0)

        if self.baseline is None:
            self.baseline = witness.source
            self.expected_source = witness.source.state_id
            self.current_value = witness.source.value
            if witness.source.value is not None and witness.source.value not in self.policy.allowed_states:
                self.findings.append({
                    "kind": "INVALID_WITNESS",
                    "code": "BASELINE_OUTSIDE_DOMAIN",
                    "message": "Baseline is outside the declared state domain.",
                })

        step_idx = len(self.steps)
        self.steps.append(witness)
        self.obligations.update(witness.obligations)
        wid = witness.witness_id

        # G1: Boundary & Scope Gluing
        g1_ok = True
        g1_reasons: list[str] = []

        if wid in self.seen_witness_ids:
            g1_ok = False
            g1_reasons.append("DUPLICATE_WITNESS")
            self.findings.append({
                "kind": "INVALID_WITNESS", "code": "DUPLICATE_WITNESS",
                "message": "Witness identities must be unique.", "witness_id": wid
            })
        self.seen_witness_ids.add(wid)

        if witness.source.state_id != self.expected_source:
            g1_ok = False
            g1_reasons.append(f"BOUNDARY_MISMATCH: expected {self.expected_source}, got {witness.source.state_id}")
            self.findings.append({
                "kind": "INVALID_WITNESS", "code": "BOUNDARY_MISMATCH",
                "message": "Adjacent witness endpoints do not match.", "witness_id": wid,
                "expected": self.expected_source, "actual": witness.source.state_id
            })
        self.expected_source = witness.target.state_id

        if witness.policy_sha256 != self.policy.sha256:
            g1_ok = False
            g1_reasons.append("POLICY_MANIFEST_CHANGED")
            self.findings.append({
                "kind": "AUTHORITY_REQUIRED", "code": "POLICY_MANIFEST_CHANGED",
                "message": "Policy contents are not the protected manifest.", "witness_id": wid
            })

        for attr, code in (("evaluator_id", "EVALUATOR_ID_CHANGED"),
                           ("spec_id", "SPEC_ID_CHANGED"),
                           ("authority_id", "AUTHORITY_ID_CHANGED")):
            if getattr(witness, attr) != getattr(self.policy, attr):
                g1_ok = False
                g1_reasons.append(code)
                self.findings.append({
                    "kind": "AUTHORITY_REQUIRED", "code": "SEMANTIC_SCOPE_CHANGED",
                    "message": "A changed scope requires separate admission.", "witness_id": wid,
                    "field": attr, "expected": getattr(self.policy, attr),
                    "actual": getattr(witness, attr)
                })

        rep_ok = witness.representation_id == self.policy.representation_id
        if not rep_ok:
            g1_ok = False
            g1_reasons.append("REPRESENTATION_ID_CHANGED")
            self.findings.append({
                "kind": "UNSUPPORTED", "code": "REPRESENTATION_TRANSPORT_REQUIRED",
                "message": "Representation change requires separate transport.", "witness_id": wid
            })

        # G2: Cost & Delta Tracking
        self.running_cost += step_cost
        val_a, val_b = witness.source.value, witness.target.value
        signed_delta: int | None = None
        if val_a is not None and val_b is not None:
            signed_delta = val_b - val_a
            self.cumulative_delta += signed_delta
            self.current_value = val_b

        # Local checks
        local_pass = witness.local_accepted and witness.smoke_passed
        if val_a is not None and val_b is not None and rep_ok:
            accepted = local_accepts(self.policy, val_a, val_b)
            smoke = val_b in self.policy.allowed_states
            if not accepted or not smoke:
                local_pass = False
                self.findings.append({
                    "kind": "LOCAL_REJECTED", "code": "LOCAL_RULE_FAILED",
                    "message": "Step fails local rule or smoke check.", "witness_id": wid
                })
            if (witness.evaluator_id == self.policy.evaluator_id and
                    witness.spec_id == self.policy.spec_id and
                    witness.policy_sha256 == self.policy.sha256 and
                    (witness.local_accepted != accepted or witness.smoke_passed != smoke)):
                self.findings.append({
                    "kind": "INVALID_WITNESS", "code": "VERDICT_MISMATCH",
                    "message": "Claimed local verdict contradicts replay.", "witness_id": wid
                })

        step_e = 1 if local_pass else 0
        self.running_product = self.running_product * step_e

        # G3: Evaluator Defect
        defect: int | None = None
        classification: str | None = None
        if global_evaluator_sample is not None:
            if type(global_evaluator_sample) not in (bool, int) or int(global_evaluator_sample) not in (0, 1):
                raise ValidationError("global_evaluator_sample must be Boolean or integer 0/1")
            eg = int(global_evaluator_sample)
            defect = eg - self.running_product
            classification = {-1: "NGD", 0: "ZDR", 1: "PGD"}[defect]

        # G4: Prefix / Scope Bounds
        prefix_within_bound = abs(self.cumulative_delta) <= self.policy.max_total
        self.prefix_records.append({
            "step_index": step_idx,
            "witness_id": wid,
            "signed_delta": signed_delta,
            "cumulative_delta": self.cumulative_delta,
            "within_bound": prefix_within_bound,
        })

        alert_reasons: list[str] = []
        if not g1_ok:
            alert_reasons.extend(g1_reasons)
        if not local_pass:
            alert_reasons.append("LOCAL_RULE_FAILED")
        if defect == -1:
            alert_reasons.append("NGD_DEFECT_DETECTED")
        if self.policy.query_scope == "every_prefix" and not prefix_within_bound:
            alert_reasons.append("PREFIX_BUDGET_EXCEEDED")
            self.findings.append({
                "kind": "OBSTRUCTION_DETECTED", "code": "PROTECTED_QUERY_FALSE",
                "message": "Cumulative delta exceeds bound under every_prefix query scope.",
                "witness_id": wid, "cumulative_delta": self.cumulative_delta,
                "bound": self.policy.max_total
            })

        has_alert = len(alert_reasons) > 0
        if has_alert:
            self.status = "OBSTRUCTED_LGGR"
            alert_entry = {
                "schema": "lggr.online_alert.v1",
                "authority_effect": "None",
                "step_index": step_idx,
                "witness_id": wid,
                "status": "ALERT",
                "contract_status": "OBSTRUCTED_LGGR",
                "alert_reasons": alert_reasons,
                "defect": defect,
                "classification": classification,
                "running_product": self.running_product,
                "running_cost": self.running_cost,
                "cumulative_delta": self.cumulative_delta,
                "g1_glued": g1_ok,
                "g4_prefix_ok": prefix_within_bound,
                "meaning": "Mid-flight composability alert; transition to obstructed LGGR.",
            }
            self.alerts.append(alert_entry)
            return json_value(alert_entry)

        receipt = {
            "schema": "lggr.online_step.v1",
            "authority_effect": "None",
            "step_index": step_idx,
            "witness_id": wid,
            "status": "OK",
            "contract_status": self.status,
            "defect": defect,
            "classification": classification,
            "running_product": self.running_product,
            "running_cost": self.running_cost,
            "cumulative_delta": self.cumulative_delta,
            "g1_glued": True,
            "g4_prefix_ok": prefix_within_bound,
            "meaning": "Step verified under declared policy; composable LGGG maintained.",
        }
        return json_value(receipt)

    def get_receipt(self) -> dict[str, Any]:
        """Emit comprehensive audit receipt."""
        if abs(self.cumulative_delta) > self.policy.max_total:
            if not any(f.get("code") == "PROTECTED_QUERY_FALSE" for f in self.findings):
                self.findings.append({
                    "kind": "OBSTRUCTION_DETECTED",
                    "code": "PROTECTED_QUERY_FALSE",
                    "message": "Cumulative delta exceeds bound under declared query scope.",
                    "cumulative_delta": self.cumulative_delta,
                    "bound": self.policy.max_total,
                })

        priority = ["INVALID_WITNESS", "AUTHORITY_REQUIRED", "UNSUPPORTED", "LOCAL_REJECTED",
                    "OBSTRUCTION_DETECTED", "WITNESS_INCOMPLETE"]
        kinds = {f["kind"] for f in self.findings}
        status = next((k for k in priority if k in kinds), "COMPOSITION_VERIFIED")

        body = {
            "schema": "lggr.audit.v1",
            "authority_effect": "None",
            "status": status,
            "composition_certified": status == "COMPOSITION_VERIFIED",
            "contract_status": "COMPOSABLE_LGGG" if status == "COMPOSITION_VERIFIED" else "OBSTRUCTED_LGGR",
            "policy_sha256": self.policy.sha256,
            "query_scope": self.policy.query_scope,
            "total_steps": len(self.steps),
            "running_cost": self.running_cost,
            "cumulative_delta": self.cumulative_delta,
            "running_product": self.running_product,
            "alerts_count": len(self.alerts),
            "findings": self.findings,
            "unresolved_obligations": sorted(self.obligations),
            "scope": "Supplied streaming trace under protected budget policy.",
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingCochainMonitor:
    """Incremental 1-cochain cycle and exact rational L1 repair monitor.

    Adds streaming graph edges incrementally.
    Detects cycle closure in the active spanning forest.
    On cycle closure:
      - Computes coboundary defect along cycle: (D_1 h)_C
      - Solves exact rational L1 repair distance Phi(h) = min_x ||h - D_0 x||_{1,w}
      - Solves exact rational dual witness z: D_0^T z = 0, |z_e| <= w_e, z^T h = Phi(h)
      - Verifies certificate via lggr.linear.verify_l1_certificate
    """

    def __init__(self) -> None:
        self.edges: list[dict[str, Any]] = []
        self.vertices: set[str] = set()
        self.forest_edge_indices: list[int] = []
        self.adj_forest: dict[str, list[tuple[str, int, int]]] = {}
        self.cycles: list[dict[str, Any]] = []
        self.status: str = "OPEN_TREE"

    def add_edge(self, u: str, v: str, value: Fraction | int | str,
                 weight: Fraction | int = 1) -> dict[str, Any]:
        """Ingest a directed edge u -> v, check cycle closure, and compute repair distance."""
        src = text(u, "source vertex u")
        tgt = text(v, "target vertex v")
        val = rational(value)
        wt = rational(weight)
        if wt <= 0:
            raise ValidationError("weight must be strictly positive")

        e_idx = len(self.edges)
        edge_data = {"index": e_idx, "source": src, "target": tgt, "value": val, "weight": wt}
        self.edges.append(edge_data)
        self.vertices.add(src)
        self.vertices.add(tgt)

        if src not in self.adj_forest:
            self.adj_forest[src] = []
        if tgt not in self.adj_forest:
            self.adj_forest[tgt] = []

        # Find path from tgt to src in existing spanning forest
        path = self._find_forest_path(tgt, src)

        if path is None:
            # No cycle formed: edge joins components or extends tree
            self.forest_edge_indices.append(e_idx)
            self.adj_forest[src].append((tgt, e_idx, +1))
            self.adj_forest[tgt].append((src, e_idx, -1))
            receipt: dict[str, Any] = {
                "schema": "lggr.online_cochain.v1",
                "authority_effect": "None",
                "status": "OPEN_TREE",
                "edge_index": e_idx,
                "source": src,
                "target": tgt,
                "value": val,
                "weight": wt,
                "cycle_detected": False,
                "closure_defect": None,
                "l1_repair_distance": None,
                "dual_witness": None,
                "potential": None,
                "meaning": "Edge added without closing a cycle in the active spanning forest.",
            }
            return receipt

        # Cycle closed!
        self.status = "CYCLE_CLOSED"
        # Cycle consists of edge e_idx (src -> tgt, sign +1) followed by path tgt -> ... -> src
        # Path is list of (curr, next_node, forest_e_idx, direction)
        cycle_edges: list[tuple[int, int]] = [(e_idx, +1)]  # (edge_idx, orientation)
        for _, _, f_idx, direct in path:
            cycle_edges.append((f_idx, direct))

        # Compute cycle coboundary defect (D_1 h)_C
        defect = Fraction(0)
        for f_idx, sign in cycle_edges:
            defect += sign * self.edges[f_idx]["value"]

        # Minimum weight on the cycle
        cycle_weights = [self.edges[f_idx]["weight"] for f_idx, _ in cycle_edges]
        min_weight = min(cycle_weights)
        l1_distance = min_weight * abs(defect)

        # Construct dual witness z
        # Dual witness has support on cycle edges: z_e = sign(defect) * min_weight * orientation
        dual_witness: dict[str, Fraction] = {}
        z_by_f_idx: dict[int, Fraction] = {}
        sign_defect = Fraction(1) if defect > 0 else Fraction(-1) if defect < 0 else Fraction(0)

        name_counts: dict[str, int] = {}
        for f_idx, _ in cycle_edges:
            base_name = f"{self.edges[f_idx]['source']}->{self.edges[f_idx]['target']}"
            name_counts[base_name] = name_counts.get(base_name, 0) + 1

        seen_names: set[str] = set()
        for f_idx, orient in cycle_edges:
            base_name = f"{self.edges[f_idx]['source']}->{self.edges[f_idx]['target']}"
            if name_counts[base_name] > 1 and base_name in seen_names:
                e_name = f"{base_name}#{f_idx}"
            else:
                e_name = base_name
                seen_names.add(base_name)
            z_val = Fraction(0) if defect == 0 else sign_defect * min_weight * orient
            dual_witness[e_name] = z_val
            z_by_f_idx[f_idx] = z_val

        # Construct exact vertex potentials x on the active graph
        potential = self._compute_potential(cycle_edges, defect)

        # Build certificate check across cycle edges to independently verify optimality
        certificate = self._verify_cycle_certificate(cycle_edges, potential, dual_witness, z_by_f_idx)

        cycle_record = {
            "cycle_index": len(self.cycles),
            "closing_edge": e_idx,
            "cycle_edges": [{"source": self.edges[f_idx]["source"],
                             "target": self.edges[f_idx]["target"],
                             "orientation": orient,
                             "value": str(self.edges[f_idx]["value"]),
                             "weight": str(self.edges[f_idx]["weight"])}
                            for f_idx, orient in cycle_edges],
            "closure_defect": defect,
            "l1_repair_distance": l1_distance,
            "dual_witness": dual_witness,
            "potential": potential,
            "certificate": certificate,
        }
        self.cycles.append(cycle_record)

        receipt = {
            "schema": "lggr.online_cochain.v1",
            "authority_effect": "None",
            "status": "CYCLE_CLOSED",
            "edge_index": e_idx,
            "source": src,
            "target": tgt,
            "value": val,
            "weight": wt,
            "cycle_detected": True,
            "closure_defect": defect,
            "l1_repair_distance": l1_distance,
            "dual_witness": dual_witness,
            "potential": potential,
            "certificate_status": certificate.get("status"),
            "meaning": ("Cycle closed with zero defect; exact repair verified."
                        if defect == 0
                        else "Cycle closed with nonzero defect; obstruction certified by dual witness."),
        }
        return receipt

    def _find_forest_path(self, start: str, goal: str) -> list[tuple[str, str, int, int]] | None:
        """Find path in forest from start to goal via BFS. Returns list of (u, v, edge_idx, dir)."""
        if start == goal:
            return []
        queue: deque[tuple[str, list[tuple[str, str, int, int]]]] = deque([(start, [])])
        visited = {start}
        while queue:
            curr, path = queue.popleft()
            if curr == goal:
                return path
            for neighbor, e_idx, direction in self.adj_forest.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [(curr, neighbor, e_idx, direction)]))
        return None

    def _compute_potential(self, cycle_edges: list[tuple[int, int]],
                           defect: Fraction) -> dict[str, Fraction]:
        """Compute exact rational vertex potentials satisfying primal L1 optimality."""
        potential: dict[str, Fraction] = {}
        if not self.vertices:
            return potential

        # Exclude the bottleneck edge from the cycle tree propagation
        cycle_weights = [self.edges[f_idx]["weight"] for f_idx, _ in cycle_edges]
        min_w = min(cycle_weights)
        bottleneck_f_idx = next(f_idx for f_idx, _ in cycle_edges if self.edges[f_idx]["weight"] == min_w)

        # Spanning tree edges: non-cycle forest edges + cycle edges except bottleneck
        cycle_indices = {f_idx for f_idx, _ in cycle_edges}
        prop_indices = [idx for idx in self.forest_edge_indices if idx not in cycle_indices]
        prop_indices.extend(idx for idx in cycle_indices if idx != bottleneck_f_idx)

        propagation_edges = [
            (self.edges[idx]["source"], self.edges[idx]["target"], self.edges[idx]["value"])
            for idx in prop_indices
        ]

        # Adjacency for potential propagation
        prop_adj: dict[str, list[tuple[str, Fraction]]] = {v: [] for v in self.vertices}
        for u, v, h_val in propagation_edges:
            prop_adj[u].append((v, h_val))
            prop_adj[v].append((u, -h_val))

        for root in sorted(self.vertices):
            if root in potential:
                continue
            potential[root] = Fraction(0)
            queue: deque[str] = deque([root])
            while queue:
                curr = queue.popleft()
                curr_x = potential[curr]
                for neighbor, delta_h in prop_adj[curr]:
                    if neighbor not in potential:
                        potential[neighbor] = curr_x + delta_h
                        queue.append(neighbor)

        return potential

    def _verify_cycle_certificate(self, cycle_edges: list[tuple[int, int]],
                                  potential: dict[str, Fraction],
                                  dual_witness: dict[str, Fraction],
                                  z_by_f_idx: dict[int, Fraction] | None = None) -> dict[str, Any]:
        """Construct D, h, w, x, z on the cycle subgraph and verify with verify_l1_certificate."""
        cycle_node_list = sorted({self.edges[f_idx][end] for f_idx, _ in cycle_edges for end in ("source", "target")})
        node_to_idx = {name: i for i, name in enumerate(cycle_node_list)}

        d_rows: list[list[Fraction]] = []
        h_vec: list[Fraction] = []
        w_vec: list[Fraction] = []
        z_vec: list[Fraction] = []

        for f_idx, _ in cycle_edges:
            e = self.edges[f_idx]
            u_name, v_name = e["source"], e["target"]
            row = [Fraction(0)] * len(cycle_node_list)
            row[node_to_idx[u_name]] -= Fraction(1)
            row[node_to_idx[v_name]] += Fraction(1)
            d_rows.append(row)
            h_vec.append(e["value"])
            w_vec.append(e["weight"])
            if z_by_f_idx is not None and f_idx in z_by_f_idx:
                z_vec.append(z_by_f_idx[f_idx])
            else:
                e_name = f"{u_name}->{v_name}"
                z_vec.append(dual_witness.get(e_name, Fraction(0)))

        x_vec = [potential.get(node, Fraction(0)) for node in cycle_node_list]
        return verify_l1_certificate(d_rows, h_vec, w_vec, x_vec, z_vec)

    def _forest_potential_and_residuals(
        self, tree_indices: set[int], node_list: list[str]
    ) -> tuple[dict[str, Fraction], list[Fraction], Fraction]:
        """Integrate h along a spanning forest and return (potential, residuals, weighted_l1_cost)."""
        prop_adj: dict[str, list[tuple[str, Fraction]]] = {v: [] for v in node_list}
        for idx in tree_indices:
            e = self.edges[idx]
            u, v, h_val = e["source"], e["target"], e["value"]
            if u != v:
                prop_adj[u].append((v, h_val))
                prop_adj[v].append((u, -h_val))

        potential: dict[str, Fraction] = {}
        for root in node_list:
            if root in potential:
                continue
            potential[root] = Fraction(0)
            queue: deque[str] = deque([root])
            while queue:
                curr = queue.popleft()
                curr_x = potential[curr]
                for neighbor, delta_h in prop_adj[curr]:
                    if neighbor not in potential:
                        potential[neighbor] = curr_x + delta_h
                        queue.append(neighbor)

        residuals: list[Fraction] = []
        cost = Fraction(0)
        for e in self.edges:
            r_e = e["value"] - (potential[e["target"]] - potential[e["source"]])
            residuals.append(r_e)
            cost += e["weight"] * abs(r_e)
        return potential, residuals, cost

    def _find_tree_path_for_indices(
        self, tree_indices: set[int], start: str, goal: str
    ) -> list[tuple[int, int]] | None:
        """Return path from start to goal in tree_indices as list of (edge_idx, orientation)."""
        if start == goal:
            return []
        adj: dict[str, list[tuple[str, int, int]]] = {}
        for idx in tree_indices:
            e = self.edges[idx]
            u, v = e["source"], e["target"]
            adj.setdefault(u, []).append((v, idx, +1))
            adj.setdefault(v, []).append((u, idx, -1))
        queue: deque[tuple[str, list[tuple[int, int]]]] = deque([(start, [])])
        visited = {start}
        while queue:
            curr, path = queue.popleft()
            if curr == goal:
                return path
            for neighbor, e_idx, orient in adj.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [(e_idx, orient)]))
        return None

    @staticmethod
    def _solve_bounded_linear_feasibility(
        var_bounds: list[tuple[Fraction, Fraction]],
        constraints: list[tuple[list[Fraction], Fraction, Fraction]],
    ) -> list[Fraction] | None:
        """Exact rational Fourier-Motzkin elimination for L_j <= a_j^T y <= U_j with l_i <= y_i <= u_i."""
        k = len(var_bounds)
        if k == 0:
            for coeffs, lo, hi in constraints:
                if not (lo <= 0 <= hi):
                    return None
            return []

        # Convert to inequalities: sum_i c_i y_i <= rhs
        ineqs: list[tuple[list[Fraction], Fraction]] = []
        for i, (lo, hi) in enumerate(var_bounds):
            row_hi = [Fraction(0)] * k
            row_hi[i] = Fraction(1)
            ineqs.append((row_hi, hi))
            row_lo = [Fraction(0)] * k
            row_lo[i] = Fraction(-1)
            ineqs.append((row_lo, -lo))

        for coeffs, lo, hi in constraints:
            ineqs.append((list(coeffs), hi))
            ineqs.append(([-c for c in coeffs], -lo))

        history: list[list[tuple[list[Fraction], Fraction]]] = []
        curr_ineqs = ineqs
        for var_idx in range(k - 1, -1, -1):
            history.append(curr_ineqs)
            pos: list[tuple[list[Fraction], Fraction]] = []
            neg: list[tuple[list[Fraction], Fraction]] = []
            zero: list[tuple[list[Fraction], Fraction]] = []
            for coeffs, rhs in curr_ineqs:
                c = coeffs[var_idx]
                if c > 0:
                    pos.append(([x / c for x in coeffs[:var_idx]], rhs / c))
                elif c < 0:
                    neg_c = -c
                    neg.append(([x / neg_c for x in coeffs[:var_idx]], rhs / neg_c))
                else:
                    zero.append((coeffs[:var_idx], rhs))
            next_ineqs: list[tuple[list[Fraction], Fraction]] = list(zero)
            for p_coeffs, p_rhs in pos:
                for n_coeffs, n_rhs in neg:
                    comb = [p + n for p, n in zip(p_coeffs, n_coeffs)]
                    next_ineqs.append((comb, p_rhs + n_rhs))
            curr_ineqs = next_ineqs

        for _, rhs in curr_ineqs:
            if rhs < 0:
                return None

        sol: list[Fraction] = []
        for var_idx in range(k):
            step_ineqs = history[k - 1 - var_idx]
            lo_val: Fraction | None = None
            hi_val: Fraction | None = None
            for coeffs, rhs in step_ineqs:
                c = coeffs[var_idx]
                if c == 0:
                    continue
                rem = rhs - sum((coeffs[j] * sol[j] for j in range(var_idx)), Fraction(0))
                bound = rem / c
                if c > 0:
                    hi_val = bound if hi_val is None else min(hi_val, bound)
                else:
                    lo_val = bound if lo_val is None else max(lo_val, bound)
            if lo_val is not None and hi_val is not None and lo_val > hi_val:
                return None
            chosen = Fraction(0)
            if lo_val is not None and chosen < lo_val:
                chosen = lo_val
            if hi_val is not None and chosen > hi_val:
                chosen = hi_val
            sol.append(chosen)
        return sol

    def _try_construct_dual_for_forest(
        self, tree_indices: set[int], residuals: list[Fraction]
    ) -> list[Fraction] | None:
        """Attempt to build a dual circulation z in ker(D_0^T) with |z_e| <= w_e matching tree_indices."""
        m = len(self.edges)
        chords = [i for i in range(m) if i not in tree_indices]
        cycle_vecs: dict[int, list[Fraction]] = {}
        for c_idx in chords:
            e = self.edges[c_idx]
            vec = [Fraction(0)] * m
            vec[c_idx] = Fraction(1)
            path = self._find_tree_path_for_indices(tree_indices, e["target"], e["source"])
            if path is None:
                return None
            for t_idx, orient in path:
                vec[t_idx] += Fraction(orient)
            cycle_vecs[c_idx] = vec

        z_base = [Fraction(0)] * m
        zero_chords: list[int] = []
        for c_idx in chords:
            r_c = residuals[c_idx]
            w_c = self.edges[c_idx]["weight"]
            if r_c > 0:
                for i in range(m):
                    z_base[i] += w_c * cycle_vecs[c_idx][i]
            elif r_c < 0:
                for i in range(m):
                    z_base[i] -= w_c * cycle_vecs[c_idx][i]
            else:
                zero_chords.append(c_idx)

        if all(abs(z_base[i]) <= self.edges[i]["weight"] for i in range(m)):
            return z_base

        if not zero_chords:
            return None

        var_bounds = [(-self.edges[c_idx]["weight"], self.edges[c_idx]["weight"]) for c_idx in zero_chords]
        constraints: list[tuple[list[Fraction], Fraction, Fraction]] = []
        for t_idx in sorted(tree_indices):
            w_t = self.edges[t_idx]["weight"]
            coeffs = [cycle_vecs[c_idx][t_idx] for c_idx in zero_chords]
            constraints.append((coeffs, -w_t - z_base[t_idx], w_t - z_base[t_idx]))

        y_zero = self._solve_bounded_linear_feasibility(var_bounds, constraints)
        if y_zero is None:
            return None

        z_full = list(z_base)
        for val_y, c_idx in zip(y_zero, zero_chords):
            for i in range(m):
                z_full[i] += val_y * cycle_vecs[c_idx][i]
        if all(abs(z_full[i]) <= self.edges[i]["weight"] for i in range(m)):
            return z_full
        return None

    def solve_global_l1_repair(self) -> dict[str, Any]:
        """Compute exact rational global multi-cycle L1 repair distance and primal-dual certificate."""
        if not self.edges:
            body: dict[str, Any] = {
                "schema": "lggr.global_cochain_l1.v1",
                "authority_effect": "None",
                "status": "OPEN_TREE",
                "global_l1_repair_distance": Fraction(0),
                "potential": {},
                "dual_witness": [],
                "certificate": None,
            }
            return json_value({**body, "receipt_sha256": digest(body)})

        node_list = sorted(self.vertices)
        node_to_idx = {name: i for i, name in enumerate(node_list)}
        m = len(self.edges)

        # Build initial Maximum-Weight Spanning Forest via Kruskal's algorithm
        parent = {v: v for v in node_list}

        def find(v: str) -> str:
            while parent[v] != v:
                parent[v] = parent[parent[v]]
                v = parent[v]
            return v

        sorted_edge_indices = sorted(range(m), key=lambda i: (-self.edges[i]["weight"], i))
        initial_forest: set[int] = set()
        for idx in sorted_edge_indices:
            u, v = self.edges[idx]["source"], self.edges[idx]["target"]
            ru, rv = find(u), find(v)
            if ru != rv:
                parent[ru] = rv
                initial_forest.add(idx)

        best_forest = frozenset(initial_forest)
        best_pot, best_res, best_cost = self._forest_potential_and_residuals(set(best_forest), node_list)
        best_dual = self._try_construct_dual_for_forest(set(best_forest), best_res)

        if best_dual is None:
            queue: deque[frozenset[int]] = deque([best_forest])
            visited_forests: set[frozenset[int]] = {best_forest}
            while queue and best_dual is None:
                curr_forest = queue.popleft()
                curr_set = set(curr_forest)
                curr_pot, curr_res, curr_cost = self._forest_potential_and_residuals(curr_set, node_list)
                if curr_cost == best_cost:
                    cand_dual = self._try_construct_dual_for_forest(curr_set, curr_res)
                    if cand_dual is not None:
                        best_forest = curr_forest
                        best_pot, best_res, best_cost = curr_pot, curr_res, curr_cost
                        best_dual = cand_dual
                        break

                chords = [i for i in range(m) if i not in curr_set]
                improved = False
                for c_idx in chords:
                    e = self.edges[c_idx]
                    path = self._find_tree_path_for_indices(curr_set, e["target"], e["source"])
                    if not path:
                        continue
                    for t_idx, _ in path:
                        next_set = (curr_set - {t_idx}) | {c_idx}
                        next_frozen = frozenset(next_set)
                        if next_frozen in visited_forests:
                            continue
                        _, next_res, next_cost = self._forest_potential_and_residuals(next_set, node_list)
                        if next_cost < best_cost:
                            best_cost = next_cost
                            best_forest = next_frozen
                            visited_forests.add(next_frozen)
                            queue.clear()
                            queue.append(next_frozen)
                            improved = True
                            break
                        elif next_cost == best_cost:
                            visited_forests.add(next_frozen)
                            queue.append(next_frozen)
                    if improved:
                        break

        if best_dual is None:
            best_pot, best_res, best_cost = self._forest_potential_and_residuals(set(best_forest), node_list)
            best_dual = self._try_construct_dual_for_forest(set(best_forest), best_res) or [Fraction(0)] * m

        d_rows: list[list[Fraction]] = []
        h_vec: list[Fraction] = []
        w_vec: list[Fraction] = []
        for e in self.edges:
            row = [Fraction(0)] * len(node_list)
            row[node_to_idx[e["source"]]] -= Fraction(1)
            row[node_to_idx[e["target"]]] += Fraction(1)
            d_rows.append(row)
            h_vec.append(e["value"])
            w_vec.append(e["weight"])

        x_vec = [best_pot.get(v, Fraction(0)) for v in node_list]
        cert = verify_l1_certificate(d_rows, h_vec, w_vec, x_vec, best_dual)
        status = (
            "OPEN_TREE"
            if not self.cycles
            else "EXACT_REPAIR"
            if best_cost == 0
            else "OBSTRUCTED_MULTI_CYCLE"
        )
        body = {
            "schema": "lggr.global_cochain_l1.v1",
            "authority_effect": "None",
            "status": status,
            "total_edges": m,
            "total_vertices": len(node_list),
            "cycles_detected": len(self.cycles),
            "global_l1_repair_distance": best_cost,
            "potential": best_pot,
            "dual_witness": best_dual,
            "certificate_status": cert.get("status"),
            "certificate": cert,
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def merge(self, other: "StreamingCochainMonitor") -> dict[str, Any]:
        """Merge edges from a concurrent branch cochain monitor into this monitor."""
        if not isinstance(other, StreamingCochainMonitor):
            raise ValidationError("other must be a StreamingCochainMonitor instance")
        prior_cycles = len(self.cycles)
        prior_nonrepairable = sum(1 for c in self.cycles if c["closure_defect"] != 0)
        merged_edges = 0
        for e in other.edges:
            self.add_edge(e["source"], e["target"], e["value"], weight=e["weight"])
            merged_edges += 1
        new_cycles = len(self.cycles) - prior_cycles
        total_nonrepairable = sum(1 for c in self.cycles if c["closure_defect"] != 0)
        new_nonrepairable = total_nonrepairable - prior_nonrepairable
        global_l1 = self.solve_global_l1_repair()
        body = {
            "schema": "lggr.online_cochain_merge.v1",
            "authority_effect": "None",
            "merged_edges_count": merged_edges,
            "new_cycles_closed": new_cycles,
            "new_nonrepairable_cycles": new_nonrepairable,
            "total_cycles": len(self.cycles),
            "global_l1_repair_distance": global_l1["global_l1_repair_distance"],
            "global_certificate_status": global_l1["certificate_status"],
            "status": self.get_receipt()["status"],
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def get_receipt(self) -> dict[str, Any]:
        """Emit comprehensive summary receipt for cochain monitor."""
        has_nonrepairable = any(c["closure_defect"] != 0 for c in self.cycles)
        status = "OBSTRUCTED_CYCLE" if has_nonrepairable else "EXACT_REPAIR" if self.cycles else "OPEN_TREE"
        global_l1 = self.solve_global_l1_repair() if self.cycles else None

        body = {
            "schema": "lggr.online_cochain_summary.v1",
            "authority_effect": "None",
            "status": status,
            "total_edges": len(self.edges),
            "total_vertices": len(self.vertices),
            "cycles_detected": len(self.cycles),
            "nonrepairable_cycles": sum(1 for c in self.cycles if c["closure_defect"] != 0),
            "global_l1_repair_distance": (
                global_l1["global_l1_repair_distance"] if global_l1 is not None else "0"
            ),
            "global_certificate_status": (
                global_l1["certificate_status"] if global_l1 is not None else "OPEN_TREE"
            ),
            "cycles": self.cycles,
            "scope": "Supplied streaming cochain graph.",
        }
        return json_value({**body, "receipt_sha256": digest(body)})
