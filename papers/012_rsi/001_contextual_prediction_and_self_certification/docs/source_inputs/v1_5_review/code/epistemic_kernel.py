"""Exact finite checks for the epistemic no-go monograph.

Hermetic: standard library only, exact rationals (fractions.Fraction), no
imports from the monorepo. These checks cover the finite statements of the
monograph that need no linear-programming solver. The exact l1 defect and its
dual witness are computed by the Rust kernel named in section 6 of the
monograph and are not reproduced here.

Authority status: None. A passing check records that a finite statement holds
on the stated fixture; it carries no standing.
"""

from __future__ import annotations

import hashlib
import itertools
from fractions import Fraction
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Result I: Bell cover, supports and global assignments
# ---------------------------------------------------------------------------

Context = Tuple[int, int]
Outcome = Tuple[int, int]
Table = Dict[Context, Dict[Outcome, Fraction]]
Assignment = Tuple[int, int, int, int]  # (a0, a1, b0, b1)

CONTEXTS: Tuple[Context, ...] = ((0, 0), (0, 1), (1, 0), (1, 1))
ALL_ASSIGNMENTS: Tuple[Assignment, ...] = tuple(itertools.product((0, 1), repeat=4))


def restrict(g: Assignment, ctx: Context) -> Outcome:
    """Outcome the global assignment g induces on context (x, y)."""
    x, y = ctx
    return (g[x], g[2 + y])


def pr_box() -> Table:
    """Popescu-Rohrlich box: a xor b = x and y, uniform on the two allowed outcomes."""
    table: Table = {}
    for x, y in CONTEXTS:
        table[(x, y)] = {
            (a, b): Fraction(1, 2) for a in (0, 1) for b in (0, 1) if (a ^ b) == (x & y)
        }
    return table


def classical_mixture() -> Table:
    """Equal mixture of two deterministic global assignments."""
    g1: Assignment = (0, 0, 0, 0)
    g2: Assignment = (1, 1, 1, 1)
    table: Table = {ctx: {} for ctx in CONTEXTS}
    for g in (g1, g2):
        for ctx in CONTEXTS:
            o = restrict(g, ctx)
            table[ctx][o] = table[ctx].get(o, Fraction(0)) + Fraction(1, 2)
    return table


def near_tsirelson() -> Table:
    """Weights 17/40 on equal outcomes and 3/40 on unequal ones; exchanged at (1, 1)."""
    table: Table = {}
    for x, y in CONTEXTS:
        hi, lo = Fraction(17, 40), Fraction(3, 40)
        if (x, y) == (1, 1):
            hi, lo = lo, hi
        table[(x, y)] = {(a, b): (hi if a == b else lo) for a in (0, 1) for b in (0, 1)}
    return table


def is_distribution(table: Table) -> bool:
    return all(sum(row.values()) == 1 and all(v >= 0 for v in row.values()) for row in table.values())


def supported(table: Table, g: Assignment) -> bool:
    """g is a supported global assignment if every context outcome has positive weight."""
    return all(table[ctx].get(restrict(g, ctx), Fraction(0)) > 0 for ctx in CONTEXTS)


def supported_global_assignments(table: Table) -> List[Assignment]:
    return [g for g in ALL_ASSIGNMENTS if supported(table, g)]


def marginalises(joint: Dict[Assignment, Fraction], table: Table) -> bool:
    """Exact test: the joint over assignments restricts to every context's distribution."""
    for ctx in CONTEXTS:
        induced: Dict[Outcome, Fraction] = {}
        for g, w in joint.items():
            o = restrict(g, ctx)
            induced[o] = induced.get(o, Fraction(0)) + w
        expected = {o: w for o, w in table[ctx].items() if w != 0}
        induced = {o: w for o, w in induced.items() if w != 0}
        if induced != expected:
            return False
    return True


def chsh_value(table: Table) -> Fraction:
    """E(0,0) + E(0,1) + E(1,0) - E(1,1), with E the correlation (-1)^(a xor b)."""

    def corr(ctx: Context) -> Fraction:
        return sum(((-1) ** (a ^ b)) * w for (a, b), w in table[ctx].items())

    return corr((0, 0)) + corr((0, 1)) + corr((1, 0)) - corr((1, 1))


def classical_chsh_bound() -> Fraction:
    """Maximum CHSH value over the sixteen deterministic strategies."""
    best = Fraction(-10)
    for g in ALL_ASSIGNMENTS:
        e = {ctx: Fraction((-1) ** (restrict(g, ctx)[0] ^ restrict(g, ctx)[1])) for ctx in CONTEXTS}
        best = max(best, e[(0, 0)] + e[(0, 1)] + e[(1, 0)] - e[(1, 1)])
    return best


# ---------------------------------------------------------------------------
# Result II: fiber lemma and the swap-dynamics witness
# ---------------------------------------------------------------------------

K2 = [(a, b) for a in (0, 1) for b in (0, 1)]


def all_functions(domain: Sequence[int], codomain: Sequence[int]) -> Iterable[Dict[int, int]]:
    for values in itertools.product(codomain, repeat=len(domain)):
        yield dict(zip(domain, values))


def fiber_lemma_holds(
    E: Callable[[object], object], q: Callable[[object], object], W: Sequence[object]
) -> bool:
    """If some f has f(E(w)) = q(w) for all w, then E(w) = E(w') implies q(w) = q(w')."""
    reports = sorted({E(w) for w in W}, key=repr)
    answers = sorted({q(w) for w in W}, key=repr)
    has_f = False
    for values in itertools.product(answers, repeat=len(reports)):
        f = dict(zip(reports, values))
        if all(f[E(w)] == q(w) for w in W):
            has_f = True
            break
    if not has_f:
        return True  # vacuous direction
    return all(q(w) == q(v) for w in W for v in W if E(w) == E(v))


def proj(s: Tuple[int, int]) -> int:
    return s[0]


def swap(s: Tuple[int, int]) -> Tuple[int, int]:
    return (s[1], s[0])


def no_function_recovers_state_from_report() -> bool:
    """No f : report -> state satisfies f(proj(s)) = s on F_2^2."""
    for values in itertools.product(K2, repeat=2):
        f = dict(zip((0, 1), values))
        if all(f[proj(s)] == s for s in K2):
            return False
    return True


def swap_not_intertwined() -> bool:
    """No Fbar with proj(swap(s)) = Fbar(proj(s)) for all s."""
    for values in itertools.product((0, 1), repeat=2):
        fbar = dict(zip((0, 1), values))
        if all(proj(swap(s)) == fbar[proj(s)] for s in K2):
            return False
    return True


# ---------------------------------------------------------------------------
# Result III: hash-chain truncation, relabeling
# ---------------------------------------------------------------------------

Entry = Tuple[str, str]  # (payload, link)


def _link(prev: str, payload: str) -> str:
    return hashlib.sha256((prev + "|" + payload).encode("utf-8")).hexdigest()


def build_ledger(genesis: str, payloads: Sequence[str]) -> List[Entry]:
    entries: List[Entry] = []
    prev = genesis
    for p in payloads:
        prev = _link(prev, p)
        entries.append((p, prev))
    return entries


def verify_ledger(genesis: str, entries: Sequence[Entry]) -> bool:
    prev = genesis
    for payload, link in entries:
        if _link(prev, payload) != link:
            return False
        prev = link
    return True


def tip(genesis: str, entries: Sequence[Entry]) -> str:
    return entries[-1][1] if entries else genesis


def complete_against(genesis: str, entries: Sequence[Entry], pinned_tip: str) -> bool:
    """Completeness needs a tip pinned outside the ledger."""
    return verify_ledger(genesis, entries) and tip(genesis, entries) == pinned_tip


def relabel01(n: int) -> int:
    return 1 if n == 0 else 0 if n == 1 else n


def relabel_carrier(K: Sequence[int]) -> List[int]:
    return [relabel01(n) for n in K]


def first_is_zero(K: Sequence[int]) -> bool:
    return bool(K) and K[0] == 0


def invariant_verdict(K: Sequence[int]) -> int:
    """A verdict that reads only the multiset of block sizes; blind to relabeling."""
    return len(set(K))


# ---------------------------------------------------------------------------
# Result IV: three-role authority gate (finite model of the policy)
# ---------------------------------------------------------------------------


class Refusal(Exception):
    """Typed refusal; the first element of args is the refusal kind."""

    @property
    def kind(self) -> str:
        return str(self.args[0])


def verify_three_role(
    attempt_id: str,
    proposer: str,
    evaluator: str,
    authorizer: str,
    authorizer_root: Optional[str],
    basis: str,
    admitted_roots: Sequence[str],
) -> Dict[str, str]:
    """Return a receipt carrying no authority, or raise a typed Refusal."""
    if not attempt_id.strip():
        raise Refusal("MALFORMED")
    for ident in (proposer, evaluator, authorizer):
        if not ident.strip():
            raise Refusal("MALFORMED")
    if proposer == authorizer:
        raise Refusal("SELF_AUTHORIZATION_PROPOSER")
    if evaluator == authorizer:
        raise Refusal("SELF_AUTHORIZATION_EVALUATOR")
    if proposer == evaluator:
        raise Refusal("SELF_EVALUATION")
    if basis not in {"certificate", "prose"}:
        raise Refusal("MALFORMED")
    if basis == "prose":
        raise Refusal("PROSE_AUTHORITY")
    if authorizer_root is None or authorizer_root not in admitted_roots or authorizer_root in (proposer, evaluator):
        raise Refusal("NO_EXTERNAL_ROOT")
    return {"attempt_id": attempt_id, "root": authorizer_root, "authority_effect": "None"}


def compose_attempts(attempts: Sequence[Dict[str, object]]) -> Optional[Dict[str, str]]:
    """A refused link poisons the composition; otherwise the last receipt."""
    last: Optional[Dict[str, str]] = None
    for a in attempts:
        last = verify_three_role(**a)
    return last
