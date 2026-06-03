"""Tick-size band tests for each exchange."""

from __future__ import annotations

import pytest

from vn_market_calendar import HNX, HOSE, UPCOM


@pytest.fixture()
def hose() -> HOSE:
    return HOSE()


@pytest.mark.parametrize(
    "price,expected",
    [
        (1_000, 10),
        (9_990, 10),
        (9_999, 10),  # just below the 10k boundary
        (10_000, 50),  # boundary -> next band
        (15_000, 50),
        (49_950, 50),
        (49_999, 50),
        (50_000, 100),
        (123_500, 100),
        (1_000_000, 100),
    ],
)
def test_hose_tick_bands(hose: HOSE, price: float, expected: int) -> None:
    assert hose.tick_size(price) == expected


def test_hose_tick_size_zero(hose: HOSE) -> None:
    assert hose.tick_size(0) == 10


def test_hose_tick_size_negative_raises(hose: HOSE) -> None:
    with pytest.raises(ValueError):
        hose.tick_size(-1)


@pytest.mark.parametrize("price", [100, 9_999, 10_000, 50_000, 1_000_000])
def test_hnx_flat_tick(price: float) -> None:
    assert HNX().tick_size(price) == 100


@pytest.mark.parametrize("price", [100, 9_999, 10_000, 50_000, 1_000_000])
def test_upcom_flat_tick(price: float) -> None:
    assert UPCOM().tick_size(price) == 100


def test_lot_sizes() -> None:
    assert HOSE().lot_size() == 100
    assert HNX().lot_size("ACB") == 100
    assert UPCOM().lot_size() == 100
