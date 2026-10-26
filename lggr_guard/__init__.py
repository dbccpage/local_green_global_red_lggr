"""lggr_guard: catch Local Green, Global Red composition failures before they merge.

    from lggr_guard import Change, Check, Metric, compose_check
    report = compose_check(main_state, [change_a, change_b], [probe], observe=observe, metrics=[threshold])

See lggr_guard/README.md. AuthorityEffect: None.
"""
from .compose import Change, Check, Metric, compose_check
from .frozen import FrozenDecisions
from .log import DecisionLog

__all__ = ["Change", "Check", "Metric", "compose_check", "FrozenDecisions", "DecisionLog"]
