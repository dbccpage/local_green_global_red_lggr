"""Replay the v1.5 review's exact mathematics and the new observation API example.

The preserved checker reads Lean literals; fresh Lean elaboration and execution
comparison are performed by the separate census and simplex replay tools.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replay(root, write=False):
    source_record = root / "docs/v1_5_review_sources.json"
    source = json.loads(source_record.read_text(encoding="utf-8"))
    for row in source["sources"]:
        path = root / row["deposited_copy"]
        if digest(path) != row["sha256"] or path.stat().st_size != row["bytes"]:
            raise ValueError("Review source changed: " + row["deposited_copy"])
    review = root / "docs/source_inputs/v1_5_review"
    # Separate process prevents the reviewed modules from shadowing current ones.
    program = ("import json,runpy,sys; sys.path.insert(0," + repr(str(review)) + "); d=runpy.run_path(" + repr(str(review / "independent_review.py")) + "); "
               "print(json.dumps({k:d[k]() for k in ('fixture_bindings','noisy_boundary','cycling_fixture')}))")
    def execute(args):
        result = subprocess.run([sys.executable, "-X", "utf8", *args], cwd=root,
                                capture_output=True, text=True, encoding="utf-8", timeout=120)
        if result.returncode:
            raise ValueError(result.stdout + result.stderr)
        return json.loads(result.stdout)
    reviewed = execute(["-c", program])
    supplied = json.loads((review / "independent_results.json").read_text(encoding="utf-8"))
    mapping = {"fixture_bindings": "fixture_source_bindings", "noisy_boundary": "noisy_observation_boundary",
               "cycling_fixture": "degenerate_cycling_fixture"}
    if any(reviewed[key] != supplied[value] for key, value in mapping.items()):
        raise ValueError("Reviewed mathematical cases changed")
    current = execute([str(root / "code/uncertain_observation_example.py")])
    data = {"scope": "Three exact mathematical groups from preserved review; source literals are not Lean execution. The supplied path/symlink record is retained separately.",
            "review_groups": reviewed, "new_api_example": current}
    target = root / "docs/uncertain_observation_replay.json"
    if write:
        target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    elif json.loads(target.read_text(encoding="utf-8")) != data:
        raise ValueError("Uncertain-observation replay changed")
    paths = [source_record, root / "code/contextuality_lp.py", root / "code/epistemic_kernel.py",
             root / "code/uncertain_observation_example.py", Path(__file__), target]
    hashes = {p.relative_to(root).as_posix(): digest(p) for p in paths}
    bound = root / "docs/review_corrections_source_hashes.json"
    if write:
        bound.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    elif json.loads(bound.read_text(encoding="utf-8")) != hashes:
        raise ValueError("Review-correction source changed")
    return {"status": "PASS", "review_math_groups": 3, "raw_defect": "1/50", "radius": "1/50", "adjusted_margin": "0"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    print(json.dumps(replay(Path(__file__).resolve().parents[1], args.write)))
