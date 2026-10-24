"""Bind the Lean integer fixture to the exact Python certificate file.

Default mode is read-only. --write explicitly regenerates ComparisonData.lean.
"""
import argparse
import json
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def generated():
    cases = json.loads((ROOT/"data/contextual_fraction_certificates.json").read_text())["cases"]
    case = next(c for c in cases if c["name"] == "GHZ rnd2 (k=4, den=12)")
    data = {}
    for key, short, scale in [
        ("p", "pI", 768), ("cf_primal", "gammaI", 768),
        ("cf_dual", "yI", 1), ("n_primal", "qI", 768), ("n_dual", "zI", 2),
    ]:
        values = [F(v)*scale for v in case[key]]
        if any(v.denominator != 1 for v in values):
            raise ValueError("Unexpected denominator: " + key)
        if key in ("cf_primal", "n_primal"):
            values = [values[int(f"{g:06b}"[::-1], 2)] for g in range(64)]
        data[short] = [int(v) for v in values]
    text = """import Bell.BinaryScenarios

/-! Integer certificates generated from the independently checked LP fixture.
Assignment order is converted from lexicographic tuples to little-endian bits.
All finite assertions use kernel evaluation, not native_decide. -/
open scoped BigOperators
namespace Bell.ComparisonData
open Bell.BinaryScenarios
set_option maxRecDepth 100000
set_option maxHeartbeats 0

"""
    for key, values in data.items():
        text += f"def {key} : Fin 64 → ℤ := ![" + ", ".join(map(str, values)) + "]\n\n"
    facts = [
        ("p_nonnegative", "∀ i, 0 ≤ pI i"),
        ("p_total", "(∑ i, pI i) = 6144"),
        ("gamma_nonnegative", "∀ g, 0 ≤ gammaI g"),
        ("gamma_feasible", "∀ i, (∑ g, gammaI g * merminAI g i) ≤ pI i"),
        ("gamma_total", "(∑ g, gammaI g) = 540"),
        ("y_nonnegative", "∀ i, 0 ≤ yI i"),
        ("y_feasible", "∀ g, 1 ≤ ∑ i, yI i * merminAI g i"),
        ("cf_gap", "(∑ i, yI i * pI i) = 540"),
        ("q_total", "(∑ g, qI g) = 768"),
        ("q_projects", "∀ i, (∑ g, qI g * merminAI g i) = pI i"),
        ("q_mass", "(∑ g, max (-qI g) 0) = 75"),
        ("z_feasible", "∀ g, -2 ≤ (∑ i, zI i * merminAI g i) ∧ (∑ i, zI i * merminAI g i) ≤ 0"),
        ("n_gap", "(∑ i, zI i * pI i) = 150"),
    ]
    for name, statement in facts:
        text += f"theorem {name} : {statement} := by decide\n\n"
    return text + "end Bell.ComparisonData\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    path = ROOT/"lean4/Bell/ComparisonData.lean"
    content = generated()
    if args.write:
        path.write_text(content, encoding="utf-8", newline="\n")
    if path.read_text(encoding="utf-8") != content:
        raise ValueError("Lean/Python comparison fixture differs")
    print("PASS exact Lean/Python comparison fixture binding")


if __name__ == "__main__":
    main()

