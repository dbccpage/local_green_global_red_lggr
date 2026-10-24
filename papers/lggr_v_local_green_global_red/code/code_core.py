"""Core mathematical objects: Sites, Interfaces, Assignments, Evaluators, and System."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Mapping, Sequence

import numpy as np


class NormType(Enum):
    L1 = "L1"
    L2 = "L2"
    LINF = "LINF"


def scaled_euclidean_norm(v: np.ndarray) -> float:
    """Compute scaled Euclidean norm s * sqrt(sum((v/s)**2)) to avoid underflow and overflow."""
    arr = np.asarray(v, dtype=float).ravel()
    if arr.size == 0:
        return 0.0
    s = float(np.max(np.abs(arr)))
    if s == 0.0:
        return 0.0
    scaled = arr / s
    val = s * float(np.sqrt(np.sum(scaled * scaled)))
    if not np.isfinite(val):
        raise ValueError(f"Computed Euclidean norm is non-finite: {val}")
    return val


def compute_norm(v: np.ndarray, norm_type: NormType = NormType.L1) -> float:
    """Compute vector norm."""
    arr = np.asarray(v, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"Expected 1D vector for compute_norm, got shape {arr.shape}")
    if not np.all(np.isfinite(arr)):
        raise ValueError("Vector contains non-finite values (NaN or Inf)")
    if arr.size == 0:
        return 0.0
    if norm_type == NormType.L1:
        val = float(np.sum(np.abs(arr)))
    elif norm_type == NormType.L2:
        val = scaled_euclidean_norm(arr)
    elif norm_type == NormType.LINF:
        val = float(np.max(np.abs(arr)))
    else:
        raise ValueError(f"Unsupported norm type: {norm_type}")
    if not np.isfinite(val):
        raise ValueError(f"Computed norm is non-finite: {val}")
    return val


@dataclass(frozen=True)
class Site:
    """A site x with state dimension and norm."""
    name: str
    dimension: int
    norm_type: NormType = NormType.L1

    def __post_init__(self):
        if not isinstance(self.dimension, (int, np.integer)) or isinstance(self.dimension, bool) or self.dimension < 1:
            raise ValueError(f"Site dimension must be a positive integer >= 1, got {self.dimension}")



@dataclass(frozen=True)
class Interface:
    """A directed interface e = (a, b) carrying translation map r_e: F(b) -> F(a)."""
    name: str
    site_a: str  # Target site a (which holds state s(a))
    site_b: str  # Source site b (whose state s(b) is translated into a's terms)
    translation_matrix: np.ndarray  # Shape: (dim_a, dim_b)
    norm_type: NormType = NormType.L1

    def __post_init__(self):
        mat = np.asarray(self.translation_matrix, dtype=float)
        if mat.ndim != 2:
            raise ValueError(f"Interface '{self.name}' translation matrix must be 2D, got shape {mat.shape}")
        if not np.all(np.isfinite(mat)):
            raise ValueError(f"Interface '{self.name}' translation matrix contains non-finite values")
        object.__setattr__(self, "translation_matrix", mat)

    def translate(self, state_b: np.ndarray) -> np.ndarray:
        """Translate state_b into site a's terms: r_e(s(b))."""
        sb = np.asarray(state_b, dtype=float)
        if sb.ndim != 1 or sb.shape[0] != self.translation_matrix.shape[1]:
            raise ValueError(
                f"Interface '{self.name}' expected source state dimension {self.translation_matrix.shape[1]}, "
                f"got shape {sb.shape}"
            )
        if not np.all(np.isfinite(sb)):
            raise ValueError(f"Source state for interface '{self.name}' contains non-finite values")
        return self.translation_matrix @ sb

    def compute_defect(self, state_a: np.ndarray, state_b: np.ndarray) -> np.ndarray:
        """Compute defect Δ(s)_e = r_e(s(b)) - s(a)."""
        sa = np.asarray(state_a, dtype=float)
        if sa.ndim != 1 or sa.shape[0] != self.translation_matrix.shape[0]:
            raise ValueError(
                f"Interface '{self.name}' expected target state dimension {self.translation_matrix.shape[0]}, "
                f"got shape {sa.shape}"
            )
        if not np.all(np.isfinite(sa)):
            raise ValueError(f"Target state for interface '{self.name}' contains non-finite values")
        return self.translate(state_b) - sa


@dataclass
class Assignment:
    """State assignment mapping site_name -> state vector."""
    states: Dict[str, np.ndarray] = field(default_factory=dict)

    def set_state(self, site_name: str, state: Sequence[float] | np.ndarray) -> None:
        arr = np.asarray(state, dtype=float)
        if arr.ndim != 1:
            raise ValueError(f"State for site '{site_name}' must be a 1D vector, got shape {arr.shape}")
        if not np.all(np.isfinite(arr)):
            raise ValueError(f"State for site '{site_name}' contains non-finite values")
        self.states[site_name] = arr

    def get_state(self, site_name: str) -> np.ndarray:
        if site_name not in self.states:
            raise KeyError(f"Site '{site_name}' not assigned in assignment")
        return self.states[site_name]

    def validate_against_sites(self, sites: Mapping[str, Site]) -> None:
        """Validate that all sites are assigned with matching dimensions and finite values."""
        for site_name, site in sites.items():
            if site_name not in self.states:
                raise ValueError(f"Site '{site_name}' is missing from assignment")
            s = np.asarray(self.states[site_name], dtype=float)
            if s.ndim != 1 or s.shape != (site.dimension,):
                raise ValueError(
                    f"Site '{site_name}' requires 1D state of shape ({site.dimension},), got {s.shape}"
                )
            if not np.all(np.isfinite(s)):
                raise ValueError(f"Site '{site_name}' state contains non-finite values")


def compute_defect(interface: Interface, assignment: Assignment) -> np.ndarray:
    """Compute defect for an interface under a given assignment."""
    sa = assignment.get_state(interface.site_a)
    sb = assignment.get_state(interface.site_b)
    return interface.compute_defect(sa, sb)


def compute_global_inconsistency(
    interfaces: Mapping[str, Interface],
    assignment: Assignment,
) -> float:
    """Compute total global inconsistency I(s) = sum_e ||Δ(s)_e||."""
    total = 0.0
    for interface in interfaces.values():
        d = compute_defect(interface, assignment)
        total += compute_norm(d, interface.norm_type)
        if not np.isfinite(total):
            raise ValueError(f"Accumulated global inconsistency is non-finite: {total}")
    return total


@dataclass
class Evaluator:
    """An evaluator alpha watching a subset of interfaces through lossy linear measurements."""
    name: str
    watched_interfaces: List[str]
    # Mapping interface_name -> measurement matrix q_e^alpha
    measurement_matrices: Dict[str, np.ndarray]
    value_norms: Dict[str, NormType] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if len(self.watched_interfaces) != len(set(self.watched_interfaces)):
            raise ValueError(
                f"Evaluator '{self.name}' watched_interfaces contains duplicate entries: "
                f"{self.watched_interfaces}. Watched interfaces must form a distinct set."
            )
        for iface_name in self.watched_interfaces:
            if iface_name not in self.measurement_matrices:
                raise ValueError(
                    f"Evaluator '{self.name}' watches interface '{iface_name}' "
                    f"but lacks a corresponding measurement matrix."
                )
            mat = np.asarray(self.measurement_matrices[iface_name], dtype=float)
            if mat.ndim != 2:
                raise ValueError(
                    f"Evaluator '{self.name}' measurement matrix for '{iface_name}' "
                    f"must be 2D, got shape {mat.shape}."
                )
            if not np.all(np.isfinite(mat)):
                raise ValueError(
                    f"Evaluator '{self.name}' measurement matrix for '{iface_name}' "
                    f"contains non-finite values."
                )

    def measure_defect(self, interface_name: str, defect: np.ndarray) -> np.ndarray:
        """Apply linear measurement q_e^alpha(Δ_e)."""
        if interface_name not in self.measurement_matrices:
            raise KeyError(f"Interface '{interface_name}' not watched by evaluator '{self.name}'")
        q = np.asarray(self.measurement_matrices[interface_name], dtype=float)
        d = np.asarray(defect, dtype=float)
        if d.ndim != 1 or d.shape[0] != q.shape[1]:
            raise ValueError(
                f"Evaluator '{self.name}' measurement matrix for '{interface_name}' "
                f"expects input dimension {q.shape[1]}, got {d.shape}"
            )
        if not np.all(np.isfinite(d)):
            raise ValueError(f"Defect vector for '{interface_name}' contains non-finite values")
        return q @ d

    def compute_score(
        self,
        interfaces: Mapping[str, Interface],
        assignment: Assignment,
    ) -> float:
        """Compute evaluator score J^alpha(s) = sum_{e in E^alpha} ||q_e^alpha(Δ(s)_e)||."""
        score = 0.0
        for iface_name in self.watched_interfaces:
            iface = interfaces[iface_name]
            d = compute_defect(iface, assignment)
            measured = self.measure_defect(iface_name, d)
            norm_t = self.value_norms.get(iface_name, iface.norm_type)
            score += compute_norm(measured, norm_t)
            if not np.isfinite(score):
                raise ValueError(f"Accumulated evaluator score is non-finite: {score}")
        return score


@dataclass
class EvaluatorFamily:
    """A family of evaluators monitoring a system."""
    evaluators: Dict[str, Evaluator] = field(default_factory=dict)

    def add_evaluator(self, evaluator: Evaluator) -> None:
        self.evaluators[evaluator.name] = evaluator

    def compute_all_scores(
        self,
        interfaces: Mapping[str, Interface],
        assignment: Assignment,
    ) -> Dict[str, float]:
        """Compute J^alpha(s) for every evaluator in the family."""
        return {
            name: ev.compute_score(interfaces, assignment)
            for name, ev in self.evaluators.items()
        }

    def is_all_green(
        self,
        interfaces: Mapping[str, Interface],
        assignment: Assignment,
        tol: float = 1e-9,
    ) -> bool:
        """Check if every evaluator reports Local Green (J^alpha(s) <= tol)."""
        scores = self.compute_all_scores(interfaces, assignment)
        return all(s <= tol for s in scores.values())


@dataclass
class System:
    """Complete finite evaluation system with sites, interfaces, and evaluator family."""
    sites: Dict[str, Site] = field(default_factory=dict)
    interfaces: Dict[str, Interface] = field(default_factory=dict)
    evaluator_family: EvaluatorFamily = field(default_factory=EvaluatorFamily)

    def add_site(self, site: Site) -> None:
        self.sites[site.name] = site

    def add_interface(self, interface: Interface) -> None:
        if interface.site_a not in self.sites or interface.site_b not in self.sites:
            raise ValueError(f"Interface sites must exist in system sites: {interface.site_a}, {interface.site_b}")
        site_a = self.sites[interface.site_a]
        site_b = self.sites[interface.site_b]
        if interface.norm_type != site_a.norm_type:
            raise ValueError(
                f"Interface '{interface.name}' norm ({interface.norm_type}) does not match "
                f"target site '{site_a.name}' declared norm ({site_a.norm_type})"
            )
        dim_a = site_a.dimension
        dim_b = site_b.dimension
        mat = np.asarray(interface.translation_matrix, dtype=float)
        if mat.ndim != 2 or mat.shape != (dim_a, dim_b):
            raise ValueError(
                f"Interface '{interface.name}' translation matrix shape {mat.shape} "
                f"does not match site dimensions ({dim_a}, {dim_b})"
            )
        self.interfaces[interface.name] = interface

    def add_evaluator(self, evaluator: Evaluator) -> None:
        for iface in evaluator.watched_interfaces:
            if iface not in self.interfaces:
                raise ValueError(f"Evaluator '{evaluator.name}' watches non-existent interface '{iface}'")
            dim_a = self.sites[self.interfaces[iface].site_a].dimension
            q = np.asarray(evaluator.measurement_matrices[iface], dtype=float)
            if q.shape[1] != dim_a:
                raise ValueError(
                    f"Evaluator '{evaluator.name}' measurement matrix for '{iface}' "
                    f"has column dimension {q.shape[1]}, expected {dim_a}"
                )
        self.evaluator_family.add_evaluator(evaluator)

    def global_inconsistency(self, assignment: Assignment) -> float:
        assignment.validate_against_sites(self.sites)
        return compute_global_inconsistency(self.interfaces, assignment)

    def evaluator_scores(self, assignment: Assignment) -> Dict[str, float]:
        assignment.validate_against_sites(self.sites)
        return self.evaluator_family.compute_all_scores(self.interfaces, assignment)

    def is_all_green(self, assignment: Assignment, tol: float = 1e-9) -> bool:
        scores = self.evaluator_scores(assignment)
        return all(s <= tol for s in scores.values())
