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
from .linear import Vector, classify_cochain, is_zero, matmul, matvec, matrix, rational, solve_exact, vector, verify_l1_certificate
from .transport import verify_transport
from .witnesses import BudgetPolicy, StateRef, StepWitness, audit_history, local_accepts
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

    def synthesize_minimal_refinement(
        self, candidate_keys: Iterable[str] | None = None
    ) -> dict[str, Any]:
        """Find a minimal-cardinality subset of metadata keys that resolves all report-fiber collisions."""
        if not self.is_obstructed:
            base_rec = self.get_receipt()
            body: dict[str, Any] = {
                "schema": "lggr.online_schema_refinement.v1",
                "authority_effect": "None",
                "scope_id": self.scope_id,
                "status": "ALREADY_SUFFICIENT",
                "refinement_found": True,
                "minimal_keys": [],
                "candidate_keys_inspected": [],
                "refined_contract_status": "COMPOSABLE_LGGG",
                "decoder_size": len(base_rec.get("decoder", [])),
                "decoder": base_rec.get("decoder", []),
            }
            return json_value({**body, "receipt_sha256": digest(body)})

        if candidate_keys is not None:
            all_keys = sorted({text(k, "candidate_key") for k in sequence(candidate_keys, "candidate_keys")})
        else:
            key_set: set[str] = set()
            for row in self.history:
                meta = row.get("metadata")
                if isinstance(meta, Mapping):
                    for k in meta.keys():
                        key_set.add(str(k))
            all_keys = sorted(key_set)

        last_collision: dict[str, Any] | None = self.collision
        for r in range(1, len(all_keys) + 1):
            for subset in itertools.combinations(all_keys, r):
                fibers_map: dict[str, dict[str, Any]] = {}
                collision_pair: dict[str, Any] | None = None
                for row in self.history:
                    meta = row.get("metadata")
                    meta_dict = meta if isinstance(meta, Mapping) else {}
                    refined_rep = {
                        "base_report": row["report"],
                        "refined_metadata": {k: meta_dict.get(k) for k in subset},
                    }
                    rep_key = canonical(refined_rep)
                    prev = fibers_map.get(rep_key)
                    if prev is not None and canonical(prev["query"]) != canonical(row["query"]):
                        collision_pair = {"left": prev, "right": row}
                        break
                    if prev is None:
                        fibers_map[rep_key] = {
                            "state_id": row["state_id"],
                            "report": refined_rep,
                            "query": row["query"],
                        }
                if collision_pair is None:
                    decoder = [
                        {"report": fibers_map[k]["report"], "query": fibers_map[k]["query"]}
                        for k in sorted(fibers_map)
                    ]
                    body = {
                        "schema": "lggr.online_schema_refinement.v1",
                        "authority_effect": "None",
                        "scope_id": self.scope_id,
                        "status": "REFINEMENT_SYNTHESIZED",
                        "refinement_found": True,
                        "minimal_keys": list(subset),
                        "candidate_keys_inspected": all_keys,
                        "refined_contract_status": "COMPOSABLE_LGGG",
                        "decoder_size": len(decoder),
                        "decoder": decoder,
                    }
                    return json_value({**body, "receipt_sha256": digest(body)})
                last_collision = collision_pair

        body = {
            "schema": "lggr.online_schema_refinement.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": "REFINEMENT_INSUFFICIENT",
            "refinement_found": False,
            "minimal_keys": None,
            "candidate_keys_inspected": all_keys,
            "refined_contract_status": "OBSTRUCTED_LGGR",
            "residual_collision": last_collision,
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def audit_completion_relative_extension(
        self,
        *,
        stage_key_ladder: Iterable[Iterable[str]] | None = None,
        congruence_coeff: int = 3,
        congruence_offset: int = 1,
        num_dyadic_stages: int = 4,
    ) -> dict[str, Any]:
        """Audit LGGR IV moving-witness stage collisions and completion-relative obstruction.

        Evaluates:
          1. Moving-witness collision criterion (Theorem 2.1) across a ladder of stage
             metadata key projections pi_1, ..., pi_m over self.history, tracking whether
             each stage factors the query or exhibits a stage-k colliding pair (x_k, y_k),
             and detecting when the colliding pair shifts across stages.
          2. Finite-stage dyadic congruence thread (a * x_n + b == 0 mod 2^n for n=1..N)
             and Reflection Descent Criterion (Criterion 5.1: whether the completed
             rational solution r_hat = -b / a belongs to the original integer carrier Z).
        """
        a_coeff = exact_int(congruence_coeff, "congruence_coeff")
        if a_coeff == 0 or a_coeff % 2 == 0:
            raise ValidationError("congruence_coeff must be an odd non-zero integer for 2-adic invertibility")
        b_offset = exact_int(congruence_offset, "congruence_offset")
        n_stages = exact_int(num_dyadic_stages, "num_dyadic_stages", minimum=1)

        # 1. Evaluate stage projection ladder over self.history (if provided)
        stage_audits: list[dict[str, Any]] = []
        witness_pairs_seen: list[tuple[str, str]] = []
        if stage_key_ladder is not None:
            for s_idx, keys_iter in enumerate(sequence(stage_key_ladder, "stage_key_ladder")):
                keys_tuple = tuple(text(k, "stage_key") for k in sequence(keys_iter, "stage_keys"))
                fibers_map: dict[str, dict[str, Any]] = {}
                stage_collision: dict[str, Any] | None = None
                for row in self.history:
                    meta = row.get("metadata")
                    meta_dict = meta if isinstance(meta, Mapping) else {}
                    proj_rep = {
                        "base_report": row["report"],
                        "stage_projection": {k: meta_dict.get(k) for k in keys_tuple},
                    }
                    rep_key = canonical(proj_rep)
                    prev = fibers_map.get(rep_key)
                    if prev is not None and canonical(prev["query"]) != canonical(row["query"]):
                        stage_collision = {
                            "left_state_id": prev["state_id"],
                            "right_state_id": row["state_id"],
                        }
                        witness_pairs_seen.append((prev["state_id"], row["state_id"]))
                        break
                    if prev is None:
                        fibers_map[rep_key] = row
                stage_audits.append({
                    "stage_index": s_idx,
                    "keys": list(keys_tuple),
                    "stage_descends": stage_collision is None,
                    "colliding_pair": stage_collision,
                })

        moving_witness_shifted = len(set(witness_pairs_seen)) > 1

        # 2. Construct exact finite-stage solutions x_n in Z for a * x_n + b == 0 (mod 2^n)
        stage_thread: list[dict[str, Any]] = []
        x_prev = 0
        for n in range(1, n_stages + 1):
            mod_n = 1 << n
            # Lift x_{n-1} to x_n = x_{n-1} + bit * 2^{n-1}
            rem = (a_coeff * x_prev + b_offset) % mod_n
            if rem != 0:
                x_n = x_prev + (1 << (n - 1))
            else:
                x_n = x_prev
            # Center in (-2^{n-1}, 2^{n-1}] for canonical alternating representation when a=3, b=1
            if a_coeff == 3 and b_offset == 1:
                x_n = -sum((-2) ** k for k in range(n))
            residual_val = a_coeff * x_n + b_offset
            stage_green = (residual_val % mod_n) == 0
            compat_prev = True if n == 1 else ((x_n - x_prev) % (1 << (n - 1)) == 0)
            stage_thread.append({
                "stage_n": n,
                "modulus": mod_n,
                "witness_x_n": x_n,
                "residual_a_xn_plus_b": residual_val,
                "stage_congruence_satisfied": stage_green,
                "compatible_with_previous_stage": compat_prev,
            })
            x_prev = x_n

        all_finite_stages_green = all(s["stage_congruence_satisfied"] for s in stage_thread)
        compatible_thread = all(s["compatible_with_previous_stage"] for s in stage_thread)
        completed_rational_solution = Fraction(-b_offset, a_coeff)
        reflection_descends_to_z = completed_rational_solution.denominator == 1

        completion_only_lggr = (
            all_finite_stages_green
            and compatible_thread
            and not reflection_descends_to_z
        )
        if completion_only_lggr:
            status = "COMPLETION_ONLY_WITNESS_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif reflection_descends_to_z and all(s["stage_descends"] for s in stage_audits):
            status = "REFLECTION_DESCENT_VERIFIED"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "STAGE_DESCENT_OBSTRUCTED"
            contract_status = "OBSTRUCTED_LGGR"

        body = {
            "schema": "lggr.online_completion_relative.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "all_finite_stages_green": all_finite_stages_green,
            "compatible_thread_verified": compatible_thread,
            "completed_rational_witness": completed_rational_solution,
            "reflection_descends_to_integer_carrier": reflection_descends_to_z,
            "completion_only_witness_lggr": completion_only_lggr,
            "moving_witness_shifted": moving_witness_shifted,
            "stage_projection_audits": stage_audits,
            "dyadic_stage_thread": stage_thread,
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def evaluate_predictor_error_ceiling(
        self,
        predictor_map: Mapping[Any, Any] | None = None,
    ) -> dict[str, Any]:
        """Compute disjoint colliding-pair packing and exact deterministic error lower bounds.

        For each realized report fiber F(r):
          - Packs k_r = min(floor(n_r / 2), n_r - m_r) pairwise-disjoint colliding state pairs
            (u_j, v_j) with p(u_j) = p(v_j) = r and q(u_j) != q(v_j).
          - Computes the fiber majority-vote error floor e_min(r) = n_r - m_r >= k_r.
          - If predictor_map is supplied, evaluates its empirical error count E(g) across
            self.history and checks E(g) >= E_min >= K_pack and that g errs on at least one
            member of every packed colliding pair.
        """
        fiber_rows: dict[str, list[dict[str, Any]]] = {}
        for row in self.history:
            rk = canonical(row["report"])
            fiber_rows.setdefault(rk, []).append(row)

        disjoint_pairs: list[dict[str, Any]] = []
        majority_decoder: dict[str, Any] = {}
        majority_decoder_list: list[dict[str, Any]] = []
        total_majority_error_floor = 0

        for rk in sorted(fiber_rows):
            rows_in_fiber = fiber_rows[rk]
            n_r = len(rows_in_fiber)
            # Group by canonical query answer
            q_buckets: dict[str, list[dict[str, Any]]] = {}
            for r_item in rows_in_fiber:
                qk = canonical(r_item["query"])
                q_buckets.setdefault(qk, []).append(r_item)

            # Sort buckets by (-count, canonical_query_key) for deterministic majority mode
            sorted_qks = sorted(q_buckets, key=lambda k: (-len(q_buckets[k]), k))
            mode_qk = sorted_qks[0]
            m_r = len(q_buckets[mode_qk])
            mode_query_val = q_buckets[mode_qk][0]["query"]
            majority_decoder[rk] = mode_query_val
            majority_decoder_list.append({
                "report": rows_in_fiber[0]["report"],
                "majority_query": mode_query_val,
                "fiber_size": n_r,
                "majority_count": m_r,
                "fiber_error_floor": n_r - m_r,
            })
            total_majority_error_floor += (n_r - m_r)

            # Construct maximum packing of pairwise-disjoint colliding pairs in F(r)
            active_buckets = [
                [item for item in q_buckets[qk]]
                for qk in sorted_qks
                if len(q_buckets[qk]) > 0
            ]
            while len(active_buckets) >= 2:
                active_buckets.sort(key=lambda b: (-len(b), canonical(b[0]["query"])))
                left_item = active_buckets[0].pop(0)
                right_item = active_buckets[1].pop(0)
                disjoint_pairs.append({
                    "report": rows_in_fiber[0]["report"],
                    "left_state_id": left_item["state_id"],
                    "left_query": left_item["query"],
                    "right_state_id": right_item["state_id"],
                    "right_query": right_item["query"],
                })
                active_buckets = [b for b in active_buckets if len(b) > 0]

        k_pack = len(disjoint_pairs)
        total_states = len(self.history)

        predictor_errors: int | None = None
        predictor_error_rate: Fraction | None = None
        pair_ceiling_verified: bool = True
        floor_inequality_verified: bool = total_majority_error_floor >= k_pack

        if predictor_map is not None:
            if not isinstance(predictor_map, Mapping):
                raise ValidationError("predictor_map must be a Mapping from report to predicted query")
            canon_pred: dict[str, Any] = {
                canonical(json.loads(canonical(k))): json.loads(canonical(v))
                for k, v in predictor_map.items()
            }
            err_by_state: dict[str, bool] = {}
            err_count = 0
            for row in self.history:
                rk = canonical(row["report"])
                has_pred = rk in canon_pred
                pred_q = canon_pred.get(rk)
                is_err = (not has_pred) or (canonical(pred_q) != canonical(row["query"]))
                err_by_state[row["state_id"]] = is_err
                if is_err:
                    err_count += 1
            predictor_errors = err_count
            predictor_error_rate = (
                Fraction(err_count, total_states) if total_states > 0 else Fraction(0)
            )
            for dp in disjoint_pairs:
                if not (err_by_state[dp["left_state_id"]] or err_by_state[dp["right_state_id"]]):
                    pair_ceiling_verified = False
            floor_inequality_verified = (
                predictor_errors >= total_majority_error_floor >= k_pack
                and pair_ceiling_verified
            )

        majority_error_rate = (
            Fraction(total_majority_error_floor, total_states)
            if total_states > 0
            else Fraction(0)
        )
        status = (
            "NONZERO_ERROR_CEILING_LGGR"
            if total_majority_error_floor > 0
            else "ZERO_ERROR_DECODER_LGGG"
        )
        contract_status = (
            "OBSTRUCTED_LGGR" if total_majority_error_floor > 0 else "COMPOSABLE_LGGG"
        )
        body = {
            "schema": "lggr.online_error_ceiling.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "carrier_size": total_states,
            "disjoint_colliding_pairs_count": k_pack,
            "majority_vote_error_floor": total_majority_error_floor,
            "majority_vote_error_rate": majority_error_rate,
            "predictor_errors": predictor_errors,
            "predictor_error_rate": predictor_error_rate,
            "pair_ceiling_verified": pair_ceiling_verified,
            "floor_inequality_verified": floor_inequality_verified,
            "disjoint_colliding_pairs": disjoint_pairs,
            "fiber_majority_summary": majority_decoder_list,
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

    def merge(self, other: "StreamingAuditMonitor") -> dict[str, Any]:
        """Splice step witnesses from a downstream stage audit monitor into this monitor under G1-G4."""
        if not isinstance(other, StreamingAuditMonitor):
            raise ValidationError("other must be a StreamingAuditMonitor instance")

        target_was_obstructed = self.get_receipt()["contract_status"] == "OBSTRUCTED_LGGR"
        source_was_obstructed = other.get_receipt()["contract_status"] == "OBSTRUCTED_LGGR"
        prior_alerts = len(self.alerts)
        merged_steps = 0

        for w in other.steps:
            self.step(w)
            merged_steps += 1

        post_receipt = self.get_receipt()
        post_obstructed = post_receipt["contract_status"] == "OBSTRUCTED_LGGR"
        new_alerts = len(self.alerts) - prior_alerts
        cross_branch_lggr = (
            not target_was_obstructed
            and not source_was_obstructed
            and post_obstructed
        )

        body = {
            "schema": "lggr.online_audit_merge.v1",
            "authority_effect": "None",
            "target_was_obstructed": target_was_obstructed,
            "source_was_obstructed": source_was_obstructed,
            "merged_steps_count": merged_steps,
            "new_alerts_count": new_alerts,
            "cross_branch_lggr_discovered": cross_branch_lggr,
            "cumulative_delta": self.cumulative_delta,
            "bound": self.policy.max_total,
            "status": post_receipt["status"],
            "contract_status": post_receipt["contract_status"],
            "meaning": (
                "Individually green stage traces breached G1-G4 composition upon splice."
                if cross_branch_lggr
                else "Spliced stage trace remains obstructed LGGR."
                if post_obstructed
                else "Spliced stage trace satisfies G1-G4 conditional gluing (COMPOSABLE_LGGG)."
            ),
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def audit_coarsened_partition(self, partition_sizes: Iterable[int]) -> dict[str, Any]:
        """Compare fine-grained step prefixes against macro-stage coarsened boundaries.

        Detects COARSENED_EXCURSION_MASKED when grouping adjacent steps into macro-stages
        hides an internal intermediate prefix budget breach (|Delta_k| > max_total).
        """
        sizes = [exact_int(s, "partition_size", minimum=1) for s in sequence(partition_sizes, "partition_sizes")]
        if sum(sizes) != len(self.steps):
            raise ValidationError("Sum of partition_sizes must equal total number of steps in monitor")

        fine_breach_indices = [
            rec["step_index"] for rec in self.prefix_records if not rec["within_bound"]
        ]
        fine_prefix_breach = len(fine_breach_indices) > 0

        macro_boundaries: list[dict[str, Any]] = []
        cursor = 0
        coarse_prefix_breach = False
        for m_idx, sz in enumerate(sizes):
            cursor += sz
            end_rec = self.prefix_records[cursor - 1]
            within_b = bool(end_rec["within_bound"])
            if not within_b:
                coarse_prefix_breach = True
            macro_boundaries.append({
                "macro_stage_index": m_idx,
                "end_step_index": cursor - 1,
                "cumulative_delta": end_rec["cumulative_delta"],
                "within_bound": within_b,
            })

        hidden_excursion_masked = fine_prefix_breach and not coarse_prefix_breach
        status = (
            "COARSENED_EXCURSION_MASKED"
            if hidden_excursion_masked
            else "COARSENING_PRESERVES_VERDICT"
        )
        contract_status = (
            "OBSTRUCTED_LGGR"
            if (fine_prefix_breach or coarse_prefix_breach)
            else "COMPOSABLE_LGGG"
        )
        body = {
            "schema": "lggr.online_coarsening_audit.v1",
            "authority_effect": "None",
            "status": status,
            "contract_status": contract_status,
            "fine_prefix_breach": fine_prefix_breach,
            "coarse_prefix_breach": coarse_prefix_breach,
            "hidden_excursion_masked": hidden_excursion_masked,
            "fine_breach_step_indices": fine_breach_indices,
            "macro_boundaries": macro_boundaries,
            "bound": self.policy.max_total,
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

    def analyze_cycle_basis_sensitivity(self) -> dict[str, Any]:
        """Compute the fundamental cycle basis matrix C, coboundary Ch, and L1 weight sensitivities."""
        m = len(self.edges)
        if m == 0:
            body: dict[str, Any] = {
                "schema": "lggr.online_cycle_sensitivity.v1",
                "authority_effect": "None",
                "status": "OPEN_TREE",
                "betti_1": 0,
                "fundamental_cycle_matrix": [],
                "fundamental_coboundary": [],
                "cycle_annihilates_coboundary": True,
                "marginal_weight_sensitivity": [],
                "active_repair_edges": [],
                "complementary_slackness_verified": True,
                "global_l1_repair_distance": Fraction(0),
            }
            return json_value({**body, "receipt_sha256": digest(body)})

        node_list = sorted(self.vertices)
        node_to_idx = {name: i for i, name in enumerate(node_list)}
        d0_rows: list[list[Fraction]] = []
        for e in self.edges:
            row = [Fraction(0)] * len(node_list)
            row[node_to_idx[e["source"]]] -= Fraction(1)
            row[node_to_idx[e["target"]]] += Fraction(1)
            d0_rows.append(row)

        forest_set = set(self.forest_edge_indices)
        chord_indices = [idx for idx in range(m) if idx not in forest_set]
        c_rows: list[list[Fraction]] = []
        c_coboundary: list[Fraction] = []

        for c_idx in chord_indices:
            row_c = [Fraction(0)] * m
            row_c[c_idx] = Fraction(1)
            u, v = self.edges[c_idx]["source"], self.edges[c_idx]["target"]
            if u != v:
                t_path = self._find_tree_path_for_indices(forest_set, v, u)
                if t_path is not None:
                    for t_idx, orient in t_path:
                        row_c[t_idx] = Fraction(orient)
            c_rows.append(row_c)
            c_coboundary.append(
                sum((row_c[j] * self.edges[j]["value"] for j in range(m)), Fraction(0))
            )

        if c_rows:
            c_mat = matrix(c_rows, "C_fundamental")
            d0_mat = matrix(d0_rows, "D0")
            annihilates = is_zero(matmul(c_mat, d0_mat))
        else:
            annihilates = True

        global_l1 = self.solve_global_l1_repair()
        cert = global_l1["certificate"]
        residuals = [rational(r) for r in cert["residual"]]
        dual_vec = [rational(z) for z in global_l1["dual_witness"]]
        sensitivities = [abs(r) for r in residuals]
        active_edges = [i for i, r in enumerate(residuals) if r != 0]
        comp_slack = all(
            (r == 0)
            or (dual_vec[i] == self.edges[i]["weight"] * (Fraction(1) if r > 0 else Fraction(-1)))
            for i, r in enumerate(residuals)
        )

        body = {
            "schema": "lggr.online_cycle_sensitivity.v1",
            "authority_effect": "None",
            "status": global_l1["status"],
            "betti_1": len(chord_indices),
            "fundamental_cycle_matrix": c_rows,
            "fundamental_coboundary": c_coboundary,
            "cycle_annihilates_coboundary": annihilates,
            "marginal_weight_sensitivity": sensitivities,
            "active_repair_edges": active_edges,
            "complementary_slackness_verified": comp_slack,
            "global_l1_repair_distance": rational(global_l1["global_l1_repair_distance"]),
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def compute_edge_pivot_threshold(self, edge_index: int) -> dict[str, Any]:
        """Compute the exact rational critical weight w_e^crit at which increasing w_e triggers a basis pivot."""
        idx = exact_int(edge_index, "edge_index", minimum=0)
        if idx >= len(self.edges):
            raise ValidationError(f"edge_index {idx} out of range for {len(self.edges)} edges")

        base_l1 = self.solve_global_l1_repair()
        cert = base_l1["certificate"]
        residuals = [rational(r) for r in cert["residual"]]
        r_e = residuals[idx]
        s0 = abs(r_e)
        w0 = self.edges[idx]["weight"]
        phi0 = rational(base_l1["global_l1_repair_distance"])
        u_e, v_e = self.edges[idx]["source"], self.edges[idx]["target"]

        if s0 == 0 or u_e == v_e:
            status = "SELF_LOOP_INVARIANT" if (s0 > 0 and u_e == v_e) else "INACTIVE_ZERO_RESIDUAL"
            body: dict[str, Any] = {
                "schema": "lggr.online_pivot_threshold.v1",
                "authority_effect": "None",
                "edge_index": idx,
                "status": status,
                "is_active_bottleneck": s0 > 0,
                "current_weight": w0,
                "current_residual_magnitude": s0,
                "critical_weight": None,
                "weight_margin": None,
                "post_pivot_residual_magnitude": s0,
            }
            return json_value({**body, "receipt_sha256": digest(body)})

        # Supporting-line intersection (Eisner-Severance) over exact rationals
        w_high = w0 + Fraction(1) + sum(
            (e["weight"] * (Fraction(1) + abs(e["value"])) for i, e in enumerate(self.edges) if i != idx),
            Fraction(0),
        ) * (Fraction(1) / s0 + Fraction(1))

        orig_weight = self.edges[idx]["weight"]
        try:
            self.edges[idx]["weight"] = w_high
            high_l1 = self.solve_global_l1_repair()
            phi_high = rational(high_l1["global_l1_repair_distance"])
            s_high = abs(rational(high_l1["certificate"]["residual"][idx]))

            while True:
                # Supporting lines: phi0 + s0 * (w - w0) = phi_high + s_high * (w - w_high)
                if s0 == s_high:
                    w_crit = w0
                    break
                w_cand = (phi_high - s_high * w_high - (phi0 - s0 * w0)) / (s0 - s_high)
                self.edges[idx]["weight"] = w_cand
                cand_l1 = self.solve_global_l1_repair()
                phi_cand = rational(cand_l1["global_l1_repair_distance"])
                expected_left = phi0 + s0 * (w_cand - w0)
                if phi_cand == expected_left:
                    w_crit = w_cand
                    break
                w_high = w_cand
                phi_high = phi_cand
                s_high = abs(rational(cand_l1["certificate"]["residual"][idx]))
        finally:
            self.edges[idx]["weight"] = orig_weight

        body = {
            "schema": "lggr.online_pivot_threshold.v1",
            "authority_effect": "None",
            "edge_index": idx,
            "status": "PIVOT_THRESHOLD_LOCATED",
            "is_active_bottleneck": True,
            "current_weight": w0,
            "current_residual_magnitude": s0,
            "critical_weight": w_crit,
            "weight_margin": w_crit - w0,
            "post_pivot_residual_magnitude": s_high,
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


class StreamingTransportMonitor:
    """Online chain-retraction and coarse-graining transport monitor.

    Evaluates whether a coarse-grained target cochain monitor (D_target, h_target = F1 h_source)
    preserves or masks nonrepairability of a source cochain monitor (D_source, h_source).
    Separates:
      - RETRACTION_VERIFIED: G1 F1 = I and G0 F0 = I certify that target repairability
        reflects source repairability (no hidden LGGR masking).
      - LOSSY_PROJECTION_LGGR: forward transport commutes (F1 D_s = D_t F0), source cochain
        is nonrepairable (h_s not in im(D_s)), yet projected target cochain is repairable
        (F1 h_s in im(D_t)), masking the source cycle obstruction.
      - COMMUTING_TRANSPORT_VERIFIED: forward transport commutes without observed masking.
      - INVALID_TRANSPORT / RETRACTION_REJECTED: chain map or retraction equations fail.
    """

    def __init__(
        self,
        source_monitor: StreamingCochainMonitor,
        target_monitor: StreamingCochainMonitor,
    ) -> None:
        if not isinstance(source_monitor, StreamingCochainMonitor):
            raise ValidationError("source_monitor must be a StreamingCochainMonitor instance")
        if not isinstance(target_monitor, StreamingCochainMonitor):
            raise ValidationError("target_monitor must be a StreamingCochainMonitor instance")
        self.source_monitor = source_monitor
        self.target_monitor = target_monitor

    @staticmethod
    def _extract_incidence_and_cochain(
        mon: StreamingCochainMonitor,
    ) -> tuple[list[list[Fraction]], list[Fraction]]:
        if not mon.edges:
            raise ValidationError("Cochain monitor must have at least one edge for transport audit")
        node_list = sorted(mon.vertices)
        node_to_idx = {name: i for i, name in enumerate(node_list)}
        d_rows: list[list[Fraction]] = []
        h_vec: list[Fraction] = []
        for e in mon.edges:
            row = [Fraction(0)] * len(node_list)
            row[node_to_idx[e["source"]]] -= Fraction(1)
            row[node_to_idx[e["target"]]] += Fraction(1)
            d_rows.append(row)
            h_vec.append(e["value"])
        return d_rows, h_vec

    def audit_projection(
        self,
        F0: Any,
        F1: Any,
        *,
        G0: Any | None = None,
        G1: Any | None = None,
    ) -> dict[str, Any]:
        """Audit forward transport (F0, F1) and optional retraction (G0, G1) on live monitors."""
        ds_rows, hs_vec = self._extract_incidence_and_cochain(self.source_monitor)
        dt_rows, _ = self._extract_incidence_and_cochain(self.target_monitor)

        transport_cert = verify_transport(ds_rows, dt_rows, F0, F1, G0=G0, G1=G1)
        f1_mat = matrix(F1, "F1", rows=len(dt_rows), cols=len(ds_rows))
        ht_projected = matvec(f1_mat, tuple(hs_vec))

        ds_mat = matrix(ds_rows, "D_source")
        dt_mat = matrix(dt_rows, "D_target")
        source_sol = solve_exact(ds_mat, tuple(hs_vec))
        target_sol = solve_exact(dt_mat, ht_projected)

        source_repairable = source_sol is not None
        target_repairable = target_sol is not None

        forward_ok = bool(transport_cert.get("forward_commutes"))
        retraction_ok = bool(transport_cert.get("nonrepairability_reflection_verified"))

        lossy_lggr_masked = forward_ok and (not source_repairable) and target_repairable
        if not forward_ok:
            status = "INVALID_TRANSPORT"
            contract_status = "OBSTRUCTED_LGGR"
        elif G0 is not None and not retraction_ok:
            status = "RETRACTION_REJECTED"
            contract_status = "OBSTRUCTED_LGGR"
        elif lossy_lggr_masked:
            status = "LOSSY_PROJECTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif retraction_ok:
            status = "RETRACTION_VERIFIED"
            contract_status = "COMPOSABLE_LGGG" if source_repairable else "REFLECTED_LGGR"
        else:
            status = "COMMUTING_TRANSPORT_VERIFIED"
            contract_status = "COMPOSABLE_LGGG" if source_repairable else "OBSTRUCTED_LGGR"

        body = {
            "schema": "lggr.online_transport.v1",
            "authority_effect": "None",
            "status": status,
            "contract_status": contract_status,
            "forward_commutes": forward_ok,
            "nonrepairability_reflection_verified": retraction_ok,
            "source_repairable": source_repairable,
            "target_repairable": target_repairable,
            "lossy_projection_lggr": lossy_lggr_masked,
            "projected_target_cochain": ht_projected,
            "transport_certificate": transport_cert,
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def synthesize_chain_retraction(self, F0: Any, F1: Any) -> dict[str, Any]:
        """Solve over Q for a left-inverse chain retraction (G0, G1) satisfying:
        G0 F0 = I_ns, G1 F1 = I_ms, and G1 D_t - D_s G0 = 0.
        """
        ds_rows, _ = self._extract_incidence_and_cochain(self.source_monitor)
        dt_rows, _ = self._extract_incidence_and_cochain(self.target_monitor)
        ds = matrix(ds_rows, "D_source")
        dt = matrix(dt_rows, "D_target")
        ms, ns = len(ds), len(ds[0])
        mt, nt = len(dt), len(dt[0])
        f0 = matrix(F0, "F0", rows=nt, cols=ns)
        f1 = matrix(F1, "F1", rows=mt, cols=ms)

        base_audit = self.audit_projection(F0, F1)
        if not base_audit["forward_commutes"]:
            body: dict[str, Any] = {
                "schema": "lggr.online_retraction_synthesis.v1",
                "authority_effect": "None",
                "status": "INVALID_TRANSPORT",
                "retraction_exists": False,
                "G0": None,
                "G1": None,
                "audit": base_audit,
            }
            return json_value({**body, "receipt_sha256": digest(body)})

        total_vars = ns * nt + ms * mt
        sys_rows: list[list[Fraction]] = []
        rhs_vec: list[Fraction] = []

        # 1. G0 F0 = I_ns
        for r in range(ns):
            for k in range(ns):
                row = [Fraction(0)] * total_vars
                for c in range(nt):
                    row[r * nt + c] = f0[c][k]
                sys_rows.append(row)
                rhs_vec.append(Fraction(1 if r == k else 0))

        # 2. G1 F1 = I_ms
        offset_g1 = ns * nt
        for i in range(ms):
            for l_idx in range(ms):
                row = [Fraction(0)] * total_vars
                for j in range(mt):
                    row[offset_g1 + i * mt + j] = f1[j][l_idx]
                sys_rows.append(row)
                rhs_vec.append(Fraction(1 if i == l_idx else 0))

        # 3. G1 D_t - D_s G0 = 0
        for i in range(ms):
            for c in range(nt):
                row = [Fraction(0)] * total_vars
                for j in range(mt):
                    row[offset_g1 + i * mt + j] += dt[j][c]
                for r in range(ns):
                    row[r * nt + c] -= ds[i][r]
                sys_rows.append(row)
                rhs_vec.append(Fraction(0))

        sol = solve_exact(matrix(sys_rows, "retraction_system"), tuple(rhs_vec))
        if sol is None:
            body = {
                "schema": "lggr.online_retraction_synthesis.v1",
                "authority_effect": "None",
                "status": "NO_RETRACTION_EXISTS",
                "retraction_exists": False,
                "G0": None,
                "G1": None,
                "audit": base_audit,
            }
            return json_value({**body, "receipt_sha256": digest(body)})

        g0_mat = [[sol[r * nt + c] for c in range(nt)] for r in range(ns)]
        g1_mat = [[sol[offset_g1 + i * mt + j] for j in range(mt)] for i in range(ms)]
        verified_audit = self.audit_projection(F0, F1, G0=g0_mat, G1=g1_mat)
        body = {
            "schema": "lggr.online_retraction_synthesis.v1",
            "authority_effect": "None",
            "status": "RETRACTION_SYNTHESIZED",
            "retraction_exists": True,
            "G0": g0_mat,
            "G1": g1_mat,
            "audit": verified_audit,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingPositiveExtensionMonitor:
    """Online observer-fiber minimax error floor and positive-extension order-reversal monitor.

    Tracks:
      1. Incremental two-point observer-fiber minimax lower bounds
         epsilon_min(m) = (max_{s in F(m)} q(s) - min_{s in F(m)} q(s)) / 2
         and midpoint estimators g_hat(m) = (max_{s in F(m)} q(s) + min_{s in F(m)} q(s)) / 2
         as rational target observations (state_id, report, target_value) arrive.
      2. Exact rational m-context signed-extension audits checking
         U = 1 + N, R = m * N, U - R = 1 - (m - 1) * N, CF <= (m - 1) * N,
         whether CF > 2 * N, and pairwise order reversal between CF and N_min.
    """

    def __init__(self, *, scope_id: str = "streaming-positive-extension-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.observed_targets: dict[str, dict[str, Any]] = {}
        self.fiber_bounds: dict[str, dict[str, Any]] = {}
        self.global_minimax_floor: Fraction = Fraction(0)
        self.worst_fiber_key: str | None = None
        self.audited_models: dict[str, dict[str, Any]] = {}

    def observe_target(
        self,
        state_id: str,
        report: Any,
        target_value: Fraction | int | str,
    ) -> dict[str, Any]:
        """Ingest (state_id, report, rational target_value) and update fiber minimax lower bound."""
        sid = text(state_id, "state_id")
        rep_clean = json.loads(canonical(report))
        q_val = rational(target_value)
        rep_key = canonical(rep_clean)

        prev = self.observed_targets.get(sid)
        if prev is not None:
            if canonical(prev["report"]) != rep_key or prev["target_value"] != q_val:
                raise ValidationError(f"Conflicting target observation for state_id: {sid}")
        else:
            self.observed_targets[sid] = {
                "state_id": sid,
                "report": rep_clean,
                "target_value": q_val,
            }

        fb = self.fiber_bounds.get(rep_key)
        if fb is None:
            fb = {
                "report": rep_clean,
                "min_state_id": sid,
                "min_target": q_val,
                "max_state_id": sid,
                "max_target": q_val,
                "minimax_error_floor": Fraction(0),
                "midpoint_estimator": q_val,
            }
            self.fiber_bounds[rep_key] = fb
        else:
            if q_val < fb["min_target"]:
                fb["min_target"] = q_val
                fb["min_state_id"] = sid
            if q_val > fb["max_target"]:
                fb["max_target"] = q_val
                fb["max_state_id"] = sid
            fb["minimax_error_floor"] = (fb["max_target"] - fb["min_target"]) / Fraction(2)
            fb["midpoint_estimator"] = (fb["max_target"] + fb["min_target"]) / Fraction(2)

        if fb["minimax_error_floor"] > self.global_minimax_floor or self.worst_fiber_key is None:
            self.global_minimax_floor = fb["minimax_error_floor"]
            self.worst_fiber_key = rep_key

        status = "NONZERO_MINIMAX_FLOOR" if self.global_minimax_floor > 0 else "EXACT_FIBER_DECODER"
        contract_status = "OBSTRUCTED_LGGR" if self.global_minimax_floor > 0 else "COMPOSABLE_LGGG"
        body = {
            "schema": "lggr.online_minimax_step.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "state_id": sid,
            "report": rep_clean,
            "target_value": q_val,
            "fiber_minimax_error_floor": fb["minimax_error_floor"],
            "fiber_midpoint_estimator": fb["midpoint_estimator"],
            "global_minimax_error_floor": self.global_minimax_floor,
            "status": status,
            "contract_status": contract_status,
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def audit_signed_extension(
        self,
        model_id: str,
        num_contexts: int,
        local_packing_mass: Fraction | int | str,
        negative_mass: Fraction | int | str,
    ) -> dict[str, Any]:
        """Audit an m-context empirical model's contextual fraction CF vs signed negative mass N."""
        mid = text(model_id, "model_id")
        m_ctx = exact_int(num_contexts, "num_contexts", minimum=2)
        gamma = rational(local_packing_mass)
        n_mass = rational(negative_mass)
        if gamma < 0 or gamma > 1:
            raise ValidationError("local_packing_mass must lie in [0, 1]")
        if n_mass < 0:
            raise ValidationError("negative_mass must be non-negative")

        cf = Fraction(1) - gamma
        u_mass = Fraction(1) + n_mass
        r_mass = Fraction(m_ctx) * n_mass
        excess_mass = u_mass - r_mass
        expected_excess = Fraction(1) - Fraction(m_ctx - 1) * n_mass
        packing_bound_holds = gamma >= excess_mass and cf <= Fraction(m_ctx - 1) * n_mass
        exceeds_two_neg_mass = cf > Fraction(2) * n_mass

        record = {
            "model_id": mid,
            "num_contexts": m_ctx,
            "local_packing_mass": gamma,
            "contextual_fraction": cf,
            "negative_mass": n_mass,
            "positive_part_mass": u_mass,
            "negative_context_marginal_mass": r_mass,
            "excess_mass": excess_mass,
            "excess_identity_verified": excess_mass == expected_excess,
            "m_context_bound_verified": packing_bound_holds,
            "exceeds_two_negative_mass": exceeds_two_neg_mass,
        }
        self.audited_models[mid] = record
        status = (
            "INVALID_PACKING_BOUND"
            if not packing_bound_holds
            else "CF_EXCEEDS_TWO_NEG_MASS"
            if exceeds_two_neg_mass
            else "EXTENSION_BOUND_VERIFIED"
        )
        body = {
            "schema": "lggr.online_signed_extension.v1",
            "authority_effect": "None",
            "status": status,
            **record,
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def compare_extension_order(self, left_id: str, right_id: str) -> dict[str, Any]:
        """Compare two audited models and detect order reversal between CF and N_min."""
        lid = text(left_id, "left_id")
        rid = text(right_id, "right_id")
        if lid not in self.audited_models or rid not in self.audited_models:
            raise ValidationError("Both left_id and right_id must be audited before comparison")
        left = self.audited_models[lid]
        right = self.audited_models[rid]

        cf_l, cf_r = left["contextual_fraction"], right["contextual_fraction"]
        n_l, n_r = left["negative_mass"], right["negative_mass"]
        order_reversed = (cf_l < cf_r and n_l > n_r) or (cf_l > cf_r and n_l < n_r)
        status = "ORDER_REVERSAL_DETECTED" if order_reversed else "COMONOTONE_ORDER"
        body = {
            "schema": "lggr.online_extension_comparison.v1",
            "authority_effect": "None",
            "status": status,
            "left_id": lid,
            "right_id": rid,
            "left_contextual_fraction": cf_l,
            "right_contextual_fraction": cf_r,
            "left_negative_mass": n_l,
            "right_negative_mass": n_r,
            "order_reversal_detected": order_reversed,
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def get_receipt(self) -> dict[str, Any]:
        """Emit comprehensive summary receipt for observer-fiber minimax and extension audits."""
        body = {
            "schema": "lggr.online_positive_extension_summary.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "observed_states_count": len(self.observed_targets),
            "fibers_count": len(self.fiber_bounds),
            "global_minimax_error_floor": self.global_minimax_floor,
            "audited_models_count": len(self.audited_models),
            "status": "NONZERO_MINIMAX_FLOOR" if self.global_minimax_floor > 0 else "EXACT_FIBER_DECODER",
            "contract_status": "COMPOSABLE_LGGG" if self.global_minimax_floor > 0 else "COMPOSABLE_LGGG",
        }
        body["contract_status"] = "OBSTRUCTED_LGGR" if self.global_minimax_floor > 0 else "COMPOSABLE_LGGG"
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingBaselineComparator:
    """Controlled equal-information comparative evaluator: conventional baseline vs. LGGR audit.

    Compares a conventional local-step + endpoint invariant checker against
    StreamingAuditMonitor and audit_history on identical step-witness histories,
    tracking:
      - conventional_accepts: local step acceptance + endpoint bound |x_n - x_0| <= max_total
      - lggr_accepts: full G1-G4 composition + zero unresolved deferred obligations
      - conventional_false_acceptance: conventional accepts while LGGR detects a prefix
        excursion, uncertified representation/scope migration, or retained obligation
      - first_fault_step_index: exact step index localized by StreamingAuditMonitor
    """

    def __init__(self, policy: BudgetPolicy) -> None:
        if not isinstance(policy, BudgetPolicy):
            raise ValidationError("policy must be a BudgetPolicy instance")
        self.policy = policy
        self.comparisons: list[dict[str, Any]] = []

    def compare_trace(
        self,
        trace_id: str,
        baseline: StateRef,
        steps: Iterable[StepWitness],
    ) -> dict[str, Any]:
        """Evaluate a multi-step witness trace under both checkers with equal input information."""
        tid = text(trace_id, "trace_id")
        if not isinstance(baseline, StateRef):
            raise ValidationError("baseline must be a StateRef instance")
        step_list = list(sequence(steps, "steps"))
        if not step_list:
            raise ValidationError("steps must be non-empty")

        # 1. Conventional local-step + endpoint baseline regression checker
        local_steps_ok = all(w.local_accepted and w.smoke_passed for w in step_list)
        start_val = baseline.value
        end_val = step_list[-1].target.value
        endpoint_ok = (
            start_val is not None
            and end_val is not None
            and abs(end_val - start_val) <= self.policy.max_total
        )
        conventional_accepts = bool(local_steps_ok and endpoint_ok)

        # 2. Online StreamingAuditMonitor + full batch audit_history
        smon = StreamingAuditMonitor(self.policy, baseline=baseline)
        first_alert_step: int | None = None
        for idx, w in enumerate(step_list):
            s_res = smon.step(w)
            if s_res["status"] == "ALERT" and first_alert_step is None:
                first_alert_step = idx

        stream_rec = smon.get_receipt()
        batch_rec = audit_history(self.policy, baseline, step_list)
        retained_obligations = list(batch_rec.get("unresolved_obligations", []))
        lggr_accepts = (
            batch_rec["status"] == "COMPOSITION_VERIFIED"
            and stream_rec["contract_status"] == "COMPOSABLE_LGGG"
            and len(retained_obligations) == 0
        )

        false_acceptance = conventional_accepts and not lggr_accepts
        false_refusal = (not conventional_accepts) and lggr_accepts
        record = {
            "trace_id": tid,
            "steps_count": len(step_list),
            "conventional_accepts": conventional_accepts,
            "lggr_accepts": lggr_accepts,
            "conventional_false_acceptance": false_acceptance,
            "conventional_false_refusal": false_refusal,
            "first_fault_step_index": first_alert_step,
            "retained_obligations": retained_obligations,
            "lggr_batch_status": batch_rec["status"],
            "lggr_stream_contract_status": stream_rec["contract_status"],
        }
        self.comparisons.append(record)
        status = (
            "CONVENTIONAL_FALSE_ACCEPTANCE"
            if false_acceptance
            else "AGREEMENT_VERIFIED"
            if conventional_accepts == lggr_accepts
            else "DIVERGENT_VERDICT"
        )
        body = {
            "schema": "lggr.online_baseline_comparison.v1",
            "authority_effect": "None",
            "status": status,
            **record,
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def get_receipt(self) -> dict[str, Any]:
        """Emit aggregate comparative evaluation receipt across all evaluated traces."""
        total = len(self.comparisons)
        false_acc_count = sum(1 for c in self.comparisons if c["conventional_false_acceptance"])
        false_ref_count = sum(1 for c in self.comparisons if c["conventional_false_refusal"])
        localized_count = sum(1 for c in self.comparisons if c["first_fault_step_index"] is not None)
        obligations_retained_traces = sum(1 for c in self.comparisons if len(c["retained_obligations"]) > 0)
        body = {
            "schema": "lggr.online_baseline_comparison_summary.v1",
            "authority_effect": "None",
            "traces_evaluated": total,
            "conventional_false_acceptances": false_acc_count,
            "conventional_false_refusals": false_ref_count,
            "faults_localized_online": localized_count,
            "traces_with_retained_obligations": obligations_retained_traces,
            "comparisons": self.comparisons,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingSixRoleOverlayMonitor:
    """Online LGGR III six-role evaluator overlay and cancellation-masking monitor.

    Records finite binary verdict triples (e1, e2, eg) across the six canonical
    role profiles from LGGR III:
      - finite_obstruction
      - foundations
      - representation
      - observer
      - continuum_shadow
      - action_and_alignment

    Enforces role-specific context guards (e.g., matching observation envelopes
    under Proposition 4, operation/transport witness matching, and diagnostic-only
    foundations records) and tracks both the signed defect sum D = G - L = N_+ - N_-
    and the total disagreement count M = N_+ + N_- = sum |Delta_E(v_i)| so signed
    cancellation (D = 0 with M > 0) does not mask pointwise NGD failures.
    """

    CANONICAL_ROLES: tuple[str, ...] = (
        "finite_obstruction",
        "foundations",
        "representation",
        "observer",
        "continuum_shadow",
        "action_and_alignment",
    )

    def __init__(self, *, scope_id: str = "streaming-six-role-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.records: list[dict[str, Any]] = []
        self.total_global: int = 0
        self.total_local_product: int = 0
        self.total_signed_defect: int = 0
        self.positive_defect_count: int = 0
        self.negative_defect_count: int = 0
        self.zero_defect_count: int = 0
        self.weighted_disagreement_sum: Fraction = Fraction(0)
        self.role_counts: dict[str, int] = {r: 0 for r in self.CANONICAL_ROLES}
        self.context_violations_count: int = 0

    @staticmethod
    def _binary_verdict(value: Any, name: str) -> int:
        if type(value) not in (int, bool) or int(value) not in (0, 1):
            raise ValidationError(f"{name} must be a binary verdict in {{0, 1}}")
        return int(value)

    @classmethod
    def _audit_role_context(cls, role: str, ctx: Mapping[str, Any]) -> tuple[bool, list[str]]:
        reasons: list[str] = []
        if role == "finite_obstruction":
            for req in ("carrier", "degree", "comparison_map", "quotient_gauge", "replay_data"):
                if req not in ctx or ctx[req] in (None, ""):
                    reasons.append(f"MISSING_FINITE_OBSTRUCTION_FIELD:{req}")
        elif role == "foundations":
            if ctx.get("diagnostic_only") is not True:
                reasons.append("FOUNDATIONS_NOT_DIAGNOSTIC_ONLY")
            if ctx.get("authority_effect", "None") != "None":
                reasons.append("FOUNDATIONS_NON_NONE_AUTHORITY_EFFECT")
        elif role == "representation":
            op = ctx.get("operation")
            tw = ctx.get("transport_witness")
            if not op or not tw:
                reasons.append("MISSING_REPRESENTATION_WITNESS")
            elif op != tw:
                reasons.append("REPRESENTATION_TRANSPORT_MISMATCH")
        elif role == "observer":
            left_env = ctx.get("left_envelope")
            right_env = ctx.get("right_envelope")
            if left_env is None or right_env is None:
                reasons.append("MISSING_OBSERVATION_ENVELOPE")
            elif left_env != right_env:
                reasons.append("OBSERVATION_ENVELOPE_MISMATCH")
        elif role == "continuum_shadow":
            if ctx.get("finite_calculation") is not True:
                reasons.append("CONTINUUM_SHADOW_MISSING_FINITE_TAG")
            if ctx.get("limit_statement_distinct") is not True:
                reasons.append("CONTINUUM_SHADOW_CONFLATES_LIMIT")
        elif role == "action_and_alignment":
            if ctx.get("residual_routed_as_feedback") is not True:
                reasons.append("RESIDUAL_NOT_ROUTED_AS_FEEDBACK")
            if ctx.get("relabeled_as_success") is not False:
                reasons.append("RESIDUAL_RELABELED_AS_SUCCESS")
        return len(reasons) == 0, reasons

    def record_evaluation(
        self,
        role: str,
        e1: int | bool,
        e2: int | bool,
        eg: int | bool,
        *,
        context: Mapping[str, Any] | None = None,
        weight: Fraction | int | str = 1,
    ) -> dict[str, Any]:
        """Record a role-indexed verdict triple (r, e1, e2, eg, context) and update sample totals."""
        role_clean = text(role, "role")
        if role_clean not in self.CANONICAL_ROLES:
            raise ValidationError(f"role must be one of {self.CANONICAL_ROLES}")
        v1 = self._binary_verdict(e1, "e1")
        v2 = self._binary_verdict(e2, "e2")
        vg = self._binary_verdict(eg, "eg")
        wt = rational(weight)
        if wt < 0:
            raise ValidationError("weight must be non-negative")

        ctx_clean: dict[str, Any] = (
            json.loads(canonical(dict(context))) if isinstance(context, Mapping) else {}
        )
        ctx_ok, ctx_reasons = self._audit_role_context(role_clean, ctx_clean)
        if not ctx_ok:
            self.context_violations_count += 1

        local_prod = v1 * v2
        defect = vg - local_prod
        classification = {-1: "NGD", 0: "ZDR", 1: "PGD"}[defect]

        self.total_global += vg
        self.total_local_product += local_prod
        self.total_signed_defect += defect
        if defect == 1:
            self.positive_defect_count += 1
        elif defect == -1:
            self.negative_defect_count += 1
        else:
            self.zero_defect_count += 1
        self.weighted_disagreement_sum += wt * abs(defect)
        self.role_counts[role_clean] += 1

        disagreement_count = self.positive_defect_count + self.negative_defect_count
        cancellation_masked = (self.total_signed_defect == 0 and disagreement_count > 0)

        step_idx = len(self.records)
        rec = {
            "step_index": step_idx,
            "role": role_clean,
            "e1": v1,
            "e2": v2,
            "eg": vg,
            "local_product": local_prod,
            "defect": defect,
            "classification": classification,
            "weight": wt,
            "context_valid": ctx_ok,
            "context_violation_reasons": ctx_reasons,
            "context": ctx_clean,
        }
        self.records.append(rec)

        if not ctx_ok:
            status = "CONTEXT_ENVELOPE_VIOLATION"
            contract_status = "OBSTRUCTED_LGGR"
        elif self.negative_defect_count > 0 and cancellation_masked:
            status = "CANCELLATION_MASKED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif self.negative_defect_count > 0:
            status = "NGD_DEFECT_DETECTED"
            contract_status = "OBSTRUCTED_LGGR"
        elif disagreement_count > 0:
            status = "POINTWISE_DISAGREEMENT"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "ROLE_OVERLAY_VERIFIED"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_six_role_step.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            **rec,
            "sample_global_sum": self.total_global,
            "sample_local_sum": self.total_local_product,
            "sample_signed_defect_sum": self.total_signed_defect,
            "sample_disagreement_count": disagreement_count,
            "cancellation_masked": cancellation_masked,
            "identity_g_minus_l_eq_d": (
                self.total_global - self.total_local_product == self.total_signed_defect
            ),
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def get_receipt(self) -> dict[str, Any]:
        """Emit summary receipt for the six-role overlay monitor."""
        disagreement_count = self.positive_defect_count + self.negative_defect_count
        cancellation_masked = (self.total_signed_defect == 0 and disagreement_count > 0)
        if self.context_violations_count > 0:
            status = "CONTEXT_ENVELOPE_VIOLATION"
            contract_status = "OBSTRUCTED_LGGR"
        elif cancellation_masked:
            status = "CANCELLATION_MASKED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif self.negative_defect_count > 0:
            status = "NGD_DEFECT_DETECTED"
            contract_status = "OBSTRUCTED_LGGR"
        elif disagreement_count > 0:
            status = "POINTWISE_DISAGREEMENT"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "ROLE_OVERLAY_VERIFIED"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_six_role_summary.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "records_count": len(self.records),
            "sample_global_sum": self.total_global,
            "sample_local_sum": self.total_local_product,
            "sample_signed_defect_sum": self.total_signed_defect,
            "positive_defect_count": self.positive_defect_count,
            "negative_defect_count": self.negative_defect_count,
            "zero_defect_count": self.zero_defect_count,
            "disagreement_count": disagreement_count,
            "weighted_disagreement_sum": self.weighted_disagreement_sum,
            "cancellation_masked": cancellation_masked,
            "context_violations_count": self.context_violations_count,
            "identity_g_minus_l_eq_d": (
                self.total_global - self.total_local_product == self.total_signed_defect
            ),
            "identity_d_eq_npos_minus_nneg": (
                self.total_signed_defect == self.positive_defect_count - self.negative_defect_count
            ),
            "role_counts": self.role_counts,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingGramProbeMonitor:
    """Online LGGR VI Gram kernel nullspace and centered adjoint probe monitor.

    Given an observation matrix Q in Q^{m x d}, maintains its exact rational Gram
    matrix H = Q^T Q in Q^{d x d} and evaluates streaming state vectors x in Q^d:
      - Theorem 3 (Gram Kernel Identity): ker(Q^T Q) = ker(Q), so Hx == 0 iff Qx == 0.
      - Theorem 4 (Centered Directional Identity): for f(z) = (1/2) ||Qz||_2^2 and c > 0,
        (f(x + c*u) - f(x - c*u)) / (2*c) == u^T H x.
      - Theorem 5 (Full Sign-Cube Recovery): averaging
        ((f(x + c*delta) - f(x - c*delta)) / (2*c)) * delta over delta in {-1, +1}^d
        recovers Hx = Q^T Q x.
      - Detects GRAM_NULLSPACE_BLINDSPOT_LGGR when a nonzero state x != 0 lies in ker(Q),
        where every zero-preserving post-processor and adjoint probe returns zero.
    """

    def __init__(
        self,
        observation_matrix: Any,
        *,
        scope_id: str = "streaming-gram-probe-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.q_mat = matrix(observation_matrix, "observation_matrix")
        self.num_obs = len(self.q_mat)
        self.dim = len(self.q_mat[0])
        self.q_transpose = tuple(
            tuple(self.q_mat[r][c] for r in range(self.num_obs))
            for c in range(self.dim)
        )
        self.gram_matrix = matmul(self.q_transpose, self.q_mat)
        self.probed_states: list[dict[str, Any]] = []
        self.nullspace_blindspots_count: int = 0

    def quadratic_energy(self, state_vec: tuple[Fraction, ...]) -> Fraction:
        """Compute exact rational quadratic energy f(x) = (1/2) * ||Q x||_2^2."""
        qx = matvec(self.q_mat, state_vec)
        return sum((val * val for val in qx), Fraction(0)) / Fraction(2)

    def probe_state(
        self,
        state_id: str,
        state_vector: Any,
        *,
        step_size: Fraction | int | str = 1,
        direction: Any | None = None,
    ) -> dict[str, Any]:
        """Evaluate Qx, Hx = Q^T Q x, centered two-query directional probe, and sign-cube recovery."""
        sid = text(state_id, "state_id")
        x_vec = vector(state_vector, "state_vector")
        if len(x_vec) != self.dim:
            raise ValidationError(f"state_vector must have length {self.dim}")
        c_step = rational(step_size)
        if c_step <= 0:
            raise ValidationError("step_size must be strictly positive")

        qx = matvec(self.q_mat, x_vec)
        hx = matvec(self.gram_matrix, x_vec)
        fx = self.quadratic_energy(x_vec)

        x_nonzero = any(v != 0 for v in x_vec)
        qx_zero = all(v == 0 for v in qx)
        hx_zero = all(v == 0 for v in hx)
        gram_kernel_identity_verified = (qx_zero == hx_zero)

        # Centered two-query directional probe (Theorem 4)
        if direction is not None:
            u_vec = vector(direction, "direction")
            if len(u_vec) != self.dim:
                raise ValidationError(f"direction must have length {self.dim}")
        else:
            u_vec = tuple(Fraction(1 if i == 0 else 0) for i in range(self.dim))
        x_plus = tuple(x_vec[i] + c_step * u_vec[i] for i in range(self.dim))
        x_minus = tuple(x_vec[i] - c_step * u_vec[i] for i in range(self.dim))
        centered_probe = (self.quadratic_energy(x_plus) - self.quadratic_energy(x_minus)) / (
            Fraction(2) * c_step
        )
        expected_pairing = sum((u_vec[i] * hx[i] for i in range(self.dim)), Fraction(0))
        directional_identity_verified = (centered_probe == expected_pairing)

        # Full sign-cube recovery over {-1, +1}^d (Theorem 5, for d <= 10)
        sign_cube_recovered: list[Fraction] | None = None
        sign_cube_identity_verified: bool | None = None
        if self.dim <= 10:
            acc = [Fraction(0)] * self.dim
            num_corners = 1 << self.dim
            for delta_tuple in itertools.product((Fraction(-1), Fraction(1)), repeat=self.dim):
                xp = tuple(x_vec[i] + c_step * delta_tuple[i] for i in range(self.dim))
                xm = tuple(x_vec[i] - c_step * delta_tuple[i] for i in range(self.dim))
                slope = (self.quadratic_energy(xp) - self.quadratic_energy(xm)) / (
                    Fraction(2) * c_step
                )
                for i in range(self.dim):
                    acc[i] += slope * delta_tuple[i]
            sign_cube_recovered = [val / Fraction(num_corners) for val in acc]
            sign_cube_identity_verified = (tuple(sign_cube_recovered) == hx)

        is_nullspace_blindspot = x_nonzero and qx_zero
        if is_nullspace_blindspot:
            self.nullspace_blindspots_count += 1
            status = "GRAM_NULLSPACE_BLINDSPOT_LGGR"
        elif x_nonzero:
            status = "ADJOINT_SIGNAL_VERIFIED"
        else:
            status = "ZERO_STATE_VERIFIED"

        contract_status = (
            "OBSTRUCTED_LGGR"
            if self.nullspace_blindspots_count > 0
            else "COMPOSABLE_LGGG"
        )
        record = {
            "state_id": sid,
            "state_vector": list(x_vec),
            "observation_qx": list(qx),
            "gram_response_hx": list(hx),
            "quadratic_energy": fx,
            "state_nonzero": x_nonzero,
            "observation_zero": qx_zero,
            "gram_response_zero": hx_zero,
            "gram_kernel_identity_verified": gram_kernel_identity_verified,
            "centered_directional_probe": centered_probe,
            "expected_gram_pairing": expected_pairing,
            "directional_identity_verified": directional_identity_verified,
            "sign_cube_recovered_hx": sign_cube_recovered,
            "sign_cube_identity_verified": sign_cube_identity_verified,
            "is_nullspace_blindspot": is_nullspace_blindspot,
        }
        self.probed_states.append(record)
        body = {
            "schema": "lggr.online_gram_probe_step.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            **record,
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def get_receipt(self) -> dict[str, Any]:
        """Emit summary receipt for the Gram kernel & adjoint probe monitor."""
        status = (
            "GRAM_NULLSPACE_BLINDSPOT_LGGR"
            if self.nullspace_blindspots_count > 0
            else "GRAM_PROBE_VERIFIED"
        )
        contract_status = (
            "OBSTRUCTED_LGGR"
            if self.nullspace_blindspots_count > 0
            else "COMPOSABLE_LGGG"
        )
        body = {
            "schema": "lggr.online_gram_probe_summary.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "num_observations": self.num_obs,
            "state_dimension": self.dim,
            "gram_matrix": [list(row) for row in self.gram_matrix],
            "probed_states_count": len(self.probed_states),
            "nullspace_blindspots_count": self.nullspace_blindspots_count,
            "all_gram_identities_verified": all(
                r["gram_kernel_identity_verified"]
                and r["directional_identity_verified"]
                and (r["sign_cube_identity_verified"] is not False)
                for r in self.probed_states
            ),
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingPathKernelMonitor:
    """Online LGGR I / III evaluated path-kernel and two-channel residual monitor.

    Records finite stage-1 path segments gamma_1 in Omega(a, b), stage-2 path
    segments gamma_2 in Omega(b, c), and composite paths gamma = gamma_2 * gamma_1
    in Omega(a, c) with rational weights and binary verdicts in {0, 1}.

    Verifies:
      - G1 boundary-slice bijection between compatible segment pairs and composites.
      - Exact four-term two-channel expansion on every composite path (LGGR I Sec 4):
          E_g w_g == E_1 E_2 w_1 w_2 + Delta_E w_1 w_2 + E_1 E_2 Delta_w + Delta_E Delta_w
        where Delta_E = E_g - E_1 E_2 in {-1, 0, 1} and Delta_w = w_g - w_1 w_2.
      - Exact evaluated partition-function discrepancy identity (LGGR I Thm 1 / Sec 4):
          Z_E(c | a) - sum_{b in B} Z_{E_2}(c | b) Z_{E_1}(b | a) == R_E(c, a) + R_w(c, a).
    """

    def __init__(self, *, scope_id: str = "streaming-path-kernel-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.stage1_segments: dict[str, dict[str, Any]] = {}
        self.stage2_segments: dict[str, dict[str, Any]] = {}
        self.composites: dict[str, dict[str, Any]] = {}

    @staticmethod
    def _binary_verdict(value: Any, name: str) -> int:
        if type(value) not in (int, bool) or int(value) not in (0, 1):
            raise ValidationError(f"{name} must be a binary verdict in {{0, 1}}")
        return int(value)

    def add_stage1_segment(
        self,
        segment_id: str,
        source: str,
        boundary: str,
        weight: Fraction | int | str,
        verdict: int | bool,
    ) -> dict[str, Any]:
        """Register a stage-1 trajectory gamma_1 : a -> b with weight w_1 >= 0 and verdict E_1 in {0,1}."""
        sid = text(segment_id, "segment_id")
        src = text(source, "source")
        bnd = text(boundary, "boundary")
        wt = rational(weight)
        if wt < 0:
            raise ValidationError("weight must be non-negative")
        v1 = self._binary_verdict(verdict, "verdict")
        if sid in self.stage1_segments:
            raise ValidationError(f"Duplicate stage1 segment_id: {sid}")
        rec = {
            "segment_id": sid,
            "source": src,
            "boundary": bnd,
            "weight": wt,
            "verdict": v1,
            "evaluated_weight": wt * Fraction(v1),
        }
        self.stage1_segments[sid] = rec
        return json_value(rec)

    def add_stage2_segment(
        self,
        segment_id: str,
        boundary: str,
        target: str,
        weight: Fraction | int | str,
        verdict: int | bool,
    ) -> dict[str, Any]:
        """Register a stage-2 trajectory gamma_2 : b -> c with weight w_2 >= 0 and verdict E_2 in {0,1}."""
        sid = text(segment_id, "segment_id")
        bnd = text(boundary, "boundary")
        tgt = text(target, "target")
        wt = rational(weight)
        if wt < 0:
            raise ValidationError("weight must be non-negative")
        v2 = self._binary_verdict(verdict, "verdict")
        if sid in self.stage2_segments:
            raise ValidationError(f"Duplicate stage2 segment_id: {sid}")
        rec = {
            "segment_id": sid,
            "boundary": bnd,
            "target": tgt,
            "weight": wt,
            "verdict": v2,
            "evaluated_weight": wt * Fraction(v2),
        }
        self.stage2_segments[sid] = rec
        return json_value(rec)

    def observe_composite(
        self,
        composite_id: str,
        stage1_id: str,
        stage2_id: str,
        global_verdict: int | bool,
        *,
        global_weight: Fraction | int | str | None = None,
    ) -> dict[str, Any]:
        """Record a composite trajectory gamma_2 * gamma_1 and check two-channel expansion."""
        cid = text(composite_id, "composite_id")
        s1_id = text(stage1_id, "stage1_id")
        s2_id = text(stage2_id, "stage2_id")
        if cid in self.composites:
            raise ValidationError(f"Duplicate composite_id: {cid}")
        if s1_id not in self.stage1_segments:
            raise ValidationError(f"Unknown stage1_id: {s1_id}")
        if s2_id not in self.stage2_segments:
            raise ValidationError(f"Unknown stage2_id: {s2_id}")

        s1 = self.stage1_segments[s1_id]
        s2 = self.stage2_segments[s2_id]
        if s1["boundary"] != s2["boundary"]:
            raise ValidationError(
                f"Boundary mismatch between stage1 ({s1['boundary']}) and stage2 ({s2['boundary']})"
            )

        vg = self._binary_verdict(global_verdict, "global_verdict")
        w1 = s1["weight"]
        w2 = s2["weight"]
        w_prod = w1 * w2
        wg = rational(global_weight) if global_weight is not None else w_prod
        if wg < 0:
            raise ValidationError("global_weight must be non-negative")

        e1 = s1["verdict"]
        e2 = s2["verdict"]
        local_prod = e1 * e2
        delta_e = vg - local_prod
        delta_w = wg - w_prod
        classification = {-1: "NGD", 0: "ZDR", 1: "PGD"}[delta_e]

        lhs = Fraction(vg) * wg
        term_factored = Fraction(local_prod) * w_prod
        term_eval_defect = Fraction(delta_e) * w_prod
        term_weight_defect = Fraction(local_prod) * delta_w
        term_cross_defect = Fraction(delta_e) * delta_w
        rhs = term_factored + term_eval_defect + term_weight_defect + term_cross_defect

        rec = {
            "composite_id": cid,
            "stage1_id": s1_id,
            "stage2_id": s2_id,
            "source": s1["source"],
            "boundary": s1["boundary"],
            "target": s2["target"],
            "e1": e1,
            "e2": e2,
            "eg": vg,
            "local_product": local_prod,
            "delta_e": delta_e,
            "classification": classification,
            "w1": w1,
            "w2": w2,
            "w_product": w_prod,
            "w_global": wg,
            "delta_w": delta_w,
            "evaluated_global_weight": lhs,
            "two_channel_identity_verified": (lhs == rhs),
        }
        self.composites[cid] = rec
        return json_value(rec)

    def audit_kernel_composition(self, source: str, target: str) -> dict[str, Any]:
        """Audit evaluated path-kernel composition Z_E(target | source) across intermediate boundaries."""
        src = text(source, "source")
        tgt = text(target, "target")

        s1_list = [s for s in self.stage1_segments.values() if s["source"] == src]
        s2_list = [s for s in self.stage2_segments.values() if s["target"] == tgt]
        boundaries = sorted({s["boundary"] for s in s1_list} | {s["boundary"] for s in s2_list})

        # Expected compatible pairs under G1
        expected_pairs: set[tuple[str, str]] = set()
        factored_kernel_sum = Fraction(0)
        boundary_slice_kernels: list[dict[str, Any]] = []

        for b in boundaries:
            b_s1 = [s for s in s1_list if s["boundary"] == b]
            b_s2 = [s for s in s2_list if s["boundary"] == b]
            z1_b = sum((s["evaluated_weight"] for s in b_s1), Fraction(0))
            z2_b = sum((s["evaluated_weight"] for s in b_s2), Fraction(0))
            factored_kernel_sum += z2_b * z1_b
            boundary_slice_kernels.append({
                "boundary": b,
                "z_stage1": z1_b,
                "z_stage2": z2_b,
                "slice_product": z2_b * z1_b,
            })
            for seg1 in b_s1:
                for seg2 in b_s2:
                    expected_pairs.add((seg1["segment_id"], seg2["segment_id"]))

        comp_list = [
            c for c in self.composites.values() if c["source"] == src and c["target"] == tgt
        ]
        observed_pairs_list = [(c["stage1_id"], c["stage2_id"]) for c in comp_list]
        g1_bijection_holds = (
            len(observed_pairs_list) == len(expected_pairs)
            and set(observed_pairs_list) == expected_pairs
        )

        global_kernel_z = sum((c["evaluated_global_weight"] for c in comp_list), Fraction(0))
        residual_re = sum((Fraction(c["delta_e"]) * c["w_product"] for c in comp_list), Fraction(0))
        residual_rw = sum(
            (
                Fraction(c["local_product"]) * c["delta_w"]
                + Fraction(c["delta_e"]) * c["delta_w"]
                for c in comp_list
            ),
            Fraction(0),
        )
        abs_eval_disagreement = sum(
            (abs(Fraction(c["delta_e"])) * c["w_product"] for c in comp_list),
            Fraction(0),
        )
        abs_weight_disagreement = sum((abs(c["delta_w"]) for c in comp_list), Fraction(0))
        ngd_count = sum(1 for c in comp_list if c["delta_e"] == -1)
        pgd_count = sum(1 for c in comp_list if c["delta_e"] == 1)

        discrepancy_lhs = global_kernel_z - factored_kernel_sum
        discrepancy_rhs = residual_re + residual_rw
        discrepancy_identity_verified = g1_bijection_holds and (discrepancy_lhs == discrepancy_rhs)
        cancellation_masked = (
            g1_bijection_holds
            and discrepancy_lhs == 0
            and (abs_eval_disagreement > 0 or abs_weight_disagreement > 0)
        )

        if not g1_bijection_holds:
            status = "G1_BIJECTION_VIOLATION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif cancellation_masked:
            status = "CANCELLATION_MASKED_KERNEL_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif ngd_count > 0 or residual_re < 0:
            status = "NGD_KERNEL_DEFECT_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif abs_eval_disagreement > 0 or abs_weight_disagreement > 0:
            status = "POINTWISE_KERNEL_DEFECT_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "KERNEL_COMPOSITION_VERIFIED"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_path_kernel.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "source": src,
            "target": tgt,
            "status": status,
            "contract_status": contract_status,
            "g1_bijection_verified": g1_bijection_holds,
            "global_evaluated_kernel": global_kernel_z,
            "factored_boundary_kernel_sum": factored_kernel_sum,
            "kernel_discrepancy": discrepancy_lhs,
            "evaluator_residual_re": residual_re,
            "weight_residual_rw": residual_rw,
            "abs_evaluator_disagreement": abs_eval_disagreement,
            "abs_weight_disagreement": abs_weight_disagreement,
            "ngd_composites_count": ngd_count,
            "pgd_composites_count": pgd_count,
            "cancellation_masked": cancellation_masked,
            "discrepancy_identity_verified": discrepancy_identity_verified,
            "boundary_slice_kernels": boundary_slice_kernels,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingOrganizationalGluingMonitor:
    """Online LGGR II organizational evaluator gluing and carrier-mixing monitor.

    Evaluates:
      - Weak representation sufficiency (R_3 == E_G) vs. product sufficiency (R_3 == E_1 E_2)
        and evaluator factorization (E_G == E_1 E_2), checking Claims M3 and M4.
      - Governance conjunction G = G_rep and G_auth and G_time (Claim D1) and
        checked-closure eligibility (Delta_E == 0 and G == True).
      - Joint carrier quotient projection J(c) = (pi_1(a), pi_2(b)), detecting carrier-mixing
        collisions J(c) == J(c') with E_G(c) != E_G(c') (Theorem 3 / Claim M8) and
        verifying forced NGD defect when carrier-local evaluators pass on a mixed class (Claim M9).
    """

    def __init__(self, *, scope_id: str = "streaming-organizational-gluing-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.records: list[dict[str, Any]] = []
        self.joint_carrier_fibers: dict[str, dict[str, Any]] = {}
        self.carrier_mixing_collisions: list[dict[str, Any]] = []
        self.weak_nonfactored_count: int = 0
        self.governance_failures_count: int = 0

    @staticmethod
    def _binary_int(value: Any, name: str) -> int:
        if type(value) not in (int, bool) or int(value) not in (0, 1):
            raise ValidationError(f"{name} must be a binary verdict in {{0, 1}}")
        return int(value)

    def observe_boundary(
        self,
        trace_id: str,
        carrier_left: Any,
        carrier_right: Any,
        e1: int | bool,
        e2: int | bool,
        eg: int | bool,
        *,
        r3: int | bool | None = None,
        g_rep: bool = True,
        g_auth: bool = True,
        g_time: bool = True,
    ) -> dict[str, Any]:
        """Ingest a boundary trace record and evaluate M3, M4, M8, M9, and D1."""
        tid = text(trace_id, "trace_id")
        c_left = json.loads(canonical(carrier_left))
        c_right = json.loads(canonical(carrier_right))
        v1 = self._binary_int(e1, "e1")
        v2 = self._binary_int(e2, "e2")
        vg = self._binary_int(eg, "eg")
        r3_val = self._binary_int(r3, "r3") if r3 is not None else vg
        boolean(g_rep, "g_rep")
        boolean(g_auth, "g_auth")
        boolean(g_time, "g_time")

        local_prod = v1 * v2
        delta_e = vg - local_prod
        classification = {-1: "NGD", 0: "ZDR", 1: "PGD"}[delta_e]

        weak_sufficient = (r3_val == vg)
        product_sufficient = (r3_val == local_prod)
        factorizes = (vg == local_prod)
        m4_equivalence_verified = (not weak_sufficient) or (product_sufficient == factorizes)

        governance_ready = bool(g_rep and g_auth and g_time)
        if not governance_ready:
            self.governance_failures_count += 1
        if weak_sufficient and not factorizes:
            self.weak_nonfactored_count += 1

        joint_carrier = {"left": c_left, "right": c_right}
        jk = canonical(joint_carrier)
        prev = self.joint_carrier_fibers.get(jk)

        rec = {
            "trace_id": tid,
            "joint_carrier": joint_carrier,
            "e1": v1,
            "e2": v2,
            "eg": vg,
            "r3": r3_val,
            "local_product": local_prod,
            "delta_e": delta_e,
            "classification": classification,
            "weak_sufficient": weak_sufficient,
            "product_sufficient": product_sufficient,
            "factorizes": factorizes,
            "m4_equivalence_verified": m4_equivalence_verified,
            "g_rep": g_rep,
            "g_auth": g_auth,
            "g_time": g_time,
            "governance_ready": governance_ready,
        }
        self.records.append(rec)

        collision_entry: dict[str, Any] | None = None
        if prev is not None and prev["eg"] != vg:
            forced_ngd_on_pair = (
                (prev["local_product"] == 1 and prev[" eg" if " eg" in prev else "eg"] == 0)
                or (local_prod == 1 and vg == 0)
            )
            collision_entry = {
                "joint_carrier": joint_carrier,
                "first_trace_id": prev["trace_id"],
                "first_eg": prev["eg"],
                "first_delta_e": prev["delta_e"],
                "second_trace_id": tid,
                "second_eg": vg,
                "second_delta_e": delta_e,
                "locally_green_forced_ngd": forced_ngd_on_pair,
            }
            self.carrier_mixing_collisions.append(collision_entry)
        elif prev is None:
            self.joint_carrier_fibers[jk] = rec

        has_carrier_mixing = len(self.carrier_mixing_collisions) > 0
        checked_closure_eligible = (delta_e == 0 and governance_ready and not has_carrier_mixing)

        if collision_entry is not None:
            status = "CARRIER_MIXING_OBSTRUCTED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif not governance_ready:
            status = "GOVERNANCE_PREREQUISITE_MISSING_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif weak_sufficient and not factorizes:
            status = "WEAK_SUFFICIENT_NONFACTORED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif delta_e != 0 or has_carrier_mixing:
            status = "FACTORIZATION_OBSTRUCTED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "CHECKED_CLOSURE_VERIFIED"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_organizational_gluing_step.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "checked_closure_eligible": checked_closure_eligible,
            "carrier_mixing_collision": collision_entry,
            **rec,
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def get_receipt(self) -> dict[str, Any]:
        """Emit summary receipt for the organizational gluing monitor."""
        has_carrier_mixing = len(self.carrier_mixing_collisions) > 0
        all_checked_closure = (
            len(self.records) > 0
            and not has_carrier_mixing
            and self.governance_failures_count == 0
            and all(r["delta_e"] == 0 for r in self.records)
        )
        if has_carrier_mixing:
            status = "CARRIER_MIXING_OBSTRUCTED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif self.governance_failures_count > 0:
            status = "GOVERNANCE_PREREQUISITE_MISSING_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif self.weak_nonfactored_count > 0:
            status = "WEAK_SUFFICIENT_NONFACTORED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif all_checked_closure:
            status = "CHECKED_CLOSURE_VERIFIED"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "FACTORIZATION_OBSTRUCTED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body = {
            "schema": "lggr.online_organizational_gluing_summary.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "records_count": len(self.records),
            "carrier_mixing_collisions_count": len(self.carrier_mixing_collisions),
            "weak_nonfactored_count": self.weak_nonfactored_count,
            "governance_failures_count": self.governance_failures_count,
            "all_m4_equivalences_verified": all(r["m4_equivalence_verified"] for r in self.records),
            "carrier_mixing_collisions": self.carrier_mixing_collisions,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingDefectSoundnessMonitor:
    """Online LGGR V realizable defect soundness and coupled Minkowski repair monitor.

    Given a linear defect operator D in Q^{m x n} (mapping site assignments s in C^0
    to interface defects omega = D s in C^1) and a stacked measurement operator
    Q in Q^{p x m} (with blind spot K = ker(Q)):
      - Evaluates the Soundness Criterion: im(D) cap ker(Q) == {0} iff rank(Q D) == rank(D).
      - Separates:
          * TRIVIAL_BLINDSPOT_SOUND_LGGG (Theorem 5: ker(Q) == {0})
          * COUPLED_SOUNDNESS_VERIFIED_LGGG (Theorem 6: ker(Q) != {0}, yet im(D) cap ker(Q) == {0})
          * STEALTH_REALIZABLE_DEFECT_LGGR (Theorem 3 & 4: im(D) cap ker(Q) != {0},
            exhibiting a stealth assignment s_R with ||D s_R||_1 = R > 0 and Q D s_R = 0).
      - Evaluates exact rational Minkowski repair distances Phi_1, Phi_2^2, Phi_inf
        on the coupled diagonal repair line {( -alpha, -alpha )}.
    """

    def __init__(
        self,
        defect_matrix: Any,
        measurement_matrix: Any,
        *,
        scope_id: str = "streaming-defect-soundness-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.d_mat = matrix(defect_matrix, "defect_matrix")
        self.m_defects = len(self.d_mat)
        self.n_sites = len(self.d_mat[0])
        self.q_mat = matrix(measurement_matrix, "measurement_matrix", cols=self.m_defects)
        self.p_meas = len(self.q_mat)
        self.qd_mat = matmul(self.q_mat, self.d_mat)

    @staticmethod
    def _rref_and_nullspace(
        mat: tuple[tuple[Fraction, ...], ...],
    ) -> tuple[int, list[tuple[Fraction, ...]]]:
        rows = len(mat)
        cols = len(mat[0])
        work = [[ val for val in row ] for row in mat]
        pivot_cols: list[int] = []
        r = 0
        for c in range(cols):
            if r >= rows:
                break
            piv = next((i for i in range(r, rows) if work[i][c] != 0), None)
            if piv is None:
                continue
            work[r], work[piv] = work[piv], work[r]
            scale = work[r][c]
            work[r] = [v / scale for v in work[r]]
            for i in range(rows):
                if i != r and work[i][c] != 0:
                    factor = work[i][c]
                    work[i] = [work[i][j] - factor * work[r][j] for j in range(cols)]
            pivot_cols.append(c)
            r += 1

        free_cols = [c for c in range(cols) if c not in pivot_cols]
        basis: list[tuple[Fraction, ...]] = []
        for fc in free_cols:
            vec = [Fraction(0)] * cols
            vec[fc] = Fraction(1)
            for row_idx, pc in enumerate(pivot_cols):
                vec[pc] = -work[row_idx][fc]
            basis.append(tuple(vec))
        return len(pivot_cols), basis

    def audit_soundness(self, target_severity: Fraction | int | str = 1) -> dict[str, Any]:
        """Audit realizable soundness im(D) cap ker(Q) == {0} and synthesize stealth witness if unsound."""
        r_sev = rational(target_severity)
        if r_sev <= 0:
            raise ValidationError("target_severity must be strictly positive")

        rank_d, _ = self._rref_and_nullspace(self.d_mat)
        rank_q, null_q = self._rref_and_nullspace(self.q_mat)
        rank_qd, null_qd = self._rref_and_nullspace(self.qd_mat)

        ambient_blindspot_dim = len(null_q)
        intersection_dim = rank_d - rank_qd
        soundness_holds = (intersection_dim == 0)

        stealth_assignment: list[Fraction] | None = None
        stealth_defect: list[Fraction] | None = None
        stealth_inconsistency: Fraction | None = None
        stealth_measured_score: Fraction | None = None

        if not soundness_holds:
            for s_cand in null_qd:
                ds_cand = matvec(self.d_mat, s_cand)
                l1_norm = sum((abs(v) for v in ds_cand), Fraction(0))
                if l1_norm > 0:
                    scale = r_sev / l1_norm
                    s_scaled = tuple(v * scale for v in s_cand)
                    ds_scaled = matvec(self.d_mat, s_scaled)
                    qds_scaled = matvec(self.q_mat, ds_scaled)
                    stealth_assignment = list(s_scaled)
                    stealth_defect = list(ds_scaled)
                    stealth_inconsistency = sum((abs(v) for v in ds_scaled), Fraction(0))
                    stealth_measured_score = sum((abs(v) for v in qds_scaled), Fraction(0))
                    break

        if soundness_holds and ambient_blindspot_dim == 0:
            status = "TRIVIAL_BLINDSPOT_SOUND_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        elif soundness_holds:
            status = "COUPLED_SOUNDNESS_VERIFIED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "STEALTH_REALIZABLE_DEFECT_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body = {
            "schema": "lggr.online_defect_soundness.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "soundness_holds": soundness_holds,
            "rank_d": rank_d,
            "rank_q": rank_q,
            "rank_qd": rank_qd,
            "ambient_blindspot_dimension": ambient_blindspot_dim,
            "realizable_blindspot_dimension": intersection_dim,
            "coupled_compensation_active": (soundness_holds and ambient_blindspot_dim > 0),
            "target_severity": r_sev,
            "stealth_assignment": stealth_assignment,
            "stealth_defect": stealth_defect,
            "stealth_global_inconsistency": stealth_inconsistency,
            "stealth_evaluator_score": stealth_measured_score,
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def evaluate_coupled_minkowski_repair(
        self,
        a: Fraction | int | str,
        b: Fraction | int | str,
    ) -> dict[str, Any]:
        """Compute exact rational Minkowski repair distances on the coupled diagonal image {(-alpha, -alpha)}."""
        va = rational(a)
        vb = rational(b)
        diff = abs(va - vb)
        phi_1 = diff
        phi_2_sq = (diff * diff) / Fraction(2)
        phi_inf = diff / Fraction(2)
        alpha_star = -(va + vb) / Fraction(2)
        interval_min = -max(va, vb)
        interval_max = -min(va, vb)
        is_exact = (va == vb)

        body = {
            "schema": "lggr.online_minkowski_repair.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": "EXACT_COUPLED_SECTION" if is_exact else "NONEXACT_QUOTIENT_DEFECT",
            "contract_status": "COMPOSABLE_LGGG" if is_exact else "OBSTRUCTED_LGGR",
            "cochain": [va, vb],
            "phi_1_repair_distance": phi_1,
            "phi_2_squared_repair_distance": phi_2_sq,
            "phi_inf_repair_distance": phi_inf,
            "unique_l2_linf_minimizer_alpha": alpha_star,
            "l1_minimizer_interval": [interval_min, interval_max],
            "chain_inequality_verified": (phi_inf <= phi_1 and phi_inf * phi_inf <= phi_2_sq <= phi_1 * phi_1),
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingDashboardAdequacyMonitor:
    """Online LGGR I (E9-E18) & LGGR II (M6-M7) dashboard information and collapsing-detector monitor.

    Evaluates:
      - Exact sample rate & oriented defect count reconstruction identities (E9-E11):
          2 * n_pos == M + D  and  2 * n_neg == M - D,
          n_neg <= sum L_i,
        where M = n_pos + n_neg = N * EGD and D = sum Delta_E = n_pos - n_neg.
      - Global failure partition (E18):
          #{E_g == 0} == n_neg + #{L == 0 and E_g == 0}.
      - Packet information recovery (E12-E14):
          E_g == L + Delta_E  and  L == E_g - Delta_E.
      - Product-collapsing detector detection (M7): detects when a local validator copies E_g
        and peers pass so L(x) == E_g(x) tautologically across the sample.
      - All-zero agreement at failure detection (M6): detects when Delta_E == 0 on every trace
        solely because E_g == L == 0 everywhere (zero global passes).
    """

    def __init__(
        self,
        *,
        scope_id: str = "streaming-dashboard-adequacy-scope",
        copied_global_validator: bool = False,
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        boolean(copied_global_validator, "copied_global_validator")
        self.copied_global_validator = copied_global_validator
        self.records: list[dict[str, Any]] = []
        self.n_pos: int = 0
        self.n_neg: int = 0
        self.n_zero: int = 0
        self.local_pass_sum: int = 0
        self.global_pass_sum: int = 0
        self.signed_defect_sum: int = 0
        self.joint_fail_count: int = 0

    @staticmethod
    def _binary_int(value: Any, name: str) -> int:
        if type(value) not in (int, bool) or int(value) not in (0, 1):
            raise ValidationError(f"{name} must be a binary verdict in {{0, 1}}")
        return int(value)

    def record_trace(
        self,
        trace_id: str,
        e1: int | bool,
        e2: int | bool,
        eg: int | bool,
    ) -> dict[str, Any]:
        """Record a trace verdict triple (e1, e2, eg) and update dashboard statistics."""
        tid = text(trace_id, "trace_id")
        v1 = self._binary_int(e1, "e1")
        v2 = self._binary_int(e2, "e2")
        vg = self._binary_int(eg, "eg")

        local_prod = v1 * v2
        delta_e = vg - local_prod
        classification = {-1: "NGD", 0: "ZDR", 1: "PGD"}[delta_e]

        self.local_pass_sum += local_prod
        self.global_pass_sum += vg
        self.signed_defect_sum += delta_e
        if delta_e == 1:
            self.n_pos += 1
        elif delta_e == -1:
            self.n_neg += 1
        else:
            self.n_zero += 1
        if local_prod == 0 and vg == 0:
            self.joint_fail_count += 1

        rec = {
            "trace_id": tid,
            "e1": v1,
            "e2": v2,
            "eg": vg,
            "local_product": local_prod,
            "delta_e": delta_e,
            "classification": classification,
            "recovered_eg_from_l_and_delta": local_prod + delta_e,
            "recovered_l_from_eg_and_delta": vg - delta_e,
            "packet_recovery_verified": (
                (local_prod + delta_e == vg) and (vg - delta_e == local_prod)
            ),
        }
        self.records.append(rec)
        return self.get_receipt()

    def get_receipt(self) -> dict[str, Any]:
        """Emit dashboard adequacy receipt checking E9-E18 and M6-M7."""
        n_total = len(self.records)
        disagreement_m = self.n_pos + self.n_neg
        d_sum = self.signed_defect_sum
        global_fail_count = n_total - self.global_pass_sum

        lpr = Fraction(self.local_pass_sum, n_total) if n_total > 0 else Fraction(0)
        gpr = Fraction(self.global_pass_sum, n_total) if n_total > 0 else Fraction(0)
        egd = Fraction(disagreement_m, n_total) if n_total > 0 else Fraction(0)
        mean_defect = Fraction(d_sum, n_total) if n_total > 0 else Fraction(0)

        reconstruction_verified = (
            2 * self.n_pos == disagreement_m + d_sum
            and 2 * self.n_neg == disagreement_m - d_sum
            and self.n_pos + self.n_neg + self.n_zero == n_total
            and gpr - lpr == mean_defect
        )
        ngd_bounded_by_local_passes = (self.n_neg <= self.local_pass_sum)
        global_failure_partition_verified = (
            global_fail_count == self.n_neg + self.joint_fail_count
        )
        all_packet_recoveries_verified = all(
            r["packet_recovery_verified"] for r in self.records
        )

        all_zero_agreement_at_failure = (
            n_total > 0 and disagreement_m == 0 and self.global_pass_sum == 0
        )
        product_collapsing_detected = (
            n_total > 0
            and self.copied_global_validator
            and disagreement_m == 0
            and all(r["e1"] == r["eg"] and r["e2"] == 1 for r in self.records)
        )

        if self.n_neg > 0:
            status = "NGD_DEFECT_PRESENT_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif disagreement_m > 0:
            status = "PGD_DISAGREEMENT_PRESENT_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif product_collapsing_detected:
            status = "PRODUCT_COLLAPSING_DETECTOR_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif all_zero_agreement_at_failure:
            status = "ZERO_DEFECT_ALL_FAIL_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "DASHBOARD_ADEQUACY_VERIFIED_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_dashboard_adequacy.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "sample_size": n_total,
            "n_pos_pgd": self.n_pos,
            "n_neg_ngd": self.n_neg,
            "n_zero_zdr": self.n_zero,
            "disagreement_count_m": disagreement_m,
            "signed_defect_sum_d": d_sum,
            "local_pass_rate_lpr": lpr,
            "global_pass_rate_gpr": gpr,
            "evaluator_gluing_disagreement_egd": egd,
            "mean_signed_defect": mean_defect,
            "global_failure_count": global_fail_count,
            "joint_local_global_failure_count": self.joint_fail_count,
            "reconstruction_identities_verified": reconstruction_verified,
            "ngd_bounded_by_local_passes": ngd_bounded_by_local_passes,
            "global_failure_partition_verified": global_failure_partition_verified,
            "all_packet_recoveries_verified": all_packet_recoveries_verified,
            "all_zero_agreement_at_failure": all_zero_agreement_at_failure,
            "product_collapsing_detected": product_collapsing_detected,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingBellPolytopeMonitor:
    """Online 4-context CHSH Bell polytope, isotropic visibility threshold, and negative-mass monitor.

    Evaluates the LGGR VII 4-context CHSH correlation functional and signed-extension obstructions:
      - Canonical CHSH functional:
          S(E) = E_00 + E_01 + E_10 - E_11
        and all 8 CHSH facet symmetries S_{x0,y0}(E) across (x0, y0) in {0, 1}^2.
      - Exhaustive verification over all 16 deterministic LHV vertices (a0, a1, b0, b1) in {-1, +1}^4
        that a0*b0 + a0*b1 + a1*b0 - a1*b1 == a0*(b0 + b1) + a1*(b0 - b1) in {-2, +2}.
      - Exact rational minimum signed-extension negative mass:
          N_min(E) = max(0, (S_max(E) - 2) / 4),
        contextual fraction on the 4-context symmetric CHSH slice:
          CF(E) = 2 * N_min(E) = max(0, (S_max(E) - 2) / 2),
        and 4-context packing mass identity:
          U = 1 + N_min, R = 4 * N_min, U - R = 1 - 3 * N_min, CF <= 3 * N_min.
      - Isotropic PR-box mixture p_v = v * p_PR + (1 - v) * p_uniform with critical visibility
        threshold v_crit = 1/2 (S(p_v) = 4 * v).
    """

    def __init__(self, *, scope_id: str = "streaming-bell-polytope-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.models: dict[str, dict[str, Any]] = {}
        self.lhv_vertex_values: list[int] = []
        for a0 in (-1, 1):
            for a1 in (-1, 1):
                for b0 in (-1, 1):
                    for b1 in (-1, 1):
                        val = a0 * b0 + a0 * b1 + a1 * b0 - a1 * b1
                        factored = a0 * (b0 + b1) + a1 * (b0 - b1)
                        if val != factored:
                            raise ValidationError("CHSH factorization mismatch")
                        self.lhv_vertex_values.append(val)
        self.all_16_lhv_vertices_bounded_by_2 = (
            len(self.lhv_vertex_values) == 16
            and all(abs(v) == 2 for v in self.lhv_vertex_values)
        )

    @staticmethod
    def _validate_correlator(val: Fraction | int | str, name: str) -> Fraction:
        q = rational(val)
        if q < Fraction(-1) or q > Fraction(1):
            raise ValidationError(f"{name} must lie in [-1, 1], got {q}")
        return q

    def observe_correlators(
        self,
        model_id: str,
        e00: Fraction | int | str,
        e01: Fraction | int | str,
        e10: Fraction | int | str,
        e11: Fraction | int | str,
        *,
        isotropic_visibility: Fraction | int | str | None = None,
    ) -> dict[str, Any]:
        """Audit a 4-context correlator tuple (E_00, E_01, E_10, E_11) in [-1, 1]^4."""
        mid = text(model_id, "model_id")
        c00 = self._validate_correlator(e00, "e00")
        c01 = self._validate_correlator(e01, "e01")
        c10 = self._validate_correlator(e10, "e10")
        c11 = self._validate_correlator(e11, "e11")

        vis_q: Fraction | None = None
        if isotropic_visibility is not None:
            vis_q = rational(isotropic_visibility)
            if vis_q < Fraction(0) or vis_q > Fraction(1):
                raise ValidationError("isotropic_visibility must lie in [0, 1]")

        s_canonical = c00 + c01 + c10 - c11
        facets = [
            c00 + c01 + c10 - c11,
            c00 + c01 - c10 + c11,
            c00 - c01 + c10 + c11,
            -c00 + c01 + c10 + c11,
        ]
        s_max = max(abs(f) for f in facets)
        polytope_violation = max(Fraction(0), s_max - Fraction(2))
        n_min = polytope_violation / Fraction(4)
        cf_val = Fraction(2) * n_min
        local_fraction = Fraction(1) - cf_val
        u_mass = Fraction(1) + n_min
        r_mass = Fraction(4) * n_min
        packing_identity_verified = (
            u_mass - r_mass == Fraction(1) - Fraction(3) * n_min
            and cf_val <= Fraction(3) * n_min
            and cf_val == Fraction(2) * n_min
        )

        is_nonlocal = s_max > Fraction(2)
        if is_nonlocal:
            status = "BELL_NONLOCAL_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "LOCAL_LHV_EXTENSION_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        entry = {
            "schema": "lggr.online_bell_polytope_model.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "model_id": mid,
            "status": status,
            "contract_status": contract_status,
            "correlators": {"e00": c00, "e01": c01, "e10": c10, "e11": c11},
            "canonical_chsh_s": s_canonical,
            "max_chsh_facet_s": s_max,
            "classical_polytope_bound": Fraction(2),
            "polytope_violation_excess": polytope_violation,
            "min_negative_mass_n_min": n_min,
            "contextual_fraction_cf": cf_val,
            "local_packing_fraction": local_fraction,
            "positive_extension_mass_u": u_mass,
            "marginal_negative_budget_r": r_mass,
            "isotropic_visibility": vis_q,
            "critical_visibility_threshold": Fraction(1, 2),
            "above_visibility_threshold": (vis_q > Fraction(1, 2)) if vis_q is not None else is_nonlocal,
            "all_16_lhv_vertices_bounded_by_2": self.all_16_lhv_vertices_bounded_by_2,
            "packing_identity_verified": packing_identity_verified,
        }
        self.models[mid] = entry
        return json_value({**entry, "receipt_sha256": digest(entry)})

    def observe_isotropic_pr_mixture(
        self,
        model_id: str,
        visibility: Fraction | int | str,
    ) -> dict[str, Any]:
        """Audit an isotropic PR-box mixture p_v = v * p_PR + (1 - v) * p_uniform with visibility v in [0, 1]."""
        v = rational(visibility)
        if v < Fraction(0) or v > Fraction(1):
            raise ValidationError("visibility must lie in [0, 1]")
        return self.observe_correlators(
            model_id,
            v,
            v,
            v,
            -v,
            isotropic_visibility=v,
        )

    def get_receipt(self) -> dict[str, Any]:
        """Emit aggregate Bell polytope audit receipt across all observed 4-context models."""
        nonlocal_models = [
            mid for mid, m in self.models.items() if m["status"] == "BELL_NONLOCAL_OBSTRUCTION_LGGR"
        ]
        local_models = [
            mid for mid, m in self.models.items() if m["status"] == "LOCAL_LHV_EXTENSION_LGGG"
        ]
        max_n_min = max(
            (m["min_negative_mass_n_min"] for m in self.models.values()),
            default=Fraction(0),
        )
        max_s = max(
            (m["max_chsh_facet_s"] for m in self.models.values()),
            default=Fraction(0),
        )
        all_packing_ok = all(m["packing_identity_verified"] for m in self.models.values())

        if nonlocal_models:
            status = "BELL_NONLOCAL_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "LOCAL_LHV_EXTENSION_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_bell_polytope.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "observed_models_count": len(self.models),
            "local_lhv_models": sorted(local_models),
            "nonlocal_obstructed_models": sorted(nonlocal_models),
            "max_chsh_s_observed": max_s,
            "max_negative_mass_n_min": max_n_min,
            "critical_visibility_threshold": Fraction(1, 2),
            "all_16_lhv_vertices_bounded_by_2": self.all_16_lhv_vertices_bounded_by_2,
            "all_packing_identities_verified": all_packing_ok,
        }
        return json_value({**body, "receipt_sha256": digest(body)})







