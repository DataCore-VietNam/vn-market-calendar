"""Tests for intraday session schedules."""

from __future__ import annotations

from datetime import time

import pytest

from vn_market_calendar import HNX, HOSE, UPCOM, Session


@pytest.fixture()
def hose() -> HOSE:
    return HOSE()


def test_hose_sessions_on_normal_day(hose: HOSE) -> None:
    sessions = hose.sessions("2024-05-02")  # Thursday, normal day
    names = [s.name for s in sessions]
    assert names == [
        "pre_open_ato",
        "continuous_morning",
        "lunch_break",
        "continuous_afternoon",
        "atc",
        "put_through",
    ]
    ato = sessions[0]
    assert ato.start == time(9, 0) and ato.end == time(9, 15)
    assert sessions[-1].end == time(15, 0)


def test_hose_sessions_empty_on_holiday(hose: HOSE) -> None:
    assert hose.sessions("2024-04-30") == []  # Reunification Day


def test_hose_sessions_empty_on_weekend(hose: HOSE) -> None:
    assert hose.sessions("2024-04-27") == []  # Saturday


def test_hnx_has_no_pre_open_ato() -> None:
    sessions = HNX().sessions("2024-05-02")
    assert sessions[0].name == "continuous_morning"
    assert sessions[0].start == time(9, 0)


def test_upcom_has_no_atc() -> None:
    sessions = UPCOM().sessions("2024-05-02")
    names = [s.name for s in sessions]
    assert "atc" not in names
    assert "put_through" not in names
    # UPCOM closes at 15:00.
    assert sessions[-1].end == time(15, 0)


def test_session_contains() -> None:
    s = Session("test", time(9, 0), time(11, 30))
    assert s.contains(time(9, 0)) is True
    assert s.contains(time(10, 0)) is True
    assert s.contains(time(11, 30)) is False  # end is exclusive
    assert s.contains(time(8, 59)) is False
