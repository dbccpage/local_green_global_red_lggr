"""Explicit commuting-square and chain-retraction checks on finite rational maps.

Forward transport preserves repairs. Forward transport *alone* does not imply
that target repairability reflects source repairability.
"""
from __future__ import annotations

from typing import Any

from .common import ValidationError, digest, json_value
from .linear import identity, is_zero, matmul, matrix, subtract


def verify_transport(D_source: Any, D_target: Any, F0: Any, F1: Any,
                     *, G0: Any | None = None, G1: Any | None = None) -> dict[str, Any]:
    """Check F1 Ds = Dt F0, optionally with a left-inverse chain map G.

    Ds:C0s->C1s; Dt:C0t->C1t. A verified retraction requires both
    G1 Dt = Ds G0 and G0 F0 = id, G1 F1 = id. This is a sufficient
    repair-reflection certificate, not a necessary condition for every query.
    """
    ds, dt = matrix(D_source, "D_source"), matrix(D_target, "D_target")
    ms, ns, mt, nt = len(ds), len(ds[0]), len(dt), len(dt[0])
    f0, f1 = matrix(F0, "F0", rows=nt, cols=ns), matrix(F1, "F1", rows=mt, cols=ms)
    forward_defect = subtract(matmul(f1, ds), matmul(dt, f0))
    forward = is_zero(forward_defect)
    if (G0 is None) != (G1 is None):
        raise ValidationError("Supply both G0 and G1, or neither")
    reflected = False
    backward_defect = left0_defect = left1_defect = None
    if G0 is not None:
        g0, g1 = matrix(G0, "G0", rows=ns, cols=nt), matrix(G1, "G1", rows=ms, cols=mt)
        backward_defect = subtract(matmul(g1, dt), matmul(ds, g0))
        left0_defect = subtract(matmul(g0, f0), identity(ns))
        left1_defect = subtract(matmul(g1, f1), identity(ms))
        reflected = forward and all(is_zero(a) for a in (backward_defect, left0_defect, left1_defect))
    if not forward:
        status = "INVALID_TRANSPORT"
    elif G0 is not None and not reflected:
        status = "RETRACTION_REJECTED"
    else:
        status = "RETRACTION_VERIFIED" if reflected else "COMMUTING_TRANSPORT_VERIFIED"
    return json_value({"schema": "lggr.transport.v1", "authority_effect": "None", "status": status,
                       "input_sha256": digest({"Ds": ds, "Dt": dt, "F0": f0, "F1": f1, "G0": G0, "G1": G1}),
                       "forward_commutes": forward,
                       "repair_preservation_verified": forward,
                       "nonrepairability_reflection_verified": reflected,
                       "forward_defect": forward_defect, "backward_defect": backward_defect,
                       "left_inverse_C0_defect": left0_defect, "left_inverse_C1_defect": left1_defect,
                       "scope": "Supplied finite rational maps only. No unprovided runtime interpretation is inferred."})
