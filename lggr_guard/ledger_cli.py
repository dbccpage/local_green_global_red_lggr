"""Ledger-mode CLI (dispatched from ``python -m lggr_guard``). Run it from the host, never from a worker.

AuthorityEffect: None.

  python -m lggr_guard init       --approved-by NAME          checkpoint main + anchor its facts
  python -m lggr_guard check      BRANCH [--declares JSON]     gate a candidate (exit 0 = COMPOSITION_VERIFIED)
  python -m lggr_guard accept     BRANCH --approved-by NAME    check again, then record it as accepted
  python -m lggr_guard checkpoint --smoke passed               after a green post-merge smoke on main
  python -m lggr_guard blame                                   after a red smoke: which pending set broke what
  python -m lggr_guard clear      CHANGE OBLIGATION --approved-by NAME
  python -m lggr_guard status
  python -m lggr_guard.ledger_demo [--json]

Common flags: --repo . --main main --suite .lggr/suite.py --ledger <git-common-dir>/lggr-guard/ledger.jsonl
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .replay import GitComposer, candidate_from_branch, git, load_suite_from_ref, rev_parse
from .gate import CompositionGate
from .ledger import Ledger


def _ledger_path(args: argparse.Namespace) -> Path:
    if args.ledger:
        return Path(args.ledger)
    common = git(Path(args.repo), "rev-parse", "--git-common-dir").stdout.decode().strip()
    return (Path(args.repo) / common / "lggr-guard" / "ledger.jsonl").resolve()


def _gate(args: argparse.Namespace, ledger: Ledger) -> CompositionGate:
    if ledger.checkpoint is None:
        raise SystemExit("no checkpoint yet: run `python -m lggr_guard init --approved-by <owner>` first")
    suite = load_suite_from_ref(args.repo, args.main, args.suite)
    return CompositionGate(suite, GitComposer(args.repo, ledger.checkpoint["ref"], suite.observe), ledger)


def _candidate(args: argparse.Namespace):
    declares = json.loads(args.declares) if args.declares else {}
    return candidate_from_branch(args.repo, args.branch, args.main, change_id=args.id or args.branch,
                              declares=declares, obligations=tuple(args.obligation or ()))


def _print(obj) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    p = argparse.ArgumentParser(prog="lggr_guard", description=__doc__.split("\n")[0])
    p.add_argument("--repo", default=".")
    p.add_argument("--main", default="main")
    p.add_argument("--suite", default=".lggr/suite.py")
    p.add_argument("--ledger")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init"); s.add_argument("--approved-by", required=True)
    for name in ("check", "accept"):
        s = sub.add_parser(name)
        s.add_argument("branch")
        s.add_argument("--id")
        s.add_argument("--declares", help='JSON object of facts this change says it alters, e.g. \'{"review.model": "sonnet"}\'')
        s.add_argument("--obligation", action="append")
        if name == "accept":
            s.add_argument("--approved-by", required=True)
    s = sub.add_parser("checkpoint"); s.add_argument("--smoke", required=True, choices=("passed",))
    sub.add_parser("blame")
    s = sub.add_parser("clear"); s.add_argument("change_id"); s.add_argument("obligation")
    s.add_argument("--approved-by", required=True)
    sub.add_parser("status")
    args = p.parse_args(argv)

    ledger = Ledger.load(_ledger_path(args))
    if args.cmd in ("init", "checkpoint"):
        suite = load_suite_from_ref(args.repo, args.main, args.suite)
        ref = rev_parse(Path(args.repo), args.main)
        facts = GitComposer(args.repo, ref, suite.observe).facts([])
        _print(ledger.record_checkpoint(ref, facts, smoke="passed"))
        if args.cmd == "init":
            _print(ledger.record_anchor(facts, approved_by=args.approved_by))
        return 0
    if args.cmd == "status":
        _print({"ledger": str(ledger.path), "checkpoint": ledger.checkpoint and ledger.checkpoint["ref"],
                "anchor": ledger.anchor_facts, "pending": [c.change_id for c in ledger.pending()],
                "open_obligations": ledger.open_obligations()})
        return 0
    if args.cmd == "clear":
        _print(ledger.record_clear(args.change_id, args.obligation, approved_by=args.approved_by))
        return 0
    gate = _gate(args, ledger)
    if args.cmd == "blame":
        receipt = gate.blame()
        _print(receipt)
        return 0 if receipt["status"] == "COMPOSITION_VERIFIED" else 1
    change = _candidate(args)
    receipt = gate.check(change)
    _print(receipt)
    if receipt["status"] != "COMPOSITION_VERIFIED":
        return 1
    if args.cmd == "accept":
        _print(ledger.record_accept(change, receipt, approved_by=args.approved_by))
    return 0


if __name__ == "__main__":
    sys.exit(main())
