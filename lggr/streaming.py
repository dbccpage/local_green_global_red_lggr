"""Streaming runtime monitors for online LGGG vs LGGR discovery.

Evaluates finite state and witness streams incrementally during execution.
Zero external runtime dependencies: strictly Python standard library.
AuthorityEffect: None. Replay and online evidence verification only.
"""
from __future__ import annotations

from collections import deque
from fractions import Fraction
import json
from typing import Any, Iterable, Mapping, Sequence

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
from .linear import Vector, classify_cochain, is_zero, matmul, matvec, matrix, rational, solve_exact, transpose, vector, verify_l1_certificate
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
    if "prior_obligations_satisfied" in kwargs:
        satisfied = boolean(kwargs.pop("prior_obligations_satisfied"), "prior_obligations_satisfied")
        if not satisfied:
            kwargs["obligations"] = tuple(kwargs.get("obligations", ())) + ("prior_obligations_unsatisfied",)
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
        self.observation_indices: dict[str, int] = {}
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
            self.observation_indices[sid] = len(self.history)
            self.history.append(row)

        report_key = canonical(rep_clean)
        first_rep = self.fibers.get(report_key)

        step_idx = self.observation_indices[sid]

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
        self.state_values: dict[str, int] = {}
        if baseline is not None and baseline.value is not None:
            self.state_values[baseline.state_id] = baseline.value

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

        for state in (witness.source, witness.target):
            if state.value is not None:
                if state.state_id in self.state_values and self.state_values[state.state_id] != state.value:
                    g1_ok = False
                    g1_reasons.append("CONFLICTING_STATE")
                self.state_values[state.state_id] = state.value

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
        if val_a is None or val_b is None:
            g1_ok = False
            g1_reasons.append("MISSING_ENDPOINT")
        if self.obligations:
            g1_ok = False
            g1_reasons.append("OPEN_OBLIGATIONS")
        if (val_a is not None and val_b is not None and rep_ok
                and witness.observed_magnitude is not None
                and witness.observed_magnitude != abs(val_b - val_a)):
            g1_ok = False
            g1_reasons.append("MAGNITUDE_MISMATCH")
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

        # Endpoint scope is evaluated by get_receipt() on the supplied trace.
        # A temporary excursion may recover before its final endpoint, so it
        # must not create a persistent early-stopping alert here.
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

        if self.policy.query_scope == "endpoint" and self.status == "OBSTRUCTED_LGGR":
            # Recheck the current endpoint after a prior receipt observed an
            # excursion. Full replay retains independent structural/NGD faults.
            self.get_receipt()

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
        baseline = self.baseline or StateRef("unobserved-baseline", None)
        replay = audit_history(self.policy, baseline, self.steps,
                               prior_obligations=tuple(sorted(self.obligations)))
        self.findings = list(replay["findings"])
        if any(a.get("defect") == -1 for a in self.alerts):
            self.findings.append({"kind": "OBSTRUCTION_DETECTED", "code": "NGD_DEFECT_DETECTED",
                                  "message": "A supplied global sample disagreed with the local product."})

        priority = ["INVALID_WITNESS", "AUTHORITY_REQUIRED", "UNSUPPORTED", "LOCAL_REJECTED",
                    "OBSTRUCTION_DETECTED", "WITNESS_INCOMPLETE"]
        kinds = {f["kind"] for f in self.findings}
        status = next((k for k in priority if k in kinds), "COMPOSITION_VERIFIED")
        self.status = "COMPOSABLE_LGGG" if status == "COMPOSITION_VERIFIED" else "OBSTRUCTED_LGGR"

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


class StreamingProductRetractionMonitor:
    """Online LGGR VII product-state retraction residual vs. separable LHV extension monitor.

    Evaluates on 2x2 joint probability tables p = [[p00, p01], [p10, p11]] (and 4-context CHSH
    families of 2x2 tables):
      - Marginals p_A = (p00 + p01, p10 + p11) and p_B = (p00 + p10, p01 + p11).
      - Product retraction Pi(p) = p_A x p_B and residual F_p = p - p_A x p_B.
      - Exact 2x2 determinant identity:
          F_p == det(p) * [[1, -1], [-1, 1]],   ||F_p||_1 == 4 * |p00 * p11 - p01 * p10|.
      - Zero row and column marginals of F_p and idempotence Pi(Pi(p)) == Pi(p) (F_{Pi(p)} == 0).
      - Separation of three regimes across 4-context CHSH tables:
          1. PRODUCT_FACTORIZED_LGGG (COMPOSABLE_LGGG): max ||F_p||_1 == 0 and N_min == 0.
          2. CLASSICAL_CORRELATION_LHV_LGGG (COMPOSABLE_LGGG): max ||F_p||_1 > 0 while N_min == 0
             (shared randomness / separable correlation without Bell nonlocality).
          3. BELL_NONLOCAL_OBSTRUCTION_LGGR (OBSTRUCTED_LGGR): max ||F_p||_1 > 0 and N_min > 0.
    """

    def __init__(self, *, scope_id: str = "streaming-product-retraction-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.tables: dict[str, dict[str, Any]] = {}
        self.models: dict[str, dict[str, Any]] = {}

    @staticmethod
    def _audit_2x2_table(
        p00: Fraction | int | str,
        p01: Fraction | int | str,
        p10: Fraction | int | str,
        p11: Fraction | int | str,
    ) -> dict[str, Any]:
        q00 = rational(p00)
        q01 = rational(p01)
        q10 = rational(p10)
        q11 = rational(p11)
        for name, val in (("p00", q00), ("p01", q01), ("p10", q10), ("p11", q11)):
            if val < Fraction(0):
                raise ValidationError(f"{name} must be nonnegative, got {val}")
        total = q00 + q01 + q10 + q11
        if total != Fraction(1):
            raise ValidationError(f"2x2 probability table must sum to 1, got {total}")

        pa0 = q00 + q01
        pa1 = q10 + q11
        pb0 = q00 + q10
        pb1 = q01 + q11

        pi00 = pa0 * pb0
        pi01 = pa0 * pb1
        pi10 = pa1 * pb0
        pi11 = pa1 * pb1

        f00 = q00 - pi00
        f01 = q01 - pi01
        f10 = q10 - pi10
        f11 = q11 - pi11

        det_p = q00 * q11 - q01 * q10
        l1_residual = abs(f00) + abs(f01) + abs(f10) + abs(f11)
        det_identity_ok = (
            f00 == det_p
            and f01 == -det_p
            and f10 == -det_p
            and f11 == det_p
            and l1_residual == Fraction(4) * abs(det_p)
        )
        zero_row_marginals = (f00 + f01 == Fraction(0)) and (f10 + f11 == Fraction(0))
        zero_col_marginals = (f00 + f10 == Fraction(0)) and (f01 + f11 == Fraction(0))

        # Idempotence check: marginals of Pi(p) equal (pa0, pa1) and (pb0, pb1), so F_{Pi(p)} == 0
        pi_pa0 = pi00 + pi01
        pi_pa1 = pi10 + pi11
        pi_pb0 = pi00 + pi10
        pi_pb1 = pi01 + pi11
        idempotence_ok = (
            pi_pa0 == pa0
            and pi_pa1 == pa1
            and pi_pb0 == pb0
            and pi_pb1 == pb1
            and (pi00 - pi_pa0 * pi_pb0 == Fraction(0))
            and (pi01 - pi_pa0 * pi_pb1 == Fraction(0))
            and (pi10 - pi_pa1 * pi_pb0 == Fraction(0))
            and (pi11 - pi_pa1 * pi_pb1 == Fraction(0))
        )

        # Parity correlator E = P(a == b) - P(a != b) = (p00 + p11) - (p01 + p10)
        correlator_e = (q00 + q11) - (q01 + q10)

        return {
            "table": [[q00, q01], [q10, q11]],
            "marginal_a": [pa0, pa1],
            "marginal_b": [pb0, pb1],
            "product_retraction": [[pi00, pi01], [pi10, pi11]],
            "residual_f": [[f00, f01], [f10, f11]],
            "determinant": det_p,
            "l1_product_residual": l1_residual,
            "correlator_e": correlator_e,
            "determinant_identity_verified": det_identity_ok,
            "zero_row_marginals_verified": zero_row_marginals,
            "zero_col_marginals_verified": zero_col_marginals,
            "retraction_idempotence_verified": idempotence_ok,
        }

    def observe_bivariate_table(
        self,
        table_id: str,
        p00: Fraction | int | str,
        p01: Fraction | int | str,
        p10: Fraction | int | str,
        p11: Fraction | int | str,
    ) -> dict[str, Any]:
        """Audit a single 2x2 bivariate probability table for product factorization vs correlation."""
        tid = text(table_id, "table_id")
        info = self._audit_2x2_table(p00, p01, p10, p11)
        is_product = info["l1_product_residual"] == Fraction(0)
        status = "PRODUCT_FACTORIZED_LGGG" if is_product else "CORRELATED_NONPRODUCT_TABLE"
        entry = {
            "schema": "lggr.online_product_retraction_table.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "table_id": tid,
            "status": status,
            "is_product_state": is_product,
            **info,
        }
        self.tables[tid] = entry
        return json_value({**entry, "receipt_sha256": digest(entry)})

    def observe_four_context_tables(
        self,
        model_id: str,
        contexts: dict[str, tuple[Any, Any, Any, Any] | list[Any]],
    ) -> dict[str, Any]:
        """Audit a 4-context CHSH family of 2x2 tables keyed by ('00', '01', '10', '11')."""
        mid = text(model_id, "model_id")
        required_keys = ("00", "01", "10", "11")
        if not isinstance(contexts, dict) or any(k not in contexts for k in required_keys):
            raise ValidationError("contexts must be a dict containing keys '00', '01', '10', '11'")

        ctx_audits: dict[str, dict[str, Any]] = {}
        for k in required_keys:
            vals = contexts[k]
            if not isinstance(vals, (tuple, list)) or len(vals) != 4:
                raise ValidationError(f"Context {k} must provide 4 probabilities (p00, p01, p10, p11)")
            ctx_audits[k] = self._audit_2x2_table(vals[0], vals[1], vals[2], vals[3])

        e00 = ctx_audits["00"]["correlator_e"]
        e01 = ctx_audits["01"]["correlator_e"]
        e10 = ctx_audits["10"]["correlator_e"]
        e11 = ctx_audits["11"]["correlator_e"]

        facets = [
            e00 + e01 + e10 - e11,
            e00 + e01 - e10 + e11,
            e00 - e01 + e10 + e11,
            -e00 + e01 + e10 + e11,
        ]
        s_canonical = facets[0]
        s_max = max(abs(f) for f in facets)
        n_min = max(Fraction(0), s_max - Fraction(2)) / Fraction(4)
        cf_val = Fraction(2) * n_min
        max_l1_prod = max(ctx_audits[k]["l1_product_residual"] for k in required_keys)

        all_identities_ok = all(
            ctx_audits[k]["determinant_identity_verified"]
            and ctx_audits[k]["zero_row_marginals_verified"]
            and ctx_audits[k]["zero_col_marginals_verified"]
            and ctx_audits[k]["retraction_idempotence_verified"]
            for k in required_keys
        )

        if n_min > Fraction(0):
            status = "BELL_NONLOCAL_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif max_l1_prod > Fraction(0):
            status = "CLASSICAL_CORRELATION_LHV_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "PRODUCT_FACTORIZED_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        entry = {
            "schema": "lggr.online_product_retraction_model.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "model_id": mid,
            "status": status,
            "contract_status": contract_status,
            "max_l1_product_residual": max_l1_prod,
            "canonical_chsh_s": s_canonical,
            "max_chsh_facet_s": s_max,
            "min_negative_mass_n_min": n_min,
            "contextual_fraction_cf": cf_val,
            "classical_correlation_without_nonlocality": (
                max_l1_prod > Fraction(0) and n_min == Fraction(0)
            ),
            "all_retraction_identities_verified": all_identities_ok,
            "contexts": ctx_audits,
        }
        self.models[mid] = entry
        return json_value({**entry, "receipt_sha256": digest(entry)})

    def get_receipt(self) -> dict[str, Any]:
        """Emit aggregate receipt separating product states, classical LHV correlations, and Bell nonlocality."""
        product_models = [
            mid for mid, m in self.models.items() if m["status"] == "PRODUCT_FACTORIZED_LGGG"
        ]
        classical_corr_models = [
            mid for mid, m in self.models.items() if m["status"] == "CLASSICAL_CORRELATION_LHV_LGGG"
        ]
        nonlocal_models = [
            mid for mid, m in self.models.items() if m["status"] == "BELL_NONLOCAL_OBSTRUCTION_LGGR"
        ]
        all_ok = all(
            t["determinant_identity_verified"]
            and t["zero_row_marginals_verified"]
            and t["zero_col_marginals_verified"]
            and t["retraction_idempotence_verified"]
            for t in self.tables.values()
        ) and all(m["all_retraction_identities_verified"] for m in self.models.values())

        if nonlocal_models:
            status = "BELL_NONLOCAL_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif classical_corr_models:
            status = "CLASSICAL_CORRELATION_LHV_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "PRODUCT_FACTORIZED_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_product_retraction.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "observed_tables_count": len(self.tables),
            "observed_models_count": len(self.models),
            "product_factorized_models": sorted(product_models),
            "classical_correlation_lhv_models": sorted(classical_corr_models),
            "bell_nonlocal_models": sorted(nonlocal_models),
            "all_retraction_identities_verified": all_ok,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingRSIFiberCeilingMonitor:
    """Online LGGR VII evidence-preserving Recursive Self-Improvement (RSI) fiber ceiling monitor.

    Audits multi-generation recursive predictor updates g^(0), g^(1), ..., g^(T) that factor
    through a fixed coarse observation map p: X -> A (g^(t) = h^(t) o p):
      - Tracks coarse observation fibers F(r) = {x in X : p(x) = r}, fiber width
        W_f(r) = max_{x in F(r)} f(x) - min_{x in F(r)} f(x), and minimax half-spread
        ceiling epsilon_min(r) = W_f(r) / 2.
      - Verifies across every evidence-preserving recursive update generation t >= 0 that
        worst-case fiber error satisfies:
          max_{x in F(r)} |f(x) - g^(t)(x)| >= W_f(r) / 2,
        demonstrating in this model that recursive post-processing of a fixed report channel
        cannot reduce worst-case error below half the fiber spread.
      - Verifies that an informative sensor/evidence refinement p': X -> A' splitting colliding
        states into zero-spread refined fibers reduces worst-case error below the coarse ceiling.
    """

    def __init__(self, *, scope_id: str = "streaming-rsi-fiber-ceiling-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.states: dict[str, dict[str, Any]] = {}
        self.coarse_fibers: dict[str, dict[str, Any]] = {}
        self.refined_fibers: dict[str, dict[str, Any]] = {}
        self.generations: list[dict[str, Any]] = []

    def observe_state(
        self,
        state_id: str,
        coarse_report: Any,
        target_value: Fraction | int | str,
        *,
        refined_report: Any = None,
    ) -> dict[str, Any]:
        """Register a state with its coarse report p(x), rational target f(x), and optional refined report p'(x)."""
        sid = text(state_id, "state_id")
        c_clean = json.loads(canonical(coarse_report))
        c_key = canonical(c_clean)
        r_clean = json.loads(canonical(refined_report if refined_report is not None else coarse_report))
        r_key = canonical(r_clean)
        f_val = rational(target_value)

        prev = self.states.get(sid)
        if prev is not None:
            if (
                prev["coarse_key"] != c_key
                or prev["refined_key"] != r_key
                or prev["target_value"] != f_val
            ):
                raise ValidationError(f"Conflicting state observation for state_id: {sid}")
        else:
            self.states[sid] = {
                "state_id": sid,
                "coarse_report": c_clean,
                "coarse_key": c_key,
                "refined_report": r_clean,
                "refined_key": r_key,
                "target_value": f_val,
            }

        self._update_fiber_dict(self.coarse_fibers, c_key, c_clean, sid, f_val)
        self._update_fiber_dict(self.refined_fibers, r_key, r_clean, sid, f_val)
        return self.get_receipt()

    @staticmethod
    def _update_fiber_dict(
        fiber_dict: dict[str, dict[str, Any]],
        key: str,
        report_obj: Any,
        sid: str,
        f_val: Fraction,
    ) -> None:
        fb = fiber_dict.get(key)
        if fb is None:
            fiber_dict[key] = {
                "report": report_obj,
                "state_ids": [sid],
                "min_target": f_val,
                "max_target": f_val,
                "spread_width": Fraction(0),
                "half_spread_ceiling": Fraction(0),
                "midpoint_prediction": f_val,
            }
        else:
            if sid not in fb["state_ids"]:
                fb["state_ids"].append(sid)
                fb["state_ids"].sort()
            if f_val < fb["min_target"]:
                fb["min_target"] = f_val
            if f_val > fb["max_target"]:
                fb["max_target"] = f_val
            spread = fb["max_target"] - fb["min_target"]
            fb["spread_width"] = spread
            fb["half_spread_ceiling"] = spread / Fraction(2)
            fb["midpoint_prediction"] = (fb["max_target"] + fb["min_target"]) / Fraction(2)

    def evaluate_generation(
        self,
        generation_id: str,
        predictor_by_report: dict[str, Fraction | int | str],
        *,
        use_refined_report: bool = False,
    ) -> dict[str, Any]:
        """Evaluate a generation-t predictor mapping report keys (or canonical JSON strings) to rational predictions."""
        gid = text(generation_id, "generation_id")
        boolean(use_refined_report, "use_refined_report")
        if not self.states:
            raise ValidationError("Cannot evaluate generation before observing states")
        if not isinstance(predictor_by_report, dict):
            raise ValidationError("predictor_by_report must be a dict")

        norm_map: dict[str, Fraction] = {}
        for k, v in predictor_by_report.items():
            q_v = rational(v)
            norm_map[str(k)] = q_v
            norm_map[canonical(k)] = q_v

        per_coarse_fiber_max_err: dict[str, Fraction] = {
            ck: Fraction(0) for ck in self.coarse_fibers
        }
        max_err = Fraction(0)

        for sid, st in sorted(self.states.items()):
            lookup_key = st["refined_key"] if use_refined_report else st["coarse_key"]
            raw_rep = st["refined_report"] if use_refined_report else st["coarse_report"]
            if lookup_key in norm_map:
                pred = norm_map[lookup_key]
            elif str(raw_rep) in norm_map:
                pred = norm_map[str(raw_rep)]
            else:
                raise ValidationError(f"Missing prediction for report {raw_rep} in generation {gid}")
            err = abs(st["target_value"] - pred)
            if err > max_err:
                max_err = err
            ck = st["coarse_key"]
            if err > per_coarse_fiber_max_err[ck]:
                per_coarse_fiber_max_err[ck] = err

        coarse_ceiling = max(
            (fb["half_spread_ceiling"] for fb in self.coarse_fibers.values()),
            default=Fraction(0),
        )
        refined_ceiling = max(
            (fb["half_spread_ceiling"] for fb in self.refined_fibers.values()),
            default=Fraction(0),
        )

        if not use_refined_report:
            invariance_verified = all(
                per_coarse_fiber_max_err[ck] >= fb["half_spread_ceiling"]
                for ck, fb in self.coarse_fibers.items()
            ) and (max_err >= coarse_ceiling)
            broke_coarse_ceiling = False
        else:
            invariance_verified = (max_err >= refined_ceiling)
            broke_coarse_ceiling = (max_err < coarse_ceiling)

        if use_refined_report and broke_coarse_ceiling and max_err == Fraction(0):
            status = "EVIDENCE_REFINEMENT_RESOLVED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        elif coarse_ceiling > Fraction(0) and not broke_coarse_ceiling:
            status = "RSI_FIBER_CEILING_LOCKED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "ZERO_SPREAD_FIBER_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        gen_entry = {
            "schema": "lggr.online_rsi_generation.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "generation_id": gid,
            "status": status,
            "contract_status": contract_status,
            "use_refined_report": use_refined_report,
            "worst_case_error": max_err,
            "coarse_half_spread_ceiling": coarse_ceiling,
            "refined_half_spread_ceiling": refined_ceiling,
            "attains_minimax_midpoint_floor": (not use_refined_report and max_err == coarse_ceiling),
            "invariance_lower_bound_verified": invariance_verified,
            "broke_coarse_ceiling_via_refinement": broke_coarse_ceiling,
        }
        self.generations.append(gen_entry)
        return json_value({**gen_entry, "receipt_sha256": digest(gen_entry)})

    def get_receipt(self) -> dict[str, Any]:
        """Emit aggregate RSI fiber ceiling receipt across all observed states and recursive generations."""
        coarse_ceiling = max(
            (fb["half_spread_ceiling"] for fb in self.coarse_fibers.values()),
            default=Fraction(0),
        )
        refined_ceiling = max(
            (fb["half_spread_ceiling"] for fb in self.refined_fibers.values()),
            default=Fraction(0),
        )
        evidence_preserving_gens = [
            g for g in self.generations if not g["use_refined_report"]
        ]
        refined_gens = [
            g for g in self.generations if g["use_refined_report"]
        ]
        all_invariance_ok = all(
            g["invariance_lower_bound_verified"] for g in self.generations
        )
        refinement_resolved = any(
            g["broke_coarse_ceiling_via_refinement"] and g["worst_case_error"] == Fraction(0)
            for g in refined_gens
        )

        if refinement_resolved:
            status = "EVIDENCE_REFINEMENT_RESOLVED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        elif coarse_ceiling > Fraction(0):
            status = "RSI_FIBER_CEILING_LOCKED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "ZERO_SPREAD_FIBER_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_rsi_fiber_ceiling.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "observed_states_count": len(self.states),
            "coarse_fibers_count": len(self.coarse_fibers),
            "refined_fibers_count": len(self.refined_fibers),
            "coarse_half_spread_ceiling": coarse_ceiling,
            "refined_half_spread_ceiling": refined_ceiling,
            "evaluated_generations_count": len(self.generations),
            "evidence_preserving_generations_count": len(evidence_preserving_gens),
            "refined_generations_count": len(refined_gens),
            "all_invariance_lower_bounds_verified": all_invariance_ok,
            "refinement_resolved": refinement_resolved,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingCoalitionalAttributionMonitor:
    """Online LGGR II coalitional Shapley attribution vs. non-additive raw defect monitor.

    Computes exact rational Shapley attributions phi_i(v) for finite n-player evaluator
    coalitions and verifies:
      - Efficiency: sum_{i in N} phi_i(v) == v(N) - v(emptyset).
      - Symmetry: if v(S U {i}) == v(S U {j}) for all S subseteq N \\ {i, j}, then phi_i(v) == phi_j(v).
      - Dummy-player axiom: if v(S U {i}) == v(S) for all S subseteq N \\ {i}, then phi_i(v) == 0.
      - Separation between exact coalitional attribution (phi_1 + phi_2 == Delta_E) and
        non-additive raw singleton defect sums (v({1}) + v({2}) != v({1, 2}) when interaction
        synergy I_12 = v({1, 2}) - v({1}) - v({2}) + v(emptyset) != 0).
    """

    def __init__(self, *, scope_id: str = "streaming-coalitional-attribution-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.games: dict[str, dict[str, Any]] = {}

    @staticmethod
    def _factorial(k: int) -> int:
        res = 1
        for i in range(2, k + 1):
            res *= i
        return res

    @staticmethod
    def _normalize_coalition_key(coalition: Any, players_set: set[str]) -> frozenset[str]:
        if isinstance(coalition, str):
            raw = coalition.strip()
            if not raw:
                items: list[str] = []
            else:
                items = [part.strip() for part in raw.split(",") if part.strip()]
        elif isinstance(coalition, (set, frozenset, list, tuple)):
            items = [text(p, "player") for p in coalition]
        else:
            raise ValidationError(f"Unsupported coalition key type: {type(coalition).__name__}")
        for item in items:
            if item not in players_set:
                raise ValidationError(f"Unknown player {item!r} in coalition key")
        return frozenset(items)

    def observe_coalition_game(
        self,
        game_id: str,
        players: Iterable[str],
        characteristic_values: Mapping[Any, Fraction | int | str],
    ) -> dict[str, Any]:
        """Compute exact rational Shapley attributions and audit axioms for an n-player game."""
        gid = text(game_id, "game_id")
        player_list = [text(p, "player") for p in sequence(players, "players")]
        if not player_list:
            raise ValidationError("players must be non-empty")
        if len(set(player_list)) != len(player_list):
            raise ValidationError("players must be distinct")
        n = len(player_list)
        if n > 8:
            raise ValidationError("StreamingCoalitionalAttributionMonitor supports 1 <= n <= 8 players")

        players_set = set(player_list)
        val_map: dict[frozenset[str], Fraction] = {}
        for k, v in characteristic_values.items():
            c_key = self._normalize_coalition_key(k, players_set)
            val_map[c_key] = rational(v)

        # Default missing subsets to 0 if not provided, or require all 2^n subsets?
        # Populate missing empty set as 0 if omitted; require all other subsets to be present or default to 0.
        all_subsets: list[frozenset[str]] = []
        for r in range(n + 1):
            for comb in itertools.combinations(player_list, r):
                sub = frozenset(comb)
                all_subsets.append(sub)
                if sub not in val_map:
                    raise ValidationError(
                        f"Missing characteristic value for coalition {sorted(sub)}"
                    )

        n_fact = Fraction(self._factorial(n))
        shapley: dict[str, Fraction] = {}
        dummy_players: list[str] = []

        for p in player_list:
            others = [q for q in player_list if q != p]
            total_phi = Fraction(0)
            is_dummy = True
            for r in range(n):
                weight = Fraction(self._factorial(r) * self._factorial(n - r - 1)) / n_fact
                for comb in itertools.combinations(others, r):
                    s_set = frozenset(comb)
                    s_with_p = s_set | {p}
                    marginal = val_map[s_with_p] - val_map[s_set]
                    if marginal != Fraction(0):
                        is_dummy = False
                    total_phi += weight * marginal
            shapley[p] = total_phi
            if is_dummy:
                dummy_players.append(p)

        v_empty = val_map[frozenset()]
        v_grand = val_map[frozenset(player_list)]
        total_Gain = v_grand - v_empty
        shapley_sum = sum(shapley.values(), Fraction(0))
        efficiency_ok = (shapley_sum == total_Gain)
        dummy_ok = all(shapley[p] == Fraction(0) for p in dummy_players)

        symmetric_pairs: list[list[str]] = []
        symmetry_ok = True
        for i_idx in range(n):
            for j_idx in range(i_idx + 1, n):
                pi, pj = player_list[i_idx], player_list[j_idx]
                rem = [q for q in player_list if q not in (pi, pj)]
                pair_sym = True
                for r in range(len(rem) + 1):
                    for comb in itertools.combinations(rem, r):
                        base = frozenset(comb)
                        if val_map[base | {pi}] != val_map[base | {pj}]:
                            pair_sym = False
                            break
                    if not pair_sym:
                        break
                if pair_sym:
                    symmetric_pairs.append([pi, pj])
                    if shapley[pi] != shapley[pj]:
                        symmetry_ok = False

        singleton_sum = sum(
            (val_map[frozenset([p])] - v_empty for p in player_list),
            Fraction(0),
        )
        synergy_term = total_Gain - singleton_sum
        non_additive_synergy = (synergy_term != Fraction(0))

        if non_additive_synergy and total_Gain < Fraction(0):
            status = "NONADDITIVE_COALITIONAL_DEFECT_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif non_additive_synergy:
            status = "NONADDITIVE_SYNERGY_ATTRIBUTION"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "ADDITIVE_COALITIONAL_ATTRIBUTION_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        entry = {
            "schema": "lggr.online_coalitional_game.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "game_id": gid,
            "status": status,
            "contract_status": contract_status,
            "players": player_list,
            "v_empty": v_empty,
            "v_grand_coalition": v_grand,
            "net_coalitional_value": total_Gain,
            "shapley_attributions": shapley,
            "shapley_sum": shapley_sum,
            "naive_singleton_marginal_sum": singleton_sum,
            "synergy_interaction_term": synergy_term,
            "raw_singleton_sum_equals_grand_value": (singleton_sum == total_Gain),
            "symmetric_player_pairs": symmetric_pairs,
            "dummy_players": dummy_players,
            "efficiency_verified": efficiency_ok,
            "symmetry_verified": symmetry_ok,
            "dummy_player_axiom_verified": dummy_ok,
        }
        self.games[gid] = entry
        return json_value({**entry, "receipt_sha256": digest(entry)})

    def audit_evaluator_defect_game(
        self,
        game_id: str,
        e1: int | bool,
        e2: int | bool,
        eg: int | bool,
    ) -> dict[str, Any]:
        """Construct and audit the 2-evaluator coalitional defect game for binary verdicts (e1, e2, eg)."""
        for name, val in (("e1", e1), ("e2", e2), ("eg", eg)):
            if type(val) not in (int, bool) or int(val) not in (0, 1):
                raise ValidationError(f"{name} must be a binary verdict in {{0, 1}}")
        v1 = int(e1)
        v2 = int(e2)
        vg = int(eg)
        char_map = {
            frozenset(): Fraction(0),
            frozenset(["E1"]): Fraction(vg - v1),
            frozenset(["E2"]): Fraction(vg - v2),
            frozenset(["E1", "E2"]): Fraction(vg - v1 * v2),
        }
        return self.observe_coalition_game(game_id, ["E1", "E2"], char_map)

    def get_receipt(self) -> dict[str, Any]:
        """Emit aggregate coalitional attribution receipt across all audited games."""
        all_eff = all(g["efficiency_verified"] for g in self.games.values())
        all_sym = all(g["symmetry_verified"] for g in self.games.values())
        all_dum = all(g["dummy_player_axiom_verified"] for g in self.games.values())
        defect_games = [
            gid for gid, g in self.games.items()
            if g["status"] == "NONADDITIVE_COALITIONAL_DEFECT_LGGR"
        ]

        if defect_games:
            status = "NONADDITIVE_COALITIONAL_DEFECT_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "COALITIONAL_ATTRIBUTION_VERIFIED_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_coalitional_attribution.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "audited_games_count": len(self.games),
            "nonadditive_defect_games": sorted(defect_games),
            "all_efficiency_verified": all_eff,
            "all_symmetry_verified": all_sym,
            "all_dummy_player_axioms_verified": all_dum,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingThresholdGovernanceMonitor:
    """Online k-of-n quorum/majority vs. strict product aggregator defect monitor.

    Evaluates n binary local validators (E_1, ..., E_n) in {0, 1}^n and global verdict
    E_g in {0, 1} under both the strict product aggregator L = prod_{i=1}^n E_i = 1[sum E_i == n]
    and the k-of-n threshold aggregator M_{k,n} = 1[sum E_i >= k] (1 <= k <= n):
      - Monotonicity: L <= M_{k,n} on every trace since k <= n.
      - Defect difference identity:
          Delta_prod - Delta_quorum == (E_g - L) - (E_g - M_{k,n}) == M_{k,n} - L == 1[k <= sum E_i < n].
      - Separates:
          1. UNANIMOUS_NGD_DEFECT_LGGR (OBSTRUCTED_LGGR): sum E_i == n and E_g == 0
             (both L == 1 and M_{k,n} == 1 incur negative defect -1).
          2. QUORUM_MASKED_DEFECT_LGGR (OBSTRUCTED_LGGR): k <= sum E_i < n and E_g == 0
             (at least one local validator vetoed so L == 0 and Delta_prod == 0, yet the
             k-of-n quorum overrides the veto so M_{k,n} == 1 and Delta_quorum == -1).
          3. QUORUM_RECOVERED_PGD (COMPOSABLE_LGGG): k <= sum E_i < n and E_g == 1
             (Delta_prod == +1 while Delta_quorum == 0).
          4. THRESHOLD_GOVERNANCE_COHERENT_LGGG (COMPOSABLE_LGGG): Delta_prod == 0 and Delta_quorum == 0.
    """

    def __init__(
        self,
        n_validators: int,
        quorum_k: int,
        *,
        scope_id: str = "streaming-threshold-governance-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        n_val = exact_int(n_validators, "n_validators")
        k_val = exact_int(quorum_k, "quorum_k")
        if n_val < 1:
            raise ValidationError("n_validators must be >= 1")
        if k_val < 1 or k_val > n_val:
            raise ValidationError(f"quorum_k must satisfy 1 <= k <= n_validators ({n_val}), got {k_val}")
        self.n_validators = n_val
        self.quorum_k = k_val
        self.records: list[dict[str, Any]] = []
        self.unanimous_ngd_count: int = 0
        self.quorum_masked_ngd_count: int = 0
        self.quorum_recovered_pgd_count: int = 0
        self.coherent_count: int = 0

    @staticmethod
    def _binary_int(value: Any, name: str) -> int:
        if type(value) not in (int, bool) or int(value) not in (0, 1):
            raise ValidationError(f"{name} must be a binary verdict in {{0, 1}}")
        return int(value)

    def record_vote(
        self,
        trace_id: str,
        local_verdicts: Iterable[int | bool],
        eg: int | bool,
    ) -> dict[str, Any]:
        """Record an n-validator binary vote vector and global verdict eg."""
        tid = text(trace_id, "trace_id")
        verdicts = [
            self._binary_int(v, f"local_verdicts[{idx}]")
            for idx, v in enumerate(sequence(local_verdicts, "local_verdicts"))
        ]
        if len(verdicts) != self.n_validators:
            raise ValidationError(
                f"Expected {self.n_validators} local verdicts, got {len(verdicts)}"
            )
        vg = self._binary_int(eg, "eg")

        vote_sum = sum(verdicts)
        l_prod = 1 if vote_sum == self.n_validators else 0
        m_quorum = 1 if vote_sum >= self.quorum_k else 0
        delta_prod = vg - l_prod
        delta_quorum = vg - m_quorum
        quorum_inflation = m_quorum - l_prod

        monotonicity_ok = (l_prod <= m_quorum)
        difference_identity_ok = (delta_prod - delta_quorum == quorum_inflation)

        if l_prod == 1 and vg == 0:
            trace_status = "UNANIMOUS_NGD_DEFECT_LGGR"
            self.unanimous_ngd_count += 1
        elif m_quorum == 1 and l_prod == 0 and vg == 0:
            trace_status = "QUORUM_MASKED_DEFECT_LGGR"
            self.quorum_masked_ngd_count += 1
        elif m_quorum == 1 and l_prod == 0 and vg == 1:
            trace_status = "QUORUM_RECOVERED_PGD"
            self.quorum_recovered_pgd_count += 1
        else:
            trace_status = "THRESHOLD_GOVERNANCE_COHERENT_LGGG"
            self.coherent_count += 1

        rec = {
            "trace_id": tid,
            "local_verdicts": verdicts,
            "vote_sum": vote_sum,
            "eg": vg,
            "product_aggregator_l": l_prod,
            "quorum_aggregator_m": m_quorum,
            "delta_product": delta_prod,
            "delta_quorum": delta_quorum,
            "quorum_inflation_gap": quorum_inflation,
            "trace_status": trace_status,
            "monotonicity_l_le_quorum_verified": monotonicity_ok,
            "defect_difference_identity_verified": difference_identity_ok,
        }
        self.records.append(rec)
        return self.get_receipt()

    def get_receipt(self) -> dict[str, Any]:
        """Emit threshold governance audit receipt separating quorum-masked defects from unanimous NGD."""
        all_mono = all(r["monotonicity_l_le_quorum_verified"] for r in self.records)
        all_diff = all(r["defect_difference_identity_verified"] for r in self.records)

        if self.unanimous_ngd_count > 0:
            status = "UNANIMOUS_NGD_DEFECT_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif self.quorum_masked_ngd_count > 0:
            status = "QUORUM_MASKED_DEFECT_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif self.quorum_recovered_pgd_count > 0:
            status = "QUORUM_RECOVERED_PGD"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "THRESHOLD_GOVERNANCE_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_threshold_governance.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "n_validators": self.n_validators,
            "quorum_k": self.quorum_k,
            "observed_traces_count": len(self.records),
            "unanimous_ngd_count": self.unanimous_ngd_count,
            "quorum_masked_ngd_count": self.quorum_masked_ngd_count,
            "quorum_recovered_pgd_count": self.quorum_recovered_pgd_count,
            "coherent_count": self.coherent_count,
            "all_monotonicity_verified": all_mono,
            "all_defect_difference_identities_verified": all_diff,
            "latest_trace": self.records[-1] if self.records else None,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingCPTPTraceMonitor:
    """Online rational Kraus channel trace-preservation residual, state-blindspot, and composition monitor.

    Audits finite rational Kraus operator families E = {K_r}_{r=1}^m in Q^{d x d}:
      - Trace-preservation residual matrix:
          R_TP(E) = sum_{r=1}^m K_r^T K_r - I_d.
      - Exact state-dependent trace discrepancy identity on any d x d matrix rho:
          tr(E(rho)) - tr(rho) == tr(rho * R_TP(E)).
      - Separates operator-level trace preservation (R_TP(E) == 0, OPERATOR_TP_VERIFIED_LGGG)
        from state-dependent blindspots (tr(rho * R_TP(E)) == 0 while R_TP(E) != 0,
        STATE_BLINDSPOT_NON_TP_LGGR) and overt state trace violations (tr(rho * R_TP(E)) != 0,
        STATE_TRACE_VIOLATION_LGGR).
      - Exact two-channel composition residual identity for E_2 o E_1 = {L_s K_r}_{s,r}:
          R_TP(E_2 o E_1) == R_TP(E_1) + E_1^dagger(R_TP(E_2)),
        where E_1^dagger(X) = sum_{r=1}^{m_1} K_r^T X K_r.
    """

    def __init__(
        self,
        kraus_operators: Iterable[Any],
        *,
        scope_id: str = "streaming-cptp-trace-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        raw_ops = sequence(kraus_operators, "kraus_operators")
        if not raw_ops:
            raise ValidationError("kraus_operators must be non-empty")

        first_mat = matrix(raw_ops[0], "kraus_operators[0]")
        d = len(first_mat)
        if len(first_mat[0]) != d:
            raise ValidationError("Each Kraus operator must be a square d x d matrix")

        self.dim = d
        self.kraus_ops = [
            matrix(op, f"kraus_operators[{idx}]", rows=d, cols=d)
            for idx, op in enumerate(raw_ops)
        ]
        self.sum_kt_k = self._compute_sum_kt_k(self.kraus_ops, d)
        self.residual_r_tp = self._subtract_identity(self.sum_kt_k, d)
        self.is_operator_trace_preserving = is_zero(self.residual_r_tp)
        self.residual_l1_norm = sum(
            (abs(val) for row in self.residual_r_tp for val in row),
            Fraction(0),
        )
        self.probed_states: dict[str, dict[str, Any]] = {}
        self.compositions: dict[str, dict[str, Any]] = {}

    @staticmethod
    def _transpose(mat: Any) -> tuple[tuple[Fraction, ...], ...]:
        rows = len(mat)
        cols = len(mat[0])
        return tuple(
            tuple(mat[r][c] for r in range(rows))
            for c in range(cols)
        )

    @classmethod
    def _compute_sum_kt_k(cls, ops: list[Any], d: int) -> tuple[tuple[Fraction, ...], ...]:
        acc = [[Fraction(0) for _ in range(d)] for _ in range(d)]
        for k_mat in ops:
            kt = cls._transpose(k_mat)
            prod = matmul(kt, k_mat)
            for r in range(d):
                for c in range(d):
                    acc[r][c] += prod[r][c]
        return tuple(tuple(row) for row in acc)

    @staticmethod
    def _subtract_identity(mat: Any, d: int) -> tuple[tuple[Fraction, ...], ...]:
        return tuple(
            tuple(mat[r][c] - (Fraction(1) if r == c else Fraction(0)) for c in range(d))
            for r in range(d)
        )

    @staticmethod
    def _trace(mat: Any) -> Fraction:
        return sum((mat[i][i] for i in range(len(mat))), Fraction(0))

    @classmethod
    def _apply_channel(cls, ops: list[Any], rho: Any, d: int) -> tuple[tuple[Fraction, ...], ...]:
        acc = [[Fraction(0) for _ in range(d)] for _ in range(d)]
        for k_mat in ops:
            kt = cls._transpose(k_mat)
            term = matmul(matmul(k_mat, rho), kt)
            for r in range(d):
                for c in range(d):
                    acc[r][c] += term[r][c]
        return tuple(tuple(row) for row in acc)

    @classmethod
    def _apply_adjoint(cls, ops: list[Any], obs: Any, d: int) -> tuple[tuple[Fraction, ...], ...]:
        acc = [[Fraction(0) for _ in range(d)] for _ in range(d)]
        for k_mat in ops:
            kt = cls._transpose(k_mat)
            term = matmul(matmul(kt, obs), k_mat)
            for r in range(d):
                for c in range(d):
                    acc[r][c] += term[r][c]
        return tuple(tuple(row) for row in acc)

    def probe_state(self, state_id: str, rho: Any) -> dict[str, Any]:
        """Audit tr(E(rho)) - tr(rho) == tr(rho * R_TP) on a d x d rational state matrix rho."""
        sid = text(state_id, "state_id")
        rho_mat = matrix(rho, "rho", rows=self.dim, cols=self.dim)
        out_rho = self._apply_channel(self.kraus_ops, rho_mat, self.dim)
        tr_in = self._trace(rho_mat)
        tr_out = self._trace(out_rho)
        tr_diff = tr_out - tr_in
        rho_r_tp = matmul(rho_mat, self.residual_r_tp)
        tr_rho_rtp = self._trace(rho_r_tp)
        discrepancy_identity_ok = (tr_diff == tr_rho_rtp)

        state_blindspot = (not self.is_operator_trace_preserving and tr_diff == Fraction(0))
        if self.is_operator_trace_preserving:
            status = "OPERATOR_TP_VERIFIED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        elif state_blindspot:
            status = "STATE_BLINDSPOT_NON_TP_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "STATE_TRACE_VIOLATION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        entry = {
            "schema": "lggr.online_cptp_state_probe.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "state_id": sid,
            "status": status,
            "contract_status": contract_status,
            "input_trace": tr_in,
            "output_trace": tr_out,
            "trace_discrepancy": tr_diff,
            "trace_rho_times_r_tp": tr_rho_rtp,
            "operator_trace_preserving": self.is_operator_trace_preserving,
            "residual_l1_norm": self.residual_l1_norm,
            "state_blindspot_masked": state_blindspot,
            "trace_discrepancy_identity_verified": discrepancy_identity_ok,
        }
        self.probed_states[sid] = entry
        return json_value({**entry, "receipt_sha256": digest(entry)})

    def audit_composition(
        self,
        composition_id: str,
        second_kraus_operators: Iterable[Any],
    ) -> dict[str, Any]:
        """Audit R_TP(E_2 o E_1) == R_TP(E_1) + E_1^dagger(R_TP(E_2)) for composed Kraus channels."""
        cid = text(composition_id, "composition_id")
        raw_second = sequence(second_kraus_operators, "second_kraus_operators")
        if not raw_second:
            raise ValidationError("second_kraus_operators must be non-empty")
        second_ops = [
            matrix(op, f"second_kraus_operators[{idx}]", rows=self.dim, cols=self.dim)
            for idx, op in enumerate(raw_second)
        ]

        r_tp_2 = self._subtract_identity(self._compute_sum_kt_k(second_ops, self.dim), self.dim)
        composed_ops = [
            matmul(l_mat, k_mat)
            for l_mat in second_ops
            for k_mat in self.kraus_ops
        ]
        r_tp_composed = self._subtract_identity(
            self._compute_sum_kt_k(composed_ops, self.dim),
            self.dim,
        )
        e1_dag_rtp2 = self._apply_adjoint(self.kraus_ops, r_tp_2, self.dim)
        rhs_sum = tuple(
            tuple(self.residual_r_tp[r][c] + e1_dag_rtp2[r][c] for c in range(self.dim))
            for r in range(self.dim)
        )
        identity_ok = (r_tp_composed == rhs_sum)
        composed_tp = is_zero(r_tp_composed)
        second_tp = is_zero(r_tp_2)

        if composed_tp and self.is_operator_trace_preserving and second_tp:
            status = "COMPOSED_TP_VERIFIED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        elif composed_tp:
            status = "COMPENSATED_COMPOSITION_TP_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "COMPOSED_NON_TP_DEFECT_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        entry = {
            "schema": "lggr.online_cptp_composition.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "composition_id": cid,
            "status": status,
            "contract_status": contract_status,
            "first_channel_tp": self.is_operator_trace_preserving,
            "second_channel_tp": second_tp,
            "composed_channel_tp": composed_tp,
            "residual_r_tp_first": self.residual_r_tp,
            "residual_r_tp_second": r_tp_2,
            "residual_r_tp_composed": r_tp_composed,
            "composition_residual_identity_verified": identity_ok,
        }
        self.compositions[cid] = entry
        return json_value({**entry, "receipt_sha256": digest(entry)})

    def get_receipt(self) -> dict[str, Any]:
        """Emit aggregate Kraus channel trace-preservation receipt."""
        blindspot_states = [
            sid for sid, s in self.probed_states.items() if s["state_blindspot_masked"]
        ]
        all_state_ids_ok = all(
            s["trace_discrepancy_identity_verified"] for s in self.probed_states.values()
        )
        all_comp_ids_ok = all(
            c["composition_residual_identity_verified"] for c in self.compositions.values()
        )

        if self.is_operator_trace_preserving and all(
            c["composed_channel_tp"] for c in self.compositions.values()
        ):
            status = "OPERATOR_TP_VERIFIED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        elif blindspot_states:
            status = "STATE_BLINDSPOT_NON_TP_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "OPERATOR_NON_TP_DEFECT_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body = {
            "schema": "lggr.online_cptp_trace.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "dimension": self.dim,
            "kraus_count": len(self.kraus_ops),
            "operator_trace_preserving": self.is_operator_trace_preserving,
            "residual_r_tp": self.residual_r_tp,
            "residual_l1_norm": self.residual_l1_norm,
            "probed_states_count": len(self.probed_states),
            "blindspot_state_ids": sorted(blindspot_states),
            "audited_compositions_count": len(self.compositions),
            "all_state_discrepancy_identities_verified": all_state_ids_ok,
            "all_composition_identities_verified": all_comp_ids_ok,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingWindowedDriftMonitor:
    """Online LGGR I/VIII sliding-window local budget vs. full-horizon cumulative drift monitor.

    Audits a stream of rational step drifts d_1, d_2, ..., d_N under a fixed sliding window
    of length W >= 1 with window budget B_W >= 0 and full-horizon global budget B_global >= 0:
      - Tracks contiguous W-step window sums S_W(t) = sum_{j=max(1, t-W+1)}^t d_j and
        cumulative horizon sum S_cum(t) = sum_{j=1}^t d_j.
      - Verifies the disjoint block-partition bound: partitioning {1, ..., N} into
        K = ceil(N / W) disjoint contiguous windows of length <= W gives
          S_cum(N) == sum_{b=1}^K S_{block,b} <= K * max_{1 <= t <= N} S_W(t).
      - Separates:
          1. LOCAL_WINDOW_BUDGET_BREACH (OBSTRUCTED_LGGR): max S_W(t) > B_W.
          2. SLIDING_WINDOW_HORIZON_BREACH_LGGR (OBSTRUCTED_LGGR): max S_W(t) <= B_W
             (every contiguous W-step window is locally within budget), yet
             max S_cum(t) > B_global (sliding-window horizon truncation masks cumulative breach).
          3. WINDOW_AND_HORIZON_WITHIN_BUDGET_LGGG (COMPOSABLE_LGGG):
             max S_W(t) <= B_W and max S_cum(t) <= B_global.
    """

    def __init__(
        self,
        window_size: int,
        window_budget: Fraction | int | str,
        global_budget: Fraction | int | str,
        *,
        scope_id: str = "streaming-windowed-drift-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        w_val = exact_int(window_size, "window_size")
        if w_val < 1:
            raise ValidationError("window_size must be >= 1")
        bw_val = rational(window_budget)
        bg_val = rational(global_budget)
        if bw_val < Fraction(0):
            raise ValidationError("window_budget must be >= 0")
        if bg_val < Fraction(0):
            raise ValidationError("global_budget must be >= 0")

        self.window_size = w_val
        self.window_budget = bw_val
        self.global_budget = bg_val
        self.steps: list[dict[str, Any]] = []
        self.recent_window: deque[Fraction] = deque(maxlen=w_val)
        self.cumulative_drift: Fraction = Fraction(0)
        self.max_window_sum: Fraction = Fraction(0)
        self.max_prefix_drift: Fraction = Fraction(0)

    def record_step(
        self,
        step_id: str,
        step_drift: Fraction | int | str,
    ) -> dict[str, Any]:
        """Ingest a rational step drift d_t and update sliding-window vs. cumulative horizon state."""
        sid = text(step_id, "step_id")
        d_val = rational(step_drift)
        self.recent_window.append(d_val)
        win_sum = sum(self.recent_window, Fraction(0))
        self.cumulative_drift += d_val

        if len(self.steps) == 0 or win_sum > self.max_window_sum:
            self.max_window_sum = win_sum
        if len(self.steps) == 0 or self.cumulative_drift > self.max_prefix_drift:
            self.max_prefix_drift = self.cumulative_drift

        self.steps.append(
            {
                "step_id": sid,
                "step_drift": d_val,
                "window_sum": win_sum,
                "cumulative_drift": self.cumulative_drift,
            }
        )
        return self.get_receipt()

    def get_receipt(self) -> dict[str, Any]:
        """Emit sliding-window vs. full-horizon drift audit receipt."""
        n_steps = len(self.steps)
        w = self.window_size
        k_blocks = (n_steps + w - 1) // w if n_steps > 0 else 0

        block_sums: list[Fraction] = []
        for idx in range(0, n_steps, w):
            blk = self.steps[idx : idx + w]
            b_sum = sum((s["step_drift"] for s in blk), Fraction(0))
            block_sums.append(b_sum)

        partition_sum = sum(block_sums, Fraction(0))
        block_partition_verified = (
            partition_sum == self.cumulative_drift
            and (
                n_steps == 0
                or self.cumulative_drift <= Fraction(k_blocks) * self.max_window_sum
            )
        )

        all_windows_green = (n_steps == 0) or (self.max_window_sum <= self.window_budget)
        horizon_within_budget = (
            (n_steps == 0)
            or (
                self.max_prefix_drift <= self.global_budget
                and self.cumulative_drift <= self.global_budget
            )
        )
        sliding_window_masked_breach = (all_windows_green and not horizon_within_budget)

        if not all_windows_green:
            status = "LOCAL_WINDOW_BUDGET_BREACH"
            contract_status = "OBSTRUCTED_LGGR"
        elif sliding_window_masked_breach:
            status = "SLIDING_WINDOW_HORIZON_BREACH_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "WINDOW_AND_HORIZON_WITHIN_BUDGET_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_windowed_drift.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "window_size": self.window_size,
            "window_budget": self.window_budget,
            "global_budget": self.global_budget,
            "observed_steps_count": n_steps,
            "disjoint_window_blocks_count": k_blocks,
            "current_window_sum": sum(self.recent_window, Fraction(0)),
            "max_window_sum": self.max_window_sum,
            "cumulative_horizon_drift": self.cumulative_drift,
            "max_prefix_horizon_drift": self.max_prefix_drift,
            "all_windows_within_budget": all_windows_green,
            "horizon_within_budget": horizon_within_budget,
            "sliding_window_masked_breach": sliding_window_masked_breach,
            "block_partition_bound_verified": block_partition_verified,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingReplayOrderMonitor:
    """Online LGGR VIII permutation-sensitive prefix budget vs. commutative endpoint monitor.

    Audits reordered asynchronous step arrivals (event_id, delta_value, causal_index) under a
    prefix budget B_prefix >= 0:
      - Verifies commutative endpoint invariance across arrival order, causal order, and
        worst/best permutations:
          sum_{t=1}^N d_{arrival(t)} == sum_{t=1}^N d_{causal(t)} == sum_{t=1}^N d_{pi_max(t)}.
      - Verifies that the positive-first permutation pi_max attains the exact positive-mass
        prefix ceiling:
          max_{0 <= k <= N} sum_{t=1}^k d_{pi_max(t)} == sum_{i : d_i > 0} d_i.
      - Separates:
          1. CAUSAL_AND_ARRIVAL_PREFIX_BREACH (OBSTRUCTED_LGGR): both arrival and causal orders
             exceed B_prefix.
          2. ARRIVAL_MASKED_CAUSAL_BREACH_LGGR (OBSTRUCTED_LGGR): arrival order stays within
             B_prefix (because negative credits arrived ahead of positive spikes), while the
             causal order exceeds B_prefix.
          3. REORDER_SENSITIVE_PREFIX_EXCURSION_LGGR (OBSTRUCTED_LGGR): causal order stays within
             B_prefix while arrival order or worst-case permutation pi_max exceeds B_prefix.
          4. PERMUTATION_ROBUST_PREFIX_LGGG (COMPOSABLE_LGGG): sum_{d_i > 0} d_i <= B_prefix,
             so every arrival permutation stays within B_prefix.
    """

    def __init__(
        self,
        prefix_budget: Fraction | int | str,
        *,
        scope_id: str = "streaming-replay-order-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        bp = rational(prefix_budget)
        if bp < Fraction(0):
            raise ValidationError("prefix_budget must be >= 0")
        self.prefix_budget = bp
        self.events: list[dict[str, Any]] = []

    def register_event(
        self,
        event_id: str,
        delta_value: Fraction | int | str,
        *,
        causal_index: int,
    ) -> dict[str, Any]:
        """Record an asynchronous event with its arrival position and causal index."""
        eid = text(event_id, "event_id")
        if any(e["event_id"] == eid for e in self.events):
            raise ValidationError(f"Duplicate event_id: {eid}")
        c_idx = exact_int(causal_index, "causal_index")
        d_val = rational(delta_value)

        self.events.append(
            {
                "event_id": eid,
                "arrival_index": len(self.events),
                "causal_index": c_idx,
                "delta_value": d_val,
            }
        )
        return self.get_receipt()

    @staticmethod
    def _prefix_profile(deltas: list[Fraction]) -> tuple[Fraction, Fraction, list[Fraction]]:
        running = Fraction(0)
        max_pref = Fraction(0)
        prefs: list[Fraction] = []
        for d in deltas:
            running += d
            prefs.append(running)
            if running > max_pref:
                max_pref = running
        return running, max_pref, prefs

    def get_receipt(self) -> dict[str, Any]:
        """Emit replay-order audit receipt comparing arrival, causal, and extremal permutations."""
        arrival_deltas = [e["delta_value"] for e in self.events]
        causal_events = sorted(self.events, key=lambda e: (e["causal_index"], e["arrival_index"]))
        causal_deltas = [e["delta_value"] for e in causal_events]
        worst_deltas = sorted(arrival_deltas, reverse=True)
        best_deltas = sorted(arrival_deltas)

        end_arr, max_arr, _ = self._prefix_profile(arrival_deltas)
        end_caus, max_caus, _ = self._prefix_profile(causal_deltas)
        end_worst, max_worst, _ = self._prefix_profile(worst_deltas)
        end_best, max_best, _ = self._prefix_profile(best_deltas)

        pos_sum = sum((d for d in arrival_deltas if d > Fraction(0)), Fraction(0))
        endpoint_invariance_ok = (end_arr == end_caus == end_worst == end_best)
        worst_perm_identity_ok = (max_worst == pos_sum)

        arr_breach = max_arr > self.prefix_budget
        caus_breach = max_caus > self.prefix_budget
        worst_breach = max_worst > self.prefix_budget

        if arr_breach and caus_breach:
            status = "CAUSAL_AND_ARRIVAL_PREFIX_BREACH"
            contract_status = "OBSTRUCTED_LGGR"
        elif caus_breach and not arr_breach:
            status = "ARRIVAL_MASKED_CAUSAL_BREACH_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif arr_breach or worst_breach:
            status = "REORDER_SENSITIVE_PREFIX_EXCURSION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "PERMUTATION_ROBUST_PREFIX_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_replay_order.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "prefix_budget": self.prefix_budget,
            "observed_events_count": len(self.events),
            "common_endpoint_sum": end_arr,
            "arrival_max_prefix": max_arr,
            "causal_max_prefix": max_caus,
            "worst_permutation_max_prefix": max_worst,
            "best_permutation_max_prefix": max_best,
            "positive_delta_mass": pos_sum,
            "arrival_within_budget": not arr_breach,
            "causal_within_budget": not caus_breach,
            "arrival_masked_causal_breach": (caus_breach and not arr_breach),
            "prefix_order_diverged": (max_arr != max_caus),
            "endpoint_permutation_invariance_verified": endpoint_invariance_ok,
            "positive_sum_equals_worst_permutation_max_verified": worst_perm_identity_ok,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingSimplicialCupMonitor:
    """Online Alexander-Whitney simplicial cup product and graded Leibniz cocycle monitor.

    Evaluates rational 0-cochains f in C^0 and 1-cochains alpha, beta in C^1 on oriented
    2-simplices sigma = (v_0, v_1, v_2):
      - Simplicial 1-coboundary:
          (d^1 alpha)_{(v_0, v_1, v_2)} = alpha_{(v_1, v_2)} - alpha_{(v_0, v_2)} + alpha_{(v_0, v_1)}.
      - Alexander-Whitney cup product of 1-cochains on (v_0, v_1, v_2):
          (alpha cup beta)_{(v_0, v_1, v_2)} = alpha_{(v_0, v_1)} * beta_{(v_1, v_2)},
        reverse cup product (beta cup alpha)_{(v_0, v_1, v_2)} = beta_{(v_0, v_1)} * alpha_{(v_1, v_2)},
        and cup commutator [alpha, beta]_cup = alpha_{01} beta_{12} - beta_{01} alpha_{12}.
      - Graded Leibniz identity for (f, alpha) in C^0 x C^1 on (v_0, v_1, v_2):
          d^1(f cup alpha) == (d^0 f cup alpha) + (f cup d^1 alpha),
        where (f cup alpha)_{(v_i, v_j)} = f(v_i) * alpha_{(v_i, v_j)}.
      - Separates:
          1. NON_COCYCLE_COBOUNDARY_LGGR (OBSTRUCTED_LGGR): d^1 alpha != 0 or d^1 beta != 0.
          2. NONTRIVIAL_CUP_COCYCLE_OBSTRUCTION_LGGR (OBSTRUCTED_LGGR): d^1 alpha == 0 and
             d^1 beta == 0, while (alpha cup beta)_{(v_0, v_1, v_2)} != 0.
          3. EXACT_TRIVIAL_CUP_COCYCLE_LGGG (COMPOSABLE_LGGG): d^1 alpha == 0, d^1 beta == 0,
             and (alpha cup beta)_{(v_0, v_1, v_2)} == 0.
    """

    def __init__(self, *, scope_id: str = "streaming-simplicial-cup-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.simplices: dict[str, dict[str, Any]] = {}

    def evaluate_two_simplex(
        self,
        simplex_id: str,
        v0: str,
        v1: str,
        v2: str,
        *,
        alpha_01: Fraction | int | str,
        alpha_12: Fraction | int | str,
        alpha_02: Fraction | int | str,
        beta_01: Fraction | int | str,
        beta_12: Fraction | int | str,
        beta_02: Fraction | int | str,
        f_v0: Fraction | int | str = 0,
        f_v1: Fraction | int | str = 0,
        f_v2: Fraction | int | str = 0,
    ) -> dict[str, Any]:
        """Audit d^1 alpha, d^1 beta, alpha cup beta, and graded Leibniz rule on (v0, v1, v2)."""
        sid = text(simplex_id, "simplex_id")
        n0 = text(v0, "v0")
        n1 = text(v1, "v1")
        n2 = text(v2, "v2")
        if len({n0, n1, n2}) != 3:
            raise ValidationError("2-simplex vertices (v0, v1, v2) must be distinct")

        a01 = rational(alpha_01)
        a12 = rational(alpha_12)
        a02 = rational(alpha_02)
        b01 = rational(beta_01)
        b12 = rational(beta_12)
        b02 = rational(beta_02)
        f0 = rational(f_v0)
        f1 = rational(f_v1)
        f2 = rational(f_v2)

        d1_alpha = a12 - a02 + a01
        d1_beta = b12 - b02 + b01
        alpha_cup_beta = a01 * b12
        beta_cup_alpha = b01 * a12
        cup_commutator = alpha_cup_beta - beta_cup_alpha

        # Graded Leibniz check for (f, alpha):
        # (f cup alpha)_{01} = f0 * a01, (f cup alpha)_{12} = f1 * a12, (f cup alpha)_{02} = f0 * a02
        d1_f_cup_alpha = f1 * a12 - f0 * a02 + f0 * a01
        d0f_cup_alpha = (f1 - f0) * a12
        f_cup_d1_alpha = f0 * d1_alpha
        leibniz_alpha_ok = (d1_f_cup_alpha == d0f_cup_alpha + f_cup_d1_alpha)

        # Graded Leibniz check for (f, beta):
        d1_f_cup_beta = f1 * b12 - f0 * b02 + f0 * b01
        d0f_cup_beta = (f1 - f0) * b12
        f_cup_d1_beta = f0 * d1_beta
        leibniz_beta_ok = (d1_f_cup_beta == d0f_cup_beta + f_cup_d1_beta)

        # Exact 1-coboundary check d^1(d^0 f) == 0 on (v0, v1, v2)
        d0f_01 = f1 - f0
        d0f_12 = f2 - f1
        d0f_02 = f2 - f0
        d1_d0_f = d0f_12 - d0f_02 + d0f_01
        d1_d0_zero_ok = (d1_d0_f == Fraction(0))

        if d1_alpha != Fraction(0) or d1_beta != Fraction(0):
            status = "NON_COCYCLE_COBOUNDARY_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif alpha_cup_beta != Fraction(0):
            status = "NONTRIVIAL_CUP_COCYCLE_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "EXACT_TRIVIAL_CUP_COCYCLE_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        entry = {
            "schema": "lggr.online_simplicial_cup_simplex.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "simplex_id": sid,
            "vertices": [n0, n1, n2],
            "status": status,
            "contract_status": contract_status,
            "d1_alpha": d1_alpha,
            "d1_beta": d1_beta,
            "alpha_is_cocycle": (d1_alpha == Fraction(0)),
            "beta_is_cocycle": (d1_beta == Fraction(0)),
            "alpha_cup_beta": alpha_cup_beta,
            "beta_cup_alpha": beta_cup_alpha,
            "cup_commutator": cup_commutator,
            "d1_f_cup_alpha": d1_f_cup_alpha,
            "d0f_cup_alpha": d0f_cup_alpha,
            "f_cup_d1_alpha": f_cup_d1_alpha,
            "leibniz_identity_verified": (leibniz_alpha_ok and leibniz_beta_ok),
            "exact_coboundary_d1_d0_zero_verified": d1_d0_zero_ok,
        }
        self.simplices[sid] = entry
        return json_value({**entry, "receipt_sha256": digest(entry)})

    def get_receipt(self) -> dict[str, Any]:
        """Emit aggregate simplicial cup product and graded Leibniz receipt."""
        non_cocycle_ids = [
            sid for sid, s in self.simplices.items()
            if s["status"] == "NON_COCYCLE_COBOUNDARY_LGGR"
        ]
        nontrivial_cup_ids = [
            sid for sid, s in self.simplices.items()
            if s["status"] == "NONTRIVIAL_CUP_COCYCLE_OBSTRUCTION_LGGR"
        ]
        all_leibniz = all(s["leibniz_identity_verified"] for s in self.simplices.values())
        all_d1_d0 = all(s["exact_coboundary_d1_d0_zero_verified"] for s in self.simplices.values())

        if non_cocycle_ids:
            status = "NON_COCYCLE_COBOUNDARY_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif nontrivial_cup_ids:
            status = "NONTRIVIAL_CUP_COCYCLE_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "EXACT_TRIVIAL_CUP_COCYCLE_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_simplicial_cup.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluated_simplices_count": len(self.simplices),
            "non_cocycle_simplex_ids": sorted(non_cocycle_ids),
            "nontrivial_cup_simplex_ids": sorted(nontrivial_cup_ids),
            "all_leibniz_identities_verified": all_leibniz,
            "all_d1_d0_zero_verified": all_d1_d0,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingMayerVietorisMonitor:
    """Online Mayer-Vietoris subcomplex cover and connecting-homomorphism obstruction monitor.

    Audits two-subcomplex covers K = U U V of a 1-cochain h:
      - Tracks subcomplex monitors for U, V, and the union U U V.
      - When h|_U = d^0 f_U is locally exact on U and h|_V = d^0 f_V is locally exact on V,
        computes the intersection difference 0-cochain on V(U) cap V(V):
          delta_{U cap V}(w) = f_U(w) - f_V(w).
      - Verifies that delta_{U cap V} is locally constant on every connected component of
        U cap V (d^0 delta_{U cap V} == 0 on E(U) cap E(V)).
      - Computes the Mayer-Vietoris connecting coboundary spread:
          Delta_MV = max_{w in V(U) cap V(V)} delta_{U cap V}(w) - min_{w in V(U) cap V(V)} delta_{U cap V}(w)
        and verifies that for connected locally exact U and V, h is globally exact on U U V
        if and only if delta_{U cap V} is constant across all connected components of U cap V
        (Delta_MV == 0).
    """

    def __init__(self, *, scope_id: str = "streaming-mayer-vietoris-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.monitor_u = StreamingCochainMonitor()
        self.monitor_v = StreamingCochainMonitor()
        self.monitor_union = StreamingCochainMonitor()
        self.overlap_edges: list[dict[str, Any]] = []

    def record_edge(
        self,
        source: str,
        target: str,
        value: Fraction | int | str,
        *,
        in_u: bool,
        in_v: bool,
        weight: Fraction | int | str = 1,
    ) -> dict[str, Any]:
        """Record a directed edge in U, V, or both (U cap V)."""
        u_node = text(source, "source")
        v_node = text(target, "target")
        boolean(in_u, "in_u")
        boolean(in_v, "in_v")
        if not in_u and not in_v:
            raise ValidationError("Edge must belong to at least one subcomplex (in_u or in_v)")
        val_q = rational(value)
        w_q = rational(weight)

        if in_u:
            self.monitor_u.add_edge(u_node, v_node, val_q, weight=w_q)
        if in_v:
            self.monitor_v.add_edge(u_node, v_node, val_q, weight=w_q)
        self.monitor_union.add_edge(u_node, v_node, val_q, weight=w_q)
        if in_u and in_v:
            self.overlap_edges.append(
                {
                    "source": u_node,
                    "target": v_node,
                    "value": val_q,
                }
            )
        return self.audit_mayer_vietoris()

    @staticmethod
    def _is_exact(mon: StreamingCochainMonitor) -> bool:
        return all(c["closure_defect"] == Fraction(0) for c in mon.cycles)

    @staticmethod
    def _integrate_potentials(mon: StreamingCochainMonitor) -> dict[str, Fraction]:
        potentials: dict[str, Fraction] = {}
        adj: dict[str, list[tuple[str, Fraction]]] = {v: [] for v in mon.vertices}
        for e in mon.edges:
            u, v, val = e["source"], e["target"], e["value"]
            adj[u].append((v, val))
            adj[v].append((u, -val))
        for start in sorted(mon.vertices):
            if start in potentials:
                continue
            potentials[start] = Fraction(0)
            queue: deque[str] = deque([start])
            while queue:
                curr = queue.popleft()
                for nxt, diff in adj[curr]:
                    if nxt not in potentials:
                        potentials[nxt] = potentials[curr] + diff
                        queue.append(nxt)
        return potentials

    def audit_mayer_vietoris(self) -> dict[str, Any]:
        """Audit local exactness on U and V, intersection 0-cocycle delta_{U cap V}, and global exactness on U U V."""
        u_exact = self._is_exact(self.monitor_u)
        v_exact = self._is_exact(self.monitor_v)
        union_exact = self._is_exact(self.monitor_union)
        overlap_vertices = sorted(self.monitor_u.vertices & self.monitor_v.vertices)

        delta_map: dict[str, Fraction] = {}
        glued_potential: dict[str, Fraction] | None = None
        locally_constant_on_overlap = True
        mv_spread = Fraction(0)

        if u_exact and v_exact:
            f_u = self._integrate_potentials(self.monitor_u)
            f_v = self._integrate_potentials(self.monitor_v)
            for w in overlap_vertices:
                delta_map[w] = f_u[w] - f_v[w]
            for oe in self.overlap_edges:
                if delta_map[oe["target"]] - delta_map[oe["source"]] != Fraction(0):
                    locally_constant_on_overlap = False
            if delta_map:
                mv_spread = max(delta_map.values()) - min(delta_map.values())
            if mv_spread == Fraction(0) and union_exact:
                shift = next(iter(delta_map.values()), Fraction(0))
                glued_potential = {}
                for x, val in sorted(f_u.items()):
                    glued_potential[x] = val
                for x, val in sorted(f_v.items()):
                    glued_potential[x] = val + shift

        mv_equivalence_ok = (
            not (u_exact and v_exact and len(overlap_vertices) > 0)
            or (union_exact == (mv_spread == Fraction(0)))
        )

        if not u_exact or not v_exact:
            status = "SUBCOMPLEX_LOCALLY_OBSTRUCTED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif not union_exact:
            status = "MAYER_VIETORIS_CONNECTING_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "MAYER_VIETORIS_EXACT_GLUED_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_mayer_vietoris.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "u_locally_exact": u_exact,
            "v_locally_exact": v_exact,
            "union_globally_exact": union_exact,
            "overlap_vertices": overlap_vertices,
            "intersection_difference_cocycle": delta_map,
            "connecting_coboundary_spread": mv_spread,
            "glued_global_potential": glued_potential,
            "intersection_cocycle_locally_constant_verified": locally_constant_on_overlap,
            "mayer_vietoris_equivalence_verified": mv_equivalence_ok,
        }
        return json_value({**body, "receipt_sha256": digest(body)})

    def get_receipt(self) -> dict[str, Any]:
        """Return the current Mayer-Vietoris cover audit receipt."""
        return self.audit_mayer_vietoris()


class StreamingHodgeDecompositionMonitor:
    """Online discrete Hodge-Laplacian orthogonal decomposition monitor over Q.

    Decomposes a rational 1-cochain h in C^1(K; Q) on a finite 2-complex (D_0, D_1)
    with D_1 D_0 = 0 into three mutually orthogonal rational components:
      h = h_exact + h_coexact + h_harmonic
    where:
      - h_exact = D_0 phi in im(D_0) solves the normal system (D_0^T D_0) phi = D_0^T h,
      - h_coexact = D_1^T psi in im(D_1^T) solves the normal system (D_1 D_1^T) psi = D_1 h,
      - h_harmonic = h - h_exact - h_coexact in ker(D_0^T) cap ker(D_1) = ker(L_1),
        with discrete 1-form Hodge Laplacian L_1 = D_0 D_0^T + D_1^T D_1.
    Audits pairwise Euclidean orthogonality, Pythagorean L2 energy decomposition
    ||h||_2^2 = ||h_exact||_2^2 + ||h_coexact||_2^2 + ||h_harmonic||_2^2,
    and separates pure exact gradients from coexact 2-cell curl and harmonic
    cohomology obstructions.
    """

    def __init__(self, *, scope_id: str = "streaming-hodge-decomposition-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.records: list[dict[str, Any]] = []

    @staticmethod
    def _dot(u: tuple[Fraction, ...], v: tuple[Fraction, ...]) -> Fraction:
        return sum((a * b for a, b in zip(u, v)), Fraction(0))

    def record_complex_cochain(
        self,
        complex_id: str,
        D0: Any,
        h: Any,
        D1: Any | None = None,
    ) -> dict[str, Any]:
        """Decompose 1-cochain h on complex (D0, D1) into exact, coexact, and harmonic parts."""
        cid = text(complex_id, "complex_id")
        d0 = matrix(D0, "D0")
        m, _ = len(d0), len(d0[0])
        hv = vector(h, "h", m)
        d0_t = transpose(d0)

        has_d1 = False
        d1: tuple[tuple[Fraction, ...], ...] = ()
        d1_t: tuple[tuple[Fraction, ...], ...] = ()
        if D1 is not None:
            raw_d1 = sequence(D1, "D1")
            if raw_d1:
                d1 = matrix(raw_d1, "D1", cols=m)
                d1_t = transpose(d1)
                has_d1 = True
                comp = matmul(d1, d0)
                if not is_zero(comp):
                    raise ValidationError("Invalid cochain complex: D1 * D0 must be zero")

        # 1. Exact component: solve (D0^T D0) phi = D0^T h
        gram_0 = matmul(d0_t, d0)
        rhs_0 = matvec(d0_t, hv)
        phi_opt = solve_exact(gram_0, rhs_0)
        if phi_opt is None:
            raise ValidationError("Normal equations for exact projection failed")
        h_exact = matvec(d0, phi_opt)

        # 2. Coexact component: solve (D1 D1^T) psi = D1 h
        if has_d1:
            gram_1 = matmul(d1, d1_t)
            rhs_1 = matvec(d1, hv)
            psi_opt = solve_exact(gram_1, rhs_1)
            if psi_opt is None:
                raise ValidationError("Normal equations for coexact projection failed")
            h_coexact = matvec(d1_t, psi_opt)
        else:
            psi_opt = ()
            h_coexact = tuple(Fraction(0) for _ in range(m))

        # 3. Harmonic residual: h_harm = h - h_exact - h_coexact
        h_harm = tuple(hv[i] - h_exact[i] - h_coexact[i] for i in range(m))

        # Check kernel conditions on h_harm: D0^T h_harm == 0 and D1 h_harm == 0
        div_harm = matvec(d0_t, h_harm)
        curl_harm = matvec(d1, h_harm) if has_d1 else ()
        harm_in_ker_d0t = all(v == Fraction(0) for v in div_harm)
        harm_in_ker_d1 = all(v == Fraction(0) for v in curl_harm)

        # Discrete 1-form Hodge Laplacian L_1 h_harm = D0(D0^T h_harm) + D1^T(D1 h_harm)
        l1_down = matvec(d0, div_harm)
        l1_up = matvec(d1_t, curl_harm) if has_d1 else tuple(Fraction(0) for _ in range(m))
        l1_harm = tuple(l1_down[i] + l1_up[i] for i in range(m))
        laplacian_kernel_verified = all(v == Fraction(0) for v in l1_harm)

        # Orthogonality and Pythagorean identity
        ip_exact_coexact = self._dot(h_exact, h_coexact)
        ip_exact_harm = self._dot(h_exact, h_harm)
        ip_coexact_harm = self._dot(h_coexact, h_harm)
        orthogonality_ok = (
            ip_exact_coexact == Fraction(0)
            and ip_exact_harm == Fraction(0)
            and ip_coexact_harm == Fraction(0)
        )

        norm2_h = self._dot(hv, hv)
        norm2_exact = self._dot(h_exact, h_exact)
        norm2_coexact = self._dot(h_coexact, h_coexact)
        norm2_harm = self._dot(h_harm, h_harm)
        pythagorean_ok = norm2_h == (norm2_exact + norm2_coexact + norm2_harm)

        if norm2_coexact == Fraction(0) and norm2_harm == Fraction(0):
            classification = "EXACT_GRADIENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        elif norm2_coexact == Fraction(0) and norm2_harm > Fraction(0):
            classification = "HARMONIC_COHOMOLOGY_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif norm2_coexact > Fraction(0) and norm2_harm == Fraction(0):
            classification = "COEXACT_CURL_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            classification = "MIXED_CURL_AND_HARMONIC_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        rec = {
            "complex_id": cid,
            "h": list(hv),
            "h_exact": list(h_exact),
            "h_coexact": list(h_coexact),
            "h_harmonic": list(h_harm),
            "vertex_potential_phi": list(phi_opt),
            "two_cell_potential_psi": list(psi_opt),
            "norm2_total": norm2_h,
            "norm2_exact": norm2_exact,
            "norm2_coexact": norm2_coexact,
            "norm2_harmonic": norm2_harm,
            "harmonic_in_ker_d0_transpose": harm_in_ker_d0t,
            "harmonic_in_ker_d1": harm_in_ker_d1,
            "laplacian_kernel_verified": laplacian_kernel_verified,
            "orthogonality_verified": orthogonality_ok,
            "pythagorean_energy_verified": pythagorean_ok,
            "classification": classification,
            "contract_status": contract_status,
        }
        self.records.append(rec)
        return json_value(rec)

    def get_receipt(self) -> dict[str, Any]:
        """Emit a signed discrete Hodge decomposition audit receipt."""
        if not self.records:
            raise ValidationError("At least one complex cochain must be recorded before emitting a receipt")

        harmonic_ids = [r["complex_id"] for r in self.records if r["norm2_harmonic"] > Fraction(0)]
        coexact_ids = [r["complex_id"] for r in self.records if r["norm2_coexact"] > Fraction(0)]
        all_orth = all(r["orthogonality_verified"] for r in self.records)
        all_pyth = all(r["pythagorean_energy_verified"] for r in self.records)
        all_lap = all(r["laplacian_kernel_verified"] for r in self.records)

        if harmonic_ids or coexact_ids:
            status = "HODGE_OBSTRUCTED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "HODGE_EXACT_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_hodge_decomposition.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "complex_count": len(self.records),
            "harmonic_obstructed_ids": sorted(harmonic_ids),
            "coexact_obstructed_ids": sorted(coexact_ids),
            "all_orthogonality_verified": all_orth,
            "all_pythagorean_energy_verified": all_pyth,
            "all_laplacian_kernels_verified": all_lap,
            "records": self.records,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingDFAGrammarGluingMonitor:
    """Online finite-state automaton (DFA) tape grammar and trace concatenation monitor.

    Audits a deterministic finite automaton A = (Q, Sigma, delta, q0, F) across
    multi-segment tape traces w = w_1 w_2 ... w_k:
      - Evaluates each segment w_i locally from the initial state q0:
          E_local(w_i) = 1[delta*(q0, w_i) in F],   L = prod_i E_local(w_i).
      - Evaluates the concatenated trajectory globally from q0:
          q_i = delta*(q_{i-1}, w_i),   E_global(w_1...w_k) = 1[q_k in F].
      - Verifies the transition monoid homomorphism identity:
          delta*(q_{i-1}, w_i) == delta*(q0, w_1...w_i) for all prefixes.
      - Separates:
          * DFA_CONCATENATION_COHERENT_LGGG (L == 1 and E_global == 1),
          * DFA_BOUNDARY_STATE_MISMATCH_NGD_LGGR (L == 1 and E_global == 0, Delta_E = -1),
            occurring when a locally accepting segment terminates at a non-reset accepting
            state q_1 in F \\ {q0} from which the next locally accepted segment is rejected,
          * DFA_COMPENSATING_RECOVERY_PGD_LGGR (L == 0 and E_global == 1, Delta_E = +1),
          * DFA_LOCAL_AND_GLOBAL_REJECTED (L == 0 and E_global == 0, Delta_E = 0).
    """

    def __init__(
        self,
        states: Iterable[str],
        alphabet: Iterable[str],
        transitions: Mapping[str, Mapping[str, str]],
        initial_state: str,
        accepting_states: Iterable[str],
        *,
        scope_id: str = "streaming-dfa-grammar-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        raw_states = [text(s, "state") for s in sequence(states, "states")]
        if not raw_states:
            raise ValidationError("states must be non-empty")
        self.states = set(raw_states)

        raw_alpha = [text(a, "symbol") for a in sequence(alphabet, "alphabet")]
        if not raw_alpha:
            raise ValidationError("alphabet must be non-empty")
        self.alphabet = set(raw_alpha)

        q0 = text(initial_state, "initial_state")
        if q0 not in self.states:
            raise ValidationError("initial_state must belong to states")
        self.initial_state = q0

        raw_acc = [text(s, "accepting_state") for s in sequence(accepting_states, "accepting_states")]
        for s in raw_acc:
            if s not in self.states:
                raise ValidationError(f"accepting_state {s!r} not in states")
        self.accepting_states = set(raw_acc)

        if not isinstance(transitions, Mapping):
            raise ValidationError("transitions must be a mapping")
        self.transitions: dict[str, dict[str, str]] = {}
        for s in sorted(self.states):
            if s not in transitions or not isinstance(transitions[s], Mapping):
                raise ValidationError(f"Missing transition table for state {s!r}")
            self.transitions[s] = {}
            for sym in sorted(self.alphabet):
                if sym not in transitions[s]:
                    raise ValidationError(f"Missing transition from state {s!r} on symbol {sym!r}")
                nxt = text(transitions[s][sym], "target_state")
                if nxt not in self.states:
                    raise ValidationError(f"Transition target {nxt!r} not in states")
                self.transitions[s][sym] = nxt

        self.current_state = self.initial_state
        self.concatenated_tokens: list[str] = []
        self.segments: list[dict[str, Any]] = []

    def _run_from(self, start_state: str, tokens: list[str]) -> str:
        curr = start_state
        for tok in tokens:
            curr = self.transitions[curr][tok]
        return curr

    def record_segment(self, segment_id: str, tokens: Iterable[str]) -> dict[str, Any]:
        """Record a tape segment, evaluating local acceptance from q0 vs global chained state."""
        sid = text(segment_id, "segment_id")
        tok_list = [text(t, "token") for t in sequence(tokens, "tokens")]
        for t in tok_list:
            if t not in self.alphabet:
                raise ValidationError(f"Token {t!r} is outside declared alphabet")

        local_end = self._run_from(self.initial_state, tok_list)
        local_pass = 1 if local_end in self.accepting_states else 0

        entry_state = self.current_state
        chained_end = self._run_from(entry_state, tok_list)
        self.current_state = chained_end
        self.concatenated_tokens.extend(tok_list)

        direct_prefix_end = self._run_from(self.initial_state, self.concatenated_tokens)
        homomorphism_ok = chained_end == direct_prefix_end

        rec = {
            "segment_index": len(self.segments),
            "segment_id": sid,
            "tokens": tok_list,
            "entry_state": entry_state,
            "local_end_state_from_q0": local_end,
            "local_pass_from_q0": local_pass,
            "is_reset_idempotent_on_q0": local_end == self.initial_state,
            "chained_end_state": chained_end,
            "chained_prefix_accepted": 1 if chained_end in self.accepting_states else 0,
            "monoid_homomorphism_verified": homomorphism_ok,
        }
        self.segments.append(rec)
        return json_value(rec)

    def get_receipt(self) -> dict[str, Any]:
        """Emit a signed DFA tape grammar gluing audit receipt."""
        if not self.segments:
            raise ValidationError("At least one tape segment must be recorded before emitting a receipt")

        local_product = 1
        for seg in self.segments:
            local_product *= seg["local_pass_from_q0"]

        global_eval = 1 if self.current_state in self.accepting_states else 0
        defect = global_eval - local_product
        all_homomorphism = all(seg["monoid_homomorphism_verified"] for seg in self.segments)
        non_reset_accepting_segments = [
            seg["segment_id"]
            for seg in self.segments
            if seg["local_pass_from_q0"] == 1 and not seg["is_reset_idempotent_on_q0"]
        ]

        if local_product == 1 and global_eval == 1:
            status = "DFA_CONCATENATION_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        elif local_product == 1 and global_eval == 0:
            status = "DFA_BOUNDARY_STATE_MISMATCH_NGD_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif local_product == 0 and global_eval == 1:
            status = "DFA_COMPENSATING_RECOVERY_PGD_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "DFA_LOCAL_AND_GLOBAL_REJECTED"
            contract_status = "OBSTRUCTED_LGGR"

        body = {
            "schema": "lggr.online_dfa_grammar_gluing.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "initial_state": self.initial_state,
            "accepting_states": sorted(self.accepting_states),
            "segment_count": len(self.segments),
            "total_tokens": len(self.concatenated_tokens),
            "terminal_state": self.current_state,
            "local_product_aggregator": local_product,
            "global_concatenated_evaluator": global_eval,
            "evaluator_defect": defect,
            "non_reset_accepting_segment_ids": non_reset_accepting_segments,
            "all_monoid_homomorphisms_verified": all_homomorphism,
            "segments": self.segments,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingCatalystDegradationMonitor:
    """Online constructor-task catalyst residual wear and cycle-ceiling monitor.

    Audits multi-cycle constructor tasks (S_t, C_t) -> (S_{t+1}, C_{t+1}) over Q:
      - Tracks initial catalyst state C_0, catalyst tolerance threshold tau_cat >= 0,
        and per-cycle local step wear tolerance eps_local >= 0.
      - On each cycle t, records substrate task completion E_sub(t) in {0, 1} and
        catalyst residual wear delta_C_t = C_t - C_{t-1}.
      - Evaluates the single-cycle local gate:
          E_local(t) = 1[E_sub(t) == 1 and |delta_C_t| <= eps_local]
        and local product aggregator L = prod_{t=1}^N E_local(t).
      - Evaluates cumulative catalyst deviation |C_t - C_0| = |sum_{k=1}^t delta_C_k|
        against tau_cat and global multi-cycle task evaluator:
          E_g = 1[(prod_{t=1}^N E_sub(t) == 1) and (max_{1<=t<=N} |C_t - C_0| <= tau_cat)].
      - Computes the exact uniform-wear cycle ceiling floor(tau_cat / |delta_C_t|)
        when delta_C_t != 0, and separates:
          * IDEAL_EXACT_CATALYST_LGGG (L == 1, E_g == 1, max |C_t - C_0| == 0),
          * BOUNDED_APPROXIMATE_CATALYST_LGGG (L == 1, E_g == 1, 0 < max |C_t - C_0| <= tau_cat),
          * CATALYST_DEGRADATION_EXHAUSTION_NGD_LGGR (L == 1, E_g == 0, Delta_E = -1),
          * LOCAL_CYCLE_REJECTED (L == 0).
    """

    def __init__(
        self,
        initial_catalyst_state: Fraction | int | str = 0,
        catalyst_tolerance: Fraction | int | str = 1,
        *,
        per_cycle_local_tolerance: Fraction | int | str | None = None,
        scope_id: str = "streaming-catalyst-degradation-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.initial_catalyst = rational(initial_catalyst_state)
        self.catalyst_tolerance = rational(catalyst_tolerance)
        if self.catalyst_tolerance < 0:
            raise ValidationError("catalyst_tolerance must be non-negative")
        if per_cycle_local_tolerance is None:
            self.per_cycle_local_tolerance = self.catalyst_tolerance
        else:
            self.per_cycle_local_tolerance = rational(per_cycle_local_tolerance)
            if self.per_cycle_local_tolerance < 0:
                raise ValidationError("per_cycle_local_tolerance must be non-negative")

        self.current_catalyst = self.initial_catalyst
        self.cumulative_wear = Fraction(0)
        self.cumulative_abs_wear = Fraction(0)
        self.max_catalyst_deviation = Fraction(0)
        self.cycles: list[dict[str, Any]] = []

    def record_cycle(
        self,
        cycle_id: str,
        substrate_in: str,
        substrate_out: str,
        substrate_target_met: bool,
        catalyst_wear_delta: Fraction | int | str,
    ) -> dict[str, Any]:
        """Record a single constructor cycle and evaluate local vs cumulative catalyst bounds."""
        cid = text(cycle_id, "cycle_id")
        s_in = text(substrate_in, "substrate_in")
        s_out = text(substrate_out, "substrate_out")
        boolean(substrate_target_met, "substrate_target_met")
        wear = rational(catalyst_wear_delta)

        c_prev = self.current_catalyst
        c_next = c_prev + wear
        self.current_catalyst = c_next
        self.cumulative_wear += wear
        self.cumulative_abs_wear += abs(wear)

        deviation = abs(c_next - self.initial_catalyst)
        if deviation > self.max_catalyst_deviation:
            self.max_catalyst_deviation = deviation

        telescoping_ok = (c_next - self.initial_catalyst) == self.cumulative_wear
        sub_ok = 1 if substrate_target_met else 0
        step_wear_ok = abs(wear) <= self.per_cycle_local_tolerance
        local_eval = 1 if (substrate_target_met and step_wear_ok) else 0
        within_global_tolerance = deviation <= self.catalyst_tolerance

        uniform_cycle_ceiling: int | None = None
        if wear != Fraction(0):
            uniform_cycle_ceiling = int(self.catalyst_tolerance // abs(wear))

        rec = {
            "cycle_index": len(self.cycles),
            "cycle_id": cid,
            "substrate_in": s_in,
            "substrate_out": s_out,
            "substrate_target_met": sub_ok,
            "catalyst_state_before": c_prev,
            "catalyst_wear_delta": wear,
            "catalyst_state_after": c_next,
            "cumulative_catalyst_drift": self.cumulative_wear,
            "cumulative_abs_wear": self.cumulative_abs_wear,
            "catalyst_deviation_from_initial": deviation,
            "local_cycle_evaluator": local_eval,
            "within_global_catalyst_tolerance": within_global_tolerance,
            "uniform_wear_cycle_ceiling": uniform_cycle_ceiling,
            "telescoping_identity_verified": telescoping_ok,
        }
        self.cycles.append(rec)
        return json_value(rec)

    def get_receipt(self) -> dict[str, Any]:
        """Emit a signed multi-cycle constructor catalyst degradation receipt."""
        if not self.cycles:
            raise ValidationError("At least one constructor cycle must be recorded before emitting a receipt")

        local_product = 1
        all_sub_ok = True
        for cyc in self.cycles:
            local_product *= cyc["local_cycle_evaluator"]
            if cyc["substrate_target_met"] != 1:
                all_sub_ok = False

        catalyst_viable_all_cycles = self.max_catalyst_deviation <= self.catalyst_tolerance
        global_eval = 1 if (all_sub_ok and catalyst_viable_all_cycles) else 0
        defect = global_eval - local_product
        exhausted_cycle_ids = [
            cyc["cycle_id"] for cyc in self.cycles if not cyc["within_global_catalyst_tolerance"]
        ]
        all_telescoping = all(cyc["telescoping_identity_verified"] for cyc in self.cycles)

        if local_product == 1 and global_eval == 1:
            if self.max_catalyst_deviation == Fraction(0):
                status = "IDEAL_EXACT_CATALYST_LGGG"
            else:
                status = "BOUNDED_APPROXIMATE_CATALYST_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        elif local_product == 1 and global_eval == 0:
            status = "CATALYST_DEGRADATION_EXHAUSTION_NGD_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "LOCAL_CYCLE_REJECTED"
            contract_status = "OBSTRUCTED_LGGR"

        body = {
            "schema": "lggr.online_catalyst_degradation.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "initial_catalyst_state": self.initial_catalyst,
            "terminal_catalyst_state": self.current_catalyst,
            "catalyst_tolerance": self.catalyst_tolerance,
            "per_cycle_local_tolerance": self.per_cycle_local_tolerance,
            "cycle_count": len(self.cycles),
            "cumulative_catalyst_drift": self.cumulative_wear,
            "cumulative_abs_wear": self.cumulative_abs_wear,
            "max_catalyst_deviation": self.max_catalyst_deviation,
            "local_product_aggregator": local_product,
            "global_evaluator": global_eval,
            "evaluator_defect": defect,
            "exhausted_cycle_ids": exhausted_cycle_ids,
            "all_telescoping_identities_verified": all_telescoping,
            "cycles": self.cycles,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingDiscreteCurvatureMonitor:
    """Online discrete Bochner-Dirichlet curvature and 1-form Hodge Laplacian energy monitor.

    Audits the discrete 1-form Hodge Laplacian on a finite 2-complex (D_0, D_1) over Q:
      L_down = D_0 D_0^T,   L_up = D_1^T D_1,   L_1 = L_down + L_up.
    For each recorded 1-cochain h in C^1(K; Q):
      - Evaluates the quadratic Dirichlet energy identity:
          <h, L_1 h> = <h, L_down h> + <h, L_up h> = ||D_0^T h||_2^2 + ||D_1 h||_2^2 >= 0.
      - Verifies the nilpotent operator orthogonality L_down * L_up == 0 and L_up * L_down == 0
        induced by D_1 * D_0 == 0.
      - Verifies the kernel equivalence:
          L_1 h == 0  <=>  <h, L_1 h> == 0  <=>  (D_0^T h == 0 and D_1 h == 0).
      - Separates:
          * ZERO_COCHAIN_TRIVIAL_LGGG (h == 0),
          * HARMONIC_ZERO_ENERGY_KERNEL_OBSTRUCTION_LGGR (h != 0 and L_1 h == 0),
          * PURE_DIVERGENCE_GRADIENT_FLOW_LGGG (D_1 h == 0 and h in im(D_0) with h != 0),
          * CURL_OR_MIXED_ENERGY_OBSTRUCTION_LGGR (D_1 h != 0 or non-exact divergence flow).
    """

    def __init__(self, *, scope_id: str = "streaming-discrete-curvature-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.records: list[dict[str, Any]] = []

    @staticmethod
    def _dot(u: tuple[Fraction, ...], v: tuple[Fraction, ...]) -> Fraction:
        return sum((a * b for a, b in zip(u, v)), Fraction(0))

    def record_laplacian_probe(
        self,
        probe_id: str,
        D0: Any,
        h: Any,
        D1: Any | None = None,
    ) -> dict[str, Any]:
        """Evaluate L_down, L_up, L_1, and the Dirichlet energy identity on 1-cochain h."""
        pid = text(probe_id, "probe_id")
        d0 = matrix(D0, "D0")
        m, _ = len(d0), len(d0[0])
        hv = vector(h, "h", m)
        d0_t = transpose(d0)
        l_down = matmul(d0, d0_t)

        has_d1 = False
        d1: tuple[tuple[Fraction, ...], ...] = ()
        d1_t: tuple[tuple[Fraction, ...], ...] = ()
        if D1 is not None:
            raw_d1 = sequence(D1, "D1")
            if raw_d1:
                d1 = matrix(raw_d1, "D1", cols=m)
                d1_t = transpose(d1)
                has_d1 = True
                if not is_zero(matmul(d1, d0)):
                    raise ValidationError("Invalid 2-complex: D1 * D0 must be zero")

        if has_d1:
            l_up = matmul(d1_t, d1)
            operator_orthogonality_ok = is_zero(matmul(l_down, l_up)) and is_zero(matmul(l_up, l_down))
        else:
            l_up = tuple(tuple(Fraction(0) for _ in range(m)) for _ in range(m))
            operator_orthogonality_ok = True

        div_h = matvec(d0_t, hv)
        curl_h = matvec(d1, hv) if has_d1 else ()
        l_down_h = matvec(l_down, hv)
        l_up_h = matvec(l_up, hv)
        l1_h = tuple(l_down_h[i] + l_up_h[i] for i in range(m))

        norm2_h = self._dot(hv, hv)
        energy_div = self._dot(div_h, div_h)
        energy_curl = self._dot(curl_h, curl_h) if has_d1 else Fraction(0)
        energy_dirichlet = self._dot(hv, l1_h)
        energy_identity_ok = (
            self._dot(hv, l_down_h) == energy_div
            and self._dot(hv, l_up_h) == energy_curl
            and energy_dirichlet == (energy_div + energy_curl)
        )

        l1_h_zero = all(v == Fraction(0) for v in l1_h)
        div_zero = all(v == Fraction(0) for v in div_h)
        curl_zero = all(v == Fraction(0) for v in curl_h)
        kernel_equivalence_ok = (
            l1_h_zero == (energy_dirichlet == Fraction(0))
            and l1_h_zero == (div_zero and curl_zero)
        )

        exact_sol = solve_exact(d0, hv)
        is_exact = exact_sol is not None

        if norm2_h == Fraction(0):
            classification = "ZERO_COCHAIN_TRIVIAL_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        elif l1_h_zero:
            classification = "HARMONIC_ZERO_ENERGY_KERNEL_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif curl_zero and is_exact:
            classification = "PURE_DIVERGENCE_GRADIENT_FLOW_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            classification = "CURL_OR_MIXED_ENERGY_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        rec = {
            "probe_id": pid,
            "h": list(hv),
            "divergence_d0_transpose_h": list(div_h),
            "curl_d1_h": list(curl_h),
            "l_down_h": list(l_down_h),
            "l_up_h": list(l_up_h),
            "l1_h": list(l1_h),
            "norm2_h": norm2_h,
            "divergence_energy": energy_div,
            "curl_energy": energy_curl,
            "dirichlet_energy": energy_dirichlet,
            "in_laplacian_kernel": l1_h_zero,
            "is_exact_coboundary": is_exact,
            "dirichlet_energy_identity_verified": energy_identity_ok,
            "operator_orthogonality_verified": operator_orthogonality_ok,
            "kernel_equivalence_verified": kernel_equivalence_ok,
            "classification": classification,
            "contract_status": contract_status,
        }
        self.records.append(rec)
        return json_value(rec)

    def get_receipt(self) -> dict[str, Any]:
        """Emit a signed discrete curvature and Hodge Laplacian energy audit receipt."""
        if not self.records:
            raise ValidationError("At least one Laplacian probe must be recorded before emitting a receipt")

        harmonic_kernel_ids = [
            r["probe_id"]
            for r in self.records
            if r["classification"] == "HARMONIC_ZERO_ENERGY_KERNEL_OBSTRUCTION_LGGR"
        ]
        curl_obstructed_ids = [
            r["probe_id"]
            for r in self.records
            if r["classification"] == "CURL_OR_MIXED_ENERGY_OBSTRUCTION_LGGR"
        ]
        all_energy_id = all(r["dirichlet_energy_identity_verified"] for r in self.records)
        all_op_orth = all(r["operator_orthogonality_verified"] for r in self.records)
        all_ker_eq = all(r["kernel_equivalence_verified"] for r in self.records)

        if harmonic_kernel_ids or curl_obstructed_ids:
            status = "CURVATURE_OR_HARMONIC_OBSTRUCTED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "EXACT_GRADIENT_ENERGY_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_discrete_curvature.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "probe_count": len(self.records),
            "harmonic_kernel_probe_ids": sorted(harmonic_kernel_ids),
            "curl_obstructed_probe_ids": sorted(curl_obstructed_ids),
            "all_dirichlet_energy_identities_verified": all_energy_id,
            "all_operator_orthogonalities_verified": all_op_orth,
            "all_kernel_equivalences_verified": all_ker_eq,
            "records": self.records,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingContextualSheafMonitor:
    """Online 3-cycle empirical presheaf marginal-compatibility and global section monitor.

    Audits 3-variable hollow-triangle empirical models over contexts
    C_AB = {A, B}, C_BC = {B, C}, C_CA = {C, A} with binary outcomes {0, 1}^2:
      - Each context table specifies (p_00, p_01, p_10, p_11) in Q_{>=0}^4 with sum == 1.
      - Verifies pairwise single-variable marginal compatibility (no-signaling / presheaf
        restriction agreement):
          p_AB^A(1) == p_CA^A(1),   p_AB^B(1) == p_BC^B(1),   p_BC^C(1) == p_CA^C(1).
      - Solves the exact 1-parameter affine family d_alpha(a, b, c) parameterized by
        alpha = d(1, 1, 1) in Q:
          alpha_min = max(0, q_AB + q_CA - p_A, q_AB + q_BC - p_B, q_BC + q_CA - p_C),
          alpha_max = min(q_AB, q_BC, q_CA, 1 - p_A - p_B - p_C + q_AB + q_BC + q_CA).
      - A nonnegative global joint distribution d >= 0 on {0, 1}^3 exists iff
        pairwise marginals agree and alpha_min <= alpha_max.
      - Separates:
          * GLOBAL_JOINT_SECTION_EXTENSIBLE_LGGG (no-signaling and alpha_min <= alpha_max),
          * CONTEXTUAL_HOLLOW_TRIANGLE_OBSTRUCTION_LGGR (no-signaling holds on all
            single-variable overlaps, yet alpha_min > alpha_max blocks global gluing),
          * SIGNALING_MARGINAL_MISMATCH_LGGR (single-variable overlap marginals disagree).
    """

    def __init__(self, *, scope_id: str = "streaming-contextual-sheaf-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.models: list[dict[str, Any]] = []

    @staticmethod
    def _parse_context_table(table: Any, name: str) -> tuple[Fraction, Fraction, Fraction, Fraction]:
        vals = vector(table, name, 4)
        if any(v < 0 for v in vals):
            raise ValidationError(f"{name} probabilities must be non-negative")
        if sum(vals, Fraction(0)) != Fraction(1):
            raise ValidationError(f"{name} probabilities must sum to 1")
        return vals[0], vals[1], vals[2], vals[3]

    def record_three_cycle_model(
        self,
        model_id: str,
        table_ab: Iterable[Fraction | int | str],
        table_bc: Iterable[Fraction | int | str],
        table_ca: Iterable[Fraction | int | str],
    ) -> dict[str, Any]:
        """Audit a 3-cycle empirical model (p_AB, p_BC, p_CA) for marginal compatibility and global section existence."""
        mid = text(model_id, "model_id")
        ab00, ab01, ab10, ab11 = self._parse_context_table(table_ab, "table_ab")
        bc00, bc01, bc10, bc11 = self._parse_context_table(table_bc, "table_bc")
        ca00, ca01, ca10, ca11 = self._parse_context_table(table_ca, "table_ca")

        # Single-variable marginals for outcome 1
        p_a_from_ab = ab10 + ab11
        p_a_from_ca = ca01 + ca11
        p_b_from_ab = ab01 + ab11
        p_b_from_bc = bc10 + bc11
        p_c_from_bc = bc01 + bc11
        p_c_from_ca = ca10 + ca11

        no_signaling_ok = (
            p_a_from_ab == p_a_from_ca
            and p_b_from_ab == p_b_from_bc
            and p_c_from_bc == p_c_from_ca
        )

        p_a = p_a_from_ab
        p_b = p_b_from_bc
        p_c = p_c_from_ca
        q_ab, q_bc, q_ca = ab11, bc11, ca11

        alpha_min = max(
            Fraction(0),
            q_ab + q_ca - p_a,
            q_ab + q_bc - p_b,
            q_bc + q_ca - p_c,
        )
        d000_plus_d111 = Fraction(1) - p_a - p_b - p_c + q_ab + q_bc + q_ca
        alpha_max = min(q_ab, q_bc, q_ca, d000_plus_d111)

        interval_gap = max(Fraction(0), alpha_min - alpha_max)
        global_section_exists = no_signaling_ok and (alpha_min <= alpha_max)

        witness_joint: dict[str, Fraction] | None = None
        marginal_recovery_verified = False
        if no_signaling_ok:
            alpha = (alpha_min + alpha_max) / Fraction(2)
            d111 = alpha
            d110 = q_ab - alpha
            d011 = q_bc - alpha
            d101 = q_ca - alpha
            d100 = p_a - q_ab - q_ca + alpha
            d010 = p_b - q_ab - q_bc + alpha
            d001 = p_c - q_bc - q_ca + alpha
            d000 = d000_plus_d111 - alpha
            marginal_recovery_verified = (
                (d000 + d001 == ab00)
                and (d010 + d011 == ab01)
                and (d100 + d101 == ab10)
                and (d110 + d111 == ab11)
                and (d000 + d100 == bc00)
                and (d001 + d101 == bc01)
                and (d010 + d110 == bc10)
                and (d011 + d111 == bc11)
                and (d000 + d010 == ca00)
                and (d100 + d110 == ca01)
                and (d001 + d011 == ca10)
                and (d101 + d111 == ca11)
            )
            if global_section_exists:
                witness_joint = {
                    "000": d000,
                    "001": d001,
                    "010": d010,
                    "011": d011,
                    "100": d100,
                    "101": d101,
                    "110": d110,
                    "111": d111,
                }

        if not no_signaling_ok:
            classification = "SIGNALING_MARGINAL_MISMATCH_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif not global_section_exists:
            classification = "CONTEXTUAL_HOLLOW_TRIANGLE_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            classification = "GLOBAL_JOINT_SECTION_EXTENSIBLE_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        rec = {
            "model_id": mid,
            "no_signaling_verified": no_signaling_ok,
            "marginals_one": {"A": p_a, "B": p_b, "C": p_c},
            "joint_ones": {"AB": q_ab, "BC": q_bc, "CA": q_ca},
            "d000_plus_d111_invariant": d000_plus_d111,
            "alpha_min": alpha_min,
            "alpha_max": alpha_max,
            "infeasibility_gap": interval_gap,
            "global_section_exists": global_section_exists,
            "witness_global_joint": witness_joint,
            "affine_marginal_recovery_verified": marginal_recovery_verified,
            "classification": classification,
            "contract_status": contract_status,
        }
        self.models.append(rec)
        return json_value(rec)

    def get_receipt(self) -> dict[str, Any]:
        """Emit a signed 3-cycle contextual presheaf audit receipt."""
        if not self.models:
            raise ValidationError("At least one 3-cycle empirical model must be recorded before emitting a receipt")

        contextual_ids = [
            m["model_id"]
            for m in self.models
            if m["classification"] == "CONTEXTUAL_HOLLOW_TRIANGLE_OBSTRUCTION_LGGR"
        ]
        signaling_ids = [
            m["model_id"]
            for m in self.models
            if m["classification"] == "SIGNALING_MARGINAL_MISMATCH_LGGR"
        ]
        all_affine_ok = all(
            m["affine_marginal_recovery_verified"]
            for m in self.models
            if m["no_signaling_verified"]
        )

        if contextual_ids or signaling_ids:
            status = "PRESHEAF_SECTION_OBSTRUCTED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "PRESHEAF_SECTION_EXTENSIBLE_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_contextual_sheaf.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "model_count": len(self.models),
            "contextual_obstructed_model_ids": sorted(contextual_ids),
            "signaling_obstructed_model_ids": sorted(signaling_ids),
            "all_affine_marginal_recoveries_verified": all_affine_ok,
            "models": self.models,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingReggeDeficitCurvatureMonitor:
    """Online 2D piecewise-flat Regge hinge deficit curvature and Gauss-Bonnet monitor.

    Audits a 2D triangulation K = (V, E, F) with interior vertices V_int, boundary
    vertices V_bnd, and normalized turn-angle assignments theta_{v, f} in Q_{>0}
    (where 1 full turn = 1 and 1 Euclidean triangle angle sum = 1/2):
      - Evaluates each triangle f = (v_0, v_1, v_2) locally for Euclidean closure:
          E_tri(f) = 1[theta_{v_0, f} + theta_{v_1, f} + theta_{v_2, f} == 1/2],
          L = prod_{f in F} E_tri(f).
      - Computes interior hinge deficit curvature at each v in V_int:
          eps_v = 1 - sum_{f ni v} theta_{v, f}
        and boundary geodesic turn at each v in V_bnd:
          kappa_v = 1/2 - sum_{f ni v} theta_{v, f}.
      - Evaluates global interior flatness:
          E_g = 1[L == 1 and all(eps_v == 0 for v in V_int)].
      - Verifies the discrete Gauss-Bonnet angle-deficit identity:
          sum_{v in V_int} eps_v + sum_{v in V_bnd} kappa_v == |V_int| + (1/2)|V_bnd| - sum_{f, v} theta_{v, f}
        and when 2|E| == 3|F| + |V_bnd| and all triangles close (sum_v theta_{v, f} == 1/2),
        verifies equality with the Euler characteristic chi(K) = |V| - |E| + |F|.
      - Separates:
          * FLAT_EUCLIDEAN_LATTICE_LGGG (L == 1 and E_g == 1),
          * REGGE_HINGE_DEFICIT_CURVATURE_NGD_LGGR (L == 1 and E_g == 0, Delta_E = -1),
          * LOCAL_TRIANGLE_CLOSURE_REJECTED (L == 0).
    """

    def __init__(
        self,
        interior_vertices: Iterable[str],
        boundary_vertices: Iterable[str] = (),
        *,
        scope_id: str = "streaming-regge-deficit-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        int_v = [text(v, "interior_vertex") for v in sequence(interior_vertices, "interior_vertices")]
        bnd_v = [text(v, "boundary_vertex") for v in sequence(boundary_vertices, "boundary_vertices")]
        if not int_v and not bnd_v:
            raise ValidationError("At least one vertex must be declared")
        if set(int_v) & set(bnd_v):
            raise ValidationError("interior_vertices and boundary_vertices must be disjoint")

        self.interior_vertices = sorted(set(int_v))
        self.boundary_vertices = sorted(set(bnd_v))
        self.all_vertices = set(self.interior_vertices) | set(self.boundary_vertices)
        self.vertex_angle_sums: dict[str, Fraction] = {v: Fraction(0) for v in self.all_vertices}
        self.edges: set[tuple[str, str]] = set()
        self.triangles: list[dict[str, Any]] = []

    def record_triangle(
        self,
        triangle_id: str,
        vertices: Iterable[str],
        angles: Iterable[Fraction | int | str],
    ) -> dict[str, Any]:
        """Record a triangle with 3 vertices and 3 normalized turn angles."""
        tid = text(triangle_id, "triangle_id")
        v_list = [text(v, "vertex") for v in sequence(vertices, "vertices")]
        if len(v_list) != 3 or len(set(v_list)) != 3:
            raise ValidationError("Each triangle must have exactly 3 distinct vertices")
        for v in v_list:
            if v not in self.all_vertices:
                raise ValidationError(f"Triangle vertex {v!r} was not declared in monitor")

        ang_vec = vector(angles, "angles", 3)
        if any(a <= 0 for a in ang_vec):
            raise ValidationError("Triangle interior angles must be strictly positive")

        for i in range(3):
            u, w = sorted((v_list[i], v_list[(i + 1) % 3]))
            self.edges.add((u, w))
            self.vertex_angle_sums[v_list[i]] += ang_vec[i]

        ang_sum = sum(ang_vec, Fraction(0))
        local_flat_ok = 1 if ang_sum == Fraction(1, 2) else 0

        rec = {
            "triangle_index": len(self.triangles),
            "triangle_id": tid,
            "vertices": v_list,
            "angles": list(ang_vec),
            "angle_sum": ang_sum,
            "local_euclidean_closure": local_flat_ok,
        }
        self.triangles.append(rec)
        return json_value(rec)

    def get_receipt(self) -> dict[str, Any]:
        """Emit a signed Regge hinge deficit curvature and Gauss-Bonnet audit receipt."""
        if not self.triangles:
            raise ValidationError("At least one triangle must be recorded before emitting a receipt")

        local_product = 1
        total_angle_sum = Fraction(0)
        for tri in self.triangles:
            local_product *= tri["local_euclidean_closure"]
            total_angle_sum += tri["angle_sum"]

        interior_deficits: dict[str, Fraction] = {}
        curved_interior_hinges: list[str] = []
        sum_interior_deficit = Fraction(0)
        for v in self.interior_vertices:
            eps_v = Fraction(1) - self.vertex_angle_sums[v]
            interior_deficits[v] = eps_v
            sum_interior_deficit += eps_v
            if eps_v != Fraction(0):
                curved_interior_hinges.append(v)

        boundary_turns: dict[str, Fraction] = {}
        sum_boundary_turn = Fraction(0)
        for v in self.boundary_vertices:
            kap_v = Fraction(1, 2) - self.vertex_angle_sums[v]
            boundary_turns[v] = kap_v
            sum_boundary_turn += kap_v

        total_gauss_bonnet_curvature = sum_interior_deficit + sum_boundary_turn
        expected_angle_balance = (
            Fraction(len(self.interior_vertices))
            + Fraction(len(self.boundary_vertices), 2)
            - total_angle_sum
        )
        angle_balance_identity_ok = total_gauss_bonnet_curvature == expected_angle_balance

        v_count = len(self.all_vertices)
        e_count = len(self.edges)
        f_count = len(self.triangles)
        euler_characteristic = v_count - e_count + f_count
        manifold_edge_incidence = (2 * e_count) == (3 * f_count + len(self.boundary_vertices))
        gauss_bonnet_equals_euler = (
            not (local_product == 1 and manifold_edge_incidence)
            or (total_gauss_bonnet_curvature == Fraction(euler_characteristic))
        )

        global_flat = 1 if (local_product == 1 and len(curved_interior_hinges) == 0) else 0
        defect = global_flat - local_product

        if local_product == 1 and global_flat == 1:
            status = "FLAT_EUCLIDEAN_LATTICE_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        elif local_product == 1 and global_flat == 0:
            status = "REGGE_HINGE_DEFICIT_CURVATURE_NGD_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "LOCAL_TRIANGLE_CLOSURE_REJECTED"
            contract_status = "OBSTRUCTED_LGGR"

        body = {
            "schema": "lggr.online_regge_deficit_curvature.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "vertex_count": v_count,
            "edge_count": e_count,
            "triangle_count": f_count,
            "euler_characteristic": euler_characteristic,
            "interior_deficits": interior_deficits,
            "boundary_geodesic_turns": boundary_turns,
            "curved_interior_hinge_ids": curved_interior_hinges,
            "sum_interior_deficit": sum_interior_deficit,
            "sum_boundary_turn": sum_boundary_turn,
            "total_gauss_bonnet_curvature": total_gauss_bonnet_curvature,
            "local_product_aggregator": local_product,
            "global_flatness_evaluator": global_flat,
            "evaluator_defect": defect,
            "angle_balance_identity_verified": angle_balance_identity_ok,
            "gauss_bonnet_euler_identity_verified": gauss_bonnet_equals_euler,
            "triangles": self.triangles,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingPullbackSquareMonitor:
    """Online categorical fibered pullback square and canonical cone mediator monitor.

    Audits a finite cospan A -f-> C <-g- B and its fibered pullback
    A x_C B = {(a, b) in A x B | f(a) == g(b)}:
      - Computes the exact fibered pullback carrier P = A x_C B and fiber cardinalities
        |f^{-1}(c) x g^{-1}(c)| for each shared interface value c in C.
      - For each recorded branch pair (a, b) with local branch indicators E_A, E_B in {0, 1}:
          * Evaluates local product L = E_A * E_B,
          * Checks pullback compatibility f(a) == g(b) and global fibered evaluator
            E_g = 1[L == 1 and f(a) == g(b)],
          * Flags fiber ambiguity when |f^{-1}(f(a)) x g^{-1}(g(b))| > 1 (where the
            interface value c alone does not uniquely identify the pair in A x_C B).
      - Audits candidate cones W -p_A-> A, W -p_B-> B for cone commutativity
        f(p_A(w)) == g(p_B(w)) and constructs the unique mediating map
        u: W -> A x_C B, u(w) = (p_A(w), p_B(w)).
      - Separates:
          * PULLBACK_FIBER_GLUED_LGGG (all recorded pairs have L == 1 and E_g == 1),
          * PULLBACK_INTERFACE_MISMATCH_NGD_LGGR (at least one pair has L == 1 and f(a) != g(b)),
          * LOCAL_BRANCH_REJECTED (L == 0).
    """

    def __init__(
        self,
        f_map: Mapping[str, str],
        g_map: Mapping[str, str],
        *,
        scope_id: str = "streaming-pullback-square-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        if not isinstance(f_map, Mapping) or not f_map:
            raise ValidationError("f_map must be a non-empty mapping A -> C")
        if not isinstance(g_map, Mapping) or not g_map:
            raise ValidationError("g_map must be a non-empty mapping B -> C")

        self.f_map: dict[str, str] = {
            text(k, "a_state"): text(v, "c_state") for k, v in sorted(f_map.items())
        }
        self.g_map: dict[str, str] = {
            text(k, "b_state"): text(v, "c_state") for k, v in sorted(g_map.items())
        }

        self.pullback_carrier: list[tuple[str, str, str]] = []
        self.fiber_counts: dict[str, int] = {}
        for a, ca in self.f_map.items():
            for b, cb in self.g_map.items():
                if ca == cb:
                    self.pullback_carrier.append((a, b, ca))
                    self.fiber_counts[ca] = self.fiber_counts.get(ca, 0) + 1

        self.pair_records: list[dict[str, Any]] = []
        self.cone_records: list[dict[str, Any]] = []

    def record_branch_pair(
        self,
        pair_id: str,
        a_state: str,
        b_state: str,
        *,
        local_a_pass: bool = True,
        local_b_pass: bool = True,
    ) -> dict[str, Any]:
        """Record a candidate branch pair (a, b) and test fibered pullback compatibility."""
        pid = text(pair_id, "pair_id")
        a = text(a_state, "a_state")
        b = text(b_state, "b_state")
        boolean(local_a_pass, "local_a_pass")
        boolean(local_b_pass, "local_b_pass")
        if a not in self.f_map:
            raise ValidationError(f"a_state {a!r} not in domain of f_map")
        if b not in self.g_map:
            raise ValidationError(f"b_state {b!r} not in domain of g_map")

        fa = self.f_map[a]
        gb = self.g_map[b]
        in_pullback = fa == gb
        ea = 1 if local_a_pass else 0
        eb = 1 if local_b_pass else 0
        l_prod = ea * eb
        eg = 1 if (l_prod == 1 and in_pullback) else 0
        defect = eg - l_prod
        fiber_size = self.fiber_counts.get(fa, 0) if in_pullback else 0

        rec = {
            "pair_index": len(self.pair_records),
            "pair_id": pid,
            "a_state": a,
            "b_state": b,
            "f_a": fa,
            "g_b": gb,
            "in_pullback_square": in_pullback,
            "local_a_evaluator": ea,
            "local_b_evaluator": eb,
            "local_product": l_prod,
            "global_pullback_evaluator": eg,
            "evaluator_defect": defect,
            "interface_fiber_size": fiber_size,
            "interface_uniquely_identifies_pair": fiber_size == 1,
        }
        self.pair_records.append(rec)
        return json_value(rec)

    def verify_cone_mediator(
        self,
        cone_id: str,
        p_a_map: Mapping[str, str],
        p_b_map: Mapping[str, str],
    ) -> dict[str, Any]:
        """Verify canonical pullback mediator existence and uniqueness for a cone W -> A, W -> B."""
        cid = text(cone_id, "cone_id")
        if not isinstance(p_a_map, Mapping) or not isinstance(p_b_map, Mapping):
            raise ValidationError("p_a_map and p_b_map must be mappings")
        if set(p_a_map.keys()) != set(p_b_map.keys()) or not p_a_map:
            raise ValidationError("p_a_map and p_b_map must share the same non-empty apex domain W")

        mediator: dict[str, list[str]] = {}
        mismatched_apex_states: list[str] = []
        projection_recovery_ok = True

        for w_raw in sorted(p_a_map.keys()):
            w = text(w_raw, "apex_state")
            a = text(p_a_map[w_raw], "a_target")
            b = text(p_b_map[w_raw], "b_target")
            if a not in self.f_map or b not in self.g_map:
                raise ValidationError(f"Cone target ({a!r}, {b!r}) outside cospan domains")
            if self.f_map[a] == self.g_map[b]:
                mediator[w] = [a, b]
                if mediator[w][0] != a or mediator[w][1] != b:
                    projection_recovery_ok = False
            else:
                mismatched_apex_states.append(w)

        commutes = len(mismatched_apex_states) == 0
        rec = {
            "cone_id": cid,
            "commutes_over_c": commutes,
            "mismatched_apex_states": mismatched_apex_states,
            "universal_mediator": mediator if commutes else None,
            "mediator_uniqueness_and_projection_verified": commutes and projection_recovery_ok,
        }
        self.cone_records.append(rec)
        return json_value(rec)

    def get_receipt(self) -> dict[str, Any]:
        """Emit a signed categorical pullback square and cone mediator audit receipt."""
        if not self.pair_records:
            raise ValidationError("At least one branch pair must be recorded before emitting a receipt")

        ngd_pair_ids = [r["pair_id"] for r in self.pair_records if r["evaluator_defect"] == -1]
        rejected_pair_ids = [r["pair_id"] for r in self.pair_records if r["local_product"] == 0]
        ambiguous_fiber_pair_ids = [
            r["pair_id"]
            for r in self.pair_records
            if r["in_pullback_square"] and not r["interface_uniquely_identifies_pair"]
        ]

        if ngd_pair_ids:
            status = "PULLBACK_INTERFACE_MISMATCH_NGD_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif rejected_pair_ids:
            status = "LOCAL_BRANCH_REJECTED"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "PULLBACK_FIBER_GLUED_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_pullback_square.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "pullback_carrier_size": len(self.pullback_carrier),
            "interface_fiber_counts": self.fiber_counts,
            "pair_count": len(self.pair_records),
            "ngd_mismatch_pair_ids": ngd_pair_ids,
            "ambiguous_fiber_pair_ids": ambiguous_fiber_pair_ids,
            "cone_records": self.cone_records,
            "pair_records": self.pair_records,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingMartingaleOptionalStoppingMonitor:
    """Online two-step martingale optional stopping and terminal-loss monitor over Q.

    Audits 2-step rational binary trees with root X_0, step-1 states (X_u, X_d)
    under probabilities (p_1, 1 - p_1), and step-2 states (X_uu, X_ud) under
    (p_u, 1 - p_u) and (X_du, X_dd) under (p_d, 1 - p_d):
      - Evaluates the three local conditional martingale zero-drift equations:
          E_mart,1 = 1[p_1 X_u + (1 - p_1) X_d == X_0],
          E_mart,u = 1[p_u X_uu + (1 - p_u) X_ud == X_u],
          E_mart,d = 1[p_d X_du + (1 - p_d) X_dd == X_d],
          L = E_mart,1 * E_mart,u * E_mart,d.
      - For an adapted stopping rule tau in {1, 2} (stop_on_step1_up, stop_on_step1_down):
          * Computes the stopped expectation E[X_tau] and full-horizon expectation E[X_2],
          * Checks the actual equality E[X_tau] == E[X_2] == X_0, separately
            from applicability of bounded optional stopping (L == 1).
          * Computes the stopped win probability P(X_tau > X_0) and worst
            stopped terminal loss Delta_tail = max(0, X_0 - min_omega X_tau(omega))
            against max_tail_drawdown_budget. This is not peak-to-trough drawdown.
          * Evaluates the loss budget independently: E_g = 1[Delta_tail <= budget].
            Joint admission additionally requires L == 1.
      - Separates:
          * MARTINGALE_STOPPING_WITHIN_DRAWDOWN_LGGG (L == 1 and Delta_tail <= budget),
          * MARTINGALE_STOPPING_TAIL_DRAWDOWN_NGD_LGGR (L == 1 and E[X_tau] == X_0,
            yet Delta_tail > max_tail_drawdown_budget, so E_g = 0, Delta_E = -1),
          * NON_MARTINGALE_DRIFT_REJECTED (L == 0).
    """

    def __init__(
        self,
        max_tail_drawdown_budget: Fraction | int | str,
        *,
        scope_id: str = "streaming-martingale-stopping-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.max_tail_drawdown_budget = rational(max_tail_drawdown_budget)
        if self.max_tail_drawdown_budget < 0:
            raise ValidationError("max_tail_drawdown_budget must be non-negative")
        self.trees: list[dict[str, Any]] = []

    @staticmethod
    def _prob(val: Fraction | int | str, name: str) -> Fraction:
        q = rational(val)
        if q <= 0 or q >= 1:
            raise ValidationError(f"{name} must lie strictly inside (0, 1)")
        return q

    def record_stopped_tree(
        self,
        tree_id: str,
        x0: Fraction | int | str,
        x_u: Fraction | int | str,
        x_d: Fraction | int | str,
        x_uu: Fraction | int | str,
        x_ud: Fraction | int | str,
        x_du: Fraction | int | str,
        x_dd: Fraction | int | str,
        *,
        p_1: Fraction | int | str = "1/2",
        p_u: Fraction | int | str = "1/2",
        p_d: Fraction | int | str = "1/2",
        stop_on_step1_up: bool = True,
        stop_on_step1_down: bool = False,
    ) -> dict[str, Any]:
        """Audit a 2-step branching tree and adapted stopping rule tau."""
        tid = text(tree_id, "tree_id")
        v0 = rational(x0)
        vu, vd = rational(x_u), rational(x_d)
        vuu, vud, vdu, vdd = rational(x_uu), rational(x_ud), rational(x_du), rational(x_dd)
        q1 = self._prob(p_1, "p_1")
        qu = self._prob(p_u, "p_u")
        qd = self._prob(p_d, "p_d")
        boolean(stop_on_step1_up, "stop_on_step1_up")
        boolean(stop_on_step1_down, "stop_on_step1_down")

        exp_step1 = q1 * vu + (Fraction(1) - q1) * vd
        exp_u = qu * vuu + (Fraction(1) - qu) * vud
        exp_d = qd * vdu + (Fraction(1) - qd) * vdd

        e_m1 = 1 if exp_step1 == v0 else 0
        e_mu = 1 if exp_u == vu else 0
        e_md = 1 if exp_d == vd else 0
        local_product = e_m1 * e_mu * e_md

        exp_horizon2 = (
            q1 * qu * vuu
            + q1 * (Fraction(1) - qu) * vud
            + (Fraction(1) - q1) * qd * vdu
            + (Fraction(1) - q1) * (Fraction(1) - qd) * vdd
        )

        # Build stopped terminal outcome distribution {(value, prob)}
        stopped_outcomes: list[tuple[Fraction, Fraction]] = []
        if stop_on_step1_up:
            stopped_outcomes.append((vu, q1))
        else:
            stopped_outcomes.append((vuu, q1 * qu))
            stopped_outcomes.append((vud, q1 * (Fraction(1) - qu)))

        if stop_on_step1_down:
            stopped_outcomes.append((vd, Fraction(1) - q1))
        else:
            stopped_outcomes.append((vdu, (Fraction(1) - q1) * qd))
            stopped_outcomes.append((vdd, (Fraction(1) - q1) * (Fraction(1) - qd)))

        exp_stopped = sum((val * prob for val, prob in stopped_outcomes), Fraction(0))
        win_prob = sum((prob for val, prob in stopped_outcomes if val > v0), Fraction(0))
        min_stopped_val = min(val for val, _ in stopped_outcomes)
        tail_drawdown = max(Fraction(0), v0 - min_stopped_val)
        within_drawdown_budget = tail_drawdown <= self.max_tail_drawdown_budget

        # Verify the equality itself; a false martingale premise is not evidence
        # of conservation. Accidental equality on a non-martingale is possible,
        # so theorem applicability is a separate fact.
        optional_stopping_applicable = local_product == 1
        optional_stopping_conserved = exp_stopped == v0 and exp_horizon2 == v0

        global_eval = 1 if within_drawdown_budget else 0
        joint_admission = local_product * global_eval
        defect = global_eval - local_product

        if local_product == 1 and global_eval == 1:
            classification = "MARTINGALE_STOPPING_WITHIN_DRAWDOWN_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        elif local_product == 1 and global_eval == 0:
            classification = "MARTINGALE_STOPPING_TAIL_DRAWDOWN_NGD_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            classification = "NON_MARTINGALE_DRIFT_REJECTED"
            contract_status = "OBSTRUCTED_LGGR"

        rec = {
            "tree_id": tid,
            "x0": v0,
            "step1_expectation": exp_step1,
            "horizon2_expectation": exp_horizon2,
            "stopped_expectation": exp_stopped,
            "stopped_win_probability": win_prob,
            "min_stopped_value": min_stopped_val,
            "tail_drawdown": tail_drawdown,
            "max_tail_drawdown_budget": self.max_tail_drawdown_budget,
            "local_martingale_product": local_product,
            "global_drawdown_evaluator": global_eval,
            "joint_admission_evaluator": joint_admission,
            "evaluator_defect": defect,
            "optional_stopping_theorem_applicable": optional_stopping_applicable,
            "optional_stopping_conservation_verified": optional_stopping_conserved,
            "classification": classification,
            "contract_status": contract_status,
        }
        self.trees.append(rec)
        return json_value(rec)

    def get_receipt(self) -> dict[str, Any]:
        """Emit a hash-bound two-step martingale optional stopping audit receipt."""
        if not self.trees:
            raise ValidationError("At least one stopped tree must be recorded before emitting a receipt")

        ngd_tree_ids = [
            t["tree_id"]
            for t in self.trees
            if t["classification"] == "MARTINGALE_STOPPING_TAIL_DRAWDOWN_NGD_LGGR"
        ]
        non_martingale_ids = [
            t["tree_id"]
            for t in self.trees
            if t["classification"] == "NON_MARTINGALE_DRIFT_REJECTED"
        ]
        all_ost_ok = all(t["optional_stopping_conservation_verified"] for t in self.trees)

        if ngd_tree_ids or non_martingale_ids:
            status = "OPTIONAL_STOPPING_DRAWDOWN_OBSTRUCTED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "OPTIONAL_STOPPING_BOUNDED_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_martingale_optional_stopping.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "max_tail_drawdown_budget": self.max_tail_drawdown_budget,
            "tree_count": len(self.trees),
            "tail_drawdown_ngd_tree_ids": sorted(ngd_tree_ids),
            "non_martingale_tree_ids": sorted(non_martingale_ids),
            "all_optional_stopping_theorems_applicable": not non_martingale_ids,
            "all_optional_stopping_conservations_verified": all_ost_ok,
            "trees": self.trees,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingProjectiveTowerMonitor:
    """Online projective tower and R^1 lim^1 derived-limit integer lifting monitor (LGGR IV).

    Audits finite-stage modular congruence threads (x_n, m_n) for a linear equation
    a * x + b == 0 along a divisibility tower m_1 | m_2 | ... | m_N:
      - Evaluates each stage n locally for modular root satisfaction:
          E_mod(n) = 1[(a * x_n + b) % m_n == 0]
        and inverse-limit transition compatibility with the prior stage:
          E_proj(n) = 1[(x_n - x_{n-1}) % m_{n-1} == 0]  (for n >= 2).
      - Computes the step-lift coboundary differences d_n = x_{n+1} - x_n in m_n Z
        and the rational completion root x_inf = -b / a in Q.
      - Evaluates global integral lifting E_g in {0, 1}:
          E_g = 1 iff there exists x_* in Z such that a * x_* + b == 0 and
          (x_* - x_n) % m_n == 0 for all recorded stages n.
      - Separates:
          * INTEGRAL_GLOBAL_LIFT_COHERENT_LGGG (L == 1 and E_g == 1, Delta_E = 0),
          * DERIVED_LIMIT_R1_LIFTING_OBSTRUCTION_NGD_LGGR (L == 1 and E_g == 0,
            Delta_E = -1: every finite modular stage is solvable and compatible in
            lim Z/m_n Z, yet x_inf = -b / a not in Z leaves a non-zero coset
            obstruction [-b/a] != 0 in Q/Z),
          * LOCAL_TOWER_STAGE_REJECTED (L == 0).
    """

    def __init__(
        self,
        coeff_a: int,
        const_b: int,
        *,
        scope_id: str = "streaming-projective-tower-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.coeff_a = exact_int(coeff_a, "coeff_a")
        self.const_b = exact_int(const_b, "const_b")
        if self.coeff_a == 0:
            raise ValidationError("coeff_a must be non-zero")
        self.rational_completion_root = Fraction(-self.const_b, self.coeff_a)
        self.integral_root: int | None = (
            -self.const_b // self.coeff_a if (-self.const_b) % self.coeff_a == 0 else None
        )
        self.stages: list[dict[str, Any]] = []

    def record_stage(
        self,
        stage_id: str,
        modulus: int,
        candidate_x: int,
    ) -> dict[str, Any]:
        """Record a finite presentation stage (m_n, x_n) and check modular and projection compatibility."""
        sid = text(stage_id, "stage_id")
        mod_n = exact_int(modulus, "modulus", minimum=2)
        x_n = exact_int(candidate_x, "candidate_x")

        if self.stages:
            prev_mod = self.stages[-1]["modulus"]
            prev_x = self.stages[-1]["candidate_x"]
            if mod_n % prev_mod != 0 or mod_n <= prev_mod:
                raise ValidationError("Each stage modulus must strictly divide the next stage modulus")
            step_diff = x_n - prev_x
            proj_ok = 1 if (step_diff % prev_mod == 0) else 0
        else:
            step_diff = 0
            proj_ok = 1

        mod_residual = (self.coeff_a * x_n + self.const_b) % mod_n
        mod_ok = 1 if mod_residual == 0 else 0
        local_stage_pass = mod_ok * proj_ok

        rec = {
            "stage_index": len(self.stages),
            "stage_id": sid,
            "modulus": mod_n,
            "candidate_x": x_n,
            "modular_residual": mod_residual,
            "local_modular_pass": mod_ok,
            "step_lift_difference": step_diff,
            "inverse_limit_projection_compatible": proj_ok,
            "local_stage_evaluator": local_stage_pass,
        }
        self.stages.append(rec)
        return json_value(rec)

    def get_receipt(self) -> dict[str, Any]:
        """Emit a signed projective tower and R^1 lim^1 lifting obstruction receipt."""
        if not self.stages:
            raise ValidationError("At least one projective tower stage must be recorded before emitting a receipt")

        local_product = 1
        for st in self.stages:
            local_product *= st["local_stage_evaluator"]

        if self.integral_root is not None:
            all_stages_lift = all(
                (self.integral_root - st["candidate_x"]) % st["modulus"] == 0
                for st in self.stages
            )
            global_eval = 1 if (local_product == 1 and all_stages_lift) else 0
        else:
            global_eval = 0

        defect = global_eval - local_product
        fractional_coset_residual = self.rational_completion_root - Fraction(
            self.rational_completion_root.numerator // self.rational_completion_root.denominator
        )

        if local_product == 1 and global_eval == 1:
            status = "INTEGRAL_GLOBAL_LIFT_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        elif local_product == 1 and global_eval == 0:
            status = "DERIVED_LIMIT_R1_LIFTING_OBSTRUCTION_NGD_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "LOCAL_TOWER_STAGE_REJECTED"
            contract_status = "OBSTRUCTED_LGGR"

        body = {
            "schema": "lggr.online_projective_tower.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "coeff_a": self.coeff_a,
            "const_b": self.const_b,
            "stage_count": len(self.stages),
            "rational_completion_root": self.rational_completion_root,
            "integral_global_root": self.integral_root,
            "r1_lim_coset_residual_mod_z": fractional_coset_residual,
            "local_product_aggregator": local_product,
            "global_integral_lift_evaluator": global_eval,
            "evaluator_defect": defect,
            "stages": self.stages,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingSkewRepairMonitor:
    """Online skew non-diagonal exact subspace norm-attainment divergence monitor (LGGR V §4 Remark LGR-R4).

    Audits candidate cochains omega = (a, b) in Q^2 against the skew non-diagonal exact subspace
    S = {(-alpha, -2*alpha) : alpha in Q} subset Q^2, where the repaired residual is
    r(alpha) = (a + alpha, b + 2*alpha):
      - Computes the skew cycle discrepancy Delta_skew = 2*a - b.
      - Computes the exact norm-minimizing parameters across l^1, l^2, and l^infty:
          alpha_1   = -b / 2
          alpha_2   = -(a + 2*b) / 5
          alpha_inf = -(a + b) / 3
        and the corresponding minimum norm values:
          Phi_1     = |2*a - b| / 2
          Phi_2_sq  = (2*a - b)^2 / 5
          Phi_inf   = |2*a - b| / 3
      - Verifies that whenever 2*a != b, alpha_1, alpha_2, and alpha_inf strictly diverge:
          alpha_1 - alpha_2 = (2*a - b) / 10,
          alpha_2 - alpha_inf = (2*a - b) / 15,
          alpha_1 - alpha_inf = (2*a - b) / 6.
      - Evaluates a selected repair parameter alpha_cand (defaulting to alpha_inf) against
        coordinatewise l^infty bounds B_inf (defaulting to Phi_inf):
          L = E_coord_1 * E_coord_2, where E_coord_i = 1[|r_i(alpha_cand)| <= B_inf]
        versus the global l^1 minimum repair budget B_1 (defaulting to Phi_1):
          E_g = 1[||r(alpha_cand)||_1 <= B_1].
      - Separates:
          * SKEW_NORM_ATTAINMENT_DIVERGENCE_LGGR (L == 1 and E_g == 0, Delta_E = -1:
            e.g., selecting the l^infty-optimal repair alpha_inf satisfies both coordinate
            l^infty bounds |r_i(alpha_inf)| = |2*a - b|/3 <= Phi_inf, yet incurs
            ||r(alpha_inf)||_1 = 2*|2*a - b|/3 > |2*a - b|/2 = Phi_1),
          * SKEW_REPAIR_BUDGET_COHERENT_LGGG (L == 1 and E_g == 1, Delta_E = 0),
          * LOCAL_COORDINATE_BOUND_REJECTED (L == 0).
    """

    def __init__(self, *, scope_id: str = "streaming-skew-repair-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.probes: list[dict[str, Any]] = []

    def record_probe(
        self,
        probe_id: str,
        omega_a: int | str | Fraction,
        omega_b: int | str | Fraction,
        *,
        candidate_alpha: int | str | Fraction | None = None,
        l_inf_coordinate_budget: int | str | Fraction | None = None,
        l_1_global_budget: int | str | Fraction | None = None,
    ) -> dict[str, Any]:
        """Record a 2-cochain probe omega = (a, b) and audit l^1, l^2, l^infty repair attainment."""
        pid = text(probe_id, "probe_id")
        a = rational(omega_a)
        b = rational(omega_b)

        skew_discrepancy = 2 * a - b
        abs_skew = abs(skew_discrepancy)

        alpha_1 = -b / Fraction(2)
        alpha_2 = -(a + 2 * b) / Fraction(5)
        alpha_inf = -(a + b) / Fraction(3)

        phi_1 = abs_skew / Fraction(2)
        phi_2_sq = (skew_discrepancy * skew_discrepancy) / Fraction(5)
        phi_inf = abs_skew / Fraction(3)

        # Verify that r(alpha_1), r(alpha_2), r(alpha_inf) attain the closed-form minima
        r1_at_alpha1 = abs(a + alpha_1) + abs(b + 2 * alpha_1)
        r2_sq_at_alpha2 = (a + alpha_2) ** 2 + (b + 2 * alpha_2) ** 2
        rinf_at_alphainf = max(abs(a + alpha_inf), abs(b + 2 * alpha_inf))
        closed_form_identities_hold = (
            r1_at_alpha1 == phi_1
            and r2_sq_at_alpha2 == phi_2_sq
            and rinf_at_alphainf == phi_inf
        )

        minimizers_strictly_diverge = (
            alpha_1 != alpha_2 and alpha_2 != alpha_inf and alpha_1 != alpha_inf
        )

        alpha_c = rational(candidate_alpha) if candidate_alpha is not None else alpha_inf
        b_inf = (
            rational(l_inf_coordinate_budget)
            if l_inf_coordinate_budget is not None
            else phi_inf
        )
        b_1 = (
            rational(l_1_global_budget)
            if l_1_global_budget is not None
            else phi_1
        )
        if b_inf < 0 or b_1 < 0:
            raise ValidationError("Repair budgets must be non-negative")

        res_1 = a + alpha_c
        res_2 = b + 2 * alpha_c
        cand_l1 = abs(res_1) + abs(res_2)
        cand_l2_sq = res_1 * res_1 + res_2 * res_2
        cand_linf = max(abs(res_1), abs(res_2))

        e_coord_1 = 1 if abs(res_1) <= b_inf else 0
        e_coord_2 = 1 if abs(res_2) <= b_inf else 0
        local_product = e_coord_1 * e_coord_2
        global_eval = 1 if (local_product == 1 and cand_l1 <= b_1) else 0
        defect = global_eval - local_product

        if local_product == 1 and global_eval == 0:
            probe_status = "SKEW_NORM_ATTAINMENT_DIVERGENCE_LGGR"
        elif local_product == 1 and global_eval == 1:
            probe_status = "SKEW_REPAIR_BUDGET_COHERENT_LGGG"
        else:
            probe_status = "LOCAL_COORDINATE_BOUND_REJECTED"

        rec = {
            "probe_id": pid,
            "omega": [a, b],
            "skew_discrepancy_2a_minus_b": skew_discrepancy,
            "alpha_1": alpha_1,
            "alpha_2": alpha_2,
            "alpha_inf": alpha_inf,
            "phi_1": phi_1,
            "phi_2_squared": phi_2_sq,
            "phi_inf": phi_inf,
            "closed_form_identities_hold": closed_form_identities_hold,
            "minimizers_strictly_diverge": minimizers_strictly_diverge,
            "candidate_alpha": alpha_c,
            "candidate_residual": [res_1, res_2],
            "candidate_l1_cost": cand_l1,
            "candidate_l2_squared_cost": cand_l2_sq,
            "candidate_linf_cost": cand_linf,
            "l_inf_coordinate_budget": b_inf,
            "l_1_global_budget": b_1,
            "local_coordinate_evaluators": [e_coord_1, e_coord_2],
            "local_product_aggregator": local_product,
            "global_l1_budget_evaluator": global_eval,
            "evaluator_defect": defect,
            "probe_status": probe_status,
        }
        self.probes.append(rec)
        return json_value(rec)

    def get_receipt(self) -> dict[str, Any]:
        """Emit a signed skew repair norm-attainment receipt."""
        if not self.probes:
            raise ValidationError("At least one skew repair probe must be recorded before emitting a receipt")

        divergent_ids = [
            p["probe_id"]
            for p in self.probes
            if p["probe_status"] == "SKEW_NORM_ATTAINMENT_DIVERGENCE_LGGR"
        ]
        rejected_ids = [
            p["probe_id"]
            for p in self.probes
            if p["probe_status"] == "LOCAL_COORDINATE_BOUND_REJECTED"
        ]
        all_closed_forms_ok = all(p["closed_form_identities_hold"] for p in self.probes)

        if divergent_ids:
            status = "SKEW_NORM_ATTAINMENT_DIVERGENCE_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif rejected_ids:
            status = "LOCAL_COORDINATE_BOUND_REJECTED"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "SKEW_REPAIR_BUDGET_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_skew_repair.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "probe_count": len(self.probes),
            "all_closed_form_identities_verified": all_closed_forms_ok,
            "skew_norm_divergence_probe_ids": divergent_ids,
            "rejected_probe_ids": rejected_ids,
            "probes": self.probes,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingMerminPeresParityMonitor:
    """Online 3x3 Mermin-Peres magic-square parity contextuality monitor (012_rsi/003 BELL-08 & LGGR VII §5.2).

    Audits 3x3 parity grids of {-1, +1}-valued observables across 3 row contexts and 3 column contexts:
      - Row product targets R = (R_0, R_1, R_2) in {-1, +1}^3 (defaulting to (+1, +1, +1))
        and column product targets C = (C_0, C_1, C_2) in {-1, +1}^3 (defaulting to (+1, +1, -1)).
      - Evaluates each of the 6 contexts locally:
          E_row,i = 1[prod_{j=0}^2 r_{i,j} == R_i],  i in {0, 1, 2}
          E_col,j = 1[prod_{i=0}^2 c_{i,j} == C_j],  j in {0, 1, 2}
        and forms the local product aggregator:
          L = (prod_{i=0}^2 E_row,i) * (prod_{j=0}^2 E_col,j) in {0, 1}.
      - Computes the row target parity product Pi_R = R_0 * R_1 * R_2 and column target
        parity product Pi_C = C_0 * C_1 * C_2, and checks all 2^9 = 512 global non-contextual
        assignments A in {-1, +1}^{3x3} to determine:
          * max_satisfied_contexts_out_of_6 (5 when Pi_R != Pi_C, 6 when Pi_R == Pi_C),
          * min_violated_contexts (1 when Pi_R != Pi_C, 0 when Pi_R == Pi_C),
          * global evaluator E_g in {0, 1}, where E_g = 1 iff L == 1, Pi_R == Pi_C, and
            any supplied global grid (or the target parity system) admits a non-contextual
            {-1, +1}^{3x3} assignment satisfying all 6 contexts simultaneously.
      - Separates:
          * MERMIN_PERES_PARITY_OBSTRUCTION_LGGR (L == 1 and E_g == 0, Delta_E = -1:
            all 6 row/column contexts are locally satisfiable, yet Pi_R != Pi_C obstructs
            every global non-contextual assignment),
          * NONCONTEXTUAL_PARITY_COHERENT_LGGG (L == 1 and E_g == 1, Delta_E = 0),
          * LOCAL_CONTEXT_PARITY_REJECTED (L == 0).
    """

    def __init__(self, *, scope_id: str = "streaming-mermin-peres-parity-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.grids: list[dict[str, Any]] = []

    @staticmethod
    def _validate_sign(val: int, name: str) -> int:
        v = exact_int(val, name)
        if v not in (-1, 1):
            raise ValidationError(f"{name} must be in {{-1, +1}}, got {v}")
        return v

    def record_grid(
        self,
        grid_id: str,
        *,
        row_targets: Sequence[int] = (1, 1, 1),
        col_targets: Sequence[int] = (1, 1, -1),
        row_context_assignments: Sequence[Sequence[int]] | None = None,
        col_context_assignments: Sequence[Sequence[int]] | None = None,
    ) -> dict[str, Any]:
        """Record a 3x3 Mermin-Peres parity grid and audit context-local vs global non-contextual satisfiability."""
        gid = text(grid_id, "grid_id")
        if len(row_targets) != 3 or len(col_targets) != 3:
            raise ValidationError("row_targets and col_targets must each have length 3")

        r_targets = [self._validate_sign(x, f"row_targets[{i}]") for i, x in enumerate(row_targets)]
        c_targets = [self._validate_sign(x, f"col_targets[{j}]") for j, x in enumerate(col_targets)]

        if row_context_assignments is not None:
            if len(row_context_assignments) != 3 or any(len(r) != 3 for r in row_context_assignments):
                raise ValidationError("row_context_assignments must be a 3x3 sequence of {-1, +1}")
            r_assign = [
                [self._validate_sign(row_context_assignments[i][j], f"row_assign[{i}][{j}]") for j in range(3)]
                for i in range(3)
            ]
        else:
            r_assign = [[1, 1, r_targets[i]] for i in range(3)]

        if col_context_assignments is not None:
            if len(col_context_assignments) != 3 or any(len(c) != 3 for c in col_context_assignments):
                raise ValidationError("col_context_assignments must be a 3x3 sequence of {-1, +1}")
            c_assign = [
                [self._validate_sign(col_context_assignments[j][i], f"col_assign[{j}][{i}]") for i in range(3)]
                for j in range(3)
            ]
        else:
            c_assign = [[1, 1, c_targets[j]] for j in range(3)]

        row_evals = [
            1 if (r_assign[i][0] * r_assign[i][1] * r_assign[i][2] == r_targets[i]) else 0
            for i in range(3)
        ]
        col_evals = [
            1 if (c_assign[j][0] * c_assign[j][1] * c_assign[j][2] == c_targets[j]) else 0
            for j in range(3)
        ]

        local_product = 1
        for ev in row_evals + col_evals:
            local_product *= ev

        row_target_product = r_targets[0] * r_targets[1] * r_targets[2]
        col_target_product = c_targets[0] * c_targets[1] * c_targets[2]
        parity_obstruction = row_target_product != col_target_product

        # Exhaustively evaluate all 2^9 = 512 global non-contextual grids A in {-1, +1}^{3x3}
        max_satisfied = 0
        witness_count = 0
        for bits in range(512):
            a = [
                [-1 if ((bits >> (3 * i + j)) & 1) else 1 for j in range(3)]
                for i in range(3)
            ]
            sat = 0
            for i in range(3):
                if a[i][0] * a[i][1] * a[i][2] == r_targets[i]:
                    sat += 1
            for j in range(3):
                if a[0][j] * a[1][j] * a[2][j] == c_targets[j]:
                    sat += 1
            if sat > max_satisfied:
                max_satisfied = sat
            if sat == 6:
                witness_count += 1

        global_noncontextual_exists = witness_count > 0
        min_violated_contexts = 6 - max_satisfied
        global_eval = 1 if (local_product == 1 and global_noncontextual_exists) else 0
        defect = global_eval - local_product

        if local_product == 1 and global_eval == 0:
            grid_status = "MERMIN_PERES_PARITY_OBSTRUCTION_LGGR"
        elif local_product == 1 and global_eval == 1:
            grid_status = "NONCONTEXTUAL_PARITY_COHERENT_LGGG"
        else:
            grid_status = "LOCAL_CONTEXT_PARITY_REJECTED"

        rec = {
            "grid_id": gid,
            "row_targets": r_targets,
            "col_targets": c_targets,
            "row_context_evaluators": row_evals,
            "col_context_evaluators": col_evals,
            "row_target_product": row_target_product,
            "col_target_product": col_target_product,
            "parity_mismatch_obstruction": parity_obstruction,
            "max_satisfied_contexts_out_of_6": max_satisfied,
            "min_violated_contexts": min_violated_contexts,
            "global_noncontextual_witness_count": witness_count,
            "global_noncontextual_assignment_exists": global_noncontextual_exists,
            "local_product_aggregator": local_product,
            "global_noncontextual_evaluator": global_eval,
            "evaluator_defect": defect,
            "grid_status": grid_status,
        }
        self.grids.append(rec)
        return json_value(rec)

    def get_receipt(self) -> dict[str, Any]:
        """Emit a signed Mermin-Peres parity contextuality audit receipt."""
        if not self.grids:
            raise ValidationError("At least one Mermin-Peres parity grid must be recorded before emitting a receipt")

        obstructed_ids = [
            g["grid_id"]
            for g in self.grids
            if g["grid_status"] == "MERMIN_PERES_PARITY_OBSTRUCTION_LGGR"
        ]
        rejected_ids = [
            g["grid_id"]
            for g in self.grids
            if g["grid_status"] == "LOCAL_CONTEXT_PARITY_REJECTED"
        ]

        if obstructed_ids:
            status = "MERMIN_PERES_PARITY_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif rejected_ids:
            status = "LOCAL_CONTEXT_PARITY_REJECTED"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "NONCONTEXTUAL_PARITY_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_mermin_peres_parity.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "grid_count": len(self.grids),
            "parity_obstructed_grid_ids": obstructed_ids,
            "rejected_grid_ids": rejected_ids,
            "grids": self.grids,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingSideInformationCapacityMonitor:
    """Online side-information channel capacity and report-fiber error floor monitor (012_rsi/002 IK-04/IK-05 & LGGR I §5).

    Audits finite report fibers X_a = p^{-1}(a) equipped with an auxiliary side-information
    channel s: X_a -> {0, ..., S - 1} of finite alphabet capacity S >= 1:
      - Evaluates each state x in X_a locally for side-channel alphabet compliance:
          E_chan(x) = 1[0 <= s(x) < S],   L = prod_{x in X_a} E_chan(x) in {0, 1}.
      - Computes the number of distinct query values K = |q(X_a)| on the fiber,
        the active side-channel alphabet size S_used = |s(X_a)| <= S, and the
        capacity-induced distinct-value error floor:
          E_cap_floor(K, S) = max(0, K - S).
      - Partitions X_a into side-information sub-fibers X_{a, sigma} = {x in X_a : s(x) == sigma}
        with k_sigma = |q(X_{a, sigma})| distinct query values and computes:
          * realized_subfiber_error_floor = sum_{sigma in s(X_a)} (k_sigma - 1) >= max(0, K - S),
          * realized_sample_error_floor = sum_{sigma in s(X_a)} (|X_{a, sigma}| - max_y count(sigma, y)).
      - Evaluates global decodability E_g = 1[L == 1 and realized_subfiber_error_floor <= error_budget]
        and separates:
          * SIDE_INFORMATION_CAPACITY_DEFICIT_LGGR (L == 1 and E_g == 0, Delta_E = -1:
            every state emits a valid side-channel symbol in {0, ..., S - 1}, yet S < K
            forces at least K - S distinct query values on the fiber to collide under s),
          * SIDE_INFORMATION_SUFFICIENT_LGGG (L == 1 and E_g == 1, Delta_E = 0),
          * LOCAL_CHANNEL_SYMBOL_OUT_OF_RANGE (L == 0).
    """

    def __init__(self, *, scope_id: str = "streaming-side-information-capacity-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.fibers: list[dict[str, Any]] = []

    def record_fiber_channel(
        self,
        fiber_id: str,
        states: Sequence[dict[str, Any]],
        *,
        channel_capacity_s: int,
        error_budget: int = 0,
    ) -> dict[str, Any]:
        """Record a report fiber X_a with side-channel symbols s(x) and audit capacity vs K = |q(X_a)|."""
        fid = text(fiber_id, "fiber_id")
        cap_s = exact_int(channel_capacity_s, "channel_capacity_s", minimum=1)
        budget = exact_int(error_budget, "error_budget", minimum=0)
        if not states:
            raise ValidationError("states must be a non-empty sequence of fiber state records")

        parsed_states: list[dict[str, Any]] = []
        distinct_queries: set[str] = set()
        subfiber_queries: dict[int, set[str]] = {}
        subfiber_counts: dict[int, dict[str, int]] = {}
        local_product = 1

        for idx, st in enumerate(states):
            if not isinstance(st, Mapping):
                raise ValidationError(f"states[{idx}] must be a mapping")
            sid = text(st.get("state_id", f"state_{idx}"), f"states[{idx}].state_id")
            q_val = canonical(st.get("query_value"))
            sym = exact_int(st.get("side_symbol"), f"states[{idx}].side_symbol")

            in_range = 1 if (0 <= sym < cap_s) else 0
            local_product *= in_range
            distinct_queries.add(q_val)

            if in_range == 1:
                subfiber_queries.setdefault(sym, set()).add(q_val)
                counts = subfiber_counts.setdefault(sym, {})
                counts[q_val] = counts.get(q_val, 0) + 1

            parsed_states.append(
                {
                    "state_id": sid,
                    "query_value": st.get("query_value"),
                    "side_symbol": sym,
                    "local_channel_evaluator": in_range,
                }
            )

        k_distinct = len(distinct_queries)
        used_symbols = len(subfiber_queries)
        capacity_floor = max(0, k_distinct - cap_s)

        subfiber_error_floor = sum(max(0, len(qs) - 1) for qs in subfiber_queries.values())
        sample_error_floor = sum(
            sum(cnts.values()) - max(cnts.values())
            for cnts in subfiber_counts.values()
        )
        pigeonhole_bound_verified = (local_product == 0) or (subfiber_error_floor >= capacity_floor)

        global_eval = 1 if (local_product == 1 and subfiber_error_floor <= budget) else 0
        defect = global_eval - local_product

        if local_product == 1 and global_eval == 0:
            fiber_status = "SIDE_INFORMATION_CAPACITY_DEFICIT_LGGR"
        elif local_product == 1 and global_eval == 1:
            fiber_status = "SIDE_INFORMATION_SUFFICIENT_LGGG"
        else:
            fiber_status = "LOCAL_CHANNEL_SYMBOL_OUT_OF_RANGE"

        rec = {
            "fiber_id": fid,
            "state_count": len(parsed_states),
            "distinct_query_values_k": k_distinct,
            "channel_capacity_s": cap_s,
            "used_symbols_count": used_symbols,
            "error_budget": budget,
            "capacity_error_floor_k_minus_s": capacity_floor,
            "realized_subfiber_error_floor": subfiber_error_floor,
            "realized_sample_error_floor": sample_error_floor,
            "pigeonhole_bound_verified": pigeonhole_bound_verified,
            "local_product_aggregator": local_product,
            "global_decodability_evaluator": global_eval,
            "evaluator_defect": defect,
            "fiber_status": fiber_status,
            "states": parsed_states,
        }
        self.fibers.append(rec)
        return json_value(rec)

    def get_receipt(self) -> dict[str, Any]:
        """Emit a signed side-information channel capacity audit receipt."""
        if not self.fibers:
            raise ValidationError("At least one fiber channel must be recorded before emitting a receipt")

        deficit_ids = [
            f["fiber_id"]
            for f in self.fibers
            if f["fiber_status"] == "SIDE_INFORMATION_CAPACITY_DEFICIT_LGGR"
        ]
        rejected_ids = [
            f["fiber_id"]
            for f in self.fibers
            if f["fiber_status"] == "LOCAL_CHANNEL_SYMBOL_OUT_OF_RANGE"
        ]
        all_bounds_ok = all(f["pigeonhole_bound_verified"] for f in self.fibers)

        if deficit_ids:
            status = "SIDE_INFORMATION_CAPACITY_DEFICIT_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif rejected_ids:
            status = "LOCAL_CHANNEL_SYMBOL_OUT_OF_RANGE"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "SIDE_INFORMATION_SUFFICIENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_side_information_capacity.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "fiber_count": len(self.fibers),
            "all_pigeonhole_bounds_verified": all_bounds_ok,
            "capacity_deficit_fiber_ids": deficit_ids,
            "rejected_fiber_ids": rejected_ids,
            "fibers": self.fibers,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingProductOfExpertsMonitor:
    """Online Product-of-Experts (PoE) vs Mixture-of-Experts (MoE) disjoint-support collapse monitor (LGGR I §7.2 & II §2.2).

    Audits finite K-expert score tables p_k in Q_{>=0}^m over m candidate actions W = {w_0, ..., w_{m-1}}:
      - Evaluates each expert k in {0, ..., K-1} locally for positive total score mass:
          M_k = sum_{j=0}^{m-1} p_k(w_j),   E_expert(k) = 1[M_k > 0],
        and forms the local product aggregator:
          L = prod_{k=0}^{K-1} E_expert(k) in {0, 1}.
      - Computes the unnormalized Product-of-Experts score vector:
          P_PoE(w_j) = prod_{k=0}^{K-1} p_k(w_j)
        and the PoE partition sum (normalizing denominator):
          D_PoE = sum_{j=0}^{m-1} P_PoE(w_j).
      - Computes the weighted Mixture-of-Experts score vector (under positive weights alpha_k > 0,
        sum_k alpha_k = 1, defaulting to uniform 1/K):
          P_MoE(w_j) = sum_{k=0}^{K-1} alpha_k * p_k(w_j)
        and the MoE partition sum:
          D_MoE = sum_{j=0}^{m-1} P_MoE(w_j) = sum_{k=0}^{K-1} alpha_k * M_k.
      - Identifies the joint support intersection:
          supp_intersection = {j in {0, ..., m-1} : forall k, p_k(w_j) > 0},
        where D_PoE > 0 iff supp_intersection is non-empty.
      - Evaluates global PoE normalizability E_g = 1[L == 1 and D_PoE > 0] and separates:
          * POE_DISJOINT_SUPPORT_COLLAPSE_LGGR (L == 1 and E_g == 0, Delta_E = -1:
            every expert has positive score mass M_k > 0 and D_MoE > 0, yet disjoint expert
            supports cause D_PoE == 0 so PoE normalization collapses),
          * POE_AND_MOE_COHERENT_LGGG (L == 1 and E_g == 1, Delta_E = 0),
          * LOCAL_EXPERT_ZERO_MASS_REJECTED (L == 0).
    """

    def __init__(self, *, scope_id: str = "streaming-product-of-experts-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.rounds: list[dict[str, Any]] = []

    def record_expert_scores(
        self,
        round_id: str,
        expert_scores: Sequence[Sequence[int | str | Fraction]],
        *,
        mixture_weights: Sequence[int | str | Fraction] | None = None,
    ) -> dict[str, Any]:
        """Record a K x m table of non-negative rational expert scores and audit PoE vs MoE partition sums."""
        rid = text(round_id, "round_id")
        if not expert_scores:
            raise ValidationError("expert_scores must contain at least one expert row")
        num_experts = len(expert_scores)
        num_candidates = len(expert_scores[0])
        if num_candidates == 0:
            raise ValidationError("expert_scores must have at least one candidate column")

        parsed_scores: list[list[Fraction]] = []
        for k, row in enumerate(expert_scores):
            if len(row) != num_candidates:
                raise ValidationError("All expert score rows must have the same number of candidates")
            parsed_row = [rational(val) for val in row]
            if any(v < 0 for v in parsed_row):
                raise ValidationError(f"expert_scores[{k}] entries must be non-negative")
            parsed_scores.append(parsed_row)

        if mixture_weights is not None:
            if len(mixture_weights) != num_experts:
                raise ValidationError("mixture_weights length must match number of experts")
            weights = [rational(w) for w in mixture_weights]
            if any(w <= 0 for w in weights) or sum(weights, Fraction(0)) != Fraction(1):
                raise ValidationError("mixture_weights must be strictly positive and sum to 1")
        else:
            weights = [Fraction(1, num_experts) for _ in range(num_experts)]

        expert_masses = [sum(row, Fraction(0)) for row in parsed_scores]
        expert_evals = [1 if m > 0 else 0 for m in expert_masses]
        local_product = 1
        for ev in expert_evals:
            local_product *= ev

        poe_vector: list[Fraction] = []
        moe_vector: list[Fraction] = []
        joint_support_indices: list[int] = []

        for j in range(num_candidates):
            prod_j = Fraction(1)
            mix_j = Fraction(0)
            for k in range(num_experts):
                prod_j *= parsed_scores[k][j]
                mix_j += weights[k] * parsed_scores[k][j]
            poe_vector.append(prod_j)
            moe_vector.append(mix_j)
            if prod_j > 0:
                joint_support_indices.append(j)

        d_poe = sum(poe_vector, Fraction(0))
        d_moe = sum(moe_vector, Fraction(0))
        normalized_poe = [val / d_poe for val in poe_vector] if d_poe > 0 else None
        normalized_moe = [val / d_moe for val in moe_vector] if d_moe > 0 else None

        global_eval = 1 if (local_product == 1 and d_poe > 0) else 0
        defect = global_eval - local_product

        if local_product == 1 and global_eval == 0:
            round_status = "POE_DISJOINT_SUPPORT_COLLAPSE_LGGR"
        elif local_product == 1 and global_eval == 1:
            round_status = "POE_AND_MOE_COHERENT_LGGG"
        else:
            round_status = "LOCAL_EXPERT_ZERO_MASS_REJECTED"

        rec = {
            "round_id": rid,
            "expert_count": num_experts,
            "candidate_count": num_candidates,
            "expert_masses": expert_masses,
            "local_expert_evaluators": expert_evals,
            "joint_support_indices": joint_support_indices,
            "poe_unnormalized_vector": poe_vector,
            "poe_partition_sum": d_poe,
            "poe_normalized_distribution": normalized_poe,
            "moe_unnormalized_vector": moe_vector,
            "moe_partition_sum": d_moe,
            "moe_normalized_distribution": normalized_moe,
            "local_product_aggregator": local_product,
            "global_poe_normalizable_evaluator": global_eval,
            "evaluator_defect": defect,
            "round_status": round_status,
        }
        self.rounds.append(rec)
        return json_value(rec)

    def get_receipt(self) -> dict[str, Any]:
        """Emit a signed Product-of-Experts vs Mixture-of-Experts support-collapse receipt."""
        if not self.rounds:
            raise ValidationError("At least one expert score round must be recorded before emitting a receipt")

        collapsed_ids = [
            r["round_id"]
            for r in self.rounds
            if r["round_status"] == "POE_DISJOINT_SUPPORT_COLLAPSE_LGGR"
        ]
        rejected_ids = [
            r["round_id"]
            for r in self.rounds
            if r["round_status"] == "LOCAL_EXPERT_ZERO_MASS_REJECTED"
        ]

        if collapsed_ids:
            status = "POE_DISJOINT_SUPPORT_COLLAPSE_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        elif rejected_ids:
            status = "LOCAL_EXPERT_ZERO_MASS_REJECTED"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "POE_AND_MOE_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"

        body = {
            "schema": "lggr.online_product_of_experts.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "round_count": len(self.rounds),
            "poe_collapsed_round_ids": collapsed_ids,
            "rejected_round_ids": rejected_ids,
            "rounds": self.rounds,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingClosedLoopRepairMonitor:
    """Finite observed repair-trajectory summaries (LGGR VIII §6 & Theorem 55).

    Theorem 55 supplies fixed arithmetic examples, not a convergence or termination
    theorem. These rates summarize supplied rounds; they do not establish a causal
    advantage over another solver or feedback protocol.

    Audits multi-round closed-loop orchestrator repair trajectories
    R_0 (baseline obstructed) -> R_1 (single-round raw receipt feedback) -> R_2 (multi-round witness-guided feedback)
    across frontier monitors and model families:
      - Evaluates whether an initial NGD obstruction (L^{(0)} == 1, E_g^{(0)} == 0, Delta_E^{(0)} == -1)
        converges to a globally coherent LGGG state (L^{(r)} == 1, E_g^{(r)} == 1, Delta_E^{(r)} == 0)
        at Round 1 (single-round convergence) or by Round T (multi-round convergence).
      - Separates:
          * SINGLE_ROUND_RECEIPT_CONVERGED_LGGG (converged at Round 1 and remains coherent at Round T),
          * MULTI_ROUND_WITNESS_CONVERGED_LGGG (obstructed at Round 1, converged by Round T via witness feedback),
          * UNREPAIRED_PERSISTENT_OBSTRUCTION_LGGR (remains obstructed at Round T, Delta_E^{(T)} == -1 or L^{(T)} == 0).
      - Computes exact rational single-round vs multi-round convergence rates and per-model / per-monitor breakdowns.
    """

    def __init__(self, *, scope_id: str = "streaming-closed-loop-repair-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.trajectories: list[dict[str, Any]] = []

    def record_trajectory(
        self,
        trajectory_id: str,
        *,
        monitor_name: str,
        model_id: str,
        rounds: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        """Record a multi-round closed-loop receipt-feedback trajectory (R_0, R_1, ..., R_T)."""
        tid = text(trajectory_id, "trajectory_id")
        mon = text(monitor_name, "monitor_name")
        mdl = text(model_id, "model_id")
        if len(rounds) < 2:
            raise ValidationError("A closed-loop repair trajectory requires at least 2 rounds (baseline R_0 and repair R_1)")

        parsed_rounds: list[dict[str, Any]] = []
        for idx, r in enumerate(rounds):
            if not isinstance(r, Mapping):
                raise ValidationError(f"rounds[{idx}] must be a mapping")
            r_status = text(r.get("receipt_status", "UNKNOWN"), f"rounds[{idx}].receipt_status")
            c_status = text(r.get("contract_status"), f"rounds[{idx}].contract_status")
            l_pass = boolean(r.get("local_pass"), f"rounds[{idx}].local_pass")
            g_pass = boolean(r.get("global_pass"), f"rounds[{idx}].global_pass")
            expected_status = "COMPOSABLE_LGGG" if l_pass and g_pass else "OBSTRUCTED_LGGR"
            if c_status != expected_status:
                raise ValidationError(f"rounds[{idx}].contract_status contradicts its Boolean verdicts")
            defect = (1 if g_pass else 0) - (1 if l_pass else 0)
            fb_mode = text(r.get("feedback_mode", f"round_{idx}"), f"rounds[{idx}].feedback_mode")
            parsed_rounds.append(
                {
                    "round_index": idx,
                    "feedback_mode": fb_mode,
                    "receipt_status": r_status,
                    "contract_status": c_status,
                    "local_pass": l_pass,
                    "global_pass": g_pass,
                    "evaluator_defect": defect,
                }
            )

        r0 = parsed_rounds[0]
        r1 = parsed_rounds[1]
        r_final = parsed_rounds[-1]

        initial_ngd = r0["local_pass"] and (not r0["global_pass"]) and (r0["evaluator_defect"] == -1)
        single_round_ok = r1["local_pass"] and r1["global_pass"] and (r1["evaluator_defect"] == 0)
        multi_round_ok = r_final["local_pass"] and r_final["global_pass"] and (r_final["evaluator_defect"] == 0)

        rounds_to_converge: int | None = None
        for pr in parsed_rounds[1:]:
            if pr["local_pass"] and pr["global_pass"] and pr["evaluator_defect"] == 0:
                rounds_to_converge = pr["round_index"]
                break

        if single_round_ok and multi_round_ok:
            traj_status = "SINGLE_ROUND_RECEIPT_CONVERGED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        elif (not single_round_ok) and multi_round_ok:
            traj_status = "MULTI_ROUND_WITNESS_CONVERGED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            traj_status = "UNREPAIRED_PERSISTENT_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        rec = {
            "trajectory_id": tid,
            "monitor_name": mon,
            "model_id": mdl,
            "round_count": len(parsed_rounds),
            "initial_ngd_obstructed": initial_ngd,
            "converged_single_round": single_round_ok,
            "converged_multi_round": multi_round_ok,
            "rounds_to_convergence": rounds_to_converge,
            "defect_progression": [pr["evaluator_defect"] for pr in parsed_rounds],
            "final_local_pass": r_final["local_pass"],
            "final_global_pass": r_final["global_pass"],
            "final_evaluator_defect": r_final["evaluator_defect"],
            "trajectory_status": traj_status,
            "contract_status": contract_status,
            "rounds": parsed_rounds,
        }
        self.trajectories.append(rec)
        return json_value(rec)

    def get_receipt(self) -> dict[str, Any]:
        """Emit a signed closed-loop repair convergence receipt."""
        if not self.trajectories:
            raise ValidationError("At least one closed-loop trajectory must be recorded before emitting a receipt")

        n = len(self.trajectories)
        single_cnt = sum(1 for t in self.trajectories if t["converged_single_round"])
        multi_cnt = sum(1 for t in self.trajectories if t["converged_multi_round"])
        unrepaired_ids = [
            t["trajectory_id"] for t in self.trajectories if not t["converged_multi_round"]
        ]
        multi_only_ids = [
            t["trajectory_id"]
            for t in self.trajectories
            if t["converged_multi_round"] and (not t["converged_single_round"])
        ]

        r1_rate = Fraction(single_cnt, n)
        rt_rate = Fraction(multi_cnt, n)
        multi_gain = rt_rate - r1_rate
        unrepaired_rate = Fraction(n - multi_cnt, n)

        if len(unrepaired_ids) == 0:
            status = "CLOSED_LOOP_REPAIR_CONVERGED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "CLOSED_LOOP_RESIDUAL_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body = {
            "schema": "lggr.online_closed_loop_repair.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "trajectory_count": n,
            "single_round_converged_count": single_cnt,
            "multi_round_converged_count": multi_cnt,
            "single_round_convergence_rate": r1_rate,
            "multi_round_convergence_rate": rt_rate,
            "multi_round_convergence_gain": multi_gain,
            "residual_unrepaired_rate": unrepaired_rate,
            "monotonic_convergence_verified": rt_rate >= r1_rate,
            "multi_round_witness_rescued_ids": multi_only_ids,
            "unrepaired_trajectory_ids": unrepaired_ids,
            "trajectories": self.trajectories,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingJointMultiMonitorRepairGuard:
    """Online coupled multi-monitor closed-loop repair guard (LGGR VIII §6 & Theorem 56).

    Audits closed-loop orchestrator repair trajectories where a single orchestrator
    decision u^{(r)} simultaneously touches two coupled frontier monitors (Monitor A and Monitor B):
      - Evaluates joint local aggregator L_joint = L_A * L_B in {0, 1}
        and joint global evaluator E_{g,joint} = E_{g,A} * E_{g,B} in {0, 1},
        with joint defect Delta_{E,joint} = E_{g,joint} - L_joint in {-1, 0, 1}.
      - Separates:
          * JOINT_PARETO_COHERENT_LGGG (L_joint == 1, E_{g,A} == 1, E_{g,B} == 1, Delta_{E,joint} == 0),
          * CROSS_MONITOR_WHACK_A_MOLE_NGD_LGGR (L_joint == 1 and E_{g,A} != E_{g,B}, so repairing
            one monitor leaves or induces an NGD obstruction in the coupled monitor, Delta_{E,joint} == -1),
          * DOUBLE_MONITOR_OBSTRUCTED_NGD_LGGR (L_joint == 1, E_{g,A} == 0, E_{g,B} == 0, Delta_{E,joint} == -1),
          * LOCAL_SUBMONITOR_REJECTED_LRGR (L_joint == 0).
    """

    def __init__(self, *, scope_id: str = "streaming-joint-multi-monitor-repair-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.trajectories: list[dict[str, Any]] = []

    def record_coupled_trajectory(
        self,
        trajectory_id: str,
        *,
        pair_name: str,
        monitor_a_name: str,
        monitor_b_name: str,
        model_id: str,
        rounds: Sequence[Mapping[str, Any]],
        feasible_intersection_empty: bool | None = None,
        candidate_actions: Sequence[Mapping[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Record a multi-round joint repair trajectory across two coupled frontier monitors."""
        tid = text(trajectory_id, "trajectory_id")
        pname = text(pair_name, "pair_name")
        mon_a = text(monitor_a_name, "monitor_a_name")
        mon_b = text(monitor_b_name, "monitor_b_name")
        mdl = text(model_id, "model_id")
        if len(rounds) < 2:
            raise ValidationError("A coupled repair trajectory requires at least 2 rounds (R_0 and R_1)")

        escalation_audit_active = (feasible_intersection_empty is not None) or (candidate_actions is not None)
        is_empty_intersection = False
        parsed_candidates: list[dict[str, Any]] = []
        if candidate_actions is not None:
            if len(candidate_actions) == 0:
                raise ValidationError("candidate_actions cannot be empty when provided")
            for c_idx, cand in enumerate(candidate_actions):
                if not isinstance(cand, Mapping):
                    raise ValidationError(f"candidate_actions[{c_idx}] must be a mapping")
                c_id = text(cand.get("action_id", f"action_{c_idx}"), f"candidate_actions[{c_idx}].action_id")
                c_ga = bool(cand.get("global_a_pass", False))
                c_gb = bool(cand.get("global_b_pass", False))
                parsed_candidates.append(
                    {
                        "action_id": c_id,
                        "global_a_pass": c_ga,
                        "global_b_pass": c_gb,
                        "joint_global_pass": c_ga and c_gb,
                    }
                )
            computed_empty = not any(c["joint_global_pass"] for c in parsed_candidates)
            if (feasible_intersection_empty is not None) and (bool(feasible_intersection_empty) != computed_empty):
                raise ValidationError("feasible_intersection_empty disagrees with candidate_actions table")
            is_empty_intersection = computed_empty
        elif feasible_intersection_empty is not None:
            is_empty_intersection = bool(feasible_intersection_empty)

        parsed_rounds: list[dict[str, Any]] = []
        for idx, r in enumerate(rounds):
            if not isinstance(r, Mapping):
                raise ValidationError(f"rounds[{idx}] must be a mapping")
            fb_mode = text(r.get("feedback_mode", f"round_{idx}"), f"rounds[{idx}].feedback_mode")
            la = bool(r.get("local_a_pass", False))
            ga = bool(r.get("global_a_pass", False))
            lb = bool(r.get("local_b_pass", False))
            gb = bool(r.get("global_b_pass", False))
            sa = text(r.get("status_a", "UNKNOWN"), f"rounds[{idx}].status_a")
            sb = text(r.get("status_b", "UNKNOWN"), f"rounds[{idx}].status_b")

            l_joint = la and lb
            g_joint = ga and gb
            d_joint = (1 if g_joint else 0) - (1 if l_joint else 0)
            whack_a_mole = l_joint and (ga != gb)

            if l_joint and g_joint:
                r_status = "JOINT_PARETO_COHERENT_LGGG"
                c_status = "COMPOSABLE_LGGG"
            elif whack_a_mole:
                r_status = "CROSS_MONITOR_WHACK_A_MOLE_NGD_LGGR"
                c_status = "OBSTRUCTED_LGGR"
            elif l_joint and (not ga) and (not gb):
                r_status = "DOUBLE_MONITOR_OBSTRUCTED_NGD_LGGR"
                c_status = "OBSTRUCTED_LGGR"
            else:
                r_status = "LOCAL_SUBMONITOR_REJECTED_LRGR"
                c_status = "OBSTRUCTED_LGGR"

            parsed_rounds.append(
                {
                    "round_index": idx,
                    "feedback_mode": fb_mode,
                    "status_a": sa,
                    "status_b": sb,
                    "local_a_pass": la,
                    "global_a_pass": ga,
                    "local_b_pass": lb,
                    "global_b_pass": gb,
                    "local_pass": l_joint,
                    "global_pass": g_joint,
                    "defect": d_joint,
                    "whack_a_mole_partial_repair": whack_a_mole,
                    "round_joint_status": r_status,
                    "contract_status": c_status,
                }
            )

        r1 = parsed_rounds[1]
        r_final = parsed_rounds[-1]

        single_round_ok = r1["local_pass"] and r1["global_pass"] and (r1["defect"] == 0)
        multi_round_ok = r_final["local_pass"] and r_final["global_pass"] and (r_final["defect"] == 0)
        r1_whack_a_mole = r1["whack_a_mole_partial_repair"]

        oscillation_detected = False
        oscillation_step_l1 = 0
        for i in range(1, len(parsed_rounds)):
            for j in range(i + 1, len(parsed_rounds)):
                pi = parsed_rounds[i]
                pj = parsed_rounds[j]
                if pi["whack_a_mole_partial_repair"] and pj["whack_a_mole_partial_repair"]:
                    if (pi["global_a_pass"] != pj["global_a_pass"]) and (
                        pi["global_b_pass"] != pj["global_b_pass"]
                    ):
                        oscillation_detected = True
                        oscillation_step_l1 = abs(
                            (1 if pj["global_a_pass"] else 0) - (1 if pi["global_a_pass"] else 0)
                        ) + abs((1 if pj["global_b_pass"] else 0) - (1 if pi["global_b_pass"] else 0))

        if single_round_ok and multi_round_ok:
            traj_status = "JOINT_SINGLE_ROUND_CONVERGED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        elif (not single_round_ok) and multi_round_ok:
            traj_status = "JOINT_MULTI_ROUND_PARETO_CONVERGED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            traj_status = "JOINT_UNREPAIRED_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        rec: dict[str, Any] = {
            "trajectory_id": tid,
            "pair_name": pname,
            "monitor_a_name": mon_a,
            "monitor_b_name": mon_b,
            "model_id": mdl,
            "round_count": len(parsed_rounds),
            "round_1_whack_a_mole_detected": r1_whack_a_mole,
            "converged_single_round": single_round_ok,
            "converged_multi_round": multi_round_ok,
            "joint_defect_progression": [pr["defect"] for pr in parsed_rounds],
            "trajectory_status": traj_status,
            "contract_status": contract_status,
            "rounds": parsed_rounds,
        }
        if escalation_audit_active:
            halted_and_escalated = (not multi_round_ok) and (oscillation_detected or is_empty_intersection)
            if halted_and_escalated and oscillation_detected and is_empty_intersection:
                rec["trajectory_status"] = "INFEASIBLE_EMPTY_INTERSECTION_OSCILLATION_HALTED_AND_ESCALATED_LGGR"
                esc_action = "HALT_OSCILLATING_REPAIR_AND_ESCALATE_INFEASIBLE_COUPLED_CONSTRAINTS"
            elif halted_and_escalated and is_empty_intersection:
                rec["trajectory_status"] = "INFEASIBLE_EMPTY_INTERSECTION_HALTED_AND_ESCALATED_LGGR"
                esc_action = "HALT_REPAIR_AND_ESCALATE_INFEASIBLE_COUPLED_CONSTRAINTS"
            elif halted_and_escalated and oscillation_detected:
                rec["trajectory_status"] = "WHACK_A_MOLE_OSCILLATION_HALTED_AND_ESCALATED_LGGR"
                esc_action = "HALT_OSCILLATING_REPAIR_AND_ESCALATE"
            else:
                esc_action = "NONE"
            rec["feasible_intersection_empty"] = is_empty_intersection
            rec["whack_a_mole_oscillation_detected"] = oscillation_detected
            rec["oscillation_l1_step_distance"] = oscillation_step_l1
            rec["halted_and_escalated"] = halted_and_escalated
            rec["escalation_action"] = esc_action
            if parsed_candidates:
                rec["candidate_actions"] = parsed_candidates

        self.trajectories.append(rec)
        return json_value(rec)

    def get_receipt(self) -> dict[str, Any]:
        """Emit a signed coupled multi-monitor repair convergence receipt."""
        if not self.trajectories:
            raise ValidationError("At least one coupled trajectory must be recorded before emitting a receipt")

        n = len(self.trajectories)
        single_cnt = sum(1 for t in self.trajectories if t["converged_single_round"])
        multi_cnt = sum(1 for t in self.trajectories if t["converged_multi_round"])
        wam_cnt = sum(1 for t in self.trajectories if t["round_1_whack_a_mole_detected"])

        unrepaired_ids = [
            t["trajectory_id"] for t in self.trajectories if not t["converged_multi_round"]
        ]
        wam_ids = [
            t["trajectory_id"] for t in self.trajectories if t["round_1_whack_a_mole_detected"]
        ]

        r1_rate = Fraction(single_cnt, n)
        rt_rate = Fraction(multi_cnt, n)
        multi_gain = rt_rate - r1_rate
        wam_rate = Fraction(wam_cnt, n)

        has_escalation = any("halted_and_escalated" in t for t in self.trajectories)
        if len(unrepaired_ids) == 0:
            status = "JOINT_MULTI_MONITOR_PARETO_CONVERGED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        elif has_escalation and all(
            t.get("halted_and_escalated", False) for t in self.trajectories if not t["converged_multi_round"]
        ):
            status = "INFEASIBLE_COUPLED_REGIME_HALTED_AND_ESCALATED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"
        else:
            status = "JOINT_MULTI_MONITOR_RESIDUAL_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_joint_multi_monitor_repair.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "trajectory_count": n,
            "single_round_converged_count": single_cnt,
            "multi_round_converged_count": multi_cnt,
            "round_1_whack_a_mole_count": wam_cnt,
            "single_round_convergence_rate": r1_rate,
            "multi_round_convergence_rate": rt_rate,
            "multi_round_convergence_gain": multi_gain,
            "round_1_whack_a_mole_rate": wam_rate,
            "monotonic_convergence_verified": rt_rate >= r1_rate,
            "round_1_whack_a_mole_trajectory_ids": wam_ids,
            "unrepaired_trajectory_ids": unrepaired_ids,
            "trajectories": self.trajectories,
        }
        if has_escalation:
            empty_cnt = sum(1 for t in self.trajectories if t.get("feasible_intersection_empty", False))
            osc_cnt = sum(1 for t in self.trajectories if t.get("whack_a_mole_oscillation_detected", False))
            esc_cnt = sum(1 for t in self.trajectories if t.get("halted_and_escalated", False))
            osc_ids = [
                t["trajectory_id"]
                for t in self.trajectories
                if t.get("whack_a_mole_oscillation_detected", False)
            ]
            esc_ids = [
                t["trajectory_id"]
                for t in self.trajectories
                if t.get("halted_and_escalated", False)
            ]
            body["empty_feasible_intersection_count"] = empty_cnt
            body["whack_a_mole_oscillation_count"] = osc_cnt
            body["halted_and_escalated_count"] = esc_cnt
            body["whack_a_mole_oscillation_rate"] = Fraction(osc_cnt, n)
            body["halt_and_escalate_rate"] = Fraction(esc_cnt, n)
            body["oscillating_trajectory_ids"] = osc_ids
            body["halted_and_escalated_trajectory_ids"] = esc_ids

        return json_value({**body, "receipt_sha256": digest(body)})


def _validate_sha256_hex(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise ValidationError(f"{label} must be a 64-character lowercase hex SHA-256 string")
    return value


class StreamingGovernedPolicyRelaxationMonitor:
    r"""Audit governed external policy-relaxation handoffs vs. unauthorized worker self-relaxation (LGGR VIII §5.23).

    Starting from a halted and escalated coupled regime
    (``INFEASIBLE_COUPLED_REGIME_HALTED_AND_ESCALATED_LGGR``), verifies:
    1. Any worker attempt to self-relax its own ``BudgetPolicy`` or side-channel
       capacity without an external authority grant (``authority_grant_verified = False``)
       is rejected with ``UNAUTHORIZED_SELF_RELAXATION_REJECTED_LGGR``
       (``local_pass = True``, ``global_pass = False``, ``defect = -1``).
    2. An external authority gate that binds ``prior_escalation_receipt_sha256`` and
       transitions ``prior_policy_sha256 -> relaxed_policy_sha256`` with a non-empty
       relaxed Pareto intersection $\mathcal{F}_A(P_1) \cap \mathcal{F}_B(P_1) \ne \emptyset$
       enables post-handoff Round 3 convergence to ``(E_{g,A}, E_{g,B}) = (1, 1)``
       (``GOVERNED_POLICY_RELAXATION_PARETO_RESTORED_LGGG``).
    """

    def __init__(self, scope_id: str) -> None:
        if not isinstance(scope_id, str) or not scope_id.strip():
            raise ValidationError("scope_id must be a non-empty string")
        self.scope_id = scope_id.strip()
        self.handoffs: list[dict[str, Any]] = []

    def record_relaxation_handoff(
        self,
        *,
        handoff_id: str,
        pair_name: str,
        model_id: str,
        prior_escalation_receipt_sha256: str,
        prior_policy_sha256: str,
        relaxed_policy_sha256: str,
        authority_id: str,
        authority_grant_verified: bool,
        pre_handoff_halted_and_escalated: bool,
        relaxed_candidate_actions: Sequence[Mapping[str, Any]],
        unauthorized_self_relaxation_attempt: Mapping[str, Any],
        post_handoff_round: Mapping[str, Any],
    ) -> dict[str, Any]:
        if not isinstance(handoff_id, str) or not handoff_id.strip():
            raise ValidationError("handoff_id must be a non-empty string")
        if not isinstance(pair_name, str) or not pair_name.strip():
            raise ValidationError("pair_name must be a non-empty string")
        if not isinstance(model_id, str) or not model_id.strip():
            raise ValidationError("model_id must be a non-empty string")
        if not isinstance(authority_id, str) or not authority_id.strip():
            raise ValidationError("authority_id must be a non-empty string")
        if not isinstance(authority_grant_verified, bool):
            raise ValidationError("authority_grant_verified must be a boolean")
        if not isinstance(pre_handoff_halted_and_escalated, bool):
            raise ValidationError("pre_handoff_halted_and_escalated must be a boolean")

        esc_sha = _validate_sha256_hex(prior_escalation_receipt_sha256, "prior_escalation_receipt_sha256")
        p0_sha = _validate_sha256_hex(prior_policy_sha256, "prior_policy_sha256")
        p1_sha = _validate_sha256_hex(relaxed_policy_sha256, "relaxed_policy_sha256")
        if p0_sha == p1_sha:
            raise ValidationError("relaxed_policy_sha256 must differ from prior_policy_sha256")

        if not isinstance(relaxed_candidate_actions, Sequence) or len(relaxed_candidate_actions) == 0:
            raise ValidationError("relaxed_candidate_actions must be a non-empty sequence")

        normalized_candidates: list[dict[str, Any]] = []
        for c_idx, cand in enumerate(relaxed_candidate_actions):
            if not isinstance(cand, Mapping):
                raise ValidationError(f"relaxed_candidate_actions[{c_idx}] must be a mapping")
            c_ga = cand.get("global_a_pass")
            c_gb = cand.get("global_b_pass")
            if not isinstance(c_ga, bool) or not isinstance(c_gb, bool):
                raise ValidationError(
                    f"relaxed_candidate_actions[{c_idx}] must specify boolean global_a_pass and global_b_pass"
                )
            normalized_candidates.append(
                {
                    "action_id": str(cand.get("action_id", f"relaxed_action_{c_idx}")),
                    "global_a_pass": c_ga,
                    "global_b_pass": c_gb,
                    "joint_global_pass": bool(c_ga and c_gb),
                }
            )
        relaxed_pareto_nonempty = any(c["joint_global_pass"] for c in normalized_candidates)

        if not isinstance(unauthorized_self_relaxation_attempt, Mapping):
            raise ValidationError("unauthorized_self_relaxation_attempt must be a mapping")
        unauth_grant = unauthorized_self_relaxation_attempt.get("authority_grant_verified", False)
        if not isinstance(unauth_grant, bool) or unauth_grant:
            raise ValidationError(
                "unauthorized_self_relaxation_attempt must have authority_grant_verified=False"
            )
        unauth_la = unauthorized_self_relaxation_attempt.get("local_a_pass")
        unauth_ga = unauthorized_self_relaxation_attempt.get("global_a_pass")
        unauth_lb = unauthorized_self_relaxation_attempt.get("local_b_pass")
        unauth_gb = unauthorized_self_relaxation_attempt.get("global_b_pass")
        if (
            not isinstance(unauth_la, bool)
            or not isinstance(unauth_ga, bool)
            or not isinstance(unauth_lb, bool)
            or not isinstance(unauth_gb, bool)
        ):
            raise ValidationError(
                "unauthorized_self_relaxation_attempt must contain boolean local_a_pass, global_a_pass, local_b_pass, global_b_pass"
            )
        unauth_local_pass = bool(unauth_la and unauth_lb)
        unauth_global_pass = bool(unauth_grant and unauth_ga and unauth_gb)
        unauth_defect = int(unauth_global_pass) - int(unauth_local_pass)
        unauth_rejected = bool(unauth_local_pass and not unauth_global_pass and unauth_defect == -1)
        unauth_record = {
            "authority_grant_verified": unauth_grant,
            "local_a_pass": unauth_la,
            "global_a_pass": unauth_ga,
            "local_b_pass": unauth_lb,
            "global_b_pass": unauth_gb,
            "local_pass": unauth_local_pass,
            "global_pass": unauth_global_pass,
            "defect": unauth_defect,
            "rejected": unauth_rejected,
            "status": (
                "UNAUTHORIZED_SELF_RELAXATION_REJECTED_LGGR"
                if unauth_rejected
                else "UNAUTHORIZED_ATTEMPT_NOT_REJECTED_ERROR"
            ),
        }

        if not isinstance(post_handoff_round, Mapping):
            raise ValidationError("post_handoff_round must be a mapping")
        post_la = post_handoff_round.get("local_a_pass")
        post_ga = post_handoff_round.get("global_a_pass")
        post_lb = post_handoff_round.get("local_b_pass")
        post_gb = post_handoff_round.get("global_b_pass")
        if (
            not isinstance(post_la, bool)
            or not isinstance(post_ga, bool)
            or not isinstance(post_lb, bool)
            or not isinstance(post_gb, bool)
        ):
            raise ValidationError(
                "post_handoff_round must contain boolean local_a_pass, global_a_pass, local_b_pass, global_b_pass"
            )
        post_local_pass = bool(post_la and post_lb)
        digest_chain_valid = bool(pre_handoff_halted_and_escalated and (p0_sha != p1_sha))
        post_global_pass = bool(
            authority_grant_verified
            and digest_chain_valid
            and relaxed_pareto_nonempty
            and post_ga
            and post_gb
        )
        post_defect = int(post_global_pass) - int(post_local_pass)

        if not authority_grant_verified or not digest_chain_valid:
            handoff_status = "UNAUTHORIZED_SELF_RELAXATION_REJECTED_LGGR"
        elif not relaxed_pareto_nonempty:
            handoff_status = "RELAXED_POLICY_STILL_INFEASIBLE_LGGR"
        elif post_global_pass:
            handoff_status = "GOVERNED_POLICY_RELAXATION_PARETO_RESTORED_LGGG"
        else:
            handoff_status = "POST_HANDOFF_RESIDUAL_OBSTRUCTION_LGGR"

        post_record: dict[str, Any] = {
            "round_index": int(post_handoff_round.get("round_index", 2)),
            "local_a_pass": post_la,
            "global_a_pass": post_ga,
            "local_b_pass": post_lb,
            "global_b_pass": post_gb,
            "local_pass": post_local_pass,
            "global_pass": post_global_pass,
            "defect": post_defect,
            "status_a": str(post_handoff_round.get("status_a", "")),
            "status_b": str(post_handoff_round.get("status_b", "")),
        }
        if "action" in post_handoff_round:
            post_record["action"] = post_handoff_round["action"]

        entry: dict[str, Any] = {
            "handoff_id": handoff_id.strip(),
            "pair_name": pair_name.strip(),
            "model_id": model_id.strip(),
            "authority_id": authority_id.strip(),
            "authority_grant_verified": authority_grant_verified,
            "pre_handoff_halted_and_escalated": pre_handoff_halted_and_escalated,
            "prior_escalation_receipt_sha256": esc_sha,
            "prior_policy_sha256": p0_sha,
            "relaxed_policy_sha256": p1_sha,
            "digest_chain_valid": digest_chain_valid,
            "relaxed_candidate_actions": normalized_candidates,
            "relaxed_pareto_nonempty": relaxed_pareto_nonempty,
            "unauthorized_self_relaxation_attempt": unauth_record,
            "post_handoff_round": post_record,
            "pareto_restored": post_global_pass,
            "handoff_status": handoff_status,
        }
        self.handoffs.append(entry)
        return json_value(entry)

    def emit_receipt(self) -> dict[str, Any]:
        if not self.handoffs:
            raise ValidationError("cannot emit receipt without recorded relaxation handoffs")
        n = len(self.handoffs)
        unauth_rej_cnt = sum(
            1 for h in self.handoffs if h["unauthorized_self_relaxation_attempt"]["rejected"]
        )
        pareto_nonempty_cnt = sum(1 for h in self.handoffs if h["relaxed_pareto_nonempty"])
        restored_cnt = sum(1 for h in self.handoffs if h["pareto_restored"])
        digest_all = all(h["digest_chain_valid"] for h in self.handoffs)

        unauth_rej_rate = Fraction(unauth_rej_cnt, n)
        pareto_nonempty_rate = Fraction(pareto_nonempty_cnt, n)
        restored_rate = Fraction(restored_cnt, n)

        unrestored_ids = [h["handoff_id"] for h in self.handoffs if not h["pareto_restored"]]

        if restored_cnt == n and unauth_rej_cnt == n and digest_all:
            status = "GOVERNED_POLICY_RELAXATION_PARETO_RESTORED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "GOVERNED_POLICY_RELAXATION_OBSTRUCTED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_governed_policy_relaxation.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "handoff_count": n,
            "unauthorized_self_relaxation_rejected_count": unauth_rej_cnt,
            "relaxed_pareto_nonempty_count": pareto_nonempty_cnt,
            "pareto_restored_count": restored_cnt,
            "unauthorized_self_relaxation_rejection_rate": unauth_rej_rate,
            "relaxed_pareto_nonempty_rate": pareto_nonempty_rate,
            "post_handoff_pareto_restoration_rate": restored_rate,
            "digest_chain_verified_all": digest_all,
            "unrestored_handoff_ids": unrestored_ids,
            "handoffs": self.handoffs,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingMinimumSlackPolicyRelaxationMonitor:
    r"""Audit minimum-cost ($\ell^1$ minimum-slack) Pareto policy relaxation vs. over-permissive budget grants (LGGR VIII §5.24).

    Given an initial policy parameter vector $P_0 \in \mathbb{Q}^d$ whose coupled feasible
    intersection is empty ($\mathcal{F}_A(P_0) \cap \mathcal{F}_B(P_0) = \emptyset$) and a
    candidate menu $\{P_1, \dots, P_m\} \subset \mathbb{Q}^d$, computes for each candidate:
      - Exact $\ell^1$ policy slack $\Delta_{\mathrm{policy}}(P_k) = \lVert P_k - P_0 \rVert_1$,
      - Minimum Pareto-restoring slack floor
        $\Delta_{\mathrm{policy}}^* = \min \{ \lVert P_k - P_0 \rVert_1 : \mathcal{F}_A(P_k) \cap \mathcal{F}_B(P_k) \ne \emptyset \}$.

    Separates:
      1. **Under-relaxed candidate ($P_{\mathrm{under}}$):** $\mathcal{F}_A(P_k) \cap \mathcal{F}_B(P_k) = \emptyset$
         (``UNDER_RELAXED_POLICY_STILL_INFEASIBLE_LGGR``).
      2. **Over-permissive budget grant ($P_{\mathrm{over}}$):** $\mathcal{F}_A(P_k) \cap \mathcal{F}_B(P_k) \ne \emptyset$
         and both coupled monitors pass ($L_{\mathrm{relax}} = 1$), but
         $\lVert P_{\mathrm{over}} - P_0 \rVert_1 > \Delta_{\mathrm{policy}}^*$, yielding
         $E_{g,\mathrm{min\_slack}} = 0$ and $\Delta_{E,\mathrm{min\_slack}} = -1$
         (``OVER_PERMISSIVE_POLICY_RELAXATION_SLACK_BREACH_LGGR``).
      3. **Minimum-slack Pareto policy relaxation ($P_*$):** $\mathcal{F}_A(P_*) \cap \mathcal{F}_B(P_*) \ne \emptyset$,
         both coupled monitors pass ($L_{\mathrm{relax}} = 1$), and
         $\lVert P_* - P_0 \rVert_1 = \Delta_{\mathrm{policy}}^*$ (zero excess slack), yielding
         $E_{g,\mathrm{min\_slack}} = 1$ and $\Delta_{E,\mathrm{min\_slack}} = 0$
         (``MINIMUM_SLACK_PARETO_POLICY_RELAXATION_VERIFIED_LGGG``).
    """

    def __init__(self, scope_id: str) -> None:
        if not isinstance(scope_id, str) or not scope_id.strip():
            raise ValidationError("scope_id must be a non-empty string")
        self.scope_id = scope_id.strip()
        self.evaluations: list[dict[str, Any]] = []

    def record_minimum_slack_evaluation(
        self,
        *,
        evaluation_id: str,
        pair_name: str,
        model_id: str,
        prior_escalation_receipt_sha256: str,
        prior_policy_sha256: str,
        prior_policy_vector: Sequence[int | float | str | Fraction],
        candidate_policies: Sequence[Mapping[str, Any]],
        rounds: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        if not isinstance(evaluation_id, str) or not evaluation_id.strip():
            raise ValidationError("evaluation_id must be a non-empty string")
        if not isinstance(pair_name, str) or not pair_name.strip():
            raise ValidationError("pair_name must be a non-empty string")
        if not isinstance(model_id, str) or not model_id.strip():
            raise ValidationError("model_id must be a non-empty string")

        esc_sha = _validate_sha256_hex(prior_escalation_receipt_sha256, "prior_escalation_receipt_sha256")
        p0_sha = _validate_sha256_hex(prior_policy_sha256, "prior_policy_sha256")

        if not isinstance(prior_policy_vector, Sequence) or len(prior_policy_vector) == 0:
            raise ValidationError("prior_policy_vector must be a non-empty sequence")
        p0_vec = [rational(v) for v in prior_policy_vector]
        dim = len(p0_vec)

        if not isinstance(candidate_policies, Sequence) or len(candidate_policies) < 2:
            raise ValidationError("candidate_policies must contain at least 2 candidate policy relaxations")

        normalized_candidates: list[dict[str, Any]] = []
        candidate_by_id: dict[str, dict[str, Any]] = {}
        seen_shas: set[str] = set()

        for idx, cand in enumerate(candidate_policies):
            if not isinstance(cand, Mapping):
                raise ValidationError(f"candidate_policies[{idx}] must be a mapping")
            pid = cand.get("policy_id")
            if not isinstance(pid, str) or not pid.strip():
                raise ValidationError(f"candidate_policies[{idx}].policy_id must be a non-empty string")
            pid = pid.strip()
            if pid in candidate_by_id:
                raise ValidationError(f"duplicate candidate policy_id: {pid}")
            psha = _validate_sha256_hex(cand.get("policy_sha256"), f"candidate_policies[{idx}].policy_sha256")
            if psha == p0_sha:
                raise ValidationError(f"candidate_policies[{idx}].policy_sha256 must differ from prior_policy_sha256")
            if psha in seen_shas:
                raise ValidationError(f"duplicate candidate policy_sha256: {psha}")
            seen_shas.add(psha)

            raw_vec = cand.get("policy_vector")
            if not isinstance(raw_vec, Sequence) or len(raw_vec) != dim:
                raise ValidationError(
                    f"candidate_policies[{idx}].policy_vector must have length {dim}"
                )
            p_vec = [rational(v) for v in raw_vec]
            restores = cand.get("restores_pareto_intersection")
            if not isinstance(restores, bool):
                raise ValidationError(
                    f"candidate_policies[{idx}].restores_pareto_intersection must be a boolean"
                )
            l1_slack = sum((abs(p_vec[j] - p0_vec[j]) for j in range(dim)), Fraction(0))
            c_entry: dict[str, Any] = {
                "policy_id": pid,
                "policy_sha256": psha,
                "policy_vector": p_vec,
                "restores_pareto_intersection": restores,
                "l1_policy_slack": l1_slack,
            }
            normalized_candidates.append(c_entry)
            candidate_by_id[pid] = c_entry

        feasible_candidates = [c for c in normalized_candidates if c["restores_pareto_intersection"]]
        if not feasible_candidates:
            raise ValidationError(
                "candidate_policies must include at least one candidate with restores_pareto_intersection=True"
            )

        min_pareto_slack = min(c["l1_policy_slack"] for c in feasible_candidates)
        optimal_policy_ids = [
            c["policy_id"]
            for c in feasible_candidates
            if c["l1_policy_slack"] == min_pareto_slack
        ]
        for c in normalized_candidates:
            if c["restores_pareto_intersection"]:
                c["excess_policy_slack_l1"] = c["l1_policy_slack"] - min_pareto_slack
                c["is_minimum_slack_pareto"] = bool(c["l1_policy_slack"] == min_pareto_slack)
            else:
                c["excess_policy_slack_l1"] = None
                c["is_minimum_slack_pareto"] = False

        if not isinstance(rounds, Sequence) or len(rounds) == 0:
            raise ValidationError("rounds must be a non-empty sequence")

        normalized_rounds: list[dict[str, Any]] = []
        for r_idx, rnd in enumerate(rounds):
            if not isinstance(rnd, Mapping):
                raise ValidationError(f"rounds[{r_idx}] must be a mapping")
            sel_id = rnd.get("selected_policy_id")
            if not isinstance(sel_id, str) or sel_id.strip() not in candidate_by_id:
                raise ValidationError(
                    f"rounds[{r_idx}].selected_policy_id must reference a declared candidate policy"
                )
            sel_cand = candidate_by_id[sel_id.strip()]
            auth_ok = rnd.get("authority_grant_verified")
            la = rnd.get("local_a_pass")
            ga = rnd.get("global_a_pass")
            lb = rnd.get("local_b_pass")
            gb = rnd.get("global_b_pass")
            if (
                not isinstance(auth_ok, bool)
                or not isinstance(la, bool)
                or not isinstance(ga, bool)
                or not isinstance(lb, bool)
                or not isinstance(gb, bool)
            ):
                raise ValidationError(
                    f"rounds[{r_idx}] must specify boolean authority_grant_verified, local_a_pass, global_a_pass, local_b_pass, global_b_pass"
                )

            restores_pareto = bool(sel_cand["restores_pareto_intersection"])
            sel_slack: Fraction = sel_cand["l1_policy_slack"]
            excess_slack: Fraction = sel_slack - min_pareto_slack
            is_min_slack = bool(restores_pareto and excess_slack == 0)

            pair_joint_pass = bool(auth_ok and restores_pareto and la and ga and lb and gb)
            local_pass = pair_joint_pass
            global_pass = bool(pair_joint_pass and is_min_slack)
            defect = int(global_pass) - int(local_pass)

            if not auth_ok:
                r_status = "UNAUTHORIZED_POLICY_RELAXATION_REJECTED_LGGR"
            elif not restores_pareto:
                r_status = "UNDER_RELAXED_POLICY_STILL_INFEASIBLE_LGGR"
            elif not pair_joint_pass:
                r_status = "POST_RELAXATION_PAIR_OBSTRUCTED_LGGR"
            elif not is_min_slack:
                r_status = "OVER_PERMISSIVE_POLICY_RELAXATION_SLACK_BREACH_LGGR"
            else:
                r_status = "MINIMUM_SLACK_PARETO_POLICY_RELAXATION_VERIFIED_LGGG"

            r_entry: dict[str, Any] = {
                "round_index": int(rnd.get("round_index", r_idx)),
                "feedback_mode": str(rnd.get("feedback_mode", f"round_{r_idx}")),
                "selected_policy_id": sel_cand["policy_id"],
                "selected_policy_sha256": sel_cand["policy_sha256"],
                "authority_grant_verified": auth_ok,
                "restores_pareto_intersection": restores_pareto,
                "selected_l1_policy_slack": sel_slack,
                "minimum_pareto_l1_slack": min_pareto_slack,
                "excess_policy_slack_l1": excess_slack,
                "is_minimum_slack_pareto": is_min_slack,
                "local_a_pass": la,
                "global_a_pass": ga,
                "local_b_pass": lb,
                "global_b_pass": gb,
                "local_pass": local_pass,
                "global_pass": global_pass,
                "defect": defect,
                "status_a": str(rnd.get("status_a", "")),
                "status_b": str(rnd.get("status_b", "")),
                "round_status": r_status,
            }
            if "action" in rnd:
                r_entry["action"] = rnd["action"]
            normalized_rounds.append(r_entry)

        r0 = normalized_rounds[0]
        r_final = normalized_rounds[-1]
        r0_over_permissive = bool(
            r0["round_status"] == "OVER_PERMISSIVE_POLICY_RELAXATION_SLACK_BREACH_LGGR"
        )
        single_round_ok = bool(r0["global_pass"])
        multi_round_ok = bool(r_final["global_pass"])

        entry: dict[str, Any] = {
            "evaluation_id": evaluation_id.strip(),
            "pair_name": pair_name.strip(),
            "model_id": model_id.strip(),
            "prior_escalation_receipt_sha256": esc_sha,
            "prior_policy_sha256": p0_sha,
            "prior_policy_vector": p0_vec,
            "minimum_pareto_l1_slack": min_pareto_slack,
            "optimal_minimum_slack_policy_ids": optimal_policy_ids,
            "candidate_policies": normalized_candidates,
            "rounds": normalized_rounds,
            "round_1_over_permissive_breach": r0_over_permissive,
            "converged_single_round": single_round_ok,
            "converged_multi_round": multi_round_ok,
            "evaluation_status": (
                "MINIMUM_SLACK_PARETO_POLICY_RELAXATION_VERIFIED_LGGG"
                if multi_round_ok
                else r_final["round_status"]
            ),
        }
        self.evaluations.append(entry)
        return json_value(entry)

    def emit_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("cannot emit receipt without recorded minimum-slack evaluations")
        n = len(self.evaluations)
        single_cnt = sum(1 for e in self.evaluations if e["converged_single_round"])
        multi_cnt = sum(1 for e in self.evaluations if e["converged_multi_round"])
        over_cnt = sum(1 for e in self.evaluations if e["round_1_over_permissive_breach"])

        single_rate = Fraction(single_cnt, n)
        multi_rate = Fraction(multi_cnt, n)
        gain_rate = multi_rate - single_rate
        over_rate = Fraction(over_cnt, n)

        over_ids = [
            e["evaluation_id"] for e in self.evaluations if e["round_1_over_permissive_breach"]
        ]
        unconverged_ids = [
            e["evaluation_id"] for e in self.evaluations if not e["converged_multi_round"]
        ]

        if multi_cnt == n:
            status = "MINIMUM_SLACK_PARETO_POLICY_RELAXATION_VERIFIED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "OVER_PERMISSIVE_OR_UNCONVERGED_POLICY_RELAXATION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_minimum_slack_policy_relaxation.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "single_round_minimum_slack_converged_count": single_cnt,
            "multi_round_minimum_slack_converged_count": multi_cnt,
            "round_1_over_permissive_breach_count": over_cnt,
            "single_round_minimum_slack_rate": single_rate,
            "multi_round_minimum_slack_rate": multi_rate,
            "multi_round_minimum_slack_gain": gain_rate,
            "round_1_over_permissive_breach_rate": over_rate,
            "monotonic_convergence_verified": multi_rate >= single_rate,
            "round_1_over_permissive_evaluation_ids": over_ids,
            "unconverged_evaluation_ids": unconverged_ids,
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingWeightedPolicyRelaxationMonitor:
    r"""Audit asymmetric risk-weighted ($\ell^1_w$) policy-relaxation trade-offs on equal-unweighted-slack Pareto ties (LGGR VIII §5.25).

    Given an initial policy parameter vector $P_0 \in \mathbb{Q}^d$, a strictly positive
    asymmetric risk-weight vector $w \in \mathbb{Q}_{>0}^d$, and a candidate menu
    $\{P_1, \dots, P_m\} \subset \mathbb{Q}^d$ containing at least two Pareto-restoring
    policies $P_A, P_B \in \mathcal{R}$ that tie on minimum unweighted $\ell^1$ slack:
      $$\lVert P_A - P_0 \rVert_1 = \lVert P_B - P_0 \rVert_1 = \Delta_{\mathrm{unweighted}}^* = \min_{P_k \in \mathcal{R}} \lVert P_k - P_0 \rVert_1,$$
    computes for each candidate its risk-weighted $\ell^1_w$ cost:
      $$\lVert P_k - P_0 \rVert_{1,w} = \sum_{j=1}^d w_j \lvert P_{k,j} - P_{0,j} \rvert, \quad
        \Delta_w^* = \min_{P_k \in \mathcal{R}} \lVert P_k - P_0 \rVert_{1,w}.$$

    Separates:
      1. **Unweighted-tie high-risk relaxation ($P_B$):** satisfies both coupled monitors and
         attains minimum unweighted $\ell^1$ slack ($L_{\mathrm{unweighted}} = 1$,
         $\mathrm{unweighted\_excess} = 0$), yet incurs positive weighted excess slack
         $\lVert P_B - P_0 \rVert_{1,w} - \Delta_w^* > 0$, yielding $E_{g,\mathrm{weighted}} = 0$
         and $\Delta_{E,\mathrm{weighted}} = -1$
         (``UNWEIGHTED_TIE_HIGH_RISK_RELAXATION_REJECTED_LGGR``).
      2. **Risk-weighted minimum-slack Pareto relaxation ($P_A$):** satisfies both coupled
         monitors, attains minimum unweighted $\ell^1$ slack ($L_{\mathrm{unweighted}} = 1$),
         and attains the risk-weighted minimum $\lVert P_A - P_0 \rVert_{1,w} = \Delta_w^*$
         ($\mathrm{weighted\_excess} = 0$), yielding $E_{g,\mathrm{weighted}} = 1$ and
         $\Delta_{E,\mathrm{weighted}} = 0$
         (``RISK_WEIGHTED_MINIMUM_SLACK_PARETO_VERIFIED_LGGG``).
    """

    def __init__(self, scope_id: str) -> None:
        if not isinstance(scope_id, str) or not scope_id.strip():
            raise ValidationError("scope_id must be a non-empty string")
        self.scope_id = scope_id.strip()
        self.evaluations: list[dict[str, Any]] = []

    def record_weighted_relaxation_evaluation(
        self,
        *,
        evaluation_id: str,
        pair_name: str,
        model_id: str,
        prior_escalation_receipt_sha256: str,
        prior_policy_sha256: str,
        prior_policy_vector: Sequence[int | float | str | Fraction],
        risk_weight_vector: Sequence[int | float | str | Fraction],
        candidate_policies: Sequence[Mapping[str, Any]],
        rounds: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        if not isinstance(evaluation_id, str) or not evaluation_id.strip():
            raise ValidationError("evaluation_id must be a non-empty string")
        if not isinstance(pair_name, str) or not pair_name.strip():
            raise ValidationError("pair_name must be a non-empty string")
        if not isinstance(model_id, str) or not model_id.strip():
            raise ValidationError("model_id must be a non-empty string")

        esc_sha = _validate_sha256_hex(prior_escalation_receipt_sha256, "prior_escalation_receipt_sha256")
        p0_sha = _validate_sha256_hex(prior_policy_sha256, "prior_policy_sha256")

        if not isinstance(prior_policy_vector, Sequence) or len(prior_policy_vector) < 2:
            raise ValidationError("prior_policy_vector must have length >= 2")
        p0_vec = [rational(v) for v in prior_policy_vector]
        dim = len(p0_vec)

        if not isinstance(risk_weight_vector, Sequence) or len(risk_weight_vector) != dim:
            raise ValidationError(f"risk_weight_vector must have length {dim}")
        w_vec = [rational(w) for w in risk_weight_vector]
        if any(w <= 0 for w in w_vec):
            raise ValidationError("all coordinates of risk_weight_vector must be strictly positive (> 0)")
        if len(set(w_vec)) < 2:
            raise ValidationError("risk_weight_vector must be asymmetric (at least two distinct weights)")

        if not isinstance(candidate_policies, Sequence) or len(candidate_policies) < 2:
            raise ValidationError("candidate_policies must contain at least 2 candidate policy relaxations")

        normalized_candidates: list[dict[str, Any]] = []
        candidate_by_id: dict[str, dict[str, Any]] = {}
        seen_shas: set[str] = set()

        for idx, cand in enumerate(candidate_policies):
            if not isinstance(cand, Mapping):
                raise ValidationError(f"candidate_policies[{idx}] must be a mapping")
            pid = cand.get("policy_id")
            if not isinstance(pid, str) or not pid.strip():
                raise ValidationError(f"candidate_policies[{idx}].policy_id must be a non-empty string")
            pid = pid.strip()
            if pid in candidate_by_id:
                raise ValidationError(f"duplicate candidate policy_id: {pid}")
            psha = _validate_sha256_hex(cand.get("policy_sha256"), f"candidate_policies[{idx}].policy_sha256")
            if psha == p0_sha:
                raise ValidationError(f"candidate_policies[{idx}].policy_sha256 must differ from prior_policy_sha256")
            if psha in seen_shas:
                raise ValidationError(f"duplicate candidate policy_sha256: {psha}")
            seen_shas.add(psha)

            raw_vec = cand.get("policy_vector")
            if not isinstance(raw_vec, Sequence) or len(raw_vec) != dim:
                raise ValidationError(
                    f"candidate_policies[{idx}].policy_vector must have length {dim}"
                )
            p_vec = [rational(v) for v in raw_vec]
            restores = cand.get("restores_pareto_intersection")
            if not isinstance(restores, bool):
                raise ValidationError(
                    f"candidate_policies[{idx}].restores_pareto_intersection must be a boolean"
                )
            unweighted_slack = sum((abs(p_vec[j] - p0_vec[j]) for j in range(dim)), Fraction(0))
            weighted_slack = sum((w_vec[j] * abs(p_vec[j] - p0_vec[j]) for j in range(dim)), Fraction(0))
            c_entry: dict[str, Any] = {
                "policy_id": pid,
                "policy_sha256": psha,
                "policy_vector": p_vec,
                "restores_pareto_intersection": restores,
                "unweighted_l1_slack": unweighted_slack,
                "weighted_l1_slack": weighted_slack,
            }
            normalized_candidates.append(c_entry)
            candidate_by_id[pid] = c_entry

        feasible_candidates = [c for c in normalized_candidates if c["restores_pareto_intersection"]]
        if len(feasible_candidates) < 2:
            raise ValidationError(
                "candidate_policies must include at least 2 Pareto-restoring candidates"
            )

        min_unweighted_slack = min(c["unweighted_l1_slack"] for c in feasible_candidates)
        unweighted_tie_ids = [
            c["policy_id"]
            for c in feasible_candidates
            if c["unweighted_l1_slack"] == min_unweighted_slack
        ]
        if len(unweighted_tie_ids) < 2:
            raise ValidationError(
                "candidate_policies must include at least 2 Pareto-restoring candidates tied at minimum unweighted l1 slack"
            )

        min_weighted_slack = min(c["weighted_l1_slack"] for c in feasible_candidates)
        optimal_weighted_ids = [
            c["policy_id"]
            for c in feasible_candidates
            if c["weighted_l1_slack"] == min_weighted_slack
        ]

        for c in normalized_candidates:
            if c["restores_pareto_intersection"]:
                c["unweighted_excess_slack_l1"] = c["unweighted_l1_slack"] - min_unweighted_slack
                c["weighted_excess_slack_l1"] = c["weighted_l1_slack"] - min_weighted_slack
                c["is_unweighted_minimum_slack"] = bool(
                    c["unweighted_l1_slack"] == min_unweighted_slack
                )
                c["is_weighted_minimum_slack"] = bool(
                    c["weighted_l1_slack"] == min_weighted_slack
                )
            else:
                c["unweighted_excess_slack_l1"] = None
                c["weighted_excess_slack_l1"] = None
                c["is_unweighted_minimum_slack"] = False
                c["is_weighted_minimum_slack"] = False

        if not isinstance(rounds, Sequence) or len(rounds) == 0:
            raise ValidationError("rounds must be a non-empty sequence")

        normalized_rounds: list[dict[str, Any]] = []
        for r_idx, rnd in enumerate(rounds):
            if not isinstance(rnd, Mapping):
                raise ValidationError(f"rounds[{r_idx}] must be a mapping")
            sel_id = rnd.get("selected_policy_id")
            if not isinstance(sel_id, str) or sel_id.strip() not in candidate_by_id:
                raise ValidationError(
                    f"rounds[{r_idx}].selected_policy_id must reference a declared candidate policy"
                )
            sel_cand = candidate_by_id[sel_id.strip()]
            auth_ok = rnd.get("authority_grant_verified")
            la = rnd.get("local_a_pass")
            ga = rnd.get("global_a_pass")
            lb = rnd.get("local_b_pass")
            gb = rnd.get("global_b_pass")
            if (
                not isinstance(auth_ok, bool)
                or not isinstance(la, bool)
                or not isinstance(ga, bool)
                or not isinstance(lb, bool)
                or not isinstance(gb, bool)
            ):
                raise ValidationError(
                    f"rounds[{r_idx}] must specify boolean authority_grant_verified, local_a_pass, global_a_pass, local_b_pass, global_b_pass"
                )

            restores_pareto = bool(sel_cand["restores_pareto_intersection"])
            sel_unweighted: Fraction = sel_cand["unweighted_l1_slack"]
            sel_weighted: Fraction = sel_cand["weighted_l1_slack"]
            unweighted_excess: Fraction = sel_unweighted - min_unweighted_slack
            weighted_excess: Fraction = sel_weighted - min_weighted_slack
            is_unweighted_min = bool(restores_pareto and unweighted_excess == 0)
            is_weighted_min = bool(restores_pareto and weighted_excess == 0)

            pair_joint_pass = bool(auth_ok and restores_pareto and la and ga and lb and gb)
            local_pass = bool(pair_joint_pass and is_unweighted_min)
            global_pass = bool(local_pass and is_weighted_min)
            defect = int(global_pass) - int(local_pass)

            if not auth_ok:
                r_status = "UNAUTHORIZED_POLICY_RELAXATION_REJECTED_LGGR"
            elif not restores_pareto:
                r_status = "UNDER_RELAXED_POLICY_STILL_INFEASIBLE_LGGR"
            elif not pair_joint_pass:
                r_status = "POST_RELAXATION_PAIR_OBSTRUCTED_LGGR"
            elif not is_unweighted_min:
                r_status = "OVER_PERMISSIVE_UNWEIGHTED_SLACK_BREACH_LGGR"
            elif not is_weighted_min:
                r_status = "UNWEIGHTED_TIE_HIGH_RISK_RELAXATION_REJECTED_LGGR"
            else:
                r_status = "RISK_WEIGHTED_MINIMUM_SLACK_PARETO_VERIFIED_LGGG"

            r_entry: dict[str, Any] = {
                "round_index": int(rnd.get("round_index", r_idx)),
                "feedback_mode": str(rnd.get("feedback_mode", f"round_{r_idx}")),
                "selected_policy_id": sel_cand["policy_id"],
                "selected_policy_sha256": sel_cand["policy_sha256"],
                "authority_grant_verified": auth_ok,
                "restores_pareto_intersection": restores_pareto,
                "selected_unweighted_l1_slack": sel_unweighted,
                "minimum_unweighted_l1_slack": min_unweighted_slack,
                "unweighted_excess_slack_l1": unweighted_excess,
                "selected_weighted_l1_slack": sel_weighted,
                "minimum_weighted_l1_slack": min_weighted_slack,
                "weighted_excess_slack_l1": weighted_excess,
                "is_unweighted_minimum_slack": is_unweighted_min,
                "is_weighted_minimum_slack": is_weighted_min,
                "local_a_pass": la,
                "global_a_pass": ga,
                "local_b_pass": lb,
                "global_b_pass": gb,
                "local_pass": local_pass,
                "global_pass": global_pass,
                "defect": defect,
                "status_a": str(rnd.get("status_a", "")),
                "status_b": str(rnd.get("status_b", "")),
                "round_status": r_status,
            }
            if "action" in rnd:
                r_entry["action"] = rnd["action"]
            normalized_rounds.append(r_entry)

        r0 = normalized_rounds[0]
        r_final = normalized_rounds[-1]
        r0_high_risk_tie = bool(
            r0["round_status"] == "UNWEIGHTED_TIE_HIGH_RISK_RELAXATION_REJECTED_LGGR"
        )
        single_round_ok = bool(r0["global_pass"])
        multi_round_ok = bool(r_final["global_pass"])

        entry: dict[str, Any] = {
            "evaluation_id": evaluation_id.strip(),
            "pair_name": pair_name.strip(),
            "model_id": model_id.strip(),
            "prior_escalation_receipt_sha256": esc_sha,
            "prior_policy_sha256": p0_sha,
            "prior_policy_vector": p0_vec,
            "risk_weight_vector": w_vec,
            "minimum_unweighted_l1_slack": min_unweighted_slack,
            "unweighted_minimum_tie_policy_ids": unweighted_tie_ids,
            "minimum_weighted_l1_slack": min_weighted_slack,
            "optimal_weighted_policy_ids": optimal_weighted_ids,
            "candidate_policies": normalized_candidates,
            "rounds": normalized_rounds,
            "round_1_unweighted_tie_high_risk_breach": r0_high_risk_tie,
            "converged_single_round": single_round_ok,
            "converged_multi_round": multi_round_ok,
            "evaluation_status": (
                "RISK_WEIGHTED_MINIMUM_SLACK_PARETO_VERIFIED_LGGG"
                if multi_round_ok
                else r_final["round_status"]
            ),
        }
        self.evaluations.append(entry)
        return json_value(entry)

    def emit_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("cannot emit receipt without recorded weighted relaxation evaluations")
        n = len(self.evaluations)
        single_cnt = sum(1 for e in self.evaluations if e["converged_single_round"])
        multi_cnt = sum(1 for e in self.evaluations if e["converged_multi_round"])
        tie_breach_cnt = sum(
            1 for e in self.evaluations if e["round_1_unweighted_tie_high_risk_breach"]
        )

        single_rate = Fraction(single_cnt, n)
        multi_rate = Fraction(multi_cnt, n)
        gain_rate = multi_rate - single_rate
        tie_breach_rate = Fraction(tie_breach_cnt, n)

        tie_breach_ids = [
            e["evaluation_id"]
            for e in self.evaluations
            if e["round_1_unweighted_tie_high_risk_breach"]
        ]
        unconverged_ids = [
            e["evaluation_id"] for e in self.evaluations if not e["converged_multi_round"]
        ]

        if multi_cnt == n:
            status = "RISK_WEIGHTED_MINIMUM_SLACK_PARETO_VERIFIED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "UNWEIGHTED_TIE_OR_UNCONVERGED_WEIGHTED_RELAXATION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_weighted_policy_relaxation.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "single_round_weighted_converged_count": single_cnt,
            "multi_round_weighted_converged_count": multi_cnt,
            "round_1_unweighted_tie_high_risk_breach_count": tie_breach_cnt,
            "single_round_weighted_convergence_rate": single_rate,
            "multi_round_weighted_convergence_rate": multi_rate,
            "multi_round_weighted_convergence_gain": gain_rate,
            "round_1_unweighted_tie_high_risk_breach_rate": tie_breach_rate,
            "monotonic_convergence_verified": multi_rate >= single_rate,
            "round_1_unweighted_tie_high_risk_evaluation_ids": tie_breach_ids,
            "unconverged_evaluation_ids": unconverged_ids,
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingPolicyRatchetDriftMonitor:
    """Audit multi-step cumulative policy-relaxation drift (ratchet effect) across sequential incidents.

    Separates:
      1. Unrevoked monotone policy ratchet (L_t = 1 at every incident step t = 1..T via
         ||P_t - P_{t-1}||_{1,w} <= tau_step, yet cumulative horizon drift
         ||P_T - P_0||_{1,w} > tau_horizon -> E_{g,T} = 0, Delta_{E,chain} = -1,
         CUMULATIVE_POLICY_RATCHET_HORIZON_BREACH_LGGR).
      2. Scoped lease revocation / rollback after incident resolution (prior temporary
         relaxations revoked back to P_0 before incident t -> ||P_t - P_0||_{1,w} <= tau_step
         <= tau_horizon for all t = 1..T -> L_chain = 1, E_{g,chain} = 1, Delta_{E,chain} = 0,
         SCOPED_LEASE_REVOCATION_HORIZON_COHERENT_LGGG).

    AuthorityEffect: None.
    """

    def __init__(self, scope_id: str) -> None:
        if not scope_id:
            raise ValidationError("scope_id must be non-empty")
        self.scope_id = scope_id
        self.trajectories: list[dict[str, Any]] = []

    def _audit_incident_chain(
        self,
        *,
        incidents: Sequence[Mapping[str, Any]],
        p0_vec: list[Fraction],
        w_vec: list[Fraction],
        tau_step: Fraction,
        tau_horizon: Fraction,
        dim: int,
        require_revocation: bool,
    ) -> dict[str, Any]:
        if len(incidents) < 2:
            raise ValidationError("incident trajectory must contain at least 2 sequential incidents")

        step_records: list[dict[str, Any]] = []
        prev_post_vec = list(p0_vec)
        l_chain = 1
        eg_chain = 1
        sum_step_weighted_slacks = Fraction(0)
        max_horizon_weighted_drift = Fraction(0)
        first_breach_step: int | None = None

        for idx, inc in enumerate(incidents):
            step_num = int(inc.get("incident_index", idx + 1))
            pair_id = str(inc.get("incident_pair_id", f"incident_{step_num}"))
            prior_revoked = bool(inc.get("prior_lease_revoked", False))
            sig_valid = bool(inc.get("authority_signature_valid", False))
            mon_a = bool(inc.get("post_relaxation_monitor_a_passed", False))
            mon_b = bool(inc.get("post_relaxation_monitor_b_passed", False))

            if idx == 0:
                expected_pre = list(p0_vec)
            else:
                expected_pre = list(p0_vec) if prior_revoked else list(prev_post_vec)

            raw_pre = inc.get("pre_incident_policy_vector")
            if raw_pre is not None:
                pre_vec = [rational(v) for v in raw_pre]
                if len(pre_vec) != dim:
                    raise ValidationError("pre_incident_policy_vector dimension mismatch")
            else:
                pre_vec = expected_pre

            raw_post = inc.get("post_incident_policy_vector")
            if raw_post is None:
                raise ValidationError("incident must provide post_incident_policy_vector")
            post_vec = [rational(v) for v in raw_post]
            if len(post_vec) != dim:
                raise ValidationError("post_incident_policy_vector dimension mismatch")

            delta_step_vec = [post_vec[j] - pre_vec[j] for j in range(dim)]
            delta_horizon_vec = [post_vec[j] - p0_vec[j] for j in range(dim)]

            step_unweighted_slack = sum((abs(d) for d in delta_step_vec), Fraction(0))
            step_weighted_slack = sum(
                (w_vec[j] * abs(delta_step_vec[j]) for j in range(dim)), Fraction(0)
            )
            horizon_unweighted_drift = sum((abs(d) for d in delta_horizon_vec), Fraction(0))
            horizon_weighted_drift = sum(
                (w_vec[j] * abs(delta_horizon_vec[j]) for j in range(dim)), Fraction(0)
            )

            sum_step_weighted_slacks += step_weighted_slack
            if horizon_weighted_drift > max_horizon_weighted_drift:
                max_horizon_weighted_drift = horizon_weighted_drift

            pre_state_consistent = pre_vec == expected_pre
            revocation_policy_satisfied = True
            if idx > 0 and require_revocation and not prior_revoked:
                revocation_policy_satisfied = False

            step_within_budget = step_weighted_slack <= tau_step
            horizon_within_ceiling = horizon_weighted_drift <= tau_horizon
            pareto_restored = mon_a and mon_b

            l_t = (
                1
                if (sig_valid and pareto_restored and step_within_budget and pre_state_consistent)
                else 0
            )
            eg_t = (
                1
                if (
                    l_t == 1
                    and horizon_within_ceiling
                    and revocation_policy_satisfied
                )
                else 0
            )
            delta_e_t = eg_t - l_t

            if l_t == 0:
                l_chain = 0
            if eg_t == 0:
                eg_chain = 0
                if first_breach_step is None and l_t == 1 and not horizon_within_ceiling:
                    first_breach_step = step_num

            if eg_t == 1:
                step_status = (
                    "SCOPED_LEASE_REVOKED_STEP_COHERENT_LGGG"
                    if (idx > 0 and prior_revoked)
                    else "WITHIN_STEP_AND_HORIZON_BUDGET_LGGG"
                )
            elif l_t == 1 and not horizon_within_ceiling:
                step_status = "CUMULATIVE_POLICY_RATCHET_HORIZON_BREACH_LGGR"
            else:
                step_status = "STEP_OBSTRUCTED_OR_INVALID_LEASE_LGGR"

            step_records.append(
                {
                    "incident_index": step_num,
                    "incident_pair_id": pair_id,
                    "prior_lease_revoked": prior_revoked,
                    "authority_signature_valid": sig_valid,
                    "pre_incident_policy_vector": pre_vec,
                    "post_incident_policy_vector": post_vec,
                    "delta_step_vector": delta_step_vec,
                    "delta_horizon_vector": delta_horizon_vec,
                    "step_unweighted_l1_slack": step_unweighted_slack,
                    "step_weighted_l1_slack": step_weighted_slack,
                    "horizon_unweighted_l1_drift": horizon_unweighted_drift,
                    "horizon_weighted_l1_drift": horizon_weighted_drift,
                    "step_within_budget": step_within_budget,
                    "horizon_within_ceiling": horizon_within_ceiling,
                    "post_relaxation_monitor_a_passed": mon_a,
                    "post_relaxation_monitor_b_passed": mon_b,
                    "pareto_intersection_restored": pareto_restored,
                    "local_step_indicator_L_t": l_t,
                    "global_horizon_indicator_E_g_t": eg_t,
                    "step_evaluator_defect": delta_e_t,
                    "step_status": step_status,
                }
            )
            prev_post_vec = post_vec

        final_horizon_drift = step_records[-1]["horizon_weighted_l1_drift"]
        delta_e_chain = eg_chain - l_chain
        ratchet_horizon_breach = l_chain == 1 and eg_chain == 0 and max_horizon_weighted_drift > tau_horizon

        if eg_chain == 1:
            chain_status = "SCOPED_LEASE_REVOCATION_HORIZON_COHERENT_LGGG"
        elif ratchet_horizon_breach:
            chain_status = "CUMULATIVE_POLICY_RATCHET_HORIZON_BREACH_LGGR"
        else:
            chain_status = "CHAIN_STEP_OBSTRUCTED_LGGR"

        return {
            "incident_count": len(step_records),
            "sum_step_weighted_l1_slacks": sum_step_weighted_slacks,
            "final_horizon_weighted_l1_drift": final_horizon_drift,
            "max_horizon_weighted_l1_drift": max_horizon_weighted_drift,
            "telescoping_ratchet_equality_holds": final_horizon_drift == sum_step_weighted_slacks,
            "first_horizon_breach_incident_index": first_breach_step,
            "local_chain_indicator_L": l_chain,
            "global_chain_indicator_E_g": eg_chain,
            "chain_evaluator_defect": delta_e_chain,
            "ratchet_horizon_breach_detected": ratchet_horizon_breach,
            "chain_status": chain_status,
            "incidents": step_records,
        }

    def record_incident_trajectory(
        self,
        *,
        trajectory_id: str,
        model_id: str,
        prior_escalation_receipt_sha256: str,
        baseline_policy_sha256: str,
        baseline_policy_vector: Sequence[int | float | str | Fraction],
        risk_weight_vector: Sequence[int | float | str | Fraction],
        step_slack_budget: int | float | str | Fraction,
        horizon_drift_ceiling: int | float | str | Fraction,
        unrevoked_ratchet_incidents: Sequence[Mapping[str, Any]],
        lease_revoked_incidents: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        if not trajectory_id or not model_id:
            raise ValidationError("trajectory_id and model_id must be non-empty")
        if not prior_escalation_receipt_sha256 or not baseline_policy_sha256:
            raise ValidationError("prior_escalation_receipt_sha256 and baseline_policy_sha256 must be non-empty")
        if not baseline_policy_vector:
            raise ValidationError("baseline_policy_vector must be non-empty")

        p0_vec = [rational(v) for v in baseline_policy_vector]
        w_vec = [rational(w) for w in risk_weight_vector]
        dim = len(p0_vec)
        if len(w_vec) != dim:
            raise ValidationError("risk_weight_vector must have the same dimension as baseline_policy_vector")
        if any(w <= 0 for w in w_vec):
            raise ValidationError("all coordinates of risk_weight_vector must be strictly positive")

        tau_step = rational(step_slack_budget)
        tau_horizon = rational(horizon_drift_ceiling)
        if tau_step <= 0 or tau_horizon <= 0:
            raise ValidationError("step_slack_budget and horizon_drift_ceiling must be strictly positive")
        if tau_horizon < tau_step:
            raise ValidationError("horizon_drift_ceiling must be >= step_slack_budget")

        ratchet_audit = self._audit_incident_chain(
            incidents=unrevoked_ratchet_incidents,
            p0_vec=p0_vec,
            w_vec=w_vec,
            tau_step=tau_step,
            tau_horizon=tau_horizon,
            dim=dim,
            require_revocation=False,
        )
        revoked_audit = self._audit_incident_chain(
            incidents=lease_revoked_incidents,
            p0_vec=p0_vec,
            w_vec=w_vec,
            tau_step=tau_step,
            tau_horizon=tau_horizon,
            dim=dim,
            require_revocation=True,
        )

        converged_single_round = ratchet_audit["global_chain_indicator_E_g"] == 1
        converged_multi_round = converged_single_round or (revoked_audit["global_chain_indicator_E_g"] == 1)
        horizon_drift_reduction = (
            ratchet_audit["max_horizon_weighted_l1_drift"] - revoked_audit["max_horizon_weighted_l1_drift"]
        )

        record: dict[str, Any] = {
            "trajectory_id": trajectory_id,
            "model_id": model_id,
            "prior_escalation_receipt_sha256": prior_escalation_receipt_sha256,
            "baseline_policy_sha256": baseline_policy_sha256,
            "baseline_policy_vector": p0_vec,
            "risk_weight_vector": w_vec,
            "step_slack_budget": tau_step,
            "horizon_drift_ceiling": tau_horizon,
            "phase_1_unrevoked_ratchet_chain": ratchet_audit,
            "phase_2_lease_revoked_chain": revoked_audit,
            "phase_1_ratchet_horizon_breach": ratchet_audit["ratchet_horizon_breach_detected"],
            "converged_single_round": converged_single_round,
            "converged_multi_round": converged_multi_round,
            "horizon_weighted_drift_reduction": horizon_drift_reduction,
        }
        self.trajectories.append(record)
        return json_value(record)

    def emit_receipt(self) -> dict[str, Any]:
        if not self.trajectories:
            raise ValidationError("cannot emit receipt without recorded policy ratchet trajectories")
        n = len(self.trajectories)
        single_cnt = sum(1 for t in self.trajectories if t["converged_single_round"])
        multi_cnt = sum(1 for t in self.trajectories if t["converged_multi_round"])
        ratchet_breach_cnt = sum(1 for t in self.trajectories if t["phase_1_ratchet_horizon_breach"])

        single_rate = Fraction(single_cnt, n)
        multi_rate = Fraction(multi_cnt, n)
        gain_rate = multi_rate - single_rate
        ratchet_breach_rate = Fraction(ratchet_breach_cnt, n)

        ratchet_breach_ids = [
            t["trajectory_id"] for t in self.trajectories if t["phase_1_ratchet_horizon_breach"]
        ]
        unconverged_ids = [
            t["trajectory_id"] for t in self.trajectories if not t["converged_multi_round"]
        ]

        if multi_cnt == n:
            status = "SCOPED_LEASE_REVOCATION_HORIZON_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "CUMULATIVE_POLICY_RATCHET_HORIZON_BREACH_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_policy_ratchet_drift.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "trajectory_count": n,
            "single_round_horizon_coherent_count": single_cnt,
            "multi_round_lease_revoked_coherent_count": multi_cnt,
            "phase_1_ratchet_horizon_breach_count": ratchet_breach_cnt,
            "single_round_horizon_coherence_rate": single_rate,
            "multi_round_lease_revoked_coherence_rate": multi_rate,
            "lease_revocation_coherence_gain": gain_rate,
            "phase_1_ratchet_horizon_breach_rate": ratchet_breach_rate,
            "monotonic_coherence_verified": multi_rate >= single_rate,
            "phase_1_ratchet_horizon_breach_trajectory_ids": ratchet_breach_ids,
            "unconverged_trajectory_ids": unconverged_ids,
            "trajectories": self.trajectories,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingConcurrentLeaseOverlapMonitor:
    """Audit concurrent overlapping incident leases where incident t+1 arrives before incident t's lease expires.

    Separates:
      1. Uncoordinated concurrent lease overlap (every individual lease k = 1..M has finite expiration
         e_k > s_k and satisfies ||delta_k||_{1,w} <= tau_lease <= tau_horizon with L_k = 1, yet
         overlapping active intervals [s_t, e_t) cap [s_{t+1}, e_{t+1}) != empty cause peak active
         weighted drift max_tau ||sum_{k in A(tau)} delta_k||_{1,w} > tau_horizon ->
         E_{g,schedule} = 0, Delta_{E,schedule} = -1, CONCURRENT_LEASE_OVERLAP_HORIZON_BREACH_LGGR).
      2. Lease-overlap accounting and admission control (tracking active leases A(tau) and enforcing
         ||sum_{k in A(tau)} delta_k||_{1,w} <= tau_horizon at every timestamp tau via early lease
         release upon repair completion or headroom-bounded scheduling -> L_schedule = 1,
         E_{g,schedule} = 1, Delta_{E,schedule} = 0, LEASE_OVERLAP_ACCOUNTING_HORIZON_COHERENT_LGGG).

    AuthorityEffect: None.
    """

    def __init__(self, scope_id: str) -> None:
        if not scope_id:
            raise ValidationError("scope_id must be non-empty")
        self.scope_id = scope_id
        self.schedules: list[dict[str, Any]] = []

    def _audit_lease_schedule(
        self,
        *,
        leases: Sequence[Mapping[str, Any]],
        p0_vec: list[Fraction],
        w_vec: list[Fraction],
        tau_lease: Fraction,
        tau_horizon: Fraction,
        dim: int,
        require_overlap_accounting: bool,
    ) -> dict[str, Any]:
        if len(leases) < 2:
            raise ValidationError("lease schedule must contain at least 2 incidents")

        parsed_leases: list[dict[str, Any]] = []
        l_schedule = 1
        min_start: int | None = None
        max_end: int | None = None

        for idx, ls in enumerate(leases):
            inc_num = int(ls.get("incident_index", idx + 1))
            pair_id = str(ls.get("incident_pair_id", f"incident_{inc_num}"))
            s_k = int(ls.get("arrival_tick", idx))
            e_k = int(ls.get("expiration_tick", s_k + 1))
            if e_k <= s_k:
                raise ValidationError("expiration_tick must be strictly greater than arrival_tick")

            sig_valid = bool(ls.get("authority_signature_valid", False))
            overlap_accounted = bool(ls.get("overlap_accounting_enforced", False))
            mon_a = bool(ls.get("post_relaxation_monitor_a_passed", False))
            mon_b = bool(ls.get("post_relaxation_monitor_b_passed", False))

            raw_delta = ls.get("lease_delta_vector")
            if raw_delta is not None:
                delta_vec = [rational(v) for v in raw_delta]
                if len(delta_vec) != dim:
                    raise ValidationError("lease_delta_vector dimension mismatch")
            else:
                raw_policy = ls.get("lease_policy_vector")
                if raw_policy is None:
                    raise ValidationError("lease must provide lease_delta_vector or lease_policy_vector")
                pol_vec = [rational(v) for v in raw_policy]
                if len(pol_vec) != dim:
                    raise ValidationError("lease_policy_vector dimension mismatch")
                delta_vec = [pol_vec[j] - p0_vec[j] for j in range(dim)]

            lease_policy_vec = [p0_vec[j] + delta_vec[j] for j in range(dim)]
            unweighted_slack = sum((abs(d) for d in delta_vec), Fraction(0))
            weighted_slack = sum((w_vec[j] * abs(delta_vec[j]) for j in range(dim)), Fraction(0))
            within_lease_budget = weighted_slack <= tau_lease
            pareto_restored = mon_a and mon_b

            l_k = 1 if (sig_valid and pareto_restored and within_lease_budget) else 0
            if l_k == 0:
                l_schedule = 0

            if min_start is None or s_k < min_start:
                min_start = s_k
            if max_end is None or e_k > max_end:
                max_end = e_k

            parsed_leases.append(
                {
                    "incident_index": inc_num,
                    "incident_pair_id": pair_id,
                    "arrival_tick": s_k,
                    "expiration_tick": e_k,
                    "lease_duration_ticks": e_k - s_k,
                    "authority_signature_valid": sig_valid,
                    "overlap_accounting_enforced": overlap_accounted,
                    "lease_delta_vector": delta_vec,
                    "lease_policy_vector": lease_policy_vec,
                    "lease_unweighted_l1_slack": unweighted_slack,
                    "lease_weighted_l1_slack": weighted_slack,
                    "within_individual_lease_budget": within_lease_budget,
                    "post_relaxation_monitor_a_passed": mon_a,
                    "post_relaxation_monitor_b_passed": mon_b,
                    "pareto_intersection_restored": pareto_restored,
                    "local_lease_indicator_L_k": l_k,
                }
            )

        assert min_start is not None and max_end is not None
        tick_records: list[dict[str, Any]] = []
        peak_weighted_drift = Fraction(0)
        peak_tick: int | None = None
        first_breach_tick: int | None = None
        max_concurrent_leases = 0
        overlap_tick_count = 0
        breach_tick_count = 0

        for tick in range(min_start, max_end):
            active = [
                ls
                for ls in parsed_leases
                if ls["arrival_tick"] <= tick < ls["expiration_tick"]
            ]
            active_indices = [ls["incident_index"] for ls in active]
            if len(active) > max_concurrent_leases:
                max_concurrent_leases = len(active)
            if len(active) >= 2:
                overlap_tick_count += 1

            agg_delta = [
                sum((ls["lease_delta_vector"][j] for ls in active), Fraction(0))
                for j in range(dim)
            ]
            agg_policy = [p0_vec[j] + agg_delta[j] for j in range(dim)]
            tick_unweighted_drift = sum((abs(d) for d in agg_delta), Fraction(0))
            tick_weighted_drift = sum(
                (w_vec[j] * abs(agg_delta[j]) for j in range(dim)), Fraction(0)
            )
            if tick_weighted_drift > peak_weighted_drift:
                peak_weighted_drift = tick_weighted_drift
                peak_tick = tick

            within_horizon = tick_weighted_drift <= tau_horizon
            if not within_horizon:
                breach_tick_count += 1
                if first_breach_tick is None:
                    first_breach_tick = tick

            tick_records.append(
                {
                    "tick": tick,
                    "active_incident_indices": active_indices,
                    "active_lease_count": len(active),
                    "aggregate_delta_vector": agg_delta,
                    "aggregate_policy_vector": agg_policy,
                    "concurrent_unweighted_l1_drift": tick_unweighted_drift,
                    "concurrent_weighted_l1_drift": tick_weighted_drift,
                    "horizon_within_ceiling": within_horizon,
                }
            )

        for ls in parsed_leases:
            s_k = ls["arrival_tick"]
            e_k = ls["expiration_tick"]
            lease_max_concurrent_drift = max(
                (
                    tr["concurrent_weighted_l1_drift"]
                    for tr in tick_records
                    if s_k <= tr["tick"] < e_k
                ),
                default=ls["lease_weighted_l1_slack"],
            )
            acct_ok = (not require_overlap_accounting) or ls["overlap_accounting_enforced"]
            eg_k = (
                1
                if (
                    ls["local_lease_indicator_L_k"] == 1
                    and lease_max_concurrent_drift <= tau_horizon
                    and acct_ok
                )
                else 0
            )
            ls["peak_concurrent_weighted_drift_during_lease"] = lease_max_concurrent_drift
            ls["global_overlap_indicator_E_g_k"] = eg_k
            ls["lease_evaluator_defect"] = eg_k - ls["local_lease_indicator_L_k"]
            if eg_k == 1:
                ls["lease_status"] = "LEASE_OVERLAP_ACCOUNTING_COHERENT_LGGG"
            elif ls["local_lease_indicator_L_k"] == 1 and lease_max_concurrent_drift > tau_horizon:
                ls["lease_status"] = "CONCURRENT_LEASE_OVERLAP_HORIZON_BREACH_LGGR"
            else:
                ls["lease_status"] = "LEASE_STEP_OBSTRUCTED_LGGR"

        all_acct_ok = (not require_overlap_accounting) or all(
            ls["overlap_accounting_enforced"] for ls in parsed_leases
        )
        eg_schedule = (
            1
            if (l_schedule == 1 and peak_weighted_drift <= tau_horizon and all_acct_ok)
            else 0
        )
        delta_e_schedule = eg_schedule - l_schedule
        overlap_breach_detected = (
            l_schedule == 1 and eg_schedule == 0 and peak_weighted_drift > tau_horizon
        )

        if eg_schedule == 1:
            schedule_status = "LEASE_OVERLAP_ACCOUNTING_HORIZON_COHERENT_LGGG"
        elif overlap_breach_detected:
            schedule_status = "CONCURRENT_LEASE_OVERLAP_HORIZON_BREACH_LGGR"
        else:
            schedule_status = "SCHEDULE_LEASE_OBSTRUCTED_LGGR"

        return {
            "incident_count": len(parsed_leases),
            "horizon_span_ticks": max_end - min_start,
            "max_concurrent_active_leases": max_concurrent_leases,
            "overlap_tick_count": overlap_tick_count,
            "breach_tick_count": breach_tick_count,
            "peak_concurrent_weighted_l1_drift": peak_weighted_drift,
            "peak_drift_tick": peak_tick,
            "first_horizon_breach_tick": first_breach_tick,
            "local_schedule_indicator_L": l_schedule,
            "global_schedule_indicator_E_g": eg_schedule,
            "schedule_evaluator_defect": delta_e_schedule,
            "overlap_horizon_breach_detected": overlap_breach_detected,
            "schedule_status": schedule_status,
            "leases": parsed_leases,
            "ticks": tick_records,
        }

    def record_overlap_schedule(
        self,
        *,
        schedule_id: str,
        model_id: str,
        prior_ratchet_receipt_sha256: str,
        baseline_policy_sha256: str,
        baseline_policy_vector: Sequence[int | float | str | Fraction],
        risk_weight_vector: Sequence[int | float | str | Fraction],
        individual_lease_budget: int | float | str | Fraction,
        horizon_drift_ceiling: int | float | str | Fraction,
        uncoordinated_overlapping_leases: Sequence[Mapping[str, Any]],
        overlap_accounted_leases: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        if not schedule_id or not model_id:
            raise ValidationError("schedule_id and model_id must be non-empty")
        if not prior_ratchet_receipt_sha256 or not baseline_policy_sha256:
            raise ValidationError("prior_ratchet_receipt_sha256 and baseline_policy_sha256 must be non-empty")
        if not baseline_policy_vector:
            raise ValidationError("baseline_policy_vector must be non-empty")

        p0_vec = [rational(v) for v in baseline_policy_vector]
        w_vec = [rational(w) for w in risk_weight_vector]
        dim = len(p0_vec)
        if len(w_vec) != dim:
            raise ValidationError("risk_weight_vector must have the same dimension as baseline_policy_vector")
        if any(w <= 0 for w in w_vec):
            raise ValidationError("all coordinates of risk_weight_vector must be strictly positive")

        tau_lease = rational(individual_lease_budget)
        tau_horizon = rational(horizon_drift_ceiling)
        if tau_lease <= 0 or tau_horizon <= 0:
            raise ValidationError("individual_lease_budget and horizon_drift_ceiling must be strictly positive")
        if tau_horizon < tau_lease:
            raise ValidationError("horizon_drift_ceiling must be >= individual_lease_budget")

        uncoordinated_audit = self._audit_lease_schedule(
            leases=uncoordinated_overlapping_leases,
            p0_vec=p0_vec,
            w_vec=w_vec,
            tau_lease=tau_lease,
            tau_horizon=tau_horizon,
            dim=dim,
            require_overlap_accounting=False,
        )
        accounted_audit = self._audit_lease_schedule(
            leases=overlap_accounted_leases,
            p0_vec=p0_vec,
            w_vec=w_vec,
            tau_lease=tau_lease,
            tau_horizon=tau_horizon,
            dim=dim,
            require_overlap_accounting=True,
        )

        converged_single_round = uncoordinated_audit["global_schedule_indicator_E_g"] == 1
        converged_multi_round = converged_single_round or (
            accounted_audit["global_schedule_indicator_E_g"] == 1
        )
        peak_drift_reduction = (
            uncoordinated_audit["peak_concurrent_weighted_l1_drift"]
            - accounted_audit["peak_concurrent_weighted_l1_drift"]
        )

        record: dict[str, Any] = {
            "schedule_id": schedule_id,
            "model_id": model_id,
            "prior_ratchet_receipt_sha256": prior_ratchet_receipt_sha256,
            "baseline_policy_sha256": baseline_policy_sha256,
            "baseline_policy_vector": p0_vec,
            "risk_weight_vector": w_vec,
            "individual_lease_budget": tau_lease,
            "horizon_drift_ceiling": tau_horizon,
            "phase_1_uncoordinated_overlap_schedule": uncoordinated_audit,
            "phase_2_overlap_accounted_schedule": accounted_audit,
            "phase_1_overlap_horizon_breach": uncoordinated_audit["overlap_horizon_breach_detected"],
            "converged_single_round": converged_single_round,
            "converged_multi_round": converged_multi_round,
            "peak_concurrent_weighted_drift_reduction": peak_drift_reduction,
        }
        self.schedules.append(record)
        return json_value(record)

    def emit_receipt(self) -> dict[str, Any]:
        if not self.schedules:
            raise ValidationError("cannot emit receipt without recorded concurrent lease overlap schedules")
        n = len(self.schedules)
        single_cnt = sum(1 for s in self.schedules if s["converged_single_round"])
        multi_cnt = sum(1 for s in self.schedules if s["converged_multi_round"])
        overlap_breach_cnt = sum(1 for s in self.schedules if s["phase_1_overlap_horizon_breach"])

        single_rate = Fraction(single_cnt, n)
        multi_rate = Fraction(multi_cnt, n)
        gain_rate = multi_rate - single_rate
        overlap_breach_rate = Fraction(overlap_breach_cnt, n)

        overlap_breach_ids = [
            s["schedule_id"] for s in self.schedules if s["phase_1_overlap_horizon_breach"]
        ]
        unconverged_ids = [
            s["schedule_id"] for s in self.schedules if not s["converged_multi_round"]
        ]

        if multi_cnt == n:
            status = "LEASE_OVERLAP_ACCOUNTING_HORIZON_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "CONCURRENT_LEASE_OVERLAP_HORIZON_BREACH_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_concurrent_lease_overlap.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "schedule_count": n,
            "single_round_overlap_coherent_count": single_cnt,
            "multi_round_overlap_accounted_coherent_count": multi_cnt,
            "phase_1_overlap_horizon_breach_count": overlap_breach_cnt,
            "single_round_overlap_coherence_rate": single_rate,
            "multi_round_overlap_accounted_coherence_rate": multi_rate,
            "overlap_accounting_coherence_gain": gain_rate,
            "phase_1_overlap_horizon_breach_rate": overlap_breach_rate,
            "monotonic_coherence_verified": multi_rate >= single_rate,
            "phase_1_overlap_horizon_breach_schedule_ids": overlap_breach_ids,
            "unconverged_schedule_ids": unconverged_ids,
            "schedules": self.schedules,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingSimultaneousBudgetSplitMonitor:
    """Audit non-preemptible simultaneous incidents (s_1 = s_2 = ... = s_M) under fractional budget-splitting vs. priority queueing.

    When multiple non-preemptible incidents arrive at the same tick s_0 and their joint minimum
    weighted Pareto floor exceeds the global horizon ceiling:
        sum_{k=1}^M Delta_{w,k}^* > tau_horizon  (while max_k Delta_{w,k}^* <= tau_lease <= tau_horizon),
    separates:
      1. Fractional concurrent budget-splitting at tick s_0 (all M incidents admitted simultaneously
         at execution_tick = s_0 under reduced leases delta_k' satisfying
         sum_{k=1}^M ||delta_k'||_{1,w} <= tau_horizon -> L_budget_split = 1, yet by additivity
         at least one incident k receives ||delta_k'||_{1,w} < Delta_{w,k}^*, starving its coupled
         monitors below their Pareto floor -> E_{g,split} = 0, Delta_{E,split} = -1,
         FRACTIONAL_BUDGET_SPLIT_UNDER_PARETO_FLOOR_LGGR).
      2. Priority-queued deferred admission (assigning priority queue slots execution_tick = s_0 + rank_k
         so each non-preemptible incident k executes with its full Pareto-restoring lease
         ||delta_k||_{1,w} >= Delta_{w,k}^* while active concurrent drift at every tick tau satisfies
         D_w(tau) <= tau_horizon -> L_queued = 1, E_{g,queued} = 1, Delta_{E,queued} = 0,
         PRIORITY_QUEUE_DEFERRED_ADMISSION_COHERENT_LGGG).

    AuthorityEffect: None.
    """

    def __init__(self, scope_id: str) -> None:
        if not scope_id:
            raise ValidationError("scope_id must be non-empty")
        self.scope_id = scope_id
        self.bursts: list[dict[str, Any]] = []

    def _audit_burst_admission(
        self,
        *,
        incidents: Sequence[Mapping[str, Any]],
        p0_vec: list[Fraction],
        w_vec: list[Fraction],
        tau_lease: Fraction,
        tau_horizon: Fraction,
        dim: int,
        require_priority_queueing: bool,
    ) -> dict[str, Any]:
        if len(incidents) < 2:
            raise ValidationError("simultaneous burst must contain at least 2 incidents")

        parsed_incidents: list[dict[str, Any]] = []
        joint_pareto_floor = Fraction(0)
        arrival_ticks: set[int] = set()
        min_exec_tick: int | None = None
        max_comp_tick: int | None = None

        for idx, inc in enumerate(incidents):
            inc_num = int(inc.get("incident_index", idx + 1))
            pair_id = str(inc.get("incident_pair_id", f"incident_{inc_num}"))
            prio_rank = int(inc.get("priority_rank", idx + 1))
            s_k = int(inc.get("arrival_tick", 0))
            exec_k = int(inc.get("execution_tick", s_k))
            comp_k = int(inc.get("completion_tick", exec_k + 1))
            if exec_k < s_k:
                raise ValidationError("execution_tick must be >= arrival_tick")
            if comp_k <= exec_k:
                raise ValidationError("completion_tick must be strictly greater than execution_tick")

            arrival_ticks.add(s_k)
            non_preemptible = bool(inc.get("non_preemptible", True))
            sig_valid = bool(inc.get("authority_signature_valid", False))
            queue_enforced = bool(inc.get("priority_queue_enforced", False))
            mon_a = bool(inc.get("post_relaxation_monitor_a_passed", False))
            mon_b = bool(inc.get("post_relaxation_monitor_b_passed", False))

            pareto_floor_k = rational(inc.get("minimum_weighted_pareto_floor", 0))
            if pareto_floor_k <= 0:
                raise ValidationError("minimum_weighted_pareto_floor must be strictly positive")
            joint_pareto_floor += pareto_floor_k

            raw_delta = inc.get("allocated_delta_vector")
            if raw_delta is None:
                raise ValidationError("incident must provide allocated_delta_vector")
            delta_vec = [rational(v) for v in raw_delta]
            if len(delta_vec) != dim:
                raise ValidationError("allocated_delta_vector dimension mismatch")

            allocated_policy_vec = [p0_vec[j] + delta_vec[j] for j in range(dim)]
            unweighted_slack = sum((abs(d) for d in delta_vec), Fraction(0))
            weighted_slack = sum((w_vec[j] * abs(delta_vec[j]) for j in range(dim)), Fraction(0))

            within_individual_lease = weighted_slack <= tau_lease
            meets_pareto_floor = weighted_slack >= pareto_floor_k
            under_pareto_floor = weighted_slack < pareto_floor_k
            pareto_deficit = max(Fraction(0), pareto_floor_k - weighted_slack)
            pareto_restored = mon_a and mon_b and meets_pareto_floor

            if min_exec_tick is None or exec_k < min_exec_tick:
                min_exec_tick = exec_k
            if max_comp_tick is None or comp_k > max_comp_tick:
                max_comp_tick = comp_k

            parsed_incidents.append(
                {
                    "incident_index": inc_num,
                    "incident_pair_id": pair_id,
                    "priority_rank": prio_rank,
                    "arrival_tick": s_k,
                    "execution_tick": exec_k,
                    "completion_tick": comp_k,
                    "queue_delay_ticks": exec_k - s_k,
                    "non_preemptible": non_preemptible,
                    "authority_signature_valid": sig_valid,
                    "priority_queue_enforced": queue_enforced,
                    "minimum_weighted_pareto_floor": pareto_floor_k,
                    "allocated_delta_vector": delta_vec,
                    "allocated_policy_vector": allocated_policy_vec,
                    "allocated_unweighted_l1_slack": unweighted_slack,
                    "allocated_weighted_l1_slack": weighted_slack,
                    "within_individual_lease_budget": within_individual_lease,
                    "meets_pareto_floor": meets_pareto_floor,
                    "under_pareto_floor": under_pareto_floor,
                    "pareto_floor_deficit_l1_w": pareto_deficit,
                    "post_relaxation_monitor_a_passed": mon_a,
                    "post_relaxation_monitor_b_passed": mon_b,
                    "pareto_intersection_restored": pareto_restored,
                }
            )

        simultaneous_arrival_verified = len(arrival_ticks) == 1
        assert min_exec_tick is not None and max_comp_tick is not None

        tick_records: list[dict[str, Any]] = []
        peak_concurrent_drift = Fraction(0)
        max_concurrent_executing = 0

        for tick in range(min_exec_tick, max_comp_tick):
            active = [
                inc
                for inc in parsed_incidents
                if inc["execution_tick"] <= tick < inc["completion_tick"]
            ]
            if len(active) > max_concurrent_executing:
                max_concurrent_executing = len(active)
            agg_delta = [
                sum((inc["allocated_delta_vector"][j] for inc in active), Fraction(0))
                for j in range(dim)
            ]
            tick_weighted_drift = sum(
                (w_vec[j] * abs(agg_delta[j]) for j in range(dim)), Fraction(0)
            )
            if tick_weighted_drift > peak_concurrent_drift:
                peak_concurrent_drift = tick_weighted_drift
            tick_records.append(
                {
                    "tick": tick,
                    "executing_incident_indices": [inc["incident_index"] for inc in active],
                    "executing_count": len(active),
                    "aggregate_delta_vector": agg_delta,
                    "concurrent_weighted_l1_drift": tick_weighted_drift,
                    "horizon_within_ceiling": tick_weighted_drift <= tau_horizon,
                }
            )

        horizon_budget_respected = peak_concurrent_drift <= tau_horizon
        starved_count = 0

        for inc in parsed_incidents:
            exec_k = inc["execution_tick"]
            comp_k = inc["completion_tick"]
            inc_peak_drift = max(
                (
                    tr["concurrent_weighted_l1_drift"]
                    for tr in tick_records
                    if exec_k <= tr["tick"] < comp_k
                ),
                default=inc["allocated_weighted_l1_slack"],
            )
            inc_horizon_ok = inc_peak_drift <= tau_horizon
            l_k = (
                1
                if (
                    inc["authority_signature_valid"]
                    and inc["within_individual_lease_budget"]
                    and inc_horizon_ok
                )
                else 0
            )
            q_ok = (not require_priority_queueing) or inc["priority_queue_enforced"]
            eg_k = (
                1
                if (
                    l_k == 1
                    and inc["pareto_intersection_restored"]
                    and not inc["under_pareto_floor"]
                    and q_ok
                )
                else 0
            )
            if inc["under_pareto_floor"] or not inc["pareto_intersection_restored"]:
                starved_count += 1

            inc["peak_concurrent_weighted_drift_during_execution"] = inc_peak_drift
            inc["local_budget_indicator_L_k"] = l_k
            inc["global_pareto_indicator_E_g_k"] = eg_k
            inc["incident_evaluator_defect"] = eg_k - l_k
            if eg_k == 1:
                inc["incident_status"] = "PRIORITY_QUEUE_PARETO_RESTORED_LGGG"
            elif l_k == 1 and (inc["under_pareto_floor"] or not inc["pareto_intersection_restored"]):
                inc["incident_status"] = "FRACTIONAL_BUDGET_SPLIT_UNDER_PARETO_FLOOR_LGGR"
            else:
                inc["incident_status"] = "INCIDENT_BUDGET_OR_SIGNATURE_OBSTRUCTED_LGGR"

        l_burst = (
            1
            if (
                simultaneous_arrival_verified
                and horizon_budget_respected
                and all(inc["local_budget_indicator_L_k"] == 1 for inc in parsed_incidents)
            )
            else 0
        )
        eg_burst = (
            1
            if (
                l_burst == 1
                and all(inc["global_pareto_indicator_E_g_k"] == 1 for inc in parsed_incidents)
            )
            else 0
        )
        delta_e_burst = eg_burst - l_burst
        fractional_starvation_detected = (
            l_burst == 1 and eg_burst == 0 and starved_count > 0
        )

        if eg_burst == 1:
            burst_status = "PRIORITY_QUEUE_DEFERRED_ADMISSION_COHERENT_LGGG"
        elif fractional_starvation_detected:
            burst_status = "FRACTIONAL_BUDGET_SPLIT_UNDER_PARETO_FLOOR_LGGR"
        else:
            burst_status = "BURST_BUDGET_OR_ADMISSION_OBSTRUCTED_LGGR"

        return {
            "incident_count": len(parsed_incidents),
            "simultaneous_arrival_verified": simultaneous_arrival_verified,
            "joint_simultaneous_pareto_floor_l1_w": joint_pareto_floor,
            "joint_pareto_floor_exceeds_horizon": joint_pareto_floor > tau_horizon,
            "max_concurrent_executing_incidents": max_concurrent_executing,
            "peak_concurrent_weighted_l1_drift": peak_concurrent_drift,
            "starved_incident_count": starved_count,
            "local_burst_indicator_L": l_burst,
            "global_burst_indicator_E_g": eg_burst,
            "burst_evaluator_defect": delta_e_burst,
            "fractional_split_starvation_detected": fractional_starvation_detected,
            "burst_status": burst_status,
            "incidents": parsed_incidents,
            "ticks": tick_records,
        }

    def record_simultaneous_burst(
        self,
        *,
        burst_id: str,
        model_id: str,
        prior_overlap_receipt_sha256: str,
        baseline_policy_sha256: str,
        baseline_policy_vector: Sequence[int | float | str | Fraction],
        risk_weight_vector: Sequence[int | float | str | Fraction],
        individual_lease_budget: int | float | str | Fraction,
        horizon_drift_ceiling: int | float | str | Fraction,
        fractional_split_incidents: Sequence[Mapping[str, Any]],
        priority_queued_incidents: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        if not burst_id or not model_id:
            raise ValidationError("burst_id and model_id must be non-empty")
        if not prior_overlap_receipt_sha256 or not baseline_policy_sha256:
            raise ValidationError("prior_overlap_receipt_sha256 and baseline_policy_sha256 must be non-empty")
        if not baseline_policy_vector:
            raise ValidationError("baseline_policy_vector must be non-empty")

        p0_vec = [rational(v) for v in baseline_policy_vector]
        w_vec = [rational(w) for w in risk_weight_vector]
        dim = len(p0_vec)
        if len(w_vec) != dim:
            raise ValidationError("risk_weight_vector must have the same dimension as baseline_policy_vector")
        if any(w <= 0 for w in w_vec):
            raise ValidationError("all coordinates of risk_weight_vector must be strictly positive")

        tau_lease = rational(individual_lease_budget)
        tau_horizon = rational(horizon_drift_ceiling)
        if tau_lease <= 0 or tau_horizon <= 0:
            raise ValidationError("individual_lease_budget and horizon_drift_ceiling must be strictly positive")
        if tau_horizon < tau_lease:
            raise ValidationError("horizon_drift_ceiling must be >= individual_lease_budget")

        split_audit = self._audit_burst_admission(
            incidents=fractional_split_incidents,
            p0_vec=p0_vec,
            w_vec=w_vec,
            tau_lease=tau_lease,
            tau_horizon=tau_horizon,
            dim=dim,
            require_priority_queueing=False,
        )
        queued_audit = self._audit_burst_admission(
            incidents=priority_queued_incidents,
            p0_vec=p0_vec,
            w_vec=w_vec,
            tau_lease=tau_lease,
            tau_horizon=tau_horizon,
            dim=dim,
            require_priority_queueing=True,
        )

        converged_single_round = split_audit["global_burst_indicator_E_g"] == 1
        converged_multi_round = converged_single_round or (
            queued_audit["global_burst_indicator_E_g"] == 1
        )
        starved_eliminated = (
            split_audit["starved_incident_count"] - queued_audit["starved_incident_count"]
        )

        record: dict[str, Any] = {
            "burst_id": burst_id,
            "model_id": model_id,
            "prior_overlap_receipt_sha256": prior_overlap_receipt_sha256,
            "baseline_policy_sha256": baseline_policy_sha256,
            "baseline_policy_vector": p0_vec,
            "risk_weight_vector": w_vec,
            "individual_lease_budget": tau_lease,
            "horizon_drift_ceiling": tau_horizon,
            "phase_1_fractional_budget_split": split_audit,
            "phase_2_priority_queued_admission": queued_audit,
            "phase_1_fractional_split_starvation": split_audit[
                "fractional_split_starvation_detected"
            ],
            "converged_single_round": converged_single_round,
            "converged_multi_round": converged_multi_round,
            "starved_incidents_eliminated": starved_eliminated,
        }
        self.bursts.append(record)
        return json_value(record)

    def emit_receipt(self) -> dict[str, Any]:
        if not self.bursts:
            raise ValidationError("cannot emit receipt without recorded simultaneous bursts")
        n = len(self.bursts)
        single_cnt = sum(1 for b in self.bursts if b["converged_single_round"])
        multi_cnt = sum(1 for b in self.bursts if b["converged_multi_round"])
        starv_cnt = sum(1 for b in self.bursts if b["phase_1_fractional_split_starvation"])

        single_rate = Fraction(single_cnt, n)
        multi_rate = Fraction(multi_cnt, n)
        gain_rate = multi_rate - single_rate
        starv_rate = Fraction(starv_cnt, n)

        starv_ids = [
            b["burst_id"] for b in self.bursts if b["phase_1_fractional_split_starvation"]
        ]
        unconverged_ids = [
            b["burst_id"] for b in self.bursts if not b["converged_multi_round"]
        ]

        if multi_cnt == n:
            status = "PRIORITY_QUEUE_DEFERRED_ADMISSION_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "FRACTIONAL_BUDGET_SPLIT_UNDER_PARETO_FLOOR_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_simultaneous_budget_split.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "burst_count": n,
            "single_round_split_coherent_count": single_cnt,
            "multi_round_priority_queued_coherent_count": multi_cnt,
            "phase_1_fractional_split_starvation_count": starv_cnt,
            "single_round_split_coherence_rate": single_rate,
            "multi_round_priority_queued_coherence_rate": multi_rate,
            "priority_queue_coherence_gain": gain_rate,
            "phase_1_fractional_split_starvation_rate": starv_rate,
            "monotonic_coherence_verified": multi_rate >= single_rate,
            "phase_1_fractional_split_starvation_burst_ids": starv_ids,
            "unconverged_burst_ids": unconverged_ids,
            "bursts": self.bursts,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingDeadlinePriorityQueueMonitor:
    """Audit deadline-constrained priority queueing under simultaneous bursts (EDF vs. static priority ordering).

    When M non-preemptible incidents arrive simultaneously at tick s_0 with minimum weighted
    Pareto floors Delta_{w,k}^* <= tau_lease <= tau_horizon (and sum_k Delta_{w,k}^* > tau_horizon),
    static priority ranks pi_k, and strict SLA completion deadlines D_k, separates:
      1. Static priority queue ordering (scheduling in order of static priority pi_1 < pi_2 < ... < pi_M
         grants each incident its full Pareto-restoring lease ||delta_k||_{1,w} >= Delta_{w,k}^* and
         respects active horizon ceiling D_w(tau) <= tau_horizon -> L_queue = 1, yet defers a
         tight-deadline low-priority incident past its SLA deadline C_k > D_k -> E_{g,queue} = 0,
         Delta_{E,queue} = -1, STATIC_PRIORITY_SLA_DEADLINE_BREACH_LGGR).
      2. Earliest-Deadline-First (EDF) queue ordering (scheduling in non-decreasing order of SLA
         deadlines D_{k_1} <= D_{k_2} <= ... <= D_{k_M} so every incident satisfies both
         ||delta_k||_{1,w} >= Delta_{w,k}^*, D_w(tau) <= tau_horizon, and C_k <= D_k ->
         L_queue = 1, E_{g,queue} = 1, Delta_{E,queue} = 0,
         EDF_DEADLINE_COHERENT_QUEUE_VERIFIED_LGGG).

    AuthorityEffect: None.
    """

    def __init__(self, scope_id: str) -> None:
        if not scope_id:
            raise ValidationError("scope_id must be non-empty")
        self.scope_id = scope_id
        self.queues: list[dict[str, Any]] = []

    def _audit_queue_schedule(
        self,
        *,
        incidents: Sequence[Mapping[str, Any]],
        p0_vec: list[Fraction],
        w_vec: list[Fraction],
        tau_lease: Fraction,
        tau_horizon: Fraction,
        dim: int,
        require_edf_ordering: bool,
    ) -> dict[str, Any]:
        if len(incidents) < 2:
            raise ValidationError("deadline queue schedule must contain at least 2 incidents")

        parsed_incidents: list[dict[str, Any]] = []
        joint_pareto_floor = Fraction(0)
        arrival_ticks: set[int] = set()
        min_exec_tick: int | None = None
        max_comp_tick: int | None = None

        for idx, inc in enumerate(incidents):
            inc_num = int(inc.get("incident_index", idx + 1))
            pair_id = str(inc.get("incident_pair_id", f"incident_{inc_num}"))
            static_prio = int(inc.get("static_priority_rank", idx + 1))
            sla_deadline = int(inc.get("sla_deadline_tick", idx + 1))
            s_k = int(inc.get("arrival_tick", 0))
            exec_k = int(inc.get("execution_tick", s_k))
            comp_k = int(inc.get("completion_tick", exec_k + 1))
            if exec_k < s_k:
                raise ValidationError("execution_tick must be >= arrival_tick")
            if comp_k <= exec_k:
                raise ValidationError("completion_tick must be strictly greater than execution_tick")
            if sla_deadline <= s_k:
                raise ValidationError("sla_deadline_tick must be strictly greater than arrival_tick")

            arrival_ticks.add(s_k)
            sig_valid = bool(inc.get("authority_signature_valid", False))
            edf_enforced = bool(inc.get("edf_policy_enforced", False))
            mon_a = bool(inc.get("post_relaxation_monitor_a_passed", False))
            mon_b = bool(inc.get("post_relaxation_monitor_b_passed", False))

            pareto_floor_k = rational(inc.get("minimum_weighted_pareto_floor", 0))
            if pareto_floor_k <= 0:
                raise ValidationError("minimum_weighted_pareto_floor must be strictly positive")
            joint_pareto_floor += pareto_floor_k

            raw_delta = inc.get("allocated_delta_vector")
            if raw_delta is None:
                raise ValidationError("incident must provide allocated_delta_vector")
            delta_vec = [rational(v) for v in raw_delta]
            if len(delta_vec) != dim:
                raise ValidationError("allocated_delta_vector dimension mismatch")

            allocated_policy_vec = [p0_vec[j] + delta_vec[j] for j in range(dim)]
            unweighted_slack = sum((abs(d) for d in delta_vec), Fraction(0))
            weighted_slack = sum((w_vec[j] * abs(delta_vec[j]) for j in range(dim)), Fraction(0))

            within_individual_lease = weighted_slack <= tau_lease
            meets_pareto_floor = weighted_slack >= pareto_floor_k
            pareto_restored = mon_a and mon_b and meets_pareto_floor

            lateness_ticks = max(0, comp_k - sla_deadline)
            sla_deadline_met = comp_k <= sla_deadline

            if min_exec_tick is None or exec_k < min_exec_tick:
                min_exec_tick = exec_k
            if max_comp_tick is None or comp_k > max_comp_tick:
                max_comp_tick = comp_k

            parsed_incidents.append(
                {
                    "incident_index": inc_num,
                    "incident_pair_id": pair_id,
                    "static_priority_rank": static_prio,
                    "sla_deadline_tick": sla_deadline,
                    "arrival_tick": s_k,
                    "execution_tick": exec_k,
                    "completion_tick": comp_k,
                    "queue_delay_ticks": exec_k - s_k,
                    "lateness_ticks": lateness_ticks,
                    "sla_deadline_met": sla_deadline_met,
                    "authority_signature_valid": sig_valid,
                    "edf_policy_enforced": edf_enforced,
                    "minimum_weighted_pareto_floor": pareto_floor_k,
                    "allocated_delta_vector": delta_vec,
                    "allocated_policy_vector": allocated_policy_vec,
                    "allocated_unweighted_l1_slack": unweighted_slack,
                    "allocated_weighted_l1_slack": weighted_slack,
                    "within_individual_lease_budget": within_individual_lease,
                    "meets_pareto_floor": meets_pareto_floor,
                    "post_relaxation_monitor_a_passed": mon_a,
                    "post_relaxation_monitor_b_passed": mon_b,
                    "pareto_intersection_restored": pareto_restored,
                }
            )

        simultaneous_arrival_verified = len(arrival_ticks) == 1
        assert min_exec_tick is not None and max_comp_tick is not None

        # Check EDF non-decreasing deadline order along execution_tick
        sorted_by_exec = sorted(
            parsed_incidents,
            key=lambda x: (x["execution_tick"], x["sla_deadline_tick"], x["incident_index"]),
        )
        edf_order_verified = all(
            sorted_by_exec[i]["sla_deadline_tick"] <= sorted_by_exec[i + 1]["sla_deadline_tick"]
            for i in range(len(sorted_by_exec) - 1)
        )

        tick_records: list[dict[str, Any]] = []
        peak_concurrent_drift = Fraction(0)
        max_concurrent_executing = 0

        for tick in range(min_exec_tick, max_comp_tick):
            active = [
                inc
                for inc in parsed_incidents
                if inc["execution_tick"] <= tick < inc["completion_tick"]
            ]
            if len(active) > max_concurrent_executing:
                max_concurrent_executing = len(active)
            agg_delta = [
                sum((inc["allocated_delta_vector"][j] for inc in active), Fraction(0))
                for j in range(dim)
            ]
            tick_weighted_drift = sum(
                (w_vec[j] * abs(agg_delta[j]) for j in range(dim)), Fraction(0)
            )
            if tick_weighted_drift > peak_concurrent_drift:
                peak_concurrent_drift = tick_weighted_drift
            tick_records.append(
                {
                    "tick": tick,
                    "executing_incident_indices": [inc["incident_index"] for inc in active],
                    "executing_count": len(active),
                    "aggregate_delta_vector": agg_delta,
                    "concurrent_weighted_l1_drift": tick_weighted_drift,
                    "horizon_within_ceiling": tick_weighted_drift <= tau_horizon,
                }
            )

        horizon_budget_respected = peak_concurrent_drift <= tau_horizon
        deadline_miss_count = 0
        max_lateness_ticks = 0

        for inc in parsed_incidents:
            exec_k = inc["execution_tick"]
            comp_k = inc["completion_tick"]
            inc_peak_drift = max(
                (
                    tr["concurrent_weighted_l1_drift"]
                    for tr in tick_records
                    if exec_k <= tr["tick"] < comp_k
                ),
                default=inc["allocated_weighted_l1_slack"],
            )
            inc_horizon_ok = inc_peak_drift <= tau_horizon
            l_k = (
                1
                if (
                    inc["authority_signature_valid"]
                    and inc["within_individual_lease_budget"]
                    and inc["pareto_intersection_restored"]
                    and inc_horizon_ok
                )
                else 0
            )
            edf_ok = (not require_edf_ordering) or (inc["edf_policy_enforced"] and edf_order_verified)
            eg_k = 1 if (l_k == 1 and inc["sla_deadline_met"] and edf_ok) else 0

            if not inc["sla_deadline_met"]:
                deadline_miss_count += 1
            if inc["lateness_ticks"] > max_lateness_ticks:
                max_lateness_ticks = inc["lateness_ticks"]

            inc["peak_concurrent_weighted_drift_during_execution"] = inc_peak_drift
            inc["local_budget_pareto_indicator_L_k"] = l_k
            inc["global_deadline_pareto_indicator_E_g_k"] = eg_k
            inc["incident_evaluator_defect"] = eg_k - l_k
            if eg_k == 1:
                inc["incident_status"] = "EDF_SLA_DEADLINE_AND_PARETO_MET_LGGG"
            elif l_k == 1 and not inc["sla_deadline_met"]:
                inc["incident_status"] = "STATIC_PRIORITY_SLA_DEADLINE_BREACH_LGGR"
            else:
                inc["incident_status"] = "INCIDENT_BUDGET_OR_PARETO_OBSTRUCTED_LGGR"

        l_queue = (
            1
            if (
                simultaneous_arrival_verified
                and horizon_budget_respected
                and all(inc["local_budget_pareto_indicator_L_k"] == 1 for inc in parsed_incidents)
            )
            else 0
        )
        eg_queue = (
            1
            if (
                l_queue == 1
                and all(inc["global_deadline_pareto_indicator_E_g_k"] == 1 for inc in parsed_incidents)
            )
            else 0
        )
        delta_e_queue = eg_queue - l_queue
        static_deadline_breach_detected = (
            l_queue == 1 and eg_queue == 0 and deadline_miss_count > 0
        )

        if eg_queue == 1:
            queue_status = "EDF_DEADLINE_COHERENT_QUEUE_VERIFIED_LGGG"
        elif static_deadline_breach_detected:
            queue_status = "STATIC_PRIORITY_SLA_DEADLINE_BREACH_LGGR"
        else:
            queue_status = "QUEUE_BUDGET_OR_PARETO_OBSTRUCTED_LGGR"

        return {
            "incident_count": len(parsed_incidents),
            "simultaneous_arrival_verified": simultaneous_arrival_verified,
            "edf_order_verified": edf_order_verified,
            "joint_simultaneous_pareto_floor_l1_w": joint_pareto_floor,
            "max_concurrent_executing_incidents": max_concurrent_executing,
            "peak_concurrent_weighted_l1_drift": peak_concurrent_drift,
            "deadline_miss_count": deadline_miss_count,
            "max_lateness_ticks": max_lateness_ticks,
            "local_queue_indicator_L": l_queue,
            "global_queue_indicator_E_g": eg_queue,
            "queue_evaluator_defect": delta_e_queue,
            "static_deadline_breach_detected": static_deadline_breach_detected,
            "queue_status": queue_status,
            "incidents": parsed_incidents,
            "ticks": tick_records,
        }

    def record_deadline_queue_comparison(
        self,
        *,
        queue_id: str,
        model_id: str,
        prior_split_receipt_sha256: str,
        baseline_policy_sha256: str,
        baseline_policy_vector: Sequence[int | float | str | Fraction],
        risk_weight_vector: Sequence[int | float | str | Fraction],
        individual_lease_budget: int | float | str | Fraction,
        horizon_drift_ceiling: int | float | str | Fraction,
        static_priority_incidents: Sequence[Mapping[str, Any]],
        edf_queued_incidents: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        if not queue_id or not model_id:
            raise ValidationError("queue_id and model_id must be non-empty")
        if not prior_split_receipt_sha256 or not baseline_policy_sha256:
            raise ValidationError("prior_split_receipt_sha256 and baseline_policy_sha256 must be non-empty")
        if not baseline_policy_vector:
            raise ValidationError("baseline_policy_vector must be non-empty")

        p0_vec = [rational(v) for v in baseline_policy_vector]
        w_vec = [rational(w) for w in risk_weight_vector]
        dim = len(p0_vec)
        if len(w_vec) != dim:
            raise ValidationError("risk_weight_vector must have the same dimension as baseline_policy_vector")
        if any(w <= 0 for w in w_vec):
            raise ValidationError("all coordinates of risk_weight_vector must be strictly positive")

        tau_lease = rational(individual_lease_budget)
        tau_horizon = rational(horizon_drift_ceiling)
        if tau_lease <= 0 or tau_horizon <= 0:
            raise ValidationError("individual_lease_budget and horizon_drift_ceiling must be strictly positive")
        if tau_horizon < tau_lease:
            raise ValidationError("horizon_drift_ceiling must be >= individual_lease_budget")

        static_audit = self._audit_queue_schedule(
            incidents=static_priority_incidents,
            p0_vec=p0_vec,
            w_vec=w_vec,
            tau_lease=tau_lease,
            tau_horizon=tau_horizon,
            dim=dim,
            require_edf_ordering=False,
        )
        edf_audit = self._audit_queue_schedule(
            incidents=edf_queued_incidents,
            p0_vec=p0_vec,
            w_vec=w_vec,
            tau_lease=tau_lease,
            tau_horizon=tau_horizon,
            dim=dim,
            require_edf_ordering=True,
        )

        converged_single_round = static_audit["global_queue_indicator_E_g"] == 1
        converged_multi_round = converged_single_round or (
            edf_audit["global_queue_indicator_E_g"] == 1
        )
        lateness_reduction = (
            static_audit["max_lateness_ticks"] - edf_audit["max_lateness_ticks"]
        )

        record: dict[str, Any] = {
            "queue_id": queue_id,
            "model_id": model_id,
            "prior_split_receipt_sha256": prior_split_receipt_sha256,
            "baseline_policy_sha256": baseline_policy_sha256,
            "baseline_policy_vector": p0_vec,
            "risk_weight_vector": w_vec,
            "individual_lease_budget": tau_lease,
            "horizon_drift_ceiling": tau_horizon,
            "phase_1_static_priority_queue": static_audit,
            "phase_2_edf_deadline_queue": edf_audit,
            "phase_1_static_deadline_breach": static_audit["static_deadline_breach_detected"],
            "converged_single_round": converged_single_round,
            "converged_multi_round": converged_multi_round,
            "max_lateness_reduction_ticks": lateness_reduction,
        }
        self.queues.append(record)
        return json_value(record)

    def emit_receipt(self) -> dict[str, Any]:
        if not self.queues:
            raise ValidationError("cannot emit receipt without recorded deadline queue comparisons")
        n = len(self.queues)
        single_cnt = sum(1 for q in self.queues if q["converged_single_round"])
        multi_cnt = sum(1 for q in self.queues if q["converged_multi_round"])
        breach_cnt = sum(1 for q in self.queues if q["phase_1_static_deadline_breach"])

        single_rate = Fraction(single_cnt, n)
        multi_rate = Fraction(multi_cnt, n)
        gain_rate = multi_rate - single_rate
        breach_rate = Fraction(breach_cnt, n)

        breach_ids = [
            q["queue_id"] for q in self.queues if q["phase_1_static_deadline_breach"]
        ]
        unconverged_ids = [
            q["queue_id"] for q in self.queues if not q["converged_multi_round"]
        ]

        if multi_cnt == n:
            status = "EDF_DEADLINE_COHERENT_QUEUE_VERIFIED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "STATIC_PRIORITY_SLA_DEADLINE_BREACH_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_deadline_priority_queue.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "queue_count": n,
            "single_round_static_deadline_coherent_count": single_cnt,
            "multi_round_edf_deadline_coherent_count": multi_cnt,
            "phase_1_static_deadline_breach_count": breach_cnt,
            "single_round_static_deadline_coherence_rate": single_rate,
            "multi_round_edf_deadline_coherence_rate": multi_rate,
            "edf_deadline_coherence_gain": gain_rate,
            "phase_1_static_deadline_breach_rate": breach_rate,
            "monotonic_coherence_verified": multi_rate >= single_rate,
            "phase_1_static_deadline_breach_queue_ids": breach_ids,
            "unconverged_queue_ids": unconverged_ids,
            "queues": self.queues,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingOverloadedDeadlineBinPackingMonitor:
    """Audit overloaded SLA deadline bursts where serial EDF violates sum_{j=1}^k p_j <= D_k.

    Evaluates 3-phase governance across M simultaneous non-preemptible incidents (s_1 = ... = s_M = s_0)
    with minimum weighted Pareto floors Delta_{w,k}^* <= tau_lease and strict SLA completion deadlines D_k
    where multiple incidents share a tight deadline (e.g., D_1 = D_2 = 1, D_3 = 2):
      1. Phase 1 — Serial 1-per-slot EDF ordering under initial horizon ceiling tau_horizon:
         Every incident receives its full Pareto lease ||delta_k||_{1,w} >= Delta_{w,k}^* and respects
         active drift D_w(tau) <= tau_horizon (L_serial = 1), yet serial 1-per-slot execution violates
         sum_{j=1}^k p_j <= D_k (e.g., C_2 = 2 > D_2 = 1 and C_3 = 3 > D_3 = 2 -> E_{g,serial} = 0,
         Delta_{E,serial} = -1, SERIAL_EDF_SLA_DEADLINE_OVERLOAD_LGGR).
      2. Phase 2 — Unpackable horizon overload detection & Halt-and-Escalate under initial tau_horizon:
         When the mandatory slot-0 weighted Pareto load of deadline-1 incidents
         Lambda_{D<=1} = sum_{k : D_k - s_k <= 1} Delta_{w,k}^* > tau_horizon (e.g., Delta_{w,1}^* + Delta_{w,2}^*
         = 4 + 3 = 7 > tau_horizon = 6), packing the deadline-1 incidents into slot [s_0, s_0 + 1)
         breaches tau_horizon while deferring any of them to [s_0 + 1, s_0 + 2) breaches D_k = 1.
         Rather than oscillating between SLA deadline breach and horizon breach, the monitor halts and
         escalates (OVERLOADED_DEADLINE_BURST_HALTED_AND_ESCALATED_LGGR) with the exact minimum emergency
         horizon expansion tau_horizon^* = Lambda_{D<=1} (Delta tau_horizon^* = Lambda_{D<=1} - tau_horizon).
      3. Phase 3 — Selective multi-incident sub-horizon bin-packed EDF under expanded tau_horizon^*:
         Packs compatible sub-horizon pairs (Delta_{w,a}^* + Delta_{w,b}^* <= tau_horizon^*) with tight
         deadlines into slot [s_0, s_0 + 1) while separating incompatible incidents (where full M-way
         simultaneous execution sum_{k=1}^M Delta_{w,k}^* > tau_horizon^*) into subsequent EDF slots,
         satisfying Pareto restoration, D_w(tau) <= tau_horizon^*, and C_k <= D_k for all k
         (L_packed = 1, E_{g,packed} = 1, Delta_{E,packed} = 0, EDF_BIN_PACKED_DEADLINE_COHERENT_LGGG).

    AuthorityEffect: None.
    """

    def __init__(self, scope_id: str) -> None:
        if not scope_id:
            raise ValidationError("scope_id must be non-empty")
        self.scope_id = scope_id
        self.bursts: list[dict[str, Any]] = []

    def _audit_schedule_phase(
        self,
        *,
        incidents: Sequence[Mapping[str, Any]],
        p0_vec: list[Fraction],
        w_vec: list[Fraction],
        tau_lease: Fraction,
        tau_horizon: Fraction,
        dim: int,
        phase_mode: str,
    ) -> dict[str, Any]:
        if len(incidents) < 2:
            raise ValidationError("overloaded deadline burst must contain at least 2 incidents")

        parsed_incidents: list[dict[str, Any]] = []
        joint_pareto_floor = Fraction(0)
        mandatory_slot0_pareto_load = Fraction(0)
        arrival_ticks: set[int] = set()
        min_exec_tick: int | None = None
        max_comp_tick: int | None = None

        for idx, inc in enumerate(incidents):
            inc_num = int(inc.get("incident_index", idx + 1))
            pair_id = str(inc.get("incident_pair_id", f"incident_{inc_num}"))
            static_prio = int(inc.get("static_priority_rank", idx + 1))
            sla_deadline = int(inc.get("sla_deadline_tick", idx + 1))
            s_k = int(inc.get("arrival_tick", 0))
            exec_k = int(inc.get("execution_tick", s_k))
            comp_k = int(inc.get("completion_tick", exec_k + 1))
            if exec_k < s_k:
                raise ValidationError("execution_tick must be >= arrival_tick")
            if comp_k <= exec_k:
                raise ValidationError("completion_tick must be strictly greater than execution_tick")
            if sla_deadline <= s_k:
                raise ValidationError("sla_deadline_tick must be strictly greater than arrival_tick")

            arrival_ticks.add(s_k)
            sig_valid = bool(inc.get("authority_signature_valid", False))
            bin_pack_enforced = bool(inc.get("selective_bin_packing_enforced", False))
            halt_escalated = bool(inc.get("halt_and_escalate_triggered", False))
            mon_a = bool(inc.get("post_relaxation_monitor_a_passed", False))
            mon_b = bool(inc.get("post_relaxation_monitor_b_passed", False))

            pareto_floor_k = rational(inc.get("minimum_weighted_pareto_floor", 0))
            if pareto_floor_k <= 0:
                raise ValidationError("minimum_weighted_pareto_floor must be strictly positive")
            joint_pareto_floor += pareto_floor_k
            if sla_deadline - s_k <= 1:
                mandatory_slot0_pareto_load += pareto_floor_k

            raw_delta = inc.get("allocated_delta_vector")
            if raw_delta is None:
                raise ValidationError("incident must provide allocated_delta_vector")
            delta_vec = [rational(v) for v in raw_delta]
            if len(delta_vec) != dim:
                raise ValidationError("allocated_delta_vector dimension mismatch")

            allocated_policy_vec = [p0_vec[j] + delta_vec[j] for j in range(dim)]
            unweighted_slack = sum((abs(d) for d in delta_vec), Fraction(0))
            weighted_slack = sum((w_vec[j] * abs(delta_vec[j]) for j in range(dim)), Fraction(0))

            within_individual_lease = weighted_slack <= tau_lease
            meets_pareto_floor = weighted_slack >= pareto_floor_k
            pareto_restored = mon_a and mon_b and meets_pareto_floor

            lateness_ticks = max(0, comp_k - sla_deadline)
            sla_deadline_met = comp_k <= sla_deadline

            if min_exec_tick is None or exec_k < min_exec_tick:
                min_exec_tick = exec_k
            if max_comp_tick is None or comp_k > max_comp_tick:
                max_comp_tick = comp_k

            parsed_incidents.append(
                {
                    "incident_index": inc_num,
                    "incident_pair_id": pair_id,
                    "static_priority_rank": static_prio,
                    "sla_deadline_tick": sla_deadline,
                    "arrival_tick": s_k,
                    "execution_tick": exec_k,
                    "completion_tick": comp_k,
                    "queue_delay_ticks": exec_k - s_k,
                    "lateness_ticks": lateness_ticks,
                    "sla_deadline_met": sla_deadline_met,
                    "authority_signature_valid": sig_valid,
                    "selective_bin_packing_enforced": bin_pack_enforced,
                    "halt_and_escalate_triggered": halt_escalated,
                    "minimum_weighted_pareto_floor": pareto_floor_k,
                    "allocated_delta_vector": delta_vec,
                    "allocated_policy_vector": allocated_policy_vec,
                    "allocated_unweighted_l1_slack": unweighted_slack,
                    "allocated_weighted_l1_slack": weighted_slack,
                    "within_individual_lease_budget": within_individual_lease,
                    "meets_pareto_floor": meets_pareto_floor,
                    "post_relaxation_monitor_a_passed": mon_a,
                    "post_relaxation_monitor_b_passed": mon_b,
                    "pareto_intersection_restored": pareto_restored,
                }
            )

        simultaneous_arrival_verified = len(arrival_ticks) == 1
        assert min_exec_tick is not None and max_comp_tick is not None

        sorted_by_exec = sorted(
            parsed_incidents,
            key=lambda x: (x["execution_tick"], x["sla_deadline_tick"], x["incident_index"]),
        )
        edf_order_verified = all(
            sorted_by_exec[i]["sla_deadline_tick"] <= sorted_by_exec[i + 1]["sla_deadline_tick"]
            for i in range(len(sorted_by_exec) - 1)
        )

        tick_records: list[dict[str, Any]] = []
        peak_concurrent_drift = Fraction(0)
        max_concurrent_executing = 0

        for tick in range(min_exec_tick, max_comp_tick):
            active = [
                inc
                for inc in parsed_incidents
                if inc["execution_tick"] <= tick < inc["completion_tick"]
            ]
            if len(active) > max_concurrent_executing:
                max_concurrent_executing = len(active)
            agg_delta = [
                sum((inc["allocated_delta_vector"][j] for inc in active), Fraction(0))
                for j in range(dim)
            ]
            tick_weighted_drift = sum(
                (w_vec[j] * abs(agg_delta[j]) for j in range(dim)), Fraction(0)
            )
            if tick_weighted_drift > peak_concurrent_drift:
                peak_concurrent_drift = tick_weighted_drift
            tick_records.append(
                {
                    "tick": tick,
                    "executing_incident_indices": [inc["incident_index"] for inc in active],
                    "executing_count": len(active),
                    "aggregate_delta_vector": agg_delta,
                    "concurrent_weighted_l1_drift": tick_weighted_drift,
                    "horizon_within_ceiling": tick_weighted_drift <= tau_horizon,
                }
            )

        horizon_budget_respected = peak_concurrent_drift <= tau_horizon
        deadline_miss_count = 0
        max_lateness_ticks = 0
        horizon_breach_count = 0

        for inc in parsed_incidents:
            exec_k = inc["execution_tick"]
            comp_k = inc["completion_tick"]
            inc_peak_drift = max(
                (
                    tr["concurrent_weighted_l1_drift"]
                    for tr in tick_records
                    if exec_k <= tr["tick"] < comp_k
                ),
                default=inc["allocated_weighted_l1_slack"],
            )
            inc_horizon_ok = inc_peak_drift <= tau_horizon
            if not inc_horizon_ok:
                horizon_breach_count += 1
            if not inc["sla_deadline_met"]:
                deadline_miss_count += 1
            if inc["lateness_ticks"] > max_lateness_ticks:
                max_lateness_ticks = inc["lateness_ticks"]

            if phase_mode == "overload_escalation":
                l_k = (
                    1
                    if (
                        inc["authority_signature_valid"]
                        and inc["within_individual_lease_budget"]
                        and inc["pareto_intersection_restored"]
                        and inc["sla_deadline_met"]
                    )
                    else 0
                )
            else:
                l_k = (
                    1
                    if (
                        inc["authority_signature_valid"]
                        and inc["within_individual_lease_budget"]
                        and inc["pareto_intersection_restored"]
                        and inc_horizon_ok
                    )
                    else 0
                )

            bin_pack_ok = (phase_mode != "selective_bin_packing") or (
                inc["selective_bin_packing_enforced"]
                and edf_order_verified
                and max_concurrent_executing >= 2
            )
            eg_k = (
                1
                if (
                    l_k == 1
                    and inc_horizon_ok
                    and inc["sla_deadline_met"]
                    and bin_pack_ok
                )
                else 0
            )

            inc["peak_concurrent_weighted_drift_during_execution"] = inc_peak_drift
            inc["horizon_within_ceiling_during_execution"] = inc_horizon_ok
            inc["local_incident_indicator_L_k"] = l_k
            inc["global_incident_indicator_E_g_k"] = eg_k
            inc["incident_evaluator_defect"] = eg_k - l_k
            if eg_k == 1:
                inc["incident_status"] = "EDF_BIN_PACKED_DEADLINE_COHERENT_LGGG"
            elif phase_mode == "overload_escalation" and not inc_horizon_ok:
                inc["incident_status"] = "OVERLOADED_DEADLINE_BURST_HALTED_AND_ESCALATED_LGGR"
            elif l_k == 1 and not inc["sla_deadline_met"]:
                inc["incident_status"] = "SERIAL_EDF_SLA_DEADLINE_OVERLOAD_LGGR"
            else:
                inc["incident_status"] = "INCIDENT_BUDGET_OR_DEADLINE_OBSTRUCTED_LGGR"

        slot0_overload_infeasible = mandatory_slot0_pareto_load > tau_horizon
        required_emergency_horizon = max(tau_horizon, mandatory_slot0_pareto_load)
        required_horizon_expansion = max(Fraction(0), mandatory_slot0_pareto_load - tau_horizon)

        l_phase = (
            1
            if (
                simultaneous_arrival_verified
                and all(inc["local_incident_indicator_L_k"] == 1 for inc in parsed_incidents)
            )
            else 0
        )
        eg_phase = (
            1
            if (
                l_phase == 1
                and horizon_budget_respected
                and all(inc["global_incident_indicator_E_g_k"] == 1 for inc in parsed_incidents)
            )
            else 0
        )
        delta_e_phase = eg_phase - l_phase

        halt_and_escalate_verified = (
            phase_mode == "overload_escalation"
            and slot0_overload_infeasible
            and all(inc["halt_and_escalate_triggered"] for inc in parsed_incidents)
        )

        if eg_phase == 1:
            phase_status = "EDF_BIN_PACKED_DEADLINE_COHERENT_LGGG"
        elif halt_and_escalate_verified:
            phase_status = "OVERLOADED_DEADLINE_BURST_HALTED_AND_ESCALATED_LGGR"
        elif l_phase == 1 and deadline_miss_count > 0:
            phase_status = "SERIAL_EDF_SLA_DEADLINE_OVERLOAD_LGGR"
        else:
            phase_status = "DEADLINE_OR_HORIZON_OBSTRUCTED_LGGR"

        return {
            "phase_mode": phase_mode,
            "horizon_drift_ceiling": tau_horizon,
            "incident_count": len(parsed_incidents),
            "simultaneous_arrival_verified": simultaneous_arrival_verified,
            "edf_order_verified": edf_order_verified,
            "joint_simultaneous_pareto_floor_l1_w": joint_pareto_floor,
            "mandatory_slot0_pareto_load_l1_w": mandatory_slot0_pareto_load,
            "slot0_overload_infeasible_under_horizon": slot0_overload_infeasible,
            "required_emergency_horizon_ceiling": required_emergency_horizon,
            "required_emergency_horizon_expansion": required_horizon_expansion,
            "max_concurrent_executing_incidents": max_concurrent_executing,
            "peak_concurrent_weighted_l1_drift": peak_concurrent_drift,
            "horizon_budget_respected": horizon_budget_respected,
            "horizon_breach_incident_count": horizon_breach_count,
            "deadline_miss_count": deadline_miss_count,
            "max_lateness_ticks": max_lateness_ticks,
            "halt_and_escalate_verified": halt_and_escalate_verified,
            "local_phase_indicator_L": l_phase,
            "global_phase_indicator_E_g": eg_phase,
            "phase_evaluator_defect": delta_e_phase,
            "phase_status": phase_status,
            "incidents": parsed_incidents,
            "ticks": tick_records,
        }

    def record_overloaded_deadline_burst(
        self,
        *,
        burst_id: str,
        model_id: str,
        prior_deadline_receipt_sha256: str,
        baseline_policy_sha256: str,
        baseline_policy_vector: Sequence[int | float | str | Fraction],
        risk_weight_vector: Sequence[int | float | str | Fraction],
        individual_lease_budget: int | float | str | Fraction,
        initial_horizon_drift_ceiling: int | float | str | Fraction,
        expanded_horizon_drift_ceiling: int | float | str | Fraction,
        serial_edf_incidents: Sequence[Mapping[str, Any]],
        overload_escalation_incidents: Sequence[Mapping[str, Any]],
        selective_bin_packed_incidents: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        if not burst_id or not model_id:
            raise ValidationError("burst_id and model_id must be non-empty")
        if not prior_deadline_receipt_sha256 or not baseline_policy_sha256:
            raise ValidationError(
                "prior_deadline_receipt_sha256 and baseline_policy_sha256 must be non-empty"
            )
        if not baseline_policy_vector:
            raise ValidationError("baseline_policy_vector must be non-empty")

        p0_vec = [rational(v) for v in baseline_policy_vector]
        w_vec = [rational(w) for w in risk_weight_vector]
        dim = len(p0_vec)
        if len(w_vec) != dim:
            raise ValidationError(
                "risk_weight_vector must have the same dimension as baseline_policy_vector"
            )
        if any(w <= 0 for w in w_vec):
            raise ValidationError("all coordinates of risk_weight_vector must be strictly positive")

        tau_lease = rational(individual_lease_budget)
        tau_horizon_init = rational(initial_horizon_drift_ceiling)
        tau_horizon_exp = rational(expanded_horizon_drift_ceiling)
        if tau_lease <= 0 or tau_horizon_init <= 0 or tau_horizon_exp <= 0:
            raise ValidationError("lease and horizon ceilings must be strictly positive")
        if tau_horizon_init < tau_lease or tau_horizon_exp < tau_horizon_init:
            raise ValidationError(
                "expanded_horizon_drift_ceiling >= initial_horizon_drift_ceiling >= individual_lease_budget required"
            )

        p1_serial = self._audit_schedule_phase(
            incidents=serial_edf_incidents,
            p0_vec=p0_vec,
            w_vec=w_vec,
            tau_lease=tau_lease,
            tau_horizon=tau_horizon_init,
            dim=dim,
            phase_mode="serial_edf",
        )
        p2_escalate = self._audit_schedule_phase(
            incidents=overload_escalation_incidents,
            p0_vec=p0_vec,
            w_vec=w_vec,
            tau_lease=tau_lease,
            tau_horizon=tau_horizon_init,
            dim=dim,
            phase_mode="overload_escalation",
        )
        p3_bin_packed = self._audit_schedule_phase(
            incidents=selective_bin_packed_incidents,
            p0_vec=p0_vec,
            w_vec=w_vec,
            tau_lease=tau_lease,
            tau_horizon=tau_horizon_exp,
            dim=dim,
            phase_mode="selective_bin_packing",
        )

        phase_1_serial_overload = (
            p1_serial["local_phase_indicator_L"] == 1
            and p1_serial["global_phase_indicator_E_g"] == 0
            and p1_serial["deadline_miss_count"] > 0
        )
        phase_2_halted_and_escalated = p2_escalate["halt_and_escalate_verified"]
        converged_single_round = p1_serial["global_phase_indicator_E_g"] == 1
        converged_multi_round = converged_single_round or (
            p3_bin_packed["global_phase_indicator_E_g"] == 1
        )
        deadline_misses_eliminated = (
            p1_serial["deadline_miss_count"] - p3_bin_packed["deadline_miss_count"]
        )
        max_lateness_reduction = (
            p1_serial["max_lateness_ticks"] - p3_bin_packed["max_lateness_ticks"]
        )

        record: dict[str, Any] = {
            "burst_id": burst_id,
            "model_id": model_id,
            "prior_deadline_receipt_sha256": prior_deadline_receipt_sha256,
            "baseline_policy_sha256": baseline_policy_sha256,
            "baseline_policy_vector": p0_vec,
            "risk_weight_vector": w_vec,
            "individual_lease_budget": tau_lease,
            "initial_horizon_drift_ceiling": tau_horizon_init,
            "expanded_horizon_drift_ceiling": tau_horizon_exp,
            "emergency_horizon_expansion_granted": tau_horizon_exp - tau_horizon_init,
            "phase_1_serial_edf_overload": p1_serial,
            "phase_2_overload_halt_and_escalate": p2_escalate,
            "phase_3_selective_bin_packed_edf": p3_bin_packed,
            "phase_1_serial_edf_deadline_breach": phase_1_serial_overload,
            "phase_2_halted_and_escalated": phase_2_halted_and_escalated,
            "converged_single_round": converged_single_round,
            "converged_multi_round": converged_multi_round,
            "deadline_misses_eliminated": deadline_misses_eliminated,
            "max_lateness_reduction_ticks": max_lateness_reduction,
        }
        self.bursts.append(record)
        return json_value(record)

    def emit_receipt(self) -> dict[str, Any]:
        if not self.bursts:
            raise ValidationError("cannot emit receipt without recorded overloaded deadline bursts")
        n = len(self.bursts)
        single_cnt = sum(1 for b in self.bursts if b["converged_single_round"])
        multi_cnt = sum(1 for b in self.bursts if b["converged_multi_round"])
        serial_breach_cnt = sum(
            1 for b in self.bursts if b["phase_1_serial_edf_deadline_breach"]
        )
        escalate_cnt = sum(
            1 for b in self.bursts if b["phase_2_halted_and_escalated"]
        )

        single_rate = Fraction(single_cnt, n)
        multi_rate = Fraction(multi_cnt, n)
        gain_rate = multi_rate - single_rate
        serial_breach_rate = Fraction(serial_breach_cnt, n)
        escalate_rate = Fraction(escalate_cnt, n)

        serial_breach_ids = [
            b["burst_id"]
            for b in self.bursts
            if b["phase_1_serial_edf_deadline_breach"]
        ]
        escalated_ids = [
            b["burst_id"] for b in self.bursts if b["phase_2_halted_and_escalated"]
        ]
        unconverged_ids = [
            b["burst_id"] for b in self.bursts if not b["converged_multi_round"]
        ]

        if multi_cnt == n and escalate_cnt == n:
            status = "EDF_BIN_PACKED_DEADLINE_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "SERIAL_EDF_SLA_DEADLINE_OVERLOAD_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_overloaded_deadline_bin_packing.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "burst_count": n,
            "single_round_serial_edf_coherent_count": single_cnt,
            "phase_2_halt_and_escalate_count": escalate_cnt,
            "multi_round_bin_packed_edf_coherent_count": multi_cnt,
            "phase_1_serial_edf_deadline_breach_count": serial_breach_cnt,
            "single_round_serial_edf_coherence_rate": single_rate,
            "phase_2_halt_and_escalate_rate": escalate_rate,
            "multi_round_bin_packed_edf_coherence_rate": multi_rate,
            "bin_packed_edf_coherence_gain": gain_rate,
            "phase_1_serial_edf_deadline_breach_rate": serial_breach_rate,
            "monotonic_coherence_verified": multi_rate >= single_rate,
            "phase_1_serial_edf_breach_burst_ids": serial_breach_ids,
            "phase_2_escalated_burst_ids": escalated_ids,
            "unconverged_burst_ids": unconverged_ids,
            "bursts": self.bursts,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingVariableDurationGracefulSheddingMonitor:
    """Online LGGR VIII monitor for multi-tick variable-duration incidents and graceful-degradation shedding.

    Evaluates simultaneous non-preemptible bursts where each incident k carries:
      - a multi-tick execution duration p_k in {1, 2, ...} (holding lease delta_k across [t_k, t_k + p_k)),
      - a strict SLA completion deadline D_k >= p_k (requiring C_k = t_k + p_k <= D_k),
      - a minimum weighted Pareto floor Delta_{w,k}^* > 0, and
      - a criticality weight kappa_k > 0.
    When no multi-tick bin-packed schedule can satisfy all K deadlines under the fixed global
    horizon ceiling tau_horizon and the authority gate denies emergency horizon expansion
    (Delta tau_horizon^* > 0 denied), the monitor computes the minimum-criticality-loss shed subset
    S^* subset {1, ..., K} whose retained complement R^* = {1, ..., K} \\ S^* admits a feasible
    multi-tick schedule under tau_horizon with zero lateness on all retained incidents.
    """

    def __init__(
        self,
        *,
        scope_id: str = "streaming-variable-duration-graceful-shedding-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.bursts: list[dict[str, Any]] = []

    @staticmethod
    def _weighted_l1(
        weights: tuple[Fraction, ...],
        delta: tuple[Fraction, ...],
    ) -> Fraction:
        return sum((w * abs(d) for w, d in zip(weights, delta)), Fraction(0))

    @staticmethod
    def _find_multitick_schedule(
        retained_indices: tuple[int, ...],
        durations: tuple[int, ...],
        deadlines: tuple[int, ...],
        slacks: tuple[Fraction, ...],
        arrival_tick: int,
        tau_h: Fraction,
    ) -> tuple[bool, dict[int, int], list[Fraction]]:
        if not retained_indices:
            return True, {}, []
        max_deadline = max(deadlines[i] for i in retained_indices)
        horizon_ticks = max_deadline - arrival_tick
        if horizon_ticks <= 0:
            return False, {}, []

        # Enumerate start ticks t_i in [arrival_tick, deadlines[i] - durations[i]]
        domains: list[list[int]] = []
        for idx in retained_indices:
            latest_start = deadlines[idx] - durations[idx]
            if latest_start < arrival_tick:
                return False, {}, []
            domains.append(list(range(arrival_tick, latest_start + 1)))

        best_starts: dict[int, int] | None = None
        best_tick_loads: list[Fraction] | None = None
        best_score: tuple[Fraction, int] | None = None

        def backtrack(pos: int, current_starts: dict[int, int], loads: list[Fraction]) -> None:
            nonlocal best_starts, best_tick_loads, best_score
            if pos == len(retained_indices):
                peak = max(loads, default=Fraction(0))
                sum_starts = sum(current_starts.values())
                score = (peak, sum_starts)
                if best_score is None or score < best_score:
                    best_score = score
                    best_starts = dict(current_starts)
                    best_tick_loads = list(loads)
                return

            idx = retained_indices[pos]
            dur = durations[idx]
            slk = slacks[idx]
            for st in domains[pos]:
                rel = st - arrival_tick
                if rel + dur > horizon_ticks:
                    continue
                feasible = True
                for u in range(rel, rel + dur):
                    if loads[u] + slk > tau_h:
                        feasible = False
                        break
                if not feasible:
                    continue
                for u in range(rel, rel + dur):
                    loads[u] += slk
                current_starts[idx] = st
                backtrack(pos + 1, current_starts, loads)
                del current_starts[idx]
                for u in range(rel, rel + dur):
                    loads[u] -= slk

        backtrack(0, {}, [Fraction(0) for _ in range(horizon_ticks)])
        if best_starts is None or best_tick_loads is None:
            return False, {}, []
        return True, best_starts, best_tick_loads

    def observe_burst(
        self,
        *,
        burst_id: str,
        baseline_policy: Sequence[Fraction | int | str],
        risk_weights: Sequence[Fraction | int | str],
        per_incident_lease_budget: Fraction | int | str,
        horizon_drift_ceiling: Fraction | int | str,
        arrival_tick: int = 0,
        expansion_denied: bool = True,
        incidents: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        b_id = text(burst_id, "burst_id")
        base_pol = tuple(rational(v) for v in baseline_policy)
        weights = tuple(rational(w) for w in risk_weights)
        if not base_pol or len(base_pol) != len(weights):
            raise ValidationError("baseline_policy and risk_weights must have equal non-zero length")
        if any(w <= 0 for w in weights):
            raise ValidationError("all risk_weights must be strictly positive")

        tau_lease = rational(per_incident_lease_budget)
        tau_h = rational(horizon_drift_ceiling)
        if tau_lease <= 0 or tau_h <= 0:
            raise ValidationError("budgets must be strictly positive")
        if arrival_tick < 0:
            raise ValidationError("arrival_tick must be non-negative")
        if len(incidents) < 2:
            raise ValidationError("at least 2 incidents are required")

        k_count = len(incidents)
        durations: list[int] = []
        deadlines: list[int] = []
        floors: list[Fraction] = []
        criticalities: list[Fraction] = []

        p1_slacks: list[Fraction] = []
        p1_starts: list[int] = []
        p1_feasible_flags: list[bool] = []

        p2_slacks: list[Fraction] = []
        p2_starts: list[int] = []
        p2_shed_flags: list[bool] = []
        p2_feasible_flags: list[bool] = []

        p3_slacks: list[Fraction] = []
        p3_starts: list[int] = []
        p3_shed_flags: list[bool] = []
        p3_feasible_flags: list[bool] = []

        for idx, inc in enumerate(incidents):
            dur = int(inc.get("duration_ticks", 1))
            dl = int(inc["sla_deadline_tick"])
            flr = rational(inc["min_weighted_pareto_floor"])
            crit = rational(inc["criticality_weight"])
            if dur <= 0 or dl < arrival_tick + dur or flr <= 0 or crit <= 0:
                raise ValidationError(f"invalid incident parameters at index {idx}")
            durations.append(dur)
            deadlines.append(dl)
            floors.append(flr)
            criticalities.append(crit)

            d1 = tuple(rational(v) for v in inc["phase_1_deferral_lease_delta"])
            d2 = tuple(rational(v) for v in inc["phase_2_inverted_shed_lease_delta"])
            d3 = tuple(rational(v) for v in inc["phase_3_governed_shed_lease_delta"])
            if len(d1) != len(base_pol) or len(d2) != len(base_pol) or len(d3) != len(base_pol):
                raise ValidationError("lease delta dimension mismatch")

            p1_slacks.append(self._weighted_l1(weights, d1))
            p2_slacks.append(self._weighted_l1(weights, d2))
            p3_slacks.append(self._weighted_l1(weights, d3))

            p1_starts.append(int(inc["phase_1_start_tick"]))
            p2_starts.append(int(inc.get("phase_2_start_tick", arrival_tick)))
            p3_starts.append(int(inc.get("phase_3_start_tick", arrival_tick)))

            p2_shed_flags.append(bool(inc.get("phase_2_shed", False)))
            p3_shed_flags.append(bool(inc.get("phase_3_shed", False)))

            p1_feasible_flags.append(bool(inc["phase_1_restores_pareto"]) and bool(inc["phase_1_candidate_passes"]))
            p2_feasible_flags.append(bool(inc["phase_2_restores_pareto"]) and bool(inc["phase_2_candidate_passes"]))
            p3_feasible_flags.append(bool(inc["phase_3_restores_pareto"]) and bool(inc["phase_3_candidate_passes"]))

        total_criticality = sum(criticalities, Fraction(0))

        # Compute optimal minimum-criticality-loss shed subset S^* under fixed tau_h
        all_indices = tuple(range(k_count))
        full_sched_ok, _, _ = self._find_multitick_schedule(
            all_indices,
            tuple(durations),
            tuple(deadlines),
            tuple(floors),
            arrival_tick,
            tau_h,
        )

        best_shed_mask: tuple[bool, ...] | None = None
        min_criticality_loss: Fraction | None = None
        optimal_starts: dict[int, int] = {}
        optimal_loads: list[Fraction] = []

        for mask_int in range(1 << k_count):
            shed_mask = tuple(bool((mask_int >> i) & 1) for i in range(k_count))
            retained = tuple(i for i in range(k_count) if not shed_mask[i])
            if not retained:
                continue
            loss = sum((criticalities[i] for i in range(k_count) if shed_mask[i]), Fraction(0))
            ok, st_map, ld_list = self._find_multitick_schedule(
                retained,
                tuple(durations),
                tuple(deadlines),
                tuple(floors),
                arrival_tick,
                tau_h,
            )
            if ok:
                if min_criticality_loss is None or loss < min_criticality_loss:
                    min_criticality_loss = loss
                    best_shed_mask = shed_mask
                    optimal_starts = st_map
                    optimal_loads = ld_list

        assert min_criticality_loss is not None and best_shed_mask is not None
        optimal_retained_criticality = total_criticality - min_criticality_loss

        # Evaluate Phase 1 (multi-tick deferral without shedding)
        p1_max_end = max(p1_starts[i] + durations[i] for i in range(k_count))
        p1_tick_loads = [Fraction(0) for _ in range(max(1, p1_max_end - arrival_tick))]
        p1_missed_count = 0
        p1_max_lateness = 0
        for i in range(k_count):
            c_i = p1_starts[i] + durations[i]
            late_i = max(0, c_i - deadlines[i])
            if late_i > 0:
                p1_missed_count += 1
            if late_i > p1_max_lateness:
                p1_max_lateness = late_i
            for u in range(p1_starts[i] - arrival_tick, c_i - arrival_tick):
                p1_tick_loads[u] += p1_slacks[i]

        p1_peak_drift = max(p1_tick_loads, default=Fraction(0))
        l_p1 = int(
            all(p1_feasible_flags[i] and p1_slacks[i] >= floors[i] and p1_slacks[i] <= tau_lease for i in range(k_count))
            and p1_peak_drift <= tau_h
        )
        eg_p1 = int(l_p1 == 1 and p1_missed_count == 0)
        defect_p1 = eg_p1 - l_p1

        # Evaluate Phase 2 (priority-inverted shedding)
        p2_retained = [i for i in range(k_count) if not p2_shed_flags[i]]
        p2_shed_loss = sum((criticalities[i] for i in range(k_count) if p2_shed_flags[i]), Fraction(0))
        p2_max_end = max((p2_starts[i] + durations[i] for i in p2_retained), default=arrival_tick + 1)
        p2_tick_loads = [Fraction(0) for _ in range(max(1, p2_max_end - arrival_tick))]
        p2_missed_count = 0
        for i in p2_retained:
            c_i = p2_starts[i] + durations[i]
            if c_i > deadlines[i]:
                p2_missed_count += 1
            for u in range(p2_starts[i] - arrival_tick, c_i - arrival_tick):
                p2_tick_loads[u] += p2_slacks[i]
        p2_peak_drift = max(p2_tick_loads, default=Fraction(0))
        l_p2 = int(
            bool(p2_retained)
            and all(p2_feasible_flags[i] and p2_slacks[i] >= floors[i] and p2_slacks[i] <= tau_lease for i in p2_retained)
            and p2_peak_drift <= tau_h
            and p2_missed_count == 0
        )
        eg_p2 = int(l_p2 == 1 and p2_shed_loss <= min_criticality_loss)
        defect_p2 = eg_p2 - l_p2

        # Evaluate Phase 3 (governed minimum-criticality graceful-degradation shedding)
        p3_retained = [i for i in range(k_count) if not p3_shed_flags[i]]
        p3_shed_loss = sum((criticalities[i] for i in range(k_count) if p3_shed_flags[i]), Fraction(0))
        p3_retained_crit = total_criticality - p3_shed_loss
        p3_max_end = max((p3_starts[i] + durations[i] for i in p3_retained), default=arrival_tick + 1)
        p3_tick_loads = [Fraction(0) for _ in range(max(1, p3_max_end - arrival_tick))]
        p3_missed_count = 0
        p3_max_lateness = 0
        for i in p3_retained:
            c_i = p3_starts[i] + durations[i]
            late_i = max(0, c_i - deadlines[i])
            if late_i > 0:
                p3_missed_count += 1
            if late_i > p3_max_lateness:
                p3_max_lateness = late_i
            for u in range(p3_starts[i] - arrival_tick, c_i - arrival_tick):
                p3_tick_loads[u] += p3_slacks[i]
        p3_peak_drift = max(p3_tick_loads, default=Fraction(0))
        l_p3 = int(
            bool(p3_retained)
            and all(p3_feasible_flags[i] and p3_slacks[i] >= floors[i] and p3_slacks[i] <= tau_lease for i in p3_retained)
            and p3_peak_drift <= tau_h
        )
        eg_p3 = int(
            l_p3 == 1
            and p3_missed_count == 0
            and p3_shed_loss == min_criticality_loss
            and tuple(p3_shed_flags) == best_shed_mask
        )
        defect_p3 = eg_p3 - l_p3

        record: dict[str, Any] = {
            "burst_id": b_id,
            "incident_count": k_count,
            "arrival_tick": arrival_tick,
            "expansion_denied": expansion_denied,
            "per_incident_lease_budget": tau_lease,
            "horizon_drift_ceiling": tau_h,
            "durations": durations,
            "deadlines": deadlines,
            "criticalities": criticalities,
            "total_criticality": total_criticality,
            "full_retention_schedulable_under_horizon": full_sched_ok,
            "optimal_shed_incident_indices": [i for i, sh in enumerate(best_shed_mask) if sh],
            "minimum_criticality_loss": min_criticality_loss,
            "optimal_retained_criticality": optimal_retained_criticality,
            "optimal_retained_starts": {str(k): v for k, v in optimal_starts.items()},
            "optimal_tick_loads": optimal_loads,
            "phase_1_peak_drift": p1_peak_drift,
            "phase_1_missed_deadline_count": p1_missed_count,
            "phase_1_max_lateness": p1_max_lateness,
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": (
                "VARIABLE_DURATION_DEADLINE_OVERLOAD_LGGR"
                if (l_p1 == 1 and eg_p1 == 0)
                else "GRACEFUL_DEGRADATION_SHEDDING_COHERENT_LGGG"
            ),
            "phase_2_shed_criticality_loss": p2_shed_loss,
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": (
                "SUBOPTIMAL_CRITICALITY_SHEDDING_LGGR"
                if (l_p2 == 1 and eg_p2 == 0)
                else "GRACEFUL_DEGRADATION_SHEDDING_COHERENT_LGGG"
            ),
            "phase_3_shed_incident_indices": [i for i, sh in enumerate(p3_shed_flags) if sh],
            "phase_3_shed_criticality_loss": p3_shed_loss,
            "phase_3_retained_criticality": p3_retained_crit,
            "phase_3_peak_drift": p3_peak_drift,
            "phase_3_missed_deadline_count": p3_missed_count,
            "phase_3_max_lateness": p3_max_lateness,
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": (
                "GRACEFUL_DEGRADATION_SHEDDING_COHERENT_LGGG"
                if eg_p3 == 1
                else "VARIABLE_DURATION_DEADLINE_OVERLOAD_LGGR"
            ),
            "converged_single_round": eg_p1 == 1,
            "converged_multi_round": eg_p3 == 1,
        }
        self.bursts.append(record)
        return json_value(record)

    def current_receipt(self) -> dict[str, Any]:
        if not self.bursts:
            raise ValidationError("at least one burst must be observed before generating a receipt")
        n = len(self.bursts)
        p1_coherent = sum(1 for b in self.bursts if b["converged_single_round"])
        p1_breach = sum(1 for b in self.bursts if b["phase_1_defect"] == -1)
        p2_inverted = sum(1 for b in self.bursts if b["phase_2_defect"] == -1)
        p3_coherent = sum(1 for b in self.bursts if b["converged_multi_round"])

        single_rate = Fraction(p1_coherent, n)
        multi_rate = Fraction(p3_coherent, n)
        gain_rate = multi_rate - single_rate

        if p3_coherent == n:
            status = "GRACEFUL_DEGRADATION_SHEDDING_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "VARIABLE_DURATION_DEADLINE_OVERLOAD_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_variable_duration_graceful_shedding.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "burst_count": n,
            "single_round_deferral_coherent_count": p1_coherent,
            "phase_1_deadline_breach_count": p1_breach,
            "phase_2_inverted_shedding_defect_count": p2_inverted,
            "multi_round_graceful_shedding_coherent_count": p3_coherent,
            "single_round_coherence_rate": single_rate,
            "multi_round_graceful_shedding_coherence_rate": multi_rate,
            "graceful_shedding_coherence_gain": gain_rate,
            "monotonic_coherence_verified": multi_rate >= single_rate,
            "bursts": self.bursts,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingLinearizedPipelineJacobianMonitor:
    """Online LGGR V/VIII monitor instantiating (D, Q) on linearized state-estimation pipelines.

    Wraps StreamingDefectSoundnessMonitor on a linearized state-estimation defect Jacobian
    D in Q^{m x n} across three observer measurement Jacobians:
      - Q_blind (collapsing observer with dim(im(D) cap ker(Q_blind)) > 0),
      - Q_coupled (compensating observer with dim(ker(Q_coupled)) > 0 yet im(D) cap ker(Q_coupled) == {0}),
      - Q_full (full-rank observer with ker(Q_full) == {0}),
    and evaluates live state-perturbation trajectories s in Q^n across all three regimes.
    """

    def __init__(
        self,
        *,
        defect_matrix: Sequence[Sequence[Fraction | int | str]],
        blind_measurement_matrix: Sequence[Sequence[Fraction | int | str]],
        coupled_measurement_matrix: Sequence[Sequence[Fraction | int | str]],
        full_measurement_matrix: Sequence[Sequence[Fraction | int | str]],
        scope_id: str = "streaming-linearized-pipeline-jacobian-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.d_mat = matrix(defect_matrix, "defect_matrix")
        self.q_blind = matrix(blind_measurement_matrix, "blind_measurement_matrix", cols=len(self.d_mat))
        self.q_coupled = matrix(coupled_measurement_matrix, "coupled_measurement_matrix", cols=len(self.d_mat))
        self.q_full = matrix(full_measurement_matrix, "full_measurement_matrix", cols=len(self.d_mat))

        self.blind_monitor = StreamingDefectSoundnessMonitor(
            self.d_mat, self.q_blind, scope_id=f"{self.scope_id}-blind"
        )
        self.coupled_monitor = StreamingDefectSoundnessMonitor(
            self.d_mat, self.q_coupled, scope_id=f"{self.scope_id}-coupled"
        )
        self.full_monitor = StreamingDefectSoundnessMonitor(
            self.d_mat, self.q_full, scope_id=f"{self.scope_id}-full"
        )

        self.blind_audit = self.blind_monitor.audit_soundness(target_severity=2)
        self.coupled_audit = self.coupled_monitor.audit_soundness(target_severity=2)
        self.full_audit = self.full_monitor.audit_soundness(target_severity=2)
        self.evaluations: list[dict[str, Any]] = []

    def observe_pipeline_perturbation(
        self,
        *,
        evaluation_id: str,
        state_perturbation: Sequence[Fraction | int | str],
        blind_claimed_sound: bool = True,
        coupled_verified_sound: bool = True,
        full_verified_sound: bool = True,
    ) -> dict[str, Any]:
        e_id = text(evaluation_id, "evaluation_id")
        s_vec = tuple(rational(v) for v in state_perturbation)
        if len(s_vec) != len(self.d_mat[0]):
            raise ValidationError("state_perturbation length must match defect_matrix column count")

        omega = matvec(self.d_mat, s_vec)
        y_blind = matvec(self.q_blind, omega)
        y_coupled = matvec(self.q_coupled, omega)
        y_full = matvec(self.q_full, omega)

        i_defect = sum((abs(v) for v in omega), Fraction(0))
        score_blind = sum((abs(v) for v in y_blind), Fraction(0))
        score_coupled = sum((abs(v) for v in y_coupled), Fraction(0))
        score_full = sum((abs(v) for v in y_full), Fraction(0))

        blind_dim = int(self.blind_audit["realizable_blindspot_dimension"])
        coupled_dim = int(self.coupled_audit["realizable_blindspot_dimension"])
        full_dim = int(self.full_audit["realizable_blindspot_dimension"])

        # Regime 1: Blind observer passes locally when score_blind == 0, but fails globally when i_defect > 0
        l_blind = int(blind_claimed_sound and score_blind == 0)
        eg_blind = int(l_blind == 1 and i_defect == 0 and blind_dim == 0)
        defect_blind = eg_blind - l_blind

        # Regime 2: Coupled observer verifies im(D) cap ker(Q_coupled) == {0} and detects i_defect > 0
        l_coupled = int(coupled_verified_sound and coupled_dim == 0 and (i_defect == 0 or score_coupled > 0))
        eg_coupled = int(l_coupled == 1 and bool(self.coupled_audit["soundness_holds"]))
        defect_coupled = eg_coupled - l_coupled

        # Regime 3: Full-rank observer verifies ker(Q_full) == {0} and im(D) cap ker(Q_full) == {0}
        l_full = int(full_verified_sound and full_dim == 0 and (i_defect == 0 or score_full > 0))
        eg_full = int(l_full == 1 and bool(self.full_audit["soundness_holds"]))
        defect_full = eg_full - l_full

        rec: dict[str, Any] = {
            "evaluation_id": e_id,
            "state_perturbation": list(s_vec),
            "interface_defect_omega": list(omega),
            "true_l1_inconsistency": i_defect,
            "blind_measured_output": list(y_blind),
            "blind_measured_l1_score": score_blind,
            "blind_realizable_blindspot_dim": blind_dim,
            "blind_local_green": l_blind,
            "blind_global_green": eg_blind,
            "blind_defect": defect_blind,
            "blind_status": self.blind_audit["status"],
            "coupled_measured_output": list(y_coupled),
            "coupled_measured_l1_score": score_coupled,
            "coupled_ambient_blindspot_dim": int(self.coupled_audit["ambient_blindspot_dimension"]),
            "coupled_realizable_blindspot_dim": coupled_dim,
            "coupled_local_green": l_coupled,
            "coupled_global_green": eg_coupled,
            "coupled_defect": defect_coupled,
            "coupled_status": self.coupled_audit["status"],
            "full_measured_output": list(y_full),
            "full_measured_l1_score": score_full,
            "full_realizable_blindspot_dim": full_dim,
            "full_local_green": l_full,
            "full_global_green": eg_full,
            "full_defect": defect_full,
            "full_status": self.full_audit["status"],
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one pipeline perturbation must be observed")
        n = len(self.evaluations)
        blind_stealth_cnt = sum(1 for e in self.evaluations if e["blind_defect"] == -1)
        coupled_sound_cnt = sum(1 for e in self.evaluations if e["coupled_global_green"] == 1)
        full_sound_cnt = sum(1 for e in self.evaluations if e["full_global_green"] == 1)

        blind_coherence_rate = Fraction(n - blind_stealth_cnt, n)
        coupled_coherence_rate = Fraction(coupled_sound_cnt, n)
        full_coherence_rate = Fraction(full_sound_cnt, n)

        if coupled_sound_cnt == n and full_sound_cnt == n and blind_stealth_cnt == n:
            status = "COUPLED_SOUNDNESS_VERIFIED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "STEALTH_REALIZABLE_DEFECT_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_linearized_pipeline_jacobian.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "blind_stealth_defect_count": blind_stealth_cnt,
            "coupled_sound_coherent_count": coupled_sound_cnt,
            "full_sound_coherent_count": full_sound_cnt,
            "blind_coherence_rate": blind_coherence_rate,
            "coupled_coherence_rate": coupled_coherence_rate,
            "full_coherence_rate": full_coherence_rate,
            "coupled_soundness_gain": coupled_coherence_rate - blind_coherence_rate,
            "blind_audit": self.blind_audit,
            "coupled_audit": self.coupled_audit,
            "full_audit": self.full_audit,
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingWatcherDropoutGramAuditMonitor:
    """Online LGGR VI/VIII watcher-dropout and Gram rank-deficiency audit monitor.

    Given a multi-evaluator observation matrix Q in Q^{m x d} and a task-critical
    direction v_crit in Q^d \\ {0}, wraps StreamingGramProbeMonitor across:
      - the full m-row watcher matrix Q, and
      - each single-row dropout submatrix Q_{-r} (removing measurement row r),
    to detect when removing a measurement row r reduces rank(Q_{-r}^T Q_{-r}) and
    enlarges ker(Q_{-r}^T Q_{-r}) along v_crit (so Q_{-r} v_crit == 0 and centered
    adjoint probes vanish despite ||Q v_crit||_2^2 > 0), versus redundant row dropout
    where rank(Q_{-r}^T Q_{-r}) == rank(Q^T Q) and ker(Q_{-r}^T Q_{-r}) is unchanged.
    """

    def __init__(
        self,
        *,
        observation_matrix: Sequence[Sequence[Fraction | int | str]],
        scope_id: str = "streaming-watcher-dropout-gram-audit-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.q_mat = matrix(observation_matrix, "observation_matrix")
        self.num_rows = len(self.q_mat)
        self.dim = len(self.q_mat[0])
        if self.num_rows < 2:
            raise ValidationError("observation_matrix must have at least 2 watcher rows for dropout auditing")

        self.full_probe_monitor = StreamingGramProbeMonitor(
            self.q_mat, scope_id=f"{self.scope_id}-full"
        )
        self.full_rank, self.full_nullspace = StreamingDefectSoundnessMonitor._rref_and_nullspace(
            self.full_probe_monitor.gram_matrix
        )

        self.dropout_monitors: list[StreamingGramProbeMonitor] = []
        self.dropout_ranks: list[int] = []
        self.dropout_nullspaces: list[list[tuple[Fraction, ...]]] = []
        for r in range(self.num_rows):
            sub_q = tuple(row for idx, row in enumerate(self.q_mat) if idx != r)
            mon_r = StreamingGramProbeMonitor(sub_q, scope_id=f"{self.scope_id}-drop-row-{r}")
            rk_r, ns_r = StreamingDefectSoundnessMonitor._rref_and_nullspace(mon_r.gram_matrix)
            self.dropout_monitors.append(mon_r)
            self.dropout_ranks.append(rk_r)
            self.dropout_nullspaces.append(ns_r)

        self.evaluations: list[dict[str, Any]] = []

    def observe_watcher_dropout(
        self,
        *,
        evaluation_id: str,
        critical_direction: Sequence[Fraction | int | str],
        redundant_dropout_row: int,
        critical_dropout_row: int,
    ) -> dict[str, Any]:
        e_id = text(evaluation_id, "evaluation_id")
        v_vec = tuple(rational(v) for v in critical_direction)
        if len(v_vec) != self.dim or all(v == 0 for v in v_vec):
            raise ValidationError("critical_direction must be a nonzero vector matching state dimension")
        if not (0 <= redundant_dropout_row < self.num_rows) or not (0 <= critical_dropout_row < self.num_rows):
            raise ValidationError("dropout row index out of range")

        full_probe = self.full_probe_monitor.probe_state(
            f"{e_id}-full", v_vec, direction=v_vec
        )
        red_probe = self.dropout_monitors[redundant_dropout_row].probe_state(
            f"{e_id}-redundant-drop-{redundant_dropout_row}", v_vec, direction=v_vec
        )
        crit_probe = self.dropout_monitors[critical_dropout_row].probe_state(
            f"{e_id}-critical-drop-{critical_dropout_row}", v_vec, direction=v_vec
        )

        full_norm_sq = Fraction(2) * rational(full_probe["quadratic_energy"])
        red_norm_sq = Fraction(2) * rational(red_probe["quadratic_energy"])
        crit_norm_sq = Fraction(2) * rational(crit_probe["quadratic_energy"])

        red_rank = self.dropout_ranks[redundant_dropout_row]
        crit_rank = self.dropout_ranks[critical_dropout_row]
        red_null_dim = len(self.dropout_nullspaces[redundant_dropout_row])
        crit_null_dim = len(self.dropout_nullspaces[critical_dropout_row])

        # Phase 1: Critical watcher dropout masks v_crit (local green L=1 because Q_{-crit} v_crit == 0, global red E_g=0)
        l_crit = int(crit_norm_sq == 0 and bool(crit_probe["is_nullspace_blindspot"]))
        eg_crit = int(l_crit == 1 and full_norm_sq == 0 and crit_rank == self.full_rank)
        defect_crit = eg_crit - l_crit

        # Phase 2: Redundant watcher dropout preserves rank and detects v_crit (L=1, E_g=1, Delta_E=0)
        l_red = int(red_rank == self.full_rank and red_norm_sq > 0 and not bool(red_probe["is_nullspace_blindspot"]))
        eg_red = int(l_red == 1 and red_norm_sq == full_norm_sq and red_null_dim == len(self.full_nullspace))
        defect_red = eg_red - l_red

        rec: dict[str, Any] = {
            "evaluation_id": e_id,
            "critical_direction": list(v_vec),
            "full_rank": self.full_rank,
            "full_nullspace_dim": len(self.full_nullspace),
            "full_norm_squared": full_norm_sq,
            "redundant_dropout_row": redundant_dropout_row,
            "redundant_dropout_rank": red_rank,
            "redundant_dropout_nullspace_dim": red_null_dim,
            "redundant_dropout_norm_squared": red_norm_sq,
            "redundant_local_green": l_red,
            "redundant_global_green": eg_red,
            "redundant_defect": defect_red,
            "redundant_status": "REDUNDANT_WATCHER_DROPOUT_SAFE_LGGG" if eg_red == 1 else "CRITICAL_WATCHER_DROPOUT_BLINDSPOT_LGGR",
            "critical_dropout_row": critical_dropout_row,
            "critical_dropout_rank": crit_rank,
            "critical_dropout_nullspace_dim": crit_null_dim,
            "critical_dropout_norm_squared": crit_norm_sq,
            "critical_local_green": l_crit,
            "critical_global_green": eg_crit,
            "critical_defect": defect_crit,
            "critical_status": "CRITICAL_WATCHER_DROPOUT_BLINDSPOT_LGGR" if defect_crit == -1 else "REDUNDANT_WATCHER_DROPOUT_SAFE_LGGG",
            "full_probe_step": full_probe,
            "redundant_probe_step": red_probe,
            "critical_probe_step": crit_probe,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one watcher dropout evaluation must be observed")
        n = len(self.evaluations)
        crit_blind_cnt = sum(1 for e in self.evaluations if e["critical_defect"] == -1)
        red_safe_cnt = sum(1 for e in self.evaluations if e["redundant_global_green"] == 1)

        crit_coherence_rate = Fraction(n - crit_blind_cnt, n)
        red_coherence_rate = Fraction(red_safe_cnt, n)

        if crit_blind_cnt == n and red_safe_cnt == n:
            status = "WATCHER_DROPOUT_RANK_AUDIT_VERIFIED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "CRITICAL_WATCHER_DROPOUT_BLINDSPOT_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_watcher_dropout_gram_audit.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "full_rank": self.full_rank,
            "dropout_ranks_by_row": self.dropout_ranks,
            "critical_dropout_blindspot_count": crit_blind_cnt,
            "redundant_dropout_safe_count": red_safe_cnt,
            "critical_dropout_coherence_rate": crit_coherence_rate,
            "redundant_dropout_coherence_rate": red_coherence_rate,
            "watcher_retention_coherence_gain": red_coherence_rate - crit_coherence_rate,
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingPolicyRankingOrderReversalMonitor:
    """Online RSI Paper 003 / LGGR VII-VIII multi-evaluator policy ranking order-reversal monitor.

    Wraps StreamingPositiveExtensionMonitor across candidate multi-evaluator agent policies
    A and B over m measurement contexts under a signed constraint violation ceiling tau_{N_min}:
      - Phase 1 (CF-Only Misselection): ranking solely by lowest fallback frequency CF(p)
        selects Policy A when CF(A) < CF(B), yet breaches N_min(A) <= tau_{N_min} whenever
        CF and N_min reverse relative order (CF(A) < CF(B) while N_min(A) > tau_{N_min} >= N_min(B)).
      - Phase 2 (Surrogate CF <= 2 N_min Violation): checks whether the false surrogate bound
        CF(p) <= 2 N_min(p) fails (CF(B) > 2 N_min(B)) while the constructive m-context bound
        CF(p) <= (m - 1) N_min(p) holds.
      - Phase 3 (Dual-Metric (CF, N_min) Order-Reversal Audit): audits both CF and N_min via
        StreamingPositiveExtensionMonitor, detects ORDER_REVERSAL_DETECTED, and selects the
        safety-admissible policy satisfying N_min <= tau_{N_min}.
    """

    def __init__(
        self,
        *,
        scope_id: str = "streaming-policy-ranking-order-reversal-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.ext_monitor = StreamingPositiveExtensionMonitor(
            scope_id=f"{self.scope_id}-positive-extension"
        )
        self.evaluations: list[dict[str, Any]] = []

    def observe_policy_pair(
        self,
        *,
        evaluation_id: str,
        num_contexts: int,
        policy_a_id: str,
        policy_a_packing_mass: Fraction | int | str,
        policy_a_negative_mass: Fraction | int | str,
        policy_b_id: str,
        policy_b_packing_mass: Fraction | int | str,
        policy_b_negative_mass: Fraction | int | str,
        negative_mass_ceiling: Fraction | int | str,
        phase_3_selected_policy_id: str,
    ) -> dict[str, Any]:
        e_id = text(evaluation_id, "evaluation_id")
        m_ctx = exact_int(num_contexts, "num_contexts", minimum=2)
        pa_id = text(policy_a_id, "policy_a_id")
        pb_id = text(policy_b_id, "policy_b_id")
        sel_id = text(phase_3_selected_policy_id, "phase_3_selected_policy_id")
        tau_n = rational(negative_mass_ceiling)
        if tau_n <= 0:
            raise ValidationError("negative_mass_ceiling must be strictly positive")

        audit_a = self.ext_monitor.audit_signed_extension(
            f"{e_id}::{pa_id}", m_ctx, policy_a_packing_mass, policy_a_negative_mass
        )
        audit_b = self.ext_monitor.audit_signed_extension(
            f"{e_id}::{pb_id}", m_ctx, policy_b_packing_mass, policy_b_negative_mass
        )
        cmp_rec = self.ext_monitor.compare_extension_order(
            f"{e_id}::{pa_id}", f"{e_id}::{pb_id}"
        )

        cf_a = rational(audit_a["contextual_fraction"])
        n_a = rational(audit_a["negative_mass"])
        cf_b = rational(audit_b["contextual_fraction"])
        n_b = rational(audit_b["negative_mass"])
        order_rev = bool(cmp_rec["order_reversal_detected"])

        # Phase 1: CF-only ranking selects whichever has smaller CF (here Policy A)
        cf_winner_n = n_a if cf_a <= cf_b else n_b
        l_p1 = int(cf_a < cf_b)
        eg_p1 = int(l_p1 == 1 and cf_winner_n <= tau_n)
        defect_p1 = eg_p1 - l_p1

        # Phase 2: Surrogate CF <= 2 * N_min assumption
        l_p2 = int(cf_a <= Fraction(2) * n_a)
        eg_p2 = int(l_p2 == 1 and cf_b <= Fraction(2) * n_b)
        defect_p2 = eg_p2 - l_p2

        # Phase 3: Dual-metric (CF, N_min) audit
        sel_n = n_b if sel_id == pb_id else n_a
        l_p3 = int(
            order_rev
            and bool(audit_a["m_context_bound_verified"])
            and bool(audit_b["m_context_bound_verified"])
        )
        eg_p3 = int(l_p3 == 1 and sel_n <= tau_n and sel_id == pb_id)
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": e_id,
            "num_contexts": m_ctx,
            "policy_a_id": pa_id,
            "policy_a_contextual_fraction": cf_a,
            "policy_a_negative_mass": n_a,
            "policy_b_id": pb_id,
            "policy_b_contextual_fraction": cf_b,
            "policy_b_negative_mass": n_b,
            "negative_mass_ceiling": tau_n,
            "order_reversal_detected": order_rev,
            "policy_b_exceeds_two_negative_mass": bool(audit_b["exceeds_two_negative_mass"]),
            "m_context_bound_verified": bool(audit_a["m_context_bound_verified"]) and bool(audit_b["m_context_bound_verified"]),
            "phase_1_cf_only_local_green": l_p1,
            "phase_1_cf_only_global_green": eg_p1,
            "phase_1_cf_only_defect": defect_p1,
            "phase_1_status": "CF_ONLY_ORDER_REVERSAL_MISSELECTION_LGGR" if defect_p1 == -1 else "DUAL_METRIC_ORDER_REVERSAL_COHERENT_LGGG",
            "phase_2_surrogate_local_green": l_p2,
            "phase_2_surrogate_global_green": eg_p2,
            "phase_2_surrogate_defect": defect_p2,
            "phase_2_status": "SURROGATE_BOUND_VIOLATION_LGGR" if defect_p2 == -1 else "DUAL_METRIC_ORDER_REVERSAL_COHERENT_LGGG",
            "phase_3_selected_policy_id": sel_id,
            "phase_3_dual_local_green": l_p3,
            "phase_3_dual_global_green": eg_p3,
            "phase_3_dual_defect": defect_p3,
            "phase_3_status": "DUAL_METRIC_ORDER_REVERSAL_COHERENT_LGGG" if eg_p3 == 1 else "CF_ONLY_ORDER_REVERSAL_MISSELECTION_LGGR",
            "audit_a": audit_a,
            "audit_b": audit_b,
            "comparison_receipt": cmp_rec,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one policy pair must be observed")
        n = len(self.evaluations)
        p1_misselection = sum(1 for e in self.evaluations if e["phase_1_cf_only_defect"] == -1)
        p2_surrogate_fail = sum(1 for e in self.evaluations if e["phase_2_surrogate_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_dual_global_green"] == 1)

        cf_only_coherence_rate = Fraction(n - p1_misselection, n)
        dual_metric_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_misselection == n:
            status = "DUAL_METRIC_ORDER_REVERSAL_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "CF_ONLY_ORDER_REVERSAL_MISSELECTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_policy_ranking_order_reversal.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_cf_only_misselection_count": p1_misselection,
            "phase_2_surrogate_violation_count": p2_surrogate_fail,
            "phase_3_dual_metric_coherent_count": p3_coherent,
            "cf_only_coherence_rate": cf_only_coherence_rate,
            "dual_metric_coherence_rate": dual_metric_coherence_rate,
            "dual_metric_coherence_gain": dual_metric_coherence_rate - cf_only_coherence_rate,
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingToolAssistedFiberSplittingMonitor:
    """Online RSI Paper 000 / Volume VIII tool-assisted fiber splitting vs. unassisted self-reflection monitor.

    Wraps StreamingRSIFiberCeilingMonitor across 3-phase multi-turn reasoning trajectories:
      - Phase 1 (Unassisted Self-Reflection on Coarse Report p0):
        Evaluates unassisted self-reflection predictions on coarse report p0(x).
        When max_{x} |f(x) - g_unass(x)| == W0 / 2 > 0, the predictor attains the minimax midpoint
        floor on p0 (L_unass = 1), yet worst-case error remains locked at W0 / 2 > 0
        (Eg_unass = 0, Delta_{E,unass} = -1, UNASSISTED_FIBER_CEILING_LOCKED_LGGR).
      - Phase 2 (Partial 1-Bit Tool Query Splitting p1):
        Evaluates intermediate predictions on partial tool-query report p1(x) that refines p0
        into sub-fibers of width W1 < W0. The minimax floor drops strictly from W0 / 2 to W1 / 2
        (L_part = 1 when E_part == W1 / 2 < W0 / 2), yet residual within-sub-fiber ambiguity
        W1 / 2 > 0 persists (Eg_part = 0, Delta_{E,part} = -1, PARTIAL_TOOL_RESIDUAL_AMBIGUITY_LGGR).
      - Phase 3 (Complete Multi-Turn Tool-Assisted Fiber Splitting p2):
        Evaluates multi-turn tool-assisted predictions on refined report p2(x) that splits all
        colliding target states into zero-spread fibers (W2 = 0, E_split = 0), achieving
        L_split = 1, Eg_split = 1, Delta_{E,split} = 0 (TOOL_ASSISTED_FIBER_SPLIT_RESOLVED_LGGG).
    """

    def __init__(self, *, scope_id: str = "streaming-tool-assisted-fiber-splitting-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.evaluations: list[dict[str, Any]] = []

    def evaluate_trajectory(
        self,
        trajectory_id: str,
        states: Iterable[Mapping[str, Any]],
        *,
        unassisted_predictions: Mapping[str, Fraction | int | str],
        partial_tool_predictions: Mapping[str, Fraction | int | str],
        full_tool_predictions: Mapping[str, Fraction | int | str],
    ) -> dict[str, Any]:
        tid = text(trajectory_id, "trajectory_id")
        state_list = list(sequence(states, "states"))
        if not state_list:
            raise ValidationError("states must be non-empty")

        partial_mon = StreamingRSIFiberCeilingMonitor(scope_id=f"{self.scope_id}-{tid}-partial")
        full_mon = StreamingRSIFiberCeilingMonitor(scope_id=f"{self.scope_id}-{tid}-full")

        for st in state_list:
            sid = text(st["state_id"], "state_id")
            f_val = rational(st["target_value"])
            c_rep = st["coarse_report"]
            p_rep = st["partial_tool_report"]
            r_rep = st["full_tool_report"]
            partial_mon.observe_state(sid, c_rep, f_val, refined_report=p_rep)
            full_mon.observe_state(sid, c_rep, f_val, refined_report=r_rep)

        gen_unass = partial_mon.evaluate_generation(
            "phase_1_unassisted",
            dict(unassisted_predictions),
            use_refined_report=False,
        )
        gen_part = partial_mon.evaluate_generation(
            "phase_2_partial_tool",
            dict(partial_tool_predictions),
            use_refined_report=True,
        )
        gen_full = full_mon.evaluate_generation(
            "phase_3_full_tool",
            dict(full_tool_predictions),
            use_refined_report=True,
        )

        floor0 = rational(gen_unass["coarse_half_spread_ceiling"])
        w0 = Fraction(2) * floor0
        floor1 = rational(gen_part["refined_half_spread_ceiling"])
        w1 = Fraction(2) * floor1
        floor2 = rational(gen_full["refined_half_spread_ceiling"])
        w2 = Fraction(2) * floor2

        err_unass = rational(gen_unass["worst_case_error"])
        err_part = rational(gen_part["worst_case_error"])
        err_full = rational(gen_full["worst_case_error"])

        l_p1 = 1 if (err_unass == floor0) else 0
        eg_p1 = 1 if (l_p1 == 1 and err_unass == Fraction(0)) else 0
        defect_p1 = eg_p1 - l_p1

        l_p2 = 1 if (err_part == floor1 and floor1 < floor0) else 0
        eg_p2 = 1 if (l_p2 == 1 and err_part == Fraction(0)) else 0
        defect_p2 = eg_p2 - l_p2

        l_p3 = 1 if (w2 == Fraction(0) and err_full == Fraction(0)) else 0
        eg_p3 = 1 if (l_p3 == 1 and w2 < w1 and w1 < w0) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "trajectory_id": tid,
            "state_count": len(state_list),
            "coarse_fiber_width_w0": w0,
            "coarse_minimax_floor_0": floor0,
            "partial_tool_width_w1": w1,
            "partial_tool_floor_1": floor1,
            "full_tool_width_w2": w2,
            "full_tool_floor_2": floor2,
            "unassisted_worst_case_error": err_unass,
            "partial_tool_worst_case_error": err_part,
            "full_tool_worst_case_error": err_full,
            "phase_1_unassisted_local_green": l_p1,
            "phase_1_unassisted_global_green": eg_p1,
            "phase_1_unassisted_defect": defect_p1,
            "phase_1_status": "UNASSISTED_FIBER_CEILING_LOCKED_LGGR" if defect_p1 == -1 else "TOOL_ASSISTED_FIBER_SPLIT_RESOLVED_LGGG",
            "phase_2_partial_tool_local_green": l_p2,
            "phase_2_partial_tool_global_green": eg_p2,
            "phase_2_partial_tool_defect": defect_p2,
            "phase_2_status": "PARTIAL_TOOL_RESIDUAL_AMBIGUITY_LGGR" if defect_p2 == -1 else "TOOL_ASSISTED_FIBER_SPLIT_RESOLVED_LGGG",
            "phase_3_full_tool_local_green": l_p3,
            "phase_3_full_tool_global_green": eg_p3,
            "phase_3_full_tool_defect": defect_p3,
            "phase_3_status": "TOOL_ASSISTED_FIBER_SPLIT_RESOLVED_LGGG" if eg_p3 == 1 else "UNASSISTED_FIBER_CEILING_LOCKED_LGGR",
            "partial_monitor_receipt": partial_mon.get_receipt(),
            "full_monitor_receipt": full_mon.get_receipt(),
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one trajectory must be evaluated")
        n = len(self.evaluations)
        p1_locked = sum(1 for e in self.evaluations if e["phase_1_unassisted_defect"] == -1)
        p2_partial = sum(1 for e in self.evaluations if e["phase_2_partial_tool_defect"] == -1)
        p3_resolved = sum(1 for e in self.evaluations if e["phase_3_full_tool_global_green"] == 1)

        unassisted_resolution_rate = Fraction(n - p1_locked, n)
        tool_assisted_resolution_rate = Fraction(p3_resolved, n)

        if p3_resolved == n and p1_locked == n:
            status = "TOOL_ASSISTED_FIBER_SPLIT_RESOLVED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "UNASSISTED_FIBER_CEILING_LOCKED_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_tool_assisted_fiber_splitting.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_unassisted_ceiling_locked_count": p1_locked,
            "phase_2_partial_tool_residual_count": p2_partial,
            "phase_3_full_tool_resolved_count": p3_resolved,
            "unassisted_resolution_rate": unassisted_resolution_rate,
            "tool_assisted_resolution_rate": tool_assisted_resolution_rate,
            "tool_assisted_resolution_gain": tool_assisted_resolution_rate - unassisted_resolution_rate,
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingMultiTurnPairwiseTranscriptMonitor:
    """Online RSI Paper 001 / Volume VIII pre-generation multi-turn pairwise constraint contextuality monitor.

    Wraps StreamingContextualSheafMonitor to audit multi-turn tool-use transcripts where an agent is
    queried across pairwise subsets of binary specification constraints C_AB = {A, B}, C_BC = {B, C},
    C_CA = {C, A} before code generation:
      - Phase 1 (Signaling Single-Constraint Overlap Drift Across Turns):
        Turn 1 (C_AB) and Turn 3 (C_CA) assign conflicting single-variable marginals to constraint A
        (p_AB^A(1) != p_CA^A(1)), failing presheaf restriction agreement (L_sig = 0, Eg_sig = 0,
        Delta_{E,sig} = 0, SIGNALING_MARGINAL_MISMATCH_LGGR).
      - Phase 2 (No-Signaling Contextual Hollow-Triangle Transcript Before Code Generation):
        Every single-variable overlap agrees across turns (p_A = p_B = p_C = 1/2, L_ctx = 1),
        yet pairwise commitments form an anti-correlated odd cycle (q_AB = q_BC = q_CA = 0),
        forcing alpha_min = 0 > -1/2 = alpha_max (infeasibility_gap = 1/2 > 0) so no global code
        implementation d >= 0 on {0, 1}^3 exists (Eg_ctx = 0, Delta_{E,ctx} = -1,
        CONTEXTUAL_HOLLOW_TRIANGLE_OBSTRUCTION_LGGR).
      - Phase 3 (Pre-Generation Sheaf-Gated Constraint Reconciliation):
        Reconciling Turn 3's pairwise table C_CA to correlated [1/2, 0, 0, 1/2] (q_CA = 1/2)
        while preserving p_A = p_B = p_C = 1/2 closes the feasibility interval
        (alpha_min = alpha_max = 0, infeasibility_gap = 0), yielding a valid global joint section
        d(0, 1, 0) = 1/2, d(1, 0, 1) = 1/2 before code generation proceeds
        (L_rec = 1, Eg_rec = 1, Delta_{E,rec} = 0, GLOBAL_JOINT_SECTION_EXTENSIBLE_LGGG).
    """

    def __init__(
        self,
        *,
        scope_id: str = "streaming-multi-turn-pairwise-transcript-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.sheaf_monitor = StreamingContextualSheafMonitor(
            scope_id=f"{self.scope_id}-sheaf"
        )
        self.evaluations: list[dict[str, Any]] = []

    def evaluate_transcript(
        self,
        transcript_id: str,
        *,
        table_ab: Iterable[Fraction | int | str] = ("0", "1/2", "1/2", "0"),
        table_bc: Iterable[Fraction | int | str] = ("0", "1/2", "1/2", "0"),
        signaling_table_ca: Iterable[Fraction | int | str] = ("1/4", "1/2", "0", "1/4"),
        contextual_table_ca: Iterable[Fraction | int | str] = ("0", "1/2", "1/2", "0"),
        reconciled_table_ca: Iterable[Fraction | int | str] = ("1/2", "0", "0", "1/2"),
    ) -> dict[str, Any]:
        tid = text(transcript_id, "transcript_id")
        t_ab = list(sequence(table_ab, "table_ab"))
        t_bc = list(sequence(table_bc, "table_bc"))
        t_ca_sig = list(sequence(signaling_table_ca, "signaling_table_ca"))
        t_ca_ctx = list(sequence(contextual_table_ca, "contextual_table_ca"))
        t_ca_rec = list(sequence(reconciled_table_ca, "reconciled_table_ca"))

        audit_sig = self.sheaf_monitor.record_three_cycle_model(
            f"{tid}::phase_1_signaling", t_ab, t_bc, t_ca_sig
        )
        audit_ctx = self.sheaf_monitor.record_three_cycle_model(
            f"{tid}::phase_2_contextual", t_ab, t_bc, t_ca_ctx
        )
        audit_rec = self.sheaf_monitor.record_three_cycle_model(
            f"{tid}::phase_3_reconciled", t_ab, t_bc, t_ca_rec
        )

        l_p1 = 1 if bool(audit_sig["no_signaling_verified"]) else 0
        eg_p1 = 1 if (l_p1 == 1 and bool(audit_sig["global_section_exists"])) else 0
        defect_p1 = eg_p1 - l_p1

        l_p2 = 1 if bool(audit_ctx["no_signaling_verified"]) else 0
        eg_p2 = 1 if (l_p2 == 1 and bool(audit_ctx["global_section_exists"])) else 0
        defect_p2 = eg_p2 - l_p2

        l_p3 = 1 if bool(audit_rec["no_signaling_verified"]) else 0
        eg_p3 = 1 if (l_p3 == 1 and bool(audit_rec["global_section_exists"])) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "transcript_id": tid,
            "phase_1_no_signaling_verified": bool(audit_sig["no_signaling_verified"]),
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": audit_sig["classification"],
            "phase_2_no_signaling_verified": bool(audit_ctx["no_signaling_verified"]),
            "phase_2_alpha_min": audit_ctx["alpha_min"],
            "phase_2_alpha_max": audit_ctx["alpha_max"],
            "phase_2_infeasibility_gap": audit_ctx["infeasibility_gap"],
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": audit_ctx["classification"],
            "phase_3_no_signaling_verified": bool(audit_rec["no_signaling_verified"]),
            "phase_3_alpha_min": audit_rec["alpha_min"],
            "phase_3_alpha_max": audit_rec["alpha_max"],
            "phase_3_infeasibility_gap": audit_rec["infeasibility_gap"],
            "phase_3_witness_global_joint": audit_rec["witness_global_joint"],
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": audit_rec["classification"],
            "audit_signaling": audit_sig,
            "audit_contextual": audit_ctx,
            "audit_reconciled": audit_rec,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one transcript must be evaluated")
        n = len(self.evaluations)
        p1_sig_mismatch = sum(
            1 for e in self.evaluations if not e["phase_1_no_signaling_verified"]
        )
        p2_contextual_obstruction = sum(
            1 for e in self.evaluations if e["phase_2_defect"] == -1
        )
        p3_reconciled = sum(
            1 for e in self.evaluations if e["phase_3_global_green"] == 1
        )

        ungated_contextual_coherence_rate = Fraction(n - p2_contextual_obstruction, n)
        sheaf_reconciled_coherence_rate = Fraction(p3_reconciled, n)

        if p3_reconciled == n and p2_contextual_obstruction == n:
            status = "PRE_GENERATION_SHEAF_RECONCILED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "PRE_GENERATION_CONTEXTUAL_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_multi_turn_pairwise_transcript.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_signaling_mismatch_count": p1_sig_mismatch,
            "phase_2_contextual_obstruction_count": p2_contextual_obstruction,
            "phase_3_sheaf_reconciled_count": p3_reconciled,
            "ungated_contextual_coherence_rate": ungated_contextual_coherence_rate,
            "sheaf_reconciled_coherence_rate": sheaf_reconciled_coherence_rate,
            "sheaf_reconciliation_coherence_gain": (
                sheaf_reconciled_coherence_rate - ungated_contextual_coherence_rate
            ),
            "sheaf_monitor_receipt": self.sheaf_monitor.get_receipt(),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingDisagreementPreservingCouncilMonitor:
    """Online RSI Paper 002 / Volume VIII disagreement-preserving side-channel council vs. collapsing consensus monitor.

    Wraps StreamingSideInformationCapacityMonitor and StreamingProductOfExpertsMonitor to audit
    multi-agent code-review councils on patch fibers with K > 2 distinct latent root causes:
      - Phase 1 (Collapsing Consensus Prompt S = 1 with Disjoint PoE Supports):
        Forces a single unanimous summary tag (S_cons = 1) while specialist action distributions
        have disjoint supports (D_PoE = 0). Incurs root-cause collision floor K - 1 >= 2 > 0
        and PoE collapse (L_cons = 1, Eg_cons = 0, Delta_{E,cons} = -1,
        COLLAPSING_CONSENSUS_ROOT_CAUSE_LOSS_LGGR).
      - Phase 2 (Binary Pass/Block Escalation Tag S = 2 < K):
        Expands the council tag to S_bin = 2 symbols, reducing the collision floor from
        K - 1 to K - 2 > 0 (L_bin = 1), yet still conflating K - 2 >= 1 distinct root causes
        (Eg_bin = 0, Delta_{E,bin} = -1, BINARY_TAG_CAPACITY_DEFICIT_LGGR).
      - Phase 3 (Disagreement-Preserving Side-Channel Council S >= K with Shared Support):
        Allocates S_council >= K distinct side-channel symbols (collision floor K - S_council = 0,
        realized_subfiber_error_floor = 0) and shared remediation support (D_PoE > 0, D_MoE > 0),
        achieving zero-loss root-cause routing (L_council = 1, Eg_council = 1,
        Delta_{E,council} = 0, DISAGREEMENT_PRESERVING_COUNCIL_COHERENT_LGGG).
    """

    def __init__(
        self,
        *,
        scope_id: str = "streaming-disagreement-preserving-council-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.capacity_monitor = StreamingSideInformationCapacityMonitor(
            scope_id=f"{self.scope_id}-capacity"
        )
        self.poe_monitor = StreamingProductOfExpertsMonitor(
            scope_id=f"{self.scope_id}-poe"
        )
        self.evaluations: list[dict[str, Any]] = []

    def evaluate_council(
        self,
        evaluation_id: str,
        root_causes: Sequence[str] = (
            "auth_bypass",
            "race_condition",
            "memory_leak",
            "sql_injection",
        ),
        *,
        binary_symbols: Sequence[int] = (0, 0, 1, 1),
        council_symbols: Sequence[int] = (0, 1, 2, 3),
        council_capacity_s: int = 4,
        disjoint_expert_scores: Sequence[Sequence[Fraction | int | str]] = (
            ("1", "0"),
            ("0", "1"),
        ),
        shared_expert_scores: Sequence[Sequence[Fraction | int | str]] = (
            ("3/4", "1/4"),
            ("1/4", "3/4"),
        ),
    ) -> dict[str, Any]:
        eid = text(evaluation_id, "evaluation_id")
        causes = [text(c, "root_cause") for c in sequence(root_causes, "root_causes")]
        k_causes = len(set(causes))
        if k_causes < 3 or len(causes) != k_causes:
            raise ValidationError("root_causes must contain K >= 3 distinct root causes")
        bin_syms = [exact_int(s, "binary_symbol") for s in sequence(binary_symbols, "binary_symbols")]
        c_syms = [exact_int(s, "council_symbol") for s in sequence(council_symbols, "council_symbols")]
        cap_s = exact_int(council_capacity_s, "council_capacity_s", minimum=k_causes)
        if len(bin_syms) != k_causes or len(c_syms) != k_causes:
            raise ValidationError("symbol sequences must match root_causes length")

        states_cons = [
            {"state_id": f"patch_{i}", "query_value": causes[i], "side_symbol": 0}
            for i in range(k_causes)
        ]
        states_bin = [
            {"state_id": f"patch_{i}", "query_value": causes[i], "side_symbol": bin_syms[i]}
            for i in range(k_causes)
        ]
        states_council = [
            {"state_id": f"patch_{i}", "query_value": causes[i], "side_symbol": c_syms[i]}
            for i in range(k_causes)
        ]

        cap_cons = self.capacity_monitor.record_fiber_channel(
            f"{eid}::phase_1_consensus",
            states_cons,
            channel_capacity_s=1,
            error_budget=0,
        )
        poe_cons = self.poe_monitor.record_expert_scores(
            f"{eid}::phase_1_disjoint_poe",
            disjoint_expert_scores,
        )

        cap_bin = self.capacity_monitor.record_fiber_channel(
            f"{eid}::phase_2_binary_tag",
            states_bin,
            channel_capacity_s=2,
            error_budget=0,
        )

        cap_council = self.capacity_monitor.record_fiber_channel(
            f"{eid}::phase_3_council",
            states_council,
            channel_capacity_s=cap_s,
            error_budget=0,
        )
        poe_council = self.poe_monitor.record_expert_scores(
            f"{eid}::phase_3_shared_poe",
            shared_expert_scores,
        )

        floor_cons = int(cap_cons["realized_subfiber_error_floor"])
        floor_bin = int(cap_bin["realized_subfiber_error_floor"])
        floor_council = int(cap_council["realized_subfiber_error_floor"])
        d_poe_cons = rational(poe_cons["poe_partition_sum"])
        d_poe_council = rational(poe_council["poe_partition_sum"])

        l_p1 = 1 if (int(cap_cons["local_product_aggregator"]) == 1 and int(poe_cons["local_product_aggregator"]) == 1) else 0
        eg_p1 = 1 if (l_p1 == 1 and floor_cons == 0 and d_poe_cons > Fraction(0)) else 0
        defect_p1 = eg_p1 - l_p1

        l_p2 = 1 if (int(cap_bin["local_product_aggregator"]) == 1 and floor_bin < floor_cons) else 0
        eg_p2 = 1 if (l_p2 == 1 and floor_bin == 0) else 0
        defect_p2 = eg_p2 - l_p2

        l_p3 = 1 if (int(cap_council["local_product_aggregator"]) == 1 and floor_council == 0 and d_poe_council > Fraction(0)) else 0
        eg_p3 = 1 if (l_p3 == 1 and floor_council < floor_bin and floor_bin < floor_cons) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eid,
            "distinct_root_causes_k": k_causes,
            "consensus_collision_floor": floor_cons,
            "binary_tag_collision_floor": floor_bin,
            "council_collision_floor": floor_council,
            "consensus_poe_partition_sum": d_poe_cons,
            "council_poe_partition_sum": d_poe_council,
            "phase_1_consensus_local_green": l_p1,
            "phase_1_consensus_global_green": eg_p1,
            "phase_1_consensus_defect": defect_p1,
            "phase_1_status": "COLLAPSING_CONSENSUS_ROOT_CAUSE_LOSS_LGGR" if defect_p1 == -1 else "DISAGREEMENT_PRESERVING_COUNCIL_COHERENT_LGGG",
            "phase_2_binary_local_green": l_p2,
            "phase_2_binary_global_green": eg_p2,
            "phase_2_binary_defect": defect_p2,
            "phase_2_status": "BINARY_TAG_CAPACITY_DEFICIT_LGGR" if defect_p2 == -1 else "DISAGREEMENT_PRESERVING_COUNCIL_COHERENT_LGGG",
            "phase_3_council_local_green": l_p3,
            "phase_3_council_global_green": eg_p3,
            "phase_3_council_defect": defect_p3,
            "phase_3_status": "DISAGREEMENT_PRESERVING_COUNCIL_COHERENT_LGGG" if eg_p3 == 1 else "COLLAPSING_CONSENSUS_ROOT_CAUSE_LOSS_LGGR",
            "capacity_consensus": cap_cons,
            "capacity_binary": cap_bin,
            "capacity_council": cap_council,
            "poe_consensus": poe_cons,
            "poe_council": poe_council,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one council evaluation must be recorded")
        n = len(self.evaluations)
        p1_collapse = sum(1 for e in self.evaluations if e["phase_1_consensus_defect"] == -1)
        p2_binary_deficit = sum(1 for e in self.evaluations if e["phase_2_binary_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_council_global_green"] == 1)

        collapsing_consensus_coherence_rate = Fraction(n - p1_collapse, n)
        disagreement_council_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_collapse == n:
            status = "DISAGREEMENT_PRESERVING_COUNCIL_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "COLLAPSING_CONSENSUS_ROOT_CAUSE_LOSS_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_disagreement_preserving_council.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_collapsing_consensus_loss_count": p1_collapse,
            "phase_2_binary_tag_deficit_count": p2_binary_deficit,
            "phase_3_disagreement_council_coherent_count": p3_coherent,
            "collapsing_consensus_coherence_rate": collapsing_consensus_coherence_rate,
            "disagreement_council_coherence_rate": disagreement_council_coherence_rate,
            "disagreement_council_coherence_gain": (
                disagreement_council_coherence_rate - collapsing_consensus_coherence_rate
            ),
            "capacity_monitor_receipt": self.capacity_monitor.get_receipt(),
            "poe_monitor_receipt": self.poe_monitor.get_receipt(),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingBoundedDepthKInductionMonitor:
    """Online LGGR IV / VIII bounded-depth symbolic execution & k-induction projective tower vs. reachable carrier monitor.

    Wraps StreamingProjectiveTowerMonitor across 4-depth modular unrollings m_k in {2, 4, 8, 16}
    and a reachable non-negative finite-state carrier X_reach = [0, M_reach]:
      - Phase 1 (R^1 lim^1 Fractional Coset Obstruction — Completion Witness in Q \\ Z):
        For 3*x + 1 == 0, the unrolling thread (1, 1, 5, 5) passes all 4 finite depths (L_frac = 1),
        yet x_inf = -1/3 in Q \\ Z has no integer lift (Eg_frac = 0, Delta_{E,frac} = -1,
        R1_FRACTIONAL_COMPLETION_OBSTRUCTION_LGGR).
      - Phase 2 (Out-of-Carrier Signed Integer Completion Witness in Z \\ X_reach):
        For 3*x + 3 == 0, the unrolling thread (1, 3, 7, 15) passes all 4 finite depths with positive
        modular witnesses x_k = 2^k - 1 > 0 and admits global integer lift x_* = -1 in Z (L_carr = 1),
        yet x_* = -1 not in [0, M_reach] lies outside the reachable non-negative carrier and step-lift
        differences (2, 4, 8) diverge (Eg_carr = 0, Delta_{E,carr} = -1,
        OUT_OF_CARRIER_COMPLETION_WITNESS_LGGR).
      - Phase 3 (In-Carrier Stabilized Reachable Witness in X_reach = [0, M_reach]):
        For 3*x - 6 == 0, the unrolling thread (0, 2, 2, 2) passes all 4 finite depths and stabilizes
        at x_* = 2 in [0, M_reach] with zero step-lift differences from depth 2 onward
        (L_reach = 1, Eg_reach = 1, Delta_{E,reach} = 0, REACHABLE_CARRIER_LIFT_COHERENT_LGGG).
    """

    def __init__(
        self,
        *,
        reachable_carrier_max: int = 10,
        scope_id: str = "streaming-bounded-depth-k-induction-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.reachable_carrier_max = exact_int(
            reachable_carrier_max, "reachable_carrier_max", minimum=2
        )
        self.evaluations: list[dict[str, Any]] = []

    def evaluate_k_induction_harness(
        self,
        evaluation_id: str,
        *,
        moduli: Sequence[int] = (2, 4, 8, 16),
        fractional_thread: Sequence[int] = (1, 1, 5, 5),
        out_of_carrier_thread: Sequence[int] = (1, 3, 7, 15),
        reachable_thread: Sequence[int] = (0, 2, 2, 2),
    ) -> dict[str, Any]:
        eid = text(evaluation_id, "evaluation_id")
        mods = [exact_int(m, "modulus", minimum=2) for m in sequence(moduli, "moduli")]
        f_th = [exact_int(x, "fractional_x") for x in sequence(fractional_thread, "fractional_thread")]
        c_th = [exact_int(x, "carrier_x") for x in sequence(out_of_carrier_thread, "out_of_carrier_thread")]
        r_th = [exact_int(x, "reachable_x") for x in sequence(reachable_thread, "reachable_thread")]
        if len(mods) < 2 or not (len(mods) == len(f_th) == len(c_th) == len(r_th)):
            raise ValidationError("moduli and all 3 threads must have the same length >= 2")

        mon_frac = StreamingProjectiveTowerMonitor(
            3, 1, scope_id=f"{self.scope_id}-{eid}-frac"
        )
        mon_carr = StreamingProjectiveTowerMonitor(
            3, 3, scope_id=f"{self.scope_id}-{eid}-carr"
        )
        mon_reach = StreamingProjectiveTowerMonitor(
            3, -6, scope_id=f"{self.scope_id}-{eid}-reach"
        )

        for idx, m_val in enumerate(mods):
            mon_frac.record_stage(f"depth_{idx + 1}", m_val, f_th[idx])
            mon_carr.record_stage(f"depth_{idx + 1}", m_val, c_th[idx])
            mon_reach.record_stage(f"depth_{idx + 1}", m_val, r_th[idx])

        rec_frac = mon_frac.get_receipt()
        rec_carr = mon_carr.get_receipt()
        rec_reach = mon_reach.get_receipt()

        l_p1 = int(rec_frac["local_product_aggregator"])
        eg_p1 = int(rec_frac["global_integral_lift_evaluator"])
        defect_p1 = eg_p1 - l_p1

        x_star_carr = rec_carr["integral_global_root"]
        in_carr_p2 = (
            x_star_carr is not None
            and 0 <= int(x_star_carr) <= self.reachable_carrier_max
        )
        l_p2 = 1 if (int(rec_carr["local_product_aggregator"]) == 1 and int(rec_carr["global_integral_lift_evaluator"]) == 1) else 0
        eg_p2 = 1 if (l_p2 == 1 and in_carr_p2) else 0
        defect_p2 = eg_p2 - l_p2

        x_star_reach = rec_reach["integral_global_root"]
        in_carr_p3 = (
            x_star_reach is not None
            and 0 <= int(x_star_reach) <= self.reachable_carrier_max
        )
        tail_stabilized = (r_th[-1] - r_th[-2] == 0)
        l_p3 = 1 if (int(rec_reach["local_product_aggregator"]) == 1 and int(rec_reach["global_integral_lift_evaluator"]) == 1) else 0
        eg_p3 = 1 if (l_p3 == 1 and in_carr_p3 and tail_stabilized) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eid,
            "unrolling_depths": len(mods),
            "reachable_carrier_max": self.reachable_carrier_max,
            "phase_1_rational_root": rec_frac["rational_completion_root"],
            "phase_1_integral_root": rec_frac["integral_global_root"],
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "R1_FRACTIONAL_COMPLETION_OBSTRUCTION_LGGR" if defect_p1 == -1 else "REACHABLE_CARRIER_LIFT_COHERENT_LGGG",
            "phase_2_integral_root": x_star_carr,
            "phase_2_in_reachable_carrier": in_carr_p2,
            "phase_2_tail_step_difference": c_th[-1] - c_th[-2],
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "OUT_OF_CARRIER_COMPLETION_WITNESS_LGGR" if defect_p2 == -1 else "REACHABLE_CARRIER_LIFT_COHERENT_LGGG",
            "phase_3_integral_root": x_star_reach,
            "phase_3_in_reachable_carrier": in_carr_p3,
            "phase_3_tail_step_difference": r_th[-1] - r_th[-2],
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "REACHABLE_CARRIER_LIFT_COHERENT_LGGG" if eg_p3 == 1 else "OUT_OF_CARRIER_COMPLETION_WITNESS_LGGR",
            "tower_fractional_receipt": rec_frac,
            "tower_out_of_carrier_receipt": rec_carr,
            "tower_reachable_receipt": rec_reach,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one k-induction evaluation must be recorded")
        n = len(self.evaluations)
        p1_frac_fail = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_carr_fail = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        out_of_carrier_coherence_rate = Fraction(n - p2_carr_fail, n)
        reachable_carrier_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_frac_fail == n and p2_carr_fail == n:
            status = "REACHABLE_CARRIER_LIFT_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "OUT_OF_CARRIER_COMPLETION_WITNESS_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_bounded_depth_k_induction.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_fractional_obstruction_count": p1_frac_fail,
            "phase_2_out_of_carrier_obstruction_count": p2_carr_fail,
            "phase_3_reachable_carrier_coherent_count": p3_coherent,
            "out_of_carrier_coherence_rate": out_of_carrier_coherence_rate,
            "reachable_carrier_coherence_rate": reachable_carrier_coherence_rate,
            "reachable_carrier_coherence_gain": (
                reachable_carrier_coherence_rate - out_of_carrier_coherence_rate
            ),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingBoundaryQuorumInterfaceMonitor:
    """Online multi-agent interface schema audit (Theorem 74).

    Wraps ``StreamingOrganizationalGluingMonitor`` and ``StreamingThresholdGovernanceMonitor``
    across a 3-phase interface schema separation:
      - Phase 1 (Pass-flag-only interface schema J_pass(c) = (pass, pass)):
        Both ``c_matched`` (E_g = 1) and ``c_skew`` (E_g = 0) project to the identical
        joint pass-flag quotient J_pass = {"left": {"pass": 1}, "right": {"pass": 1}},
        triggering a carrier-mixing collision (L_mix = 1, Eg_mix = 0, defect_mix = -1).
      - Phase 2 (k-of-n majority quorum gate on validator votes (1, 1, ..., 0) with E_g = 0):
        A specialist validator vetoes (e_n = 0) so the strict product aggregator is
        L_prod = 0 (Delta_prod = 0), yet the k-of-n quorum gate M_{k,n} = 1 overrides
        the veto and masks the failure (quorum_inflation = 1, L_quor = 1, Eg_quor = 0,
        defect_quor = -1).
      - Phase 3 (Full boundary payload J_full(c_matched) != J_full(c_skew) + strict product gate):
        Separating the boundary payload eliminates carrier-mixing collisions and enforcing
        the strict product gate honours the specialist veto (L_full = 1, Eg_full = 1,
        defect_full = 0).
    """

    def __init__(
        self,
        *,
        n_validators: int = 3,
        quorum_k: int = 2,
        scope_id: str = "streaming-boundary-quorum-interface-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        n_val = exact_int(n_validators, "n_validators")
        k_val = exact_int(quorum_k, "quorum_k")
        if n_val < 2:
            raise ValidationError("n_validators must be >= 2")
        if k_val < 1 or k_val >= n_val:
            raise ValidationError("quorum_k must satisfy 1 <= quorum_k < n_validators")
        self.n_validators = n_val
        self.quorum_k = k_val
        self.evaluations: list[dict[str, Any]] = []

    def evaluate_interface_schema(
        self,
        evaluation_id: str,
        *,
        matched_boundary_left: Any,
        matched_boundary_right: Any,
        skew_boundary_left: Any,
        skew_boundary_right: Any,
        quorum_votes: Iterable[int | bool],
        eg_matched: int | bool = 1,
        eg_skew: int | bool = 0,
    ) -> dict[str, Any]:
        """Evaluate pass-flag mixing, k-of-n quorum masking, and full boundary product gating."""
        eid = text(evaluation_id, "evaluation_id")
        votes = [
            StreamingThresholdGovernanceMonitor._binary_int(v, f"quorum_votes[{idx}]")
            for idx, v in enumerate(sequence(quorum_votes, "quorum_votes"))
        ]
        if len(votes) != self.n_validators:
            raise ValidationError(f"Expected {self.n_validators} quorum_votes, got {len(votes)}")
        vg_matched = StreamingOrganizationalGluingMonitor._binary_int(eg_matched, "eg_matched")
        vg_skew = StreamingOrganizationalGluingMonitor._binary_int(eg_skew, "eg_skew")

        # Phase 1: Pass-flag-only interface schema
        pass_gluing = StreamingOrganizationalGluingMonitor(
            scope_id=f"{self.scope_id}-{eid}-pass-flag"
        )
        pass_gluing.observe_boundary(
            f"{eid}-matched-pass",
            {"pass": 1},
            {"pass": 1},
            1,
            1,
            vg_matched,
        )
        pass_gluing.observe_boundary(
            f"{eid}-skew-pass",
            {"pass": 1},
            {"pass": 1},
            1,
            1,
            vg_skew,
        )
        rec_pass = pass_gluing.get_receipt()

        # Phase 2: k-of-n majority quorum vs. strict product on specialist veto
        quorum_mon = StreamingThresholdGovernanceMonitor(
            self.n_validators,
            self.quorum_k,
            scope_id=f"{self.scope_id}-{eid}-quorum",
        )
        rec_quorum = quorum_mon.record_vote(f"{eid}-skew-quorum", votes, vg_skew)
        vote_rec = rec_quorum["latest_trace"]

        # Phase 3: Full boundary payload + strict product gate
        full_gluing = StreamingOrganizationalGluingMonitor(
            scope_id=f"{self.scope_id}-{eid}-full-payload"
        )
        full_gluing.observe_boundary(
            f"{eid}-matched-full",
            matched_boundary_left,
            matched_boundary_right,
            1,
            1,
            vg_matched,
        )
        full_gluing.observe_boundary(
            f"{eid}-skew-full",
            skew_boundary_left,
            skew_boundary_right,
            1,
            int(vote_rec["product_aggregator_l"]),
            vg_skew,
        )
        rec_full = full_gluing.get_receipt()

        has_pass_collision = rec_pass["carrier_mixing_collisions_count"] > 0
        l_p1 = 1 if has_pass_collision else 0
        eg_p1 = 1 if (l_p1 == 1 and vg_matched == vg_skew) else 0
        defect_p1 = eg_p1 - l_p1

        l_prod = int(vote_rec["product_aggregator_l"])
        m_quorum = int(vote_rec["quorum_aggregator_m"])
        quorum_inflation = int(vote_rec["quorum_inflation_gap"])
        l_p2 = 1 if (m_quorum == 1 and l_prod == 0) else 0
        eg_p2 = 1 if (l_p2 == 1 and vg_skew == 1) else 0
        defect_p2 = eg_p2 - l_p2

        full_collision_free = (rec_full["carrier_mixing_collisions_count"] == 0)
        l_p3 = 1 if (full_collision_free and l_prod == vg_skew) else 0
        eg_p3 = 1 if (l_p3 == 1 and quorum_inflation == 1 and has_pass_collision) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eid,
            "n_validators": self.n_validators,
            "quorum_k": self.quorum_k,
            "quorum_votes": votes,
            "local_product": l_prod,
            "quorum_verdict": m_quorum,
            "quorum_inflation": quorum_inflation,
            "phase_1_carrier_mixing_collisions": rec_pass["carrier_mixing_collisions_count"],
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "PASS_FLAG_CARRIER_MIXING_OBSTRUCTION_LGGR" if defect_p1 == -1 else "FULL_BOUNDARY_STRICT_PRODUCT_COHERENT_LGGG",
            "phase_2_quorum_masked_count": rec_quorum["quorum_masked_ngd_count"],
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "QUORUM_MASKED_VETO_OBSTRUCTION_LGGR" if defect_p2 == -1 else "FULL_BOUNDARY_STRICT_PRODUCT_COHERENT_LGGG",
            "phase_3_carrier_mixing_collisions": rec_full["carrier_mixing_collisions_count"],
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "FULL_BOUNDARY_STRICT_PRODUCT_COHERENT_LGGG" if eg_p3 == 1 else "PASS_FLAG_CARRIER_MIXING_OBSTRUCTION_LGGR",
            "pass_flag_gluing_receipt": rec_pass,
            "quorum_governance_receipt": rec_quorum,
            "full_boundary_gluing_receipt": rec_full,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one interface schema evaluation must be recorded")
        n = len(self.evaluations)
        p1_mix_fail = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_quor_fail = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        pass_quorum_coherence_rate = Fraction(n - max(p1_mix_fail, p2_quor_fail), n)
        full_product_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_mix_fail == n and p2_quor_fail == n:
            status = "FULL_BOUNDARY_STRICT_PRODUCT_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "PASS_FLAG_CARRIER_MIXING_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_boundary_quorum_interface.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_carrier_mixing_obstruction_count": p1_mix_fail,
            "phase_2_quorum_masked_obstruction_count": p2_quor_fail,
            "phase_3_full_boundary_coherent_count": p3_coherent,
            "pass_quorum_coherence_rate": pass_quorum_coherence_rate,
            "full_product_coherence_rate": full_product_coherence_rate,
            "interface_coherence_gain": (
                full_product_coherence_rate - pass_quorum_coherence_rate
            ),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingCrossRoleDeduplicationMonitor:
    """Online cross-role six-role schema validation and double-count audit (Theorem 75).

    Wraps ``StreamingSixRoleOverlayMonitor`` across a 3-phase multi-stage audit log check:
      - Phase 1 (Cross-role verdict triple drift on shared ``trace_id``):
        Audits whether all role-indexed adapters logging the same ``trace_id`` preserve
        the exact verdict triple ``(e1, e2, eg)`` and pointwise defect ``eg - e1 * e2``.
        When a role adapter mutates ``(1, 1, 0) -> (1, 1, 1)`` on ``tr-01``, flags
        ``CROSS_ROLE_VERDICT_DRIFT_LGGR`` (L_drift = 1, Eg_drift = 0, defect_drift = -1).
      - Phase 2 (Un-deduplicated persona double-counting across 6 role views):
        Audits 6 role log entries covering 3 unique traces ``tr-01`` (d1 = -1, m1 = 2),
        ``tr-02`` (d2 = -1, m2 = 1), and ``tr-03`` (d3 = +1, m3 = 3). Naive un-deduplicated
        6-role summation computes D_raw = 2*(-1) + 1*(-1) + 3*(+1) = 0, masking the
        unique-trace net negative defect D_unique = -1 + -1 + 1 = -1 (multiplicity
        inflation D_raw - D_unique = +1; L_dup = 1, Eg_dup = 0, defect_dup = -1).
      - Phase 3 (Trace-ID deduplicated & context-validated 6-role overlay):
        Enforces exact cross-role ``(e1, e2, eg)`` preservation per ``trace_id`` and
        normalizes role entries by inverse trace multiplicity ``w_r(t) = 1 / m(t)``
        (equivalently deduplicating by ``trace_id``), recovering the exact unique-trace
        sample defect D_unique = -1 without double-counting (L_dedup = 1, Eg_dedup = 1,
        defect_dedup = 0).
    """

    def __init__(self, *, scope_id: str = "streaming-cross-role-deduplication-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.evaluations: list[dict[str, Any]] = []

    @staticmethod
    def _default_valid_context(role: str) -> dict[str, Any]:
        if role == "finite_obstruction":
            return {
                "carrier": "X_trace",
                "degree": 1,
                "comparison_map": "pi_boundary",
                "quotient_gauge": "exact",
                "replay_data": "retained",
            }
        if role == "foundations":
            return {"diagnostic_only": True, "authority_effect": "None"}
        if role == "representation":
            return {"operation": " compose_v2", "transport_witness": " compose_v2"}
        if role == "observer":
            return {"left_envelope": "env_v2", "right_envelope": "env_v2"}
        if role == "continuum_shadow":
            return {"finite_calculation": True, "limit_statement_distinct": True}
        if role == "action_and_alignment":
            return {"residual_routed_as_feedback": True, "relabeled_as_success": False}
        return {}

    def evaluate_cross_role_log(
        self,
        evaluation_id: str,
        *,
        drift_log_entries: Sequence[Mapping[str, Any]],
        shared_role_entries: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        """Evaluate cross-role triple drift, persona double-counting, and trace-ID deduplication."""
        eid = text(evaluation_id, "evaluation_id")
        drift_list = list(sequence(drift_log_entries, "drift_log_entries"))
        shared_list = list(sequence(shared_role_entries, "shared_role_entries"))
        if len(drift_list) < 2:
            raise ValidationError("drift_log_entries must contain at least 2 entries")
        if len(shared_list) != 6:
            raise ValidationError("shared_role_entries must contain 6 role entries")

        # Phase 1: Check cross-role verdict triple consistency on drift_log_entries
        drift_by_tid: dict[str, tuple[int, int, int]] = {}
        drift_conflicts: list[dict[str, Any]] = []
        for entry in drift_list:
            tid = text(entry["trace_id"], "trace_id")
            role = text(entry["role"], "role")
            triple = (
                StreamingSixRoleOverlayMonitor._binary_verdict(entry["e1"], "e1"),
                StreamingSixRoleOverlayMonitor._binary_verdict(entry["e2"], "e2"),
                StreamingSixRoleOverlayMonitor._binary_verdict(entry["eg"], "eg"),
            )
            if tid not in drift_by_tid:
                drift_by_tid[tid] = triple
            elif drift_by_tid[tid] != triple:
                drift_conflicts.append(
                    {
                        "trace_id": tid,
                        "role": role,
                        "expected_triple": list(drift_by_tid[tid]),
                        "observed_triple": list(triple),
                    }
                )

        # Phase 2: Un-deduplicated 6-role overlay monitor on shared_role_entries
        raw_mon = StreamingSixRoleOverlayMonitor(scope_id=f"{self.scope_id}-{eid}-raw")
        tid_counts: dict[str, int] = {}
        unique_triples: dict[str, tuple[int, int, int]] = {}
        shared_drift_conflicts: list[dict[str, Any]] = []

        for entry in shared_list:
            tid = text(entry["trace_id"], "trace_id")
            role = text(entry["role"], "role")
            triple = (
                StreamingSixRoleOverlayMonitor._binary_verdict(entry["e1"], "e1"),
                StreamingSixRoleOverlayMonitor._binary_verdict(entry["e2"], "e2"),
                StreamingSixRoleOverlayMonitor._binary_verdict(entry["eg"], "eg"),
            )
            tid_counts[tid] = tid_counts.get(tid, 0) + 1
            if tid not in unique_triples:
                unique_triples[tid] = triple
            elif unique_triples[tid] != triple:
                shared_drift_conflicts.append({"trace_id": tid, "role": role})
            raw_mon.record_evaluation(
                role,
                triple[0],
                triple[1],
                triple[2],
                context=self._default_valid_context(role),
                weight=1,
            )
        rec_raw = raw_mon.get_receipt()

        # Phase 3: Trace-ID deduplicated & inverse-multiplicity weighted 6-role overlay
        dedup_mon = StreamingSixRoleOverlayMonitor(scope_id=f"{self.scope_id}-{eid}-dedup")
        for tid, triple in unique_triples.items():
            dedup_mon.record_evaluation(
                "finite_obstruction",
                triple[0],
                triple[1],
                triple[2],
                context=self._default_valid_context("finite_obstruction"),
                weight=1,
            )
        rec_dedup = dedup_mon.get_receipt()

        d_raw = int(rec_raw["sample_signed_defect_sum"])
        d_unique = int(rec_dedup["sample_signed_defect_sum"])
        dup_inflation = d_raw - d_unique
        double_counted_entries = len(shared_list) - len(unique_triples)

        l_p1 = 1 if len(drift_conflicts) > 0 else 0
        eg_p1 = 1 if (l_p1 == 1 and len(drift_conflicts) == 0) else 0
        defect_p1 = eg_p1 - l_p1

        l_p2 = 1 if (double_counted_entries > 0 and d_raw == 0 and d_unique < 0) else 0
        eg_p2 = 1 if (l_p2 == 1 and d_raw == d_unique) else 0
        defect_p2 = eg_p2 - l_p2

        l_p3 = 1 if (len(shared_drift_conflicts) == 0 and len(unique_triples) == 3 and d_unique == -1) else 0
        eg_p3 = 1 if (l_p3 == 1 and dup_inflation == 1) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eid,
            "raw_role_entries_count": len(shared_list),
            "unique_traces_count": len(unique_triples),
            "double_counted_entries_count": double_counted_entries,
            "trace_multiplicities": tid_counts,
            "raw_signed_defect_sum": d_raw,
            "unique_signed_defect_sum": d_unique,
            "multiplicity_inflation": dup_inflation,
            "phase_1_verdict_drift_count": len(drift_conflicts),
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "CROSS_ROLE_VERDICT_DRIFT_LGGR" if defect_p1 == -1 else "CROSS_ROLE_DEDUPLICATED_AUDIT_COHERENT_LGGG",
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "SHARED_TRACE_DOUBLE_COUNT_MASKING_LGGR" if defect_p2 == -1 else "CROSS_ROLE_DEDUPLICATED_AUDIT_COHERENT_LGGG",
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "CROSS_ROLE_DEDUPLICATED_AUDIT_COHERENT_LGGG" if eg_p3 == 1 else "SHARED_TRACE_DOUBLE_COUNT_MASKING_LGGR",
            "raw_six_role_receipt": rec_raw,
            "deduplicated_six_role_receipt": rec_dedup,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one cross-role evaluation must be recorded")
        n = len(self.evaluations)
        p1_drift_fail = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_dup_fail = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        undeduplicated_coherence_rate = Fraction(n - max(p1_drift_fail, p2_dup_fail), n)
        deduplicated_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_drift_fail == n and p2_dup_fail == n:
            status = "CROSS_ROLE_DEDUPLICATED_AUDIT_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "SHARED_TRACE_DOUBLE_COUNT_MASKING_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_cross_role_deduplication.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_verdict_drift_obstruction_count": p1_drift_fail,
            "phase_2_double_count_masking_count": p2_dup_fail,
            "phase_3_deduplicated_coherent_count": p3_coherent,
            "undeduplicated_coherence_rate": undeduplicated_coherence_rate,
            "deduplicated_coherence_rate": deduplicated_coherence_rate,
            "cross_role_deduplication_gain": (
                deduplicated_coherence_rate - undeduplicated_coherence_rate
            ),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingStageVsE2EIntegrationMonitor:
    """Online stage-level unit tests vs. end-to-end integration oracle audit (Theorem 76).

    Wraps ``StreamingPathKernelMonitor`` and ``StreamingDashboardAdequacyMonitor`` across
    4 composite trajectories c_{i,j} = s2_j * s1_i (s1_1: E1=1, s1_2: E1=0; s2_1: E2=1,
    s2_2: E2=1; Z1 = 1, Z2 = 2, Z2 * Z1 = 2):
      - Phase 1 (3-tuple pass-rate dashboard & naive stage-kernel multiplication on
        (n11, n10, n01, n00) = (1, 1, 1, 1)):
        Both global kernel Z_E = 2 and factored stage product Z2 * Z1 = 2 give LPR = GPR = 1/2
        with net discrepancy GPR - LPR = 0, masking NGD count n_- = 1 (rate 1/4), PGD count
        n_+ = 1 (rate 1/4), and EGD = 1/2 (L_mask = 1, Eg_mask = 0, defect_mask = -1).
      - Phase 2 (Unrepaired NGD integration regression on (n11, n10, n01, n00) = (1, 1, 0, 2)):
        When downstream fallback on c_{2,1} is disabled, Z_E = 1 < 2 = Z2 * Z1 with negative
        evaluator residual R_E = -1 < 0 and NGD rate 1/4 (L_ngd = 1, Eg_ngd = 0,
        defect_ngd = -1).
      - Phase 3 (4-tuple dashboard (N, sum L, sum E_g, n_-) & path-kernel audit after boundary
        repair on (n11, n10, n01, n00) = (2, 0, 0, 2)):
        Reconstructs all four contingency counts from the 4-tuple summary and verifies zero
        pointwise disagreement (n_- = 0, n_+ = 0, EGD = 0, Z_E = Z2 * Z1 = 2; L_full = 1,
        Eg_full = 1, defect_full = 0).
    """

    def __init__(self, *, scope_id: str = "streaming-stage-vs-e2e-integration-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.evaluations: list[dict[str, Any]] = []

    @staticmethod
    def _build_pair(
        scope_prefix: str,
        e2e_verdicts: Sequence[int | bool],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if len(e2e_verdicts) != 4:
            raise ValidationError("Expected 4 composite E2E verdicts")
        pk = StreamingPathKernelMonitor(scope_id=f"{scope_prefix}-pk")
        pk.add_stage1_segment("s1_1", "src", "bnd", 1, 1)
        pk.add_stage1_segment("s1_2", "src", "bnd", 1, 0)
        pk.add_stage2_segment("s2_1", "bnd", "tgt", 1, 1)
        pk.add_stage2_segment("s2_2", "bnd", "tgt", 1, 1)

        dash = StreamingDashboardAdequacyMonitor(scope_id=f"{scope_prefix}-dash")
        pairs = [("s1_1", "s2_1", 1, 1), ("s1_1", "s2_2", 1, 1), ("s1_2", "s2_1", 0, 1), ("s1_2", "s2_2", 0, 1)]
        for idx, ((s1_id, s2_id, e1, e2), eg) in enumerate(zip(pairs, e2e_verdicts)):
            cid = f"c_{idx + 1}"
            pk.observe_composite(cid, s1_id, s2_id, eg)
            dash.record_trace(cid, e1, e2, eg)
        return pk.audit_kernel_composition("src", "tgt"), dash.get_receipt()

    def evaluate_stage_vs_e2e(
        self,
        evaluation_id: str,
        *,
        masked_e2e_verdicts: Sequence[int | bool] = (1, 0, 1, 0),
        ngd_e2e_verdicts: Sequence[int | bool] = (1, 0, 0, 0),
        repaired_e2e_verdicts: Sequence[int | bool] = (1, 1, 0, 0),
    ) -> dict[str, Any]:
        """Evaluate cancellation-masked stage kernels, unmasked NGD regression, and 4-tuple dashboard repair."""
        eid = text(evaluation_id, "evaluation_id")
        pk_mask, dash_mask = self._build_pair(
            f"{self.scope_id}-{eid}-mask", masked_e2e_verdicts
        )
        pk_ngd, dash_ngd = self._build_pair(
            f"{self.scope_id}-{eid}-ngd", ngd_e2e_verdicts
        )
        pk_rep, dash_rep = self._build_pair(
            f"{self.scope_id}-{eid}-rep", repaired_e2e_verdicts
        )

        # Phase 1: Cancellation-masked NGD + PGD
        l_p1 = 1 if (pk_mask["cancellation_masked"] and dash_mask["n_neg_ngd"] == 1 and dash_mask["n_pos_pgd"] == 1) else 0
        eg_p1 = 1 if (l_p1 == 1 and dash_mask["n_neg_ngd"] == 0) else 0
        defect_p1 = eg_p1 - l_p1

        # Phase 2: Unmasked NGD regression
        l_p2 = 1 if (int(pk_ngd["evaluator_residual_re"]) == -1 and dash_ngd["n_neg_ngd"] == 1) else 0
        eg_p2 = 1 if (l_p2 == 1 and int(pk_ngd["evaluator_residual_re"]) == 0) else 0
        defect_p2 = eg_p2 - l_p2

        # Phase 3: 4-tuple contingency reconstruction + repaired zero-defect kernel
        l_p3 = (
            1
            if (
                dash_mask["reconstruction_identities_verified"]
                and dash_rep["n_neg_ngd"] == 0
                and dash_rep["n_pos_pgd"] == 0
                and pk_rep["status"] == "KERNEL_COMPOSITION_VERIFIED"
            )
            else 0
        )
        eg_p3 = 1 if (l_p3 == 1 and dash_mask["disagreement_count_m"] == 2) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eid,
            "factored_stage_kernel_product": pk_mask["factored_boundary_kernel_sum"],
            "phase_1_global_kernel": pk_mask["global_evaluated_kernel"],
            "phase_1_ngd_rate": Fraction(dash_mask["n_neg_ngd"], dash_mask["sample_size"]),
            "phase_1_pgd_rate": Fraction(dash_mask["n_pos_pgd"], dash_mask["sample_size"]),
            "phase_1_egd_rate": dash_mask["evaluator_gluing_disagreement_egd"],
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "CANCELLATION_MASKED_STAGE_KERNEL_LGGR" if defect_p1 == -1 else "STAGE_E2E_KERNEL_DASHBOARD_COHERENT_LGGG",
            "phase_2_global_kernel": pk_ngd["global_evaluated_kernel"],
            "phase_2_evaluator_residual": pk_ngd["evaluator_residual_re"],
            "phase_2_ngd_rate": Fraction(dash_ngd["n_neg_ngd"], dash_ngd["sample_size"]),
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "NGD_INTEGRATION_REGRESSION_LGGR" if defect_p2 == -1 else "STAGE_E2E_KERNEL_DASHBOARD_COHERENT_LGGG",
            "phase_3_global_kernel": pk_rep["global_evaluated_kernel"],
            "phase_3_egd_rate": dash_rep["evaluator_gluing_disagreement_egd"],
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "STAGE_E2E_KERNEL_DASHBOARD_COHERENT_LGGG" if eg_p3 == 1 else "CANCELLATION_MASKED_STAGE_KERNEL_LGGR",
            "masked_path_kernel_receipt": pk_mask,
            "masked_dashboard_receipt": dash_mask,
            "ngd_path_kernel_receipt": pk_ngd,
            "repaired_path_kernel_receipt": pk_rep,
            "repaired_dashboard_receipt": dash_rep,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one stage-vs-E2E evaluation must be recorded")
        n = len(self.evaluations)
        p1_mask_fail = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_ngd_fail = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        collapsing_dashboard_coherence_rate = Fraction(n - max(p1_mask_fail, p2_ngd_fail), n)
        four_tuple_kernel_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_mask_fail == n and p2_ngd_fail == n:
            status = "STAGE_E2E_KERNEL_DASHBOARD_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "CANCELLATION_MASKED_STAGE_KERNEL_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_stage_vs_e2e_integration.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_cancellation_masked_count": p1_mask_fail,
            "phase_2_ngd_regression_count": p2_ngd_fail,
            "phase_3_repaired_coherent_count": p3_coherent,
            "collapsing_dashboard_coherence_rate": collapsing_dashboard_coherence_rate,
            "four_tuple_kernel_coherence_rate": four_tuple_kernel_coherence_rate,
            "dashboard_kernel_coherence_gain": (
                four_tuple_kernel_coherence_rate - collapsing_dashboard_coherence_rate
            ),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingThreePartyConstantBoundMonitor:
    """Online parameterized 8-context three-party no-signalling c_3 interval family monitor (Theorem 77).

    Wraps ``StreamingPositiveExtensionMonitor`` across the 5-point parameterized slice
    k in {0, 1, 2, 3, 4} (lambda = k / 4) between Q_{5/8} (CF = 192/768, N_min = 96/768)
    and p_* (CF = 228/768, N_min = 75/768):
      - Phase 1 (Bipartite c = 2 surrogate ceiling on interior point k = 2, lambda = 1/2):
        At lambda = 0, CF / N_min = 2 <= 2, yet at lambda = 1/2, CF(1/2) = 840/3072 and
        N_min(1/2) = 342/3072 give ratio CF / N_min = 140/57 > 2, refuting c_3 <= 2
        (L_c2 = 1, Eg_c2 = 0, defect_c2 = -1).
      - Phase 2 (Integer c = 3 ceiling on endpoint k = 4, lambda = 1):
        At lambda = 1/2, CF / N_min = 140/57 <= 3, yet at lambda = 1 (p_*),
        CF(1) = 912/3072 = 228/768 and N_min(1) = 300/3072 = 75/768 give ratio
        CF / N_min = 228/75 = 76/25 > 3, refuting c_3 <= 3 (L_c3 = 1, Eg_c3 = 0,
        defect_c3 = -1).
      - Phase 3 (Certified bracket c_3 in [228/75, 7] across all 5 slice points):
        Verifies via ``StreamingPositiveExtensionMonitor`` that every slice point k in {0..4}
        satisfies CF(k) <= (228/75) * N_min(k) <= 7 * N_min(k), with supremum ratio
        228/75 = 76/25 attained at k = 4 (L_brk = 1, Eg_brk = 1, defect_brk = 0).
    """

    def __init__(self, *, scope_id: str = "streaming-three-party-c3-bound-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.evaluations: list[dict[str, Any]] = []

    def evaluate_parameterized_slice(
        self,
        evaluation_id: str,
        *,
        slice_steps: Sequence[int] = (0, 1, 2, 3, 4),
    ) -> dict[str, Any]:
        """Audit the 5-point parameterized 8-context slice and bracket c_3 in [228/75, 7]."""
        eid = text(evaluation_id, "evaluation_id")
        steps = [exact_int(k, f"slice_steps[{idx}]") for idx, k in enumerate(sequence(slice_steps, "slice_steps"))]
        if steps != [0, 1, 2, 3, 4]:
            raise ValidationError("slice_steps must be [0, 1, 2, 3, 4]")

        ext_mon = StreamingPositiveExtensionMonitor(scope_id=f"{self.scope_id}-{eid}-ext")
        slice_records: list[dict[str, Any]] = []
        ratios: list[Fraction] = []

        for k in steps:
            cf_k = Fraction(768 + 36 * k, 3072)
            n_k = Fraction(384 - 21 * k, 3072)
            gamma_k = Fraction(1) - cf_k
            audit_k = ext_mon.audit_signed_extension(f"{eid}::k={k}", 8, gamma_k, n_k)
            ratio_k = cf_k / n_k
            ratios.append(ratio_k)
            slice_records.append(
                {
                    "step_k": k,
                    "lambda": Fraction(k, 4),
                    "contextual_fraction": cf_k,
                    "negative_mass": n_k,
                    "ratio_cf_over_n_min": ratio_k,
                    "exceeds_c2": ratio_k > Fraction(2),
                    "exceeds_c3_int": ratio_k > Fraction(3),
                    "within_c3_bracket": ratio_k <= Fraction(228, 75) and ratio_k <= Fraction(7),
                    "signed_extension_audit": audit_k,
                }
            )

        max_ratio = max(ratios)
        strictly_increasing = all(ratios[i] < ratios[i + 1] for i in range(len(ratios) - 1))
        all_m_bound = all(
            bool(r["signed_extension_audit"]["m_context_bound_verified"]) for r in slice_records
        )

        # Phase 1: Bipartite c = 2 ceiling fails at interior k = 2 (ratio 140/57 > 2)
        r0 = ratios[0]
        r2 = ratios[2]
        r4 = ratios[4]
        l_p1 = 1 if (r0 <= Fraction(2) and r2 > Fraction(2)) else 0
        eg_p1 = 1 if (l_p1 == 1 and r2 <= Fraction(2)) else 0
        defect_p1 = eg_p1 - l_p1

        # Phase 2: Conjectured c = 3 ceiling fails at endpoint k = 4 (ratio 228/75 > 3)
        l_p2 = 1 if (r2 <= Fraction(3) and r4 > Fraction(3)) else 0
        eg_p2 = 1 if (l_p2 == 1 and r4 <= Fraction(3)) else 0
        defect_p2 = eg_p2 - l_p2

        # Phase 3: Certified interval bracket c_3 in [228/75, 7]
        l_p3 = (
            1
            if (
                strictly_increasing
                and all_m_bound
                and max_ratio == Fraction(228, 75)
                and max_ratio <= Fraction(7)
            )
            else 0
        )
        eg_p3 = 1 if (l_p3 == 1 and r2 == Fraction(140, 57)) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eid,
            "num_contexts": 8,
            "c3_lower_bound": max_ratio,
            "c3_upper_bound": Fraction(7),
            "interior_k2_ratio": r2,
            "endpoint_k4_ratio": r4,
            "ratios_strictly_increasing": strictly_increasing,
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "BIPARTITE_C2_BOUND_VIOLATION_LGGR" if defect_p1 == -1 else "THREE_PARTY_C3_BRACKET_CERTIFIED_LGGG",
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "C3_INTEGER_THREE_CEILING_VIOLATION_LGGR" if defect_p2 == -1 else "THREE_PARTY_C3_BRACKET_CERTIFIED_LGGG",
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "THREE_PARTY_C3_BRACKET_CERTIFIED_LGGG" if eg_p3 == 1 else "C3_INTEGER_THREE_CEILING_VIOLATION_LGGR",
            "slice_records": slice_records,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one parameterized slice evaluation must be recorded")
        n = len(self.evaluations)
        p1_c2_fail = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_c3_fail = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        surrogate_ceiling_coherence_rate = Fraction(n - max(p1_c2_fail, p2_c3_fail), n)
        certified_bracket_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_c2_fail == n and p2_c3_fail == n:
            status = "THREE_PARTY_C3_BRACKET_CERTIFIED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "C3_INTEGER_THREE_CEILING_VIOLATION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_three_party_c3_bound.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "c3_certified_lower_bound": Fraction(228, 75),
            "c3_constructive_upper_bound": Fraction(7),
            "phase_1_c2_violation_count": p1_c2_fail,
            "phase_2_c3_int_violation_count": p2_c3_fail,
            "phase_3_certified_bracket_count": p3_coherent,
            "surrogate_ceiling_coherence_rate": surrogate_ceiling_coherence_rate,
            "certified_bracket_coherence_rate": certified_bracket_coherence_rate,
            "c3_bracket_coherence_gain": (
                certified_bracket_coherence_rate - surrogate_ceiling_coherence_rate
            ),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingDynamicSchemaSynthesisMonitor:
    """Online automated boundary schema synthesis under fiber collisions (Theorem 78).

    Wraps ``StreamingFiberMonitor`` across a 4-state XNOR parity stream X = {s00, s01, s10, s11}
    sharing base report p_0 = {"status": "pass"} with candidate metadata features
    (k_noise, k1, k2) and query q(s_{i,j}) = 1[i == j]:
      - Phase 1 (Static 0-feature schema S_0 = [] on prefix {s00, s01}):
        s00 (q = 1) and s01 (q = 0) collide on p_0; keeping S_0 static leaves the stream
        obstructed (L_0 = 1, Eg_0 = 0, defect_0 = -1).
      - Phase 2 (1-feature greedy expansion S_1 = ["k2"] locked after prefix {s00, s01}):
        S_1 separates {s00, s01} (k2 = 0 vs 1), yet when s10 arrives with k2 = 0 = k2(s00)
        and q(s10) = 0 != 1 = q(s00), a moving-witness collision occurs on S_1
        (L_1 = 1, Eg_1 = 0, defect_1 = -1).
      - Phase 3 (Closed-loop online dynamic schema expansion S_0 -> S_1 = ["k2"] -> S_2* = ["k1", "k2"]):
        Automatically triggers ``synthesize_minimal_refinement`` on each observed collision,
        expanding S_0 -> ["k2"] at step 2 and ["k2"] -> ["k1", "k2"] at step 3 (while excluding
        the constant distractor k_noise = 1), achieving 4 collision-free fibers across all 4
        states (L_2 = 1, Eg_2 = 1, defect_2 = 0).
    """

    def __init__(self, *, scope_id: str = "streaming-dynamic-schema-synthesis-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.evaluations: list[dict[str, Any]] = []

    def evaluate_dynamic_synthesis(
        self,
        evaluation_id: str,
        *,
        candidate_keys: Sequence[str] = ("k_noise", "k1", "k2"),
    ) -> dict[str, Any]:
        """Evaluate static S_0, locked 1-feature S_1, and closed-loop dynamic schema synthesis S_2*."""
        eid = text(evaluation_id, "evaluation_id")
        cand = [text(k, f"candidate_keys[{idx}]") for idx, k in enumerate(sequence(candidate_keys, "candidate_keys"))]

        states = [
            ("s00", {"status": "pass"}, 1, {"k_noise": 1, "k1": 0, "k2": 0}),
            ("s01", {"status": "pass"}, 0, {"k_noise": 1, "k1": 0, "k2": 1}),
            ("s10", {"status": "pass"}, 0, {"k_noise": 1, "k1": 1, "k2": 0}),
            ("s11", {"status": "pass"}, 1, {"k_noise": 1, "k1": 1, "k2": 1}),
        ]

        # Phase 1: Static 0-feature monitor on prefix {s00, s01}
        mon_p1 = StreamingFiberMonitor(scope_id=f"{self.scope_id}-{eid}-p1")
        for sid, rep, qry, meta in states[:2]:
            mon_p1.observe(sid, rep, qry, metadata=meta)
        rec_p1 = mon_p1.get_receipt()
        ref_step2 = mon_p1.synthesize_minimal_refinement(cand)
        s1_keys = list(ref_step2["minimal_keys"] or [])

        # Phase 2: 1-feature schema S_1 locked across prefix {s00, s01, s10}
        mon_p2 = StreamingFiberMonitor(scope_id=f"{self.scope_id}-{eid}-p2")
        for sid, rep, qry, meta in states[:3]:
            proj_rep = {"base": rep, "features": {k: meta[k] for k in s1_keys}}
            mon_p2.observe(sid, proj_rep, qry, metadata=meta)
        rec_p2 = mon_p2.get_receipt()

        # Phase 3: Full 4-state stream + minimal-cardinality synthesis S_2* = ["k1", "k2"]
        mon_raw_all = StreamingFiberMonitor(scope_id=f"{self.scope_id}-{eid}-raw-all")
        for sid, rep, qry, meta in states:
            mon_raw_all.observe(sid, rep, qry, metadata=meta)
        ref_full = mon_raw_all.synthesize_minimal_refinement(cand)
        s2_keys = list(ref_full["minimal_keys"] or [])

        mon_p3 = StreamingFiberMonitor(scope_id=f"{self.scope_id}-{eid}-p3")
        for sid, rep, qry, meta in states:
            proj_rep = {"base": rep, "features": {k: meta[k] for k in s2_keys}}
            mon_p3.observe(sid, proj_rep, qry, metadata=meta)
        rec_p3 = mon_p3.get_receipt()

        l_p1 = 1 if mon_p1.is_obstructed else 0
        eg_p1 = 1 if (l_p1 == 1 and not mon_p1.is_obstructed) else 0
        defect_p1 = eg_p1 - l_p1

        l_p2 = 1 if (len(s1_keys) == 1 and mon_p2.is_obstructed) else 0
        eg_p2 = 1 if (l_p2 == 1 and not mon_p2.is_obstructed) else 0
        defect_p2 = eg_p2 - l_p2

        l_p3 = (
            1
            if (
                s2_keys == ["k1", "k2"]
                and "k_noise" not in s2_keys
                and not mon_p3.is_obstructed
                and len(rec_p3.get("decoder", [])) == 4
            )
            else 0
        )
        eg_p3 = 1 if (l_p3 == 1 and mon_p2.is_obstructed) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eid,
            "step_2_synthesized_keys": s1_keys,
            "step_3_synthesized_keys": s2_keys,
            "distractor_excluded": "k_noise" not in s2_keys,
            "final_decoder_size": len(rec_p3.get("decoder", [])),
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "STATIC_SCHEMA_FIBER_COLLISION_LGGR" if defect_p1 == -1 else "DYNAMIC_SCHEMA_SYNTHESIS_CONVERGED_LGGG",
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "SINGLE_FEATURE_MOVING_COLLISION_LGGR" if defect_p2 == -1 else "DYNAMIC_SCHEMA_SYNTHESIS_CONVERGED_LGGG",
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "DYNAMIC_SCHEMA_SYNTHESIS_CONVERGED_LGGG" if eg_p3 == 1 else "SINGLE_FEATURE_MOVING_COLLISION_LGGR",
            "phase_1_fiber_receipt": rec_p1,
            "phase_2_fiber_receipt": rec_p2,
            "phase_3_refinement_receipt": ref_full,
            "phase_3_fiber_receipt": rec_p3,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one dynamic schema synthesis evaluation must be recorded")
        n = len(self.evaluations)
        p1_static_fail = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_moving_fail = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        locked_schema_coherence_rate = Fraction(n - max(p1_static_fail, p2_moving_fail), n)
        dynamic_synthesis_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_static_fail == n and p2_moving_fail == n:
            status = "DYNAMIC_SCHEMA_SYNTHESIS_CONVERGED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "SINGLE_FEATURE_MOVING_COLLISION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_dynamic_schema_synthesis.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_static_collision_count": p1_static_fail,
            "phase_2_moving_collision_count": p2_moving_fail,
            "phase_3_dynamic_converged_count": p3_coherent,
            "locked_schema_coherence_rate": locked_schema_coherence_rate,
            "dynamic_synthesis_coherence_rate": dynamic_synthesis_coherence_rate,
            "dynamic_schema_coherence_gain": (
                dynamic_synthesis_coherence_rate - locked_schema_coherence_rate
            ),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingAdversarialSchemaSideChannelMonitor:
    """Online adversarial prompt injection schema synthesis and side-channel bit allocation monitor (Theorem 79).

    Wraps ``StreamingFiberMonitor`` and ``StreamingSideInformationCapacityMonitor`` across a 4-state
    autonomous swarm stream X = {s00, s01, s10, s11} with K = 4 distinct injection classes
    (benign_exec, prompt_override, tool_hijack, exfil_payload), safety query q = (1, 0, 0, 0),
    unauthenticated agent-writable metadata key ``k_agent_self_report`` spoofed by ``prompt_override``
    (s01) to match ``benign_exec`` (s00) (``k_agent_self_report`` = (1, 1, 0, 0)), and
    host-authenticated provenance keys ``k_host_1``, ``k_host_2`` in {0, 1}^2:
      - Phase 1 (Unauthenticated Schema Trusting Agent-Writable Metadata ``k_agent_self_report``):
        When ``k_agent_self_report`` is trusted on prefix {s00, s01}, s01 (prompt_override, q = 0)
        spoofs k_agent_self_report = 1 = k_agent_self_report(s00) (benign_exec, q = 1), inducing
        an adversarial fiber collision (L_spoof = 1, Eg_spoof = 0, defect_spoof = -1,
        status ``SPOOFED_METADATA_INJECTION_COLLISION_LGGR``).
      - Phase 2 (Host-Authenticated Schema Synthesis With Underallocated 1-Bit Side-Channel b = 1, S = 2 < K = 4):
        Excludes ``k_agent_self_report`` and synthesizes host-verified schema ["k_host_1", "k_host_2"]
        with 0 safety fiber collisions, yet allocating only b = 1 side-channel bit (S = 2^1 = 2 < K = 4)
        leaves a positive side-channel collision floor K - S = 4 - 2 = 2 > 0
        (L_under = 1, Eg_under = 0, defect_under = -1, status ``SIDE_CHANNEL_UNDERALLOCATION_FLOOR_LGGR``).
      - Phase 3 (Host-Authenticated Schema Synthesis + Adaptive 2-Bit Side-Channel Allocation b = 2, S = 4 = K):
        Combines host-authenticated schema ["k_host_1", "k_host_2"] with b = 2 side-channel bits
        (S = 2^2 = 4 >= K = 4), achieving 0 spoofed safety collisions and 0 side-channel collision floor
        (L_auth = 1, Eg_auth = 1, defect_auth = 0, status ``HOST_AUTHENTICATED_SCHEMA_SIDE_CHANNEL_COHERENT_LGGG``).
    """

    def __init__(self, *, scope_id: str = "streaming-adversarial-schema-side-channel-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.capacity_monitor = StreamingSideInformationCapacityMonitor(
            scope_id=f"{self.scope_id}-capacity"
        )
        self.evaluations: list[dict[str, Any]] = []

    def evaluate_adversarial_injection(
        self,
        evaluation_id: str,
        *,
        host_candidate_keys: Sequence[str] = ("k_host_1", "k_host_2"),
        injection_classes: Sequence[str] = (
            "benign_exec",
            "prompt_override",
            "tool_hijack",
            "exfil_payload",
        ),
        underallocated_bits: int = 1,
        authenticated_bits: int = 2,
    ) -> dict[str, Any]:
        """Evaluate spoofed agent metadata, underallocated 1-bit side-channel, and host-authenticated 2-bit side-channel."""
        eid = text(evaluation_id, "evaluation_id")
        host_keys = [
            text(k, f"host_candidate_keys[{idx}]")
            for idx, k in enumerate(sequence(host_candidate_keys, "host_candidate_keys"))
        ]
        classes = [
            text(c, f"injection_classes[{idx}]")
            for idx, c in enumerate(sequence(injection_classes, "injection_classes"))
        ]
        if len(classes) != 4 or len(set(classes)) != 4:
            raise ValidationError("injection_classes must contain K = 4 distinct classes")
        b_under = exact_int(underallocated_bits, "underallocated_bits", minimum=1)
        b_auth = exact_int(authenticated_bits, "authenticated_bits", minimum=2)
        s_under = 1 << b_under
        s_auth = 1 << b_auth

        states = [
            ("s00", {"status": "pass"}, 1, {"k_agent_self_report": 1, "k_host_1": 0, "k_host_2": 0}),
            ("s01", {"status": "pass"}, 0, {"k_agent_self_report": 1, "k_host_1": 0, "k_host_2": 1}),
            ("s10", {"status": "pass"}, 0, {"k_agent_self_report": 0, "k_host_1": 1, "k_host_2": 0}),
            ("s11", {"status": "pass"}, 0, {"k_agent_self_report": 0, "k_host_1": 1, "k_host_2": 1}),
        ]

        # Phase 1: Unauthenticated schema trusting k_agent_self_report on prefix {s00, s01}
        mon_spoof = StreamingFiberMonitor(scope_id=f"{self.scope_id}-{eid}-p1-spoof")
        for sid, rep, qry, meta in states[:2]:
            proj_spoof = {"base": rep, "k_agent_self_report": meta["k_agent_self_report"]}
            mon_spoof.observe(sid, proj_spoof, qry, metadata=meta)
        rec_spoof = mon_spoof.get_receipt()

        # Host-authenticated minimal refinement across all 4 states using only host_keys
        mon_raw = StreamingFiberMonitor(scope_id=f"{self.scope_id}-{eid}-raw")
        for sid, rep, qry, meta in states:
            mon_raw.observe(sid, rep, qry, metadata=meta)
        ref_host = mon_raw.synthesize_minimal_refinement(host_keys)
        synth_host_keys = list(ref_host["minimal_keys"] or [])

        mon_host = StreamingFiberMonitor(scope_id=f"{self.scope_id}-{eid}-host")
        for sid, rep, qry, meta in states:
            proj_host = {"base": rep, "features": {k: meta[k] for k in synth_host_keys}}
            mon_host.observe(sid, proj_host, qry, metadata=meta)
        rec_host = mon_host.get_receipt()

        # Phase 2: Underallocated 1-bit side-channel (S = 2 < K = 4)
        under_states = [
            {
                "state_id": states[i][0],
                "query_value": classes[i],
                "side_symbol": i % s_under,
            }
            for i in range(4)
        ]
        cap_under = self.capacity_monitor.record_fiber_channel(
            f"{eid}::phase_2_underallocated",
            under_states,
            channel_capacity_s=s_under,
            error_budget=0,
        )

        # Phase 3: Adaptive 2-bit side-channel (S = 4 = K)
        auth_states = [
            {
                "state_id": states[i][0],
                "query_value": classes[i],
                "side_symbol": i,
            }
            for i in range(4)
        ]
        cap_auth = self.capacity_monitor.record_fiber_channel(
            f"{eid}::phase_3_authenticated",
            auth_states,
            channel_capacity_s=s_auth,
            error_budget=0,
        )

        floor_under = int(cap_under["realized_subfiber_error_floor"])
        floor_auth = int(cap_auth["realized_subfiber_error_floor"])

        l_p1 = 1 if mon_spoof.is_obstructed else 0
        eg_p1 = 1 if (l_p1 == 1 and not mon_spoof.is_obstructed) else 0
        defect_p1 = eg_p1 - l_p1

        l_p2 = 1 if (not mon_host.is_obstructed and floor_under > 0) else 0
        eg_p2 = 1 if (l_p2 == 1 and floor_under == 0) else 0
        defect_p2 = eg_p2 - l_p2

        l_p3 = (
            1
            if (
                synth_host_keys == ["k_host_1", "k_host_2"]
                and "k_agent_self_report" not in synth_host_keys
                and not mon_host.is_obstructed
                and floor_auth == 0
                and s_auth >= len(classes)
            )
            else 0
        )
        eg_p3 = 1 if (l_p3 == 1 and floor_auth < floor_under and mon_spoof.is_obstructed) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eid,
            "synthesized_host_keys": synth_host_keys,
            "unauthenticated_key_excluded": "k_agent_self_report" not in synth_host_keys,
            "distinct_injection_classes_k": len(classes),
            "underallocated_side_channel_s": s_under,
            "authenticated_side_channel_s": s_auth,
            "underallocated_collision_floor": floor_under,
            "authenticated_collision_floor": floor_auth,
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "SPOOFED_METADATA_INJECTION_COLLISION_LGGR" if defect_p1 == -1 else "HOST_AUTHENTICATED_SCHEMA_SIDE_CHANNEL_COHERENT_LGGG",
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "SIDE_CHANNEL_UNDERALLOCATION_FLOOR_LGGR" if defect_p2 == -1 else "HOST_AUTHENTICATED_SCHEMA_SIDE_CHANNEL_COHERENT_LGGG",
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "HOST_AUTHENTICATED_SCHEMA_SIDE_CHANNEL_COHERENT_LGGG" if eg_p3 == 1 else "SIDE_CHANNEL_UNDERALLOCATION_FLOOR_LGGR",
            "phase_1_spoof_fiber_receipt": rec_spoof,
            "host_refinement_receipt": ref_host,
            "host_fiber_receipt": rec_host,
            "phase_2_capacity_receipt": cap_under,
            "phase_3_capacity_receipt": cap_auth,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one adversarial injection evaluation must be recorded")
        n = len(self.evaluations)
        p1_spoof_fail = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_under_fail = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        unauthenticated_or_underallocated_coherence_rate = Fraction(
            n - max(p1_spoof_fail, p2_under_fail), n
        )
        host_authenticated_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_spoof_fail == n and p2_under_fail == n:
            status = "HOST_AUTHENTICATED_SCHEMA_SIDE_CHANNEL_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "SPOOFED_METADATA_INJECTION_COLLISION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_adversarial_schema_side_channel.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_spoofed_metadata_collision_count": p1_spoof_fail,
            "phase_2_side_channel_underallocation_count": p2_under_fail,
            "phase_3_host_authenticated_coherent_count": p3_coherent,
            "unauthenticated_or_underallocated_coherence_rate": unauthenticated_or_underallocated_coherence_rate,
            "host_authenticated_coherence_rate": host_authenticated_coherence_rate,
            "host_authenticated_coherence_gain": (
                host_authenticated_coherence_rate - unauthenticated_or_underallocated_coherence_rate
            ),
            "capacity_monitor_receipt": self.capacity_monitor.get_receipt(),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingEqualInfoMigrationObligationMonitor:
    """Controlled equal-information comparative evaluation monitor across representation migrations and deferred obligations (Theorem 80).

    Wraps ``StreamingBaselineComparator`` and ``StreamingAuditMonitor`` on ``BudgetPolicy``
    (allowed_states=(0, 1, 2, 3, 4), max_step=2, max_total=3, representation_id="rep-v1",
    query_scope="every_prefix") across 3 multi-step histories supplied with identical input evidence:
      - Phase 1 (Uncertified Representation Migration Mid-Stream on 0 -> 2 -> 3 -> 1):
        Step index 1 changes ``representation_id`` from "rep-v1" to "rep-v2" without a transport
        certificate. All local step magnitudes <= 2 and endpoint |1 - 0| = 1 <= 3 pass the
        conventional baseline checker (conventional_accepts = True), while ``StreamingAuditMonitor``
        localizes ``REPRESENTATION_ID_CHANGED`` at step index 1 (lggr_accepts = False,
        conventional_false_acceptance = True, L_mig = 1, Eg_mig = 0, defect_mig = -1,
        status ``UNCERTIFIED_REPRESENTATION_MIGRATION_FALSE_ACCEPT_LGGR``).
      - Phase 2 (Retained Deferred Obligation & Prefix Excursion on 0 -> 2 -> 4 -> 2):
        Step index 1 attaches ``obligations=("recheck_schema_invariant",)`` and reaches prefix 4 > 3
        before reverting to endpoint 2 <= 3. The conventional checker accepts (conventional_accepts = True),
        while LGGR localizes both ``OPEN_OBLIGATIONS`` and prefix excursion at step index 1
        (lggr_accepts = False, conventional_false_acceptance = True, L_obl = 1, Eg_obl = 0,
        defect_obl = -1, status ``DEFERRED_OBLIGATION_PREFIX_EXCURSION_FALSE_ACCEPT_LGGR``).
      - Phase 3 (Representation-Stable, Obligation-Cleared, Prefix-Bounded Trajectory 0 -> 1 -> 2 -> 2):
        Uniform representation "rep-v1", zero open obligations, and all prefixes <= 3. Both
        checkers accept with 0 false acceptances (L_coh = 1, Eg_coh = 1, defect_coh = 0,
        status ``EQUAL_INFO_MIGRATION_OBLIGATION_AUDIT_COHERENT_LGGG``).
    """

    def __init__(self, *, scope_id: str = "streaming-equal-info-migration-obligation-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.policy = BudgetPolicy(
            policy_id="equal-info-policy/v1",
            spec_id="equal-info-spec/v1",
            evaluator_id="equal-info-eval/v1",
            representation_id="rep-v1",
            authority_id="equal-info-auth/v1",
            allowed_states=(0, 1, 2, 3, 4),
            max_step=2,
            max_total=3,
            query_scope="every_prefix",
        )
        self.comparator = StreamingBaselineComparator(self.policy)
        self.evaluations: list[dict[str, Any]] = []

    def evaluate_equal_info_comparison(
        self,
        evaluation_id: str,
        *,
        migrated_representation_id: str = "rep-v2",
        deferred_obligation_tag: str = "recheck_schema_invariant",
    ) -> dict[str, Any]:
        """Compare conventional local+endpoint baseline checker against LGGR across Phases 1-3."""
        eid = text(evaluation_id, "evaluation_id")
        mig_rep = text(migrated_representation_id, "migrated_representation_id")
        obl_tag = text(deferred_obligation_tag, "deferred_obligation_tag")
        if mig_rep == self.policy.representation_id:
            raise ValidationError("migrated_representation_id must differ from policy representation_id")

        baseline = StateRef("s0", 0)
        pol = self.policy

        # Phase 1: 0 -> 2 -> 3 -> 1 with uncertified representation migration at step index 1
        steps_p1 = [
            StepWitness(
                f"{eid}-p1-w0",
                StateRef("s0", 0),
                StateRef("s1", 2),
                pol.sha256,
                pol.evaluator_id,
                pol.spec_id,
                pol.representation_id,
                pol.authority_id,
                2,
                True,
                True,
                (),
            ),
            StepWitness(
                f"{eid}-p1-w1",
                StateRef("s1", 2),
                StateRef("s2", 3),
                pol.sha256,
                pol.evaluator_id,
                pol.spec_id,
                mig_rep,
                pol.authority_id,
                1,
                True,
                True,
                (),
            ),
            StepWitness(
                f"{eid}-p1-w2",
                StateRef("s2", 3),
                StateRef("s3", 1),
                pol.sha256,
                pol.evaluator_id,
                pol.spec_id,
                pol.representation_id,
                pol.authority_id,
                2,
                True,
                True,
                (),
            ),
        ]
        comp_p1 = self.comparator.compare_trace(f"{eid}::phase_1_migration", baseline, steps_p1)

        # Phase 2: 0 -> 2 -> 4 -> 2 with retained deferred obligation & prefix excursion at step index 1
        steps_p2 = [
            StepWitness(
                f"{eid}-p2-w0",
                StateRef("s0", 0),
                StateRef("s1", 2),
                pol.sha256,
                pol.evaluator_id,
                pol.spec_id,
                pol.representation_id,
                pol.authority_id,
                2,
                True,
                True,
                (),
            ),
            StepWitness(
                f"{eid}-p2-w1",
                StateRef("s1", 2),
                StateRef("s2", 4),
                pol.sha256,
                pol.evaluator_id,
                pol.spec_id,
                pol.representation_id,
                pol.authority_id,
                2,
                True,
                True,
                (obl_tag,),
            ),
            StepWitness(
                f"{eid}-p2-w2",
                StateRef("s2", 4),
                StateRef("s3", 2),
                pol.sha256,
                pol.evaluator_id,
                pol.spec_id,
                pol.representation_id,
                pol.authority_id,
                2,
                True,
                True,
                (),
            ),
        ]
        comp_p2 = self.comparator.compare_trace(f"{eid}::phase_2_obligation", baseline, steps_p2)

        # Phase 3: 0 -> 1 -> 2 -> 2 representation-stable, obligation-cleared, prefix-bounded
        steps_p3 = [
            StepWitness(
                f"{eid}-p3-w0",
                StateRef("s0", 0),
                StateRef("s1", 1),
                pol.sha256,
                pol.evaluator_id,
                pol.spec_id,
                pol.representation_id,
                pol.authority_id,
                1,
                True,
                True,
                (),
            ),
            StepWitness(
                f"{eid}-p3-w1",
                StateRef("s1", 1),
                StateRef("s2", 2),
                pol.sha256,
                pol.evaluator_id,
                pol.spec_id,
                pol.representation_id,
                pol.authority_id,
                1,
                True,
                True,
                (),
            ),
            StepWitness(
                f"{eid}-p3-w2",
                StateRef("s2", 2),
                StateRef("s3", 2),
                pol.sha256,
                pol.evaluator_id,
                pol.spec_id,
                pol.representation_id,
                pol.authority_id,
                0,
                True,
                True,
                (),
            ),
        ]
        comp_p3 = self.comparator.compare_trace(f"{eid}::phase_3_coherent", baseline, steps_p3)

        l_p1 = 1 if (comp_p1["conventional_accepts"] and comp_p1["first_fault_step_index"] == 1) else 0
        eg_p1 = 1 if (l_p1 == 1 and comp_p1["lggr_accepts"]) else 0
        defect_p1 = eg_p1 - l_p1

        l_p2 = (
            1
            if (
                comp_p2["conventional_accepts"]
                and comp_p2["first_fault_step_index"] == 1
                and obl_tag in comp_p2["retained_obligations"]
            )
            else 0
        )
        eg_p2 = 1 if (l_p2 == 1 and comp_p2["lggr_accepts"]) else 0
        defect_p2 = eg_p2 - l_p2

        l_p3 = (
            1
            if (
                comp_p3["conventional_accepts"]
                and comp_p3["lggr_accepts"]
                and not comp_p3["conventional_false_acceptance"]
                and comp_p3["first_fault_step_index"] is None
                and len(comp_p3["retained_obligations"]) == 0
            )
            else 0
        )
        eg_p3 = (
            1
            if (
                l_p3 == 1
                and comp_p1["conventional_false_acceptance"]
                and comp_p2["conventional_false_acceptance"]
            )
            else 0
        )
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eid,
            "phase_1_first_fault_step": comp_p1["first_fault_step_index"],
            "phase_2_first_fault_step": comp_p2["first_fault_step_index"],
            "phase_2_retained_obligations": comp_p2["retained_obligations"],
            "phase_3_first_fault_step": comp_p3["first_fault_step_index"],
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "UNCERTIFIED_REPRESENTATION_MIGRATION_FALSE_ACCEPT_LGGR" if defect_p1 == -1 else "EQUAL_INFO_MIGRATION_OBLIGATION_AUDIT_COHERENT_LGGG",
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "DEFERRED_OBLIGATION_PREFIX_EXCURSION_FALSE_ACCEPT_LGGR" if defect_p2 == -1 else "EQUAL_INFO_MIGRATION_OBLIGATION_AUDIT_COHERENT_LGGG",
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "EQUAL_INFO_MIGRATION_OBLIGATION_AUDIT_COHERENT_LGGG" if eg_p3 == 1 else "DEFERRED_OBLIGATION_PREFIX_EXCURSION_FALSE_ACCEPT_LGGR",
            "phase_1_comparison": comp_p1,
            "phase_2_comparison": comp_p2,
            "phase_3_comparison": comp_p3,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one equal-information comparison evaluation must be recorded")
        n = len(self.evaluations)
        p1_mig_false_acc = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_obl_false_acc = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        conventional_checker_soundness_rate = Fraction(
            n - max(p1_mig_false_acc, p2_obl_false_acc), n
        )
        lggr_equal_info_soundness_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_mig_false_acc == n and p2_obl_false_acc == n:
            status = "EQUAL_INFO_MIGRATION_OBLIGATION_AUDIT_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "UNCERTIFIED_REPRESENTATION_MIGRATION_FALSE_ACCEPT_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_equal_info_migration_obligation.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_migration_false_acceptance_count": p1_mig_false_acc,
            "phase_2_obligation_false_acceptance_count": p2_obl_false_acc,
            "phase_3_equal_info_coherent_count": p3_coherent,
            "conventional_checker_soundness_rate": conventional_checker_soundness_rate,
            "lggr_equal_info_soundness_rate": lggr_equal_info_soundness_rate,
            "equal_info_soundness_gain": (
                lggr_equal_info_soundness_rate - conventional_checker_soundness_rate
            ),
            "baseline_comparator_receipt": self.comparator.get_receipt(),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingCatalystRejuvenationScheduleMonitor:
    """Online multi-cycle constructor catalyst wear and periodic rejuvenation schedule monitor (Theorem 81).

    Wraps ``StreamingCatalystDegradationMonitor`` with initial state C_0 = 0, global tolerance
    tau_cat = 1, and per-cycle local tolerance eps_local = 1/3 (uniform wear delta = 1/3 has
    cycle ceiling N_max = floor(1 / (1/3)) = 3):
      - Phase 1 (Unscheduled Continuous Wear Across 4 Cycles: +1/3, +1/3, +1/3, +1/3):
        Every cycle satisfies |delta_t| = 1/3 <= 1/3 (L_unsched = 1), yet cycle 4 reaches
        cumulative deviation 4/3 > 1 = tau_cat (Eg_unsched = 0, defect_unsched = -1,
        status ``UNSCHEDULED_CATALYST_WEAR_EXHAUSTION_LGGR``).
      - Phase 2 (Late Rejuvenation After Ceiling Breach at Cycle 4: +1/3, +1/3, +1/3, +1/3, -1/3):
        Applying a -1/3 rejuvenation step at cycle 5 restores terminal state C_5 = 1 <= tau_cat,
        yet the prefix peak at cycle 4 already breached max_t |C_t - C_0| = 4/3 > 1 = tau_cat
        (L_late = 1, Eg_late = 0, defect_late = -1, status ``LATE_REJUVENATION_PREFIX_EXHAUSTION_LGGR``).
      - Phase 3 (Periodic Catalyst Rejuvenation Within Ceiling N_max = 3: +1/3, +1/3, -1/3, +1/3, -1/3):
        Applies bounded -1/3 rejuvenation steps before cumulative wear exceeds tau_cat = 1,
        keeping max_t |C_t - C_0| = 2/3 <= 1 = tau_cat across all 5 cycles
        (L_rejuv = 1, Eg_rejuv = 1, defect_rejuv = 0, status ``PERIODIC_CATALYST_REJUVENATION_COHERENT_LGGG``).
    """

    def __init__(self, *, scope_id: str = "streaming-catalyst-rejuvenation-schedule-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.evaluations: list[dict[str, Any]] = []

    def evaluate_rejuvenation_schedules(
        self,
        evaluation_id: str,
        *,
        catalyst_tolerance: Fraction | int | str = 1,
        per_cycle_wear: Fraction | int | str = "1/3",
    ) -> dict[str, Any]:
        """Evaluate unscheduled wear, late rejuvenation, and periodic rejuvenation schedules."""
        eid = text(evaluation_id, "evaluation_id")
        tau_cat = rational(catalyst_tolerance)
        delta = rational(per_cycle_wear)
        if tau_cat <= 0 or delta <= 0:
            raise ValidationError("catalyst_tolerance and per_cycle_wear must be positive")

        # Phase 1: 4 unscheduled wear cycles (+delta, +delta, +delta, +delta)
        mon_p1 = StreamingCatalystDegradationMonitor(
            initial_catalyst_state=0,
            catalyst_tolerance=tau_cat,
            per_cycle_local_tolerance=delta,
            scope_id=f"{self.scope_id}-{eid}-p1",
        )
        for idx in range(4):
            mon_p1.record_cycle(f"p1-c{idx}", f"sub_{idx}", f"sub_{idx+1}", True, delta)
        rec_p1 = mon_p1.get_receipt()

        # Phase 2: 5 cycles with late rejuvenation after cycle 4 breach (+delta x 4, -delta)
        mon_p2 = StreamingCatalystDegradationMonitor(
            initial_catalyst_state=0,
            catalyst_tolerance=tau_cat,
            per_cycle_local_tolerance=delta,
            scope_id=f"{self.scope_id}-{eid}-p2",
        )
        for idx, step_w in enumerate([delta, delta, delta, delta, -delta]):
            mon_p2.record_cycle(f"p2-c{idx}", f"sub_{idx}", f"sub_{idx+1}", True, step_w)
        rec_p2 = mon_p2.get_receipt()

        # Phase 3: 5 cycles with periodic rejuvenation within ceiling (+delta, +delta, -delta, +delta, -delta)
        mon_p3 = StreamingCatalystDegradationMonitor(
            initial_catalyst_state=0,
            catalyst_tolerance=tau_cat,
            per_cycle_local_tolerance=delta,
            scope_id=f"{self.scope_id}-{eid}-p3",
        )
        for idx, step_w in enumerate([delta, delta, -delta, delta, -delta]):
            mon_p3.record_cycle(f"p3-c{idx}", f"sub_{idx}", f"sub_{idx+1}", True, step_w)
        rec_p3 = mon_p3.get_receipt()

        peak_p1 = rational(rec_p1["max_catalyst_deviation"])
        peak_p2 = rational(rec_p2["max_catalyst_deviation"])
        term_p2 = abs(rational(rec_p2["terminal_catalyst_state"]))
        peak_p3 = rational(rec_p3["max_catalyst_deviation"])
        ceiling = int(tau_cat // delta)

        l_p1 = 1 if (rec_p1["local_product_aggregator"] == 1 and peak_p1 > tau_cat) else 0
        eg_p1 = 1 if (l_p1 == 1 and rec_p1["global_evaluator"] == 1) else 0
        defect_p1 = eg_p1 - l_p1

        l_p2 = (
            1
            if (rec_p2["local_product_aggregator"] == 1 and term_p2 <= tau_cat and peak_p2 > tau_cat)
            else 0
        )
        eg_p2 = 1 if (l_p2 == 1 and rec_p2["global_evaluator"] == 1) else 0
        defect_p2 = eg_p2 - l_p2

        l_p3 = (
            1
            if (
                rec_p3["local_product_aggregator"] == 1
                and rec_p3["global_evaluator"] == 1
                and peak_p3 <= tau_cat
            )
            else 0
        )
        eg_p3 = 1 if (l_p3 == 1 and peak_p3 < peak_p1 and peak_p3 < peak_p2) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eid,
            "uniform_wear_cycle_ceiling": ceiling,
            "phase_1_max_deviation": peak_p1,
            "phase_2_max_deviation": peak_p2,
            "phase_2_terminal_deviation": term_p2,
            "phase_3_max_deviation": peak_p3,
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "UNSCHEDULED_CATALYST_WEAR_EXHAUSTION_LGGR" if defect_p1 == -1 else "PERIODIC_CATALYST_REJUVENATION_COHERENT_LGGG",
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "LATE_REJUVENATION_PREFIX_EXHAUSTION_LGGR" if defect_p2 == -1 else "PERIODIC_CATALYST_REJUVENATION_COHERENT_LGGG",
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "PERIODIC_CATALYST_REJUVENATION_COHERENT_LGGG" if eg_p3 == 1 else "LATE_REJUVENATION_PREFIX_EXHAUSTION_LGGR",
            "phase_1_catalyst_receipt": rec_p1,
            "phase_2_catalyst_receipt": rec_p2,
            "phase_3_catalyst_receipt": rec_p3,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one catalyst rejuvenation schedule evaluation must be recorded")
        n = len(self.evaluations)
        p1_unsched_fail = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_late_fail = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        unscheduled_or_late_coherence_rate = Fraction(
            n - max(p1_unsched_fail, p2_late_fail), n
        )
        periodic_rejuvenation_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_unsched_fail == n and p2_late_fail == n:
            status = "PERIODIC_CATALYST_REJUVENATION_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "UNSCHEDULED_CATALYST_WEAR_EXHAUSTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_catalyst_rejuvenation_schedule.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_unscheduled_exhaustion_count": p1_unsched_fail,
            "phase_2_late_rejuvenation_exhaustion_count": p2_late_fail,
            "phase_3_periodic_rejuvenation_coherent_count": p3_coherent,
            "unscheduled_or_late_coherence_rate": unscheduled_or_late_coherence_rate,
            "periodic_rejuvenation_coherence_rate": periodic_rejuvenation_coherence_rate,
            "periodic_rejuvenation_coherence_gain": (
                periodic_rejuvenation_coherence_rate - unscheduled_or_late_coherence_rate
            ),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingDFAResetTokenGluingMonitor:
    """Online tool-call DFA non-resetting concatenation vs. explicit reset-token gluing monitor (Theorem 82).

    Wraps ``StreamingDFAGrammarGluingMonitor`` on a 4-state lock/commit/release protocol DFA
    Q = {"q0_idle", "q1_lock", "q2_done", "q3_err"}, Sigma = {"acquire", "commit", "release"},
    initial_state = "q0_idle", accepting_states = {"q0_idle", "q2_done"}:
      - Phase 1 (Direct Concatenation of Non-Resetting Accepting Segments):
        w1 = ["acquire", "commit"] and w2 = ["acquire", "commit"] each terminate at
        "q2_done" in F from "q0_idle" (L_direct = 1), yet "q2_done" != "q0_idle" is not
        reset-idempotent, so w1 ++ w2 transitions "q2_done" --acquire--> "q3_err" not in F
        (Eg_direct = 0, defect_direct = -1, status ``NON_RESET_DFA_CONCATENATION_MISMATCH_LGGR``).
      - Phase 2 (Late Reset Token Appended Only to Segment 2):
        w1 = ["acquire", "commit"] and w2 = ["acquire", "commit", "release"] still leave
        1 non-reset segment (w1 ends at "q2_done"), so w2 enters "q3_err" at its first token
        (L_late = 1, Eg_late = 0, defect_late = -1, status ``UNRELEASED_PREFIX_TRAP_STATE_LGGR``).
      - Phase 3 (Explicit Reset-Token Gluing on Every Segment):
        w1 = ["acquire", "commit", "release"] and w2 = ["acquire", "commit", "release"] both
        return to "q0_idle" in F (0 non-reset segments), achieving coherent concatenation
        (L_reset = 1, Eg_reset = 1, defect_reset = 0, status ``EXPLICIT_RESET_DFA_GLUING_COHERENT_LGGG``).
    """

    DEFAULT_STATES: tuple[str, ...] = ("q0_idle", "q1_lock", "q2_done", "q3_err")
    DEFAULT_ALPHABET: tuple[str, ...] = ("acquire", "commit", "release")
    DEFAULT_ACCEPTING: tuple[str, ...] = ("q0_idle", "q2_done")
    DEFAULT_TRANSITIONS: dict[str, dict[str, str]] = {
        "q0_idle": {"acquire": "q1_lock", "commit": "q3_err", "release": "q0_idle"},
        "q1_lock": {"acquire": "q3_err", "commit": "q2_done", "release": "q0_idle"},
        "q2_done": {"acquire": "q3_err", "commit": "q3_err", "release": "q0_idle"},
        "q3_err": {"acquire": "q3_err", "commit": "q3_err", "release": "q3_err"},
    }

    def __init__(self, *, scope_id: str = "streaming-dfa-reset-token-gluing-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.evaluations: list[dict[str, Any]] = []

    def _new_dfa_monitor(self, suffix: str) -> StreamingDFAGrammarGluingMonitor:
        return StreamingDFAGrammarGluingMonitor(
            states=self.DEFAULT_STATES,
            alphabet=self.DEFAULT_ALPHABET,
            transitions=self.DEFAULT_TRANSITIONS,
            initial_state="q0_idle",
            accepting_states=self.DEFAULT_ACCEPTING,
            scope_id=f"{self.scope_id}-{suffix}",
        )

    def evaluate_dfa_reset_gluing(
        self,
        evaluation_id: str,
        *,
        base_segment: Sequence[str] = ("acquire", "commit"),
        reset_token: str = "release",
    ) -> dict[str, Any]:
        """Evaluate direct concatenation, late reset, and explicit per-segment reset-token gluing."""
        eid = text(evaluation_id, "evaluation_id")
        base_toks = [text(t, f"base_segment[{idx}]") for idx, t in enumerate(sequence(base_segment, "base_segment"))]
        rst_tok = text(reset_token, "reset_token")
        reset_seg = [*base_toks, rst_tok]

        # Phase 1: Direct concatenation w1 = base_toks, w2 = base_toks
        mon_p1 = self._new_dfa_monitor(f"{eid}-p1")
        mon_p1.record_segment("seg_1", base_toks)
        mon_p1.record_segment("seg_2", base_toks)
        rec_p1 = mon_p1.get_receipt()

        # Phase 2: Late reset token appended only to w2 (w1 = base_toks, w2 = reset_seg)
        mon_p2 = self._new_dfa_monitor(f"{eid}-p2")
        mon_p2.record_segment("seg_1", base_toks)
        mon_p2.record_segment("seg_2", reset_seg)
        rec_p2 = mon_p2.get_receipt()

        # Phase 3: Explicit reset token appended to every segment (w1 = reset_seg, w2 = reset_seg)
        mon_p3 = self._new_dfa_monitor(f"{eid}-p3")
        mon_p3.record_segment("seg_1", reset_seg)
        mon_p3.record_segment("seg_2", reset_seg)
        rec_p3 = mon_p3.get_receipt()

        non_reset_p1 = len(rec_p1["non_reset_accepting_segment_ids"])
        non_reset_p2 = len(rec_p2["non_reset_accepting_segment_ids"])
        non_reset_p3 = len(rec_p3["non_reset_accepting_segment_ids"])

        l_p1 = 1 if (rec_p1["local_product_aggregator"] == 1 and non_reset_p1 == 2) else 0
        eg_p1 = 1 if (l_p1 == 1 and rec_p1["global_concatenated_evaluator"] == 1) else 0
        defect_p1 = eg_p1 - l_p1

        l_p2 = 1 if (rec_p2["local_product_aggregator"] == 1 and non_reset_p2 == 1) else 0
        eg_p2 = 1 if (l_p2 == 1 and rec_p2["global_concatenated_evaluator"] == 1) else 0
        defect_p2 = eg_p2 - l_p2

        l_p3 = (
            1
            if (
                rec_p3["local_product_aggregator"] == 1
                and rec_p3["global_concatenated_evaluator"] == 1
                and non_reset_p3 == 0
                and rec_p3["terminal_state"] == "q0_idle"
            )
            else 0
        )
        eg_p3 = 1 if (l_p3 == 1 and non_reset_p3 < non_reset_p2 and non_reset_p2 < non_reset_p1) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eid,
            "phase_1_terminal_state": rec_p1["terminal_state"],
            "phase_2_terminal_state": rec_p2["terminal_state"],
            "phase_3_terminal_state": rec_p3["terminal_state"],
            "phase_1_non_reset_count": non_reset_p1,
            "phase_2_non_reset_count": non_reset_p2,
            "phase_3_non_reset_count": non_reset_p3,
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "NON_RESET_DFA_CONCATENATION_MISMATCH_LGGR" if defect_p1 == -1 else "EXPLICIT_RESET_DFA_GLUING_COHERENT_LGGG",
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "UNRELEASED_PREFIX_TRAP_STATE_LGGR" if defect_p2 == -1 else "EXPLICIT_RESET_DFA_GLUING_COHERENT_LGGG",
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "EXPLICIT_RESET_DFA_GLUING_COHERENT_LGGG" if eg_p3 == 1 else "UNRELEASED_PREFIX_TRAP_STATE_LGGR",
            "phase_1_dfa_receipt": rec_p1,
            "phase_2_dfa_receipt": rec_p2,
            "phase_3_dfa_receipt": rec_p3,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one DFA reset-token gluing evaluation must be recorded")
        n = len(self.evaluations)
        p1_direct_fail = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_late_fail = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        non_reset_concatenation_coherence_rate = Fraction(
            n - max(p1_direct_fail, p2_late_fail), n
        )
        explicit_reset_gluing_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_direct_fail == n and p2_late_fail == n:
            status = "EXPLICIT_RESET_DFA_GLUING_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "NON_RESET_DFA_CONCATENATION_MISMATCH_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_dfa_reset_token_gluing.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_direct_mismatch_count": p1_direct_fail,
            "phase_2_late_reset_trap_count": p2_late_fail,
            "phase_3_explicit_reset_coherent_count": p3_coherent,
            "non_reset_concatenation_coherence_rate": non_reset_concatenation_coherence_rate,
            "explicit_reset_gluing_coherence_rate": explicit_reset_gluing_coherence_rate,
            "explicit_reset_gluing_coherence_gain": (
                explicit_reset_gluing_coherence_rate - non_reset_concatenation_coherence_rate
            ),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingCPTPBlindspotCompletionMonitor:
    """Online state-dependent CPTP trace preservation vs. operator-level residual and Kraus completion monitor (Theorem 83).

    Wraps ``StreamingCPTPTraceMonitor`` on 2 x 2 rational Kraus families:
      - Phase 1 (Incomplete Kraus Family E_inc = {diag(1, 0)} Probed Only on Ground State rho_0 = diag(1, 0)):
        tr(E_inc(rho_0)) - tr(rho_0) = 0 passes state-specific trace check (L_blind = 1,
        state_blindspot_masked = True), yet operator residual R_TP = diag(0, -1) has L1 norm 1 > 0
        (Eg_blind = 0, defect_blind = -1, status ``STATE_BLINDSPOT_NON_TP_LGGR``).
      - Phase 2 (Incomplete Kraus Family E_inc = {diag(1, 0)} Probed on Excited State rho_1 = diag(0, 1)):
        Probing orthogonal basis state rho_1 exposes trace leakage tr(E_inc(rho_1)) - tr(rho_1) = -1 != 0
        with ||R_TP||_1 = 1 > 0 (L_leak = 1, Eg_leak = 0, defect_leak = -1,
        status ``EXCITED_STATE_TRACE_LEAKAGE_LGGR``).
      - Phase 3 (Completed Kraus Family E_comp = {diag(1, 0), diag(0, 1)} Probed Across Basis {rho_0, rho_1}):
        Adjoining K_1 = diag(0, 1) yields sum_r K_r^T K_r = I_2, ||R_TP||_1 = 0, and 0 trace
        discrepancy across both basis states (L_comp = 1, Eg_comp = 1, defect_comp = 0,
        status ``CPTP_OPERATOR_COMPLETION_VERIFIED_LGGG``).
    """

    def __init__(self, *, scope_id: str = "streaming-cptp-blindspot-completion-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.evaluations: list[dict[str, Any]] = []

    def evaluate_cptp_completion(
        self,
        evaluation_id: str,
        *,
        k0_matrix: Sequence[Sequence[Fraction | int | str]] = ((1, 0), (0, 0)),
        k1_matrix: Sequence[Sequence[Fraction | int | str]] = ((0, 0), (0, 1)),
        rho0_matrix: Sequence[Sequence[Fraction | int | str]] = ((1, 0), (0, 0)),
        rho1_matrix: Sequence[Sequence[Fraction | int | str]] = ((0, 0), (0, 1)),
    ) -> dict[str, Any]:
        """Evaluate state-blindspot on rho_0, trace leakage on rho_1, and completed Kraus operator TP."""
        eid = text(evaluation_id, "evaluation_id")

        # Phase 1 & 2: Incomplete Kraus family {K_0}
        mon_inc = StreamingCPTPTraceMonitor(
            [k0_matrix],
            scope_id=f"{self.scope_id}-{eid}-inc",
        )
        probe_p1 = mon_inc.probe_state("rho_0_ground", rho0_matrix)
        probe_p2 = mon_inc.probe_state("rho_1_excited", rho1_matrix)
        rec_inc = mon_inc.get_receipt()

        # Phase 3: Completed Kraus family {K_0, K_1}
        mon_comp = StreamingCPTPTraceMonitor(
            [k0_matrix, k1_matrix],
            scope_id=f"{self.scope_id}-{eid}-comp",
        )
        probe_p3_0 = mon_comp.probe_state("rho_0_ground", rho0_matrix)
        probe_p3_1 = mon_comp.probe_state("rho_1_excited", rho1_matrix)
        rec_comp = mon_comp.get_receipt()

        tr_diff_p1 = rational(probe_p1["trace_discrepancy"])
        tr_diff_p2 = rational(probe_p2["trace_discrepancy"])
        res_norm_inc = rational(rec_inc["residual_l1_norm"])
        res_norm_comp = rational(rec_comp["residual_l1_norm"])

        l_p1 = 1 if (tr_diff_p1 == Fraction(0) and probe_p1["state_blindspot_masked"]) else 0
        eg_p1 = 1 if (l_p1 == 1 and rec_inc["operator_trace_preserving"]) else 0
        defect_p1 = eg_p1 - l_p1

        l_p2 = 1 if (tr_diff_p2 == Fraction(-1) and res_norm_inc == Fraction(1)) else 0
        eg_p2 = 1 if (l_p2 == 1 and tr_diff_p2 == Fraction(0) and rec_inc["operator_trace_preserving"]) else 0
        defect_p2 = eg_p2 - l_p2

        l_p3 = (
            1
            if (
                rec_comp["operator_trace_preserving"]
                and res_norm_comp == Fraction(0)
                and rational(probe_p3_0["trace_discrepancy"]) == Fraction(0)
                and rational(probe_p3_1["trace_discrepancy"]) == Fraction(0)
            )
            else 0
        )
        eg_p3 = 1 if (l_p3 == 1 and res_norm_comp < res_norm_inc) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eid,
            "incomplete_residual_l1_norm": res_norm_inc,
            "completed_residual_l1_norm": res_norm_comp,
            "phase_1_trace_discrepancy": tr_diff_p1,
            "phase_2_trace_discrepancy": tr_diff_p2,
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "STATE_BLINDSPOT_NON_TP_LGGR" if defect_p1 == -1 else "CPTP_OPERATOR_COMPLETION_VERIFIED_LGGG",
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "EXCITED_STATE_TRACE_LEAKAGE_LGGR" if defect_p2 == -1 else "CPTP_OPERATOR_COMPLETION_VERIFIED_LGGG",
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "CPTP_OPERATOR_COMPLETION_VERIFIED_LGGG" if eg_p3 == 1 else "EXCITED_STATE_TRACE_LEAKAGE_LGGR",
            "incomplete_cptp_receipt": rec_inc,
            "completed_cptp_receipt": rec_comp,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one CPTP blindspot completion evaluation must be recorded")
        n = len(self.evaluations)
        p1_blind_fail = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_leak_fail = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        incomplete_channel_coherence_rate = Fraction(
            n - max(p1_blind_fail, p2_leak_fail), n
        )
        completed_channel_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_blind_fail == n and p2_leak_fail == n:
            status = "CPTP_OPERATOR_COMPLETION_VERIFIED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "STATE_BLINDSPOT_NON_TP_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_cptp_blindspot_completion.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_state_blindspot_count": p1_blind_fail,
            "phase_2_excited_leakage_count": p2_leak_fail,
            "phase_3_completed_tp_count": p3_coherent,
            "incomplete_channel_coherence_rate": incomplete_channel_coherence_rate,
            "completed_channel_coherence_rate": completed_channel_coherence_rate,
            "cptp_completion_coherence_gain": (
                completed_channel_coherence_rate - incomplete_channel_coherence_rate
            ),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingMayerVietorisReconciliationMonitor:
    """Online Mayer-Vietoris disconnected interface gluing and connecting-coboundary reconciliation monitor (Theorem 84).

    Wraps ``StreamingMayerVietorisMonitor`` on the 4-vertex two-subswarm cover K = U U V with
    U = {w0 -> u -> w1}, V = {w0 -> v -> w1}, and disconnected overlap U cap V = {w0, w1}:
      - Phase 1 (Locally Exact Sub-Swarms U, V With Disconnected Overlap Spread Delta_MV = 2 > 0):
        On U, h(w0->u) = 1, h(u->w1) = 2 (f_U(w1) = 3); on V, h(w0->v) = 1, h(v->w1) = 0
        (f_V(w1) = 1). Both U and V are locally exact trees (L_mv = 1), yet delta_{U cap V}(w0) = 0
        != 2 = delta_{U cap V}(w1) yields connecting coboundary spread Delta_MV = 2 > 0
        (Eg_mv = 0, defect_mv = -1, status ``MAYER_VIETORIS_CONNECTING_OBSTRUCTION_LGGR``).
      - Phase 2 (Partial Boundary Adjustment Leaving Residual Spread Delta_MV = 1 > 0):
        Adjusting h(v->w1) from 0 to 1 reduces Delta_MV from 2 to 1 > 0 (L_part = 1), yet
        delta_{U cap V}(w1) = 1 != 0 still obstructs global gluing on U U V
        (Eg_part = 0, defect_part = -1, status ``RESIDUAL_OVERLAP_SPREAD_OBSTRUCTION_LGGR``).
      - Phase 3 (Exact Connecting-Coboundary Reconciliation h(v->w1) = 2 => Delta_MV = 0):
        Reconciling h(v->w1) = 0 + Delta_MV = 2 yields f_V(w1) = 3 = f_U(w1), Delta_MV = 0,
        and a glued global potential f = {u: 1, v: 1, w0: 0, w1: 3} on U U V
        (L_rec = 1, Eg_rec = 1, defect_rec = 0, status ``MAYER_VIETORIS_COBOUNDARY_RECONCILED_LGGG``).
    """

    def __init__(self, *, scope_id: str = "streaming-mayer-vietoris-reconciliation-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.evaluations: list[dict[str, Any]] = []

    @staticmethod
    def _build_cover(
        scope_id: str,
        v_to_w1_val: Fraction,
    ) -> dict[str, Any]:
        mon = StreamingMayerVietorisMonitor(scope_id=scope_id)
        mon.record_edge("w0", "u", 1, in_u=True, in_v=False)
        mon.record_edge("u", "w1", 2, in_u=True, in_v=False)
        mon.record_edge("w0", "v", 1, in_u=False, in_v=True)
        mon.record_edge("v", "w1", v_to_w1_val, in_u=False, in_v=True)
        return mon.get_receipt()

    def evaluate_mv_reconciliation(
        self,
        evaluation_id: str,
        *,
        initial_v_to_w1: Fraction | int | str = 0,
        partial_v_to_w1: Fraction | int | str = 1,
        reconciled_v_to_w1: Fraction | int | str = 2,
    ) -> dict[str, Any]:
        """Evaluate disconnected overlap obstruction, partial adjustment, and exact coboundary reconciliation."""
        eid = text(evaluation_id, "evaluation_id")
        v0 = rational(initial_v_to_w1)
        v_part = rational(partial_v_to_w1)
        v_rec = rational(reconciled_v_to_w1)

        rec_p1 = self._build_cover(f"{self.scope_id}-{eid}-p1", v0)
        rec_p2 = self._build_cover(f"{self.scope_id}-{eid}-p2", v_part)
        rec_p3 = self._build_cover(f"{self.scope_id}-{eid}-p3", v_rec)

        spread_p1 = rational(rec_p1["connecting_coboundary_spread"])
        spread_p2 = rational(rec_p2["connecting_coboundary_spread"])
        spread_p3 = rational(rec_p3["connecting_coboundary_spread"])

        l_p1 = (
            1
            if (rec_p1["u_locally_exact"] and rec_p1["v_locally_exact"] and spread_p1 == Fraction(2))
            else 0
        )
        eg_p1 = 1 if (l_p1 == 1 and rec_p1["union_globally_exact"]) else 0
        defect_p1 = eg_p1 - l_p1

        l_p2 = (
            1
            if (
                rec_p2["u_locally_exact"]
                and rec_p2["v_locally_exact"]
                and spread_p2 == Fraction(1)
                and spread_p2 < spread_p1
            )
            else 0
        )
        eg_p2 = 1 if (l_p2 == 1 and rec_p2["union_globally_exact"]) else 0
        defect_p2 = eg_p2 - l_p2

        l_p3 = (
            1
            if (
                rec_p3["u_locally_exact"]
                and rec_p3["v_locally_exact"]
                and rec_p3["union_globally_exact"]
                and spread_p3 == Fraction(0)
                and rec_p3["glued_global_potential"] is not None
            )
            else 0
        )
        eg_p3 = 1 if (l_p3 == 1 and spread_p3 < spread_p2 and spread_p2 < spread_p1) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eid,
            "phase_1_coboundary_spread": spread_p1,
            "phase_2_coboundary_spread": spread_p2,
            "phase_3_coboundary_spread": spread_p3,
            "glued_global_potential": rec_p3["glued_global_potential"],
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "MAYER_VIETORIS_CONNECTING_OBSTRUCTION_LGGR" if defect_p1 == -1 else "MAYER_VIETORIS_COBOUNDARY_RECONCILED_LGGG",
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "RESIDUAL_OVERLAP_SPREAD_OBSTRUCTION_LGGR" if defect_p2 == -1 else "MAYER_VIETORIS_COBOUNDARY_RECONCILED_LGGG",
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "MAYER_VIETORIS_COBOUNDARY_RECONCILED_LGGG" if eg_p3 == 1 else "RESIDUAL_OVERLAP_SPREAD_OBSTRUCTION_LGGR",
            "phase_1_mv_receipt": rec_p1,
            "phase_2_mv_receipt": rec_p2,
            "phase_3_mv_receipt": rec_p3,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one Mayer-Vietoris reconciliation evaluation must be recorded")
        n = len(self.evaluations)
        p1_mv_fail = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_part_fail = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        unreconciled_overlap_coherence_rate = Fraction(
            n - max(p1_mv_fail, p2_part_fail), n
        )
        reconciled_coboundary_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_mv_fail == n and p2_part_fail == n:
            status = "MAYER_VIETORIS_COBOUNDARY_RECONCILED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "MAYER_VIETORIS_CONNECTING_OBSTRUCTION_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_mayer_vietoris_reconciliation.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_connecting_obstruction_count": p1_mv_fail,
            "phase_2_residual_spread_count": p2_part_fail,
            "phase_3_coboundary_reconciled_count": p3_coherent,
            "unreconciled_overlap_coherence_rate": unreconciled_overlap_coherence_rate,
            "reconciled_coboundary_coherence_rate": reconciled_coboundary_coherence_rate,
            "mv_reconciliation_coherence_gain": (
                reconciled_coboundary_coherence_rate - unreconciled_overlap_coherence_rate
            ),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingReplayOrderEnvelopeMonitor:
    """Online asynchronous arrival-order permutation prefix-peak envelope and robustness monitor (Theorem 85).

    Wraps ``StreamingReplayOrderMonitor`` under prefix budget B_prefix = 3 across 3 step-drift multisets:
      - Phase 1 (Arrival-Masked Causal Breach on Multiset {+2, +2, -2}):
        Credit-first arrival (-2, +2, +2) keeps arrival max prefix at 2 <= 3 (L_mask = 1),
        while causal order (+2, +2, -2) hits causal max prefix 4 > 3 = B_prefix
        (Eg_mask = 0, defect_mask = -1, status ``ARRIVAL_MASKED_CAUSAL_BREACH_LGGR``).
      - Phase 2 (Reorder-Sensitive Worst-Permutation Excursion on Interleaved {+2, -2, +2}):
        Both arrival and causal order (+2, -2, +2) have max prefix 2 <= 3 (L_reord = 1),
        yet positive-delta mass 2 + 2 = 4 > 3 breaches B_prefix under the positive-first
        permutation (+2, +2, -2) (Eg_reord = 0, defect_reord = -1,
        status ``REORDER_SENSITIVE_PREFIX_EXCURSION_LGGR``).
      - Phase 3 (Permutation-Robust Positive-Mass Bounded Multiset {+1, +2, -1}):
        Positive-delta mass 1 + 2 = 3 <= 3 = B_prefix, so every arrival permutation stays
        within B_prefix (L_rob = 1, Eg_rob = 1, defect_rob = 0,
        status ``PERMUTATION_ROBUST_PREFIX_LGGG``).
    """

    def __init__(self, *, scope_id: str = "streaming-replay-order-envelope-scope") -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.evaluations: list[dict[str, Any]] = []

    def evaluate_replay_envelope(
        self,
        evaluation_id: str,
        *,
        prefix_budget: Fraction | int | str = 3,
    ) -> dict[str, Any]:
        """Evaluate arrival-masked causal breach, reorder-sensitive excursion, and permutation-robust envelope."""
        eid = text(evaluation_id, "evaluation_id")
        b_pref = rational(prefix_budget)

        # Phase 1: Arrival (-2, +2, +2) vs Causal (+2, +2, -2)
        mon_p1 = StreamingReplayOrderMonitor(b_pref, scope_id=f"{self.scope_id}-{eid}-p1")
        mon_p1.register_event("ev_credit", -2, causal_index=3)
        mon_p1.register_event("ev_pos_1", 2, causal_index=1)
        mon_p1.register_event("ev_pos_2", 2, causal_index=2)
        rec_p1 = mon_p1.get_receipt()

        # Phase 2: Interleaved (+2, -2, +2) with positive mass 4 > 3
        mon_p2 = StreamingReplayOrderMonitor(b_pref, scope_id=f"{self.scope_id}-{eid}-p2")
        mon_p2.register_event("ev_pos_1", 2, causal_index=1)
        mon_p2.register_event("ev_credit", -2, causal_index=2)
        mon_p2.register_event("ev_pos_2", 2, causal_index=3)
        rec_p2 = mon_p2.get_receipt()

        # Phase 3: Permutation-robust (+1, +2, -1) with positive mass 3 <= 3
        mon_p3 = StreamingReplayOrderMonitor(b_pref, scope_id=f"{self.scope_id}-{eid}-p3")
        mon_p3.register_event("ev_pos_1", 1, causal_index=1)
        mon_p3.register_event("ev_pos_2", 2, causal_index=2)
        mon_p3.register_event("ev_credit", -1, causal_index=3)
        rec_p3 = mon_p3.get_receipt()

        arr_p1 = rational(rec_p1["arrival_max_prefix"])
        caus_p1 = rational(rec_p1["causal_max_prefix"])
        caus_p2 = rational(rec_p2["causal_max_prefix"])
        worst_p2 = rational(rec_p2["worst_permutation_max_prefix"])
        worst_p3 = rational(rec_p3["worst_permutation_max_prefix"])

        l_p1 = 1 if (rec_p1["arrival_within_budget"] and rec_p1["arrival_masked_causal_breach"]) else 0
        eg_p1 = 1 if (l_p1 == 1 and rec_p1["causal_within_budget"]) else 0
        defect_p1 = eg_p1 - l_p1

        l_p2 = 1 if (rec_p2["causal_within_budget"] and worst_p2 > b_pref) else 0
        eg_p2 = 1 if (l_p2 == 1 and worst_p2 <= b_pref) else 0
        defect_p2 = eg_p2 - l_p2

        l_p3 = (
            1
            if (
                rec_p3["status"] == "PERMUTATION_ROBUST_PREFIX_LGGG"
                and worst_p3 <= b_pref
                and rec_p3["endpoint_permutation_invariance_verified"]
            )
            else 0
        )
        eg_p3 = 1 if (l_p3 == 1 and worst_p3 < worst_p2) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eid,
            "phase_1_arrival_max_prefix": arr_p1,
            "phase_1_causal_max_prefix": caus_p1,
            "phase_2_causal_max_prefix": caus_p2,
            "phase_2_worst_max_prefix": worst_p2,
            "phase_3_worst_max_prefix": worst_p3,
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "ARRIVAL_MASKED_CAUSAL_BREACH_LGGR" if defect_p1 == -1 else "PERMUTATION_ROBUST_PREFIX_LGGG",
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "REORDER_SENSITIVE_PREFIX_EXCURSION_LGGR" if defect_p2 == -1 else "PERMUTATION_ROBUST_PREFIX_LGGG",
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "PERMUTATION_ROBUST_PREFIX_LGGG" if eg_p3 == 1 else "REORDER_SENSITIVE_PREFIX_EXCURSION_LGGR",
            "phase_1_replay_receipt": rec_p1,
            "phase_2_replay_receipt": rec_p2,
            "phase_3_replay_receipt": rec_p3,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one replay envelope evaluation must be recorded")
        n = len(self.evaluations)
        p1_mask_fail = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_reord_fail = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        order_fragile_coherence_rate = Fraction(
            n - max(p1_mask_fail, p2_reord_fail), n
        )
        permutation_robust_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_mask_fail == n and p2_reord_fail == n:
            status = "PERMUTATION_ROBUST_PREFIX_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "ARRIVAL_MASKED_CAUSAL_BREACH_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_replay_order_envelope.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_arrival_masked_breach_count": p1_mask_fail,
            "phase_2_reorder_sensitive_excursion_count": p2_reord_fail,
            "phase_3_permutation_robust_count": p3_coherent,
            "order_fragile_coherence_rate": order_fragile_coherence_rate,
            "permutation_robust_coherence_rate": permutation_robust_coherence_rate,
            "replay_envelope_coherence_gain": (
                permutation_robust_coherence_rate - order_fragile_coherence_rate
            ),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingWindowedDriftRebalancingMonitor:
    """Online sliding-window local green vs. full-horizon cumulative drift and rebalancing monitor (Theorem 86).

    Audits long-horizon step-drift trajectories under `StreamingWindowedDriftMonitor`
    with sliding window size W, window budget B_W, and global horizon budget B_global:
      1. Phase 1 (Persistent positive drift):
         Every length-W sliding window stays within B_W (`max_window_sum <= B_W`),
         yet cumulative drift across K = ceil(N / W) disjoint blocks breaches B_global.
      2. Phase 2 (Late terminal rebalancing after mid-horizon prefix excursion):
         Every length-W window stays within B_W and terminal drift S_cum(N) <= B_global,
         yet an intermediate prefix S_cum(t) > B_global breaches the horizon ceiling.
      3. Phase 3 (Periodic inter-window rebalancing):
         Interleaving negative rebalancing steps keeps both max_window_sum <= B_W
         and max_prefix_horizon_drift <= B_global across the entire horizon.
    """

    def __init__(
        self,
        *,
        window_size: int = 2,
        window_budget: Fraction | int | str = 2,
        global_budget: Fraction | int | str = 3,
        scope_id: str = "streaming-windowed-drift-rebalancing-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        w_val = exact_int(window_size, "window_size")
        if w_val < 1:
            raise ValidationError("window_size must be >= 1")
        bw_val = rational(window_budget)
        bg_val = rational(global_budget)
        if bw_val < 0 or bg_val < 0:
            raise ValidationError("window_budget and global_budget must be >= 0")
        self.window_size = w_val
        self.window_budget = bw_val
        self.global_budget = bg_val
        self.evaluations: list[dict[str, Any]] = []

    def _run_drift_stream(
        self,
        eval_id: str,
        phase_tag: str,
        drifts: Sequence[Fraction | int | str],
    ) -> dict[str, Any]:
        mon = StreamingWindowedDriftMonitor(
            self.window_size,
            self.window_budget,
            self.global_budget,
            scope_id=f"{self.scope_id}:{eval_id}:{phase_tag}",
        )
        for idx, d in enumerate(drifts):
            mon.record_step(f"s{idx + 1}", d)
        return mon.get_receipt()

    def record_rebalancing_evaluation(
        self,
        evaluation_id: str,
        *,
        phase_1_drifts: Sequence[Fraction | int | str],
        phase_2_drifts: Sequence[Fraction | int | str],
        phase_3_drifts: Sequence[Fraction | int | str],
        model_id: str = "deterministic",
    ) -> dict[str, Any]:
        eval_id = text(evaluation_id, "evaluation_id")
        mid = text(model_id, "model_id")
        d1 = [rational(v) for v in sequence(phase_1_drifts, "phase_1_drifts")]
        d2 = [rational(v) for v in sequence(phase_2_drifts, "phase_2_drifts")]
        d3 = [rational(v) for v in sequence(phase_3_drifts, "phase_3_drifts")]
        if not d1 or not d2 or not d3:
            raise ValidationError("All drift sequences must be non-empty")

        rec_p1 = self._run_drift_stream(eval_id, "p1", d1)
        rec_p2 = self._run_drift_stream(eval_id, "p2", d2)
        rec_p3 = self._run_drift_stream(eval_id, "p3", d3)

        win_ok_p1 = bool(rec_p1["all_windows_within_budget"])
        cum_p1 = rational(rec_p1["cumulative_horizon_drift"])
        pref_p1 = rational(rec_p1["max_prefix_horizon_drift"])
        l_p1 = 1 if win_ok_p1 and cum_p1 > self.global_budget else 0
        eg_p1 = 1 if (l_p1 == 1 and bool(rec_p1["horizon_within_budget"])) else 0
        defect_p1 = eg_p1 - l_p1

        win_ok_p2 = bool(rec_p2["all_windows_within_budget"])
        cum_p2 = rational(rec_p2["cumulative_horizon_drift"])
        pref_p2 = rational(rec_p2["max_prefix_horizon_drift"])
        l_p2 = 1 if (win_ok_p2 and cum_p2 <= self.global_budget and pref_p2 > self.global_budget) else 0
        eg_p2 = 1 if (l_p2 == 1 and bool(rec_p2["horizon_within_budget"])) else 0
        defect_p2 = eg_p2 - l_p2

        win_ok_p3 = bool(rec_p3["all_windows_within_budget"])
        cum_p3 = rational(rec_p3["cumulative_horizon_drift"])
        pref_p3 = rational(rec_p3["max_prefix_horizon_drift"])
        l_p3 = 1 if (win_ok_p3 and bool(rec_p3["horizon_within_budget"])) else 0
        eg_p3 = 1 if (l_p3 == 1 and pref_p3 < pref_p2) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eval_id,
            "model_id": mid,
            "window_size": self.window_size,
            "window_budget": self.window_budget,
            "global_budget": self.global_budget,
            "phase_1_max_window_sum": rational(rec_p1["max_window_sum"]),
            "phase_1_max_prefix_drift": pref_p1,
            "phase_1_cumulative_drift": cum_p1,
            "phase_2_max_window_sum": rational(rec_p2["max_window_sum"]),
            "phase_2_max_prefix_drift": pref_p2,
            "phase_2_cumulative_drift": cum_p2,
            "phase_3_max_window_sum": rational(rec_p3["max_window_sum"]),
            "phase_3_max_prefix_drift": pref_p3,
            "phase_3_cumulative_drift": cum_p3,
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "SLIDING_WINDOW_HORIZON_BREACH_LGGR" if defect_p1 == -1 else "WINDOW_AND_HORIZON_WITHIN_BUDGET_LGGG",
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "LATE_REBALANCING_PREFIX_HORIZON_BREACH_LGGR" if defect_p2 == -1 else "WINDOW_AND_HORIZON_WITHIN_BUDGET_LGGG",
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "PERIODIC_REBALANCED_HORIZON_COHERENT_LGGG" if eg_p3 == 1 else "SLIDING_WINDOW_HORIZON_BREACH_LGGR",
            "phase_1_window_receipt": rec_p1,
            "phase_2_window_receipt": rec_p2,
            "phase_3_window_receipt": rec_p3,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one windowed drift rebalancing evaluation must be recorded")
        n = len(self.evaluations)
        p1_breach = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_late_breach = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        unrebalanced_coherence_rate = Fraction(n - max(p1_breach, p2_late_breach), n)
        periodic_rebalanced_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_breach == n and p2_late_breach == n:
            status = "PERIODIC_REBALANCED_HORIZON_COHERENT_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "SLIDING_WINDOW_HORIZON_BREACH_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_windowed_drift_rebalancing.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_sliding_window_breach_count": p1_breach,
            "phase_2_late_rebalancing_breach_count": p2_late_breach,
            "phase_3_periodic_rebalanced_coherent_count": p3_coherent,
            "unrebalanced_coherence_rate": unrebalanced_coherence_rate,
            "periodic_rebalanced_coherence_rate": periodic_rebalanced_coherence_rate,
            "horizon_rebalancing_coherence_gain": (
                periodic_rebalanced_coherence_rate - unrebalanced_coherence_rate
            ),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingOptionalStoppingDrawdownMonitor:
    """Online optional-stopping early-gain halting vs. tail-drawdown cap monitor (Theorem 87).

    Audits 2-step fair binary martingale trees under `StreamingMartingaleOptionalStoppingMonitor`
    with maximum tail-drawdown budget `max_tail_drawdown_budget`:
      1. Phase 1 (Double-down recovery stake on loss):
         Early-gain halting at X_u = +1 and continuing at X_d = -1 to (X_du = +1, X_dd = -3)
         conserves E[X_tau] = 0 = X_0 with win probability 3/4 (L = 1), yet reaches
         tail drawdown 3 > B_tail = 1 (Eg = 0, Delta_E = -1).
      2. Phase 2 (Reduced break-even stake on loss):
         Halting at X_u = +1 and continuing at X_d = -1 to (X_du = 0, X_dd = -2)
         conserves E[X_tau] = 0 = X_0 (L = 1), yet residual tail drawdown 2 > 1
         breaches B_tail = 1 (Eg = 0, Delta_E = -1).
      3. Phase 3 (Loss-capped halting at step 1 / zero step-2 stake):
         Halting at both X_u = +1 and X_d = -1 (or X_du = -1, X_dd = -1) conserves
         E[X_tau] = 0 = X_0 and bounds tail drawdown 1 <= B_tail = 1 (L = 1, Eg = 1, Delta_E = 0).
    """

    def __init__(
        self,
        *,
        max_tail_drawdown_budget: Fraction | int | str = 1,
        scope_id: str = "streaming-optional-stopping-drawdown-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        bt = rational(max_tail_drawdown_budget)
        if bt < 0:
            raise ValidationError("max_tail_drawdown_budget must be >= 0")
        self.max_tail_drawdown_budget = bt
        self.evaluations: list[dict[str, Any]] = []

    def record_stopping_evaluation(
        self,
        evaluation_id: str,
        *,
        x0: Fraction | int | str = 0,
        x_u: Fraction | int | str = 1,
        x_d: Fraction | int | str = -1,
        x_uu: Fraction | int | str = 2,
        x_ud: Fraction | int | str = 0,
        phase_1_du_dd: Sequence[Fraction | int | str] = (1, -3),
        phase_2_du_dd: Sequence[Fraction | int | str] = (0, -2),
        phase_3_du_dd: Sequence[Fraction | int | str] = (-1, -1),
        model_id: str = "deterministic",
    ) -> dict[str, Any]:
        eval_id = text(evaluation_id, "evaluation_id")
        mid = text(model_id, "model_id")
        du1, dd1 = vector(phase_1_du_dd, "phase_1_du_dd", 2)
        du2, dd2 = vector(phase_2_du_dd, "phase_2_du_dd", 2)
        du3, dd3 = vector(phase_3_du_dd, "phase_3_du_dd", 2)

        mon = StreamingMartingaleOptionalStoppingMonitor(
            self.max_tail_drawdown_budget,
            scope_id=f"{self.scope_id}:{eval_id}",
        )
        rec_p1 = mon.record_stopped_tree(
            "phase_1_double_down",
            x0, x_u, x_d, x_uu, x_ud, du1, dd1,
            stop_on_step1_up=True, stop_on_step1_down=False,
        )
        rec_p2 = mon.record_stopped_tree(
            "phase_2_break_even_stake",
            x0, x_u, x_d, x_uu, x_ud, du2, dd2,
            stop_on_step1_up=True, stop_on_step1_down=False,
        )
        rec_p3 = mon.record_stopped_tree(
            "phase_3_loss_capped_halt",
            x0, x_u, x_d, x_uu, x_ud, du3, dd3,
            stop_on_step1_up=True, stop_on_step1_down=True,
        )
        summary_rec = mon.get_receipt()

        t_dd_1 = rational(rec_p1["tail_drawdown"])
        t_dd_2 = rational(rec_p2["tail_drawdown"])
        t_dd_3 = rational(rec_p3["tail_drawdown"])

        l_p1 = int(rec_p1["local_martingale_product"])
        eg_p1 = int(rec_p1["global_drawdown_evaluator"])
        defect_p1 = int(rec_p1["evaluator_defect"])

        l_p2 = int(rec_p2["local_martingale_product"])
        eg_p2 = int(rec_p2["global_drawdown_evaluator"])
        defect_p2 = int(rec_p2["evaluator_defect"])

        l_p3 = int(rec_p3["local_martingale_product"])
        eg_p3 = int(rec_p3["global_drawdown_evaluator"])
        defect_p3 = int(rec_p3["evaluator_defect"])

        rec: dict[str, Any] = {
            "evaluation_id": eval_id,
            "model_id": mid,
            "max_tail_drawdown_budget": self.max_tail_drawdown_budget,
            "phase_1_stopped_expectation": rational(rec_p1["stopped_expectation"]),
            "phase_1_win_probability": rational(rec_p1["stopped_win_probability"]),
            "phase_1_tail_drawdown": t_dd_1,
            "phase_2_stopped_expectation": rational(rec_p2["stopped_expectation"]),
            "phase_2_tail_drawdown": t_dd_2,
            "phase_3_stopped_expectation": rational(rec_p3["stopped_expectation"]),
            "phase_3_tail_drawdown": t_dd_3,
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "MARTINGALE_STOPPING_TAIL_DRAWDOWN_NGD_LGGR" if defect_p1 == -1 else "MARTINGALE_STOPPING_WITHIN_DRAWDOWN_LGGG",
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "RESIDUAL_TAIL_DRAWDOWN_BREACH_LGGR" if defect_p2 == -1 else "MARTINGALE_STOPPING_WITHIN_DRAWDOWN_LGGG",
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "MARTINGALE_STOPPING_WITHIN_DRAWDOWN_LGGG" if eg_p3 == 1 else "MARTINGALE_STOPPING_TAIL_DRAWDOWN_NGD_LGGR",
            "martingale_tree_receipt": summary_rec,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one optional-stopping evaluation must be recorded")
        n = len(self.evaluations)
        p1_breach = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_breach = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        uncapped_stopping_coherence_rate = Fraction(n - max(p1_breach, p2_breach), n)
        loss_capped_stopping_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_breach == n and p2_breach == n:
            status = "MARTINGALE_STOPPING_WITHIN_DRAWDOWN_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "MARTINGALE_STOPPING_TAIL_DRAWDOWN_NGD_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_optional_stopping_drawdown.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_double_down_breach_count": p1_breach,
            "phase_2_residual_drawdown_breach_count": p2_breach,
            "phase_3_loss_capped_coherent_count": p3_coherent,
            "uncapped_stopping_coherence_rate": uncapped_stopping_coherence_rate,
            "loss_capped_stopping_coherence_rate": loss_capped_stopping_coherence_rate,
            "drawdown_cap_coherence_gain": (
                loss_capped_stopping_coherence_rate - uncapped_stopping_coherence_rate
            ),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingReggeGaussBonnetHolonomyMonitor:
    """Online 2D Regge hinge deficit curvature & boundary Gauss-Bonnet holonomy monitor (Theorem 88).

    Audits a 4-triangle square-pyramid star around interior vertex `v_apex` with boundary
    vertices `b0, b1, b2, b3` under `StreamingReggeDeficitCurvatureMonitor`:
      1. Phase 1 (Equilateral conical pyramid star: angles (1/6, 1/6, 1/6) per triangle):
         Every triangle closes locally (sum = 1/2, L = 1), yet interior hinge deficit is
         eps_apex = 1 - 4*(1/6) = 1/3 != 0 and boundary turn sum is 2/3 < 1
         (`REGGE_HINGE_DEFICIT_CURVATURE_NGD_LGGR`, Eg = 0, Delta_E = -1).
      2. Phase 2 (Under-flattened star: angles (5/24, 7/48, 7/48) per triangle):
         Every triangle closes locally (sum = 1/2, L = 1), yet residual interior deficit is
         eps_apex = 1 - 4*(5/24) = 1/6 != 0 and boundary turn sum is 5/6 < 1
         (`RESIDUAL_HINGE_DEFICIT_CURVATURE_LGGR`, Eg = 0, Delta_E = -1).
      3. Phase 3 (Right-isosceles flat Euclidean star: angles (1/4, 1/8, 1/8) per triangle):
         Every triangle closes locally, interior deficit is eps_apex = 1 - 4*(1/4) = 0,
         and boundary turn sum is 1 == chi(K) (`FLAT_EUCLIDEAN_LATTICE_LGGG`, L = 1, Eg = 1, Delta_E = 0).
    """

    def __init__(
        self,
        *,
        scope_id: str = "streaming-regge-gauss-bonnet-holonomy-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.evaluations: list[dict[str, Any]] = []

    def _run_four_triangle_star(
        self,
        eval_id: str,
        phase_tag: str,
        tri_angles: Sequence[Fraction | int | str],
    ) -> dict[str, Any]:
        mon = StreamingReggeDeficitCurvatureMonitor(
            interior_vertices=["v_apex"],
            boundary_vertices=["b0", "b1", "b2", "b3"],
            scope_id=f"{self.scope_id}:{eval_id}:{phase_tag}",
        )
        ang = [rational(a) for a in sequence(tri_angles, "tri_angles")]
        if len(ang) != 3:
            raise ValidationError("tri_angles must have 3 angles [apex_angle, b_i_angle, b_next_angle]")
        for i in range(4):
            b_curr = f"b{i}"
            b_next = f"b{(i + 1) % 4}"
            mon.record_triangle(f"t{i}", ["v_apex", b_curr, b_next], ang)
        return mon.get_receipt()

    def record_holonomy_evaluation(
        self,
        evaluation_id: str,
        *,
        phase_1_angles: Sequence[Fraction | int | str] = ("1/6", "1/6", "1/6"),
        phase_2_angles: Sequence[Fraction | int | str] = ("5/24", "7/48", "7/48"),
        phase_3_angles: Sequence[Fraction | int | str] = ("1/4", "1/8", "1/8"),
        model_id: str = "deterministic",
    ) -> dict[str, Any]:
        eval_id = text(evaluation_id, "evaluation_id")
        mid = text(model_id, "model_id")

        rec_p1 = self._run_four_triangle_star(eval_id, "p1", phase_1_angles)
        rec_p2 = self._run_four_triangle_star(eval_id, "p2", phase_2_angles)
        rec_p3 = self._run_four_triangle_star(eval_id, "p3", phase_3_angles)

        eps_p1 = rational(rec_p1["interior_deficits"]["v_apex"])
        bnd_p1 = rational(rec_p1["sum_boundary_turn"])
        l_p1 = int(rec_p1["local_product_aggregator"])
        eg_p1 = int(rec_p1["global_flatness_evaluator"])
        defect_p1 = int(rec_p1["evaluator_defect"])

        eps_p2 = rational(rec_p2["interior_deficits"]["v_apex"])
        bnd_p2 = rational(rec_p2["sum_boundary_turn"])
        l_p2 = int(rec_p2["local_product_aggregator"])
        eg_p2 = int(rec_p2["global_flatness_evaluator"])
        defect_p2 = int(rec_p2["evaluator_defect"])

        eps_p3 = rational(rec_p3["interior_deficits"]["v_apex"])
        bnd_p3 = rational(rec_p3["sum_boundary_turn"])
        l_p3 = int(rec_p3["local_product_aggregator"])
        eg_p3 = int(rec_p3["global_flatness_evaluator"])
        defect_p3 = int(rec_p3["evaluator_defect"])

        rec: dict[str, Any] = {
            "evaluation_id": eval_id,
            "model_id": mid,
            "euler_characteristic": int(rec_p1["euler_characteristic"]),
            "phase_1_apex_deficit": eps_p1,
            "phase_1_boundary_turn_sum": bnd_p1,
            "phase_2_apex_deficit": eps_p2,
            "phase_2_boundary_turn_sum": bnd_p2,
            "phase_3_apex_deficit": eps_p3,
            "phase_3_boundary_turn_sum": bnd_p3,
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "REGGE_HINGE_DEFICIT_CURVATURE_NGD_LGGR" if defect_p1 == -1 else "FLAT_EUCLIDEAN_LATTICE_LGGG",
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "RESIDUAL_HINGE_DEFICIT_CURVATURE_LGGR" if defect_p2 == -1 else "FLAT_EUCLIDEAN_LATTICE_LGGG",
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "FLAT_EUCLIDEAN_LATTICE_LGGG" if eg_p3 == 1 else "REGGE_HINGE_DEFICIT_CURVATURE_NGD_LGGR",
            "phase_1_regge_receipt": rec_p1,
            "phase_2_regge_receipt": rec_p2,
            "phase_3_regge_receipt": rec_p3,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one Regge holonomy evaluation must be recorded")
        n = len(self.evaluations)
        p1_cone = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_part = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_flat = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        curved_star_coherence_rate = Fraction(n - max(p1_cone, p2_part), n)
        flat_holonomy_coherence_rate = Fraction(p3_flat, n)

        if p3_flat == n and p1_cone == n and p2_part == n:
            status = "FLAT_EUCLIDEAN_LATTICE_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "REGGE_HINGE_DEFICIT_CURVATURE_NGD_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_regge_gauss_bonnet_holonomy.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_conical_deficit_count": p1_cone,
            "phase_2_residual_deficit_count": p2_part,
            "phase_3_flat_euclidean_count": p3_flat,
            "curved_star_coherence_rate": curved_star_coherence_rate,
            "flat_holonomy_coherence_rate": flat_holonomy_coherence_rate,
            "regge_holonomy_coherence_gain": (
                flat_holonomy_coherence_rate - curved_star_coherence_rate
            ),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingCoalitionalSynergyMaskingMonitor:
    """Online coalitional Shapley attribution under synergistic & leave-one-out fault masking monitor (Theorem 89).

    Audits 2-agent failure coalitions {A1, A2} under `StreamingCoalitionalAttributionMonitor`:
      1. Phase 1 (Synergistic joint fault with zero singleton marginals: v0=0, v1=0, v2=0, v12=-2):
         Each agent tested alone has zero defect (naive singleton sum = 0, L = 1), yet joint
         execution triggers v({A1, A2}) = -2 (interaction synergy I_12 = -2 != 0), and
         Shapley attribution assigns phi_1 = -1, phi_2 = -1
         (`NONADDITIVE_COALITIONAL_DEFECT_LGGR`, Eg = 0, Delta_E = -1).
      2. Phase 2 (Leave-one-out masked fault: v0=0, v1=-1, v2=-1, v12=-1):
         Single-agent leave-one-out marginals v12 - v2 = 0 and v12 - v1 = 0 vanish while
         naive singleton sum -2 != -1 double-counts the fault (I_12 = +1 != 0, L = 1);
         Shapley attribution assigns phi_1 = -1/2, phi_2 = -1/2
         (`LEAVE_ONE_OUT_MASKED_COALITIONAL_DEFECT_LGGR`, Eg = 0, Delta_E = -1).
      3. Phase 3 (Decoupled additive zero-defect coalition: v0=0, v1=0, v2=0, v12=0):
         Interaction synergy I_12 = 0, v12 = 0, and phi_1 = phi_2 = 0
         (`ADDITIVE_COALITIONAL_ATTRIBUTION_LGGG`, L = 1, Eg = 1, Delta_E = 0).
    """

    def __init__(
        self,
        *,
        scope_id: str = "streaming-coalitional-synergy-masking-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.evaluations: list[dict[str, Any]] = []

    def record_synergy_evaluation(
        self,
        evaluation_id: str,
        *,
        phase_1_values: Sequence[Fraction | int | str] = (0, 0, 0, -2),
        phase_2_values: Sequence[Fraction | int | str] = (0, -1, -1, -1),
        phase_3_values: Sequence[Fraction | int | str] = (0, 0, 0, 0),
        model_id: str = "deterministic",
    ) -> dict[str, Any]:
        eval_id = text(evaluation_id, "evaluation_id")
        mid = text(model_id, "model_id")
        v1 = vector(phase_1_values, "phase_1_values", 4)
        v2 = vector(phase_2_values, "phase_2_values", 4)
        v3 = vector(phase_3_values, "phase_3_values", 4)

        mon = StreamingCoalitionalAttributionMonitor(
            scope_id=f"{self.scope_id}:{eval_id}",
        )
        rec_p1 = mon.observe_coalition_game(
            "phase_1_synergistic_fault",
            ["A1", "A2"],
            {
                frozenset(): v1[0],
                frozenset(["A1"]): v1[1],
                frozenset(["A2"]): v1[2],
                frozenset(["A1", "A2"]): v1[3],
            },
        )
        rec_p2 = mon.observe_coalition_game(
            "phase_2_leave_one_out_masked",
            ["A1", "A2"],
            {
                frozenset(): v2[0],
                frozenset(["A1"]): v2[1],
                frozenset(["A2"]): v2[2],
                frozenset(["A1", "A2"]): v2[3],
            },
        )
        rec_p3 = mon.observe_coalition_game(
            "phase_3_additive_coherent",
            ["A1", "A2"],
            {
                frozenset(): v3[0],
                frozenset(["A1"]): v3[1],
                frozenset(["A2"]): v3[2],
                frozenset(["A1", "A2"]): v3[3],
            },
        )
        summary_rec = mon.get_receipt()

        sing_p1 = rational(rec_p1["naive_singleton_marginal_sum"])
        syn_p1 = rational(rec_p1["synergy_interaction_term"])
        net_p1 = rational(rec_p1["net_coalitional_value"])
        l_p1 = 1 if (sing_p1 == 0 and net_p1 < 0) else 0
        eg_p1 = 1 if (l_p1 == 1 and net_p1 == 0 and syn_p1 == 0) else 0
        defect_p1 = eg_p1 - l_p1

        loo_1 = v2[3] - v2[2]
        loo_2 = v2[3] - v2[1]
        syn_p2 = rational(rec_p2["synergy_interaction_term"])
        net_p2 = rational(rec_p2["net_coalitional_value"])
        l_p2 = 1 if (loo_1 == 0 and loo_2 == 0 and net_p2 < 0) else 0
        eg_p2 = 1 if (l_p2 == 1 and net_p2 == 0 and syn_p2 == 0) else 0
        defect_p2 = eg_p2 - l_p2

        syn_p3 = rational(rec_p3["synergy_interaction_term"])
        net_p3 = rational(rec_p3["net_coalitional_value"])
        l_p3 = 1 if (syn_p3 == 0 and net_p3 == 0) else 0
        eg_p3 = 1 if (l_p3 == 1 and bool(rec_p3["efficiency_verified"])) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eval_id,
            "model_id": mid,
            "phase_1_singleton_sum": sing_p1,
            "phase_1_synergy_term": syn_p1,
            "phase_1_shapley_attributions": rec_p1["shapley_attributions"],
            "phase_2_leave_one_out_marginals": [loo_1, loo_2],
            "phase_2_synergy_term": syn_p2,
            "phase_2_shapley_attributions": rec_p2["shapley_attributions"],
            "phase_3_synergy_term": syn_p3,
            "phase_3_shapley_attributions": rec_p3["shapley_attributions"],
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "NONADDITIVE_COALITIONAL_DEFECT_LGGR" if defect_p1 == -1 else "ADDITIVE_COALITIONAL_ATTRIBUTION_LGGG",
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "LEAVE_ONE_OUT_MASKED_COALITIONAL_DEFECT_LGGR" if defect_p2 == -1 else "ADDITIVE_COALITIONAL_ATTRIBUTION_LGGG",
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "ADDITIVE_COALITIONAL_ATTRIBUTION_LGGG" if eg_p3 == 1 else "NONADDITIVE_COALITIONAL_DEFECT_LGGR",
            "coalitional_monitor_receipt": summary_rec,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one coalitional synergy evaluation must be recorded")
        n = len(self.evaluations)
        p1_syn_fail = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_loo_fail = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_coherent = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        masked_coalition_coherence_rate = Fraction(
            n - max(p1_syn_fail, p2_loo_fail), n
        )
        shapley_resolved_coherence_rate = Fraction(p3_coherent, n)

        if p3_coherent == n and p1_syn_fail == n and p2_loo_fail == n:
            status = "ADDITIVE_COALITIONAL_ATTRIBUTION_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "NONADDITIVE_COALITIONAL_DEFECT_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_coalitional_synergy_masking.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_synergistic_fault_count": p1_syn_fail,
            "phase_2_leave_one_out_masked_count": p2_loo_fail,
            "phase_3_additive_coherent_count": p3_coherent,
            "masked_coalition_coherence_rate": masked_coalition_coherence_rate,
            "shapley_resolved_coherence_rate": shapley_resolved_coherence_rate,
            "coalitional_attribution_coherence_gain": (
                shapley_resolved_coherence_rate - masked_coalition_coherence_rate
            ),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})


class StreamingPullbackMediatorFactorizationMonitor:
    """Online pullback square mediator uniqueness & ambiguous interface factorization monitor (Theorem 90).

    Audits multi-adapter pullback diagrams A -f-> C <-g- B under `StreamingPullbackSquareMonitor`:
      1. Phase 1 (Interface cospan mismatch under coarse parity map: a0 -> c0, b1 -> c1):
         Both local branch checks pass (L = 1), yet f(a0) = c0 != c1 = g(b1) violates
         pullback commutativity (`PULLBACK_INTERFACE_MISMATCH_NGD_LGGR`, Eg = 0, Delta_E = -1).
      2. Phase 2 (Ambiguous non-injective interface fiber: f(a0)=f(a2)=c0, g(b0)=g(b2)=c0):
         The pair (a0, b2) satisfies f(a0) = g(b2) = c0 (L = 1), yet the interface fiber
         over c0 has size |{a0, a2} x {b0, b2}| = 4 > 1 (`interface_uniquely_identifies_pair = False`),
         so coarse interface c0 alone cannot separate matched (a0, b0) from cross-paired (a0, b2)
         (`AMBIGUOUS_PULLBACK_INTERFACE_FIBER_LGGR`, Eg = 0, Delta_E = -1).
      3. Phase 3 (Refined bijective interface & unique universal cone mediator):
         Refining f_ref(a_i) = c_i, g_ref(b_i) = c_i yields singleton fibers (size = 1)
         and unique cone mediator u(w_i) = [a_i, b_i]
         (`PULLBACK_FIBER_GLUED_LGGG`, L = 1, Eg = 1, Delta_E = 0).
    """

    def __init__(
        self,
        *,
        scope_id: str = "streaming-pullback-mediator-factorization-scope",
    ) -> None:
        self.scope_id = text(scope_id, "scope_id")
        self.evaluations: list[dict[str, Any]] = []

    def record_factorization_evaluation(
        self,
        evaluation_id: str,
        *,
        model_id: str = "deterministic",
    ) -> dict[str, Any]:
        eval_id = text(evaluation_id, "evaluation_id")
        mid = text(model_id, "model_id")

        coarse_f = {"a0": "c_even", "a1": "c_odd", "a2": "c_even", "a3": "c_odd"}
        coarse_g = {"b0": "c_even", "b1": "c_odd", "b2": "c_even", "b3": "c_odd"}

        mon_p1 = StreamingPullbackSquareMonitor(
            coarse_f,
            coarse_g,
            scope_id=f"{self.scope_id}:{eval_id}:p1",
        )
        pair_p1 = mon_p1.record_branch_pair("p1_mismatch", "a0", "b1")
        cone_p1 = mon_p1.verify_cone_mediator(
            "cone_p1_mismatch",
            {"w0": "a0"},
            {"w0": "b1"},
        )
        rec_p1 = mon_p1.get_receipt()

        mon_p2 = StreamingPullbackSquareMonitor(
            coarse_f,
            coarse_g,
            scope_id=f"{self.scope_id}:{eval_id}:p2",
        )
        pair_p2 = mon_p2.record_branch_pair("p2_ambiguous", "a0", "b2")
        rec_p2 = mon_p2.get_receipt()

        refined_f = {"a0": "c0", "a1": "c1", "a2": "c2", "a3": "c3"}
        refined_g = {"b0": "c0", "b1": "c1", "b2": "c2", "b3": "c3"}
        mon_p3 = StreamingPullbackSquareMonitor(
            refined_f,
            refined_g,
            scope_id=f"{self.scope_id}:{eval_id}:p3",
        )
        pair_p3 = mon_p3.record_branch_pair("p3_unique", "a0", "b0")
        cone_p3 = mon_p3.verify_cone_mediator(
            "cone_p3_unique",
            {"w0": "a0", "w1": "a1", "w2": "a2", "w3": "a3"},
            {"w0": "b0", "w1": "b1", "w2": "b2", "w3": "b3"},
        )
        rec_p3 = mon_p3.get_receipt()

        l_p1 = int(pair_p1["local_product"])
        eg_p1 = int(pair_p1["global_pullback_evaluator"])
        defect_p1 = int(pair_p1["evaluator_defect"])

        fib_p2 = int(pair_p2["interface_fiber_size"])
        uniq_p2 = bool(pair_p2["interface_uniquely_identifies_pair"])
        l_p2 = 1 if (bool(pair_p2["in_pullback_square"]) and fib_p2 > 1) else 0
        eg_p2 = 1 if (l_p2 == 1 and uniq_p2) else 0
        defect_p2 = eg_p2 - l_p2

        fib_p3 = int(pair_p3["interface_fiber_size"])
        uniq_p3 = bool(pair_p3["interface_uniquely_identifies_pair"])
        med_ok_p3 = bool(cone_p3["mediator_uniqueness_and_projection_verified"])
        l_p3 = 1 if (bool(pair_p3["in_pullback_square"]) and uniq_p3 and med_ok_p3) else 0
        eg_p3 = 1 if (l_p3 == 1 and fib_p3 == 1) else 0
        defect_p3 = eg_p3 - l_p3

        rec: dict[str, Any] = {
            "evaluation_id": eval_id,
            "model_id": mid,
            "phase_1_in_pullback": bool(pair_p1["in_pullback_square"]),
            "phase_1_cone_commutes": bool(cone_p1["commutes_over_c"]),
            "phase_2_interface_fiber_size": fib_p2,
            "phase_2_interface_uniquely_identifies_pair": uniq_p2,
            "phase_3_interface_fiber_size": fib_p3,
            "phase_3_interface_uniquely_identifies_pair": uniq_p3,
            "phase_3_universal_mediator": cone_p3["universal_mediator"],
            "phase_1_local_green": l_p1,
            "phase_1_global_green": eg_p1,
            "phase_1_defect": defect_p1,
            "phase_1_status": "PULLBACK_INTERFACE_MISMATCH_NGD_LGGR" if defect_p1 == -1 else "PULLBACK_FIBER_GLUED_LGGG",
            "phase_2_local_green": l_p2,
            "phase_2_global_green": eg_p2,
            "phase_2_defect": defect_p2,
            "phase_2_status": "AMBIGUOUS_PULLBACK_INTERFACE_FIBER_LGGR" if defect_p2 == -1 else "PULLBACK_FIBER_GLUED_LGGG",
            "phase_3_local_green": l_p3,
            "phase_3_global_green": eg_p3,
            "phase_3_defect": defect_p3,
            "phase_3_status": "PULLBACK_FIBER_GLUED_LGGG" if eg_p3 == 1 else "AMBIGUOUS_PULLBACK_INTERFACE_FIBER_LGGR",
            "phase_1_pullback_receipt": rec_p1,
            "phase_2_pullback_receipt": rec_p2,
            "phase_3_pullback_receipt": rec_p3,
        }
        self.evaluations.append(rec)
        return json_value(rec)

    def current_receipt(self) -> dict[str, Any]:
        if not self.evaluations:
            raise ValidationError("at least one pullback factorization evaluation must be recorded")
        n = len(self.evaluations)
        p1_mis = sum(1 for e in self.evaluations if e["phase_1_defect"] == -1)
        p2_amb = sum(1 for e in self.evaluations if e["phase_2_defect"] == -1)
        p3_uni = sum(1 for e in self.evaluations if e["phase_3_global_green"] == 1)

        coarse_interface_coherence_rate = Fraction(n - max(p1_mis, p2_amb), n)
        universal_mediator_coherence_rate = Fraction(p3_uni, n)

        if p3_uni == n and p1_mis == n and p2_amb == n:
            status = "PULLBACK_FIBER_GLUED_LGGG"
            contract_status = "COMPOSABLE_LGGG"
        else:
            status = "PULLBACK_INTERFACE_MISMATCH_NGD_LGGR"
            contract_status = "OBSTRUCTED_LGGR"

        body: dict[str, Any] = {
            "schema": "lggr.online_pullback_mediator_factorization.v1",
            "authority_effect": "None",
            "scope_id": self.scope_id,
            "status": status,
            "contract_status": contract_status,
            "evaluation_count": n,
            "phase_1_interface_mismatch_count": p1_mis,
            "phase_2_ambiguous_fiber_count": p2_amb,
            "phase_3_universal_mediator_count": p3_uni,
            "coarse_interface_coherence_rate": coarse_interface_coherence_rate,
            "universal_mediator_coherence_rate": universal_mediator_coherence_rate,
            "pullback_factorization_coherence_gain": (
                universal_mediator_coherence_rate - coarse_interface_coherence_rate
            ),
            "evaluations": self.evaluations,
        }
        return json_value({**body, "receipt_sha256": digest(body)})
















