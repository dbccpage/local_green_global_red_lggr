"""Independent exact checks for the supplied contextual-prediction v1.5 sources.

This reads Lean numeric definitions as data; it does not elaborate Lean.
Run from a reconstructed packet root containing code/ and lean4/.
"""
import ast
from dataclasses import replace
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "code"))
import contextuality_lp as lp
import epistemic_kernel as k
import deposit_paths as paths


def require(value, label):
    if not value:
        raise AssertionError(label)


def exact_literal(text):
    """Only integer/list/rational arithmetic is allowed; never eval source."""
    node = ast.parse(text.replace("![", "["), mode="eval").body
    def go(n):
        if isinstance(n, ast.Constant) and type(n.value) is int:
            return Q(n.value)
        if isinstance(n, ast.List):
            return tuple(go(x) for x in n.elts)
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -go(n.operand)
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
            return go(n.left) / go(n.right)
        raise ValueError("Nonliteral Lean fixture expression")
    return go(node)


def bell(table):
    return lp.Scenario((2, 2, 2, 2), ((0, 2), (0, 3), (1, 2), (1, 3)),
                       tuple(tuple(table[c].get(o, Q(0)) for o in product((0, 1), repeat=2))
                             for c in k.CONTEXTS))


def fixture_bindings():
    lean = (ROOT / "lean4/RationalCertificates.lean").read_text()
    fields = {}
    pattern = r"^def (\w+)\b[^\n]*?:=\s*(.*?)(?=^(?:def|theorem|end)\b|\Z)"
    for name, expr in re.findall(pattern, lean, re.M | re.S):
        fields[name] = exact_literal(expr.strip())
    s = Q(1, 2) + Q(1, 100000000)
    boundary = {c: {o: (1 + (s if (o[0] ^ o[1]) == (c[0] & c[1]) else -s)) / 4
                    for o in product((0, 1), repeat=2)} for c in k.CONTEXTS}
    models = {"classical": bell(k.classical_mixture()), "pr": bell(k.pr_box()),
              "near": bell(k.near_tsirelson()), "boundary": bell(boundary),
              "triangle": lp.Scenario((2, 2, 2), ((0, 1), (0, 2), (1, 2)),
                                      ((Q(0), Q(1, 2), Q(1, 2), Q(0)),) * 3)}
    out = {}
    for name, model in models.items():
        _, columns, target = lp.contextual_matrix(model)
        result = lp.evaluate(model)
        c = result.certificate
        observed = {"A": columns, "E": target, "P": c.coefficients,
                    "Y": c.witness, "Z": c.offset, "D": c.defect}
        for suffix, data in observed.items():
            require(data == fields[name + suffix], name + suffix)
        require(lp.verify_defect(columns, target, c), name + " certificate")
        out[name] = {"defect": str(c.defect), "pivot_count": c.lp.pivots,
                     "six_numeric_fields_match_Lean_source": True}
    return out


def noisy_boundary():
    truth = bell(k.classical_mixture())
    tables = [list(row) for row in truth.tables]
    epsilon = Q(1, 100)
    tables[0][0] -= epsilon
    tables[0][2] += epsilon
    observed = replace(truth, tables=tuple(map(tuple, tables)))
    try:
        lp.evaluate(observed)
    except lp.Refusal as exc:
        require(exc.kind == "SIGNALLING", "noisy public-API refusal")
    else:
        raise AssertionError("Expected signalling refusal")
    _, columns, target = lp.contextual_matrix(truth)
    noisy_target = tuple(v for row in observed.tables for v in row)
    c = lp.solve_l1(columns, noisy_target)
    radius = sum(abs(a - b) for a, b in zip(target, noisy_target))
    margin = max(Q(0), lp.dot(noisy_target, c.witness) + c.offset - radius)
    require(c.defect == radius == Q(1, 50) and margin == 0,
            "Noise alone must not certify contextuality of the true classical model")
    return {"public_evaluate": "SIGNALLING", "raw_LP_defect": str(c.defect),
            "known_l1_noise_radius": str(radius), "certified_positive_margin": str(margin)}


def cycling_fixture():
    costs = (-10, 57, 9, 24, 0, 0, 0)
    matrix = ((Q(1, 2), Q(-11, 2), Q(-5, 2), 9, 1, 0, 0),
              (Q(1, 2), Q(-3, 2), Q(-1, 2), 1, 0, 1, 0),
              (1, 0, 0, 0, 0, 0, 1))
    rhs = (0, 0, 1)
    c = lp.solve_standard(costs, matrix, rhs)
    require(c.value == -1, "Cycling-fixture optimum")
    require(lp.solve_standard(costs, matrix, rhs, max_pivots=c.pivots) == c,
            "Exactly sufficient pivot budget")
    try:
        lp.solve_standard(costs, matrix, rhs, max_pivots=c.pivots - 1)
    except lp.Refusal as exc:
        require(exc.kind == "BUDGET_EXHAUSTED", "One-short budget must refuse")
    else:
        raise AssertionError("One-short pivot budget unexpectedly accepted")
    return {"value": str(c.value), "pivots": c.pivots,
            "one_short_budget": "BUDGET_EXHAUSTED", "Lean_execution": False}


def path_checks():
    bad = ["", ".", "..", "../a", "/a", "a/../b", "a//b", "./a", "a\\b",
           "C:a", "CON", "AUX.txt", "a/NUL", "a/COM1.log", "a.", "a ", "a\x00b"]
    with tempfile.TemporaryDirectory(prefix="path_review_", dir=ROOT) as name:
        root = Path(name)
        for value in bad:
            try:
                paths.safe_path(root, value)
            except ValueError:
                pass
            else:
                raise AssertionError("Unsafe path accepted: " + repr(value))
        for value in ("a.txt", "code/test.py", "docs/source/SHA256SUMS"):
            require(paths.safe_path(root, value).is_relative_to(root), "Valid path")
        (root / "target").write_text("x")
        (root / "alias").symlink_to(root / "target")
        try:
            paths.safe_path(root, "alias")
        except ValueError:
            pass
        else:
            raise AssertionError("Symlink accepted")
    return {"rejected_bad_paths": len(bad), "accepted_good_paths": 3,
            "symlink_rejected": True}


if __name__ == "__main__":
    print(json.dumps({"status": "PASS", "arithmetic": "exact rational",
                      "Lean_compilation": False,
                      "fixture_source_bindings": fixture_bindings(),
                      "noisy_observation_boundary": noisy_boundary(),
                      "degenerate_cycling_fixture": cycling_fixture(),
                      "deposit_paths": path_checks()}, indent=2))
