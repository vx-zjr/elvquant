"""Core contracts for the quantitative trading research pipeline."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

AssetId = str


@dataclass(frozen=True)
class DataSnapshot:
    """Data visible to the system at one decision time."""

    as_of: datetime
    asset_ids: tuple[AssetId, ...]
    prices: Mapping[AssetId, float]
    data_version: str
    features: Mapping[AssetId, Mapping[str, float]] = field(default_factory=dict)


@dataclass(frozen=True)
class SignalSet:
    """Research signals produced from a single data snapshot."""

    as_of: datetime
    scores: Mapping[AssetId, float]
    model_name: str
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class TargetPortfolio:
    """Target portfolio weights requested for a single decision time."""

    as_of: datetime
    weights: Mapping[AssetId, float]
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Order:
    """Simulated order intent derived from approved target positions."""

    as_of: datetime
    asset_id: AssetId
    quantity: float
    reason: str


@dataclass(frozen=True)
class RiskDecision:
    """Risk approval result for target positions and simulated orders."""

    as_of: datetime
    allowed: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class Fill:
    """Simulated execution fill for an approved order."""

    as_of: datetime
    order: Order
    price: float
    quantity: float
    cost: float


@dataclass(frozen=True)
class LedgerState:
    """Accounting state after applying visible fills and prices."""

    as_of: datetime
    cash: float
    positions: Mapping[AssetId, float]
    equity: float
    cumulative_cost: float


@dataclass(frozen=True)
class BacktestResult:
    """Backtest output with reproducibility metadata."""

    run_id: str
    config_summary: Mapping[str, str]
    equity_curve: Sequence[LedgerState]
    metrics: Mapping[str, float]


@dataclass(frozen=True)
class Report:
    """Human-readable and machine-readable result summary."""

    run_id: str
    text: str
    metrics: Mapping[str, float]


class DataSource(Protocol):
    """Return data visible at a decision time and never expose future data."""

    def snapshot(self, decision_time: datetime) -> DataSnapshot:
        """Return only values visible at the requested decision time."""
        ...


class SignalModel(Protocol):
    """Convert visible data at a decision time into signals without future data."""

    def generate(self, snapshot: DataSnapshot) -> SignalSet:
        """Generate signals using only values visible in the snapshot."""
        ...


class PortfolioConstructor(Protocol):
    """Convert signals visible at a decision time into targets without future data."""

    def construct(self, snapshot: DataSnapshot, signals: SignalSet) -> TargetPortfolio:
        """Create target weights from data and signals visible at the decision time."""
        ...


class RiskManager(Protocol):
    """Approve visible targets and orders at a decision time without future data."""

    def evaluate(
        self,
        snapshot: DataSnapshot,
        target: TargetPortfolio,
        orders: Sequence[Order],
    ) -> RiskDecision:
        """Evaluate only target, order, and market data visible at the decision time."""
        ...


class Backtester(Protocol):
    """Coordinate research over visible decision time snapshots without future data."""

    def run(self, start: datetime, end: datetime, config: Mapping[str, str]) -> BacktestResult:
        """Run a backtest over decision times using only data visible at each step."""
        ...


class ExecutionSimulator(Protocol):
    """Simulate visible approved orders at a decision time without future data."""

    def simulate(self, snapshot: DataSnapshot, orders: Sequence[Order]) -> Sequence[Fill]:
        """Return simulated fills from execution assumptions visible at the decision time."""
        ...


class CostModel(Protocol):
    """Estimate visible non-negative execution cost at a decision time without future data."""

    def estimate(self, order: Order, price: float) -> float:
        """Return the non-negative estimated cost for an order and visible execution price."""
        ...


class AccountingLedger(Protocol):
    """Record visible cash, positions, costs, and equity at a decision time without future data."""

    def apply_fills(
        self,
        previous_state: LedgerState,
        fills: Sequence[Fill],
        snapshot: DataSnapshot,
    ) -> LedgerState:
        """Apply visible fills and prices to produce the next ledger state."""
        ...


class Reporter(Protocol):
    """Build visible reports after a decision time run without adding future data."""

    def build(self, result: BacktestResult) -> Report:
        """Create report output from recorded results without adding future data."""
        ...


__all__ = [
    "AccountingLedger",
    "AssetId",
    "BacktestResult",
    "Backtester",
    "CostModel",
    "DataSnapshot",
    "DataSource",
    "ExecutionSimulator",
    "Fill",
    "LedgerState",
    "Order",
    "PortfolioConstructor",
    "Report",
    "Reporter",
    "RiskDecision",
    "RiskManager",
    "SignalModel",
    "SignalSet",
    "TargetPortfolio",
]
