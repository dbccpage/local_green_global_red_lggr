"""
Unit tests for LGGR Volume VII (`lggr_vii_core.py`) and its bridge to the root
`lggr` package.
"""

from __future__ import annotations

import pathlib
import sys
import unittest
from fractions import Fraction

CODE_DIR = pathlib.Path(__file__).resolve().parents[1]
REPO_ROOT = CODE_DIR.parents[2]
for p in (str(CODE_DIR), str(REPO_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

import lggr_vii_core as vii  # noqa: E402
from lggr import (  # noqa: E402
    BudgetPolicy,
    StateRef,
    analyze_descent,
    audit_history,
    classify_cochain,
    evaluator_defect,
    make_witness,
    verify_l1_certificate,
    verify_transport,
)


class LggrVIITests(unittest.TestCase):
    def test_observer_minimax_and_evidence_preserving_predictor(self) -> None:
        rows = [
            {"state_id": "h_minus", "report": (Fraction(1, 2), Fraction(1, 2)), "target": -1},
            {"state_id": "h_plus", "report": (Fraction(1, 2), Fraction(1, 2)), "target": 1},
            {"state_id": "h_resolved", "report": (Fraction(1), Fraction(0)), "target": 3},
        ]
        summary = vii.analyze_observer_minimax(rows)
        self.assertFalse(summary["exact_recovery_possible"])
        self.assertEqual(summary["max_fiber_width"], Fraction(2))
        self.assertEqual(summary["minimax_error_floor"], Fraction(1))

        # Midpoint predictor attains the minimax floor 1
        mid_eval = vii.evaluate_evidence_preserving_predictor(
            rows,
            lambda rep: summary["fibers"][rep]["midpoint_prediction"],
        )
        self.assertTrue(mid_eval["respects_minimax_lower_bound"])
        self.assertTrue(mid_eval["attains_minimax_floor"])
        self.assertEqual(mid_eval["max_error"], Fraction(1))

        # Any biased predictor on the unresolved fiber incurs strictly larger error >= 1
        for candidate_val in (-2, -1, 0, 1, 2):
            res = vii.evaluate_evidence_preserving_predictor(
                rows,
                lambda rep, v=candidate_val: v if rep == (Fraction(1, 2), Fraction(1, 2)) else 3,
            )
            self.assertTrue(res["respects_minimax_lower_bound"])
            self.assertGreaterEqual(res["max_error"], Fraction(1))

    def test_symmetric_chsh_and_mermin_families(self) -> None:
        for v in (Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(5, 8), Fraction(3, 4), Fraction(1)):
            chsh = vii.symmetric_family_measures(v, contexts=4)
            mermin = vii.symmetric_family_measures(v, contexts=8)
            self.assertEqual(chsh["cf_minus_two_n_min"], Fraction(0))
            self.assertEqual(mermin["cf_minus_two_n_min"], Fraction(0))
            self.assertEqual(chsh["CF"], Fraction(4) * chsh["R_pi"])
            self.assertEqual(mermin["CF"], Fraction(8) * mermin["R_pi"])

    def test_pstar_no_signalling_and_cf_gt_2n_separation(self) -> None:
        cert = vii.verify_pstar_separation_Summary()
        self.assertTrue(cert["p_star_normalized_and_no_signalling"])
        self.assertTrue(cert["p_star_common_denominator_768"])
        self.assertEqual(cert["CF_p_star"], Fraction(19, 64))
        self.assertEqual(cert["N_min_p_star"], Fraction(25, 256))
        self.assertEqual(cert["CF_minus_2N_p_star"], Fraction(13, 128))
        self.assertTrue(cert["violates_cf_le_2n"])
        self.assertTrue(cert["satisfies_8_context_bound_cf_le_7n"])
        self.assertTrue(cert["order_reversed_vs_Q_5_8"])

    def test_constructive_m_context_packing_bound(self) -> None:
        T = vii.build_three_party_incidence_matrix()
        self.assertEqual(len(T), 64)
        self.assertEqual(len(T[0]), 64)

        # Build the exact signed extension q_v for Mermin Q_{5/8}:
        # q_v(g) = (1 + v * K(g)) / 64 where K(g) in {-2, +2}
        v = Fraction(5, 8)
        assignments = list(vii.itertools.product((0, 1), repeat=6))
        q_mermin = []
        for lam in assignments:
            a0, a1, b0, b1, c0, c1 = [1 if bit == 0 else -1 for bit in lam]
            k_val = -a0 * b0 * c0 + a0 * b1 * c1 + a1 * b0 * c1 + a1 * b1 * c0
            q_mermin.append((Fraction(1) + v * Fraction(k_val)) / Fraction(64))

        res = vii.constructive_cf_from_signed_extension(T, q_mermin)
        self.assertEqual(res["contexts_m"], 8)
        self.assertEqual(res["negative_mass_N"], Fraction(1, 8))
        self.assertTrue(res["gamma_nonnegative"])
        self.assertTrue(res["T_gamma_dominated_by_p"])
        self.assertTrue(res["satisfies_cf_le_m_minus_1_N"])
        self.assertLessEqual(res["cf_upper_bound"], Fraction(7, 8))

    def test_bridge_to_root_lggr_modules(self) -> None:
        # 1. Descent / collision
        rows = [
            {"state_id": "0,1,0", "report": [1, 1], "query": True},
            {"state_id": "0,1,2", "report": [1, 1], "query": False},
        ]
        descent_cert = analyze_descent(rows, scope_id="unsigned-step-reports")
        self.assertEqual(descent_cert["status"], "REPORT_INSUFFICIENT")

        # 2. Evaluator defect
        defect = evaluator_defect(True, True, False)
        self.assertEqual(defect["delta"], -1)
        self.assertEqual(defect["defect_kind"], "NGD")

        # 3. Signed history composition (endpoint vs. every_prefix)
        s0, s1, s2, s3 = StateRef("s0", 0), StateRef("s1", 1), StateRef("s2", 2), StateRef("s3", 1)
        p_end = BudgetPolicy(query_scope="endpoint")
        w01 = make_witness(p_end, s0, s1, witness_id="w01")
        w12 = make_witness(p_end, s1, s2, witness_id="w12")
        w23 = make_witness(p_end, s2, s3, witness_id="w23")
        rec_end = audit_history(p_end, s0, [w01, w12, w23])
        self.assertEqual(rec_end["status"], "COMPOSITION_VERIFIED")
        self.assertFalse(rec_end["arithmetic"]["every_prefix_verdict"])

        # 4. Exact L1 primal/dual triangle certificate and cochain classification
        D0 = [[-1, 1, 0], [0, -1, 1], [-1, 0, 1]]
        l1_rec = verify_l1_certificate(
            D=D0,
            h=[1, 1, 1],
            weights=[1, 1, 1],
            potential=[0, 1, 2],
            dual=[1, 1, -1],
        )
        self.assertEqual(l1_rec["status"], "OPTIMALITY_VERIFIED")
        self.assertEqual(l1_rec["optimum"], "1")

        filled = classify_cochain(D0=D0, h=[1, 1, 1], D1=[[1, 1, -1]])
        self.assertEqual(filled["status"], "CLOSURE_FAILURE")

        budget_exact = classify_cochain(D0=D0, h=[1, 1, 2], D1=[[1, 1, -1]])
        self.assertEqual(budget_exact["status"], "EXACT")

        # 5. Chain retraction reflection
        I3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        trans = verify_transport(D_source=D0, D_target=D0, F0=I3, F1=I3, G0=I3, G1=I3)
        self.assertEqual(trans["status"], "RETRACTION_VERIFIED")
        self.assertTrue(trans["nonrepairability_reflection_verified"])


if __name__ == "__main__":
    unittest.main()
