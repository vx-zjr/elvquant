"""Explicit execution cost models."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from qts.contracts import CostModel, Order


@dataclass(frozen=True)
class FixedCommissionCostModel:
    """Charge a fixed amount for each non-zero order."""

    amount_per_order: float

    def __post_init__(self) -> None:
        _reject_negative(self.amount_per_order, "amount_per_order")

    def estimate(self, order: Order, price: float) -> float:
        if order.quantity == 0.0:
            return 0.0
        return self.amount_per_order


@dataclass(frozen=True)
class ProportionalCommissionCostModel:
    """Charge a percentage of traded notional."""

    rate: float

    def __post_init__(self) -> None:
        _reject_negative(self.rate, "rate")

    def estimate(self, order: Order, price: float) -> float:
        return abs(order.quantity * price) * self.rate


@dataclass(frozen=True)
class SlippageCostModel:
    """Represent slippage as a percentage cost on traded notional."""

    rate: float

    def __post_init__(self) -> None:
        _reject_negative(self.rate, "rate")

    def estimate(self, order: Order, price: float) -> float:
        return abs(order.quantity * price) * self.rate


@dataclass(frozen=True)
class CompositeCostModel:
    """Sum several non-negative cost models."""

    models: Sequence[CostModel]

    def estimate(self, order: Order, price: float) -> float:
        total = sum(model.estimate(order, price) for model in self.models)
        if total < 0.0:
            raise ValueError("composite cost must not be negative")
        return total


def _reject_negative(value: float, name: str) -> None:
    if value < 0.0:
        raise ValueError(f"{name} must not be negative")


__all__ = [
    "CompositeCostModel",
    "FixedCommissionCostModel",
    "ProportionalCommissionCostModel",
    "SlippageCostModel",
]
