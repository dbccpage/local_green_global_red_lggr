"""Cookbook 04: Swarm Runtime Guard and Boundary-Sufficient LGGG Certification.

Demonstrates a multi-stage agent swarm (Specification -> Implementation -> Verification)
operating under an enriched, boundary-sufficient schema contract. Demonstrates that
when boundary reports preserve required invariants, the online monitor certifies
fiber constancy, satisfies G1-G4 conditional gluing, and maintains zero evaluator
defect (Delta_E = 0, composable LGGG).

AuthorityEffect: None.
Standard library only: Python 3.10+ (fractions, json, typing).
Claim Hygiene: Governed by Claim Hygiene Rule (zero forbidden terms).

Artifact Summary:
1. What it supports: Demonstrates online verification of boundary-sufficient schema
   contracts where report fibers are constant and step witnesses satisfy G1-G4 gluing,
   certifying composable LGGG (Delta_E = 0).
2. What it does not support: Does not claim that every heuristic agent swarm can be
   made boundary-sufficient without domain-specific schema engineering.
3. Narrowest defensible claim: When boundary reports preserve fiber constancy for the
   declared downstream query and local step witnesses satisfy G1-G4, the composed
   defect Delta_E equals zero throughout the streaming trace.
4. Next test needed: Automated schema enrichment synthesizing minimal boundary-sufficient
   projections from observed counterexample traces.
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

from lggr.streaming import StreamingAuditMonitor, StreamingFiberMonitor
from lggr.witnesses import BudgetPolicy, StateRef, make_witness


def run_swarm_runtime_guard_demo() -> dict[str, Any]:
    """Execute multi-stage swarm runtime guard with boundary-sufficient schema certification."""
    print("=" * 72)
    print("Cookbook 04: Swarm Runtime Guard and Boundary-Sufficient LGGG Certification")
    print("=" * 72)

    # -------------------------------------------------------------------------
    # Phase 1: Boundary-Sufficient Fiber Monitoring
    # -------------------------------------------------------------------------
    print("\n--- Phase 1: Boundary-Sufficient Fiber Monitoring ---")
    fiber_monitor = StreamingFiberMonitor(scope_id="swarm-enriched-schema-v1")

    # In an enriched schema, reports include complete behavioral signatures:
    # (task_type, target_env, auth_scope, timeout_sec, isolation_level)
    task_A_report = {
        "workload_type": "distributed_etl",
        "target_environment": "production",
        "data_classification": "confidential",
        "requires_vpc_peering": True,
        "isolation_tier": "Tier-3",
    }
    task_A_query = {"approved": True, "firewall_rule": "ALLOW_PEER_SECURE"}

    task_B_report = {
        "workload_type": "distributed_etl",
        "target_environment": "production",
        "data_classification": "confidential",
        "requires_vpc_peering": False,
        "isolation_tier": "Tier-1",
    }
    task_B_query = {"approved": True, "firewall_rule": "ALLOW_STANDARD_INGRESS"}

    print("Ingesting enriched state A...")
    rec_A = fiber_monitor.observe("task_state_A", task_A_report, task_A_query)
    print(f"  State A Status: {rec_A['status']}, Contract: {rec_A['contract_status']}")

    print("Ingesting enriched state B...")
    rec_B = fiber_monitor.observe("task_state_B", task_B_report, task_B_query)
    print(f"  State B Status: {rec_B['status']}, Contract: {rec_B['contract_status']}")

    fiber_receipt = fiber_monitor.get_receipt()
    print(f"  Fiber Summary Status:   {fiber_receipt['status']}")
    print(f"  Contract Status:        {fiber_receipt['contract_status']}")
    assert fiber_receipt["status"] == "DECODER_VERIFIED", "Expected verified decoder"

    # -------------------------------------------------------------------------
    # Phase 2: Multi-Stage Swarm Step Witness Composition (G1-G4)
    # -------------------------------------------------------------------------
    print("\n--- Phase 2: Multi-Stage Swarm Step Witness Composition ---")
    policy = BudgetPolicy(
        allowed_states=(0, 1, 2, 3),
        max_step=1,
        max_total=3,
        query_scope="every_prefix",
        evaluator_id="swarm-stage-evaluator/v1",
        spec_id="stage-progression/v1",
        authority_id="swarm-governor/v1",
    )

    s0 = StateRef("stage_0_spec", 0)
    s1 = StateRef("stage_1_codegen", 1)
    s2 = StateRef("stage_2_review", 2)
    s3 = StateRef("stage_3_deploy", 3)

    audit_monitor = StreamingAuditMonitor(policy, s0)

    # Stage 1: Specification Agent -> Codegen Agent (0 -> 1)
    print("\n[Stage 1] Specification Agent handoff to Codegen Agent...")
    w1 = make_witness(policy, s0, s1, witness_id="handoff_spec_to_code")
    r1 = audit_monitor.step(w1, global_evaluator_sample=1, step_cost=10)
    print(f"  Step Status:     {r1['status']}")
    print(f"  Contract Status: {r1['contract_status']}")
    print(f"  Defect:          {r1['defect']} ({r1['classification']})")

    # Stage 2: Codegen Agent -> Review Agent (1 -> 2)
    print("\n[Stage 2] Codegen Agent handoff to Review Agent...")
    w2 = make_witness(policy, s1, s2, witness_id="handoff_code_to_review")
    r2 = audit_monitor.step(w2, global_evaluator_sample=1, step_cost=12)
    print(f"  Step Status:     {r2['status']}")
    print(f"  Contract Status: {r2['contract_status']}")
    print(f"  Defect:          {r2['defect']} ({r2['classification']})")

    # Stage 3: Review Agent -> Deploy Agent (2 -> 3)
    print("\n[Stage 3] Review Agent handoff to Deploy Agent...")
    w3 = make_witness(policy, s2, s3, witness_id="handoff_review_to_deploy")
    r3 = audit_monitor.step(w3, global_evaluator_sample=1, step_cost=8)
    print(f"  Step Status:     {r3['status']}")
    print(f"  Contract Status: {r3['contract_status']}")
    print(f"  Defect:          {r3['defect']} ({r3['classification']})")

    audit_receipt = audit_monitor.get_receipt()
    print("\n[Final Audit Summary Receipt]")
    print(json.dumps(audit_receipt, indent=2))

    return {
        "fiber_receipt": fiber_receipt,
        "audit_receipt": audit_receipt,
    }


def main() -> int:
    receipts = run_swarm_runtime_guard_demo()
    assert receipts["fiber_receipt"]["status"] == "DECODER_VERIFIED"
    assert receipts["audit_receipt"]["status"] == "COMPOSITION_VERIFIED"
    assert receipts["audit_receipt"]["composition_certified"] is True
    assert receipts["audit_receipt"]["contract_status"] == "COMPOSABLE_LGGG"
    print("\nVerification check passed: Composable LGGG certified across all stages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
