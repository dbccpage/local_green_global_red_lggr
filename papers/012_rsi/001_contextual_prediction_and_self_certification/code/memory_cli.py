"""Local-only memory interface; prints checked context, never calls a provider."""

import argparse
import json
from pathlib import Path

try:
    from .residual_memory import ResidualMemory, sourced_fact
except ImportError:  # Standalone paper distribution.
    from residual_memory import ResidualMemory, sourced_fact


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    parser.add_argument("contract", type=Path)
    sub = parser.add_subparsers(dest="operation", required=True)
    sub.add_parser("init")
    learn = sub.add_parser("learn")
    learn.add_argument("source", type=Path)
    recall = sub.add_parser("recall")
    recall.add_argument("keys", nargs="+")
    prepare = sub.add_parser("prepare")
    prepare.add_argument("model")
    prepare.add_argument("prompt")
    prepare.add_argument("keys", nargs="+")
    args = parser.parse_args()
    try:
        memory = ResidualMemory(args.database, json.loads(args.contract.read_bytes()))
        if args.operation == "init":
            result = memory.initialize()
        elif args.operation == "learn":
            # Pin precisely the same bytes parsed into observations.
            from hashlib import sha256
            with args.source.open("rb") as stream:
                raw = stream.read(1_048_577)
            if len(raw) > 1_048_576:
                raise ValueError("SOURCE_TOO_LARGE")
            facts = json.loads(raw)
            if type(facts) is not dict or set(facts) != {"facts"}:
                raise ValueError("SOURCE_SCHEMA_INVALID")
            rows = [dict(**fact, source=str(args.source.resolve()),
                         source_sha256=sha256(raw).hexdigest()) for fact in facts["facts"]]
            result = memory.learn(rows)
        elif args.operation == "recall":
            result = memory.recall(args.keys)
        else:
            result = memory.prepare(args.prompt, model=args.model, keys=args.keys)
        output = dict(ok=result.ok, code=result.code, value=result.value)
    except (OSError, ValueError, TypeError, KeyError):
        output = dict(ok=False, code="MEMORY_INPUT_INVALID")
    print(json.dumps(output, ensure_ascii=True, sort_keys=True))
    return 0 if output["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
