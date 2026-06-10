from __future__ import annotations

from datetime import UTC, datetime


def test_position_value_uses_visible_prices_for_held_assets() -> None:
    from qts.portfolio_math import position_value

    assert position_value({"AAA": 2.0, "BBB": -1.0}, {"AAA": 10.0, "BBB": 3.0}) == 17.0


def test_position_value_rejects_missing_held_asset_price() -> None:
    import pytest

    from qts.portfolio_math import position_value

    with pytest.raises(ValueError, match="missing price for held asset BBB"):
        position_value({"BBB": 1.0}, {"AAA": 10.0})


def test_orders_for_target_generates_rebalance_orders() -> None:
    from qts.contracts import LedgerState, TargetPortfolio
    from qts.portfolio_math import orders_for_target

    as_of = datetime(2026, 1, 1, tzinfo=UTC)
    state = LedgerState(
        as_of=as_of,
        cash=100.0,
        positions={"AAA": 2.0},
        equity=200.0,
        cumulative_cost=0.0,
    )
    target = TargetPortfolio(as_of=as_of, weights={"AAA": 0.5, "BBB": 0.5})

    orders = orders_for_target(
        state=state,
        equity=200.0,
        asset_ids=("AAA", "BBB"),
        prices={"AAA": 25.0, "BBB": 10.0},
        target=target,
    )

    assert [(order.asset_id, order.quantity, order.reason) for order in orders] == [
        ("AAA", 2.0, "rebalance_to_target"),
        ("BBB", 10.0, "rebalance_to_target"),
    ]
