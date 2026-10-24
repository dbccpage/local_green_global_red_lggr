"""Cookbook 03: Incremental 1-Cochain Cycle Closure and Exact L1 Repair.

Demonstrates a 3-agent circular review loop (Agent A -> Agent B -> Agent C -> Agent A)
where streaming pairwise handoff values close an inconsistent cycle, triggering
online cycle closure detection, exact rational L1 repair distance calculation,
and dual witness certification.

AuthorityEffect: None.
Standard library only: Python 3.10+ (fractions, json, typing).
Claim Hygiene: Governed by Claim Hygiene Rule (zero forbidden terms).

Artifact Summary:
1. What it supports: Demonstrates online cycle closure detection on streaming directed
   graphs and exact rational weighted L1 repair distance and dual witness calculation.
2. What it does not support: Does not solve non-convex integer programming or general
   higher-degree non-graph cohomology without a boundary matrix.
3. Narrowest defensible claim: When an edge closes a cycle in the active spanning forest,
   the coboundary defect (D_1 h)_C is computed in exact rational arithmetic, and if nonzero,
   a dual witness certifies the minimal L1 repair distance.
4. Next test needed: Large scale agent swarms with chordal multi-cycle graphs and
   heterogeneous edge weights.
"""
from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import sys
from typing import Any

# Ensure repository root is on sys.path for direct script execution
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from lggr.streaming import StreamingCochainMonitor


def run_cochain_cycle_repair_demo() -> dict[str, Any]:
    """Execute streaming 1-cochain edge ingestion and cycle closure audit."""
    print("=" * 72)
    print("Cookbook 03: Incremental 1-Cochain Cycle Closure and Exact L1 Repair")
    print("=" * 72)

    monitor = StreamingCochainMonitor()

    # Step 1: Agent A (Architect) handoff to Agent B (Implementer)
    # Handoff delta/score: +1, weight: 1
    print("\n[Edge 1] Ingesting handoff Agent_A -> Agent_B (value=1, weight=1)...")
    r1 = monitor.add_edge("Agent_A", "Agent_B", value=1, weight=1)
    print(f"  Status:          {r1['status']}")
    print(f"  Cycle Detected:  {r1['cycle_detected']}")
    print(f"  Meaning:         {r1['meaning']}")

    # Step 2: Agent B (Implementer) handoff to Agent C (Reviewer)
    # Handoff delta/score: +1, weight: 1
    print("\n[Edge 2] Ingesting handoff Agent_B -> Agent_C (value=1, weight=1)...")
    r2 = monitor.add_edge("Agent_B", "Agent_C", value=1, weight=1)
    print(f"  Status:          {r2['status']}")
    print(f"  Cycle Detected:  {r2['cycle_detected']}")
    print(f"  Meaning:         {r2['meaning']}")

    # Step 3: Agent C (Reviewer) closes loop back to Agent A (Architect)
    # Handoff delta/score: +1, weight: 1
    # Note: Circulation sum = 1 + 1 + 1 = 3 != 0 (inconsistent cycle)
    print("\n[Edge 3] Ingesting closing handoff Agent_C -> Agent_A (value=1, weight=1)...")
    r3 = monitor.add_edge("Agent_C", "Agent_A", value=1, weight=1)
    print(f"  Status:              {r3['status']}")
    print(f"  Cycle Detected:      {r3['cycle_detected']}")
    print(f"  Closure Defect:      {r3['closure_defect']}")
    print(f"  L1 Repair Distance:  {r3['l1_repair_distance']}")
    print(f"  Certificate Status:  {r3['certificate_status']}")
    print(f"  Meaning:             {r3['meaning']}")

    print("\n[Dual Witness & Optimal Potentials]")
    print(f"  Dual Witness z:      {r3['dual_witness']}")
    print(f"  Vertex Potential x:  {r3['potential']}")

    # Emit final summary receipt
    receipt = monitor.get_receipt()
    print("\n[Final Summary Receipt]")
    # Convert Fraction objects to str for clean JSON serialization
    serialized = json.dumps(receipt, default=str, indent=2)
    print(serialized)

    return receipt


def main() -> int:
    receipt = run_cochain_cycle_repair_demo()
    assert receipt["status"] == "OBSTRUCTED_CYCLE", "Expected obstructed cycle status"
    assert receipt["cycles_detected"] == 1, "Expected exactly 1 cycle detected"
    assert receipt["nonrepairable_cycles"] == 1, "Expected 1 nonrepairable cycle"
    print("\nVerification check passed: Incremental 1-cochain cycle closure verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
