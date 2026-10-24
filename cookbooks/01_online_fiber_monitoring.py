"""Cookbook 01: Online Fiber Monitoring and Instant Collision Detection.

Demonstrates a two-stage agent handoff (Specifier -> Implementer) where
intermediate summary reports share representations but diverge on downstream
ground-truth requirements, triggering online collision detection.

AuthorityEffect: None.
Standard library only: Python 3.10+ (fractions, json, typing).
Claim Hygiene: Governed by Claim Hygiene Rule (zero forbidden terms).

Artifact Summary:
1. What it supports: Demonstrates online detection of report-fiber collisions in a
   two-stage agent handoff when boundary reports compress divergent downstream queries.
2. What it does not support: Does not establish that unobserved states are collision-free.
3. Narrowest defensible claim: When two observed states share an identical report while
   differing on the declared query, the monitor identifies the colliding pair and
   transitions contract status to OBSTRUCTED_LGGR.
4. Next test needed: Adaptive online schema refinement evaluating synthesized report
   features against streaming task distributions.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

# Ensure repository root is on sys.path for direct script execution
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from lggr.streaming import StreamingFiberMonitor


def run_online_fiber_monitoring_demo() -> dict[str, Any]:
    """Execute streaming observation of two agent handoffs and detect fiber collision."""
    # Initialize online fiber monitor with declared scope
    monitor = StreamingFiberMonitor(scope_id="agentic-pipeline-handoff-v1")

    # Step 1: Task 1 Specification -> Intermediate Report -> Downstream Query
    # Specifier abstracts task requirement into boundary report:
    task_1_id = "task_batch_001"
    task_1_report = {
        "workload_type": "distributed_etl",
        "target_environment": "production",
        "data_classification": "confidential",
    }
    # Ground truth downstream requirement for Task 1:
    task_1_query = {
        "requires_isolated_vpc": True,
        "encryption_at_rest": "customer_managed_kms",
        "approval_tier": "Tier-3",
    }

    print("=" * 72)
    print("Cookbook 01: Online Fiber Monitoring and Instant Collision Detection")
    print("=" * 72)
    print(f"\n[Step 1] Ingesting observation for {task_1_id}...")
    receipt_1 = monitor.observe(
        state_id=task_1_id,
        report=task_1_report,
        query=task_1_query,
        metadata={"agent": "specifier_agent_v1", "timestamp": "2026-10-24T02:00:00Z"},
    )
    print(f"  Step Status:     {receipt_1['status']}")
    print(f"  Contract Status: {receipt_1['contract_status']}")
    print(f"  Fiber Status:    {receipt_1['meaning']}")

    # Step 2: Task 2 Specification -> Intermediate Report -> Downstream Query
    # A distinct task with divergent requirements is compressed into the same report:
    task_2_id = "task_batch_002"
    task_2_report = {
        "workload_type": "distributed_etl",
        "target_environment": "production",
        "data_classification": "confidential",
    }
    # Divergent downstream requirement for Task 2 (e.g., standard KMS, lower approval):
    task_2_query = {
        "requires_isolated_vpc": False,
        "encryption_at_rest": "default_cloud_kms",
        "approval_tier": "Tier-1",
    }

    print(f"\n[Step 2] Ingesting observation for {task_2_id}...")
    receipt_2 = monitor.observe(
        state_id=task_2_id,
        report=task_2_report,
        query=task_2_query,
        metadata={"agent": "specifier_agent_v1", "timestamp": "2026-10-24T02:01:00Z"},
    )
    print(f"  Step Status:     {receipt_2['status']}")
    print(f"  Contract Status: {receipt_2['contract_status']}")
    print(f"  Fiber Status:    {receipt_2['meaning']}")

    # Check collision detection
    if monitor.is_obstructed:
        print("\n[Collision Alert] Report-fiber collision detected online!")
        pair = receipt_2["colliding_pair"]
        print(f"  Left State:  {pair['left']['state_id']}")
        print(f"  Right State: {pair['right']['state_id']}")
        print("  Shared Report:")
        print(f"    {json.dumps(pair['left']['report'])}")
        print("  Divergent Queries:")
        print(f"    Left:  {json.dumps(pair['left']['query'])}")
        print(f"    Right: {json.dumps(pair['right']['query'])}")

    # Emit final summary receipt
    summary_receipt = monitor.get_receipt()
    print("\n[Final Summary Receipt]")
    print(json.dumps(summary_receipt, indent=2))

    return summary_receipt


def main() -> int:
    receipt = run_online_fiber_monitoring_demo()
    assert receipt["status"] == "REPORT_INSUFFICIENT", "Expected collision status"
    assert receipt["contract_status"] == "OBSTRUCTED_LGGR", "Expected obstructed contract"
    print("\nVerification check passed: Online collision detected cleanly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
