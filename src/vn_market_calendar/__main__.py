"""Command-line entry point for ``python -m vn_market_calendar``.

Subcommands:
    is-trading DATE              Print "yes"/"no" and exit 0/1.
    next DATE                    Print the next trading day after DATE.
    previous DATE                Print the previous trading day before DATE.
    count START END              Print the number of trading days in [START, END].
    sessions DATE                Print intraday sessions for DATE.

All dates use ISO format (``YYYY-MM-DD``). Use ``--exchange`` to switch
between HOSE (default), HNX, and UPCOM.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date

from vn_market_calendar.exchanges import EXCHANGES, get_calendar


def _add_exchange(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--exchange",
        "-e",
        default="HOSE",
        choices=sorted(EXCHANGES),
        help="Exchange to query (default: HOSE).",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level argparse parser."""
    parser = argparse.ArgumentParser(
        prog="vn_market_calendar",
        description="Query Vietnamese exchange trading calendars from the CLI.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_is = sub.add_parser("is-trading", help="Check whether DATE is a trading day.")
    p_is.add_argument("date")
    _add_exchange(p_is)

    p_next = sub.add_parser("next", help="Print the next trading day after DATE.")
    p_next.add_argument("date")
    _add_exchange(p_next)

    p_prev = sub.add_parser("previous", help="Print the previous trading day before DATE.")
    p_prev.add_argument("date")
    _add_exchange(p_prev)

    p_count = sub.add_parser("count", help="Count trading days in [START, END] inclusive.")
    p_count.add_argument("start")
    p_count.add_argument("end")
    _add_exchange(p_count)

    p_sessions = sub.add_parser("sessions", help="List intraday sessions for DATE.")
    p_sessions.add_argument("date")
    _add_exchange(p_sessions)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    cal = get_calendar(args.exchange)

    if args.cmd == "is-trading":
        ok = cal.is_trading_day(args.date)
        print("yes" if ok else "no")
        return 0 if ok else 1

    if args.cmd == "next":
        print(cal.next_trading_day(args.date).isoformat())
        return 0

    if args.cmd == "previous":
        print(cal.previous_trading_day(args.date).isoformat())
        return 0

    if args.cmd == "count":
        print(cal.count_trading_days(args.start, args.end))
        return 0

    if args.cmd == "sessions":
        sessions = cal.sessions(args.date)
        if not sessions:
            d = date.fromisoformat(args.date)
            print(f"{d.isoformat()} is not a trading day on {cal.name}.")
            return 1
        for s in sessions:
            print(f"{s.name:<22} {s.start.strftime('%H:%M')}–{s.end.strftime('%H:%M')}")
        return 0

    parser.error(f"unknown command {args.cmd!r}")  # pragma: no cover
    return 2  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
