"""CLI smoke tests via the ``python -m vn_market_calendar`` entry point."""

from __future__ import annotations

import pytest

from vn_market_calendar.__main__ import main


def test_cli_is_trading_holiday(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["is-trading", "2024-04-30"])
    captured = capsys.readouterr()
    assert rc == 1
    assert captured.out.strip() == "no"


def test_cli_is_trading_normal_day(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["is-trading", "2024-05-02"])
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out.strip() == "yes"


def test_cli_next(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["next", "2024-04-29"])
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out.strip() == "2024-05-02"


def test_cli_count(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["count", "2024-01-01", "2024-12-31"])
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out.strip() == "250"


def test_cli_sessions_holiday_returns_nonzero(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["sessions", "2024-04-30"])
    assert rc == 1
    assert "not a trading day" in capsys.readouterr().out
