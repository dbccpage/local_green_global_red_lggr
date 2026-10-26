"""lggr_guard: catch Local Green, Global Red composition failures before they merge.

Batch mode (compose a set of pending changes, alone and together):

    from lggr_guard import Change, Check, Metric, compose_check
    report = compose_check(main_state, [change_a, change_b], [probe], observe=observe, metrics=[threshold])

Ledger mode (gate each candidate against everything accepted since the last full check):

    from lggr_guard import CompositionGate, GitComposer, Ledger, candidate_from_branch, load_suite_from_ref

See lggr_guard/README.md and lggr_guard/LEDGER.md. AuthorityEffect: None.
"""
from .compose import Change, Check, Metric, compose_check
from .frozen import FrozenDecisions
from .gate import SCHEMA, CompositionGate, minimal_failing_set
from .ledger import Ledger, LedgerTampered
from .log import DecisionLog
from .model import Candidate, Contract, Fact, Suite, drift_budget, equals
from .replay import (CompositionError, GitComposer, MemoryComposer, candidate_from_branch,
                     load_suite_from_file, load_suite_from_ref, run_json)

__all__ = [
    # batch mode
    "Change", "Check", "Metric", "compose_check", "FrozenDecisions", "DecisionLog",
    # ledger mode
    "SCHEMA", "Candidate", "CompositionError", "CompositionGate", "Contract", "Fact", "GitComposer",
    "Ledger", "LedgerTampered", "MemoryComposer", "Suite", "candidate_from_branch", "drift_budget",
    "equals", "load_suite_from_file", "load_suite_from_ref", "minimal_failing_set", "run_json",
]
