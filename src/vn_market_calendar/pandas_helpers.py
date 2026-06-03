"""Optional pandas helpers built on top of the core calendars.

Importing this module requires ``pandas``; install with::

    pip install vn-market-calendar[pandas]
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from typing import TYPE_CHECKING

from vn_market_calendar.exchanges import BaseCalendar, get_calendar

if TYPE_CHECKING:  # pragma: no cover - typing only
    import pandas as pd

try:  # Runtime import — pandas is an optional dependency.
    import pandas as pd
except ImportError as exc:  # pragma: no cover - exercised only when pandas missing
    raise ImportError(
        "pandas is required for vn_market_calendar.pandas_helpers. "
        "Install with: pip install vn-market-calendar[pandas]"
    ) from exc


def _resolve(exchange: str | BaseCalendar) -> BaseCalendar:
    """Return a calendar instance for ``exchange`` (name or instance)."""
    if isinstance(exchange, BaseCalendar):
        return exchange
    return get_calendar(exchange)


def trading_days(
    start: str | date | pd.Timestamp,
    end: str | date | pd.Timestamp,
    exchange: str | BaseCalendar = "HOSE",
) -> pd.DatetimeIndex:
    """Return a ``DatetimeIndex`` of trading days in ``[start, end]``.

    Args:
        start: Inclusive lower bound (anything ``pd.Timestamp`` can parse).
        end: Inclusive upper bound.
        exchange: Exchange name (``"HOSE"``, ``"HNX"``, ``"UPCOM"``) or
            an instantiated calendar.

    Returns:
        A ``pd.DatetimeIndex`` with ``name="trading_day"`` containing only
        trading sessions.
    """
    cal = _resolve(exchange)
    start_d = pd.Timestamp(start).date()
    end_d = pd.Timestamp(end).date()
    days = cal.trading_days(start_d, end_d)
    return pd.DatetimeIndex(pd.to_datetime(days), name="trading_day")


def is_trading_day_series(
    dates: Iterable[str | date | pd.Timestamp] | pd.Series | pd.DatetimeIndex,
    exchange: str | BaseCalendar = "HOSE",
) -> pd.Series:
    """Vectorised ``is_trading_day`` returning a boolean ``Series``.

    The output index matches the input where possible (Series/DatetimeIndex);
    otherwise a default ``RangeIndex`` is used.
    """
    cal = _resolve(exchange)
    idx = pd.to_datetime(pd.Index(list(dates)) if not hasattr(dates, "__len__") else pd.Index(dates))
    values = [cal.is_trading_day(ts.date()) for ts in idx]
    return pd.Series(values, index=idx, name="is_trading_day", dtype=bool)


def next_trading_day_series(
    dates: Iterable[str | date | pd.Timestamp] | pd.Series | pd.DatetimeIndex,
    exchange: str | BaseCalendar = "HOSE",
) -> pd.Series:
    """Vectorised ``next_trading_day`` returning a ``Series`` of Timestamps."""
    cal = _resolve(exchange)
    idx = pd.to_datetime(pd.Index(list(dates)) if not hasattr(dates, "__len__") else pd.Index(dates))
    values = [pd.Timestamp(cal.next_trading_day(ts.date())) for ts in idx]
    return pd.Series(values, index=idx, name="next_trading_day")


__all__ = [
    "trading_days",
    "is_trading_day_series",
    "next_trading_day_series",
]
