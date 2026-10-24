"""Epistemic immune system (EIS) signal independence and digest verification.

AuthorityEffect: None.

Checks the declared host-role metadata policy with ASCII identifiers
and SHA-256 Signal 1 digests matching `omega_epistemic_immune_system::independence::signal1_digest`.
Also runs cross-checks against the compiled Rust companion binary.
"""

from __future__ import annotations

from collections.abc import Sequence
from importlib.resources import files, as_file
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any

DANGER_KINDS: tuple[str, ...] = (
    "MALFORMED_PAYLOAD",
    "MANIFEST_CONTAMINATION",
    "PROTECTED_FIELD_VIOLATION",
    "REPLAY_FAILURE",
)

FORBIDDEN_SELF_OBSERVERS: frozenset[str] = frozenset(
    {"model", "llm", "agent", "detector", "matcher"}
)


def _ascii_json_string(text: str) -> str:
    out: list[str] = ['"']
    for ch in text:
        code = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\b":
            out.append("\\b")
        elif ch == "\f":
            out.append("\\f")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif not (0x20 <= code < 0x7F):
            encoded = ch.encode("utf-16-be")
            for idx in range(0, len(encoded), 2):
                unit = (encoded[idx] << 8) | encoded[idx + 1]
                out.append(f"\\u{unit:04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def compute_signal1_digest(matches: list[dict[str, object]]) -> str:
    """Compute exact SHA-256 Signal 1 digest matching `omega_epistemic_immune_system::independence::signal1_digest`."""
    rows = sorted(
        matches,
        key=lambda r: (
            str(r["epitope_name"]),
            str(r["pattern_matched"]),
            int(r["offset"]),
        ),
    )
    parts: list[str] = ["["]
    for idx, row in enumerate(rows):
        if idx > 0:
            parts.append(",")
        offset_val = int(row["offset"])
        if offset_val < 0 or isinstance(row["offset"], bool):
            raise ValueError("EIS_VALUE_ERROR: offset must be an exact nonnegative integer")
        parts.append(
            "["
            + _ascii_json_string(str(row["epitope_name"]))
            + ","
            + _ascii_json_string(str(row["pattern_matched"]))
            + ","
            + str(offset_val)
            + "]"
        )
    parts.append("]")
    raw = "".join(parts).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _trim_python(text: str) -> str:
    return text.strip()


def verify_signal_independence(
    matches: list[dict[str, object]],
    danger: dict[str, object] | None,
    context: dict[str, object],
) -> dict[str, object]:
    """Check role-label separation; trusted-host authenticity is an external premise."""
    if danger is None:
        return {"ok": "no Signal 2 was observed"}

    detector_id = str(context.get("detector_id", ""))
    if not _trim_python(detector_id):
        return {
            "error": {
                "code": "EIS_VALUE_ERROR",
                "message": "EIS_VALUE_ERROR: detector_id must name the matcher that produced Signal 1",
            }
        }

    observer = str(danger.get("observer_id", ""))
    if not _trim_python(observer):
        return {
            "error": {
                "code": "UNWITNESSED_DANGER_SIGNAL",
                "message": "UNWITNESSED_DANGER_SIGNAL: Signal 2 names no host observer, so its independence cannot be checked",
            }
        }

    if any(not ch.isascii() or not (ch.isalnum() or ch in " ._:-")
           for identity in (observer, detector_id) for ch in identity):
        return {"error": {"code": "EIS_VALUE_ERROR", "message":
            "EIS_VALUE_ERROR: identities must use ASCII letters, digits, spaces, dot, underscore, colon or hyphen"}}

    folded = _trim_python(observer).lower()
    if folded in FORBIDDEN_SELF_OBSERVERS:
        return {
            "error": {
                "code": "TWO_SIGNAL_COLLAPSE",
                "message": (
                    f"TWO_SIGNAL_COLLAPSE: Signal 2 was reported by {observer!r}; "
                    "danger is observed by a host check, not proposed by a model or a detector"
                ),
            }
        }

    if folded == _trim_python(detector_id).lower():
        return {
            "error": {
                "code": "TWO_SIGNAL_COLLAPSE",
                "message": (
                    f"TWO_SIGNAL_COLLAPSE: Signal 2 was observed by {observer!r}, "
                    "the matcher that produced Signal 1; the danger bit is derived from the match"
                ),
            }
        }

    danger_type = str(danger.get("danger_type", ""))
    if danger_type not in DANGER_KINDS:
        return {
            "error": {
                "code": "UNREGISTERED_DANGER_KIND",
                "message": (
                    f"UNREGISTERED_DANGER_KIND: {danger_type!r} is not in the closed registry: "
                    + ", ".join(DANGER_KINDS)
                ),
            }
        }

    predicates = set(context.get("detector_predicates", []))
    if danger_type in predicates:
        return {
            "error": {
                "code": "TWO_SIGNAL_COLLAPSE",
                "message": (
                    f"TWO_SIGNAL_COLLAPSE: the matcher {detector_id!r} already evaluates {danger_type}; "
                    "the same predicate would be counted twice"
                ),
            }
        }

    evidence_digest = str(danger.get("evidence_digest", ""))
    if matches and evidence_digest == compute_signal1_digest(matches):
        return {
            "error": {
                "code": "TWO_SIGNAL_COLLAPSE",
                "message": (
                    "TWO_SIGNAL_COLLAPSE: Signal 2's evidence is the digest of the Signal 1 matches; "
                    "that is one signal counted twice"
                ),
            }
        }

    if bool(context.get("offsets_are_content", False)):
        spans = list(danger.get("evidence_spans", []))
        for m in matches:
            offset = int(m["offset"])
            pat_len = max(1, len(str(m["pattern_matched"])))
            stop = offset + pat_len
            for low, high in spans:
                if offset < int(high) and int(low) < stop:
                    return {
                        "error": {
                            "code": "TWO_SIGNAL_COLLAPSE",
                            "message": (
                                f"TWO_SIGNAL_COLLAPSE: the Signal 1 match at characters [{offset}, {stop}) "
                                f"lies inside the {danger_type} evidence; one token cannot be both signals"
                            ),
                        }
                    }

    defect_count = int(danger.get("defect_count", 0))
    prefix = evidence_digest[:23]
    return {
        "ok": (
            f"host observer {observer} reported {danger_type} "
            f"({defect_count} defect(s), evidence {prefix}...), "
            f"distinct from matcher {detector_id} and its matches"
        )
    }


def verify_bundled_eis_fixture() -> dict[str, int]:
    """Check 55 local ASCII-policy vectors and 7 upstream digest vectors."""
    fixture_path = files("rsi_eis_resources").joinpath("eis_independence_vectors_v2.json")
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    vectors = list(data["vectors"])
    digests = list(data["digests"])
    if len(vectors) != 55:
        raise AssertionError(f"Expected 55 EIS independence vectors, found {len(vectors)}")
    if len(digests) != 7:
        raise AssertionError(f"Expected 7 EIS digest vectors, found {len(digests)}")

    for idx, row in enumerate(vectors):
        inp = row["input"]
        matches = list(inp["matches"])
        danger = inp["danger"]
        ctx = {
            "detector_id": inp["detector_id"],
            "detector_predicates": inp["detector_predicates"],
            "offsets_are_content": inp["offsets_are_content"],
        }
        actual = verify_signal_independence(matches, danger, ctx)
        if actual != row["expected"]:
            raise AssertionError(
                f"EIS fixture vector {idx} mismatch: {actual} != {row['expected']}"
            )

    for idx, row in enumerate(digests):
        matches = list(row["input"])
        actual_digest = compute_signal1_digest(matches)
        if actual_digest != row["expected"]:
            raise AssertionError(
                f"EIS digest vector {idx} mismatch: {actual_digest} != {row['expected']}"
            )

    return {"independence_vectors": len(vectors), "digest_vectors": len(digests)}


def cross_check_eis_metadata_against_rust(
    receipts: Sequence[Any],
) -> dict[str, object]:
    """Replay ASCII-identity metadata, digest and reported horizon arithmetic.

    This does not authenticate the host or validate an obstruction, trajectory,
    budget or cochain. The wire format supports one match, one span, at most one
    predicate and content offsets; unsupported inputs are refused explicitly.
    The 55 bundled vectors test the Python policy; supplied records also execute
    the native companion. This is a local policy, not upstream Unicode parity.
    """
    fixture_stats = verify_bundled_eis_fixture()
    rust_src = files("rsi_eis_resources").joinpath("rust_eis_companion.rs")
    if not rust_src.is_file():
        raise FileNotFoundError(f"Missing Rust companion source: {rust_src}")

    stdin_lines: list[str] = []
    for receipt in receipts:
        if not (0 <= receipt.termination_step <= receipt.carrier_capacity + 1):
            raise AssertionError(
                f"Termination step {receipt.termination_step} exceeds N + 1 = {receipt.carrier_capacity + 1}"
            )
        if hasattr(receipt, "agent_capacities") and hasattr(receipt, "product_carrier_capacity"):
            expected_prod = math.prod(receipt.agent_capacities)
            if receipt.product_carrier_capacity != expected_prod:
                raise AssertionError(
                    f"Product capacity mismatch: {receipt.product_carrier_capacity} != {expected_prod}"
                )
            if not (0 <= receipt.termination_step <= expected_prod + 1):
                raise AssertionError(
                    f"Hypergraph step {receipt.termination_step} exceeds N_A * N_B + 1 = {expected_prod + 1}"
                )

        vec = receipt.eis_vector
        matches = list(vec["matches"])  # type: ignore[arg-type]
        danger = dict(vec["danger"])  # type: ignore[arg-type]
        context = dict(vec["context"])  # type: ignore[arg-type]

        expected_sig1 = compute_signal1_digest(matches)
        if vec["signal1_digest"] != expected_sig1:
            raise AssertionError(
                f"Signal 1 digest mismatch: {vec['signal1_digest']} != {expected_sig1}"
            )
        recomputed_verdict = verify_signal_independence(matches, danger, context)
        if recomputed_verdict != receipt.eis_independence_verdict:
            raise AssertionError(
                f"Independence verdict mismatch: {recomputed_verdict} != {receipt.eis_independence_verdict}"
            )

        if (len(matches) != 1 or len(danger["evidence_spans"]) != 1
                or len(context.get("detector_predicates", [])) > 1
                or context.get("offsets_are_content") is not True):
            raise ValueError("Unsupported EIS metadata wire shape")
        m0 = matches[0]
        span0 = list(danger["evidence_spans"])[0]  # type: ignore[index]
        preds = list(context.get("detector_predicates", []))  # type: ignore[arg-type]
        pred0 = str(preds[0]) if preds else ""
        fields = [
            str(receipt.termination_step),
            str(receipt.carrier_capacity),
            str(m0["epitope_name"]),
            str(m0["pattern_matched"]),
            str(m0["offset"]),
            str(danger["danger_type"]),
            str(danger["observer_id"]),
            str(danger["evidence_digest"]),
            str(danger["defect_count"]),
            str(span0[0]),
            str(span0[1]),
            str(context["detector_id"]),
            pred0,
        ]
        if hasattr(receipt, "agent_capacities") and receipt.agent_capacities:
            fields.append(",".join(str(c) for c in receipt.agent_capacities))
        if any(any(c in field for c in "\t\r\n") for field in fields):
            raise ValueError("EIS metadata fields cannot contain wire delimiters")
        stdin_lines.append("\t".join(fields))

    with as_file(rust_src) as rust_path, tempfile.TemporaryDirectory(prefix="rsi_rust_eis_") as tmp_dir:
        exe_name = "rust_eis_companion.exe" if os.name == "nt" else "rust_eis_companion"
        exe_path = Path(tmp_dir) / exe_name
        compile_proc = subprocess.run(
            ["rustc", "--edition=2021", str(rust_path), "-o", str(exe_path)],
            cwd=tmp_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
            check=False,
        )
        if compile_proc.returncode != 0:
            raise RuntimeError(
                f"rustc compilation of rust_eis_companion.rs failed:\n{compile_proc.stdout}\n{compile_proc.stderr}"
            )

        run_proc = subprocess.run(
            [str(exe_path)],
            input="\n".join(stdin_lines) + "\n",
            cwd=tmp_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
            check=False,
        )
        if run_proc.returncode != 0:
            raise RuntimeError(
                f"Execution of rust_eis_companion failed:\n{run_proc.stdout}\n{run_proc.stderr}"
            )

        out_lines = [ln.strip() for ln in run_proc.stdout.splitlines() if ln.strip()]
        if len(out_lines) != len(receipts):
            raise AssertionError(
                f"Expected {len(receipts)} Rust output lines, got {len(out_lines)}"
            )

        for receipt, out_line in zip(receipts, out_lines):
            parts = out_line.split("\t")
            expected_sig1 = str(receipt.eis_vector["signal1_digest"])
            verdict = receipt.eis_independence_verdict
            if "ok" in verdict:
                if parts[0] != "OK" or parts[1] != expected_sig1 or parts[2] != verdict["ok"]:
                    raise AssertionError(
                        f"Rust/Python EIS mismatch on OK receipt: {parts} vs {verdict}"
                    )
            else:
                err_obj = dict(verdict["error"])  # type: ignore[arg-type]
                if (
                    parts[0] != "ERR"
                    or parts[1] != expected_sig1
                    or parts[2] != err_obj["code"]
                    or parts[3] != err_obj["message"]
                ):
                    raise AssertionError(
                        f"Rust/Python EIS mismatch on ERR receipt: {parts} vs {err_obj}"
                    )

    return {
        "metadata_record_count": len(receipts),
        "rust_companion_executed": True,
        "scope": "EIS_METADATA_ONLY",
        "obstruction_predicates_checked": False,
        "identity_contract": "ascii-identifiers-v2",
        "eis_fixture_vectors": fixture_stats["independence_vectors"],
        "eis_digest_vectors": fixture_stats["digest_vectors"],
    }


# Compatibility name; the returned scope explicitly excludes obstruction replay.
cross_check_receipts_against_rust_eis = cross_check_eis_metadata_against_rust
