"""Finite observation checks; the unbounded word theorem is proved in Lean."""
from itertools import product


def run_word(updates, word, state):
    for update in word:
        state = updates[update][state]
    return state


def preserves_fibers(report, updates):
    states = tuple(report)
    if any(set(update) != set(states) or not set(update.values()) <= set(states)
           for update in updates.values()):
        raise ValueError("Updates must be total endomorphisms of the declared state set")
    return all(report[update[s]] == report[update[t]]
               for update in updates.values() for s in states for t in states
               if report[s] == report[t])


def reports_agree_through(report, updates, depth):
    """Check all words through depth, including the empty word; finite only."""
    if not isinstance(depth, int) or depth < 0:
        raise ValueError("Depth must be a nonnegative integer")
    # Validate totality even when depth is zero.
    preserves_fibers(report, updates)
    return all(report[run_word(updates, word, s)] == report[run_word(updates, word, t)]
               for length in range(depth + 1) for word in product(updates, repeat=length)
               for s in report for t in report if report[s] == report[t])
