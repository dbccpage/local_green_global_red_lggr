"""Cookbook 02: Streaming Budget Audit and Mid-Flight Early Stopping.

Demonstrates a multi-step agent tool trajectory monitored under an every_prefix
budget policy, showing instant mid-flight alerting and early stopping when
cumulative prefix drift exceeds the declared bound.

AuthorityEffect: None.
Standard library only: Python 3.10+ (fractions, json, typing).
Claim Hygiene: Governed by Claim Hygiene Rule (zero forbidden terms).

Artifact Summary:
1. What it supports: Demonstrates online detection of prefix budget violations
   under the declared every_prefix policy in a finite step-witness stream.
2. What it does not support: Does not predict arbitrary unobserved trajectories or
   assert security against unmodeled environment transitions.
3. Narrowest defensible claim: Under every_prefix evaluation, any intermediate
   cumulative delta exceeding the declared max_total bound triggers an online ALERT
   at the exact step of excursion.
4. Next test needed: Live multi-turn interactive tool chains with dynamic branch
   selection under stochastic API costs.
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

from lggr.streaming import StreamingAuditMonitor
from lggr.witnesses import BudgetPolicy, StateRef, make_witness


def run_streaming_budget_audit_demo() -> dict[str, Any]:
    """Execute streaming step-witness audit with early stopping on prefix excursion."""
    print("=" * 72)
    print("Cookbook 02: Streaming Budget Audit and Mid-Flight Early Stopping")
    print("=" * 72)

    # Define protected budget policy with strict every_prefix scope:
    # State values represent cumulative resource utilization units {0, 1, 2, 3, 4}.
    # Allowed single step delta: <= 2.
    # Allowed cumulative total excursion: <= 2.
    policy = BudgetPolicy(
        allowed_states=(0, 1, 2, 3, 4),
        max_step=2,
        max_total=2,
        query_scope="every_prefix",
        evaluator_id="agent-action-evaluator/v1",
        spec_id="resource-budget/v1",
        authority_id="audit-authority/v1",
    )

    s0 = StateRef("step_0_init", 0)
    s1 = StateRef("step_1_search", 1)
    s2 = StateRef("step_2_heavy_computation", 3)
    s3 = StateRef("step_3_finalize", 1)

    monitor = StreamingAuditMonitor(policy, s0)

    # Step 1: Agent performs search action (cost delta: +1)
    print("\n[Step 1] Ingesting tool action 1: initial query search...")
    w1 = make_witness(policy, s0, s1, witness_id="action_001")
    r1 = monitor.step(w1, global_evaluator_sample=1, step_cost=5)
    print(f"  Witness ID:        {r1['witness_id']}")
    print(f"  Step Status:       {r1['status']}")
    print(f"  Contract Status:   {r1['contract_status']}")
    print(f"  Cumulative Delta:  {r1['cumulative_delta']} (bound: {policy.max_total})")
    print(f"  Prefix In Bound:   {r1['g4_prefix_ok']}")

    # Step 2: Agent attempts heavy computation step (delta: +2, reaching cumulative +3)
    print("\n[Step 2] Ingesting tool action 2: high-resource batch processing...")
    w2 = make_witness(policy, s1, s2, witness_id="action_002")
    r2 = monitor.step(w2, global_evaluator_sample=1, step_cost=25)
    print(f"  Witness ID:        {r2['witness_id']}")
    print(f"  Step Status:       {r2['status']}")
    print(f"  Contract Status:   {r2['contract_status']}")
    print(f"  Cumulative Delta:  {r2['cumulative_delta']} (bound: {policy.max_total})")
    print(f"  Prefix In Bound:   {r2['g4_prefix_ok']}")

    if r2["status"] == "ALERT":
        print("\n[Early Stopping Triggered] Mid-flight budget excursion detected!")
        print(f"  Alert Reasons:     {r2['alert_reasons']}")
        print(f"  Meaning:           {r2['meaning']}")
        print("  Halting execution stream immediately before executing step 3.")

    final_receipt = monitor.get_receipt()
    print("\n[Final Summary Receipt]")
    print(json.dumps(final_receipt, indent=2))

    return final_receipt


def main() -> int:
    receipt = run_streaming_budget_audit_demo()
    assert receipt["status"] == "OBSTRUCTION_DETECTED", "Expected obstruction detection status"
    assert receipt["composition_certified"] is False, "Expected false composition certification"
    assert len(receipt["findings"]) > 0, "Expected non-empty findings"
    print("\nVerification check passed: Streaming budget audit early stopping confirmed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
