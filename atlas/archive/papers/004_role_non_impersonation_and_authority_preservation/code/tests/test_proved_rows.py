"""Proved rows must be evaluated by the shipped role table and refusal pipeline."""

from proved_rows import replay_proved_rows


def test_proved_rows_call_shipped_checker():
    report = replay_proved_rows()
    row = report["C3-C14"]
    assert report["ok"] is True
    assert row["role_count"] == 6
    assert row["distinct_failures"] == 6
    assert row["roundtrip"] is True
    assert row["authority_failure"] == "proposal_becomes_action"
    assert row["refusal_absorbed"] is True
    assert row["later_stages_called"] == []
    assert row["halted_refusal"] is True
    assert row["authority_not_residual"] is True
    assert row["residual_not_authority"] is True
    assert row["refusal_not_authority"] is True
    assert row["same_payload"] is True
    assert row["distinct_role_failures"] is True
    assert row["payload_map_misses_actual"] is True
    assert row["mixed_fiber"] is True
    assert row["mixed_all"] is False
    assert row["mixed_exact"] is False
    assert row["constant_exact"] is True
    assert row["adjunction_example"] is True
