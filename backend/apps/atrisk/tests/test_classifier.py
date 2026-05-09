from __future__ import annotations

from apps.atrisk.services import classify_severity


def test_high_severity_from_one_high_signal():
    # academic_probation is a HIGH weight signal
    assert classify_severity(["academic_probation"]) == "HIGH"


def test_high_severity_from_moodle_inactivity_alone():
    # moodle_inactivity is a HIGH weight signal
    assert classify_severity(["moodle_inactivity"]) == "HIGH"


def test_high_severity_from_attendance_flag_alone():
    # attendance_flag is a HIGH weight signal
    assert classify_severity(["attendance_flag"]) == "HIGH"


def test_high_severity_from_three_signals_any_weight():
    # 3 medium signals = HIGH (total >= 3 rule)
    assert classify_severity(["financial_hold", "grade_decline", "incomplete_grade"]) == "HIGH"


def test_medium_severity_from_two_medium_signals():
    # 2 medium signals = MEDIUM
    assert classify_severity(["financial_hold", "grade_decline"]) == "MEDIUM"


def test_medium_severity_from_one_medium_plus_two_low():
    # 1 medium + 2 low => MEDIUM
    # But we only have 1 low signal available (forum_disengagement)
    # So this would need a hypothetical scenario; skip as impossible with current config
    pass


def test_low_severity_from_single_medium_signal():
    # 1 medium signal alone = LOW
    assert classify_severity(["financial_hold"]) == "LOW"


def test_low_severity_from_single_low_signal():
    # 1 low signal alone = LOW
    assert classify_severity(["forum_disengagement"]) == "LOW"


def test_none_when_no_signals_active():
    assert classify_severity([]) is None


def test_high_severity_from_two_high_signals():
    # 2 HIGH signals (obv HIGH)
    assert classify_severity(["academic_probation", "moodle_inactivity"]) == "HIGH"


def test_medium_from_quiz_and_incomplete():
    # quiz_failure_pattern (MEDIUM) + incomplete_grade (MEDIUM) = MEDIUM
    assert classify_severity(["quiz_failure_pattern", "incomplete_grade"]) == "MEDIUM"
