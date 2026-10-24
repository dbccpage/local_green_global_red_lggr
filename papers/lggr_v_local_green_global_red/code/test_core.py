import numpy as np
import pytest
from code_core import (
    Assignment,
    Evaluator,
    EvaluatorFamily,
    Interface,
    NormType,
    Site,
    System,
    compute_defect,
    compute_global_inconsistency,
    compute_norm,
    scaled_euclidean_norm,
)


def test_compute_norm():
    v = np.array([3.0, -4.0])
    assert compute_norm(v, NormType.L1) == 7.0
    assert compute_norm(v, NormType.L2) == 5.0
    assert compute_norm(v, NormType.LINF) == 4.0
    assert compute_norm(np.array([]), NormType.L1) == 0.0
    assert scaled_euclidean_norm(np.array([])) == 0.0

    # Scaled Euclidean norm without underflow or overflow
    assert compute_norm(np.array([5e-200]), NormType.L2) == pytest.approx(5e-200)
    assert compute_norm(np.array([1e200]), NormType.L2) == pytest.approx(1e200)
    assert compute_norm(np.array([0.0, 0.0]), NormType.L2) == 0.0

    # Unrepresentable norms exceeding float range must raise ValueError
    with pytest.raises(ValueError, match="Computed norm is non-finite"):
        compute_norm(np.array([1e308, 1e308]), NormType.L1)
    with pytest.raises(ValueError, match="Computed Euclidean norm is non-finite"):
        compute_norm(np.array([1.5e308, 1.5e308]), NormType.L2)

    with pytest.raises(ValueError, match="Unsupported norm type"):
        compute_norm(v, "INVALID_NORM")  # type: ignore


def test_site_creation_and_validation():
    s = Site("alpha", 3, NormType.L1)
    assert s.name == "alpha"
    assert s.dimension == 3
    assert s.norm_type == NormType.L1

    with pytest.raises(ValueError, match="Site dimension must be.*>= 1"):
        Site("bad", 0)



def test_interface_and_defect():
    mat = np.array([[1.0, 0.0], [0.0, 1.0]])
    iface = Interface("e1", "siteA", "siteB", mat, NormType.L1)

    sb = np.array([2.0, 3.0])
    sa = np.array([1.0, 1.0])
    d = iface.compute_defect(sa, sb)
    np.testing.assert_array_equal(d, np.array([1.0, 2.0]))

    # Test translate
    translated = iface.translate(sb)
    np.testing.assert_array_equal(translated, sb)


def test_assignment():
    a = Assignment()
    a.set_state("siteA", [1.0, 2.0])
    np.testing.assert_array_equal(a.get_state("siteA"), np.array([1.0, 2.0]))

    with pytest.raises(KeyError, match="Site 'siteB' not assigned"):
        a.get_state("siteB")


def test_compute_defect_and_global_inconsistency():
    mat = np.eye(2)
    iface1 = Interface("e1", "s1", "s2", mat, NormType.L1)
    iface2 = Interface("e2", "s2", "s3", mat, NormType.L1)

    a = Assignment()
    a.set_state("s1", [1.0, 0.0])
    a.set_state("s2", [2.0, 1.0])
    a.set_state("s3", [0.0, 0.0])

    d1 = compute_defect(iface1, a)
    np.testing.assert_array_equal(d1, [1.0, 1.0])

    inconsistency = compute_global_inconsistency({"e1": iface1, "e2": iface2}, a)
    assert inconsistency == 5.0

    # Test accumulated global inconsistency overflow
    if_ovf1 = Interface("o1", "s1", "s2", np.eye(1), NormType.L1)
    if_ovf2 = Interface("o2", "s2", "s3", np.eye(1), NormType.L1)
    a_ovf = Assignment()
    a_ovf.set_state("s1", [0.0])
    a_ovf.set_state("s2", [1.5e308])
    a_ovf.set_state("s3", [0.0])
    with pytest.raises(ValueError, match="Accumulated global inconsistency is non-finite"):
        compute_global_inconsistency({"o1": if_ovf1, "o2": if_ovf2}, a_ovf)


def test_evaluator_and_family():
    q = np.array([[1.0, 0.0]])
    ev = Evaluator(
        name="ev1",
        watched_interfaces=["e1"],
        measurement_matrices={"e1": q},
        value_norms={"e1": NormType.L1}
    )

    d = np.array([3.0, 4.0])
    measured = ev.measure_defect("e1", d)
    np.testing.assert_array_equal(measured, [3.0])

    with pytest.raises(KeyError, match="not watched by evaluator"):
        ev.measure_defect("e_unknown", d)

    iface1 = Interface("e1", "s1", "s2", np.eye(2), NormType.L1)
    a = Assignment()
    a.set_state("s1", [0.0, 0.0])
    a.set_state("s2", [3.0, 4.0])

    score = ev.compute_score({"e1": iface1}, a)
    assert score == 3.0

    # Test accumulated evaluator score overflow
    ev_ovf = Evaluator(
        name="ev_ovf",
        watched_interfaces=["e1", "e2"],
        measurement_matrices={"e1": np.eye(1), "e2": np.eye(1)},
    )
    if1 = Interface("e1", "s1", "s2", np.eye(1))
    if2 = Interface("e2", "s2", "s3", np.eye(1))
    a_sc = Assignment()
    a_sc.set_state("s1", [0.0])
    a_sc.set_state("s2", [1.5e308])
    a_sc.set_state("s3", [0.0])
    with pytest.raises(ValueError, match="Accumulated evaluator score is non-finite"):
        ev_ovf.compute_score({"e1": if1, "e2": if2}, a_sc)

    fam = EvaluatorFamily()
    fam.add_evaluator(ev)
    scores = fam.compute_all_scores({"e1": iface1}, a)
    assert scores == {"ev1": 3.0}
    assert not fam.is_all_green({"e1": iface1}, a)


def test_system_validation_and_methods():
    sys = System()
    s1 = Site("s1", 2)
    s2 = Site("s2", 2)
    sys.add_site(s1)
    sys.add_site(s2)

    iface = Interface("e1", "s1", "s2", np.eye(2))
    sys.add_interface(iface)

    with pytest.raises(ValueError, match="Interface sites must exist"):
        sys.add_interface(Interface("e_bad", "s1", "s_missing", np.eye(2)))

    bad_ev = Evaluator("bad_ev", ["e_missing"], {"e_missing": np.eye(2)})
    with pytest.raises(ValueError, match="watches non-existent interface"):
        sys.add_evaluator(bad_ev)

    valid_ev = Evaluator("ev1", ["e1"], {"e1": np.eye(2)})
    sys.add_evaluator(valid_ev)

    a = Assignment()
    a.set_state("s1", [0.0, 0.0])
    a.set_state("s2", [0.0, 0.0])

    assert sys.global_inconsistency(a) == 0.0
    assert sys.is_all_green(a)
    assert sys.evaluator_scores(a) == {"ev1": 0.0}


def test_evaluator_and_system_invariants_and_validations():
    # Duplicate watched interface check (F5)
    with pytest.raises(ValueError, match="watched_interfaces contains duplicate entries"):
        Evaluator("dup_ev", ["e1", "e1"], {"e1": np.eye(1)})

    # Missing measurement matrix
    with pytest.raises(ValueError, match="lacks a corresponding measurement matrix"):
        Evaluator("missing_ev", ["e1", "e2"], {"e1": np.eye(1)})

    # Non-finite measurement matrix
    with pytest.raises(ValueError, match="contains non-finite values"):
        Evaluator("nan_ev", ["e1"], {"e1": np.array([[float("nan")]])})

    sys = System()
    sys.add_site(Site("s1", 2))
    sys.add_site(Site("s2", 3))

    # Interface translation matrix dimension mismatch
    with pytest.raises(ValueError, match="does not match site dimensions"):
        sys.add_interface(Interface("e_bad_dim", "s1", "s2", np.eye(2)))  # Expected (2, 3)

    # Non-finite interface translation matrix
    bad_mat = np.zeros((2, 3))
    bad_mat[0, 0] = float("inf")
    with pytest.raises(ValueError, match="contains non-finite values"):
        sys.add_interface(Interface("e_inf", "s1", "s2", bad_mat))

    # Valid interface
    valid_mat = np.zeros((2, 3))
    sys.add_interface(Interface("e_valid", "s1", "s2", valid_mat))

    # Evaluator measurement column dimension mismatch
    with pytest.raises(ValueError, match="has column dimension"):
        sys.add_evaluator(Evaluator("ev_col_bad", ["e_valid"], {"e_valid": np.eye(3)}))  # Expected col dim 2 (dim of s1)


def test_site_and_compute_norm_validation():
    """Item 6 Regression: Validate site dimensions and vector norm dimensionality/finiteness."""
    with pytest.raises(ValueError, match="positive integer"):
        Site("s_bad", 0)
    with pytest.raises(ValueError, match="positive integer"):
        Site("s_bad", -2)
    with pytest.raises(ValueError, match="positive integer"):
        Site("s_bad", True)  # bool is subclass of int

    # compute_norm rejecting 2D matrices and non-finite entries
    with pytest.raises(ValueError, match="Expected 1D vector"):
        from code_core import compute_norm
        compute_norm(np.eye(2))
    with pytest.raises(ValueError, match="non-finite values"):
        from code_core import compute_norm
        compute_norm(np.array([1.0, float("nan")]))


def test_interface_norm_mismatch_rejection():
    """Item 6 Regression: Reject interface norm mismatching target site declared norm."""
    sys = System()
    sys.add_site(Site("s1", 2, norm_type=NormType.L2))
    sys.add_site(Site("s2", 2, norm_type=NormType.L1))

    iface_bad_norm = Interface("e", "s1", "s2", np.eye(2), norm_type=NormType.L1)
    with pytest.raises(ValueError, match="does not match target site"):
        sys.add_interface(iface_bad_norm)


def test_assignment_shape_and_finiteness_validation():
    """Item 6 Regression: Validate state dimensions, reject broadcasting and non-finite inputs."""
    sys = System()
    sys.add_site(Site("s1", 2))
    sys.add_site(Site("s2", 2))
    sys.add_interface(Interface("e", "s1", "s2", np.eye(2)))
    sys.add_evaluator(Evaluator("ev", ["e"], {"e": np.eye(2)}))

    # Wrong shape (broadcasting attempt: target state [1.0] vs dimension 2)
    a_wrong = Assignment()
    with pytest.raises(ValueError, match="1D state of shape"):
        a_wrong.set_state("s1", [1.0])
        a_wrong.set_state("s2", [1.0, 1.0])
        sys.global_inconsistency(a_wrong)

    # 2D matrix state attempt
    a_2d = Assignment()
    with pytest.raises(ValueError, match="must be a 1D vector"):
        a_2d.set_state("s1", [[1.0, 1.0]])

    # Non-finite assignment (NaN / Inf)
    a_nan = Assignment()
    with pytest.raises(ValueError, match="contains non-finite values"):
        a_nan.set_state("s1", [float("nan"), 1.0])

    # Non-finite injected after construction
    a_mutated = Assignment()
    a_mutated.states["s1"] = np.array([float("nan"), 1.0])
    a_mutated.states["s2"] = np.array([1.0, 1.0])
    with pytest.raises(ValueError, match="non-finite"):
        sys.global_inconsistency(a_mutated)
    with pytest.raises(ValueError, match="non-finite"):
        sys.evaluator_scores(a_mutated)

    # Missing site in validate_against_sites
    a_incomplete = Assignment()
    a_incomplete.set_state("s1", [1.0, 1.0])
    with pytest.raises(ValueError, match="missing from assignment"):
        sys.global_inconsistency(a_incomplete)

    # Interface validation
    with pytest.raises(ValueError, match="translation matrix must be 2D"):
        Interface("bad_iface", "s1", "s2", np.array([1.0, 2.0]))

    iface_ok = Interface("iface_ok", "s1", "s2", np.eye(2))
    with pytest.raises(ValueError, match="expected source state dimension"):
        iface_ok.translate(np.ones((2, 2)))
    with pytest.raises(ValueError, match="contains non-finite values"):
        iface_ok.translate(np.array([1.0, np.nan]))

    with pytest.raises(ValueError, match="expected target state dimension"):
        iface_ok.compute_defect(np.ones(3), np.ones(2))
    with pytest.raises(ValueError, match="contains non-finite values"):
        iface_ok.compute_defect(np.array([1.0, np.nan]), np.ones(2))

    # Evaluator measurement matrix 2D validation
    with pytest.raises(ValueError, match="must be 2D"):
        Evaluator("bad_ev", ["iface_ok"], {"iface_ok": np.array([1.0, 2.0])})

    ev_ok = Evaluator("ev_ok", ["iface_ok"], {"iface_ok": np.eye(2)})
    with pytest.raises(ValueError, match="expects input dimension"):
        ev_ok.measure_defect("iface_ok", np.ones(3))
    with pytest.raises(ValueError, match="contains non-finite values"):
        ev_ok.measure_defect("iface_ok", np.array([1.0, np.nan]))



