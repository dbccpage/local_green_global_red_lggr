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
from .linear import Vector, classify_cochain, matrix, rational, solve_exact, vector, verify_l1_certificate
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
        self.two_cells: list[dict[str, Any]] = []
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

    def _maxflow_dual_or_descent_cut(
        self, node_list: list[str], residuals: list[Fraction]
    ) -> tuple[list[Fraction] | None, set[str] | None]:
        """Solve exact rational circulation on zero-residual edges via Edmonds-Karp max-flow.

        Returns (dual_witness, None) if all vertex supplies are saturated (optimal),
        or (None, reachable_vertex_cut_U) if unsaturated, where U is a strict descent cut.
        """
        m = len(self.edges)
        z_fixed = [Fraction(0)] * m
        zero_edges: list[int] = []
        s_supply: dict[str, Fraction] = {v: Fraction(0) for v in node_list}

        for idx, e in enumerate(self.edges):
            r_e = residuals[idx]
            w_e = e["weight"]
            u, v = e["source"], e["target"]
            if r_e > 0:
                z_fixed[idx] = w_e
            elif r_e < 0:
                z_fixed[idx] = -w_e
            else:
                zero_edges.append(idx)
            # (D_0^T z_fixed)_w: +z_e at target v, -z_e at source u
            if z_fixed[idx] != 0:
                s_supply[u] -= z_fixed[idx]
                s_supply[v] += z_fixed[idx]

        # We need outflow(v) - inflow(v) = s_supply[v] on zero_edges
        total_pos_supply = sum((val for val in s_supply.values() if val > 0), Fraction(0))
        if total_pos_supply == 0:
            return z_fixed, None

        src_node = "__super_source__"
        sink_node = "__super_sink__"
        all_nodes = [src_node, sink_node] + node_list
        # Directed residual graph: adj[u] = list of [v, cap, rev_idx, zero_edge_idx, sign]
        adj: dict[str, list[list[Any]]] = {n: [] for n in all_nodes}

        def add_arc(u: str, v: str, cap_fwd: Fraction, cap_rev: Fraction,
                    e_idx: int = -1) -> None:
            fwd_idx = len(adj[u])
            rev_idx = len(adj[v])
            adj[u].append([v, cap_fwd, rev_idx, e_idx, +1])
            adj[v].append([u, cap_rev, fwd_idx, e_idx, -1])

        for v in node_list:
            sv = s_supply[v]
            if sv > 0:
                add_arc(src_node, v, sv, Fraction(0))
            elif sv < 0:
                add_arc(v, sink_node, -sv, Fraction(0))

        for idx in zero_edges:
            e = self.edges[idx]
            u, v = e["source"], e["target"]
            if u != v:
                w_e = e["weight"]
                # Flow f_e in [-w_e, +w_e] -> residual capacity w_e in both directions
                add_arc(u, v, w_e, w_e, idx)

        flow_total = Fraction(0)
        while flow_total < total_pos_supply:
            parent_map: dict[str, tuple[str, int]] = {}
            queue: deque[str] = deque([src_node])
            visited = {src_node}
            found = False
            while queue:
                curr = queue.popleft()
                if curr == sink_node:
                    found = True
                    break
                for arc_i, arc in enumerate(adj[curr]):
                    nxt, cap = arc[0], arc[1]
                    if cap > 0 and nxt not in visited:
                        visited.add(nxt)
                        parent_map[nxt] = (curr, arc_i)
                        queue.append(nxt)
            if not found:
                cut_u = {v for v in node_list if v in visited}
                return None, cut_u

            # Bottleneck capacity along shortest augmenting path
            bottleneck: Fraction | None = None
            curr = sink_node
            while curr != src_node:
                prev_n, arc_i = parent_map[curr]
                cap = adj[prev_n][arc_i][1]
                bottleneck = cap if bottleneck is None else min(bottleneck, cap)
                curr = prev_n

            assert bottleneck is not None and bottleneck > 0
            curr = sink_node
            while curr != src_node:
                prev_n, arc_i = parent_map[curr]
                arc = adj[prev_n][arc_i]
                rev_arc = adj[curr][arc[2]]
                arc[1] -= bottleneck
                rev_arc[1] += bottleneck
                curr = prev_n
            flow_total += bottleneck

        # Reconstruct f_e on zero_edges from residual capacities
        z_full = list(z_fixed)
        for u in node_list:
            for arc in adj[u]:
                e_idx, sign = arc[3], arc[4]
                if e_idx >= 0 and sign == +1:
                    w_e = self.edges[e_idx]["weight"]
                    # Initial forward cap was w_e; remaining cap is arc[1], so net flow u->v is w_e - arc[1]
                    z_full[e_idx] = w_e - arc[1]
        return z_full, None

    def solve_global_l1_repair(self) -> dict[str, Any]:
        """Compute exact rational global multi-cycle L1 repair distance and primal-dual certificate."""
        if not self.edges:
            body: dict[str, Any] = {
                "schema": "lggr.global_cochain_l1.v1",
                "authority_effect": "None",
                "status": "OPEN_TREE",
                "pivots_count": 0,
                "global_l1_repair_distance": Fraction(0),
                "potential": {},
                "dual_witness": [],
                "certificate": None,
            }
            return json_value({**body, "receipt_sha256": digest(body)})

        node_list = sorted(self.vertices)
        node_to_idx = {name: i for i, name in enumerate(node_list)}
        m = len(self.edges)

        # Stage 1: Build initial Maximum-Weight Spanning Forest via Kruskal's algorithm
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

        curr_pot, curr_res, curr_cost = self._forest_potential_and_residuals(initial_forest, node_list)
        pivots_count = 0

        # Stage 2: Exact rational Max-Flow / Min-Cut steepest-descent line search
        best_dual: list[Fraction] | None = None
        while True:
            dual_cand, cut_u = self._maxflow_dual_or_descent_cut(node_list, curr_res)
            if dual_cand is not None:
                best_dual = dual_cand
                break
            if not cut_u:
                break

            # Candidate positive step sizes theta where an edge crossing cut_u hits zero residual
            # Under x(theta) = x + theta * 1_{cut_u}:
            # d_e = (D_0 1_{cut_u})_e = 1_{v in cut_u} - 1_{u in cut_u} in {-1, 0, +1}
            # r_e(theta) = r_e - theta * d_e
            candidate_thetas: set[Fraction] = set()
            delta_dirs: list[int] = []
            for idx, e in enumerate(self.edges):
                u_in = 1 if e["source"] in cut_u else 0
                v_in = 1 if e["target"] in cut_u else 0
                d_e = v_in - u_in
                delta_dirs.append(d_e)
                if d_e != 0:
                    theta_hit = curr_res[idx] * d_e
                    if theta_hit > 0:
                        candidate_thetas.add(theta_hit)

            if not candidate_thetas:
                break

            best_theta = Fraction(0)
            best_theta_cost = curr_cost
            for theta in sorted(candidate_thetas):
                cost_t = Fraction(0)
                for idx, e in enumerate(self.edges):
                    cost_t += e["weight"] * abs(curr_res[idx] - theta * delta_dirs[idx])
                if cost_t < best_theta_cost:
                    best_theta_cost = cost_t
                    best_theta = theta

            if best_theta <= 0:
                break

            for v in cut_u:
                curr_pot[v] += best_theta
            for idx in range(m):
                curr_res[idx] -= best_theta * delta_dirs[idx]
            curr_cost = best_theta_cost
            pivots_count += 1

        if best_dual is None:
            best_dual = [Fraction(0)] * m

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

        x_vec = [curr_pot.get(v, Fraction(0)) for v in node_list]
        cert = verify_l1_certificate(d_rows, h_vec, w_vec, x_vec, best_dual)
        status = (
            "OPEN_TREE"
            if not self.cycles
            else "EXACT_REPAIR"
            if curr_cost == 0
            else "OBSTRUCTED_MULTI_CYCLE"
        )
        body = {
            "schema": "lggr.global_cochain_l1.v1",
            "authority_effect": "None",
            "status": status,
            "total_edges": m,
            "total_vertices": len(node_list),
            "cycles_detected": len(self.cycles),
            "pivots_count": pivots_count,
            "global_l1_repair_distance": curr_cost,
            "potential": curr_pot,
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

    def add_two_cell(
        self,
        cell_id: str,
        boundary: Iterable[tuple[str, str, int] | dict[str, Any]],
    ) -> dict[str, Any]:
        """Declare a 2-cell (filled plaquette/face) with oriented 1-edge boundary.

        Each boundary item is either (source, target, orientation) or
        {"source": u, "target": v, "orientation": +/-1}.
        Checks boundary closure (D_1 D_0 = 0 on vertices) and evaluates (D_1 h)_cell
        when all boundary 1-edges have been observed.
        """
        cid = text(cell_id, "cell_id")
        raw_items = list(sequence(boundary, "boundary"))
        if not raw_items:
            raise ValidationError("2-cell boundary must be non-empty")

        parsed_boundary: list[dict[str, Any]] = []
        vertex_balance: dict[str, int] = {}
        for item in raw_items:
            if isinstance(item, Mapping):
                u = text(item.get("source"), "boundary source")
                v = text(item.get("target"), "boundary target")
                orient = exact_int(item.get("orientation", 1), "orientation")
            else:
                seq_item = sequence(item, "boundary tuple")
                if len(seq_item) != 3:
                    raise ValidationError("boundary tuple must be (source, target, orientation)")
                u = text(seq_item[0], "boundary source")
                v = text(seq_item[1], "boundary target")
                orient = exact_int(seq_item[2], "orientation")
            if orient == 0:
                raise ValidationError("2-cell boundary orientation must be nonzero")
            parsed_boundary.append({"source": u, "target": v, "orientation": orient})
            vertex_balance[u] = vertex_balance.get(u, 0) - orient
            vertex_balance[v] = vertex_balance.get(v, 0) + orient

        is_closed_boundary = all(bal == 0 for bal in vertex_balance.values())
        cell_record: dict[str, Any] = {
            "cell_id": cid,
            "boundary": parsed_boundary,
            "valid_complex_boundary": is_closed_boundary,
            "vertex_balance": vertex_balance,
        }
        self.two_cells.append(cell_record)

        if not is_closed_boundary:
            body: dict[str, Any] = {
                "schema": "lggr.online_twocell.v1",
                "authority_effect": "None",
                "cell_id": cid,
                "status": "INVALID_COMPLEX",
                "complete_edges": False,
                "coboundary_value": None,
                "vertex_balance": vertex_balance,
                "meaning": "Declared 2-cell boundary does not have zero 0-boundary (D_1 D_0 != 0).",
            }
            return json_value({**body, "receipt_sha256": digest(body)})

        # Check if all boundary edges exist in self.edges
        coboundary_val = Fraction(0)
        missing_edges: list[str] = []
        for b_item in parsed_boundary:
            u, v, orient = b_item["source"], b_item["target"], b_item["orientation"]
            match_edge = next(
                (e for e in self.edges if e["source"] == u and e["target"] == v),
                None,
            )
            if match_edge is not None:
                coboundary_val += Fraction(orient) * match_edge["value"]
            else:
                rev_edge = next(
                    (e for e in self.edges if e["source"] == v and e["target"] == u),
                    None,
                )
                if rev_edge is not None:
                    coboundary_val -= Fraction(orient) * rev_edge["value"]
                else:
                    missing_edges.append(f"{u}->{v}")

        if missing_edges:
            body = {
                "schema": "lggr.online_twocell.v1",
                "authority_effect": "None",
                "cell_id": cid,
                "status": "PENDING_EDGES",
                "complete_edges": False,
                "missing_edges": missing_edges,
                "coboundary_value": None,
                "meaning": "2-cell registered; awaiting arrival of remaining boundary 1-edges.",
            }
            return json_value({**body, "receipt_sha256": digest(body)})

        status = "CELL_CLOSED" if coboundary_val == 0 else "CLOSURE_FAILURE"
        body = {
            "schema": "lggr.online_twocell.v1",
            "authority_effect": "None",
            "cell_id": cid,
            "status": status,
            "complete_edges": True,
            "missing_edges": [],
            "coboundary_value": coboundary_val,
            "meaning": (
                "1-cochain is closed on this filled 2-cell ((D_1 h)_cell = 0)."
                if coboundary_val == 0
                else "1-cochain has nonzero coboundary on this filled 2-cell ((D_1 h)_cell != 0)."
            ),
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def classify_streaming_cohomology(self) -> dict[str, Any]:
        """Classify the current streaming 1-cochain against declared 2-cells via classify_cochain.

        Separates:
          - EXACT: h in im(D_0) and D_1 h = 0
          - CLOSURE_FAILURE: D_1 h != 0 on at least one filled 2-cell
          - CLOSED_NONEXACT: D_1 h = 0 on all filled 2-cells, yet h not in im(D_0)
            (nonzero first cohomology class [h] in H^1 around an unfilled hole)
          - INVALID_COMPLEX: D_1 D_0 != 0
        """
        if not self.edges:
            body: dict[str, Any] = {
                "schema": "lggr.cochain.v1",
                "authority_effect": "None",
                "status": "EXACT",
                "repair_exists": True,
                "potential": [],
                "closure": [],
                "represents_nonzero_H1": False,
            }
            return json_value({**body, "receipt_sha256": digest(body)})

        if any(not c["valid_complex_boundary"] for c in self.two_cells):
            body = {
                "schema": "lggr.cochain.v1",
                "authority_effect": "None",
                "status": "INVALID_COMPLEX",
                "repair_exists": False,
                "potential": None,
                "closure": None,
                "represents_nonzero_H1": None,
            }
            return json_value({**body, "receipt_sha256": digest(body)})

        node_list = sorted(self.vertices)
        node_to_idx = {name: i for i, name in enumerate(node_list)}
        m = len(self.edges)

        d0_rows: list[list[Fraction]] = []
        h_vec: list[Fraction] = []
        for e in self.edges:
            row = [Fraction(0)] * len(node_list)
            row[node_to_idx[e["source"]]] -= Fraction(1)
            row[node_to_idx[e["target"]]] += Fraction(1)
            d0_rows.append(row)
            h_vec.append(e["value"])

        d1_rows: list[list[Fraction]] = []
        for cell in self.two_cells:
            row_d1 = [Fraction(0)] * m
            complete = True
            for b_item in cell["boundary"]:
                u, v, orient = b_item["source"], b_item["target"], b_item["orientation"]
                match_idx = next(
                    (i for i, e in enumerate(self.edges) if e["source"] == u and e["target"] == v),
                    None,
                )
                if match_idx is not None:
                    row_d1[match_idx] += Fraction(orient)
                else:
                    rev_idx = next(
                        (i for i, e in enumerate(self.edges) if e["source"] == v and e["target"] == u),
                        None,
                    )
                    if rev_idx is not None:
                        row_d1[rev_idx] -= Fraction(orient)
                    else:
                        complete = False
                        break
            if complete:
                d1_rows.append(row_d1)

        return classify_cochain(d0_rows, h_vec, d1_rows)

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
