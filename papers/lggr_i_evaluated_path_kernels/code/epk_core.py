"""Evaluated Path Kernel (EPK) Core Engine — Paper 012.

Local Green, Global Red: Evaluated Path Kernels for Composed Agent Reliability.
Boundary Sufficiency, Defect Mass, and Proposal-Weighted Trajectories.

AuthorityEffect: None.
Anchoring: sealed-derivation-v1 (3100c4e).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import warnings
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple
import numpy as np


class DefectKind(Enum):
    """Canonical trichotomy of evaluator gluing defect outcomes."""
    NGD = -1  # Negative Gluing Defect: Local Green, Global Red (safety failure)
    ZDR = 0   # Zero Defect Residual: Local-Global verdict agreement
    PGD = 1   # Positive Gluing Defect: Local Red, Global Green (rescue effect)


@dataclass(frozen=True)
class State:
    """Declared discrete state identifier."""
    label: str

    @property
    def id(self) -> str:
        return self.label


@dataclass(frozen=True)
class TrajectorySegment:
    """A recorded trajectory segment between two boundary states."""
    start_state: State
    end_state: State
    actions: Tuple[str, ...]
    cost: float = 0.0             # Path cost C[gamma] >= 0
    risk: float = 0.0             # Path risk R[gamma] >= 0
    proposal_prob: float = 1.0    # Proposal probability P_theta(gamma) in (0, 1]
    raw_action: float = 0.0       # Base action A[gamma] >= 0
    metadata: Dict[str, Any] = field(default_factory=dict, hash=False)

    def __post_init__(self) -> None:
        if not np.isfinite(self.cost) or self.cost < 0:
            raise ValueError(f"Cost must be non-negative, got {self.cost}")
        if not np.isfinite(self.risk) or self.risk < 0:
            raise ValueError(f"Risk must be non-negative, got {self.risk}")
        if not np.isfinite(self.raw_action) or self.raw_action < 0:
            raise ValueError(f"Raw action must be non-negative, got {self.raw_action}")
        if not np.isfinite(self.proposal_prob) or not (0.0 < self.proposal_prob <= 1.0):
            raise ValueError(f"Proposal probability must be in (0, 1], got {self.proposal_prob}")

    @property
    def source(self) -> State:
        return self.start_state

    @property
    def target(self) -> State:
        return self.end_state

    @property
    def action(self) -> float:
        return self.raw_action


# Canonical alias as specified in PROJECT.md and DISPATCH.md
PathSegment = TrajectorySegment


@dataclass(frozen=True)
class ComposedTrajectory:
    """A composed trajectory gamma = gamma_2 * gamma_1."""
    segment_1: TrajectorySegment
    segment_2: TrajectorySegment

    def __post_init__(self) -> None:
        if self.segment_1.end_state != self.segment_2.start_state:
            raise ValueError(
                f"Boundary state mismatch: segment_1 ends at {self.segment_1.end_state.label}, "
                f"segment_2 starts at {self.segment_2.start_state.label}"
            )

    @property
    def start_state(self) -> State:
        return self.segment_1.start_state

    @property
    def intermediate_state(self) -> State:
        return self.segment_1.end_state

    @property
    def end_state(self) -> State:
        return self.segment_2.end_state

    @property
    def combined_actions(self) -> Tuple[str, ...]:
        return self.segment_1.actions + self.segment_2.actions

    @property
    def total_cost(self) -> float:
        return self.segment_1.cost + self.segment_2.cost

    @property
    def total_risk(self) -> float:
        return self.segment_1.risk + self.segment_2.risk

    @property
    def proposal_product(self) -> float:
        return self.segment_1.proposal_prob * self.segment_2.proposal_prob

    @property
    def total_raw_action(self) -> float:
        return self.segment_1.raw_action + self.segment_2.raw_action

# Canonical aliases as specified in PROJECT.md and DISPATCH.md
ComposedPath = ComposedTrajectory
Trajectory = ComposedTrajectory


@dataclass(frozen=True)
class BoundarySlice:
    """Declared intermediate boundary slice B subset of S."""
    states: Set[State]

    def contains(self, state: State) -> bool:
        return state in self.states

    def validate_unique_decomposition(
        self,
        trajectories: Sequence[ComposedTrajectory],
        left_segments: Optional[Sequence[TrajectorySegment]] = None,
        right_segments: Optional[Sequence[TrajectorySegment]] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Validates condition G1: Every composed path decomposes uniquely through
        states in boundary slice B and satisfies Cartesian product completeness.

        When explicit segment sets are provided, checks the complete two-way
        correspondence:
        1. Forward: Every valid declared pair (l, r) with l.end == r.start in B
           occurs uniquely in trajectories.
        2. Reverse: Every observed composed trajectory belongs to the declared
           product (neither segment is undeclared).

        When segment sets are omitted, verifies rectangularity of observed segment pairs.
        """
        if (left_segments is None) ^ (right_segments is None):
            raise ValueError(
                "Both left_segments and right_segments must be supplied together for explicit "
                "decomposition validation, or both omitted for observed-pair inference."
            )

        violations: List[str] = []
        for idx, traj in enumerate(trajectories):
            b_state = traj.intermediate_state
            if not self.contains(b_state):
                violations.append(
                    f"Trajectory {idx} decomposes at {b_state.label} not in boundary slice B."
                )

        if left_segments is not None and right_segments is not None:
            left_set = set(left_segments)
            right_set = set(right_segments)
            if len(left_segments) != len(left_set):
                violations.append(
                    f"Duplicate segment declaration in left_segments: {len(left_segments)} declared with "
                    f"{len(left_set)} unique."
                )
            if len(right_segments) != len(right_set):
                violations.append(
                    f"Duplicate segment declaration in right_segments: {len(right_segments)} declared with "
                    f"{len(right_set)} unique."
                )
            if len(trajectories) != len(set(trajectories)):
                violations.append(
                    f"Duplicate composed trajectory declaration: {len(trajectories)} provided with "
                    f"{len(set(trajectories))} unique."
                )
            declared_valid_pairs: Set[Tuple[TrajectorySegment, TrajectorySegment]] = set()

            for l in left_segments:
                if self.contains(l.end_state):
                    for r in right_segments:
                        if r.start_state == l.end_state:
                            declared_valid_pairs.add((l, r))
                            matching = [t for t in trajectories if t.segment_1 == l and t.segment_2 == r]
                            if len(matching) == 0:
                                violations.append(
                                    f"Missing Cartesian product trajectory for pair ({l.actions}, {r.actions}) through {l.end_state.label}."
                                )
                            elif len(matching) > 1:
                                violations.append(
                                    f"Duplicate decomposition for pair ({l.actions}, {r.actions}) through {l.end_state.label}."
                                )

            # Reverse correspondence check: every observed trajectory must belong to the declared product
            for idx, t in enumerate(trajectories):
                if t.segment_1 not in left_set:
                    violations.append(
                        f"Trajectory {idx} uses undeclared left segment ({t.segment_1.actions}) "
                        f"from {t.segment_1.start_state.label} to {t.segment_1.end_state.label}."
                    )
                if t.segment_2 not in right_set:
                    violations.append(
                        f"Trajectory {idx} uses undeclared right segment ({t.segment_2.actions}) "
                        f"from {t.segment_2.start_state.label} to {t.segment_2.end_state.label}."
                    )
                if (t.segment_1, t.segment_2) not in declared_valid_pairs:
                    violations.append(
                        f"Trajectory {idx} segment pair ({t.segment_1.actions}, {t.segment_2.actions}) "
                        f"is not in the declared valid boundary product through {t.intermediate_state.label}."
                    )
        else:
            # Inferred branch: checks rectangularity of observed segment pairs
            by_mid: Dict[State, List[ComposedTrajectory]] = {}
            for t in trajectories:
                by_mid.setdefault(t.intermediate_state, []).append(t)

            for b_state, trajs in by_mid.items():
                if not self.contains(b_state):
                    continue
                s1_set = {t.segment_1 for t in trajs}
                s2_set = {t.segment_2 for t in trajs}
                expected_pairs = len(s1_set) * len(s2_set)
                observed_pairs = {(t.segment_1, t.segment_2) for t in trajs}
                if len(observed_pairs) < expected_pairs:
                    violations.append(
                        f"Incomplete Cartesian cross-product at boundary state {b_state.label}: "
                        f"observed {len(observed_pairs)} cross-pairs out of {expected_pairs} expected."
                    )
                if len(trajs) > len(observed_pairs):
                    violations.append(
                        f"Duplicate composed trajectories observed at boundary state {b_state.label}."
                    )

        return (len(violations) == 0, violations)


EvaluatorFn = Callable[[Any], int]


@dataclass(frozen=True)
class EvaluatorSet:
    """Declared evaluator triple (E_1, E_2, E_g)."""
    eval_1: EvaluatorFn
    eval_2: EvaluatorFn
    eval_g: EvaluatorFn


# Evaluator abstraction specified in PROJECT.md
Evaluator = EvaluatorSet


def _validate_binary_verdict(val: Any, name: str) -> int:
    """Strictly validates integer binary verdicts in {0, 1}, rejecting floats."""
    if isinstance(val, (bool, np.bool_)):
        return int(val)
    if isinstance(val, (int, np.integer)) and not isinstance(val, (float, np.floating)):
        if val in (0, 1):
            return int(val)
        raise ValueError(f"Verdicts must be binary in {{0, 1}}, got {name}={val}")
    raise TypeError(f"Verdicts must be integers in {{0, 1}}, got {type(val).__name__} ({name}={val})")


def calculate_evaluator_defect(
    gamma1: Any = None,
    gamma2: Any = None,
    e1: Any = None,
    e2: Any = None,
    eg: Any = None,
) -> int:
    """Calculate ``Delta_E = E_g - E_1 * E_2`` for a declared verdict triple.

    Accepted call forms are an :class:`EvaluatorVerdictTriple`, three positional
    verdicts ``(e1, e2, eg)``, the explicit ``e1=, e2=, eg=`` keywords, the
    historical ``gamma1=, gamma2=, eg=`` aliases, and the legacy five-position
    form ``(None, None, e1, e2, eg)``.  The three-position form is detected
    before the historical keyword aliases so its third argument cannot be
    mistaken for ``e1``.
    """
    if isinstance(gamma1, EvaluatorVerdictTriple):
        if any(value is not None for value in (gamma2, e1, e2, eg)):
            raise TypeError("a verdict triple cannot be combined with other verdict arguments")
        return gamma1.delta_eval

    # Python binds calculate_evaluator_defect(1, 1, 0) to
    # (gamma1, gamma2, e1).  Treat that exact shape as the documented
    # three-positional-verdict API.
    if gamma1 is not None and gamma2 is not None and e1 is not None and e2 is None and eg is None:
        raw1, raw2, rawg = gamma1, gamma2, e1
    elif e1 is not None and e2 is not None and eg is not None:
        raw1, raw2, rawg = e1, e2, eg
    elif gamma1 is not None and gamma2 is not None and eg is not None and e1 is None and e2 is None:
        raw1, raw2, rawg = gamma1, gamma2, eg
    else:
        raise TypeError(
            "expected a verdict triple or exactly three verdicts via positional, "
            "e1/e2/eg, or gamma1/gamma2/eg arguments"
        )

    v1 = _validate_binary_verdict(raw1, "e1")
    v2 = _validate_binary_verdict(raw2, "e2")
    vg = _validate_binary_verdict(rawg, "eg")
    return vg - (v1 * v2)


@dataclass(frozen=True)
class EvaluatorVerdictTriple:
    """Discrete binary verdicts for a single composed trace (E1, E2, Eg)."""
    e1: int
    e2: int
    eg: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "e1", _validate_binary_verdict(self.e1, "e1"))
        object.__setattr__(self, "e2", _validate_binary_verdict(self.e2, "e2"))
        object.__setattr__(self, "eg", _validate_binary_verdict(self.eg, "eg"))

    @property
    def local_product(self) -> int:
        return self.e1 * self.e2

    @property
    def delta_eval(self) -> int:
        """Delta_E = E_g - E_1 * E_2 in {-1, 0, 1}."""
        return self.eg - self.local_product

    @property
    def defect_kind(self) -> DefectKind:
        return DefectKind(self.delta_eval)

    @property
    def is_ngd(self) -> bool:
        """Local green (e1*e2 == 1) and global red (eg == 0)."""
        return self.local_product == 1 and self.eg == 0

    @property
    def is_pgd(self) -> bool:
        """Local red (e1*e2 == 0) and global green (eg == 1)."""
        return self.local_product == 0 and self.eg == 1

    @property
    def is_zdr(self) -> bool:
        """Local and global verdicts agree (eg == e1*e2)."""
        return self.eg == self.local_product

    @property
    def is_lrgr(self) -> bool:
        """Local red and global red."""
        return self.local_product == 0 and self.eg == 0

    @property
    def is_global_failure(self) -> bool:
        return self.eg == 0


@dataclass(frozen=True)
class MultiChannelDefect:
    """Tracks independent failure channels across composition."""
    delta_eval: int
    delta_cost: float
    delta_risk: float
    delta_prop: float
    delta_action: float

    def total_effective_defect(self, lam: float = 1.0, mu: float = 1.0) -> float:
        """Delta_total = Delta_P + lambda * Delta_C + mu * Delta_R."""
        return self.delta_prop + lam * self.delta_cost + mu * self.delta_risk


@dataclass
class MetricReport:
    """Summary report of EPK metrics over a sample of traces."""
    sample_size: int
    lpr: float                      # Local Pass Rate: mean(E_1 * E_2)
    gpr: float                      # Global Pass Rate: mean(E_g)
    mean_delta_e: float             # Mean Evaluator Defect: mean(Delta_E)
    ngd_all: float                  # Unconditional NGD rate: mean(Delta_E == -1)
    ngd_cond: Optional[float]       # Conditional NGD rate: Pr(E_g = 0 | E_1 * E_2 = 1)
    pgd: float                      # Positive Gluing Defect rate: mean(Delta_E == 1)
    zdr: float                      # Zero Defect Residual rate: mean(Delta_E == 0)
    egd: float                      # Absolute Evaluator Gluing Defect rate: NGD + PGD
    ngd_count: int
    pgd_count: int
    zdr_count: int
    local_pass_count: int
    global_pass_count: int
    delta_sum: int

    @property
    def expected_gluing_defect(self) -> float:
        return self.mean_delta_e

    @property
    def ngd(self) -> float:
        return self.ngd_all

    @property
    def absolute_pass_rate_gap(self) -> float:
        """Absolute difference between GPR and LPR: |GPR - LPR| = |mean(Delta_E)|."""
        return abs(self.mean_delta_e)

    @property
    def rke(self) -> float:
        """Deprecated property returning absolute pass-rate gap |mean(Delta_E)|.

        WARNING: .rke on MetricReport returns the pass-rate gap |GPR - LPR|, not
        the relative/residual kernel error (RKE) on weighted kernels.
        Use .absolute_pass_rate_gap for pass-rate gap, or use
        EvaluatedPathKernel.evaluate_composition(z_direct, z_composed) for true kernel RKE.
        """
        warnings.warn(
            "MetricReport.rke is deprecated and will be removed in a future release. "
            "It returns the pass-rate gap |mean(Delta_E)|, not kernel error RKE. "
            "Use report.absolute_pass_rate_gap for pass rates, or "
            "EvaluatedPathKernel.evaluate_composition() for true kernel RKE.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.absolute_pass_rate_gap


MetricsResult = MetricReport


class EPKMetrics:
    """Computes and validates evaluated path kernel metrics and balance identities."""

    @staticmethod
    def compute(triples: Sequence[EvaluatorVerdictTriple]) -> MetricReport:
        n = len(triples)
        if n == 0:
            raise ValueError("Cannot compute metrics over an empty trace set.")

        local_passes = sum(t.local_product for t in triples)
        global_passes = sum(t.eg for t in triples)
        delta_sum = sum(t.delta_eval for t in triples)

        ngd_count = sum(1 for t in triples if t.is_ngd)
        pgd_count = sum(1 for t in triples if t.is_pgd)
        zdr_count = sum(1 for t in triples if t.is_zdr)

        lpr = local_passes / n
        gpr = global_passes / n
        mean_delta = delta_sum / n
        ngd_all = ngd_count / n
        pgd = pgd_count / n
        zdr = zdr_count / n
        egd = (ngd_count + pgd_count) / n

        ngd_cond = (ngd_count / local_passes) if local_passes > 0 else None

        report = MetricReport(
            sample_size=n,
            lpr=lpr,
            gpr=gpr,
            mean_delta_e=mean_delta,
            ngd_all=ngd_all,
            ngd_cond=ngd_cond,
            pgd=pgd,
            zdr=zdr,
            egd=egd,
            ngd_count=ngd_count,
            pgd_count=pgd_count,
            zdr_count=zdr_count,
            local_pass_count=local_passes,
            global_pass_count=global_passes,
            delta_sum=delta_sum,
        )
        EPKMetrics.verify_identities(report)
        return report

    @staticmethod
    def verify_identities(report: MetricReport, tol: float = 1e-12) -> None:
        """
        Enforces mandatory mathematical identities from Section 1.5 & Section 5:
        1. GPR - LPR = mean(Delta_E)
        2. NGD + PGD + ZDR = 1
        3. EGD = NGD + PGD = 1 - ZDR
        4. sum(Delta_E) = PGD_count - NGD_count
        5. GPR_count - LPR_count = sum(Delta_E)
        """
        for rate_name in ("lpr", "gpr", "mean_delta_e", "ngd_all", "pgd", "zdr", "egd"):
            val = getattr(report, rate_name)
            if not np.isfinite(val):
                raise AssertionError(f"Identity check requires finite rate values; {rate_name}={val}")
        if report.ngd_cond is not None and not np.isfinite(report.ngd_cond):
            raise AssertionError(f"Identity check requires finite rate values; ngd_cond={report.ngd_cond}")

        if abs((report.gpr - report.lpr) - report.mean_delta_e) > tol:
            raise AssertionError(
                f"Identity GPR - LPR = mean(Delta_E) failed: "
                f"{report.gpr - report.lpr} != {report.mean_delta_e}"
            )
        if abs((report.ngd_all + report.pgd + report.zdr) - 1.0) > tol:
            raise AssertionError(
                f"Partition identity NGD + PGD + ZDR = 1 failed: sum is {report.ngd_all + report.pgd + report.zdr}"
            )
        if abs(report.egd - (report.ngd_all + report.pgd)) > tol or abs(report.egd - (1.0 - report.zdr)) > tol:
            raise AssertionError("Identity EGD = NGD + PGD failed.")
        if report.delta_sum != (report.pgd_count - report.ngd_count):
            raise AssertionError(
                f"Signed count balance failed: delta_sum={report.delta_sum}, "
                f"pgd_count - ngd_count={report.pgd_count - report.ngd_count}"
            )
        if (report.global_pass_count - report.local_pass_count) != report.delta_sum:
            raise AssertionError("Count gap global - local != delta_sum")

    @staticmethod
    def failure_partition(
        triples: Sequence[EvaluatorVerdictTriple],
    ) -> tuple[int, int, int]:
        """Return global-failure, NGD, and local-red/global-red counts."""
        if len(triples) == 0:
            raise ValueError("Cannot partition an empty trace set.")
        ngd = sum(1 for trace in triples if trace.is_ngd)
        lrgr = sum(1 for trace in triples if trace.is_lrgr)
        failure = sum(1 for trace in triples if trace.is_global_failure)
        return failure, ngd, lrgr

    @staticmethod
    def failure_partition_holds(triples: Sequence[EvaluatorVerdictTriple]) -> bool:
        failure, ngd, lrgr = EPKMetrics.failure_partition(triples)
        return failure == ngd + lrgr

    @staticmethod
    def ngd_below_failure_given_both_witnesses(
        triples: Sequence[EvaluatorVerdictTriple],
    ) -> bool:
        """Finite content of the structural-guard strict gap: both witnesses present."""
        failure, ngd, lrgr = EPKMetrics.failure_partition(triples)
        if ngd < 1 or lrgr < 1:
            raise ValueError("NGD and LRGR witnesses are both required")
        return ngd < failure

    @staticmethod
    def validate_report(report: MetricReport, tol: float = 1e-12) -> None:
        """
        Validates complete structural integrity and correspondence of a MetricReport.

        Audits:
        - Sample size must be a strictly positive integer.
        - All counts must be non-negative integers bounded by sample_size.
        - Partition count balance: ngd_count + pgd_count + zdr_count == sample_size.
        - Count balance: delta_sum == pgd_count - ngd_count.
        - Pass count balance: global_pass_count - local_pass_count == delta_sum.
        - Rate/count correspondence for lpr, gpr, mean_delta_e, ngd_all, pgd, zdr, egd.
        - Conditional NGD denominator: ngd_cond must be None if local_pass_count == 0,
          or match ngd_count / local_pass_count in [0, 1] if local_pass_count > 0.
        - All identity relations via verify_identities.
        """
        if not isinstance(report.sample_size, (int, np.integer)) or isinstance(report.sample_size, (bool, np.bool_)) or report.sample_size <= 0:
            raise ValueError(f"Sample size must be a positive integer, got {report.sample_size}")
        n = int(report.sample_size)

        count_fields = {
            "ngd_count": report.ngd_count,
            "pgd_count": report.pgd_count,
            "zdr_count": report.zdr_count,
            "local_pass_count": report.local_pass_count,
            "global_pass_count": report.global_pass_count,
        }
        for name, count in count_fields.items():
            if not isinstance(count, (int, np.integer)) or isinstance(count, (bool, np.bool_)) or count < 0 or count > n:
                raise ValueError(f"Count '{name}' must be an integer in [0, {n}], got {count}")

        if not isinstance(report.delta_sum, (int, np.integer)) or isinstance(report.delta_sum, (bool, np.bool_)):
            raise ValueError(f"delta_sum must be an integer, got {report.delta_sum}")

        if (report.ngd_count + report.pgd_count + report.zdr_count) != n:
            raise AssertionError(
                f"Count partition failed: ngd_count({report.ngd_count}) + "
                f"pgd_count({report.pgd_count}) + zdr_count({report.zdr_count}) != sample_size({n})"
            )

        if report.delta_sum != (report.pgd_count - report.ngd_count):
            raise AssertionError(
                f"delta_sum ({report.delta_sum}) != pgd_count ({report.pgd_count}) - ngd_count ({report.ngd_count})"
            )

        if (report.global_pass_count - report.local_pass_count) != report.delta_sum:
            raise AssertionError(
                f"Count gap global_pass_count ({report.global_pass_count}) - "
                f"local_pass_count ({report.local_pass_count}) != delta_sum ({report.delta_sum})"
            )

        # Joint-table feasibility (four-cell non-negativity: E11 exposure bound and dual)
        if report.ngd_count > report.local_pass_count:
            raise AssertionError(
                f"NGD count ({report.ngd_count}) exceeds local-green exposure ({report.local_pass_count})"
            )
        if report.pgd_count > (n - report.local_pass_count):
            raise AssertionError(
                f"PGD count ({report.pgd_count}) exceeds local-red exposure ({n - report.local_pass_count})"
            )

        # Rate-to-count correspondence
        rate_count_pairs = [
            ("lpr", report.lpr, report.local_pass_count),
            ("gpr", report.gpr, report.global_pass_count),
            ("mean_delta_e", report.mean_delta_e, report.delta_sum),
            ("ngd_all", report.ngd_all, report.ngd_count),
            ("pgd", report.pgd, report.pgd_count),
            ("zdr", report.zdr, report.zdr_count),
        ]
        for name, rate, count in rate_count_pairs:
            expected_rate = count / n
            if not np.isfinite(rate) or abs(rate - expected_rate) > tol:
                raise AssertionError(f"Rate '{name}' ({rate}) does not match count ratio ({expected_rate})")

        expected_egd = (report.ngd_count + report.pgd_count) / n
        if not np.isfinite(report.egd) or abs(report.egd - expected_egd) > tol:
            raise AssertionError(f"Rate 'egd' ({report.egd}) does not match count ratio ({expected_egd})")

        # Conditional NGD denominator check
        if report.local_pass_count == 0:
            if report.ngd_cond is not None:
                raise AssertionError(f"ngd_cond must be None when local_pass_count == 0, got {report.ngd_cond}")
        else:
            if report.ngd_cond is None:
                raise AssertionError("ngd_cond must not be None when local_pass_count > 0")
            expected_cond = report.ngd_count / report.local_pass_count
            if not np.isfinite(report.ngd_cond) or abs(report.ngd_cond - expected_cond) > tol:
                raise AssertionError(
                    f"ngd_cond ({report.ngd_cond}) does not match ngd_count / local_pass_count ({expected_cond})"
                )
            if not (0.0 <= report.ngd_cond <= 1.0 + tol):
                raise AssertionError(
                    f"ngd_cond ({report.ngd_cond}) outside [0, 1]"
                )

        EPKMetrics.verify_identities(report, tol=tol)


VALID_KERNEL_MODES: Set[str] = {"action", "proposal_cost_risk", "hybrid"}


class EvaluatedPathKernel:
    """Computes evaluated path kernels Z_theta and evaluates composition error."""

    @staticmethod
    def four_term_contribution(
        e1: int,
        e2: int,
        w1: float,
        w2: float,
        delta_e: int,
        delta_w: float,
    ) -> float:
        """Return the exact two-channel expansion from manuscript Section 4.

        With ``E_g = E_1 E_2 + delta_e`` and
        ``w_g = w_1 w_2 + delta_w``, this computes

        ``E_1 E_2 w_1 w_2 + delta_e w_1 w_2
        + E_1 E_2 delta_w + delta_e delta_w``.

        The method is deliberately algebraic: signed weight defects are
        allowed, while every supplied scalar must be finite and the evaluator
        inputs must have their stated finite ranges.
        """
        e1_clean = _validate_binary_verdict(e1, "e1")
        e2_clean = _validate_binary_verdict(e2, "e2")
        if delta_e not in (-1, 0, 1):
            raise ValueError(f"delta_e must lie in {{-1, 0, 1}}, got {delta_e!r}")
        scalars = (float(w1), float(w2), float(delta_w))
        if not all(np.isfinite(value) for value in scalars):
            raise ValueError("w1, w2, and delta_w must be finite")
        local_e = e1_clean * e2_clean
        return float(
            local_e * scalars[0] * scalars[1]
            + delta_e * scalars[0] * scalars[1]
            + local_e * scalars[2]
            + delta_e * scalars[2]
        )

    @staticmethod
    def compute_action_kernel(
        trajectories: Sequence[TrajectorySegment],
        evaluator: EvaluatorFn,
        beta: float = 1.0,
    ) -> float:
        """Section 2 unweighted action kernel: Z_beta(S_b | S_a) = sum_{gamma} E(gamma) * exp(-beta * A[gamma])."""
        return EvaluatedPathKernel.compute_kernel(trajectories, evaluator, beta=beta, lam=0.0, mu=0.0, mode="action")

    @staticmethod
    def compute_proposal_cost_risk_kernel(
        trajectories: Sequence[TrajectorySegment],
        evaluator: EvaluatorFn,
        lam: float = 1.0,
        mu: float = 1.0,
    ) -> float:
        """Section 11 canonical kernel: Z_{lam,mu}^theta(S_b | S_a) = sum_{gamma} E(gamma) * P_theta(gamma) * exp(-lam * C - mu * R)."""
        return EvaluatedPathKernel.compute_kernel(trajectories, evaluator, beta=0.0, lam=lam, mu=mu, mode="proposal_cost_risk")

    @staticmethod
    def compute_hybrid_kernel(
        trajectories: Sequence[TrajectorySegment],
        evaluator: EvaluatorFn,
        beta: float = 1.0,
        lam: float = 1.0,
        mu: float = 1.0,
    ) -> float:
        """Tempered hybrid extension: sum_{gamma} E(gamma) * P_theta(gamma) * exp(-beta * A - lam * C - mu * R)."""
        return EvaluatedPathKernel.compute_kernel(trajectories, evaluator, beta=beta, lam=lam, mu=mu, mode="hybrid")

    @staticmethod
    def compute_kernel(
        trajectories: Sequence[TrajectorySegment],
        evaluator: EvaluatorFn,
        beta: float = 1.0,
        lam: float = 0.0,
        mu: float = 0.0,
        mode: str = "hybrid",
    ) -> float:
        """
        Computes evaluated path kernel mass over trajectory segments.

        Modes:
        - "action": Section 2 unweighted action kernel: sum E(gamma) * exp(-beta * A)
        - "proposal_cost_risk": Section 11 canonical kernel: sum E(gamma) * P_theta(gamma) * exp(-lam * C - mu * R)
        - "hybrid": Tempered hybrid kernel: sum E(gamma) * P_theta(gamma) * exp(-beta * A - lam * C - mu * R)
        """
        if mode not in VALID_KERNEL_MODES:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of {sorted(VALID_KERNEL_MODES)}")
        if not all(np.isfinite(x) for x in (beta, lam, mu)):
            raise ValueError("Kernel coefficients must be finite (cannot be NaN or infinite)")
        if beta < 0 or lam < 0 or mu < 0:
            raise ValueError(f"Kernel coefficients must be non-negative: beta={beta}, lam={lam}, mu={mu}")

        total_mass = 0.0
        for traj in trajectories:
            if np.isnan(traj.raw_action) or np.isnan(traj.cost) or np.isnan(traj.risk) or np.isnan(traj.proposal_prob):
                raise ValueError(f"Trajectory contains NaN metrics: {traj}")
            e_raw = evaluator(traj)
            e_val = _validate_binary_verdict(e_raw, "evaluator_output")
            if e_val == 1:
                if mode == "action":
                    action_term = 0.0 if beta == 0.0 else beta * traj.raw_action
                    weight = float(np.exp(-action_term))
                elif mode == "proposal_cost_risk":
                    cost_term = (0.0 if lam == 0.0 else lam * traj.cost) + (0.0 if mu == 0.0 else mu * traj.risk)
                    weight = traj.proposal_prob * float(np.exp(-cost_term))
                else:  # hybrid
                    cost_term = (0.0 if lam == 0.0 else lam * traj.cost) + (0.0 if mu == 0.0 else mu * traj.risk)
                    action_term = (0.0 if beta == 0.0 else beta * traj.raw_action) + cost_term
                    weight = traj.proposal_prob * float(np.exp(-action_term))
                total_mass += weight
        return float(total_mass)

    @staticmethod
    def evaluate_composition(
        z_direct: float,
        z_composed_sum: float,
        eps: float = 1e-12,
    ) -> Tuple[float, float]:
        """
        Returns (RKE, nRKE):
        RKE = |Z(S_c | S_a) - sum_{S_b} Z(S_c | S_b) Z(S_b | S_a)|
        nRKE = RKE / (Z(S_c | S_a) + eps)
        """
        rke = abs(z_direct - z_composed_sum)
        nrke = rke / (z_direct + eps)
        return (rke, nrke)

    @staticmethod
    def compute_action_evaluator_residual(
        composed_trajectories: Sequence[ComposedTrajectory],
        eval_set: EvaluatorSet,
        beta: float = 1.0,
    ) -> float:
        """
        Section 4 unweighted action residual:
        R_Eval(S_c, S_a) = sum_{S_b} sum_{gamma_1, gamma_2} Delta_E(gamma_1, gamma_2) * exp(-beta * (A_1 + A_2))
        Strictly independent of proposal probability mass.
        """
        return EvaluatedPathKernel.compute_evaluator_residual(
            composed_trajectories, eval_set, beta=beta, lam=0.0, mu=0.0, mode="action"
        )

    @staticmethod
    def compute_proposal_cost_risk_evaluator_residual(
        composed_trajectories: Sequence[ComposedTrajectory],
        eval_set: EvaluatorSet,
        lam: float = 1.0,
        mu: float = 1.0,
    ) -> float:
        """
        Section 11 canonical proposal-cost-risk residual:
        R_Eval(S_c, S_a) = sum_{S_b} sum_{gamma_1, gamma_2} Delta_E(gamma_1, gamma_2) *
                           P_theta(gamma_1) * P_theta(gamma_2) * exp(-lam * (C_1 + C_2) - mu * (R_1 + R_2))
        """
        return EvaluatedPathKernel.compute_evaluator_residual(
            composed_trajectories, eval_set, beta=0.0, lam=lam, mu=mu, mode="proposal_cost_risk"
        )

    @staticmethod
    def compute_hybrid_evaluator_residual(
        composed_trajectories: Sequence[ComposedTrajectory],
        eval_set: EvaluatorSet,
        beta: float = 1.0,
        lam: float = 1.0,
        mu: float = 1.0,
    ) -> float:
        """
        Tempered hybrid residual:
        R_Eval(S_c, S_a) = sum_{S_b} sum_{gamma_1, gamma_2} Delta_E(gamma_1, gamma_2) *
                           P_theta(gamma_1) * P_theta(gamma_2) *
                           exp(-beta * (A_1 + A_2) - lam * (C_1 + C_2) - mu * (R_1 + R_2))
        """
        return EvaluatedPathKernel.compute_evaluator_residual(
            composed_trajectories, eval_set, beta=beta, lam=lam, mu=mu, mode="hybrid"
        )

    @staticmethod
    def compute_evaluator_residual(
        composed_trajectories: Sequence[ComposedTrajectory],
        eval_set: EvaluatorSet,
        beta: float = 1.0,
        lam: float = 0.0,
        mu: float = 0.0,
        mode: str = "action",
    ) -> float:
        """
        Computes evaluator residual over composed trajectories.

        Modes:
        - "action": Section 4 action residual: sum Delta_E * exp(-beta * (A_1 + A_2)) (independent of proposal prob)
        - "proposal_cost_risk": Section 11 canonical residual: sum Delta_E * P_theta * exp(-lam * C - mu * R)
        - "hybrid": Tempered hybrid residual: sum Delta_E * P_theta * exp(-beta * A - lam * C - mu * R)
        """
        if mode not in VALID_KERNEL_MODES:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of {sorted(VALID_KERNEL_MODES)}")
        if not all(np.isfinite(x) for x in (beta, lam, mu)):
            raise ValueError("Residual coefficients must be finite (cannot be NaN or infinite)")
        if beta < 0 or lam < 0 or mu < 0:
            raise ValueError(f"Coefficients must be non-negative: beta={beta}, lam={lam}, mu={mu}")

        residual = 0.0
        for comp in composed_trajectories:
            e1 = eval_set.eval_1(comp.segment_1)
            e2 = eval_set.eval_2(comp.segment_2)
            eg = eval_set.eval_g(comp)
            delta_e = calculate_evaluator_defect(e1=e1, e2=e2, eg=eg)
            if mode == "action":
                action_term = 0.0 if beta == 0.0 else beta * comp.total_raw_action
                weight = float(np.exp(-action_term))
            elif mode == "proposal_cost_risk":
                cost_term = (0.0 if lam == 0.0 else lam * comp.total_cost) + (0.0 if mu == 0.0 else mu * comp.total_risk)
                weight = comp.proposal_product * float(np.exp(-cost_term))
            else:  # hybrid
                cost_term = (0.0 if lam == 0.0 else lam * comp.total_cost) + (0.0 if mu == 0.0 else mu * comp.total_risk)
                action_term = (0.0 if beta == 0.0 else beta * comp.total_raw_action) + cost_term
                weight = comp.proposal_product * float(np.exp(-action_term))
            residual += delta_e * weight
        return float(residual)


calculate_epk = EvaluatedPathKernel.compute_kernel
calculate_action_epk = EvaluatedPathKernel.compute_action_kernel
calculate_proposal_cost_risk_epk = EvaluatedPathKernel.compute_proposal_cost_risk_kernel
calculate_proposal_weighted_epk = EvaluatedPathKernel.compute_kernel
calculate_evaluator_residual = EvaluatedPathKernel.compute_evaluator_residual
calculate_action_evaluator_residual = EvaluatedPathKernel.compute_action_evaluator_residual
calculate_proposal_cost_risk_evaluator_residual = EvaluatedPathKernel.compute_proposal_cost_risk_evaluator_residual
calculate_hybrid_evaluator_residual = EvaluatedPathKernel.compute_hybrid_evaluator_residual


class ReliabilityModels:
    """Evaluates Product-of-Experts vs Mixture-of-Experts and Activation Density."""

    @staticmethod
    def product_of_experts_pass(expert_verdicts: Sequence[int]) -> int:
        """
        PoE implements hard conjunction: E_PoE = prod_{k=1}^K E_k.
        Any hard refusal (E_k == 0) forces E_PoE = 0.
        All verdicts are strictly validated in {0, 1} before returning, regardless of order.
        """
        clean_verdicts = [
            _validate_binary_verdict(v, f"expert_verdict[{idx}]")
            for idx, v in enumerate(expert_verdicts)
        ]
        res = 1
        for v in clean_verdicts:
            res *= v
            if res == 0:
                break
        return res

    @staticmethod
    def normalized_product_of_experts(
        candidate_expert_probabilities: Sequence[Sequence[float]],
    ) -> List[float]:
        """
        Computes the normalized Product-of-Experts distribution over an ensemble of candidate trajectories:
        p_PoE(W) = (prod_e p_e(W)) / (sum_eta prod_e p_e(eta)).

        Uses log-domain aggregation for positive probabilities to prevent numerical underflow,
        while strictly handling exact zero scores.

        Args:
            candidate_expert_probabilities: Sequence of expert probability vectors, one per candidate
                trajectory: [[p_1(eta_1), ..., p_K(eta_1)], [p_1(eta_2), ...], ...].

        Returns:
            List of normalized trajectory probabilities summing to 1.0.

        Raises:
            ValueError: If candidate list is empty, expert counts are inconsistent, probabilities are
                negative/non-finite, or joint support is empty (all candidate products are 0).
        """
        if not candidate_expert_probabilities:
            raise ValueError("Candidate ensemble must not be empty.")
        num_experts = len(candidate_expert_probabilities[0])
        if num_experts == 0:
            raise ValueError("Each candidate must have at least one expert evaluation.")

        pos_indices: List[int] = []
        log_masses: Dict[int, float] = {}

        for idx, probs in enumerate(candidate_expert_probabilities):
            if len(probs) != num_experts:
                raise ValueError(
                    f"Candidate {idx} has {len(probs)} experts, expected {num_experts}."
                )
            has_zero = False
            log_p_sum = 0.0
            for p in probs:
                if p < 0.0 or not np.isfinite(p):
                    raise ValueError(f"Expert probabilities must be non-negative and finite, got {p}")
                if p == 0.0:
                    has_zero = True
                elif not has_zero:
                    log_p_sum += float(np.log(p))
            if not has_zero:
                pos_indices.append(idx)
                log_masses[idx] = log_p_sum

        if not pos_indices:
            raise ValueError(
                "Normalized PoE requires positive normalization denominator (non-empty joint support), got 0.0"
            )

        max_log = max(log_masses.values())
        unnormalized_masses: List[float] = [0.0] * len(candidate_expert_probabilities)
        for idx in pos_indices:
            unnormalized_masses[idx] = float(np.exp(log_masses[idx] - max_log))

        denom = sum(unnormalized_masses)
        return [float(m / denom) for m in unnormalized_masses]

    @staticmethod
    def mixture_of_experts_pass(
        expert_verdicts: Sequence[int],
        weights: Sequence[float],
        threshold: float = 0.5,
    ) -> int:
        """
        MoE implements soft voting: E_MoE = 1 iff sum w_k E_k / sum w_k >= threshold.
        """
        if len(expert_verdicts) != len(weights):
            raise ValueError("Verdicts and weights must have matching lengths.")
        if len(expert_verdicts) == 0:
            raise ValueError("Ensemble must not be empty.")
        if not np.isfinite(threshold) or not (0.0 <= threshold <= 1.0):
            raise ValueError(f"Threshold must be finite and lie in [0, 1], got {threshold}")

        clean_verdicts = [
            _validate_binary_verdict(v, f"expert_verdicts[{idx}]")
            for idx, v in enumerate(expert_verdicts)
        ]

        clean_weights: List[float] = []
        for idx, w in enumerate(weights):
            if not np.isfinite(w) or w < 0.0:
                raise ValueError(f"Weight at index {idx} must be finite and non-negative, got {w}")
            clean_weights.append(float(w))

        max_w = max(clean_weights)
        if max_w == 0.0:
            return 0

        scaled_weights = [w / max_w for w in clean_weights]
        w_sum = sum(scaled_weights)
        score = sum(w * v for w, v in zip(scaled_weights, clean_verdicts)) / w_sum
        return 1 if score >= threshold else 0

    @staticmethod
    def activation_density_foc(
        d_val: float,
        cost_deriv: float,
        defect_deriv: float,
        cost_val: float,
        tol: float = 1e-4,
    ) -> bool:
        """
        Checks Section 6.2 interior first-order condition: C'(D) * (1 - D) = C(D) * D'(D).
        Note: This FOC applies to interior stationary points; boundary optima need not satisfy it.
        """
        lhs = cost_deriv * (1.0 - d_val)
        rhs = cost_val * defect_deriv
        return abs(lhs - rhs) < tol

    @staticmethod
    def activation_density_curve(
        alpha: np.ndarray,
        c_base: float = 0.5,
        gamma_c: float = 0.5,
        d_base: float = 0.0,
        kappa: float = 0.8,
        gamma_d: float = 1.5,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Models capability C(alpha) = c_base + (1 - c_base) * alpha^gamma_c
        and defect D(alpha) = d_base + kappa * alpha^gamma_d.
        Net success S(alpha) = C(alpha) * (1 - D(alpha)).
        """
        c = c_base + (1.0 - c_base) * (alpha ** gamma_c)
        d = np.clip(d_base + kappa * (alpha ** gamma_d), 0.0, 1.0)
        s = c * (1.0 - d)
        return (c, d, s)

    @staticmethod
    def find_optimal_activation_density(
        c_base: float = 0.5,
        gamma_c: float = 0.5,
        d_base: float = 0.0,
        kappa: float = 0.8,
        gamma_d: float = 1.5,
    ) -> Tuple[float, float]:
        """
        Locates alpha* in [0, 1] maximizing S(alpha) using a 1,001-point grid search
        evaluating endpoints and interior points.
        """
        alphas = np.linspace(0.0, 1.0, 1001)
        c, d, s = ReliabilityModels.activation_density_curve(
            alphas, c_base, gamma_c, d_base, kappa, gamma_d
        )
        best_idx = int(np.argmax(s))
        alpha_star = float(alphas[best_idx])
        s_star = float(s[best_idx])
        return (alpha_star, s_star)


class DetectorAdequacyStatus(Enum):
    NO_LISTED_DEGENERACY_OBSERVED = "NO_LISTED_DEGENERACY_OBSERVED"
    VACUOUS_LOCAL = "VACUOUS_LOCAL"          # E_1 == 1 and E_2 == 1 on all traces
    ALL_REJECTING = "ALL_REJECTING"          # E_1 == 0 or E_2 == 0 on all traces
    OBSERVED_AGREEMENT_SAMPLE_LEVEL = "OBSERVED_AGREEMENT"  # E_g == E_1 * E_2 on sample (sample agreement != tautological code)
    TAUTOLOGICAL_COUPLING = "OBSERVED_AGREEMENT"            # Backwards-compatibility alias
    TRIVIAL_SLICE = "TRIVIAL_SLICE"                         # Boundary cut has <= 1 state with confirmed terminal/identity collapse
    SINGLETON_SLICE_CUT_UNASSESSED = "SINGLETON_SLICE_CUT_UNASSESSED"  # Singleton boundary cut without endpoint/identity verification
    CONSTANT_GLOBAL_REJECT = "CONSTANT_GLOBAL_REJECT"      # E_g == 0 on all traces
    CONSTANT_GLOBAL_ACCEPT = "CONSTANT_GLOBAL_ACCEPT"      # E_g == 1 on all traces
    CONSTANT_LOCAL_PRODUCT_ZERO = "CONSTANT_LOCAL_PRODUCT_ZERO"  # E_1 * E_2 == 0 on all traces


AdequacyWarning = DetectorAdequacyStatus
AdequacyResult = List[DetectorAdequacyStatus]


class DetectorAdequacyGuard:
    """Verifies that the evaluated pipeline does not suffer from degenerate collapses."""

    @staticmethod
    def audit(
        triples: Sequence[EvaluatorVerdictTriple],
        boundary_slice: Optional[BoundarySlice] = None,
        composed_trajectories: Optional[Sequence[ComposedTrajectory]] = None,
    ) -> List[DetectorAdequacyStatus]:
        warnings: List[DetectorAdequacyStatus] = []
        n = len(triples)
        if n == 0:
            return [DetectorAdequacyStatus.ALL_REJECTING]

        all_e1_pass = all(t.e1 == 1 for t in triples)
        all_e2_pass = all(t.e2 == 1 for t in triples)
        if all_e1_pass and all_e2_pass:
            warnings.append(DetectorAdequacyStatus.VACUOUS_LOCAL)

        all_e1_fail = all(t.e1 == 0 for t in triples)
        all_e2_fail = all(t.e2 == 0 for t in triples)
        if all_e1_fail or all_e2_fail:
            warnings.append(DetectorAdequacyStatus.ALL_REJECTING)

        all_local_prod_zero = all(t.local_product == 0 for t in triples)
        if all_local_prod_zero and not (all_e1_fail or all_e2_fail):
            warnings.append(DetectorAdequacyStatus.CONSTANT_LOCAL_PRODUCT_ZERO)

        all_eg_fail = all(t.eg == 0 for t in triples)
        if all_eg_fail:
            warnings.append(DetectorAdequacyStatus.CONSTANT_GLOBAL_REJECT)

        all_eg_pass = all(t.eg == 1 for t in triples)
        if all_eg_pass:
            warnings.append(DetectorAdequacyStatus.CONSTANT_GLOBAL_ACCEPT)

        all_tautological = all(t.eg == t.local_product for t in triples)
        if all_tautological:
            warnings.append(DetectorAdequacyStatus.OBSERVED_AGREEMENT_SAMPLE_LEVEL)

        if boundary_slice is not None and len(boundary_slice.states) <= 1:
            if composed_trajectories is not None and len(composed_trajectories) > 0:
                is_terminal_or_identity = all(
                    t.intermediate_state == t.end_state or t.intermediate_state == t.start_state or
                    (len(t.segment_2.actions) == 0 and t.segment_2.raw_action == 0.0)
                    for t in composed_trajectories
                )
                if is_terminal_or_identity:
                    warnings.append(DetectorAdequacyStatus.TRIVIAL_SLICE)
                else:
                    warnings.append(DetectorAdequacyStatus.SINGLETON_SLICE_CUT_UNASSESSED)
            else:
                warnings.append(DetectorAdequacyStatus.SINGLETON_SLICE_CUT_UNASSESSED)

        if not warnings:
            warnings.append(DetectorAdequacyStatus.NO_LISTED_DEGENERACY_OBSERVED)

        return warnings

    check = audit


def make_five_trace_phone_test() -> List[EvaluatorVerdictTriple]:
    """
    Returns the canonical five-trace fixture from Paper 012 Section 1.6:
    Trace 1: (1, 1, 1) -> Delta_E = 0 (ZDR)
    Trace 2: (1, 1, 0) -> Delta_E = -1 (NGD)
    Trace 3: (1, 1, 0) -> Delta_E = -1 (NGD)
    Trace 4: (1, 0, 0) -> Delta_E = 0 (ZDR)
    Trace 5: (0, 1, 0) -> Delta_E = 0 (ZDR)
    Expected metrics:
      LPR = 0.60, GPR = 0.20, mean_Delta_E = -0.40
      NGD = 0.40, PGD = 0.00, ZDR = 0.60, EGD = 0.40
    """
    return [
        EvaluatorVerdictTriple(e1=1, e2=1, eg=1),
        EvaluatorVerdictTriple(e1=1, e2=1, eg=0),
        EvaluatorVerdictTriple(e1=1, e2=1, eg=0),
        EvaluatorVerdictTriple(e1=1, e2=0, eg=0),
        EvaluatorVerdictTriple(e1=0, e2=1, eg=0),
    ]
