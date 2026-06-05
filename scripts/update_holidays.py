#!/usr/bin/env python3
"""
Auto-update bridge_days.yaml from government announcements.

Called by .github/workflows/auto-holidays.yml on Oct 1 each year.
Fetches confirmed bridge days from Nager.Date (public holiday API) and
appends estimates for the next 2 years if not already present.

Usage:
    python scripts/update_holidays.py [--years 2026 2027]
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import yaml  # PyYAML, installed in CI

REPO_ROOT = Path(__file__).resolve().parent.parent
BRIDGE_DAYS_FILE = REPO_ROOT / "src" / "vn_market_calendar" / "data" / "bridge_days.yaml"

# Nager.Date public-holiday API (no auth required)
NAGER_BASE = "https://date.nager.at/api/v3/PublicHolidays/{year}/VN"


def fetch_public_holidays(year: int) -> list[date]:
    url = NAGER_BASE.format(year=year)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
        return [date.fromisoformat(h["date"]) for h in data]
    except Exception as exc:
        print(f"  Warning: could not fetch {url}: {exc}", file=sys.stderr)
        return []


def detect_bridge_days(year: int, public_holidays: list[date]) -> list[date]:
    """
    A bridge day is a working day sandwiched between a public holiday and a weekend.
    Rules (Vietnamese practice):
    - If a holiday falls on Tuesday -> Monday is a bridge day (off) + Saturday is worked
    - If a holiday falls on Thursday -> Friday is a bridge day (off) + Saturday is worked
    """
    bridges: list[date] = []
    for h in public_holidays:
        if h.weekday() == 1:  # Tuesday: bridge Mon
            candidate = h - timedelta(days=1)
            if candidate not in public_holidays and candidate not in bridges:
                bridges.append(candidate)
        elif h.weekday() == 3:  # Thursday: bridge Fri
            candidate = h + timedelta(days=1)
            if candidate not in public_holidays and candidate not in bridges:
                bridges.append(candidate)
    return sorted(bridges)


def load_bridge_days() -> dict:
    if BRIDGE_DAYS_FILE.exists():
        with BRIDGE_DAYS_FILE.open() as f:
            return yaml.safe_load(f) or {}
    return {}


def save_bridge_days(data: dict) -> None:
    with BRIDGE_DAYS_FILE.open("w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=True)


def update_year(data: dict, year: int, confirmed: bool) -> bool:
    """Returns True if any change was made."""
    year_key = str(year)

    public_holidays = fetch_public_holidays(year)
    bridges = detect_bridge_days(year, public_holidays)
    bridge_str_list = [d.isoformat() for d in bridges]

    existing = data.get(year_key)

    if confirmed:
        new_entry = {"confirmed": True, "days": bridge_str_list}
    else:
        if isinstance(existing, dict) and existing.get("confirmed"):
            print(f"  {year}: already confirmed, skipping.")
            return False
        new_entry = {"confirmed": False, "days": bridge_str_list}

    if existing == new_entry:
        print(f"  {year}: no change.")
        return False

    data[year_key] = new_entry
    print(f"  {year}: updated ({'confirmed' if confirmed else 'estimate'}): {bridge_str_list}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Update bridge_days.yaml")
    parser.add_argument("--years", nargs="*", type=int, help="Years to process")
    parser.add_argument(
        "--confirm",
        nargs="*",
        type=int,
        default=[],
        help="Mark these years as confirmed (observed)",
    )
    args = parser.parse_args()

    today = date.today()
    if args.years:
        years = args.years
    else:
        years = [today.year, today.year + 1]

    data = load_bridge_days()
    changed = False

    for year in years:
        confirmed = year in args.confirm or year < today.year
        print(f"Processing {year} (confirmed={confirmed})...")
        if update_year(data, year, confirmed):
            changed = True

    if changed:
        save_bridge_days(data)
        print("bridge_days.yaml updated.")
    else:
        print("No changes needed.")
        sys.exit(0)

    sys.path.insert(0, str(REPO_ROOT / "src"))
    try:
        from vn_market_calendar.holidays import bridge_days as bd

        for year in years:
            result = bd(year)
            print(f"  Validation {year}: {len(result)} bridge days")
    except Exception as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
