"""Runnable demo of the vn-market-calendar API.

Run with::

    python examples/usage.py
"""

from __future__ import annotations

from vn_market_calendar import HNX, HOSE, UPCOM, get_calendar


def main() -> None:
    hose = HOSE()

    print("== Trading-day checks ==")
    for d in ("2024-04-30", "2024-05-02", "2025-01-29", "2025-02-04"):
        flag = "TRADING" if hose.is_trading_day(d) else "CLOSED"
        print(f"  {d}  {flag}")

    print("\n== Next trading day after the April-May 2024 holiday block ==")
    print(f"  next after 2024-04-26: {hose.next_trading_day('2024-04-26')}")

    print("\n== Trading-day count for 2024 ==")
    print(f"  HOSE trading days in 2024: {hose.count_trading_days('2024-01-01', '2024-12-31')}")

    print("\n== HOSE intraday sessions on 2024-05-02 ==")
    for s in hose.sessions("2024-05-02"):
        print(f"  {s.name:<22} {s.start.strftime('%H:%M')}-{s.end.strftime('%H:%M')}")

    print("\n== HOSE tick size at sample prices ==")
    for p in (5_000, 25_000, 100_000):
        print(f"  price {p:>8,d} VND -> tick {hose.tick_size(p)} VND")

    print("\n== Cross-exchange via get_calendar() ==")
    for name in ("HOSE", "HNX", "UPCOM"):
        cal = get_calendar(name)
        s = cal.sessions("2024-05-02")
        print(f"  {name}: {len(s)} sessions, tick@20000 = {cal.tick_size(20_000)} VND")

    # Optional pandas integration.
    try:
        from vn_market_calendar.pandas_helpers import trading_days

        idx = trading_days("2024-04-26", "2024-05-06", exchange="HOSE")
        print("\n== pandas DatetimeIndex of HOSE trading days, late Apr/early May 2024 ==")
        print(idx)
    except ImportError:
        print("\n(pandas not installed — install with `pip install vn-market-calendar[pandas]`)")

    # Suppress unused-import warnings.
    _ = (HNX, UPCOM)


if __name__ == "__main__":
    main()
