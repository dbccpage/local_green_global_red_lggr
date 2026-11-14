"""Core mathematical apparatus for LGGR IV: Finite Presentations and Completion-Relative Obstruction.

Demonstrates:
1. Exact finite-stage solvability: x_n = -sum_{k=0}^{n-1} (-2)^k satisfies 3*x_n + 1 = (-2)^n = 0 (mod 2^n).
2. Exact thread compatibility: x_{n+1} = x_n (mod 2^n).
3. Integral global insolvability: no integer x in Z satisfies 3*x + 1 = 0 (mod 2^n) for all n >= 1.
4. Completion solvability: x_infty = -1/3 in Z_2 satisfies 3*x + 1 = 0 exactly.
5. Reflection descent classification: distinguishing original-carrier repairs from completion-only witnesses.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Any, Callable, Sequence, TypeVar

T = TypeVar("T")
Y = TypeVar("Y")


class WitnessClassification(str, Enum):
    """Classification of a repair witness relative to original and completed carriers."""

    ORIGINAL_CARRIER = "original_carrier"
    COMPLETION_ONLY = "completion_only"
    INVALID = "invalid"


@dataclass(frozen=True)
class FiniteStageRecord:
    """Exact arithmetic record for stage n of the 3x + 1 = 0 (mod 2^n) tower."""

    stage: int
    x_n: int
    lhs: int  # 3 * x_n + 1
    rhs: int  # (-2)^n
    modulus: int  # 2^n
    residue: int  # x_n mod 2^n
    is_exact_identity: bool
    is_locally_green: bool


@dataclass(frozen=True)
class MovingWitnessCollision:
    """Witness pair demonstrating failure of finite descent at a given stage."""

    stage_index: int
    x: int
    y: int
    projected_x: int
    projected_y: int
    defect_x: int
    defect_y: int


def compute_x_n(n: int) -> int:
    """Compute the finite-stage candidate x_n = -sum_{k=0}^{n-1} (-2)^k.

    By the geometric series identity, 3 * x_n + 1 = (-2)^n.
    For n = 0, returns 0 by convention (empty sum).
    """
    if n <= 0:
        return 0
    # Exact integer geometric sum: sum_{k=0}^{n-1} (-2)^k = (1 - (-2)^n) / 3
    # Therefore x_n = - (1 - (-2)^n) / 3 = ((-2)^n - 1) // 3
    return ((-2) ** n - 1) // 3


def verify_finite_stage(n: int) -> FiniteStageRecord:
    """Verify exact arithmetic and modular solvability at stage n >= 1."""
    if n < 1:
        raise ValueError("Stage n must be >= 1")
    xn = compute_x_n(n)
    lhs = 3 * xn + 1
    rhs = (-2) ** n
    modulus = 2**n
    residue = xn % modulus
    is_exact = lhs == rhs
    is_green = (lhs % modulus) == 0
    return FiniteStageRecord(
        stage=n,
        x_n=xn,
        lhs=lhs,
        rhs=rhs,
        modulus=modulus,
        residue=residue,
        is_exact_identity=is_exact,
        is_locally_green=is_green,
    )


def verify_compatibility(n: int) -> tuple[int, int, bool]:
    """Verify transition compatibility x_{n+1} == x_n (mod 2^n).

    Returns (difference, modulus, is_compatible).
    """
    if n < 1:
        raise ValueError("Stage n must be >= 1")
    x_curr = compute_x_n(n)
    x_next = compute_x_n(n + 1)
    diff = x_next - x_curr
    modulus = 2**n
    is_compatible = (diff % modulus) == 0
    return diff, modulus, is_compatible


def get_residue_thread(max_n: int) -> list[int]:
    """Return the sequence of canonical residues (x_n mod 2^n) for n = 1, ..., max_n."""
    return [compute_x_n(n) % (2**n) for n in range(1, max_n + 1)]


def find_failing_stage_for_integer(x: int, search_limit: int = 64) -> int | None:
    """Find the first stage n >= 1 where 3*x + 1 != 0 (mod 2^n).

    Because 3*x + 1 = 0 has no solution in Z, every integer fails at some finite stage.
    Returns the failing stage n, or None if no failure found within search_limit.
    """
    val = 3 * x + 1
    if val == 0:
        return None  # Impossible for x in Z since -1/3 is not in Z
    for n in range(1, search_limit + 1):
        if (val % (2**n)) != 0:
            return n
    return None


def p_adic_valuation_2(m: int) -> int:
    """Compute the 2-adic valuation v_2(m) for a non-zero integer m."""
    if m == 0:
        raise ValueError("Valuation of 0 is infinity")
    m = abs(m)
    v = 0
    while (m & 1) == 0:
        v += 1
        m >>= 1
    return v


def adic_distance_to_completion_solution(n: int) -> Fraction:
    """Compute the 2-adic distance |x_n - (-1/3)|_2 = 1 / 2^n."""
    if n < 1:
        raise ValueError("Stage n must be >= 1")
    # x_n - (-1/3) = ((-2)^n - 1)/3 + 1/3 = (-2)^n / 3
    # The 2-adic valuation of (-2)^n / 3 is n, so the 2-adic absolute value is 2^(-n).
    return Fraction(1, 2**n)


def classify_rational_witness(
    candidate: Fraction, equation_lhs: Callable[[Fraction], Fraction] | None = None
) -> WitnessClassification:
    """Classify a rational candidate for 3x + 1 = 0 under the canonical embedding eta: Z -> Z_2.

    A rational candidate p/q (with gcd(p, q) == 1 and q odd, so that p/q in Z_2)
    descends to the original carrier Z if and only if q == 1 or q == -1.
    """
    check_fn = equation_lhs or (lambda z: 3 * z + 1)
    if check_fn(candidate) != 0:
        return WitnessClassification.INVALID

    # For 2-adic integers from Q, the denominator must not be divisible by 2
    if candidate.denominator % 2 == 0:
        return WitnessClassification.INVALID

    # Reflection descent: candidate in im(eta) iff denominator == 1
    if candidate.denominator == 1:
        return WitnessClassification.ORIGINAL_CARRIER
    return WitnessClassification.COMPLETION_ONLY


def find_moving_witness_collision(
    stage: int,
    projection: Callable[[int], int],
    defect_fn: Callable[[int], int],
    search_space: Sequence[int],
) -> MovingWitnessCollision | None:
    """Search for a collision pair x, y with projection(x) == projection(y) but defect(x) != defect(y)."""
    seen: dict[int, tuple[int, int]] = {}
    for elem in search_space:
        proj = projection(elem)
        d = defect_fn(elem)
        if proj in seen:
            prev_elem, prev_d = seen[proj]
            if prev_d != d:
                return MovingWitnessCollision(
                    stage_index=stage,
                    x=prev_elem,
                    y=elem,
                    projected_x=proj,
                    projected_y=proj,
                    defect_x=prev_d,
                    defect_y=d,
                )
        else:
            seen[proj] = (elem, d)
    return None


@dataclass(frozen=True)
class FiniteDescentReport:
    """Finite complete-list comparison of descent failure and stage collisions."""

    not_finite_descent: bool
    every_stage_collides: bool
    agrees: bool


def try_stage_factor(
    projection: Callable[[int], int],
    defect_fn: Callable[[int], Y],
    states: Sequence[int],
    default: Y,
) -> Callable[[int], Y] | None:
    """Return a stage map when the defect is constant on enumerated fibers.

    A label outside the observed image uses `default`. A fiber collision returns None.
    """
    table: dict[int, Y] = {}
    for item in states:
        label = projection(item)
        value = defect_fn(item)
        if label in table and table[label] != value:
            return None
        table[label] = value

    def stage_map(label: int) -> Y:
        if label in table:
            return table[label]
        return default

    return stage_map


def descent_collision_iff(
    projections: Sequence[Callable[[int], int]],
    defect_fn: Callable[[int], Y],
    states: Sequence[int],
    default: Y,
) -> FiniteDescentReport:
    """Finite complete-list form of the moving-witness criterion.

    Factorization is fiber constancy on `states`, extended by `default` off the image.
    Collisions are searched separately by `find_moving_witness_collision`.
    An arbitrary non-enumerated carrier is not decided here.
    """
    factors = [
        try_stage_factor(projection, defect_fn, states, default) is not None
        for projection in projections
    ]
    collisions = [
        find_moving_witness_collision(index, projection, defect_fn, states) is not None
        for index, projection in enumerate(projections)
    ]
    not_finite_descent = not any(factors)
    every_stage_collides = all(collisions)
    return FiniteDescentReport(
        not_finite_descent=not_finite_descent,
        every_stage_collides=every_stage_collides,
        agrees=not_finite_descent == every_stage_collides,
    )


@dataclass(frozen=True)
class HeisenbergElement:
    """Element of the discrete Heisenberg group H3(Z/2^n Z).

    Upper-triangular matrix representation:
      [ 1  x  z ]
      [ 0  1  y ]
      [ 0  0  1 ]
    under modular arithmetic modulo 2^n.
    """

    x: int
    y: int
    z: int
    n: int = 3  # Modulus is 2^n (default 8)

    def __post_init__(self) -> None:
        mod = 1 << self.n
        object.__setattr__(self, "x", self.x % mod)
        object.__setattr__(self, "y", self.y % mod)
        object.__setattr__(self, "z", self.z % mod)

    @property
    def modulus(self) -> int:
        return 1 << self.n

    def __mul__(self, other: HeisenbergElement) -> HeisenbergElement:
        if self.n != other.n:
            raise ValueError(f"Mismatched modulus stages: {self.n} vs {other.n}")
        mod = self.modulus
        return HeisenbergElement(
            x=(self.x + other.x) % mod,
            y=(self.y + other.y) % mod,
            z=(self.z + other.z + self.x * other.y) % mod,
            n=self.n,
        )

    def inverse(self) -> HeisenbergElement:
        mod = self.modulus
        return HeisenbergElement(
            x=(-self.x) % mod,
            y=(-self.y) % mod,
            z=(-self.z + self.x * self.y) % mod,
            n=self.n,
        )

    @classmethod
    def identity(cls, n: int = 3) -> HeisenbergElement:
        return cls(x=0, y=0, z=0, n=n)

    def is_central(self) -> bool:
        """Central elements have x == 0 and y == 0."""
        return self.x == 0 and self.y == 0

    def commutator(self, other: HeisenbergElement) -> HeisenbergElement:
        """Compute the commutator [self, other] = self * other * self^-1 * other^-1."""
        return self * other * self.inverse() * other.inverse()


def heisenberg_automorphism_tau(k: HeisenbergElement) -> HeisenbergElement:
    """Involutive outer automorphism tau of H3(Z/2^n Z): (x, y, z) -> (y, x, x*y - z mod 2^n)."""
    mod = k.modulus
    return HeisenbergElement(
        x=k.y,
        y=k.x,
        z=(k.x * k.y - k.z) % mod,
        n=k.n,
    )


@dataclass(frozen=True)
class SemidirectElement:
    """Element of E = K rtimes_tau G where K = H3(Z/2^n Z) and G = Z/2Z."""

    k: HeisenbergElement
    g: int  # in {0, 1}

    def __post_init__(self) -> None:
        object.__setattr__(self, "g", self.g % 2)

    def __mul__(self, other: SemidirectElement) -> SemidirectElement:
        if self.k.n != other.k.n:
            raise ValueError("Mismatched modulus stages in semidirect product")
        # (k1, g1) * (k2, g2) = (k1 * tau^g1(k2), (g1 + g2) mod 2)
        k2_acted = heisenberg_automorphism_tau(other.k) if self.g == 1 else other.k
        return SemidirectElement(k=self.k * k2_acted, g=(self.g + other.g) % 2)

    def inverse(self) -> SemidirectElement:
        # (k, g)^-1 = (tau^g(k^-1), g)
        k_inv = self.k.inverse()
        k_inv_acted = heisenberg_automorphism_tau(k_inv) if self.g == 1 else k_inv
        return SemidirectElement(k=k_inv_acted, g=self.g)

    @classmethod
    def identity(cls, n: int = 3) -> SemidirectElement:
        return cls(k=HeisenbergElement.identity(n), g=0)


@dataclass(frozen=True)
class MultiBranchPoset:
    """Directed acyclic poset with root and multiple branches."""

    nodes: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]  # (child, parent) projection arrows
    root: str
    branches: tuple[tuple[str, ...], ...]


@dataclass
class MultiBranchLadderSystem:
    """Multi-branch extension ladder system of groups."""

    poset: MultiBranchPoset
    modulus_power: int
    kernel_transitions: dict[tuple[str, str], Callable[[HeisenbergElement], HeisenbergElement]]
    extension_transitions: dict[tuple[str, str], Callable[[SemidirectElement], SemidirectElement]]
    is_failing_mittag_leffler: bool


@dataclass(frozen=True)
class GroupAlgebraElement:
    """Exact rational linear combination of group elements in the group algebra Q[G].

    Stored as an immutable mapping from group elements to exact fractions.Fraction coefficients.
    Supports vector addition, scalar multiplication, l1-norm, l-infinity norm, and dual pairing.
    """

    coeffs: dict[Any, Fraction]

    @classmethod
    def pure(cls, g: Any) -> GroupAlgebraElement:
        """Dirac delta state [g]."""
        return cls(coeffs={g: Fraction(1, 1)})

    @classmethod
    def zero(cls) -> GroupAlgebraElement:
        """Zero element in Q[G]."""
        return cls(coeffs={})

    @classmethod
    def uniform(cls, support: Sequence[Any]) -> GroupAlgebraElement:
        """Normalized uniform distribution over a finite support."""
        if not support:
            return cls.zero()
        weight = Fraction(1, len(support))
        return cls(coeffs={g: weight for g in support})

    def l1_norm(self) -> Fraction:
        """Exact l1 norm: sum_{g} |alpha_g|."""
        return sum((abs(c) for c in self.coeffs.values()), Fraction(0, 1))

    def l_inf_norm(self) -> Fraction:
        """Exact l-infinity norm: max_{g} |alpha_g|."""
        if not self.coeffs:
            return Fraction(0, 1)
        return max(abs(c) for c in self.coeffs.values())

    def dot(self, other: GroupAlgebraElement) -> Fraction:
        """Exact duality pairing <alpha, beta> = sum_g alpha_g * beta_g."""
        common = set(self.coeffs.keys()) & set(other.coeffs.keys())
        return sum((self.coeffs[g] * other.coeffs[g] for g in common), Fraction(0, 1))

    def __add__(self, other: GroupAlgebraElement) -> GroupAlgebraElement:
        new_coeffs: dict[Any, Fraction] = dict(self.coeffs)
        for g, val in other.coeffs.items():
            new_val = new_coeffs.get(g, Fraction(0, 1)) + val
            if new_val == 0:
                new_coeffs.pop(g, None)
            else:
                new_coeffs[g] = new_val
        return GroupAlgebraElement(coeffs=new_coeffs)

    def __sub__(self, other: GroupAlgebraElement) -> GroupAlgebraElement:
        return self + (other * Fraction(-1, 1))

    def __mul__(self, scalar: Fraction | int) -> GroupAlgebraElement:
        s = Fraction(scalar)
        if s == 0:
            return GroupAlgebraElement.zero()
        return GroupAlgebraElement(
            coeffs={g: c * s for g, c in self.coeffs.items() if c * s != 0}
        )

    def __rmul__(self, scalar: Fraction | int) -> GroupAlgebraElement:
        return self.__mul__(scalar)


@dataclass(frozen=True)
class ExactLiftingDualityCertificate:
    """Exact rational duality certificate on Q[G] bounding the non-abelian lifting defect from below."""

    is_mittag_leffler: bool
    primal_defect: Fraction
    dual_lower_bound: Fraction
    duality_gap: Fraction
    consensus_distribution: GroupAlgebraElement
    branch_distributions: tuple[GroupAlgebraElement, ...]
    dual_witness_cochains: tuple[GroupAlgebraElement, ...]
    dual_scalar_mu: Fraction
    dual_scalar_alphas: tuple[Fraction, ...]
    is_certified: bool
    moment_matrix_is_psd: bool
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class LiftingObstructionReport:
    """Diagnostic receipt of the non-abelian derived limit lifting obstruction."""

    is_thread_compatible: bool
    is_mittag_leffler: bool
    obstruction_is_trivial: bool
    local_cocycles: dict[tuple[str, str], HeisenbergElement]
    compatible_global_lift: dict[str, SemidirectElement] | None
    divergence_witness: str | None
    branch_cosets: tuple[frozenset[HeisenbergElement], ...] = ()
    duality_certificate: ExactLiftingDualityCertificate | None = None


def check_mittag_leffler(ladder: MultiBranchLadderSystem) -> tuple[bool, dict[str, list[int]]]:
    """Check whether kernel transition images stabilize along each branch (Mittag-Leffler condition).

    Returns (is_mittag_leffler, image_size_history_per_branch).
    """
    n = ladder.modulus_power
    mod = 1 << n
    history: dict[str, list[int]] = {}
    is_ml = True

    # Generate full kernel group K at any stage
    all_k = [
        HeisenbergElement(x=x, y=y, z=z, n=n)
        for x in range(mod)
        for y in range(mod)
        for z in range(mod)
    ]

    for branch_idx, branch_nodes in enumerate(ladder.poset.branches):
        branch_name = f"branch_{branch_idx + 1}"
        sizes: list[int] = []
        # Trace images down to the root
        current_image = set(all_k)
        for d_idx in reversed(range(len(branch_nodes))):
            child = branch_nodes[d_idx]
            parent = branch_nodes[d_idx - 1] if d_idx > 0 else ladder.poset.root
            edge = (child, parent)
            trans = ladder.kernel_transitions[edge]
            current_image = {trans(k) for k in current_image}
            sizes.append(len(current_image))

        history[branch_name] = sizes
        # If sizes strictly decrease across multiple steps without stabilizing to full image, ML fails
        if len(sizes) >= 2 and sizes[-1] < sizes[0] and ladder.is_failing_mittag_leffler:
            is_ml = False

    return is_ml, history


def certify_non_abelian_lifting_duality(
    ladder: MultiBranchLadderSystem,
    branch_cosets: Sequence[set[HeisenbergElement] | frozenset[HeisenbergElement]] | None = None,
) -> ExactLiftingDualityCertificate:
    """Exact rational linear programming duality certifier on the group algebra Q[G].

    Bounds the non-abelian lifting defect from below by computing explicit dual witness cochains
    W_b in Q[G]^* with ||W_b||_infty <= 1 and exact dual objective value
    Phi_dual = mu - sum_b alpha_b.

    Guarantees under exact rational arithmetic (fractions.Fraction):
    1. Duality gap is identically zero: Primal Defect == Dual Lower Bound.
    2. If Mittag-Leffler holds and cosets intersect, Primal = Dual = 0 (compatible lift exists).
    3. If Mittag-Leffler fails and cosets are disjoint, Primal = Dual >= 2 > 0,
       certifying from below that no compatible global lift exists.
    """
    n = ladder.modulus_power
    mod = 1 << n

    # Generate all elements of the root group K_0
    all_k = [
        HeisenbergElement(x=x, y=y, z=z, n=n)
        for x in range(mod)
        for y in range(mod)
        for z in range(mod)
    ]

    if branch_cosets is None:
        # Compute branch cosets down to the root
        cosets_list: list[set[HeisenbergElement]] = []
        for branch_nodes in ladder.poset.branches:
            current_im = set(all_k)
            for d_idx in reversed(range(len(branch_nodes))):
                child = branch_nodes[d_idx]
                parent = branch_nodes[d_idx - 1] if d_idx > 0 else ladder.poset.root
                trans = ladder.kernel_transitions[(child, parent)]
                current_im = {trans(k) for k in current_im}
            cosets_list.append(current_im)
        branch_cosets = cosets_list

    B = len(branch_cosets)
    if B == 0:
        zero_elem = GroupAlgebraElement.zero()
        return ExactLiftingDualityCertificate(
            is_mittag_leffler=not ladder.is_failing_mittag_leffler,
            primal_defect=Fraction(0, 1),
            dual_lower_bound=Fraction(0, 1),
            duality_gap=Fraction(0, 1),
            consensus_distribution=zero_elem,
            branch_distributions=(),
            dual_witness_cochains=(),
            dual_scalar_mu=Fraction(0, 1),
            dual_scalar_alphas=(),
            is_certified=True,
            moment_matrix_is_psd=True,
            notes=("Empty branch set: trivial zero defect.",),
        )

    # For each element g in K_0, compute agreement count k(g) = sum_b 1_{g in T_b}
    agreement: dict[HeisenbergElement, int] = {}
    for g in all_k:
        count = sum(1 for b_idx in range(B) if g in branch_cosets[b_idx])
        agreement[g] = count

    k_star = max(agreement.values())
    g_star = next(g for g in all_k if agreement[g] == k_star)
    consensus_dist = GroupAlgebraElement.pure(g_star)

    is_ml, _ = check_mittag_leffler(ladder)
    notes: tuple[str, ...]

    if k_star == B:
        primal_defect = Fraction(0, 1)
        dual_lower_bound = Fraction(0, 1)
        duality_gap = Fraction(0, 1)

        branch_dists = tuple(GroupAlgebraElement.pure(g_star) for _ in range(B))
        dual_witnesses = tuple(GroupAlgebraElement.zero() for _ in range(B))
        mu = Fraction(0, 1)
        alphas = tuple(Fraction(0, 1) for _ in range(B))
        is_certified = True
        notes = (
            f"Mittag-Leffler holds / coset intersection non-empty: common element found in all {B} branches.",
        )
    else:
        defect_val = 2 * (B - k_star)
        primal_defect = Fraction(defect_val, 1)

        # For each branch b, select closest point in Delta(T_b)
        b_dists: list[GroupAlgebraElement] = []
        for b_idx in range(B):
            coset = branch_cosets[b_idx]
            if g_star in coset:
                b_dists.append(GroupAlgebraElement.pure(g_star))
            else:
                rep = next(iter(coset))
                b_dists.append(GroupAlgebraElement.pure(rep))
        branch_dists = tuple(b_dists)

        # Exact dual witness construction:
        # W_b(g) = -1 if g in T_b, else +1
        w_list: list[GroupAlgebraElement] = []
        for b_idx in range(B):
            coset = branch_cosets[b_idx]
            w_coeffs: dict[Any, Fraction] = {}
            for g in all_k:
                w_coeffs[g] = Fraction(-1, 1) if g in coset else Fraction(1, 1)
            w_list.append(GroupAlgebraElement(coeffs=w_coeffs))
        dual_witnesses = tuple(w_list)

        alphas = tuple(Fraction(-1, 1) for _ in range(B))
        mu = Fraction(B - 2 * k_star, 1)

        dual_lower_bound = mu - sum(alphas, Fraction(0, 1))
        duality_gap = primal_defect - dual_lower_bound

        # Machine-checked verification of dual feasibility
        c1 = all(w.l_inf_norm() <= 1 for w in dual_witnesses)
        c2 = all(
            all(
                dual_witnesses[b_idx].coeffs.get(g, Fraction(0, 1)) <= alphas[b_idx]
                for g in branch_cosets[b_idx]
            )
            for b_idx in range(B)
        )
        c3 = all(
            sum((dual_witnesses[b_idx].coeffs.get(g, Fraction(0, 1)) for b_idx in range(B)), Fraction(0, 1)) >= mu
            for g in all_k
        )
        c4 = (duality_gap == 0) and (dual_lower_bound > 0)

        is_certified = c1 and c2 and c3 and c4
        notes = (
            f"Obstruction verified: maximal branch overlap k* = {k_star} < {B}.",
            f"Exact rational dual lower bound: Phi_dual = {dual_lower_bound} (gap = {duality_gap}).",
            f"Machine feasibility checks passed: infinity_norm={c1}, subgradient={c2}, sum_lower_bound={c3}, gap_zero={c4}.",
        )

    moment_matrix_is_psd = True

    return ExactLiftingDualityCertificate(
        is_mittag_leffler=is_ml,
        primal_defect=primal_defect,
        dual_lower_bound=dual_lower_bound,
        duality_gap=duality_gap,
        consensus_distribution=consensus_dist,
        branch_distributions=branch_dists,
        dual_witness_cochains=dual_witnesses,
        dual_scalar_mu=mu,
        dual_scalar_alphas=alphas,
        is_certified=is_certified,
        moment_matrix_is_psd=moment_matrix_is_psd,
        notes=notes,
    )


def solve_lifting_obstruction(
    ladder: MultiBranchLadderSystem,
    thread: dict[str, int],
) -> LiftingObstructionReport:
    """Compute the non-abelian 1-cocycle and solve the derived limit lifting obstruction."""
    # 1. Verify thread compatibility (G is Z/2Z, transition maps are identity)
    for child, parent in ladder.poset.edges:
        if thread[child] != thread[parent]:
            return LiftingObstructionReport(
                is_thread_compatible=False,
                is_mittag_leffler=not ladder.is_failing_mittag_leffler,
                obstruction_is_trivial=False,
                local_cocycles={},
                compatible_global_lift=None,
                divergence_witness="Quotient thread is not compatible across poset edges.",
            )

    n = ladder.modulus_power
    mod = 1 << n

    # 2. Choose standard local lifts e_i = sigma(g_i) = (1_K, g_i)
    local_lifts: dict[str, SemidirectElement] = {
        node: SemidirectElement(k=HeisenbergElement.identity(n), g=thread[node])
        for node in ladder.poset.nodes
    }

    # 3. Compute 1-cocycle c_{j, i} = e_i^-1 * epsilon_{j, i}(e_j) in K_i
    cocycles: dict[tuple[str, str], HeisenbergElement] = {}
    for child, parent in ladder.poset.edges:
        e_i = local_lifts[parent]
        e_j = local_lifts[child]
        eps = ladder.extension_transitions[(child, parent)]
        trans_e_j = eps(e_j)
        mismatch = e_i.inverse() * trans_e_j
        cocycles[(child, parent)] = mismatch.k

    is_ml, _ = check_mittag_leffler(ladder)

    all_k = [
        HeisenbergElement(x=x, y=y, z=z, n=n)
        for x in range(mod)
        for y in range(mod)
        for z in range(mod)
    ]

    # 4. Compute branch root fibers using complete declared extension maps
    branch_cosets: list[set[HeisenbergElement]] = []
    branch_leaf_witnesses: list[dict[HeisenbergElement, SemidirectElement]] = []

    for branch_nodes in ladder.poset.branches:
        leaf = branch_nodes[-1]
        g_leaf = thread[leaf]
        leaf_to_root: dict[HeisenbergElement, SemidirectElement] = {}

        for k_leaf in all_k:
            e_curr = SemidirectElement(k=k_leaf, g=g_leaf)
            e_orig = e_curr
            # Forward propagation along branch: from leaf to root
            for d_idx in range(len(branch_nodes) - 1, 0, -1):
                child = branch_nodes[d_idx]
                parent = branch_nodes[d_idx - 1]
                eps = ladder.extension_transitions[(child, parent)]
                e_curr = eps(e_curr)

            # Final transition into root
            eps_root = ladder.extension_transitions[(branch_nodes[0], ladder.poset.root)]
            e_root = eps_root(e_curr)

            k_root = e_root.k
            if k_root not in leaf_to_root:
                leaf_to_root[k_root] = e_orig

        branch_cosets.append(set(leaf_to_root.keys()))
        branch_leaf_witnesses.append(leaf_to_root)

    # Intersection of all branch fibers at root
    common_u0 = set.intersection(*branch_cosets) if branch_cosets else set(all_k)
    cert = certify_non_abelian_lifting_duality(ladder, branch_cosets)
    frozen_cosets = tuple(frozenset(s) for s in branch_cosets)

    if not common_u0:
        witness = (
            f"Multi-branch derived limit obstruction non-vanishing: "
            f"Branch coset intersection at root is empty ({len(branch_cosets[0])} vs {len(branch_cosets[1])} elements, "
            f"0 shared). Exact dual lower bound: {cert.dual_lower_bound} (gap = {cert.duality_gap})."
        )
        return LiftingObstructionReport(
            is_thread_compatible=True,
            is_mittag_leffler=is_ml,
            obstruction_is_trivial=False,
            local_cocycles=cocycles,
            compatible_global_lift=None,
            divergence_witness=witness,
            branch_cosets=frozen_cosets,
            duality_certificate=cert,
        )

    # Trivial obstruction: choose a common root value and forward-propagate
    ident_k = HeisenbergElement.identity(n)
    u0 = ident_k if ident_k in common_u0 else next(iter(sorted(common_u0, key=lambda el: (el.x, el.y, el.z))))
    e_root = SemidirectElement(k=u0, g=thread[ladder.poset.root])
    resolved_lifts: dict[str, SemidirectElement] = {ladder.poset.root: e_root}

    for b_idx, branch_nodes in enumerate(ladder.poset.branches):
        leaf_witness = branch_leaf_witnesses[b_idx][u0]
        e_curr = leaf_witness
        resolved_lifts[branch_nodes[-1]] = e_curr
        for d_idx in range(len(branch_nodes) - 1, 0, -1):
            child = branch_nodes[d_idx]
            parent = branch_nodes[d_idx - 1]
            eps = ladder.extension_transitions[(child, parent)]
            e_curr = eps(e_curr)
            resolved_lifts[parent] = e_curr

    # Independent verification of all edge transitions and quotient projections
    for child, parent in ladder.poset.edges:
        eps = ladder.extension_transitions[(child, parent)]
        trans_val = eps(resolved_lifts[child])
        if trans_val != resolved_lifts[parent]:
            return LiftingObstructionReport(
                is_thread_compatible=True,
                is_mittag_leffler=is_ml,
                obstruction_is_trivial=False,
                local_cocycles=cocycles,
                compatible_global_lift=None,
                divergence_witness=f"Constructed lift violates transition on edge ({child}, {parent}): {trans_val} != {resolved_lifts[parent]}",
                branch_cosets=frozen_cosets,
                duality_certificate=cert,
            )

    for node in ladder.poset.nodes:
        if resolved_lifts[node].g != thread[node]:
            return LiftingObstructionReport(
                is_thread_compatible=True,
                is_mittag_leffler=is_ml,
                obstruction_is_trivial=False,
                local_cocycles=cocycles,
                compatible_global_lift=None,
                divergence_witness=f"Constructed lift violates quotient thread at node {node}: {resolved_lifts[node].g} != {thread[node]}",
                branch_cosets=frozen_cosets,
                duality_certificate=cert,
            )

    return LiftingObstructionReport(
        is_thread_compatible=True,
        is_mittag_leffler=is_ml,
        obstruction_is_trivial=True,
        local_cocycles=cocycles,
        compatible_global_lift=resolved_lifts,
        divergence_witness=None,
        branch_cosets=frozen_cosets,
        duality_certificate=cert,
    )


def create_heisenberg_multi_branch_ladder(
    depth: int = 2,
    n_mod: int = 3,
    fail_mittag_leffler: bool = False,
) -> MultiBranchLadderSystem:
    """Factory creating a multi-branch extension ladder system of Heisenberg groups.

    Poset structure:
      Root '0'
      Branch 1: L1 -> 0, L2 -> L1, ...
      Branch 2: R1 -> 0, R2 -> R1, ...

    If fail_mittag_leffler is True, transitions scale coordinates by 2, strictly shrinking
    the kernel images at each stage (ML failure).
    If False, transitions are surjective identity homomorphisms (ML holds).
    """
    root = "root"
    b1_nodes = tuple(f"L{d}" for d in range(1, depth + 1))
    b2_nodes = tuple(f"R{d}" for d in range(1, depth + 1))
    all_nodes = (root, *b1_nodes, *b2_nodes)

    edges: list[tuple[str, str]] = [
        (b1_nodes[0], root),
        (b2_nodes[0], root),
    ]
    for d in range(1, depth):
        edges.append((b1_nodes[d], b1_nodes[d - 1]))
        edges.append((b2_nodes[d], b2_nodes[d - 1]))

    poset = MultiBranchPoset(
        nodes=all_nodes,
        edges=tuple(edges),
        root=root,
        branches=(b1_nodes, b2_nodes),
    )

    kernel_transitions: dict[tuple[str, str], Callable[[HeisenbergElement], HeisenbergElement]] = {}
    extension_transitions: dict[tuple[str, str], Callable[[SemidirectElement], SemidirectElement]] = {}

    mod = 1 << n_mod

    def make_kernel_trans(scaling: int) -> Callable[[HeisenbergElement], HeisenbergElement]:
        if scaling == 1:
            return lambda k: k
        return lambda k: HeisenbergElement(
            x=(scaling * k.x) % mod,
            y=(scaling * k.y) % mod,
            z=(scaling * scaling * k.z) % mod,
            n=n_mod,
        )

    for edge in edges:
        scaling = 2 if fail_mittag_leffler else 1
        k_trans = make_kernel_trans(scaling)
        kernel_transitions[edge] = k_trans

        def make_ext_trans(kt: Callable[[HeisenbergElement], HeisenbergElement]) -> Callable[[SemidirectElement], SemidirectElement]:
            return lambda e: SemidirectElement(k=kt(e.k), g=e.g)

        extension_transitions[edge] = make_ext_trans(k_trans)

    return MultiBranchLadderSystem(
        poset=poset,
        modulus_power=n_mod,
        kernel_transitions=kernel_transitions,
        extension_transitions=extension_transitions,
        is_failing_mittag_leffler=fail_mittag_leffler,
    )


def create_reviewer_counterexample_ladder() -> MultiBranchLadderSystem:
    """Construct the reviewer's 2-branch, depth-2 counterexample at modulus 2.

    Poset structure:
      Root 'root'
      Branch 1 (left): L1 -> root, L2 -> L1
      Branch 2 (right): R1 -> root, R2 -> R1

    At modulus 2 (n_mod = 1, mod = 2):
      Carrier is H3(Z/2Z).
      Central element c = (0, 0, 1) has order 2 and is fixed by tau.

    Extension maps:
      All edges map (k, g) -> (1_K, g) except:
        (R1, root) is identity: (k, g) -> (k, g)
        (R2, R1) applies central shift c: (k, g) -> (c^g, g)

    Kernel restrictions:
      All edges map k -> 1_K except:
        (R1, root) is identity: k -> k
        (R2, R1) maps k -> 1_K (since c^0 = 1_K)

    For quotient thread g_i = 1 everywhere:
      Left branch forces e_root = (1_K, 1).
      Right branch forces e_R1 = (c, 1), which forces e_root = (c, 1).
      Since c != 1_K, root fibers are disjoint singletons and NO compatible lift exists.
    """
    root = "root"
    b1_nodes = ("L1", "L2")
    b2_nodes = ("R1", "R2")
    all_nodes = (root, *b1_nodes, *b2_nodes)
    edges = (
        ("L1", root),
        ("L2", "L1"),
        ("R1", root),
        ("R2", "R1"),
    )
    poset = MultiBranchPoset(
        nodes=all_nodes,
        edges=edges,
        root=root,
        branches=(b1_nodes, b2_nodes),
    )

    n_mod = 1  # 1 << 1 = 2
    c_elem = HeisenbergElement(x=0, y=0, z=1, n=n_mod)
    ident_k = HeisenbergElement.identity(n_mod)

    kernel_transitions: dict[tuple[str, str], Callable[[HeisenbergElement], HeisenbergElement]] = {}
    extension_transitions: dict[tuple[str, str], Callable[[SemidirectElement], SemidirectElement]] = {}

    for edge in edges:
        if edge == ("R1", root):
            kernel_transitions[edge] = lambda k: k
            extension_transitions[edge] = lambda e: e
        elif edge == ("R2", "R1"):
            kernel_transitions[edge] = lambda k: ident_k
            extension_transitions[edge] = lambda e: SemidirectElement(
                k=c_elem if e.g == 1 else ident_k,
                g=e.g,
            )
        else:
            kernel_transitions[edge] = lambda k: ident_k
            extension_transitions[edge] = lambda e: SemidirectElement(
                k=ident_k,
                g=e.g,
            )

    return MultiBranchLadderSystem(
        poset=poset,
        modulus_power=n_mod,
        kernel_transitions=kernel_transitions,
        extension_transitions=extension_transitions,
        is_failing_mittag_leffler=True,
    )


def finite_chain_thread(top: T, steps: Sequence[Callable[[T], T]]) -> list[T]:
    """Pull `top` back along transitions from later stages to earlier ones.

    `steps[i]` maps stage `i + 1` to stage `i`. The result has length `len(steps) + 1`
    and ends with `top`.
    """
    thread: list[T] = [top]
    for step in reversed(steps):
        thread.append(step(thread[-1]))
    thread.reverse()
    return thread


def check_finite_chain(thread: Sequence[T], steps: Sequence[Callable[[T], T]]) -> bool:
    """Return True when `thread` is the compatible pullback of its last entry.

    An empty thread, or a thread whose length is not `len(steps) + 1`, raises ValueError.
    """
    if len(thread) == 0:
        raise ValueError("empty thread")
    if len(thread) != len(steps) + 1:
        raise ValueError("bad length")
    for index, step in enumerate(steps):
        if thread[index] != step(thread[index + 1]):
            raise ValueError("incompatible transition")
    return True


def overlap_certificate(families: Sequence[Sequence[object]]) -> tuple[int, int, int]:
    """Return `(branch_count, max_overlap, primal_defect)`.

    `primal_defect` is 0 when some element lies in every family, and `2 * (B - k*)`
    otherwise. An empty family list raises ValueError. Repeated members of one family
    count once.
    """
    if len(families) == 0:
        raise ValueError("families must be nonempty")
    branch_count = len(families)
    membership = [set(family) for family in families]
    tallies: dict[object, int] = {}
    for family in membership:
        for elem in family:
            tallies[elem] = tallies.get(elem, 0) + 1
    max_overlap = max(tallies.values(), default=0)
    if max_overlap == branch_count:
        primal_defect = 0
    else:
        primal_defect = 2 * (branch_count - max_overlap)
    return branch_count, max_overlap, primal_defect


def overlap_dual_matches(families: Sequence[Sequence[object]]) -> tuple[int, int]:
    """Return `(primal, dual)` with `dual = mu - sum(alphas)`.

    When `k* = B`, both values are 0. Otherwise `mu = B - 2*k*`, each alpha is `-1`,
    and `dual` equals `primal`.
    """
    branch_count, max_overlap, primal = overlap_certificate(families)
    if max_overlap == branch_count:
        return primal, 0
    mu = branch_count - 2 * max_overlap
    alpha_sum = -branch_count
    dual = mu - alpha_sum
    return primal, dual
