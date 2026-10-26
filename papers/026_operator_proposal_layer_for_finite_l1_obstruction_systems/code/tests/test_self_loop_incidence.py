"""A loop has zero incidence at its vertex: both endpoint terms contribute."""
from fractions import Fraction

from mod_operator_proposal_core import AdmittedComplex, Edge, ExactPrimalDualWitness, FiniteGraph, verify_primal_dual_witness


def test_self_loop_face_satisfies_chain_condition():
    graph = FiniteGraph(vertices=(0,), edges=(Edge(0, 0),))
    complex_ = AdmittedComplex(graph, d1_matrix=((1,),))
    assert complex_.d1_matrix == ((1,),)


def test_self_loop_dual_witness_keeps_both_incidence_signs():
    graph = FiniteGraph(vertices=(0,), edges=(Edge(0, 0),))
    witness = ExactPrimalDualWitness(potential=(Fraction(0),), dual_flow=(Fraction(1),))
    assert verify_primal_dual_witness(graph, (Fraction(2),), witness) == Fraction(2)
