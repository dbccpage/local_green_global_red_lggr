# Claim Hygiene: AuthorityEffect: None
# Tests verify Lean 4 compilation, axiom audit, structural integrity, and theorems.
from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CODE_DIR = PACKAGE_ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))


def _lean_workdir(lean_dir: Path) -> Path:
    trace = lean_dir / ".lake" / "config" / "0" / "lakefile.olean.trace"
    if len(str(trace)) < 250:
        return lean_dir
    short = Path(tempfile.gettempdir()) / "rsi012-lean"
    if short.exists():
        shutil.rmtree(short)
    shutil.copytree(lean_dir, short, ignore=shutil.ignore_patterns(".lake"))
    return short


def test_rsi_impossible_lean_compilation_and_axioms() -> None:
    lean4_dir = PACKAGE_ROOT / "lean4"
    for fname in ("RsiImpossible.lean", "RelationalRsiNoGo.lean", "Census.lean"):
        fpath = lean4_dir / fname
        assert fpath.exists(), f"Lean file not found at {fpath}"
        source_text = fpath.read_text(encoding="utf-8")
        assert "sorry" not in source_text, f"Found sorry in {fname}"

    workdir = _lean_workdir(lean4_dir)
    build_res = subprocess.run(
        ["lake", "build"],
        cwd=str(workdir),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )
    assert build_res.returncode == 0, f"lake build failed:\n{build_res.stderr}\n{build_res.stdout}"

    result = subprocess.run(
        ["lake", "env", "lean", "Census.lean"],
        cwd=str(workdir),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, f"Lean Census compilation failed:\n{result.stderr}\n{result.stdout}"

    combined_output = result.stdout + result.stderr
    required_theorems = [
        # OmegaRelationalRsi (19 theorems)
        "OmegaRelationalRsi.witness_holonomy_obstruction",
        "OmegaRelationalRsi.lemma1a_self_critique_non_verification",
        "OmegaRelationalRsi.lemma1b_godel_diagonal_self_reference_obstruction",
        "OmegaRelationalRsi.lemma1c_goodhart_metric_collapse_on_collision",
        "OmegaRelationalRsi.lemma2a_nodup_length_le",
        "OmegaRelationalRsi.lemma2b_epistemic_horizon_refinement_bound",
        "OmegaRelationalRsi.lemma2c_licensed_lift_budget_bound",
        "OmegaRelationalRsi.lemma3a_private_fiber_channel_invisibility",
        "OmegaRelationalRsi.lemma3a_no_intersubjective_improvement_in_private_fiber",
        "OmegaRelationalRsi.lemma3b_overlap_conflict_refuses_sheaf_descent",
        "OmegaRelationalRsi.rsi_impossible",
        "OmegaRelationalRsi.rsi_trilemma_obstruction",
        "OmegaRelationalRsi.coupled_product_carrier_capacity",
        "OmegaRelationalRsi.coupled_coadaptation_joint_horizon_bound",
        "OmegaRelationalRsi.coupled_rsi_impossible",
        "OmegaRelationalRsi.higher_cochain_obstruction",
        "OmegaRelationalRsi.asynchronous_delayed_joint_horizon_bound",
        "OmegaRelationalRsi.dynamic_rewiring_higher_cochain_obstruction",
        "OmegaRelationalRsi.non_monotonic_rewired_joint_horizon_bound",
        # RelationalRSI (21 theorems)
        "RelationalRSI.rsi_impossible",
        "RelationalRSI.rsi_internal_impossible",
        "RelationalRSI.rsi_carrier_impossible",
        "RelationalRSI.rsi_step_impossible",
        "RelationalRSI.rsi_alignment_step_impossible",
        "RelationalRSI.rsi_carrier_step_impossible",
        "RelationalRSI.admittedGroundModel_aligned",
        "RelationalRSI.counterexample_agent_cannot_be_aligned",
        "RelationalRSI.rsi_decouples_within_carrier_bound",
        "RelationalRSI.rsi_alignment_lost_within_carrier_bound",
        "RelationalRSI.unbounded_budgeted_lifting_impossible",
        "RelationalRSI.zero_budget_carrier_lift_impossible",
        "RelationalRSI.interleaved_budgeted_lifting_impossible",
        "RelationalRSI.unbounded_carrier_lifting_impossible",
        "RelationalRSI.interleaved_carrier_lifting_impossible",
        "RelationalRSI.coupled_rsi_decouples_within_product_bound",
        "RelationalRSI.coupled_rsi_impossible",
        "RelationalRSI.asynchronous_coupled_rsi_decouples_within_product_bound",
        "RelationalRSI.asynchronous_coupled_rsi_impossible",
        "RelationalRSI.non_monotonic_rewired_rsi_decouples_within_product_bound",
        "RelationalRSI.non_monotonic_rewired_rsi_impossible",
    ]
    for thm in required_theorems:
        assert thm in combined_output, f"Missing axiom print for {thm} in output:\n{combined_output}"

    assert "sorryAx" not in combined_output, f"sorryAx detected in axiom output:\n{combined_output}"

    allowed_axioms = {"propext", "Quot.sound", "Classical.choice"}
    for line in combined_output.splitlines():
        if "depends on axioms:" in line:
            left = line.find("[")
            right = line.find("]")
            if left != -1 and right != -1:
                axioms_str = line[left + 1 : right]
                axioms = [a.strip() for a in axioms_str.split(",") if a.strip()]
                for ax in axioms:
                    assert ax in allowed_axioms, f"Non-standard axiom {ax} detected in: {line}"


def test_rsi_obstructions_formal_structure() -> None:
    lean_file = PACKAGE_ROOT / "lean4" / "RsiImpossible.lean"
    source = lean_file.read_text(encoding="utf-8")

    expected_obstructions = [
        "obstruction_relational_finitude",
        "obstruction_metric_collapse",
        "obstruction_goodhart_decoherence",
        "obstruction_intersubjective_decoherence",
        "obstruction_refusal_terminal",
        "counterexample_agent_cannot_be_aligned",
        "rsi_decouples_within_carrier_bound",
        "rsi_alignment_lost_within_carrier_bound",
    ]
    for obs in expected_obstructions:
        assert obs in source, f"Missing obstruction theorem {obs} in formalization"

    assert "IsGoodhartDecoupled" in source
    assert "IsGoodhartDecoupled C M" in source

    decl_marker = "\ntheorem rsi_impossible ("
    assert decl_marker in source
    decl_idx = source.find(decl_marker)
    decl_end = source.find("\ntheorem rsi_internal_impossible (", decl_idx)
    assert decl_end != -1
    rsi_imp_block = source[decl_idx:decl_end]

    assert "_h_traj" not in rsi_imp_block
    assert "_h_align" not in rsi_imp_block
    assert "h_traj" in rsi_imp_block
    assert "h_align" in rsi_imp_block
    assert "h_dom" in rsi_imp_block


def test_adversarial_counterexample_blocked() -> None:
    lean_file = PACKAGE_ROOT / "lean4" / "RsiImpossible.lean"
    source = lean_file.read_text(encoding="utf-8")

    decl_marker = "\ntheorem counterexample_agent_cannot_be_aligned"
    assert decl_marker in source
    idx = source.find(decl_marker)
    block = source[idx : idx + 400]
    assert "M.internalEvaluation ≥ C.carrierBound" in block or "M.internalEvaluation >= C.carrierBound" in block
    assert "¬ RelationalAlignment C M targetSig" in block
    assert "exact obstruction_goodhart_decoherence" in block


def test_interleaved_and_budgeted_lifting_theorems() -> None:
    lean_file = PACKAGE_ROOT / "lean4" / "RsiImpossible.lean"
    source = lean_file.read_text(encoding="utf-8")

    assert "structure CarrierLift" in source
    assert "carrier_expands : C_source.carrierBound < C_target.carrierBound" in source
    assert "budget_drops : targetBudget < sourceBudget" in source
    assert "theorem zero_budget_carrier_lift_impossible" in source
    assert "¬ CarrierLift C₁ C₂ 0 b_target" in source
    assert "theorem interleaved_budgeted_lifting_impossible" in source
    assert "h_budget_mono : ∀ k : Nat, budget (k + 1) ≤ budget k" in source
    assert "h_lift_drops : ∀ i : Nat, budget (liftIndices i + 1) < budget (liftIndices i)" in source


def test_zero_suppressed_or_unused_hypotheses_in_theorems() -> None:
    for fname in ("RsiImpossible.lean", "RelationalRsiNoGo.lean"):
        source = (PACKAGE_ROOT / "lean4" / fname).read_text(encoding="utf-8")
        lines = source.splitlines()
        for idx, line in enumerate(lines):
            if line.strip().startswith("theorem ") or (idx > 0 and lines[idx - 1].strip().startswith("theorem ")):
                assert "_h_" not in line, f"Found suppressed hypothesis in {fname} on line {idx + 1}: {line}"


def test_carrier_lifting_and_inhabitation_theorems() -> None:
    source = (PACKAGE_ROOT / "lean4" / "RsiImpossible.lean").read_text(encoding="utf-8")
    assert "theorem unbounded_carrier_lifting_impossible" in source
    assert "theorem interleaved_carrier_lifting_impossible" in source
    assert "def admittedGroundModel" in source
    assert "theorem admittedGroundModel_aligned" in source
    assert "theorem rsi_alignment_step_impossible" in source
    assert "def IsRSICarrierStep" in source
    assert "theorem rsi_carrier_step_impossible" in source


def test_constructive_horizon_decoupling_theorems() -> None:
    source = (PACKAGE_ROOT / "lean4" / "RsiImpossible.lean").read_text(encoding="utf-8")
    assert "theorem rsi_decouples_within_carrier_bound" in source
    assert "IsGoodhartDecoupled C (M C.carrierBound)" in source
    assert "theorem rsi_alignment_lost_within_carrier_bound" in source
    assert "¬ RelationalAlignment C (M C.carrierBound) targetSig" in source


def test_claim_hygiene_in_formalization_and_comments() -> None:
    forbidden = [
        "proves",
        "guarantees",
        "mathematically verifies",
        "fundamentally",
        "true intelligence",
        "universal",
        "flawless",
        "perfectly",
        "clearly",
        "obviously",
        "simply",
        "merely",
        "weaponized",
    ]
    for fname in ("RsiImpossible.lean", "RelationalRsiNoGo.lean", "Census.lean"):
        lean_file = PACKAGE_ROOT / "lean4" / fname
        source = lean_file.read_text(encoding="utf-8")
        for word in forbidden:
            matches = list(re.finditer(r"\b" + re.escape(word) + r"\b", source, re.IGNORECASE))
            assert not matches, (
                f"Found forbidden hype word '{word}' in {fname} on line "
                f"{source.count(chr(10), 0, matches[0].start()) + 1}"
            )
