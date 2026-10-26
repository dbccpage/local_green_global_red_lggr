"""Recipe: authority firewall (guide 02).

The host freezes the policy, builds every step witness, and takes the global
sample from a check the proposer cannot reach. A witness made under any other
policy, evaluator, spec, or authority is flagged AUTHORITY_REQUIRED. A sample
the proposer supplies never reaches the monitor.

AuthorityEffect: None.
Standard library only: Python 3.10+.

Artifact Summary:
1. What it supports: Host-side refusal of proposer-supplied global samples and detection of witnesses made under a changed policy manifest.
2. What it does not support: Authentication of identities, or a receipt as permission to merge, deploy, or spend.
3. Narrowest defensible claim: In the demo the honest run ends COMPOSITION_VERIFIED, the loosened-policy witness yields AUTHORITY_REQUIRED with code POLICY_MANIFEST_CHANGED, the proposer sample yields GLOBAL_SAMPLE_REJECTED, and an open obligation yields WITNESS_INCOMPLETE with the obligation retained.
4. Host duty that remains: Keep the policy out of the agent's reach, run the global check yourself, and keep unresolved_obligations until an external admission clears them.
"""
from __future__ import annotations

import dataclasses
from pathlib import Path
import sys
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lggr import BudgetPolicy, StateRef, StepWitness, StreamingAuditMonitor, make_witness  # noqa: E402

from learn.support import dumps, finish  # noqa: E402

RECIPE_ID = "authority_firewall"
EXPECTED_STATUS = "AUTHORITY_REQUIRED"


class AuthorityFirewall:
    """Host-owned gate between a proposing agent and the tracked state."""

    def __init__(self, policy: BudgetPolicy, baseline: StateRef) -> None:
        self.policy = policy
        self.audit = StreamingAuditMonitor(policy, baseline)

    def admit(self, before: StateRef, after: StateRef, *, global_sample: int | bool,
              sample_source: str, obligations: tuple[str, ...] = ()) -> dict[str, Any]:
        """Normal path: the host builds the witness from the frozen policy."""
        witness = make_witness(self.policy, before, after,
                               witness_id=f"w{len(self.audit.steps) + 1:03d}", obligations=obligations)
        return self.admit_witness(witness, global_sample=global_sample, sample_source=sample_source)

    def admit_witness(self, witness: StepWitness, *, global_sample: int | bool,
                      sample_source: str) -> dict[str, Any]:
        """Path for a witness that arrives from elsewhere, such as a sub-harness or a tool."""
        if sample_source != "external":
            return {"status": "GLOBAL_SAMPLE_REJECTED", "authority_effect": "None",
                    "meaning": "The global sample must come from outside the proposing stage."}
        return self.audit.step(witness, global_evaluator_sample=global_sample)

    def verdict(self) -> dict[str, Any]:
        return self.audit.get_receipt()


def _policy() -> BudgetPolicy:
    return BudgetPolicy(policy_id="deploy-budget/v1", spec_id="spend-spec/v1", evaluator_id="ci-local/v1",
                        authority_id="release-owner", allowed_states=(0, 1, 2), max_step=1, max_total=1,
                        query_scope="every_prefix")


def demo() -> dict[str, Any]:
    policy = _policy()
    s0, s1 = StateRef("s0", 0), StateRef("s1", 1)

    honest = AuthorityFirewall(policy, s0)
    honest.admit(s0, s1, global_sample=1, sample_source="external")
    honest_receipt = honest.verdict()

    # The agent built its own witness after raising max_total from 1 to 2.
    tampered = AuthorityFirewall(policy, s0)
    loosened = dataclasses.replace(policy, max_total=2)
    tampered.admit_witness(make_witness(loosened, s0, s1, witness_id="w001"),
                           global_sample=1, sample_source="external")
    tampered_receipt = tampered.verdict()

    self_signed = AuthorityFirewall(policy, s0).admit(s0, s1, global_sample=1, sample_source="proposer")

    owed = AuthorityFirewall(policy, s0)
    owed.admit(s0, s1, global_sample=1, sample_source="external", obligations=("recheck_schema",))
    owed_receipt = owed.verdict()

    return finish({
        "recipe_id": RECIPE_ID,
        "schema": tampered_receipt["schema"],
        "authority_effect": tampered_receipt["authority_effect"],
        "status": tampered_receipt["status"],
        "tampered_codes": sorted({f["code"] for f in tampered_receipt["findings"]
                                  if f["kind"] == "AUTHORITY_REQUIRED"}),
        "honest_status": honest_receipt["status"],
        "honest_certified": honest_receipt["composition_certified"],
        "self_signed_status": self_signed["status"],
        "owed_status": owed_receipt["status"],
        "owed_obligations": owed_receipt["unresolved_obligations"],
    })


def main() -> int:
    row = demo()
    print(dumps(row))
    return 0 if row["status"] == EXPECTED_STATUS else 1


if __name__ == "__main__":
    sys.exit(main())
