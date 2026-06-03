# vn-market-calendar

[![CI](https://github.com/DataCore-VietNam/vn-market-calendar/actions/workflows/ci.yml/badge.svg)](https://github.com/DataCore-VietNam/vn-market-calendar/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/vn-market-calendar.svg)](https://pypi.org/project/vn-market-calendar/)
[![Python 3.10+](https://img.shields.io/pypi/pyversions/vn-market-calendar.svg)](https://pypi.org/project/vn-market-calendar/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](https://github.com/DataCore-VietNam/vn-market-calendar/actions)

Trading calendar for Vietnamese stock exchanges — **HOSE, HNX, UPCOM**.
Holidays, session schedules, tick sizes, T+2 settlement, and real-time
market-state helpers. Data 2000-2040, auto-updated annually.

## Install

```
pip install vn-market-calendar              # core
pip install "vn-market-calendar[pandas]"   # + pandas helpers
```

## Quick start

```python
from vn_market_calendar import HOSE

cal = HOSE()
cal.is_trading_day("2024-04-30")           # False (Reunification Day)
cal.next_trading_day("2024-04-26")         # date(2024, 5, 2)
cal.count_trading_days("2024-01-01", "2024-12-31")  # 250

for s in cal.sessions("2024-05-02"):
    print(s.name, s.start, s.end)
    # pre_open_ato         09:00:00 09:15:00
    # continuous_morning   09:15:00 11:30:00
    # lunch_break          11:30:00 13:00:00
    # continuous_afternoon 13:00:00 14:30:00
    # atc                  14:30:00 14:45:00
    # put_through          14:45:00 15:00:00

    cal.tick_size(price=15_000)                # 50 VND
    cal.lot_size("ACB")                        # 100
    ```

    ## Financial analysis

    ```python
    from vn_market_calendar import HOSE, VN_TZ
    import datetime

    cal = HOSE()

    # Real-time market state
    cal.is_open()                  # True/False right now (Vietnam time)
    cal.current_session()          # Session("continuous_morning", ...) or None
    cal.next_session_open()        # datetime of next session open, tz-aware

    # T+2 settlement
    cal.settlement_day("2024-05-02")           # date(2024, 5, 6)
    cal.settlement_day("2024-04-26", lag=2)    # date(2024, 5, 3)

    # Trading minutes per day
    cal.trading_minutes("2024-05-02")          # 270 (excl. lunch)
    ```

    ## pandas helpers

    ```python
    from vn_market_calendar.pandas_helpers import (
        trading_days, is_trading_day_series,
            next_trading_day_series, previous_trading_day_series,
                settlement_day_series,
                )

                idx    = trading_days("2024-01-01", "2024-12-31")
                settled = settlement_day_series(df["trade_date"], lag=2)
                ```

                ## CLI

                ```
                vn-market-calendar is-trading 2024-04-30
                vn-market-calendar next       2024-04-29 --exchange HNX
                vn-market-calendar count      2024-01-01 2024-12-31
                vn-market-calendar sessions   2024-05-02
                ```

                ## Supported exchanges

                | Exchange | Open date  | Tick size          |
                |----------|------------|--------------------|
                | HOSE     | 2000-07-28 | 10 / 50 / 100 VND  |
                | HNX      | 2005-03-14 | 100 VND flat       |
                | UPCOM    | 2009-06-24 | 100 VND flat       |

                ## Development

                ```
                make dev      # editable install
                make check    # lint + typecheck + tests
                ```

                **First-time repo setup:** `gh workflow run repo-setup.yml` — sets GitHub topics and homepage.

                **PyPI trusted publishing** (one-time, no stored secrets):
                1. PyPI -> Manage -> Settings -> Publishing -> Add trusted publisher
                2. Workflow: `publish.yml`, Environment: `pypi`

                ## License

                MIT (c) DataCore Vietnam
                