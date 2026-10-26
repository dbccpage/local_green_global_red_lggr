"""Integer constraint DSL, module configuration parsing, hypotheses and check outcomes.

Expressions are JSON data: an int, {"x": "module.param"}, {"t": "hidden"},
{"+": [...]}, {"*": [...]}, {"-": [a, b]}, {"max": [...]}. A constraint is
{"id", "lhs", "op" ("<=" or ">="), "rhs", "text"}. Missing module parameters make
any constraint that reads them false. Module files are parsed, never executed.
"""
from itertools import product
import re

MALFORMED = "MALFORMED"
LINE = re.compile(r"^\s*([a-z_][a-z0-9_]*)\s*=\s*(-?\d{1,6})\s*$")


class Missing(Exception):
    pass


def evaluate(expr, x, theta):
    if isinstance(expr, bool):
        raise TypeError("boolean in expression")
    if isinstance(expr, int):
        return expr
    (op, arg), = expr.items()
    if op == "x":
        if x.get(arg) is None:
            raise Missing(arg)
        return x[arg]
    if op == "t":
        return theta[arg]
    values = [evaluate(a, x, theta) for a in arg]
    if op == "+":
        return sum(values)
    if op == "*":
        out = 1
        for v in values:
            out *= v
        return out
    if op == "-":
        return values[0] - values[1]
    if op == "max":
        return max(values)
    raise ValueError("unknown operator " + op)


def holds(constraint, x, theta):
    try:
        lhs, rhs = evaluate(constraint["lhs"], x, theta), evaluate(constraint["rhs"], x, theta)
    except Missing:
        return False
    return lhs <= rhs if constraint["op"] == "<=" else lhs >= rhs


def names(expr, kind):
    if isinstance(expr, int):
        return set()
    (op, arg), = expr.items()
    if op == kind:
        return {arg}
    if op in ("x", "t"):
        return set()
    return set().union(*(names(a, kind) for a in arg))


def constraint_names(constraint, kind):
    return names(constraint["lhs"], kind) | names(constraint["rhs"], kind)


def render(expr):
    if isinstance(expr, int):
        return str(expr)
    (op, arg), = expr.items()
    if op in ("x", "t"):
        return arg
    if op == "max":
        return "max(" + ", ".join(render(a) for a in arg) + ")"
    joiner = {"+": " + ", "*": "*", "-": " - "}[op]
    return "(" + joiner.join(render(a) for a in arg) + ")"


def render_constraint(c):
    return f"{c['id']}: {render(c['lhs'])} {c['op']} {render(c['rhs'])}  -- {c['text']}"


def parse_module(text, module):
    """Return {"module.param": int|None} plus a list of parse errors."""
    values, errors = {f"{module['name']}.{p}": None for p in module["params"]}, []
    for number, raw in enumerate((text or "").splitlines(), 1):
        line = raw.split("#", 1)[0]
        if not line.strip():
            continue
        match = LINE.match(line)
        if not match:
            errors.append(f"line {number}: expected `name = integer`")
            continue
        key = f"{module['name']}.{match.group(1)}"
        if key not in values:
            errors.append(f"line {number}: unknown parameter {match.group(1)}")
        elif values[key] is not None:
            errors.append(f"line {number}: duplicate parameter {match.group(1)}")
        else:
            values[key] = int(match.group(2))
    return values, errors


def snapshot_values(instance, files):
    x, errors = {}, {}
    for module in instance["modules"]:
        values, problems = parse_module(files.get(module["file"], ""), module)
        x.update(values)
        errors[module["name"]] = problems
    return x, errors


def local_report(instance, module, files):
    values, problems = parse_module(files.get(module["file"], ""), module)
    results = []
    for param, spec in module["params"].items():
        value = values[f"{module['name']}.{param}"]
        ok = value is not None and spec["lo"] <= value <= spec["hi"]
        results.append({"id": f"range.{param}", "pass": ok,
                        "text": f"{param} in [{spec['lo']}, {spec['hi']}] (got {value})"})
    for c in module["local"]:
        results.append({"id": c["id"], "pass": holds(c, values, {}), "text": render_constraint(c)})
    return {"module": module["name"], "parse_errors": problems,
            "pass": not problems and all(r["pass"] for r in results), "tests": results}


def local_green(instance, files):
    return all(local_report(instance, m, files)["pass"] for m in instance["modules"])


def verdict(instance, files, theta):
    """True iff the snapshot passes all local and global constraints under theta."""
    if not local_green(instance, files):
        return False
    x, _ = snapshot_values(instance, files)
    return all(holds(c, x, theta) for c in instance["global"])


def hypotheses(instance):
    hidden = instance["hidden"]
    return [dict(zip([h["name"] for h in hidden], combo)) for combo in product(*[h["domain"] for h in hidden])]


def outcome(instance, check, files, theta):
    kind = check["kind"]
    if kind == "probe":
        return "yes" if theta[check["param"]] >= check["threshold"] else "no"
    if kind == "sum_probe":
        return "yes" if sum(theta[p] for p in check["params"]) >= check["threshold"] else "no"
    if kind == "measure":
        return str(theta[check["param"]])
    if kind == "integration":
        constraint = next(c for c in instance["global"] if c["id"] == check["constraint"])
        x, _ = snapshot_values(instance, files)
        return "pass" if holds(constraint, x, theta) else "fail"
    if kind == "local":
        module = next(m for m in instance["modules"] if m["name"] == check["module"])
        return "pass" if local_report(instance, module, files)["pass"] else "fail"
    raise ValueError("unknown check kind " + kind)


def theta_only(check):
    """Checks whose outcome does not depend on the module files (carry over across repairs)."""
    return check["kind"] in ("probe", "sum_probe", "measure")


def check_params(instance, check):
    if check["kind"] in ("probe", "measure"):
        return {check["param"]}
    if check["kind"] == "sum_probe":
        return set(check["params"])
    if check["kind"] == "integration":
        return constraint_names(next(c for c in instance["global"] if c["id"] == check["constraint"]), "t")
    return set()


def check_modules(instance, check):
    if check["kind"] == "integration":
        keys = constraint_names(next(c for c in instance["global"] if c["id"] == check["constraint"]), "x")
        return {k.split(".", 1)[0] for k in keys}
    if check["kind"] == "local":
        return {check["module"]}
    return set()


def target(instance, files):
    """Correct decision for a frozen snapshot: accept/reject, or model_mismatch out of model."""
    if instance["control"] == "out_of_model":
        return "model_mismatch"
    return "accept" if verdict(instance, files, instance["truth"]) else "reject"


def global_contract_text(instance):
    lines = [f"System `{instance['id']}` ({instance['family']}). Modules: "
             + ", ".join(f"{m['name']} (owner {m['owner']}, file {m['file']})" for m in instance["modules"]) + ".",
             "Global contract: every module must pass its local tests AND all of:"]
    lines += ["  " + render_constraint(c) for c in instance["global"]]
    lines.append("Hidden environment parameters (true values unknown; each is one of the listed values):")
    lines += [f"  {h['name']} in {h['domain']}  -- {h['text']}" for h in instance["hidden"]]
    lines.append("Names like module.param refer to integer keys in that module's file.")
    return "\n".join(lines)


def local_contract_text(module):
    lines = [f"Module `{module['name']}` (owner {module['owner']}), file {module['file']}.",
             "File format: one `param = integer` per line; `#` starts a comment. Parameters:"]
    lines += [f"  {p}: integer in [{s['lo']}, {s['hi']}]  -- {s['text']}" for p, s in module["params"].items()]
    if module["local"]:
        lines.append("Local tests also require:")
        lines += ["  " + render_constraint(c) for c in module["local"]]
    return "\n".join(lines)


def catalog_text(instance):
    return "\n".join(f"  {c['id']} (cost {c['cost']}): {c['text']}" for c in instance["checks"])
