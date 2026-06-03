"""Exchange-specific trading calendars for Vietnamese stock exchanges.

Each exchange exposes:
    * holiday-aware ``is_trading_day`` / ``next_trading_day`` / ``trading_days``
    * intraday ``sessions(date)`` returning a list of :class:`Session` objects
    * ``tick_size(price)`` per exchange rules
    * ``lot_size(ticker)`` for round-lot quantities
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time, timedelta
from pathlib import Path
from typing import ClassVar

import yaml

# Holiday data ships inside the wheel so installs work without the repo root.
DATA_DIR = Path(__file__).resolve().parent / "data"


@dataclass(frozen=True)
class Session:
    """An intraday trading session on a Vietnamese exchange.

    Attributes:
        name: Short label (e.g. ``"ATO"``, ``"continuous_morning"``, ``"ATC"``).
        start: Session open (local Hanoi/HCMC time, no tz attached).
        end: Session close (exclusive of the next session's start).
    """

    name: str
    start: time
    end: time

    def contains(self, t: time) -> bool:
        """Return True if ``t`` is within ``[start, end)``."""
        return self.start <= t < self.end


class BaseCalendar:
    """Base class for Vietnamese exchange calendars.

    Subclasses set ``name``, ``SESSIONS``, ``TICK_BANDS``, and override
    methods as needed. Holidays are loaded once at construction from
    :data:`DATA_DIR` / ``vn_holidays.yaml``.
    """

    name: ClassVar[str] = "BASE"
    SESSIONS: ClassVar[tuple[Session, ...]] = ()

    def __init__(self) -> None:
        self._holidays: frozenset[date] = self._load_holidays()

    @staticmethod
    def _load_holidays() -> frozenset[date]:
        """Load observed market closure dates from packaged YAML."""
        path = DATA_DIR / "vn_holidays.yaml"
        if not path.exists():
            return frozenset()
        with path.open() as f:
            data = yaml.safe_load(f) or {}
        return frozenset(date.fromisoformat(d) for d in data.get("holidays", []))

    @staticmethod
    def _coerce(d: str | date) -> date:
        return date.fromisoformat(d) if isinstance(d, str) else d

    @property
    def holidays(self) -> frozenset[date]:
        """All observed holiday dates known to this calendar."""
        return self._holidays

    def is_holiday(self, d: str | date) -> bool:
        """Return True if ``d`` is an observed market holiday."""
        return self._coerce(d) in self._holidays

    def is_trading_day(self, d: str | date) -> bool:
        """Return True if the exchange trades on ``d`` (weekday + non-holiday)."""
        day = self._coerce(d)
        if day.weekday() >= 5:
            return False
        return day not in self._holidays

    def next_trading_day(self, d: str | date) -> date:
        """Return the first trading day strictly after ``d``."""
        nxt = self._coerce(d) + timedelta(days=1)
        while not self.is_trading_day(nxt):
            nxt += timedelta(days=1)
        return nxt

    def previous_trading_day(self, d: str | date) -> date:
        """Return the most recent trading day strictly before ``d``."""
        prv = self._coerce(d) - timedelta(days=1)
        while not self.is_trading_day(prv):
            prv -= timedelta(days=1)
        return prv

    def trading_days(self, start: str | date, end: str | date) -> list[date]:
        """Return the inclusive list of trading days in ``[start, end]``."""
        cur = self._coerce(start)
        last = self._coerce(end)
        out: list[date] = []
        while cur <= last:
            if self.is_trading_day(cur):
                out.append(cur)
            cur += timedelta(days=1)
        return out

    def count_trading_days(self, start: str | date, end: str | date) -> int:
        """Number of trading days in ``[start, end]`` (inclusive)."""
        return len(self.trading_days(start, end))

    def sessions(self, d: str | date) -> list[Session]:
        """Return the list of intraday sessions for ``d``.

        Returns an empty list on weekends and holidays.
        """
        if not self.is_trading_day(d):
            return []
        return list(self.SESSIONS)


# ---------------------------------------------------------------------------
# HOSE (Ho Chi Minh Stock Exchange)
# ---------------------------------------------------------------------------


class HOSE(BaseCalendar):
    """Ho Chi Minh Stock Exchange calendar.

    Tick bands (per HOSE rules, VND):
        * price <  10,000 -> 10
        * 10,000-49,950   -> 50
        * price >= 50,000 -> 100
    """

    name: ClassVar[str] = "HOSE"

    SESSIONS: ClassVar[tuple[Session, ...]] = (
        Session("pre_open_ato", time(9, 0), time(9, 15)),
        Session("continuous_morning", time(9, 15), time(11, 30)),
        Session("lunch_break", time(11, 30), time(13, 0)),
        Session("continuous_afternoon", time(13, 0), time(14, 30)),
        Session("atc", time(14, 30), time(14, 45)),
        Session("put_through", time(14, 45), time(15, 0)),
    )

    # (upper_exclusive_price, tick_size_vnd)
    TICK_BANDS: ClassVar[tuple[tuple[float, int], ...]] = (
        (10_000, 10),
        (50_000, 50),
        (float("inf"), 100),
    )

    def tick_size(self, price: float) -> int:
        """Return the minimum price increment in VND for ``price``."""
        if price < 0:
            raise ValueError("price must be non-negative")
        for upper, tick in self.TICK_BANDS:
            if price < upper:
                return tick
        return 100

    def lot_size(self, ticker: str | None = None) -> int:
        """Round-lot size on HOSE (100 shares)."""
        return 100


# ---------------------------------------------------------------------------
# HNX (Hanoi Stock Exchange)
# ---------------------------------------------------------------------------


class HNX(BaseCalendar):
    """Hanoi Stock Exchange calendar — flat 100 VND tick."""

    name: ClassVar[str] = "HNX"

    SESSIONS: ClassVar[tuple[Session, ...]] = (
        Session("continuous_morning", time(9, 0), time(11, 30)),
        Session("lunch_break", time(11, 30), time(13, 0)),
        Session("continuous_afternoon", time(13, 0), time(14, 30)),
        Session("atc", time(14, 30), time(14, 45)),
        Session("put_through", time(14, 45), time(15, 0)),
    )

    def tick_size(self, price: float) -> int:
        """HNX uses a flat 100 VND tick across all prices."""
        if price < 0:
            raise ValueError("price must be non-negative")
        return 100

    def lot_size(self, ticker: str | None = None) -> int:
        return 100


# ---------------------------------------------------------------------------
# UPCOM (Unlisted Public Company Market)
# ---------------------------------------------------------------------------


class UPCOM(BaseCalendar):
    """UPCOM calendar — continuous-only sessions, 100 VND tick."""

    name: ClassVar[str] = "UPCOM"

    SESSIONS: ClassVar[tuple[Session, ...]] = (
        Session("continuous_morning", time(9, 0), time(11, 30)),
        Session("lunch_break", time(11, 30), time(13, 0)),
        Session("continuous_afternoon", time(13, 0), time(15, 0)),
    )

    def tick_size(self, price: float) -> int:
        """UPCOM uses a flat 100 VND tick."""
        if price < 0:
            raise ValueError("price must be non-negative")
        return 100

    def lot_size(self, ticker: str | None = None) -> int:
        return 100


EXCHANGES: dict[str, type[BaseCalendar]] = {
    "HOSE": HOSE,
    "HNX": HNX,
    "UPCOM": UPCOM,
}


def get_calendar(exchange: str) -> BaseCalendar:
    """Factory: return an instance of the named exchange calendar.

    Raises:
        KeyError: if ``exchange`` is not one of ``HOSE``, ``HNX``, ``UPCOM``.
    """
    key = exchange.upper()
    if key not in EXCHANGES:
        raise KeyError(f"Unknown exchange {exchange!r}; choose from {sorted(EXCHANGES)}")
    return EXCHANGES[key]()
