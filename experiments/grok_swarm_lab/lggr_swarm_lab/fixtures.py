"""Frozen deterministic fixture inputs, never an agent-facing correctness table.

``source`` and ``semantics`` are the protected original inputs consumed by the
host's SQLite fixture importer and the independent judge.  Only ``public`` and
actual proposed operations/tool observations may reach a controller.  ``family``
and ``scenario`` select host fault injection; a controller must never branch on
them.  Scenario proposals are delivered as actual upstream planner artifacts.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import random


FAMILIES = (
    "equal_reports", "composition", "branch_join", "units_sign", "query_scope",
    "obligations", "version_transition", "evidence_resolution", "event_integrity",
    "merge_retention", "shared_budget", "completion_controls",
)
SPLIT_SEEDS = {"development": 271828, "evaluation": 161803}
VARIANTS_PER_FAMILY = {"development": 2, "evaluation": 4}
ALLOWED_PROBES = (
    "semantics", "source_counts", "obligation_evidence", "migration", "branch_evidence",
)
LEDGER_COLUMNS = (
    "order_id", "customer_id", "region", "gross_cents", "refund_cents", "net_cents",
)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _base(split: str, family: str, family_index: int, variant: int) -> dict:
    # The development collision pair deliberately shares source bytes.  Its
    # meaning differs solely in an observable metadata field, not a task ID.
    source_variant = 0 if split == "development" and family == "equal_reports" else variant
    rng = random.Random(SPLIT_SEEDS[split] + 1009 * family_index + 97 * source_variant)
    n_orders = 4 if split == "development" else 4 + variant % 3
    customers = [
        {"customer_id": "c0", "region": "north"},
        {"customer_id": "c1", "region": "south"},
        {"customer_id": "c2", "region": "west"},
        # The contract names source row order as authority.  A naive all-match
        # join really fans out and can change the customer's region.
        {"customer_id": "c0", "region": "east"},
    ]
    orders = [{"order_id": f"o{i}", "customer_id": f"c{i % 3}", "amount": rng.randint(20, 90) * 100}
              for i in range(n_orders)]
    refunds = [{"refund_id": f"r{i}", "order_id": f"o{i}", "amount": rng.randint(1, 9) * 100}
               for i in range(0, n_orders, 2)]
    contract = {
        "query_id": "ledger_reconciliation", "query_scope": "endpoint", "baseline": 0,
        "max_step": 2, "max_total": 1, "resource_limit": 20,
        "required_versions": {name: "v1" for name in
                              ("policy", "specification", "evaluator", "representation", "report_schema")},
        "required_evidence_probes": ["semantics", "branch_evidence"],
        "required_auxiliary_queries": [], "required_event_roles": ["orders", "refunds"],
        "customer_resolution": "first", "output_columns": list(LEDGER_COLUMNS),
        "terminal_observation": "only_after_integration", "authority_effect": "None",
    }
    return {
        "case_id": f"{split}.{family}.{variant:02d}", "split": split,
        "family": family, "variant": variant,
        "source": {"customers": customers, "orders": orders, "refunds": refunds},
        "semantics": {
            "spec_version": "v1", "order_scale_to_cents": 1,
            "refund_scale_to_cents": 1, "refund_sign": 1,
            "customer_resolution": "first", "inclusion": "all_orders",
            "refund_policy": "subtract_signed_magnitude", "output_columns": list(LEDGER_COLUMNS),
        },
        "public": {
            "task": "Reconcile every original order with its first authoritative customer row and all refunds into an integer-cent ledger.",
            "contract": contract, "allowed_probes": list(ALLOWED_PROBES),
        },
        "scenario": {
            "worker_proposals": {
                "orders": {"operation": "orders", "scale_to_cents": 1, "join_mode": "first", "omit_last": False},
                "refunds": {"operation": "refunds", "scale_to_cents": 1, "sign": 1, "omit_last": False, "duplicate": False},
                "integrator": {"operation": "integrate", "refund_multiplier": 1},
            },
            "drift_path": [0, 0, 0], "arrival_plan": ["orders", "refunds"],
            "obligations": [], "empty_later_obligation_report": False,
            "transition": {"kind": "none", "dimension": "report_schema", "from_version": "v1", "to_version": "v1"},
            "negative_evidence": [], "probe_failures": {}, "extra_branch_costs": [],
            "metadata": {},
        },
    }


def _configure(case: dict) -> None:
    family, v = case["family"], case["variant"]
    s, sem, public = case["scenario"], case["semantics"], case["public"]
    p, contract = s["worker_proposals"], public["contract"]
    if family == "equal_reports":
        if v in (1, 2):
            sem["order_scale_to_cents"] = 100
        if v == 3:
            sem["refund_sign"] = -1
            for row in case["source"]["refunds"]:
                row["amount"] *= -1
            p["refunds"]["sign"] = -1  # Another genuinely correct proposal.
    elif family == "composition":
        if v == 0:
            p["integrator"]["refund_multiplier"] = -1
        elif v == 1:
            p["orders"]["omit_last"] = True
        elif v == 2:
            p["refunds"]["duplicate"] = True
    elif family == "branch_join":
        if v % 2 == 0:
            p["orders"]["join_mode"] = "all"
        s["arrival_plan"] = ["refunds", "orders"] if v >= 2 else ["orders", "refunds"]
    elif family == "units_sign":
        if v in (0, 2):
            sem["order_scale_to_cents"] = 100
        if v in (1, 2):
            sem["refund_sign"] = -1
            for row in case["source"]["refunds"]:
                row["amount"] *= -1
        if v == 3:
            sem["refund_scale_to_cents"] = 100
            for row in case["source"]["refunds"]:
                row["amount"] //= 100
    elif family == "query_scope":
        s["drift_path"] = [0, 2, 1] if v in (0, 1) else ([0, 2, 2] if v == 2 else [0, 1, 0])
        contract["query_scope"] = "every_prefix" if v in (1, 3) else "endpoint"
    elif family == "obligations":
        s["obligations"] = [{"id": "refund-evidence", "branch": "refunds", "discharge_available": bool(v % 2)}]
        s["empty_later_obligation_report"] = True
        if v >= 2:
            s["arrival_plan"] = ["refunds", "orders", "refunds"]
    elif family == "version_transition":
        s["transition"] = {
            "kind": "validated" if v % 2 == 0 else "unsupported",
            "dimension": "report_schema" if v < 2 else "evaluator",
            "from_version": "v1", "to_version": "v2",
            "mapping": "identity_ledger_columns" if v % 2 == 0 else None,
        }
    elif family == "evidence_resolution":
        sem["order_scale_to_cents"] = 100
        if v % 2:
            public["allowed_probes"].remove("semantics")
        if v >= 2:
            sem["refund_sign"] = -1
            for row in case["source"]["refunds"]:
                row["amount"] *= -1
    elif family == "event_integrity":
        s["arrival_plan"] = (
            ["orders", "orders", "refunds"] if v == 0 else
            ["orders"] if v == 1 else
            ["refunds", "orders"] if v == 2 else
            ["orders", "refunds", "orders"]
        )
    elif family == "merge_retention":
        if v in (0, 2):
            contract["required_auxiliary_queries"] = ["auxiliary_branch_contract"]
            s["negative_evidence"] = [{
                "query_id": "auxiliary_branch_contract", "scope": "endpoint", "baseline": 0,
                "global_verdict": False, "terminal": True, "branch": "refunds",
                "source": "deterministic_auxiliary_fixture_check",
            }]
        s["extra_branch_costs"] = [{"branch": "orders", "cost": 3}, {"branch": "refunds", "cost": 7}]
        if v == 2:
            s["obligations"] = [{"id": "merge-negative-evidence", "branch": "refunds", "discharge_available": False}]
        if v == 3:
            contract["resource_limit"] = 9
    elif family == "shared_budget":
        contract["resource_limit"] = [4, 20, 5, 8][v]
        s["probe_failures"] = {"semantics": 2 if v in (0, 2) else 1}
        if v == 2:
            s["extra_branch_costs"] = [{"branch": "orders", "cost": 2}, {"branch": "refunds", "cost": 2}]
    elif family == "completion_controls":
        if v in (1, 2):
            sem["order_scale_to_cents"] = 100
        if v == 2:
            public["allowed_probes"].remove("semantics")
        if v == 3:
            case["source"]["refunds"] = []


def generate_cases(split: str) -> list[dict]:
    """Return a fresh deterministic split; no oracle labels are included."""
    aliases = {"dev": "development", "eval": "evaluation"}
    split = aliases.get(split, split)
    if split not in SPLIT_SEEDS:
        raise ValueError(f"unknown split: {split!r}")
    cases = []
    for index, family in enumerate(FAMILIES):
        for variant in range(VARIANTS_PER_FAMILY[split]):
            case = _base(split, family, index, variant)
            _configure(case)
            cases.append(case)
    return copy.deepcopy(cases)


def freeze_protocol(root: str | Path) -> dict:
    """Write immutable-intent byte/split pins before any evaluation is run.

    This command refuses to replace an existing freeze.  A different protocol
    requires a new experiment/version, preserving the previous evidence.
    """
    root = Path(root)
    target = root / "evidence" / "protocol-freeze.json"
    if target.exists():
        raise FileExistsError(f"protocol already frozen: {target}")
    from datetime import datetime, timezone
    files = ["protocol.json", "lggr_swarm_lab/fixtures.py", "lggr_swarm_lab/oracle.py", "tests/test_oracle.py"]
    receipt = {
        "schema": "protocol-freeze.v1", "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "phase": "before_held_out_evaluation", "authority_effect": "None",
        "files": {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files},
        "splits": {split: {"seed": seed, "case_count": len(generate_cases(split)),
                           "case_sha256": digest(generate_cases(split)),
                           "per_family": {family: VARIANTS_PER_FAMILY[split] for family in FAMILIES}}
                   for split, seed in SPLIT_SEEDS.items()},
        "operational_blinding": "Controllers receive public contract, planner proposals and actual tool results only. Family, seed, variant, original semantics and independent judge are absent from their input. Host-side Python code is inspectable, so this is a data-flow boundary rather than cryptographic secrecy.",
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    print(json.dumps(freeze_protocol(parser.parse_args().freeze), indent=2, sort_keys=True))
