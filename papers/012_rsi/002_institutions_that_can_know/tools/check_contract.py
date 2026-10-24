#!/usr/bin/env python3
"""Inspect the proposed example packet; this is not an authorization verifier."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def check() -> None:
    packet = yaml.safe_load((ROOT / "contracts/anomalon_institutional_reasoning.contract.yaml").read_text(encoding="utf-8"))
    if packet.get("schema_name") != "InstitutionalComparisonPacket":
        raise ValueError("Unexpected contract schema")
    if packet.get("AuthorityEffect") != "None" or packet.get("example_only") is not True:
        raise ValueError("Expected an example with no authority effect")
    def fields(value, key):
        if isinstance(value, dict):
            for k, v in value.items():
                if k == key:
                    yield v
                yield from fields(v, key)
        elif isinstance(value, list):
            for v in value:
                yield from fields(v, key)
    permissions = list(fields(packet, "execution_permitted"))
    if permissions != [False]:
        raise ValueError("Example must carry exactly one execution_permitted: false")
    print("PASS: parsed proposed contract; example_only=true; no execution permission")


if __name__ == "__main__":
    check()
