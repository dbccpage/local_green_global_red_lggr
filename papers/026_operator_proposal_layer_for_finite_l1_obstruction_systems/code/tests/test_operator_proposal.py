"""
test_operator_proposal.py

Unit tests for mod_operator_proposal_core.py validating discrete coboundaries,
cycle-obstruction equivalence, closure defects, piecewise R_cl vs exact R_exact,
tree exactness, general graph primal/dual witnesses, theta-graph secondary tiebreak,
evaluator supremacy, external-Xi trust boundary, and the Guarded Descent Law (Section 6).
"""

from fractions import Fraction
import pytest

try:
    from mod_operator_proposal_core import (
        AdmittedComplex,
        Edge,
        EvaluatorPolicy,
        ExactPrimalDualWitness,
        FiniteGraph,
        GuardedEvaluator,
        ObstructionTuple,
        OperatorProposal,
        StructuralOperatorProposal,
        compute_cycle_defect,
        compute_gamma2_simple,
        compute_phi1_cycle_graph,
        compute_r_cl,
        compute_r_epsilon,
        compute_r_exact,
        discrete_coboundary,
        evaluate_path_acceptance,
        evaluate_tuple_acceptance,
        solve_directed_cycle_witness,
        solve_tree_witness,
        verify_primal_dual_witness,
    )
except ImportError:
    from code.mod_operator_proposal_core import (
        AdmittedComplex,
        Edge,
        EvaluatorPolicy,
        ExactPrimalDualWitness,
        FiniteGraph,
        GuardedEvaluator,
        ObstructionTuple,
        OperatorProposal,
        StructuralOperatorProposal,
        compute_cycle_defect,
        compute_gamma2_simple,
        compute_phi1_cycle_graph,
        compute_r_cl,
        compute_r_epsilon,
        compute_r_exact,
        discrete_coboundary,
        evaluate_path_acceptance,
        evaluate_tuple_acceptance,
        solve_directed_cycle_witness,
        solve_tree_witness,
        verify_primal_dual_witness,
    )


# ---------------------------------------------------------------------------
# Discrete Coboundary & Exactness Tests
# ---------------------------------------------------------------------------

def test_discrete_coboundary_exactness():
    """Verify that a 0-cochain potential induces an exact 1-cochain whose cycle sum vanishes."""
    # Directed cycle C_3: 0 -> 1 -> 2 -> 0
    e01 = Edge(0, 1)
    e12 = Edge(1, 2)
    e20 = Edge(2, 0)
    graph = FiniteGraph(vertices=(0, 1, 2), edges=(e01, e12, e20))

    potential = {0: Fraction(5, 1), 1: Fraction(8, 1), 2: Fraction(2, 1)}
    coboundary = discrete_coboundary(graph, potential)

    # e01: f(1)-f(0) = 8 - 5 = 3
    # e12: f(2)-f(1) = 2 - 8 = -6
    # e20: f(0)-f(2) = 5 - 2 = 3
    assert coboundary == [Fraction(3, 1), Fraction(-6, 1), Fraction(3, 1)]

    # Cycle sum = 3 + (-6) + 3 = 0
    cycle = [(e01, 1), (e12, 1), (e20, 1)]
    field = {e01: coboundary[0], e12: coboundary[1], e20: coboundary[2]}
    defect = compute_cycle_defect(cycle, field)
    assert defect == Fraction(0, 1)


def test_phi1_cycle_graph_obstruction():
    """Verify non-zero obstruction on non-exact edge field on C_3."""
    omega = [Fraction(1, 1), Fraction(0, 1), Fraction(0, 1)]
    phi1 = compute_phi1_cycle_graph(omega)
    assert phi1 == Fraction(1, 1)

    omega_exact = [Fraction(2, 1), Fraction(-1, 1), Fraction(-1, 1)]
    phi1_exact = compute_phi1_cycle_graph(omega_exact)
    assert phi1_exact == Fraction(0, 1)


def test_gamma2_closure_defect():
    """Verify closure defect computation under a 2-cell boundary operator."""
    d1_matrix = [[1, 1, 1]]

    # Case 1: Closed residual [1, -1, 0] -> sum = 0 -> Gamma2 = 0
    h1_closed = [Fraction(1, 1), Fraction(-1, 1), Fraction(0, 1)]
    gamma2_zero = compute_gamma2_simple(d1_matrix, h1_closed)
    assert gamma2_zero == Fraction(0, 1)

    # Case 2: Open residual [1, 1, 0] -> sum = 2 -> Gamma2 = 2
    h1_open = [Fraction(1, 1), Fraction(1, 1), Fraction(0, 1)]
    gamma2_open = compute_gamma2_simple(d1_matrix, h1_open)
    assert gamma2_open == Fraction(2, 1)


def test_gamma2_independent_of_potential():
    """
    Mathematical check: because d_1 o d_0 = 0,
    Gamma_2 = ||d_1(omega - d_0 f)||_1 = ||d_1 omega||_1 for ANY potential f.
    """
    e01 = Edge(0, 1)
    e12 = Edge(1, 2)
    e20 = Edge(2, 0)
    graph = FiniteGraph(vertices=(0, 1, 2), edges=(e01, e12, e20))
    d1_matrix = [[1, 1, 1]]

    omega = [Fraction(3, 1), Fraction(1, 1), Fraction(2, 1)]
    gamma2_omega = compute_gamma2_simple(d1_matrix, omega)

    f1 = {0: Fraction(2, 1), 1: Fraction(5, 1), 2: Fraction(-1, 1)}
    f2 = {0: Fraction(10, 1), 1: Fraction(-4, 1), 2: Fraction(7, 1)}

    d0_f1 = discrete_coboundary(graph, f1)
    d0_f2 = discrete_coboundary(graph, f2)

    h1_1 = [w - d for w, d in zip(omega, d0_f1)]
    h1_2 = [w - d for w, d in zip(omega, d0_f2)]

    gamma2_h1_1 = compute_gamma2_simple(d1_matrix, h1_1)
    gamma2_h1_2 = compute_gamma2_simple(d1_matrix, h1_2)

    assert gamma2_omega == gamma2_h1_1 == gamma2_h1_2


def test_gamma2_rejects_mismatched_row_width():
    """Verify that compute_gamma2_simple rejects matrix rows whose width differs from field dimension."""
    d1_malformed = [[1, 1]]  # Width 2, but field has dimension 3
    field = [Fraction(1, 1), Fraction(2, 1), Fraction(3, 1)]
    with pytest.raises(ValueError, match="does not match field dimension"):
        compute_gamma2_simple(d1_malformed, field)


# ---------------------------------------------------------------------------
# Evaluator Supremacy & Mandatory Field Binding
# ---------------------------------------------------------------------------

def test_evaluator_supremacy_and_operator_passivity():
    """
    Test Evaluator Supremacy:
    Two operators with completely different IDs and internal parameters proposing
    fields with identical certified diagnostic transitions receive the exact same acceptance verdict.
    """
    policy = EvaluatorPolicy(
        max_r_cl=Fraction(1, 1),
        max_phi1=Fraction(1, 2),
        max_gamma2=Fraction(1, 4),
    )
    evaluator = GuardedEvaluator(policy)

    op_alpha = OperatorProposal(
        operator_id="LieGenerator_U1_high_priority",
        parameters={"coupling": "0.99", "certified": "true"},
        initial_field=(Fraction(1, 1),),
        proposed_field=(Fraction(1, 4),),
    )
    op_beta = OperatorProposal(
        operator_id="RandomPerturbation_untrusted",
        parameters={"coupling": "0.01", "certified": "false"},
        initial_field=(Fraction(1, 1),),
        proposed_field=(Fraction(1, 4),),
    )

    before_diag = evaluator.evaluate_field_diagnostics(op_alpha.initial_field)
    after_diag_pass = evaluator.evaluate_field_diagnostics(op_alpha.proposed_field)

    res_alpha, _ = evaluator.evaluate_acceptance(op_alpha, before_diag, after_diag_pass)
    res_beta, _ = evaluator.evaluate_acceptance(op_beta, before_diag, after_diag_pass)
    assert res_alpha is True
    assert res_beta is True
    assert res_alpha == res_beta

    op_alpha_fail = OperatorProposal(
        operator_id="LieGenerator_U1_high_priority",
        parameters={"coupling": "0.99", "certified": "true"},
        initial_field=(Fraction(1, 1),),
        proposed_field=(Fraction(3, 4),),
    )
    op_beta_fail = OperatorProposal(
        operator_id="RandomPerturbation_untrusted",
        parameters={"coupling": "0.01", "certified": "false"},
        initial_field=(Fraction(1, 1),),
        proposed_field=(Fraction(3, 4),),
    )
    after_diag_fail = evaluator.evaluate_field_diagnostics(op_alpha_fail.proposed_field)
    res_alpha_fail, _ = evaluator.evaluate_acceptance(op_alpha_fail, before_diag, after_diag_fail)
    res_beta_fail, _ = evaluator.evaluate_acceptance(op_beta_fail, before_diag, after_diag_fail)
    assert res_alpha_fail is False
    assert res_beta_fail is False
    assert res_alpha_fail == res_beta_fail


def test_guarded_descent_rejects_unchanged_tuple():
    """Section 6 Guarded Descent Law requires strict descent; an unchanged field/tuple must be rejected."""
    policy = EvaluatorPolicy(max_r_cl=Fraction(1, 1))
    evaluator = GuardedEvaluator(policy)
    proposal = OperatorProposal(
        operator_id="IdentityOp",
        parameters={},
        initial_field=(Fraction(1, 2),),
        proposed_field=(Fraction(1, 2),),
    )

    diag = evaluator.evaluate_field_diagnostics(proposal.initial_field)
    accepted, reason = evaluator.evaluate_acceptance(proposal, diag, diag)
    assert accepted is False
    assert "Unchanged obstruction tuple" in reason


def test_guarded_descent_rejects_worsening_proposal():
    """Section 6 Guarded Descent Law rejects worsening proposals (e.g. 1 -> 2) even under permissive thresholds."""
    policy = EvaluatorPolicy(
        max_r_cl=Fraction(10, 1),
        max_phi1=Fraction(10, 1),
        max_gamma2=Fraction(10, 1),
    )
    evaluator = GuardedEvaluator(policy)
    proposal = OperatorProposal(
        operator_id="PerturbOp",
        parameters={},
        initial_field=(Fraction(1, 1),),
        proposed_field=(Fraction(2, 1),),
    )

    before_diag = evaluator.evaluate_field_diagnostics(proposal.initial_field)
    after_diag_worse = evaluator.evaluate_field_diagnostics(proposal.proposed_field)

    accepted, reason = evaluator.evaluate_acceptance(proposal, before_diag, after_diag_worse)
    assert accepted is False
    assert "strictly increased" in reason


def test_guarded_descent_pure_tuple_predicate_tiebreaks():
    """
    Section 6 Guarded Descent Law evaluated on hypothetical pure diagnostic tuples:
    1. Primary descent: Phi_1 strictly decreases -> accept
    2. Phi_1 tie, Gamma_2 strictly decreases -> accept
    3. Phi_1 tie, Gamma_2 tie, Xi strictly decreases -> accept
    4. Phi_1 tie, Gamma_2 increases -> reject
    5. Phi_1 tie, Gamma_2 tie, Xi increases -> reject
    """
    policy = EvaluatorPolicy(max_r_cl=Fraction(2, 1))
    before = ObstructionTuple(phi1=Fraction(2, 1), gamma2=Fraction(1, 1), r_cl=Fraction(1, 2), xi=Fraction(5, 1))

    # 1. Primary descent
    after1 = ObstructionTuple(phi1=Fraction(1, 1), gamma2=Fraction(1, 1), r_cl=Fraction(1, 1), xi=Fraction(5, 1))
    acc1, msg1 = evaluate_tuple_acceptance(policy, before, after1)
    assert acc1 is True
    assert "primary descent" in msg1

    # 2. Second-order tiebreak
    after2 = ObstructionTuple(phi1=Fraction(2, 1), gamma2=Fraction(1, 2), r_cl=Fraction(1, 4), xi=Fraction(5, 1))
    acc2, msg2 = evaluate_tuple_acceptance(policy, before, after2)
    assert acc2 is True
    assert "second-order tiebreak" in msg2

    # 3. Third-order tiebreak (Xi descent)
    after3 = ObstructionTuple(phi1=Fraction(2, 1), gamma2=Fraction(1, 1), r_cl=Fraction(1, 2), xi=Fraction(3, 1))
    acc3, msg3 = evaluate_tuple_acceptance(policy, before, after3)
    assert acc3 is True
    assert "third-order tiebreak" in msg3

    # 4. Gamma_2 increases under Phi_1 tie -> reject
    after4 = ObstructionTuple(phi1=Fraction(2, 1), gamma2=Fraction(3, 2), r_cl=Fraction(3, 4), xi=Fraction(1, 1))
    acc4, msg4 = evaluate_tuple_acceptance(policy, before, after4)
    assert acc4 is False
    assert "Gamma_2 strictly increased" in msg4

    # 5. Xi increases under Phi_1 and Gamma_2 tie -> reject
    after5 = ObstructionTuple(phi1=Fraction(2, 1), gamma2=Fraction(1, 1), r_cl=Fraction(1, 2), xi=Fraction(7, 1))
    acc5, msg5 = evaluate_tuple_acceptance(policy, before, after5)
    assert acc5 is False
    assert "Xi strictly increased" in msg5


def test_evaluator_rejects_single_tuple_without_transition():
    """Verify that evaluate_acceptance rejects single-tuple calls without a before/after transition."""
    policy = EvaluatorPolicy(max_r_cl=Fraction(1, 1))
    evaluator = GuardedEvaluator(policy)
    op = OperatorProposal("TestOp", {}, (Fraction(1, 1),), (Fraction(1, 2),))
    diag = evaluator.evaluate_field_diagnostics(op.initial_field)

    accepted, reason = evaluator.evaluate_acceptance(op, diag, after_diag=None)
    assert accepted is False
    assert "requires both before and after states" in reason


def test_evaluate_acceptance_detects_spoofed_diagnostic_tuple():
    """
    Verify that evaluate_acceptance detects and refutes caller-supplied diagnostic tuples
    that do not match the certified diagnostics of the proposed field.
    """
    policy = EvaluatorPolicy(max_r_cl=Fraction(10, 1), max_phi1=Fraction(10, 1))
    evaluator = GuardedEvaluator(policy)

    initial_field = (Fraction(1, 1), Fraction(0, 1), Fraction(0, 1))
    proposed_field = (Fraction(10, 1), Fraction(0, 1), Fraction(0, 1))
    op = OperatorProposal("MaliciousOp", {}, initial_field, proposed_field)

    before_diag = evaluator.evaluate_field_diagnostics(initial_field)
    spoofed_zero_after_diag = evaluator.evaluate_diagnostics(phi1=Fraction(0, 1), gamma2=Fraction(0, 1))

    accepted, reason = evaluator.evaluate_acceptance(op, before_diag, spoofed_zero_after_diag)
    assert accepted is False
    assert "does not match certified proposed_field Phi_1" in reason


# ---------------------------------------------------------------------------
# R1: Bind Gate Input to Evaluator-Owned Evidence
# ---------------------------------------------------------------------------

def test_r1_evaluate_acceptance_rejects_spoofed_ratio():
    """
    R1 Requirement:
    In compatible C3 complex with face rows (1,1,1) and (-1,-1,-1),
    transition (2,0,0) -> (1,0,0) has target Phi=1, Gamma=2, R=2.
    Under max_R=1:
    1. Honest tuple has R=2 > 1 -> rejected.
    2. Caller replacing only supplied ratio with 0 -> rejected for spoofed ratio!
    """
    e01, e12, e20 = Edge(0, 1), Edge(1, 2), Edge(2, 0)
    c3_graph = FiniteGraph(vertices=(0, 1, 2), edges=(e01, e12, e20))
    d1_matrix = ((1, 1, 1), (-1, -1, -1))
    c3_complex = AdmittedComplex(graph=c3_graph, d1_matrix=d1_matrix)

    policy = EvaluatorPolicy(max_r_cl=Fraction(1, 1))
    evaluator = GuardedEvaluator(policy, admitted_complex=c3_complex)

    initial_field = (Fraction(2, 1), Fraction(0, 1), Fraction(0, 1))
    proposed_field = (Fraction(1, 1), Fraction(0, 1), Fraction(0, 1))
    op = OperatorProposal("RatioTestOp", {}, initial_field, proposed_field)

    # Honest diagnostics computed by evaluator
    honest_before = evaluator.evaluate_field_diagnostics(initial_field)
    honest_after = evaluator.evaluate_field_diagnostics(proposed_field)
    assert honest_after.phi1 == Fraction(1, 1)
    assert honest_after.gamma2 == Fraction(2, 1)
    assert honest_after.r_cl == Fraction(2, 1)

    # 1. Honest target ratio R=2 > max_R=1 must be refused
    accepted, reason = evaluator.evaluate_acceptance(op, honest_before, honest_after)
    assert accepted is False
    assert "exceeds policy ceiling" in reason

    # 2. Caller spoofing r_cl to 0 while keeping phi1=1 and gamma2=2 must be refused
    spoofed_after = ObstructionTuple(
        phi1=Fraction(1, 1),
        gamma2=Fraction(2, 1),
        r_cl=Fraction(0, 1),  # Spoofed!
        xi=Fraction(0, 1),
    )
    acc_spoof, reason_spoof = evaluator.evaluate_acceptance(op, honest_before, spoofed_after)
    assert acc_spoof is False
    assert "does not match certified proposed_field R_cl" in reason_spoof


def test_r1_no_complex_gamma_cannot_create_secondary_descent():
    """
    R1 Requirement:
    When no second differential is declared, Gamma is the declared neutral convention (0).
    Arbitrary caller-supplied Gamma values must be rejected fail-closed.
    """
    policy = EvaluatorPolicy(max_r_cl=Fraction(2, 1))
    evaluator = GuardedEvaluator(policy)  # No complex or d1 declared

    initial_field = (Fraction(1, 1), Fraction(0, 1), Fraction(0, 1))
    proposed_field = (Fraction(1, 1), Fraction(0, 1), Fraction(0, 1))
    op = OperatorProposal("NoComplexOp", {}, initial_field, proposed_field)

    # Caller tries to forge a secondary tiebreak descent on Gamma (2 -> 1)
    forged_before = ObstructionTuple(phi1=Fraction(1, 1), gamma2=Fraction(2, 1), r_cl=Fraction(2, 1))
    forged_after = ObstructionTuple(phi1=Fraction(1, 1), gamma2=Fraction(1, 1), r_cl=Fraction(1, 1))

    accepted, reason = evaluator.evaluate_acceptance(op, forged_before, forged_after)
    assert accepted is False
    assert "No second differential declared" in reason


def test_r1_domain_validation_rejects_negative_parameters():
    """R1 Requirement: Validate policy and diagnostic domains."""
    with pytest.raises(ValueError, match="Domain error"):
        EvaluatorPolicy(max_r_cl=Fraction(-1, 1))

    with pytest.raises(ValueError, match="Domain error"):
        EvaluatorPolicy(max_r_cl=Fraction(1, 1), epsilon_guard=Fraction(0, 1))

    with pytest.raises(ValueError, match="Domain error"):
        ObstructionTuple(phi1=Fraction(-1, 1), gamma2=Fraction(0, 1), r_cl=Fraction(0, 1))


# ---------------------------------------------------------------------------
# R2: Bind Carrier and Field Dimensions
# ---------------------------------------------------------------------------

def test_r2_ordinary_proposal_rejects_carrier_dimension_mismatch():
    """
    R2 Requirement:
    Ordinary proposals (2,0,0) -> (1,) and (2,0,0) -> () change carrier dimensions
    without declaring a structural operator and must be rejected before diagnostics.
    """
    policy = EvaluatorPolicy(max_r_cl=Fraction(1, 1))
    evaluator = GuardedEvaluator(policy)

    op_shrink1 = OperatorProposal("ShrinkOp1", {}, (Fraction(2), Fraction(0), Fraction(0)), (Fraction(1),))
    accepted1, reason1, _, _ = evaluator.evaluate_proposal_step(op_shrink1)
    assert accepted1 is False
    assert "carrier dimension" in reason1

    op_empty = OperatorProposal("EmptyOp", {}, (Fraction(2), Fraction(0), Fraction(0)), ())
    accepted2, reason2, _, _ = evaluator.evaluate_proposal_step(op_empty)
    assert accepted2 is False
    assert "carrier dimension" in reason2


def test_r2_empty_carrier_does_not_bypass_verification():
    """
    R2 Requirement:
    An explicitly empty carrier (dimension 0) must compute actual diagnostics (0,0,0,0)
    and must not use truthiness to skip field verification.
    """
    policy = EvaluatorPolicy(max_r_cl=Fraction(1, 1))
    evaluator = GuardedEvaluator(policy)

    op_empty = OperatorProposal("EmptyCarryOp", {}, (), ())
    # Caller supplies forged nonzero after_diag
    forged_after = ObstructionTuple(phi1=Fraction(1, 1), gamma2=Fraction(0, 1), r_cl=Fraction(0, 1))
    honest_before = ObstructionTuple(phi1=Fraction(0, 1), gamma2=Fraction(0, 1), r_cl=Fraction(0, 1))

    accepted, reason = evaluator.evaluate_acceptance(op_empty, honest_before, forged_after)
    assert accepted is False
    assert "does not match certified proposed_field Phi_1" in reason


def test_r2_structural_proposal_step_interface():
    """R2 Requirement: Structural proposals across distinct carriers use an explicit interface."""
    # Source carrier: C3 cycle with non-zero obstruction Phi_1 = 2
    g1 = FiniteGraph(vertices=(0, 1, 2), edges=(Edge(0, 1), Edge(1, 2), Edge(2, 0)))
    c1 = AdmittedComplex(graph=g1)

    # Target carrier: path tree with Phi_1 = 0
    g2 = FiniteGraph(vertices=(0, 1, 2), edges=(Edge(0, 1), Edge(1, 2)))
    c2 = AdmittedComplex(graph=g2)

    struct_op = StructuralOperatorProposal(
        operator_id="GraphExtensionLift",
        parameters={},
        source_carrier=c1,
        target_carrier=c2,
        initial_field=(Fraction(2, 1), Fraction(0, 1), Fraction(0, 1)),
        proposed_field=(Fraction(1, 1), Fraction(0, 1)),
        carrier_map={0: 0, 1: 1},
    )

    policy = EvaluatorPolicy(max_r_cl=Fraction(1, 1))
    evaluator = GuardedEvaluator(policy)
    acc, reason, b_diag, a_diag = evaluator.evaluate_structural_proposal_step(struct_op)
    # Target field on tree c2 has Phi_1 = 0 (exactness), initial has Phi_1 = 2 -> strict descent
    assert acc is True
    assert "primary descent" in reason


# ---------------------------------------------------------------------------
# R3: Distinguish Cycle Specialization from General Graph Solver
# ---------------------------------------------------------------------------

def test_r3_tree_exactness_on_path_graph():
    """
    R3 Requirement:
    On path 0->1->2, field (1, 1) = d0(0, 1, 2) is exact (Phi_1 = 0).
    The naive formula abs(sum(field)) incorrectly returned Phi_1 = 2.
    The graph evaluator certifies tree exactness with Phi_1 = 0 and residual r = 0.
    """
    e01, e12 = Edge(0, 1), Edge(1, 2)
    path_graph = FiniteGraph(vertices=(0, 1, 2), edges=(e01, e12))
    path_complex = AdmittedComplex(graph=path_graph)

    field = (Fraction(1, 1), Fraction(1, 1))
    witness = solve_tree_witness(path_graph, field)
    assert witness.potential == (Fraction(0, 1), Fraction(1, 1), Fraction(2, 1))
    assert witness.dual_flow == (Fraction(0, 1), Fraction(0, 1))

    certified_phi1 = verify_primal_dual_witness(path_graph, field, witness)
    assert certified_phi1 == Fraction(0, 1)

    # GuardedEvaluator with admitted complex computes certified Phi_1 = 0
    policy = EvaluatorPolicy(max_r_cl=Fraction(1, 1))
    evaluator = GuardedEvaluator(policy, admitted_complex=path_complex)
    diag = evaluator.evaluate_field_diagnostics(field)
    assert diag.phi1 == Fraction(0, 1)


def test_r3_malformed_complex_rejection():
    """R3 Requirement: Malformed complex violating d_1 o d_0 = 0 is rejected on initialization."""
    e01, e12, e20 = Edge(0, 1), Edge(1, 2), Edge(2, 0)
    c3_graph = FiniteGraph(vertices=(0, 1, 2), edges=(e01, e12, e20))

    # Face [1, 0, 0] does not close: d1 o d0 != 0
    bad_face = ((1, 0, 0),)
    with pytest.raises(ValueError, match="Complex validation failed: d_1 o d_0 != 0"):
        AdmittedComplex(graph=c3_graph, d1_matrix=bad_face)


def test_r3_primal_dual_witness_duality_gap_rejection():
    """R3 Requirement: Witnesses with non-zero duality gap or infeasibility are refused."""
    e01, e12, e20 = Edge(0, 1), Edge(1, 2), Edge(2, 0)
    c3_graph = FiniteGraph(vertices=(0, 1, 2), edges=(e01, e12, e20))
    field = (Fraction(2, 1), Fraction(0, 1), Fraction(0, 1))

    # Infeasible dual: flow is not divergence-free
    bad_flow_witness = ExactPrimalDualWitness(
        potential=(Fraction(0), Fraction(0), Fraction(0)),
        dual_flow=(Fraction(1), Fraction(0), Fraction(0)),
    )
    with pytest.raises(ValueError, match="Dual flow infeasible: non-zero divergence"):
        verify_primal_dual_witness(c3_graph, field, bad_flow_witness)

    # Infeasible dual: ||z||_inf > 1
    overbound_witness = ExactPrimalDualWitness(
        potential=(Fraction(0), Fraction(0), Fraction(0)),
        dual_flow=(Fraction(2), Fraction(2), Fraction(2)),
    )
    with pytest.raises(ValueError, match="Dual flow infeasible: ||z||_infinity violated"):
        verify_primal_dual_witness(c3_graph, field, overbound_witness)


# ---------------------------------------------------------------------------
# R4: Realizable Secondary Tie-Break on Theta-Graph
# ---------------------------------------------------------------------------

def test_r4_theta_graph_realizable_secondary_tiebreak():
    """
    R4 Requirement:
    Add a theta-graph example with edge order 01, 12, 02, 03, 32 and
    face rows (1, 1, -1, 0, 0) and (0, 0, -1, 1, 1).
    Before field (0, 0, -1, 0, 0) and after field (1, 0, 0, 0, 0) both have Phi_1 = 1,
    with Gamma_2 decreasing 2 -> 1.
    Zero potential and dual (1, 1, -1, 0, 0) certify both Phi_1 values exactly.
    Verified under full graph and complex binding with accepted second-order tiebreak!
    """
    e01 = Edge(0, 1)
    e12 = Edge(1, 2)
    e02 = Edge(0, 2)
    e03 = Edge(0, 3)
    e32 = Edge(3, 2)
    theta_graph = FiniteGraph(vertices=(0, 1, 2, 3), edges=(e01, e12, e02, e03, e32))
    d1_theta = (
        (1, 1, -1, 0, 0),
        (0, 0, -1, 1, 1),
    )
    theta_complex = AdmittedComplex(graph=theta_graph, d1_matrix=d1_theta)

    omega_before = (Fraction(0), Fraction(0), Fraction(-1), Fraction(0), Fraction(0))
    omega_after = (Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(0))

    # Shared certifying witness
    f_zero = (Fraction(0), Fraction(0), Fraction(0), Fraction(0))
    z_cycle = (Fraction(1), Fraction(1), Fraction(-1), Fraction(0), Fraction(0))
    witness = ExactPrimalDualWitness(potential=f_zero, dual_flow=z_cycle)

    phi_b = verify_primal_dual_witness(theta_graph, omega_before, witness)
    phi_a = verify_primal_dual_witness(theta_graph, omega_after, witness)
    assert phi_b == Fraction(1, 1)
    assert phi_a == Fraction(1, 1)

    gamma_b = compute_gamma2_simple(d1_theta, omega_before)
    gamma_a = compute_gamma2_simple(d1_theta, omega_after)
    assert gamma_b == Fraction(2, 1)
    assert gamma_a == Fraction(1, 1)

    policy = EvaluatorPolicy(max_r_cl=Fraction(1, 1))
    evaluator = GuardedEvaluator(policy, admitted_complex=theta_complex)

    proposal = OperatorProposal(
        operator_id="ThetaCycleTransport",
        parameters={},
        initial_field=omega_before,
        proposed_field=omega_after,
    )

    acc, reason, before_diag, after_diag = evaluator.evaluate_proposal_step(
        proposal,
        before_witness=witness,
        after_witness=witness,
    )

    assert before_diag.phi1 == Fraction(1, 1)
    assert after_diag.phi1 == Fraction(1, 1)
    assert before_diag.gamma2 == Fraction(2, 1)
    assert after_diag.gamma2 == Fraction(1, 1)
    assert after_diag.r_cl == Fraction(1, 1)
    assert acc is True
    assert "second-order tiebreak" in reason


# ---------------------------------------------------------------------------
# R5: External-Xi Trust Boundary
# ---------------------------------------------------------------------------

def test_r5_external_xi_trust_boundary_rejects_unbound_descent():
    """
    R5 Requirement:
    Changing caller-supplied Xi from 1 -> 0 on an unchanged field must be rejected
    unless certified by an evaluator-bound Xi verifier.
    """
    policy = EvaluatorPolicy(max_r_cl=Fraction(1, 1))
    evaluator = GuardedEvaluator(policy)  # No xi_evaluator bound

    field = (Fraction(1, 1), Fraction(0, 1), Fraction(0, 1))
    op = OperatorProposal("UnchangedWithForgedXi", {}, field, field)

    before_diag = ObstructionTuple(phi1=Fraction(1, 1), gamma2=Fraction(0, 1), r_cl=Fraction(0, 1), xi=Fraction(1, 1))
    after_diag = ObstructionTuple(phi1=Fraction(1, 1), gamma2=Fraction(0, 1), r_cl=Fraction(0, 1), xi=Fraction(0, 1))

    accepted, reason = evaluator.evaluate_acceptance(op, before_diag, after_diag)
    assert accepted is False
    assert "External Xi trust boundary" in reason


def test_r5_evaluator_bound_xi_verifier():
    """Verify that an evaluator-bound Xi verifier certifies Xi honestly."""
    policy = EvaluatorPolicy(max_r_cl=Fraction(1, 1))
    # Bound Xi verifier: sum of squares of field
    xi_func = lambda f: sum(x * x for x in f)
    evaluator = GuardedEvaluator(policy, xi_evaluator=xi_func)

    op = OperatorProposal(
        "XiDescentOp",
        {},
        (Fraction(1, 1), Fraction(0, 1)),
        (Fraction(1, 2), Fraction(1, 2)),
    )
    # Holonomy: both 1 + 0 = 1 and 1/2 + 1/2 = 1 (Phi_1 tie)
    # Xi: 1^2 + 0 = 1 -> (1/2)^2 + (1/2)^2 = 1/2 (Xi descends!)
    acc, reason, b_diag, a_diag = evaluator.evaluate_proposal_step(op)
    assert b_diag.xi == Fraction(1, 1)
    assert a_diag.xi == Fraction(1, 2)
    assert acc is True
    assert "third-order tiebreak" in reason


# ---------------------------------------------------------------------------
# R6: Correct Claim-to-Artifact Mappings
# ---------------------------------------------------------------------------

def test_r6_cyclic_shift_operator_holonomy_invariance():
    """
    R6 Requirement (C12):
    CyclicShift on C_3 cyclically permutes edge weights, leaving holonomy invariant.
    Generates a period-3 orbit rejected at every step by the Guarded Descent Law.
    """
    e01, e12, e20 = Edge(0, 1), Edge(1, 2), Edge(2, 0)
    c3_graph = FiniteGraph(vertices=(0, 1, 2), edges=(e01, e12, e20))
    c3_complex = AdmittedComplex(graph=c3_graph)

    policy = EvaluatorPolicy(max_r_cl=Fraction(1, 1))
    evaluator = GuardedEvaluator(policy, admitted_complex=c3_complex)

    # Shift 1: (1, 0, 0) -> (0, 1, 0)
    op1 = OperatorProposal("CyclicShift", {"shift": "1"}, (Fraction(1), Fraction(0), Fraction(0)), (Fraction(0), Fraction(1), Fraction(0)))
    acc1, reason1, b1, a1 = evaluator.evaluate_proposal_step(op1)
    assert b1.phi1 == a1.phi1 == Fraction(1, 1)
    assert acc1 is False
    assert "Unchanged obstruction tuple" in reason1

    # Shift 2: (0, 1, 0) -> (0, 0, 1)
    op2 = OperatorProposal("CyclicShift", {"shift": "1"}, (Fraction(0), Fraction(1), Fraction(0)), (Fraction(0), Fraction(0), Fraction(1)))
    acc2, reason2, b2, a2 = evaluator.evaluate_proposal_step(op2)
    assert b2.phi1 == a2.phi1 == Fraction(1, 1)
    assert acc2 is False
    assert "Unchanged obstruction tuple" in reason2


def test_r6_operator_atlas_lggr_non_promotion():
    """
    R6 Requirement (C13):
    Operator-Atlas LGGR Non-Promotion:
    Local chart proposals descend local obstruction (Local-Green), but their glued
    global assembly has non-vanishing global obstruction and is rejected (Global-Red).
    """
    # Global cycle C_3: edges 01, 12, 20
    e01, e12, e20 = Edge(0, 1), Edge(1, 2), Edge(2, 0)
    c3_graph = FiniteGraph(vertices=(0, 1, 2), edges=(e01, e12, e20))
    c3_complex = AdmittedComplex(graph=c3_graph)

    # Chart 1: edges 01, 12 (a tree)
    chart1_graph = FiniteGraph(vertices=(0, 1, 2), edges=(e01, e12))
    # Chart 2: edges 12, 20 (a tree)
    chart2_graph = FiniteGraph(vertices=(0, 1, 2), edges=(e12, e20))

    # Proposed global field: omega = (1, 0, 0)
    # On Chart 1, edges are (1, 0) which on a tree has Phi_1 = 0 (exactness) -> Local-Green!
    w1 = solve_tree_witness(chart1_graph, (Fraction(1), Fraction(0)))
    phi_local1 = verify_primal_dual_witness(chart1_graph, (Fraction(1), Fraction(0)), w1)
    assert phi_local1 == Fraction(0, 1)

    # On Chart 2, edges are (0, 0) which has Phi_1 = 0 -> Local-Green!
    w2 = solve_tree_witness(chart2_graph, (Fraction(0), Fraction(0)))
    phi_local2 = verify_primal_dual_witness(chart2_graph, (Fraction(0), Fraction(0)), w2)
    assert phi_local2 == Fraction(0, 1)

    # But globally on C_3, omega = (1, 0, 0) has holonomy Phi_1 = 1 > 0!
    phi_global = compute_phi1_cycle_graph((Fraction(1), Fraction(0), Fraction(0)))
    assert phi_global == Fraction(1, 1)

    # Transition from (0, 0, 0) to (1, 0, 0) is rejected globally (Global-Red)
    policy = EvaluatorPolicy(max_r_cl=Fraction(1, 1))
    evaluator = GuardedEvaluator(policy, admitted_complex=c3_complex)
    op = OperatorProposal("AtlasGluedOp", {}, (Fraction(0), Fraction(0), Fraction(0)), (Fraction(1), Fraction(0), Fraction(0)))
    acc, reason, _, _ = evaluator.evaluate_proposal_step(op)
    assert acc is False
    assert "strictly increased" in reason


def test_r6_path_operator_metadata_erasure():
    """
    R6 Requirement (C14):
    Path Operator Erasure: Replacing operator metadata along an accepted trajectory
    leaves path acceptance invariant under the Guarded Descent Law.
    """
    policy = EvaluatorPolicy(max_r_cl=Fraction(1, 1))
    evaluator = GuardedEvaluator(policy)

    step1 = OperatorProposal("AuthOp_1", {"secret": "abc"}, (Fraction(3),), (Fraction(2),))
    step2 = OperatorProposal("AuthOp_2", {"secret": "xyz"}, (Fraction(2),), (Fraction(1),))
    path_auth = [step1, step2]

    step1_erased = OperatorProposal("Dummy_0", {}, (Fraction(3),), (Fraction(2),))
    step2_erased = OperatorProposal("Dummy_0", {}, (Fraction(2),), (Fraction(1),))
    path_erased = [step1_erased, step2_erased]

    acc1, reason1, trace1 = evaluate_path_acceptance(evaluator, path_auth)
    acc2, reason2, trace2 = evaluate_path_acceptance(evaluator, path_erased)

    assert acc1 is True
    assert acc2 is True
    assert trace1 == trace2


# ---------------------------------------------------------------------------
# R7: Separate Exact Ratio and Threshold-Routing Policy
# ---------------------------------------------------------------------------

def test_r7_exact_ratio_versus_threshold_routing_separation():
    """
    R7 Requirement:
    Separate exact algebraic ratio R_exact = Gamma_2 / Phi_1 from piecewise R_epsilon.
    Example:
    Phi_1 = 1/4000, Gamma_2 = 1/2000, epsilon = 1/1000:
    - Exact algebraic ratio R_exact = (1/2000) / (1/4000) = 2.
    - Piecewise R_epsilon = 0, routing status = 'SUB_EPSILON_FLAT' (since both <= epsilon).
    - High-level evaluator accepts under max_R=1 when Phi_1 descends (e.g. 2/1000 -> 1/4000).
    Verifies that accepted thresholded gates do not imply an exact ratio ceiling <= 1.
    """
    eps = Fraction(1, 1000)
    phi1 = Fraction(1, 4000)
    gamma2 = Fraction(1, 2000)

    # 1. Exact ratio is algebraically 2
    r_exact = compute_r_exact(phi1, gamma2)
    assert r_exact == Fraction(2, 1)

    # 2. Piecewise convention routes to SUB_EPSILON_FLAT (0)
    r_eps, status = compute_r_epsilon(phi1, gamma2, epsilon_guard=eps)
    assert r_eps == Fraction(0, 1)
    assert status == "SUB_EPSILON_FLAT"

    # 3. Evaluator with max_r_cl = 1 accepts when Phi descends from 2/1000 -> 1/4000
    policy = EvaluatorPolicy(max_r_cl=Fraction(1, 1), epsilon_guard=eps)
    before_diag = ObstructionTuple(
        phi1=Fraction(2, 1000),
        gamma2=Fraction(1, 1000),
        r_cl=Fraction(1, 2),
        r_exact=Fraction(1, 2),
        routing_status="REGULAR",
    )
    after_diag = ObstructionTuple(
        phi1=phi1,
        gamma2=gamma2,
        r_cl=r_eps,
        r_exact=r_exact,
        routing_status=status,
    )
    acc, msg = evaluate_tuple_acceptance(policy, before_diag, after_diag)
    assert acc is True
    assert "primary descent" in msg


def test_r7_phi1_zero_implies_gamma2_zero_on_complex():
    """
    R7 Requirement:
    Preserve the proved result that Phi_1 = 0 implies Gamma_2 = 0 on any declared 2-complex.
    """
    e01, e12, e20 = Edge(0, 1), Edge(1, 2), Edge(2, 0)
    c3_graph = FiniteGraph(vertices=(0, 1, 2), edges=(e01, e12, e20))
    d1_matrix = ((1, 1, 1),)
    c3_complex = AdmittedComplex(graph=c3_graph, d1_matrix=d1_matrix)

    # Exact field [2, -1, -1] has holonomy 0 => Phi1 = 0
    exact_field = (Fraction(2, 1), Fraction(-1, 1), Fraction(-1, 1))
    gamma2 = compute_gamma2_simple(c3_complex.d1_matrix, exact_field)
    assert gamma2 == Fraction(0, 1)
    assert compute_r_exact(Fraction(0, 1), gamma2) == Fraction(0, 1)


# ---------------------------------------------------------------------------
# Mathematical Extension Test: Continuation-Stable Erasure
# ---------------------------------------------------------------------------

def test_continuation_stable_erasure_counterexample():
    """
    Verifies the mathematical extension counterexample:
    On C_3 with translation operator T(w) = w + (1, 0, 0):
    x = (1, 0, 0) and y = (-1, 0, 0).
    Initially:
    D(x) = D(y) = (Phi_1=1, Gamma_2=0, R_cl=0, Xi=0).
    After permitted translation T:
    T(x) = (2, 0, 0) -> Phi_1 = 2
    T(y) = (0, 0, 0) -> Phi_1 = 0
    Demonstrates that ker(D) is not stable under the admitted translation operator family,
    establishing that continuation closure ~_T is required for multi-step erasure.
    """
    x = (Fraction(1), Fraction(0), Fraction(0))
    y = (Fraction(-1), Fraction(0), Fraction(0))

    phi_x = compute_phi1_cycle_graph(x)
    phi_y = compute_phi1_cycle_graph(y)
    assert phi_x == Fraction(1, 1)
    assert phi_y == Fraction(1, 1)

    # Translation operator T(w) = w + (1, 0, 0)
    T = lambda w: (w[0] + Fraction(1), w[1], w[2])
    Tx = T(x)  # (2, 0, 0)
    Ty = T(y)  # (0, 0, 0)

    phi_Tx = compute_phi1_cycle_graph(Tx)
    phi_Ty = compute_phi1_cycle_graph(Ty)
    assert phi_Tx == Fraction(2, 1)
    assert phi_Ty == Fraction(0, 1)
    assert phi_Tx != phi_Ty
