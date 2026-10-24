"""Compare complete executable Lean/Python two-phase runs, not just witnesses.

--write binds deterministic input/output fixtures; --check detects drift;
--replay executes the total Lean implementation on every fixture. These finite
comparisons supplement the general Lean success-soundness and budget theorems;
they do not prove universal Python refinement or unbudgeted Bland termination.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "tools"))
import contextuality_lp as lp
from generate_lp_certificates import fixtures


def cases():
    rows = []
    def add(name, c, a, b, budget=100):
        rows.append({"name": name, "costs": list(map(str, c)),
                     "matrix": [list(map(str, row)) for row in a],
                     "rhs": list(map(str, b)), "budget": budget})
    add("positive", [1, 2], [[1, 1]], [1])
    add("negative_redundant", [1, 2], [[-1, -1], [-2, -2]], [-1, -2])
    add("infeasible", [1], [[1], [1]], [0, 1])
    add("unbounded", [-1], [], [])
    add("zero_rows", [1], [[0], [0]], [0, 0])
    add("empty", [], [], [])
    add("empty_infeasible", [], [[]], [1])
    add("negative_rhs_infeasible", [0], [[1]], [-1])
    add("redundant_infeasible", [0, 1], [[1, 1], [-2, -2], [0, 0]], [1, -3, 0])
    add("ray_with_base", [-1, 0], [[1, -1]], [2])
    add("ray_negative_rhs", [-1, 0], [[-1, 1]], [-2])
    add("ray_redundant", [-1, 0], [[1, -1], [2, -2], [0, 0]], [2, 4, 0])
    add("ray_zero_budget", [-1], [], [], 0)
    add("infeasible_zero_budget", [], [[]], [-1], 0)
    add("ray_needs_phase_one_budget", [-1, 0], [[1, -1]], [2], 0)
    for k in range(1, 9):
        add("farkas_scaled_" + str(k), [Q(k, 3)], [[k]], [-k])
        add("ray_scaled_" + str(k), [-Q(k, 3), 0], [[-k, k]], [-2 * k])
    add("already_optimal_zero_budget", [1], [], [], 0)
    add("phase_one_zero_budget", [1, 2], [[1, 1]], [1], 0)
    add("degenerate", [-1, -1, 0, 0], [[1, 0, 1, 0], [0, 1, 0, 1]], [0, 1])
    # Beale's classical cycling example, solved with Bland's rule.
    add("beale", [-10, 57, 9, 24, 0, 0, 0],
        [[Q(1, 2), Q(-11, 2), Q(-5, 2), 9, 1, 0, 0],
         [Q(1, 2), Q(-3, 2), Q(-1, 2), 1, 0, 1, 0],
         [1, 0, 0, 0, 0, 0, 1]], [0, 0, 1])
    for name, model in fixtures().items():
        _, a, e = lp.contextual_matrix(model)
        _, _, c, matrix, rhs = lp.standard_form(a, e)
        solved = lp.solve_standard(c, matrix, rhs)
        for budget in [0, solved.pivots - 1, solved.pivots, solved.pivots + 1]:
            add(name + "_budget_" + str(budget), c, matrix, rhs, budget)
    rng = random.Random(20261021)
    for i in range(40):
        a = tuple((Q(rng.randrange(-9, 10), rng.randrange(1, 6)),) for _ in range(4))
        e = (Q(rng.randrange(-12, 13), rng.randrange(1, 6)),)
        _, _, c, matrix, rhs = lp.standard_form(a, e)
        add("hull_" + str(i), c, matrix, rhs)
    return rows


def python_result(case):
    try:
        c = lp.solve_standard(tuple(map(Q, case["costs"])),
                              tuple(tuple(map(Q, row)) for row in case["matrix"]),
                              tuple(map(Q, case["rhs"])), max_pivots=case["budget"])
        return {"primal": list(map(str, c.primal)), "dual": list(map(str, c.dual)),
                "value": str(c.value), "pivots": c.pivots}
    except lp.CertifiedInfeasible as exc:
        assert lp.verify_infeasible(tuple(map(Q, case["costs"])),
            tuple(tuple(map(Q, row)) for row in case["matrix"]), tuple(map(Q, case["rhs"])), exc.certificate)
        return {"outcome": "infeasible", "dual": list(map(str, exc.certificate.dual)),
                "pivots": exc.certificate.pivots}
    except lp.CertifiedUnbounded as exc:
        assert lp.verify_unbounded(tuple(map(Q, case["costs"])),
            tuple(tuple(map(Q, row)) for row in case["matrix"]), tuple(map(Q, case["rhs"])), exc.certificate)
        return {"outcome": "unbounded", "primal": list(map(str, exc.certificate.primal)),
                "direction": list(map(str, exc.certificate.direction)), "pivots": exc.certificate.pivots}
    except lp.Refusal as exc:
        return {"refusal": {"BUDGET_EXHAUSTED": "budget", "INFEASIBLE": "infeasible",
                            "UNBOUNDED": "unbounded", "CERTIFICATE_MISMATCH": "certificate"}[exc.kind]}


def generate():
    inputs = cases()
    sources = ["code/contextuality_lp.py", "lean4/Simplex.lean", "lean4/CertifiedOutcomes.lean", "lean4/SimplexDriver.lean",
               "tools/replay_simplex_implementation.py", "tools/generate_lp_certificates.py"]
    return {"schema": "contextuality.simplex-executions.v2", "seed": 20261021,
            "scope": "Finite full-output execution agreement; not universal Python refinement.",
            "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sources},
            "cases": [{"input": c, "expected": python_result(c)} for c in inputs]}


def canonical_result(row):
    if "refusal" in row:
        return {"refusal": row["refusal"].split(".")[-1]}
    if row.get("outcome") == "infeasible":
        return {"outcome": "infeasible", "dual": [str(Q(v)) for v in row["dual"]], "pivots": row["pivots"]}
    if row.get("outcome") == "unbounded":
        return {"outcome": "unbounded", "primal": [str(Q(v)) for v in row["primal"]],
                "direction": [str(Q(v)) for v in row["direction"]], "pivots": row["pivots"]}
    return {"primal": list(map(lambda x: str(Q(x)), row["primal"])),
            "dual": list(map(lambda x: str(Q(x)), row["dual"])),
            "value": str(Q(row["value"])), "pivots": row["pivots"]}


def replay(record):
    with tempfile.TemporaryDirectory(prefix="simplex-execution-") as work:
        path = Path(work) / "input.json"
        path.write_text(json.dumps([r["input"] for r in record["cases"]]), encoding="utf-8")
        result = subprocess.run(["lake", "env", "lean", "--run", "SimplexDriver.lean", str(path)],
            cwd=ROOT / "lean4", capture_output=True, text=True, encoding="utf-8", timeout=600)
        if result.returncode:
            raise ValueError(result.stdout + result.stderr)
        actual = json.loads(result.stdout)
    if len(actual) != len(record["cases"]):
        raise ValueError("Lean omitted execution cases")
    for case, row in zip(record["cases"], actual):
        if canonical_result(row) != case["expected"]:
            raise ValueError(f"Execution mismatch: {case['input']['name']}: {row} != {case['expected']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    try:
        record = generate()
        path = ROOT / "docs/simplex_execution_cases.json"
        encoded = json.dumps(record, indent=2) + "\n"
        if args.write:
            path.write_text(encoded, encoding="utf-8")
        elif path.read_text(encoding="utf-8") != encoded:
            raise ValueError("Simplex execution fixtures/source binding changed")
        if args.replay:
            replay(record)
        print(f"PASS: {len(record['cases'])} complete simplex execution cases" +
              (" agree in Lean and Python" if args.replay else " bound to current sources"))
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        raise SystemExit("FAIL: " + str(exc))
