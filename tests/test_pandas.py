"""Smoke tests for the optional pandas helpers."""

from __future__ import annotations

import pytest

pd = pytest.importorskip("pandas")

from vn_market_calendar.pandas_helpers import (  # noqa: E402
    is_trading_day_series,
    next_trading_day_series,
    trading_days,
)


def test_trading_days_returns_datetime_index() -> None:
    idx = trading_days("2024-04-26", "2024-05-03", exchange="HOSE")
    assert isinstance(idx, pd.DatetimeIndex)
    # 2024-04-26 Fri, then long holiday block, then 2024-05-02 Thu + 2024-05-03 Fri.
    assert list(idx.strftime("%Y-%m-%d")) == ["2024-04-26", "2024-05-02", "2024-05-03"]
    assert idx.name == "trading_day"


def test_is_trading_day_series_against_holidays() -> None:
    dates = ["2024-04-29", "2024-04-30", "2024-05-01", "2024-05-02", "2024-05-04"]
    out = is_trading_day_series(dates, exchange="HOSE")
    assert out.tolist() == [False, False, False, True, False]
    assert out.dtype == bool


def test_next_trading_day_series_skips_holidays() -> None:
    dates = ["2024-04-26", "2024-05-02"]
    out = next_trading_day_series(dates, exchange="HOSE")
    assert out.iloc[0] == pd.Timestamp("2024-05-02")
    assert out.iloc[1] == pd.Timestamp("2024-05-03")


def test_pandas_helpers_accept_exchange_alias() -> None:
    idx = trading_days("2024-05-02", "2024-05-02", exchange="HNX")
    assert len(idx) == 1
