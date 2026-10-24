"""Fresh Bell proof compilation and exhaustive named-theorem axiom census, offline."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"propext", "Quot.sound", "Classical.choice"}
PIN = "leanprover/lean4:v4.35.0"
SCOPE = (
    "Positive extension iff finite stochastic locality or an actual setting-independent "
    "probability-integral model with measurable normalized responses; positive normalized "
    "linear averaging; classical CHSH, signed and uncertainty-adjusted bounds; complex "
    "Hilbert-space Tsirelson operator and pure/finite-mixture state bounds; exact two-qubit "
    "Born-table saturation; arbitrary finite-dimensional density spectral and binary-POVM "
    "conversions, real positive normalized Born tables, no-signalling marginals, exact CHSH "
    "score identity and local tensor lifts; finite Hermitian spectral trace-norm measurement contraction, weighted TV, local-comparison repair and state-distance witnesses; actual finite separable density mixtures and their positive extensions, partial-trace densities, product-marginal idempotence, and the full separable-infimum to product-residual bound for arbitrary finite local POVMs and its CHSH specialization; conditional matrix remainder and oriented CHSH dynamics with finite exit windows; finite scalar observer minimax and evidence-preserving recursion. "
    "Attained weighted Bell repair LP duality and normalized witness bounds, explicit slack-variable optimality, attained signed-extension negative-mass duality and vertex-spread witnesses; finite variable elimination and linear-image polyhedrality; intrinsic Bell tangent cones, exact short-ray repair and explicit quadratic trajectory bounds. Infinite-dimensional trace-class conversions "
    "and Mermin cohomology results are not claimed by this census. "
    "Real-parameter CHSH and eight-context Mermin negative-mass optima against all real signed extensions; "
    "contextual fraction as local-subdistribution packing, exact family values, explicit CF versus 2N "
    "counterexample and reversed ranking, and the constructive finite-context bound CF <= (m-1)N. "
    "Quantum CHSH-line caps from Hilbert-space bounds; explicit GHZ state, local POVMs, Born realization, "
    "unitary rotation block identities, exact first-interval exit and score/TV uncertainty-delayed windows. "
    "Full nine-context 3x3 two-qubit quantum counterexample to CF <= 2N, with an exact factor-four line and necessary universal coefficient at least four. Full rational 5x5 quantum counterexample to CF <= 4N with exact real optima; arbitrary-size parity-cycle optimization and quantum-cosine unboundedness; continuous complete-grid CHSH lower bounds and a 160/17 tail cap. The asymptotic coefficient is formalized as a quantified tail theorem. Cycle path reconstruction, global-sign propagation, two-fold packing equality and signed-budget equivalence are formalized. Constructive local Gram models, normalized complete signed extensions, vector normalization, exact finite ramp sums, restriction monotonicity and quantified unbounded comparison under explicit scalar envelope premises are proved. The cyclic profile, arbitrary finite real Clifford representation, maximally entangled density, local POVMs and every Born cell are constructed. The actual complete Bell family has an attained strictly positive signed optimum, the ratio bound and quantified quantum unboundedness with no supplied envelope or quantum-realization premise. Selected Archimedean finite shadow cutoffs and failure of a finite ratio endpoint are proved; no physical continuum or general matrix exponential/ODE claim is made."
)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def atomic(path, content):
    pending = path.with_name(path.name + ".writing")
    pending.write_text(content, encoding="utf-8", newline="\n")
    os.replace(pending, path)


def theorem_inventory(lean):
    names = []
    for path in sorted((lean / "Bell").glob("*.lean")):
        source = path.read_text(encoding="utf-8")
        namespaces = re.findall(r"^namespace (\S+)$", source, re.M)
        if len(namespaces) != 1:
            raise ValueError("Expected one declared namespace per proof module")
        names.extend(namespaces[0] + "." + name for name in
                     re.findall(r"^theorem (\w+)", source, re.M))
    if len(names) != len(set(names)) or not names:
        raise ValueError("Empty or duplicate theorem inventory")
    return sorted(names)


def replay(record=False):
    lean = ROOT / "lean4"
    vendor = lean / "vendor"
    spec = json.loads((vendor / "manifest.json").read_text(encoding="utf-8"))
    archive = vendor / "dependencies.tar.gz"
    if digest(archive) != spec["archive_sha256"] or archive.stat().st_size != spec["archive_bytes"]:
        raise ValueError("Dependency archive digest mismatch")
    if (lean / "lean-toolchain").read_text().strip() != PIN or spec["toolchain"] != PIN:
        raise ValueError("Toolchain pin mismatch")
    expected = theorem_inventory(lean)
    requested = re.findall(r"^#print axioms (\S+)$", (lean / "Census.lean").read_text(), re.M)
    if sorted(requested) != expected:
        raise ValueError("Census does not cover every named Bell theorem exactly once")
    sources = sorted((lean / "Bell").glob("*.lean")) + [
        lean / "Bell.lean", lean / "Census.lean", lean / "lakefile.lean",
        lean / "lean-toolchain", vendor / "lakefile.lean", vendor / "manifest.json", archive,
    ]
    before = {p.relative_to(ROOT).as_posix(): digest(p) for p in sources}
    home = Path(os.environ.get("ELAN_HOME", str(Path.home() / ".elan")))
    lake = home / "toolchains/leanprover--lean4---v4.35.0/bin" / ("lake.exe" if os.name == "nt" else "lake")
    if not lake.is_file():
        raise ValueError("Install Lean 4.35.0 and set ELAN_HOME to the toolchain installation")
    env = dict(os.environ)
    env["PATH"] = str(lake.parent) + os.pathsep + env.get("PATH", "")
    version = subprocess.check_output([str(lake), "--version"], env=env, text=True)
    if "Lean version 4.35.0" not in version:
        raise ValueError("Compiler version mismatch")
    print("Fresh Bell proof build; using packaged offline dependencies", flush=True)
    with tempfile.TemporaryDirectory(prefix="bell-lean-") as directory:
        work = Path(directory)
        for path in sources:
            if vendor in path.parents:
                continue
            target = work / path.relative_to(lean)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        config = work / "lakefile.lean"
        config.write_text(config.read_text().replace('from "vendor"', "from " + json.dumps(vendor.as_posix())), encoding="utf-8")
        logs = []
        for args in [["build"], ["env", "lean", "Census.lean"]]:
            run = subprocess.run([str(lake), *args], cwd=work, env=env, capture_output=True,
                                 text=True, encoding="utf-8", timeout=5400)
            logs.append(run.stdout + run.stderr)
            if run.returncode:
                raise ValueError(logs[-1])
        declarations = {}
        for name, axioms in re.findall(r"^'([^']+)' depends on axioms: \[([^\]]*)\]$", logs[-1], re.M):
            values = sorted(value.strip() for value in axioms.split(",") if value.strip())
            if not set(values) <= ALLOWED:
                raise ValueError("Unapproved axiom in " + name + ": " + str(values))
            declarations[name] = values
        for name in re.findall(r"^'([^']+)' does not depend on any axioms$", logs[-1], re.M):
            declarations[name] = []
        if sorted(declarations) != expected:
            raise ValueError("Incomplete fresh axiom output")
        print("Proofs compiled; checking every extracted dependency file", flush=True)
        cache = lean / ".lake/vendor"
        total_files = len(spec["files"])
        for checked, (relative, item) in enumerate(spec["files"].items(), 1):
            path = cache / relative
            if not path.is_file() or path.stat().st_size != item["bytes"] or digest(path) != item["sha256"]:
                raise ValueError("Dependency mismatch: " + relative)
            if checked % 2000 == 0 or checked == total_files:
                print(f"Checked {checked}/{total_files} dependency files", flush=True)
    if before != {p.relative_to(ROOT).as_posix(): digest(p) for p in sources}:
        raise ValueError("Audited sources changed during compilation")
    result = {"schema_version": 1, "date": "2026-10-24", "formalized_in_lean": True,
              "toolchain": PIN, "sources": before, "declarations": declarations,
              "count": len(declarations), "fresh_compilation": True, "custom_axioms": [], "scope": SCOPE}
    census = ROOT / "axiom_census.json"
    if record:
        atomic(census, json.dumps(result, indent=2) + "\n")
        atomic(lean / "axiom_report.txt", version + "\n" + logs[-1])
        atomic(lean / "build_report.txt", logs[0])
    elif json.loads(census.read_text(encoding="utf-8")) != result:
        raise ValueError("Stored census differs from fresh compilation")
    print(f"PASS fresh Bell census: {len(declarations)} theorems; no custom axioms", flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    try:
        replay(args.record)
    except Exception as error:
        print("FAIL", error)
        sys.exit(1)
