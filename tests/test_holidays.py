"""Tests covering the holiday-aware trading-day logic."""

from __future__ import annotations

from datetime import date

import pytest

from vn_market_calendar import HNX, HOSE, UPCOM


@pytest.fixture()
def hose() -> HOSE:
    return HOSE()


@pytest.mark.parametrize(
    "iso",
    [
        "2024-01-01",  # New Year's Day
        "2024-04-30",  # Reunification Day
        "2024-05-01",  # Labour Day
        "2024-09-02",  # National Day
        "2025-01-29",  # Tet Day 1 (At Ty)
        "2025-04-30",  # Reunification 2025
        "2023-05-02",  # Reunification observed (Apr 30 was Sun)
        "2020-04-02",  # Hung Kings 2020
        "2018-04-25",  # Hung Kings 2018
    ],
)
def test_known_holidays_are_not_trading_days(hose: HOSE, iso: str) -> None:
    assert hose.is_trading_day(iso) is False
    assert hose.is_holiday(iso) is True


@pytest.mark.parametrize(
    "iso",
    [
        "2024-01-02",  # Tue after NYD
        "2024-05-02",  # Thu after Labour Day
        "2024-09-04",  # Wed after National Day
        "2025-02-04",  # Tue after Tet break
    ],
)
def test_regular_trading_days(hose: HOSE, iso: str) -> None:
    assert hose.is_trading_day(iso) is True
    assert hose.is_holiday(iso) is False


def test_weekends_are_not_trading_days(hose: HOSE) -> None:
    # 2024-04-27 = Sat, 2024-04-28 = Sun
    assert hose.is_trading_day("2024-04-27") is False
    assert hose.is_trading_day("2024-04-28") is False


def test_holidays_shared_across_exchanges() -> None:
    """All three exchanges observe the same public-holiday list."""
    hose, hnx, upcom = HOSE(), HNX(), UPCOM()
    for iso in ("2024-04-30", "2025-01-29", "2024-09-02"):
        assert not hose.is_trading_day(iso)
        assert not hnx.is_trading_day(iso)
        assert not upcom.is_trading_day(iso)


def test_holiday_data_spans_2018_to_2027(hose: HOSE) -> None:
    years = {d.year for d in hose.holidays}
    for y in range(2018, 2028):
        assert y in years, f"missing holidays for {y}"


def test_accepts_date_and_str(hose: HOSE) -> None:
    assert hose.is_trading_day(date(2024, 5, 2)) is True
    assert hose.is_trading_day("2024-05-02") is True
