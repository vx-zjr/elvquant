"""Pure portfolio math helpers shared by research and paper workflows."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from qts.contracts import AssetId, LedgerState, Order, TargetPortfolio

_EPSILON = 1e-9


def position_value(
    positions: Mapping[AssetId, float],
    prices: Mapping[AssetId, float],
) -> float:
    """Return marked position value using only supplied visible prices."""

    value = 0.0
    for asset_id, quantity in positions.items():
        price = prices.get(asset_id)
        if price is None:
            raise ValueError(f"missing price for held asset {asset_id}")
        value += quantity * price
    return value


def orders_for_target(
    state: LedgerState,
    equity: float,
    asset_ids: Sequence[AssetId],
    prices: Mapping[AssetId, float],
    target: TargetPortfolio,
) -> tuple[Order, ...]:
    """Create rebalance orders needed to move current positions to target weights."""

    orders: list[Order] = []
    ordered_asset_ids = tuple(dict.fromkeys((*asset_ids, *state.positions.keys())))

    for asset_id in ordered_asset_ids:
        price = prices.get(asset_id)
        if price is None:
            raise ValueError(f"missing decision price for {asset_id}")
        current_quantity = state.positions.get(asset_id, 0.0)
        target_value = target.weights.get(asset_id, 0.0) * equity
        current_value = current_quantity * price
        quantity = (target_value - current_value) / price
        if abs(quantity) > _EPSILON:
            orders.append(
                Order(
                    as_of=target.as_of,
                    asset_id=asset_id,
                    quantity=quantity,
                    reason="rebalance_to_target",
                )
            )

    return tuple(orders)


__all__ = ["orders_for_target", "position_value"]
