"""CLI demonstration and numerical regression runner for Local Green, Global Red."""
from __future__ import annotations

from typing import List, Tuple

import numpy as np
from code_core import Assignment
from code_theorems import (
    check_remark_irreparable_red,
    check_theorem_1_passivity,
    check_theorem_2_characterization,
    check_theorem_5_sufficiency,
    check_theorem_6_coupled_witness,
    replay_theorem_3_three_patch,
    replay_theorem_4_no_recovery_modulus,
)
from code_witnesses import ThreePatchSystem, TrivialKernelThreePatchSystem


def run_paper_snippet_replay(R: float = 6.0) -> Tuple[float, List[float]]:
    """Parameterized NumPy demonstration snippet illustrating the 6-site construction."""
    print(f"--- Replaying §6 Python Demonstration Snippet (R = {R}) ---")
    scale = R / 6.0
    e = np.eye(3)
    s = {"u0": scale * e[0], "u1": scale * e[1], "u2": scale * e[2],
         "x01": np.zeros(3), "x12": np.zeros(3), "x20": np.zeros(3)}
    edges = [("x01", "u0"), ("x01", "u1"), ("x12", "u1"),
             ("x12", "u2"), ("x20", "u2"), ("x20", "u0")]
    watcher = {ed: int(ed[1][1]) for ed in edges}   # u_i watched by evaluator i
    d = {ed: s[ed[1]] - s[ed[0]] for ed in edges}
    inc = float(sum(np.abs(v).sum() for v in d.values()))
    J = [float(sum(np.abs(np.delete(d[ed], a)).sum()
         for ed in edges if watcher[ed] == a)) for a in range(3)]
    print(f"Global Inconsistency I = {inc}")
    print(f"Evaluator Scores J    = {J}")
    print(f"Result: Global Red (I={inc}), All-Green (J={J})")
    return inc, J


def main() -> int:
    print("=================================================================")
    print("Local Green, Global Red: Numerical Witness & Replay Harness")
    print("=================================================================\n")
    run_paper_snippet_replay(R=6.0)

    print("\n--- Numerical Regression & Replay Checks ---")
    tp = ThreePatchSystem()
    a_demo = tp.create_scaled_assignment(1.0)

    tk = TrivialKernelThreePatchSystem()
    a_tk = Assignment()
    for name in ["u0", "u1", "u2", "x01", "x12", "x20"]:
        a_tk.set_state(name, np.zeros(3))

    t1 = check_theorem_1_passivity(tp.system, a_demo)
    t2 = check_theorem_2_characterization(tp.system, a_demo)
    t3, I_3, _ = replay_theorem_3_three_patch(6.0)
    t4, _, _ = replay_theorem_4_no_recovery_modulus(lambda j: 100.0 * j + 50.0)
    t5 = check_theorem_5_sufficiency(tk.system, a_tk)
    t6 = check_theorem_6_coupled_witness()
    rem = check_remark_irreparable_red()

    checks = [
        ("Theorem 1 (Passivity Check)", t1),
        ("Theorem 2 (All-Green Characterization)", t2),
        ("Theorem 3 (Three-Patch False Green)", t3),
        ("Theorem 4 (No Recovery Modulus Replay)", t4),
        ("Theorem 5 (Sufficient Condition Check)", t5),
        ("Theorem 6 (Coupled Witness Replay)", t6),
        ("Remark (Irreparable Red Quotient Check)", rem),
    ]

    for name, ok in checks:
        print(f"{name:42}: {'PASS' if ok else 'FAIL'}")

    all_passed = all(ok for _, ok in checks)
    if all_passed:
        print("\nAll numerical witnesses and replay checks passed.")
        return 0
    else:
        failed = [name for name, ok in checks if not ok]
        print(f"\nFAIL: {len(failed)} numerical check(s) failed: {', '.join(failed)}")
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
