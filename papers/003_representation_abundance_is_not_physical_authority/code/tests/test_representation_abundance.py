import sys
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mod_representation_abundance_core import (
    CandidateModel,
    DirectedEdge,
    EvidenceRecord,
    FiniteTerminalSelector,
    LandscapeVacuaModel,
    LocalGreenGlobalRedGate,
    ObservableDatum,
    TerminalVerdict,
    WitnessedDifferenceQuotient,
)


class TestObservableAndEvidence:
    """Test exact observable structures."""

    def test_observable_datum_creation(self) -> None:
        obs = ObservableDatum(name="alpha", value=Fraction(1, 137), tolerance=Fraction(1, 10000))
        assert obs.name == "alpha"
        assert obs.value == Fraction(1, 137)
        assert obs.tolerance == Fraction(1, 10000)

    def test_negative_tolerance_raises(self) -> None:
        with pytest.raises(ValueError, match="Tolerance must be non-negative"):
            ObservableDatum(name="bad", value=Fraction(1), tolerance=Fraction(-1))

    def test_evidence_record_from_dict(self) -> None:
        rec = EvidenceRecord.from_dict(
            "ev1",
            {
                "lambda_cc": (Fraction(1, 100), Fraction(1, 1000)),
                "gauge_rank": (4, 0),
            },
        )
        assert rec.record_id == "ev1"
        assert len(rec.observables) == 2
        assert rec.observables["gauge_rank"].value == Fraction(4, 1)
        assert rec.observables["gauge_rank"].tolerance == Fraction(0, 1)

    def test_exact_rational_inputs_enforcement_and_float_rejection(self) -> None:
        """Priority 1: Reject floats to prevent precision drift and parse decimal strings to exact Fractions."""
        # Floating point values are rejected in ObservableDatum
        with pytest.raises(TypeError, match="Floating-point.*rejected"):
            ObservableDatum(name="alpha", value=0.1, tolerance=Fraction(0, 1))

        with pytest.raises(TypeError, match="Floating-point.*rejected"):
            ObservableDatum(name="alpha", value=Fraction(1, 10), tolerance=0.05)

        # Floating point values are rejected in EvidenceRecord.from_dict
        with pytest.raises(TypeError, match="Floating-point.*rejected"):
            EvidenceRecord.from_dict("ev_bad", {"alpha": (0.1, 0)})

        with pytest.raises(TypeError, match="Floating-point.*rejected"):
            EvidenceRecord.from_dict("ev_bad", {"alpha": (1, 0.05)})

        # Floating point values are rejected in CandidateModel.from_dict
        with pytest.raises(TypeError, match="Floating-point.*rejected"):
            CandidateModel.from_dict("cand_bad", {"alpha": 0.1})

        with pytest.raises(TypeError, match="Floating-point.*rejected"):
            CandidateModel.from_dict("cand_bad", {"alpha": 1}, params={"modulus": 0.5})

        # Explicit decimal strings parse into exact Fraction without float inaccuracies:
        # Note: 0.1 + 0.2 in float is 0.30000000000000004 != 0.3
        # In exact Fraction: Fraction("0.1") + Fraction("0.2") == Fraction("0.3") == Fraction(3, 10)
        ev_exact = EvidenceRecord.from_dict("ev_decimal", {"x": ("0.3", "0")})
        c_exact = CandidateModel.from_dict("c_decimal", {"x": Fraction("0.1") + Fraction("0.2")})
        receipt = FiniteTerminalSelector().verify_candidate(ev_exact, c_exact)
        assert receipt.is_consistent is True
        assert receipt.max_discrepancy == Fraction(0, 1)

    def test_certified_evidence_premise_and_certificate_metadata(self) -> None:
        """Priority 3: EvidenceRecord represents an explicitly certified premise with external provenance."""
        ev = EvidenceRecord.from_dict(
            "E_lab_certified",
            {"lambda_cc": ("0.01", "0.001")},
            certificate="sha256:cert_calibration_20261008",
        )
        assert ev.certificate == "sha256:cert_calibration_20261008"
        assert ev.observables["lambda_cc"].value == Fraction(1, 100)


class TestWitnessedDifferenceQuotient:
    """Test quotient space partitioning and underdetermination metrics."""

    def test_quotient_partitioning(self) -> None:
        vacua = LandscapeVacuaModel.standard_five_vacua()
        # Observer only measures lambda_cc and gauge_rank
        quot = WitnessedDifferenceQuotient(["lambda_cc", "gauge_rank"])
        partition = quot.partition_quotient(vacua)

        # Vacua 1, 2, and 5 share lambda_cc = 1/100, gauge_rank = 4
        # Vacuum 3 has lambda_cc = -1/100, gauge_rank = 4
        # Vacuum 4 has lambda_cc = 1/100, gauge_rank = 5
        assert len(partition) == 3
        ratio = quot.underdetermination_ratio(vacua)
        assert ratio == Fraction(5, 3)

    def test_full_observables_partition(self) -> None:
        vacua = LandscapeVacuaModel.standard_five_vacua()
        quot = WitnessedDifferenceQuotient(
            ["lambda_cc", "gauge_rank", "num_generations", "higgs_mass_sq"]
        )
        partition = quot.partition_quotient(vacua)
        # All 5 vacua are distinct under all 4 observables
        assert len(partition) == 5
        assert quot.underdetermination_ratio(vacua) == Fraction(1, 1)

    def test_underdetermination_ratio_rejects_empty_and_duplicate_candidates(self) -> None:
        """Priority 4: Reject empty families and duplicate candidate identifiers."""
        quot = WitnessedDifferenceQuotient(["lambda_cc"])

        # Empty candidate family rejected
        with pytest.raises(ValueError, match="non-empty candidate families"):
            quot.underdetermination_ratio([])

        # Duplicate candidate identifiers rejected
        c1 = CandidateModel.from_dict("V1", {"lambda_cc": 1})
        c1_dup = CandidateModel.from_dict("V1", {"lambda_cc": 1})
        with pytest.raises(ValueError, match="identifiers must be unique"):
            quot.underdetermination_ratio([c1, c1_dup])

        with pytest.raises(ValueError, match="identifiers must be unique"):
            quot.partition_quotient([c1, c1_dup])


class TestFiniteTerminalSelector:
    """Test verification, refutation, and family terminalization."""

    def test_refute_inconsistent_candidate(self) -> None:
        evidence = EvidenceRecord.from_dict(
            "E1",
            {
                "lambda_cc": (Fraction(1, 100), Fraction(1, 1000)),
                "gauge_rank": (4, 0),
            },
        )
        selector = FiniteTerminalSelector()
        v3 = LandscapeVacuaModel.standard_five_vacua()[2]  # lambda_cc = -1/100
        receipt = selector.verify_candidate(evidence, v3)

        assert receipt.is_consistent is False
        assert receipt.verdict == TerminalVerdict.REFUTED
        assert receipt.max_discrepancy == Fraction(2, 100)

    def test_survivor_consistent_candidate(self) -> None:
        evidence = EvidenceRecord.from_dict(
            "E1",
            {
                "lambda_cc": (Fraction(1, 100), Fraction(1, 1000)),
                "gauge_rank": (4, 0),
            },
        )
        selector = FiniteTerminalSelector()
        v1 = LandscapeVacuaModel.standard_five_vacua()[0]
        receipt = selector.verify_candidate(evidence, v1)

        assert receipt.is_consistent is True
        assert receipt.verdict == TerminalVerdict.SURVIVOR
        assert receipt.max_discrepancy == Fraction(0, 1)

    def test_family_underdetermined(self) -> None:
        # Evidence only measures 3 of the 4 observables
        evidence = EvidenceRecord.from_dict(
            "E_partial",
            {
                "lambda_cc": (Fraction(1, 100), Fraction(0, 1)),
                "gauge_rank": (4, 0),
                "num_generations": (3, 0),
            },
        )
        vacua = LandscapeVacuaModel.standard_five_vacua()
        selector = FiniteTerminalSelector()
        result = selector.select_family(evidence, vacua)
        family_verdict, receipts = result.verdict, result.receipts

        # Vacua 1 and 2 both survive
        assert family_verdict == TerminalVerdict.UNDERDETERMINED
        assert receipts["Vacuum_1"].verdict == TerminalVerdict.SURVIVOR
        assert receipts["Vacuum_2"].verdict == TerminalVerdict.SURVIVOR
        assert receipts["Vacuum_3"].verdict == TerminalVerdict.REFUTED
        assert receipts["Vacuum_4"].verdict == TerminalVerdict.REFUTED
        assert receipts["Vacuum_5"].verdict == TerminalVerdict.REFUTED

    def test_family_accepted_when_discriminating_observable_added(self) -> None:
        # Add higgs_mass_sq = 125 to evidence
        evidence = EvidenceRecord.from_dict(
            "E_complete",
            {
                "lambda_cc": (Fraction(1, 100), Fraction(0, 1)),
                "gauge_rank": (4, 0),
                "num_generations": (3, 0),
                "higgs_mass_sq": (125, 0),
            },
        )
        vacua = LandscapeVacuaModel.standard_five_vacua()
        selector = FiniteTerminalSelector()
        result = selector.select_family(evidence, vacua)
        family_verdict, receipts = result.verdict, result.receipts

        assert family_verdict == TerminalVerdict.ACCEPTED
        assert receipts["Vacuum_1"].verdict == TerminalVerdict.SURVIVOR
        assert receipts["Vacuum_2"].verdict == TerminalVerdict.REFUTED

    def test_explicit_zero_tolerance_is_never_overridden(self) -> None:
        evidence = EvidenceRecord.from_dict("exact", {"x": (Fraction(0), Fraction(0))})
        candidate = CandidateModel.from_dict("near", {"x": Fraction(1, 100)})

        receipt = FiniteTerminalSelector().verify_candidate(evidence, candidate)

        assert receipt.verdict == TerminalVerdict.REFUTED
        assert receipt.is_complete is True

    def test_missing_prediction_refuses_instead_of_fabricating_discrepancy(self) -> None:
        evidence = EvidenceRecord.from_dict("required", {"x": (0, 0), "y": (0, 0)})
        candidate = CandidateModel.from_dict("partial", {"x": 0})

        receipt = FiniteTerminalSelector().verify_candidate(evidence, candidate)
        result = FiniteTerminalSelector().select_family(evidence, [candidate])
        verdict, receipts = result.verdict, result.receipts

        assert receipt.verdict == TerminalVerdict.REFUSED
        assert receipt.max_discrepancy == Fraction(0)
        assert receipt.is_complete is False
        assert verdict == TerminalVerdict.REFUSED
        assert receipts["partial"].verdict == TerminalVerdict.REFUSED

    def test_empty_evidence_and_duplicate_identifiers_cannot_authorize(self) -> None:
        candidate = CandidateModel.from_dict("same", {"x": 0})
        empty = EvidenceRecord.from_dict("empty", {})

        result = FiniteTerminalSelector().select_family(empty, [candidate])
        verdict, receipts = result.verdict, result.receipts
        assert verdict == TerminalVerdict.REFUSED
        assert receipts["same"].verdict == TerminalVerdict.REFUSED

        with pytest.raises(ValueError, match="identifiers must be unique"):
            FiniteTerminalSelector().select_family(empty, [candidate, candidate])


class TestLocalGreenGlobalRedGate:
    """Test cochain complex evaluations, False-Green conditions, and cycle holonomies."""

    def setup_method(self) -> None:
        # 6-vertex directed cycle (hexagon): 0->1, 1->2, 2->3, 3->4, 4->5, 5->0
        self.edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]
        self.gate = LocalGreenGlobalRedGate(num_vertices=6, edges=self.edges)
        self.cycle = [(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 5, 1), (5, 0, 1)]

    def test_evaluator_soundness_on_coboundaries(self) -> None:
        """For any 0-cochain f in C^0(V), the cycle holonomy of d_0 f is identically zero."""
        vertex_field = {
            0: Fraction(1, 2),
            1: Fraction(7, 3),
            2: Fraction(-4, 5),
            3: Fraction(11, 7),
            4: Fraction(0, 1),
            5: Fraction(3, 4),
        }
        assert self.gate.check_evaluator_soundness(vertex_field, self.cycle) is True

    def test_false_green_cycle_obstruction(self) -> None:
        """Construct a 1-cochain that is Local-Green on all edges, yet obstructed on the global cycle."""
        # Each edge has local discrepancy 1/10
        edge_field = {
            DirectedEdge(0, 1): Fraction(1, 10),
            DirectedEdge(1, 2): Fraction(1, 10),
            DirectedEdge(2, 3): Fraction(1, 10),
            DirectedEdge(3, 4): Fraction(1, 10),
            DirectedEdge(4, 5): Fraction(1, 10),
            DirectedEdge(5, 0): Fraction(1, 10),
        }
        # Local tolerance on each edge is 1/5 (so 1/10 < 1/5 => Local Green passes)
        tolerances = {edge: Fraction(1, 5) for edge in edge_field}

        assert self.gate.evaluate_local_green(edge_field, tolerances) is True

        # But global cycle holonomy is 6 * 1/10 = 3/5 != 0 (Global Red!)
        holonomy = self.gate.cycle_holonomy(edge_field, self.cycle)
        assert holonomy == Fraction(3, 5)
        assert holonomy != Fraction(0, 1)

    def test_graph_evaluator_input_contract_and_incomplete_records(self) -> None:
        """Priority 2: Refuse incomplete records by default; declare intentional sparse-zero convention."""
        # Empty edge_field and tolerances on nonempty graph refuse by default
        with pytest.raises(ValueError, match="Incomplete edge_field"):
            self.gate.evaluate_local_green({}, {})

        # Missing tolerance refuses
        complete_field = {edge: Fraction(1, 10) for edge in self.gate.edges}
        with pytest.raises(ValueError, match="Incomplete tolerances"):
            self.gate.evaluate_local_green(complete_field, {})

        # Intentional sparse-zero convention allowed when explicitly enabled
        assert self.gate.evaluate_local_green({}, {}, allow_sparse_default=True) is True

        # Negative tolerance raises
        complete_tols = {edge: Fraction(-1, 5) for edge in self.gate.edges}
        with pytest.raises(ValueError, match="Negative tolerance"):
            self.gate.evaluate_local_green(complete_field, complete_tols)

    def test_cycle_validation_closure_and_graph_edges(self) -> None:
        """Priority 2: Validate cycle is non-empty, uses graph edges, and is strictly closed."""
        # Empty cycle
        with pytest.raises(ValueError, match="Cycle must be non-empty"):
            self.gate.validate_cycle([])

        # Edge not in graph
        with pytest.raises(ValueError, match="not an edge in the graph"):
            self.gate.validate_cycle([(0, 99, 1)])

        # Open path (not closed)
        open_path = [(0, 1, 1), (1, 2, 1)]
        with pytest.raises(ValueError, match="Cycle is not closed"):
            self.gate.validate_cycle(open_path)

        # Evaluator soundness refuses unclosed cycle
        vertex_field = {i: Fraction(i, 1) for i in range(6)}
        with pytest.raises(ValueError, match="Cycle is not closed"):
            self.gate.check_evaluator_soundness(vertex_field, open_path)

        # cycle_holonomy refuses unclosed cycle
        edge_field = {edge: Fraction(1, 10) for edge in self.gate.edges}
        with pytest.raises(ValueError, match="Cycle is not closed"):
            self.gate.cycle_holonomy(edge_field, open_path)


class TestRepresentationPlenitudeVsAuthority:
    """Stress test showing that generating 1000 vacua increases underdetermination, not authority."""

    def test_plenitude_increases_underdetermination(self) -> None:
        base_vacua = []
        for i in range(100):
            # 100 vacua with identical standard observables but varying hidden internal parameters
            base_vacua.append(
                CandidateModel.from_dict(
                    candidate_id=f"Vac_{i}",
                    predictions={
                        "lambda_cc": Fraction(1, 100),
                        "gauge_rank": Fraction(4, 1),
                        "num_generations": Fraction(3, 1),
                    },
                    params={"hidden_modulus": Fraction(i, 1)},
                )
            )

        evidence = EvidenceRecord.from_dict(
            "E_standard",
            {
                "lambda_cc": (Fraction(1, 100), Fraction(0, 1)),
                "gauge_rank": (4, 0),
                "num_generations": (3, 0),
            },
        )

        selector = FiniteTerminalSelector()
        result = selector.select_family(evidence, base_vacua)
        family_verdict, receipts = result.verdict, result.receipts

        # Despite generating 100 candidate universes, the family is strictly underdetermined
        assert family_verdict == TerminalVerdict.UNDERDETERMINED
        assert len([r for r in receipts.values() if r.verdict == TerminalVerdict.SURVIVOR]) == 100

        # The quotient underdetermination ratio is exactly 100/1
        quot = WitnessedDifferenceQuotient(["lambda_cc", "gauge_rank", "num_generations"])
        assert quot.underdetermination_ratio(base_vacua) == Fraction(100, 1)


class TestProvedFiniteClaims:
    """Calls the shipped checkers for the six proved finite statements."""

    def test_observation_decision_agrees_only_on_a_shared_profile(self) -> None:
        vacua = LandscapeVacuaModel.standard_five_vacua()
        blind = WitnessedDifferenceQuotient(["lambda_cc", "gauge_rank", "num_generations"])
        assert (
            blind.observation_decision_agrees(vacua[0], vacua[1], lambda profile: profile[0][1])
            is True
        )
        sharp = WitnessedDifferenceQuotient(
            ["lambda_cc", "gauge_rank", "num_generations", "higgs_mass_sq"]
        )
        assert (
            sharp.observation_decision_agrees(vacua[0], vacua[1], lambda profile: profile) is False
        )

    def test_plenitude_inflates_only_when_no_new_profile_appears(self) -> None:
        quot = WitnessedDifferenceQuotient(["x"])
        first = CandidateModel.from_dict("a", {"x": Fraction(1)})
        second = CandidateModel.from_dict("b", {"x": Fraction(1)})
        third = CandidateModel.from_dict("c", {"x": Fraction(1)})
        novel = CandidateModel.from_dict("d", {"x": Fraction(2)})
        assert quot.plenitude_inflates([first, second], [first, second, third]) is True
        assert quot.plenitude_inflates([first, second], [first, second, novel]) is False

    def test_false_green_witness_and_cycle_defect_bound(self) -> None:
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]
        gate = LocalGreenGlobalRedGate(num_vertices=6, edges=edges)
        cycle = [(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 5, 1), (5, 0, 1)]
        tolerances = {edge: Fraction(1, 5) for edge in gate.edges}
        assert gate.false_green_witness(cycle, tolerances) is True
        zero = dict(tolerances)
        zero[gate.edges[0]] = Fraction(0)
        assert gate.false_green_witness(cycle, zero) is False

        field = {edge: Fraction(1, 10) for edge in gate.edges}
        assert gate.cycle_defect_within_tolerance_sum(field, tolerances, cycle) is True
        assert gate.sharp_cycle_attains_tolerance_sum(tolerances, cycle) is True
        assert (
            gate.cycle_defect_within_tolerance_sum(field, tolerances, [(0, 1, 1), (1, 2, 1)])
            is False
        )

    def test_unique_acceptance_is_relative_to_the_declared_family(self) -> None:
        vacua = LandscapeVacuaModel.standard_five_vacua()
        evidence = EvidenceRecord.from_dict(
            "partial",
            {
                "lambda_cc": (Fraction(1, 100), Fraction(0)),
                "gauge_rank": (4, 0),
                "num_generations": (3, 0),
            },
        )
        selector = FiniteTerminalSelector()
        assert (
            selector.acceptance_relaxes_when_another_survivor_joins(evidence, [vacua[0]], vacua[1])
            is True
        )
        assert (
            selector.acceptance_relaxes_when_another_survivor_joins(evidence, [vacua[0]], vacua[2])
            is False
        )


class TestRepublicationRegressions:
    def test_reverse_extra_cannot_bypass_local_cochain_domain(self) -> None:
        gate = LocalGreenGlobalRedGate(3, [(0, 1), (1, 2), (2, 0)])
        field = {edge: Fraction(0) for edge in gate.edges}
        tolerances = {edge: Fraction(1) for edge in gate.edges}
        field[DirectedEdge(1, 0)] = Fraction(99)
        with pytest.raises(ValueError, match="Noncanonical"):
            gate.evaluate_local_green(field, tolerances)

    def test_zero_tolerances_attain_cycle_bound(self) -> None:
        gate = LocalGreenGlobalRedGate(3, [(0, 1), (1, 2), (2, 0)])
        assert gate.sharp_cycle_attains_tolerance_sum(
            {edge: Fraction(0) for edge in gate.edges},
            [(0, 1, 1), (1, 2, 1), (2, 0, 1)],
        )

    def test_plenitude_rejects_swapped_retained_predictions(self) -> None:
        quotient = WitnessedDifferenceQuotient(["x"])
        old = [CandidateModel.from_dict("a", {"x": 0}), CandidateModel.from_dict("b", {"x": 1})]
        swapped = [
            CandidateModel.from_dict("a", {"x": 1}),
            CandidateModel.from_dict("b", {"x": 0}),
            CandidateModel.from_dict("c", {"x": 0}),
        ]
        assert not quotient.plenitude_inflates(old, swapped)

    def test_family_acceptance_preserves_candidate_survivor_status(self) -> None:
        evidence = EvidenceRecord.from_dict("record", {"x": (0, 0)})
        candidate = CandidateModel.from_dict("a", {"x": 0})
        result = FiniteTerminalSelector().select_family(evidence, [candidate])
        assert result.verdict == TerminalVerdict.ACCEPTED
        assert result.evidence_record_id == "record"
        assert result.candidate_ids == ("a",)
        assert result.selected_candidate_id == "a"
        receipts = result.receipts
        assert receipts["a"].evidence_record_id == "record"
        assert receipts["a"].verdict == TerminalVerdict.SURVIVOR

    def test_equivalent_signed_presentations_and_reversed_traversal(self) -> None:
        gate = LocalGreenGlobalRedGate(3, [(0, 1), (1, 2), (2, 0)])
        field = {e: Fraction(i + 1, 7) for i, e in enumerate(gate.edges)}
        ordinary = [(0, 1, 1), (1, 2, 1), (2, 0, 1)]
        reexpressed = [(1, 0, -1), (1, 2, 1), (2, 0, 1)]
        reverse = [(0, 2, 1), (2, 1, 1), (1, 0, 1)]
        assert gate.cycle_holonomy(field, ordinary) == Fraction(6, 7)
        assert gate.cycle_holonomy(field, ordinary) == gate.cycle_holonomy(field, reexpressed)
        assert gate.cycle_holonomy(field, reverse) == Fraction(-6, 7)
        caps = {e: Fraction(1) for e in gate.edges}
        assert gate.sharp_cycle_attains_tolerance_sum(caps, reexpressed)
        assert gate.false_green_witness(reexpressed, caps)
        field[DirectedEdge(1, 0)] = Fraction(99)
        with pytest.raises(ValueError, match="Noncanonical"):
            gate.cycle_holonomy(field, reexpressed)
        caps[DirectedEdge(1, 0)] = Fraction(1)
        with pytest.raises(ValueError, match="Noncanonical"):
            gate.evaluate_local_green({e: 0 for e in gate.edges}, caps)

    def test_backtracking_bound_holds_but_sharpness_contract_refuses(self) -> None:
        gate = LocalGreenGlobalRedGate(3, [(0, 1), (1, 2)])
        walk = [(0, 1, 1), (1, 2, 1), (1, 2, -1), (0, 1, -1)]
        caps = {e: Fraction(1) for e in gate.edges}
        field = {e: Fraction(1, 2) for e in gate.edges}
        assert gate.cycle_holonomy(field, walk) == 0
        assert gate.cycle_defect_within_tolerance_sum(field, caps, walk)
        assert not gate.sharp_cycle_attains_tolerance_sum(caps, walk)
        assert not gate.false_green_witness(walk, caps)

    def test_retained_identity_includes_hidden_model_content(self) -> None:
        quotient = WitnessedDifferenceQuotient(["x"])
        first = CandidateModel.from_dict("a", {"x": 0}, {"hidden": 1})
        changed = CandidateModel.from_dict("a", {"x": 0}, {"hidden": 2})
        extra = CandidateModel.from_dict("b", {"x": 0})
        assert not quotient.plenitude_inflates([first], [changed, extra])
        assert quotient.plenitude_inflates([first], [first, extra])
        with pytest.raises(TypeError):
            first.predictions["x"] = Fraction(99)

    def test_family_context_changes_without_promoting_receipt(self) -> None:
        evidence = EvidenceRecord.from_dict("record", {"x": (0, 0)})
        a = CandidateModel.from_dict("a", {"x": 0})
        b = CandidateModel.from_dict("b", {"x": 0})
        selector = FiniteTerminalSelector()
        unique = selector.select_family(evidence, [a])
        enlarged = selector.select_family(evidence, [a, b])
        assert unique.receipts["a"] == enlarged.receipts["a"]
        assert enlarged.verdict == TerminalVerdict.UNDERDETERMINED
        assert enlarged.candidate_ids == ("a", "b")
        assert enlarged.selected_candidate_id is None
        assert {a.predictions["x"], b.predictions["x"]} == {Fraction(0)}
        empty = selector.select_family(evidence, [])
        assert empty.verdict == TerminalVerdict.REFUSED
        assert empty.candidate_ids == ()
        with pytest.raises(TypeError):
            unique.receipts["b"] = enlarged.receipts["b"]

    def test_graph_domain_rejects_ambiguous_edge_storage(self) -> None:
        for edges in ([(0, 1), (1, 0)], [(0, 1), (0, 1)], [(0, 0)]):
            with pytest.raises(ValueError, match="one orientation"):
                LocalGreenGlobalRedGate(2, edges)
        with pytest.raises(ValueError, match="indices"):
            LocalGreenGlobalRedGate(2, [(0, 2)])
        with pytest.raises(TypeError, match="Boolean"):
            CandidateModel.from_dict("boolean", {"x": True})
