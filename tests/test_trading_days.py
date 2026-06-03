"""Tests for trading-day sequence operations."""

from __future__ import annotations

from datetime import date

import pytest

from vn_market_calendar import HOSE, get_calendar


@pytest.fixture()
def hose() -> HOSE:
    return HOSE()


def test_next_trading_day_skips_april_holiday_block(hose: HOSE) -> None:
    # 2024-04-29 Mon = bridge, 2024-04-30 Tue = Reunification,
    # 2024-05-01 Wed = Labour Day, 2024-05-02 Thu = first trading day.
    assert hose.next_trading_day("2024-04-26") == date(2024, 5, 2)


def test_next_trading_day_skips_weekend(hose: HOSE) -> None:
    # 2024-05-03 Fri -> next trading day is Monday 2024-05-06.
    assert hose.next_trading_day("2024-05-03") == date(2024, 5, 6)


def test_previous_trading_day_skips_tet(hose: HOSE) -> None:
    # First trading day before the Tet 2024 block is 2024-02-07 (Wed).
    assert hose.previous_trading_day("2024-02-15") == date(2024, 2, 7)


def test_trading_days_sequence_around_tet_2024(hose: HOSE) -> None:
    seq = hose.trading_days("2024-02-05", "2024-02-16")
    # Feb 5 Mon, 6 Tue, 7 Wed are trading. 8/9 are Tet eve+30.
    # Feb 10-11 weekend, 12-14 Tet observed, 15 Thu, 16 Fri trading.
    assert seq == [
        date(2024, 2, 5),
        date(2024, 2, 6),
        date(2024, 2, 7),
        date(2024, 2, 15),
        date(2024, 2, 16),
    ]


def test_count_trading_days_full_year_2024(hose: HOSE) -> None:
    n = hose.count_trading_days("2024-01-01", "2024-12-31")
    # 2024 has 366 days; 104 weekend days; the YAML records 12 weekday
    # holidays for 2024 (all 12 listed holidays fall on weekdays).
    assert n == 366 - 104 - 12 == 250


def test_count_trading_days_january_2024(hose: HOSE) -> None:
    # Jan 2024: 31 days, 8 weekend days, 1 weekday holiday (Jan 1 Mon).
    n = hose.count_trading_days("2024-01-01", "2024-01-31")
    assert n == 31 - 8 - 1 == 22


def test_trading_days_empty_when_start_after_end(hose: HOSE) -> None:
    assert hose.trading_days("2024-05-10", "2024-05-01") == []


def test_get_calendar_factory() -> None:
    assert get_calendar("hose").name == "HOSE"
    assert get_calendar("HNX").name == "HNX"
    assert get_calendar("upcom").name == "UPCOM"


def test_get_calendar_unknown_raises() -> None:
    with pytest.raises(KeyError):
        get_calendar("NASDAQ")
