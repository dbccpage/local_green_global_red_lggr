"""Unit tests for LGGR IV Core Mathematical Apparatus."""

from __future__ import annotations

from fractions import Fraction
import pytest

from lggr_iv_core import (
    WitnessClassification,
    compute_x_n,
    verify_finite_stage,
    verify_compatibility,
    get_residue_thread,
    find_failing_stage_for_integer,
    p_adic_valuation_2,
    adic_distance_to_completion_solution,
    classify_rational_witness,
    find_moving_witness_collision,
    try_stage_factor,
    descent_collision_iff,
)


def test_first_few_terms():
    """Verify hand-calculated terms for n = 0, 1, 2, 3, 4, 5."""
    assert compute_x_n(0) == 0
    assert compute_x_n(-1) == 0
    assert compute_x_n(1) == -1
    assert compute_x_n(2) == 1
    assert compute_x_n(3) == -3
    assert compute_x_n(4) == 5
    assert compute_x_n(5) == -11


def test_finite_stage_identity_and_divisibility():
    """Test M3: 3*x_n + 1 = (-2)^n and 2^n | (3*x_n + 1) for stages 1 to 50."""
    for n in range(1, 51):
        rec = verify_finite_stage(n)
        assert rec.is_exact_identity, f"Exact identity failed at stage {n}"
        assert rec.is_locally_green, f"Local green divisibility failed at stage {n}"
        assert rec.lhs == 3 * rec.x_n + 1
        assert rec.rhs == (-2) ** n
        assert rec.lhs == rec.rhs
        assert rec.lhs % rec.modulus == 0


def test_stage_compatibility():
    """Test M4: x_{n+1} = x_n (mod 2^n) for stages 1 to 50."""
    for n in range(1, 51):
        diff, modulus, is_comp = verify_compatibility(n)
        assert is_comp, f"Compatibility failed at stage {n}"
        assert diff == -((-2) ** n)
        assert diff % modulus == 0


def test_residue_thread():
    """Verify the residue thread (x_n mod 2^n) and canonical projection consistency."""
    residues = get_residue_thread(10)
    assert len(residues) == 10

    # Specific canonical values
    assert residues[0] == 1  # -1 mod 2 = 1
    assert residues[1] == 1  # 1 mod 4 = 1
    assert residues[2] == 5  # -3 mod 8 = 5
    assert residues[3] == 5  # 5 mod 16 = 5
    assert residues[4] == 21  # -11 mod 32 = 21

    # Projection consistency: res_{n+1} mod 2^n == res_n
    for n in range(len(residues) - 1):
        mod_curr = 2 ** (n + 1)
        assert residues[n + 1] % mod_curr == residues[n]


def test_integral_global_red():
    """Test M5: Every integer in [-1000, 1000] fails at some finite stage."""
    for x in range(-1000, 1001):
        failing_stage = find_failing_stage_for_integer(x, search_limit=20)
        assert failing_stage is not None, f"Integer {x} unexpectedly passed all stages!"
        # Verify it actually fails at failing_stage
        mod = 2**failing_stage
        assert (3 * x + 1) % mod != 0

    # Search limit bounded test
    assert find_failing_stage_for_integer(1, search_limit=0) is None


def test_p_adic_valuation_and_distance():
    """Test 2-adic valuation and metric distance convergence to -1/3."""
    assert p_adic_valuation_2(1) == 0
    assert p_adic_valuation_2(2) == 1
    assert p_adic_valuation_2(12) == 2
    assert p_adic_valuation_2(16) == 4
    assert p_adic_valuation_2(-8) == 3

    with pytest.raises(ValueError, match="infinity"):
        p_adic_valuation_2(0)

    for n in range(1, 20):
        dist = adic_distance_to_completion_solution(n)
        assert dist == Fraction(1, 2**n)


def test_reflection_descent_classification():
    """Test M7: Reflection descent classifies -1/3 as COMPLETION_ONLY."""
    # -1/3 is the exact solution to 3x + 1 = 0
    sol = Fraction(-1, 3)
    cls = classify_rational_witness(sol)
    assert cls == WitnessClassification.COMPLETION_ONLY

    # Non-solution
    assert classify_rational_witness(Fraction(1, 3)) == WitnessClassification.INVALID

    # Even denominator cannot be a 2-adic integer
    assert classify_rational_witness(Fraction(1, 2)) == WitnessClassification.INVALID

    # An integer solution to some other equation with reflection
    # E.g. x - 5 = 0 -> solution is 5/1 in Z
    int_sol = Fraction(5, 1)
    cls_int = classify_rational_witness(int_sol, equation_lhs=lambda z: z - 5)
    assert cls_int == WitnessClassification.ORIGINAL_CARRIER


def test_moving_witness_collision():
    """Test M1 / D1: Moving-witness collision detection when a defect does not factor through stage n."""
    for n in range(1, 6):
        def proj(x: int, stage_n: int = n) -> int:
            return x % (2**stage_n)

        def defect(x: int, stage_n: int = n) -> int:
            return (3 * x + 1) % (2 ** (stage_n + 1))

        search = list(range(0, 2 ** (n + 2)))

        collision = find_moving_witness_collision(
            stage=n,
            projection=proj,
            defect_fn=defect,
            search_space=search,
        )
        assert collision is not None
        assert collision.projected_x == collision.projected_y
        assert collision.defect_x != collision.defect_y

    # Test case where defect does factor: no collision found (returns None)
    # E.g. projection is x % 4, defect is (2*x) % 4 which factors through x % 4
    def factored_proj(x: int) -> int:
        return x % 4

    def factored_defect(x: int) -> int:
        return (2 * (x % 4)) % 4
    # Also includes items that share projection and share defect
    no_collision = find_moving_witness_collision(
        stage=2,
        projection=factored_proj,
        defect_fn=factored_defect,
        search_space=[0, 4, 8, 1, 5, 2, 6, 3, 7],
    )
    assert no_collision is None


def test_finite_descent_moving_witnesses():
    """M1 on a finite complete list: descent failure matches a collision at every stage."""
    for n in range(1, 6):
        def proj(x: int, stage_n: int = n) -> int:
            return x % (2**stage_n)

        def defect(x: int, stage_n: int = n) -> int:
            return (3 * x + 1) % (2 ** (stage_n + 1))

        states = list(range(0, 2 ** (n + 2)))
        report = descent_collision_iff([proj], defect, states, default=0)
        assert report.not_finite_descent
        assert report.every_stage_collides
        assert report.agrees
        assert try_stage_factor(proj, defect, states, default=0) is None

    states = [0, 4, 8, 1, 5, 2, 6, 3, 7]

    def factored_proj(x: int) -> int:
        return x % 4

    def factored_defect(x: int) -> int:
        return (2 * (x % 4)) % 4

    factored = descent_collision_iff([factored_proj], factored_defect, states, default=0)
    assert not factored.not_finite_descent
    assert not factored.every_stage_collides
    assert factored.agrees
    stage_map = try_stage_factor(factored_proj, factored_defect, states, default=9)
    assert stage_map is not None
    assert stage_map(0) == factored_defect(0)
    assert stage_map(7) == 9

    empty_states = descent_collision_iff([factored_proj], factored_defect, [], default=5)
    assert not empty_states.not_finite_descent
    assert not empty_states.every_stage_collides
    assert empty_states.agrees
    empty_map = try_stage_factor(factored_proj, factored_defect, [], default=5)
    assert empty_map is not None
    assert empty_map(3) == 5

    empty_family = descent_collision_iff([], factored_defect, states, default=0)
    assert empty_family.not_finite_descent
    assert empty_family.every_stage_collides
    assert empty_family.agrees

    def identity_defect(x: int) -> int:
        return x

    moving = [0, 1, 2]
    both_stages = descent_collision_iff(
        [lambda x: 0, lambda x: x % 2],
        identity_defect,
        moving,
        default=0,
    )
    assert both_stages.not_finite_descent
    assert both_stages.every_stage_collides
    assert both_stages.agrees


def test_invalid_input_guards():
    """Test exception raising on malformed or non-positive stages."""
    with pytest.raises(ValueError, match="Stage n must be >= 1"):
        verify_finite_stage(0)

    with pytest.raises(ValueError, match="Stage n must be >= 1"):
        verify_compatibility(0)

    with pytest.raises(ValueError, match="Stage n must be >= 1"):
        adic_distance_to_completion_solution(0)
