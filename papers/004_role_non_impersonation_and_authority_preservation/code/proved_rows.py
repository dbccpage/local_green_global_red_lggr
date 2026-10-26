"""Finite checks for the proved rows of the role non-impersonation paper.

The checks call the shipped role table, refusal monad, and terminal
constructors. They do not restate those definitions.
"""

from __future__ import annotations

from models import (
    FAILURE_TO_ROLE,
    ROLE_TO_FAILURE,
    AuthorityToken,
    FailureMode,
    Proposal,
    Role,
    Terminal,
    TerminalStatus,
    TypedPacket,
)
from pipeline import AuthorityPipeline, Refusal, Success


def _all_along(states, quotient, predicate, image):
    return all(predicate(state) for state in states if quotient(state) == image)


def replay_proved_rows() -> dict:
    roles = list(Role)
    failures = [ROLE_TO_FAILURE[role] for role in roles]
    roundtrip = all(FAILURE_TO_ROLE[ROLE_TO_FAILURE[role]] is role for role in roles)
    inverse = all(ROLE_TO_FAILURE[FAILURE_TO_ROLE[mode]] is mode for mode in FailureMode)

    refused = Refusal("stage_refused")
    absorbed = refused.bind(lambda _value: Success("continued"))

    calls: list[str] = []

    def refuse(_proposal: Proposal) -> Refusal:
        return Refusal("obstruction")

    def later(name: str):
        def stage(proposal: Proposal):
            calls.append(name)
            return Success(proposal)

        return stage

    halted = AuthorityPipeline(
        obstruction_stage=refuse,
        transport_stage=later("transport"),
        descent_stage=later("descent"),
        verify_stage=later("verify"),
        terminalize_stage=later("terminal"),
    ).execute(Proposal(id=1, payload="same"))

    token = AuthorityToken(
        proposal_id=1,
        verifier="verifier",
        replayable=True,
        receipt_digest="digest",
        receipt_id="receipt",
    )
    authority = Terminal(status=TerminalStatus.AUTHORITY, token=token)
    residual = Terminal(status=TerminalStatus.RESIDUAL_CLOSED)
    refusal = Terminal(status=TerminalStatus.REFUSAL, reason="refused")

    intended = TypedPacket("payload", Role.AUTHORITY)
    actual = TypedPacket("payload", Role.RESIDUAL)
    intended_failure = ROLE_TO_FAILURE[intended.role]
    actual_failure = ROLE_TO_FAILURE[actual.role]
    payload_only = {intended.payload: intended_failure}

    constant_packet = TypedPacket("only", Role.AUTHORITY)

    def quotient(packet: TypedPacket) -> str:
        return packet.payload

    def authorized(packet: TypedPacket) -> bool:
        return packet.role is Role.AUTHORITY

    mixed_states = (intended, actual)
    constant_states = (constant_packet,)
    mixed_image = quotient(intended)
    constant_image = quotient(constant_packet)
    mixed_all = _all_along(mixed_states, quotient, authorized, mixed_image)
    constant_all = _all_along(constant_states, quotient, authorized, constant_image)
    mixed_exact = all(
        (_all_along(mixed_states, quotient, authorized, quotient(state)) is authorized(state))
        for state in mixed_states
    )
    constant_exact = all(
        (
            _all_along(constant_states, quotient, authorized, quotient(state))
            is authorized(state)
        )
        for state in constant_states
    )

    sound_image = "kept"
    sound_states = (
        TypedPacket(sound_image, Role.AUTHORITY),
        TypedPacket("dropped", Role.AUTHORITY),
        TypedPacket("dropped", Role.RESIDUAL),
    )

    def sound_b(image: str) -> bool:
        return image == sound_image

    pullback_inside = all(
        (not sound_b(quotient(state))) or authorized(state) for state in sound_states
    )
    b_inside_all = all(
        (not sound_b(image))
        or _all_along(sound_states, quotient, authorized, image)
        for image in {quotient(state) for state in sound_states}
    )

    row = {
        "role_count": len(roles),
        "distinct_failures": len(set(failures)),
        "roundtrip": roundtrip and inverse,
        "authority_failure": intended_failure.value,
        "refusal_absorbed": absorbed == refused and absorbed.reason == "stage_refused",
        "later_stages_called": list(calls),
        "halted_refusal": halted.is_refusal() and not halted.is_success(),
        "authority_not_residual": authority.is_authority
        and not authority.is_residual
        and not authority.is_refusal,
        "residual_not_authority": residual.is_residual and not residual.is_authority,
        "refusal_not_authority": refusal.is_refusal and not refusal.is_authority,
        "same_payload": intended.payload == actual.payload,
        "distinct_role_failures": intended_failure != actual_failure,
        "payload_map_misses_actual": payload_only[actual.payload] != actual_failure,
        "mixed_fiber": authorized(intended)
        and not authorized(actual)
        and quotient(intended) == quotient(actual),
        "mixed_all": mixed_all,
        "mixed_exact": mixed_exact,
        "constant_exact": constant_exact and constant_all,
        "adjunction_example": pullback_inside and b_inside_all,
    }
    row_ok = (
        row["role_count"] == 6
        and row["distinct_failures"] == 6
        and row["roundtrip"]
        and row["authority_failure"] == "proposal_becomes_action"
        and row["refusal_absorbed"]
        and row["later_stages_called"] == []
        and row["halted_refusal"]
        and row["authority_not_residual"]
        and row["residual_not_authority"]
        and row["refusal_not_authority"]
        and row["same_payload"]
        and row["distinct_role_failures"]
        and row["payload_map_misses_actual"]
        and row["mixed_fiber"]
        and row["mixed_all"] is False
        and row["mixed_exact"] is False
        and row["constant_exact"]
        and row["adjunction_example"]
    )
    return {"ok": row_ok, "C3-C14": row}
