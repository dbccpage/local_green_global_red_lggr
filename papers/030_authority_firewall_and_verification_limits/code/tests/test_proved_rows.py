"""AVF-030-C11 must be evaluated by the shipped partition checker."""

from proved_rows import replay_proved_rows


def test_calibration_completeness_calls_shipped_checker():
    report = replay_proved_rows()
    row = report["AVF-030-C11"]
    assert report["ok"] is True
    assert row["carrier_size"] == 5
    assert row["complete_coverage"] is True
    assert row["complete_error"] is None
    assert row["omitted_coverage"] is False
    assert "Coverage incomplete" in row["omitted_error"]
    assert row["counterexample_class_constant"] is True
    assert row["counterexample_agrees_on_tested"] is True
    assert row["counterexample_disagrees_on_omitted"] is True
    assert row["omitted_witness_coordinates"] == ["1", "1"]
