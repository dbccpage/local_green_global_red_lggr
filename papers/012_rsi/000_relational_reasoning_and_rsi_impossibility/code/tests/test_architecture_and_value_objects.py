# Claim Hygiene: AuthorityEffect: None
# Tests verify Clean Architecture AST inward dependency boundary, exact-type value object
# equality and non-coercion, and negative-control parameter validation.
from __future__ import annotations

import ast
from fractions import Fraction
from pathlib import Path
import sys

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CODE_DIR = PACKAGE_ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from single_agent_graph import (  # noqa: E402
    FiniteStateSelfModifyingGraph,
    ObstructionReceipt,
    TransitionState,
    compute_phi1_holonomy,
)
from multi_agent_hypergraph import (  # noqa: E402
    HypergraphAgentSpec,
    HypergraphObstructionReceipt,
    MultiAgentCommunicatingHypergraph,
    MultiAgentTransitionState,
    SharedTwoComplex,
)
from simplicial_complex import HigherCellComplex  # noqa: E402
from higher_cell_async_hypergraph import (  # noqa: E402
    HigherCellAsyncCommunicatingHypergraph,
    HigherCellObstructionReceipt,
)
from communication_channels import (  # noqa: E402
    AsynchronousMessageDelayBuffer,
    NonMonotonicMessageChannel,
)
from simplicial_rewiring import DynamicSimplicialRewiringSchedule  # noqa: E402


# ---------------------------------------------------------------------------
# Class 1: Clean Architecture AST Boundary & Inward Dependency Enforcement
# ---------------------------------------------------------------------------

def test_clean_architecture_code_ast_imports_have_no_outer_dependencies() -> None:
    """Class 1 Landau invariant:
    INVARIANT: The code/ module represents sovereign domain/computational logic and must NEVER import
               from outer layers (use_cases, controllers, frameworks, or external mock libraries).
    BREAK: An engineer accidentally imports an external HTTP client, web framework, or test mock into code/.
    WITNESS: AST inspection detects unauthorized imports in python files under code/.
    MUTATION: Adding `import requests` or `from unittest.mock import Mock` to single_agent_graph.py breaks this test.
    """
    forbidden_prefixes = (
        "unittest.mock",
        "mock",
        "requests",
        "urllib3",
        "fastapi",
        "flask",
        "django",
        "omega_engine_woland",
    )

    py_files = [p for p in CODE_DIR.glob("*.py") if p.is_file()]
    assert py_files, "No python source files found in code/"

    for py_file in py_files:
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for forbidden in forbidden_prefixes:
                        assert not alias.name.startswith(forbidden), (
                            f"Prohibited import '{alias.name}' detected in {py_file.name}:{node.lineno}"
                        )
            elif isinstance(node, ast.ImportFrom) and node.module:
                for forbidden in forbidden_prefixes:
                    assert not node.module.startswith(forbidden), (
                        f"Prohibited from-import '{node.module}' detected in {py_file.name}:{node.lineno}"
                    )


# ---------------------------------------------------------------------------
# Class 1: Exact-Type Value Object Equality & Non-Coercion Invariants
# ---------------------------------------------------------------------------

def test_value_object_exact_type_equality_rejects_cross_type_coercion() -> None:
    """Class 1 Landau invariant:
    INVARIANT: Domain Value Objects (TransitionState, HypergraphAgentSpec, ObstructionReceipt) must never
               equate across distinct types or coerce from raw primitive tuples or strings.
    BREAK: A loose equality implementation checks field values or uses tuple unpacking causing false equivalence.
    WITNESS: Value object equality with distinct types or primitives returns False.
    MUTATION: Overriding __eq__ on TransitionState to return tuple equality breaks this test.
    """
    ts = TransitionState(step_index=0, report_id=1, internal_eval=1, remaining_budget=0)
    # Reject raw tuple or dict equality
    assert ts != (0, 1, 1, 0)
    assert ts != {"step_index": 0, "report_id": 1, "internal_eval": 1, "remaining_budget": 0}
    assert ts != "TransitionState(0, 1, 1, 0)"

    spec = HypergraphAgentSpec(agent_id="agent_A", carrier_capacity=5)
    # Reject string or tuple equivalence
    assert spec != ("agent_A", 5)
    assert spec != "agent_A"
    assert spec != 5

    complex_two = SharedTwoComplex(vertices=(0, 1, 2), triangles=((0, 1, 2),), shared_edges=((0, 1), (1, 2), (0, 2)))
    assert complex_two != ((0, 1, 2),)
    assert complex_two != [0, 1, 2]


# ---------------------------------------------------------------------------
# Class 2: Negative-Control Parameter Boundary Falsification
# ---------------------------------------------------------------------------

def test_negative_control_finite_state_graph_parameter_falsification() -> None:
    """Class 2 Landau failure-mode kill:
    INVARIANT: FiniteStateSelfModifyingGraph must strictly reject negative, zero, non-integer,
               or boolean capacities and negative budgets with explicit ValueError.
    BREAK: Invalid constructor arguments like N=0, N=-5, N=True, or B=-1 silently succeed.
    WITNESS: Constructor raises ValueError with explicit message.
    MUTATION: Removing parameter validation in FiniteStateSelfModifyingGraph.__init__ breaks this test.
    """
    with pytest.raises(ValueError, match="carrier_capacity N must be a positive integer"):
        FiniteStateSelfModifyingGraph(carrier_capacity=0, initial_lift_budget=0)

    with pytest.raises(ValueError, match="carrier_capacity N must be a positive integer"):
        FiniteStateSelfModifyingGraph(carrier_capacity=-3, initial_lift_budget=0)

    with pytest.raises(ValueError, match="carrier_capacity N must be a positive integer"):
        # Python bool is an int subclass; strict type checking must guard against True/False
        FiniteStateSelfModifyingGraph(carrier_capacity=True, initial_lift_budget=0)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="initial_lift_budget B_0 must be a non-negative integer"):
        FiniteStateSelfModifyingGraph(carrier_capacity=5, initial_lift_budget=-1)

    with pytest.raises(ValueError, match="initial_lift_budget B_0 must be a non-negative integer"):
        FiniteStateSelfModifyingGraph(carrier_capacity=5, initial_lift_budget=False)  # type: ignore[arg-type]


def test_negative_control_non_monotonic_channel_causal_inversion_rejection() -> None:
    """Class 2 Landau failure-mode kill:
    INVARIANT: NonMonotonicMessageChannel must reject future message delivery permutations (sigma(k) > k)
               at construction time, enforcing temporal causality.
    BREAK: A permutation schedule specifying delivery from the future (e.g., step 1 receives from step 2) is accepted.
    WITNESS: Constructor raises ValueError("Causal delivery violation").
    MUTATION: Disabling causality check in NonMonotonicMessageChannel.__init__ breaks this test.
    """
    with pytest.raises(ValueError, match="Causal delivery violation"):
        NonMonotonicMessageChannel(
            num_agents=2,
            permutation_schedule_per_agent={0: {1: 2}},  # Step 1 delivers from step 2 (acausal)
        )


def test_negative_control_two_signal_collapse_refusal_matrix() -> None:
    """Class 2 Landau failure-mode kill:
    INVARIANT: Any observer identifying as an uncorroborated peer agent, internal model, LLM,
               or self-critique detector must fail closed with TWO_SIGNAL_COLLAPSE.
    BREAK: Self-critique observer string "agent" or "model" is accepted as an independent witness.
    WITNESS: eis_independence_verdict contains error code TWO_SIGNAL_COLLAPSE.
    MUTATION: Allowing observer "agent" in verify_signal_independence breaks this test.
    """
    from eis_verifier import verify_signal_independence

    detector_id = "detector.rsi_claim_scanner"
    matches = [{"matched_by": detector_id, "signature": "a" * 64}]
    context = {"detector_id": detector_id, "detector_predicates": ["PROTECTED_FIELD_VIOLATION"]}

    # 1. Reject forbidden self/model observer strings
    for bad_obs in ("agent", "model", "llm", "detector", "matcher"):
        danger = {"observer_id": bad_obs, "danger_type": "MANIFEST_CONTAMINATION"}
        res = verify_signal_independence(matches, danger, context)
        assert "error" in res, f"Expected refusal for observer '{bad_obs}'"
        assert res["error"]["code"] == "TWO_SIGNAL_COLLAPSE"  # type: ignore[index]

    # 2. Reject observer matching detector_id (circular self-critique)
    danger_self = {"observer_id": detector_id, "danger_type": "MANIFEST_CONTAMINATION"}
    res_self = verify_signal_independence(matches, danger_self, context)
    assert "error" in res_self
    assert res_self["error"]["code"] == "TWO_SIGNAL_COLLAPSE"  # type: ignore[index]

    # 3. Reject empty/unwitnessed observer
    danger_empty = {"observer_id": "", "danger_type": "MANIFEST_CONTAMINATION"}
    res_empty = verify_signal_independence(matches, danger_empty, context)
    assert "error" in res_empty
    assert res_empty["error"]["code"] == "UNWITNESSED_DANGER_SIGNAL"  # type: ignore[index]
