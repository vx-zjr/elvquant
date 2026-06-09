"""Minimal synthetic end-to-end implementations for Phase 2."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from qts.contracts import (
    AccountingLedger,
    AssetId,
    BacktestResult,
    DataSnapshot,
    DataSource,
    ExecutionSimulator,
    Fill,
    LedgerState,
    Order,
    PortfolioConstructor,
    Report,
    RiskDecision,
    RiskManager,
    SignalModel,
    SignalSet,
    TargetPortfolio,
)

_EPSILON = 1e-9


@dataclass(frozen=True)
class SyntheticDataSource:
    """Deterministic synthetic prices with no real market data."""

    asset_ids: tuple[AssetId, ...]
    start: datetime
    periods: int
    data_version: str = "synthetic-v1"
    _prices_by_time: Mapping[datetime, Mapping[AssetId, float]] = field(init=False)

    def __post_init__(self) -> None:
        if self.periods <= 0:
            raise ValueError("periods must be positive")
        if not self.asset_ids:
            raise ValueError("asset_ids must not be empty")

        prices_by_time: dict[datetime, dict[AssetId, float]] = {}
        for offset in range(self.periods):
            as_of = self.start + timedelta(days=offset)
            prices_by_time[as_of] = {
                asset_id: 100.0 + index * 10.0 + offset * (1.0 + index * 0.5)
                for index, asset_id in enumerate(self.asset_ids)
            }

        object.__setattr__(self, "_prices_by_time", prices_by_time)

    def snapshot(self, decision_time: datetime) -> DataSnapshot:
        prices = self._prices_by_time.get(decision_time)
        if prices is None:
            raise ValueError(f"no synthetic data for {decision_time.isoformat()}")

        return DataSnapshot(
            as_of=decision_time,
            asset_ids=self.asset_ids,
            prices=dict(prices),
            data_version=self.data_version,
        )


@dataclass(frozen=True)
class EqualWeightSignal:
    """Signal model that assigns the same score to every visible asset."""

    model_name: str = "equal_weight"

    def generate(self, snapshot: DataSnapshot) -> SignalSet:
        return SignalSet(
            as_of=snapshot.as_of,
            scores={asset_id: 1.0 for asset_id in snapshot.asset_ids},
            model_name=self.model_name,
        )


@dataclass(frozen=True)
class SimplePortfolioConstructor:
    """Convert visible scores into equal target weights."""

    def construct(self, snapshot: DataSnapshot, signals: SignalSet) -> TargetPortfolio:
        positive_assets = tuple(
            asset_id
            for asset_id in snapshot.asset_ids
            if signals.scores.get(asset_id, 0.0) > 0.0
        )
        if not positive_assets:
            return TargetPortfolio(as_of=snapshot.as_of, weights={})

        weight = 1.0 / len(positive_assets)
        return TargetPortfolio(
            as_of=snapshot.as_of,
            weights={asset_id: weight for asset_id in positive_assets},
        )


@dataclass(frozen=True)
class BasicRiskManager:
    """Risk manager that forbids short targets and gross exposure above 100%."""

    max_gross_exposure: float = 1.0

    def evaluate(
        self,
        snapshot: DataSnapshot,
        target: TargetPortfolio,
        orders: Sequence[Order],
    ) -> RiskDecision:
        reasons: list[str] = []
        if any(weight < -_EPSILON for weight in target.weights.values()):
            reasons.append("short target weights are not allowed")

        gross_exposure = sum(abs(weight) for weight in target.weights.values())
        if gross_exposure > self.max_gross_exposure + _EPSILON:
            reasons.append("target weights exceed 100% gross exposure")

        missing_prices = [
            order.asset_id for order in orders if order.asset_id not in snapshot.prices
        ]
        if missing_prices:
            reasons.append(f"missing prices for orders: {', '.join(sorted(missing_prices))}")

        return RiskDecision(
            as_of=snapshot.as_of,
            allowed=not reasons,
            reasons=tuple(reasons),
        )


@dataclass(frozen=True)
class SimpleExecutionSimulator:
    """Fill approved orders at the provided synthetic execution snapshot price."""

    cost_rate: float = 0.0

    def __post_init__(self) -> None:
        if self.cost_rate < 0.0:
            raise ValueError("cost_rate must not be negative")

    def simulate(self, snapshot: DataSnapshot, orders: Sequence[Order]) -> Sequence[Fill]:
        fills: list[Fill] = []
        for order in orders:
            if abs(order.quantity) <= _EPSILON:
                continue
            price = snapshot.prices.get(order.asset_id)
            if price is None:
                raise ValueError(f"missing execution price for {order.asset_id}")
            fills.append(
                Fill(
                    as_of=snapshot.as_of,
                    order=order,
                    price=price,
                    quantity=order.quantity,
                    cost=abs(price * order.quantity) * self.cost_rate,
                )
            )
        return tuple(fills)


@dataclass(frozen=True)
class SimpleAccountingLedger:
    """Apply fills and mark positions to visible synthetic prices."""

    def apply_fills(
        self,
        previous_state: LedgerState,
        fills: Sequence[Fill],
        snapshot: DataSnapshot,
    ) -> LedgerState:
        cash = previous_state.cash
        positions = dict(previous_state.positions)
        cumulative_cost = previous_state.cumulative_cost

        for fill in fills:
            if fill.cost < 0.0:
                raise ValueError("fill cost must not be negative")
            cash -= fill.price * fill.quantity + fill.cost
            positions[fill.order.asset_id] = positions.get(fill.order.asset_id, 0.0) + fill.quantity
            cumulative_cost += fill.cost

        positions = {
            asset_id: quantity
            for asset_id, quantity in positions.items()
            if abs(quantity) > _EPSILON
        }
        equity = cash + _position_value(positions, snapshot.prices)

        return LedgerState(
            as_of=snapshot.as_of,
            cash=cash,
            positions=positions,
            equity=equity,
            cumulative_cost=cumulative_cost,
        )


@dataclass(frozen=True)
class SimpleBacktester:
    """Coordinate the minimal synthetic research loop."""

    data_source: DataSource
    signal_model: SignalModel
    portfolio_constructor: PortfolioConstructor
    risk_manager: RiskManager
    execution_simulator: ExecutionSimulator
    ledger: AccountingLedger
    decision_times: Sequence[datetime]
    initial_cash: float
    execution_lag: timedelta = timedelta(days=1)

    def run(self, start: datetime, end: datetime, config: Mapping[str, str]) -> BacktestResult:
        if self.initial_cash <= 0.0:
            raise ValueError("initial_cash must be positive")

        state = LedgerState(
            as_of=start,
            cash=self.initial_cash,
            positions={},
            equity=self.initial_cash,
            cumulative_cost=0.0,
        )
        equity_curve: list[LedgerState] = [state]
        turnover_notional = 0.0

        for decision_time in self.decision_times:
            if decision_time < start or decision_time >= end:
                continue

            decision_snapshot = self.data_source.snapshot(decision_time)
            current_equity = self._mark_equity(state, decision_snapshot)
            signals = self.signal_model.generate(decision_snapshot)
            target = self.portfolio_constructor.construct(decision_snapshot, signals)
            orders = self._orders_for_target(state, current_equity, decision_snapshot, target)
            risk_decision = self.risk_manager.evaluate(decision_snapshot, target, orders)

            if not risk_decision.allowed:
                equity_curve.append(
                    LedgerState(
                        as_of=decision_snapshot.as_of,
                        cash=state.cash,
                        positions=state.positions,
                        equity=current_equity,
                        cumulative_cost=state.cumulative_cost,
                    )
                )
                continue

            execution_snapshot = self.data_source.snapshot(decision_time + self.execution_lag)
            fills = self.execution_simulator.simulate(execution_snapshot, orders)
            turnover_notional += sum(abs(fill.price * fill.quantity) for fill in fills)
            state = self.ledger.apply_fills(state, fills, execution_snapshot)
            equity_curve.append(state)

        metrics = _metrics(equity_curve, self.initial_cash, turnover_notional)
        config_summary = {
            **dict(config),
            "data_source": "synthetic",
            "initial_cash": f"{self.initial_cash:.2f}",
        }

        return BacktestResult(
            run_id=f"synthetic-{start:%Y%m%d}-{end:%Y%m%d}",
            config_summary=config_summary,
            equity_curve=tuple(equity_curve),
            metrics=metrics,
        )

    def _orders_for_target(
        self,
        state: LedgerState,
        equity: float,
        snapshot: DataSnapshot,
        target: TargetPortfolio,
    ) -> tuple[Order, ...]:
        orders: list[Order] = []
        asset_ids = tuple(dict.fromkeys((*snapshot.asset_ids, *state.positions.keys())))

        for asset_id in asset_ids:
            price = snapshot.prices.get(asset_id)
            if price is None:
                raise ValueError(f"missing decision price for {asset_id}")
            current_quantity = state.positions.get(asset_id, 0.0)
            target_value = target.weights.get(asset_id, 0.0) * equity
            current_value = current_quantity * price
            quantity = (target_value - current_value) / price
            if abs(quantity) > _EPSILON:
                orders.append(
                    Order(
                        as_of=snapshot.as_of,
                        asset_id=asset_id,
                        quantity=quantity,
                        reason="rebalance_to_target",
                    )
                )

        return tuple(orders)

    def _mark_equity(self, state: LedgerState, snapshot: DataSnapshot) -> float:
        return state.cash + _position_value(state.positions, snapshot.prices)


@dataclass(frozen=True)
class SimpleReporter:
    """Create a compact text report for the synthetic run."""

    def build(self, result: BacktestResult) -> Report:
        lines = [
            f"run_id: {result.run_id}",
            f"net_value: {result.metrics['net_value']:.6f}",
            f"total_return: {result.metrics['total_return']:.6f}",
            f"max_drawdown: {result.metrics['max_drawdown']:.6f}",
            f"turnover: {result.metrics['turnover']:.6f}",
        ]
        return Report(run_id=result.run_id, text="\n".join(lines), metrics=result.metrics)


def build_synthetic_demo() -> tuple[SimpleBacktester, datetime, datetime]:
    """Build the deterministic Phase 2 demo without real market data."""

    start = datetime(2026, 1, 1, tzinfo=UTC)
    end = start + timedelta(days=5)
    data_source = SyntheticDataSource(asset_ids=("AAA", "BBB", "CCC"), start=start, periods=6)
    backtester = SimpleBacktester(
        data_source=data_source,
        signal_model=EqualWeightSignal(),
        portfolio_constructor=SimplePortfolioConstructor(),
        risk_manager=BasicRiskManager(),
        execution_simulator=SimpleExecutionSimulator(),
        ledger=SimpleAccountingLedger(),
        decision_times=tuple(start + timedelta(days=offset) for offset in range(5)),
        initial_cash=10_000.0,
    )
    return backtester, start, end


def run_synthetic_demo() -> Report:
    """Run the deterministic synthetic demo and return a report."""

    backtester, start, end = build_synthetic_demo()
    result = backtester.run(start=start, end=end, config={"seed": "deterministic"})
    return SimpleReporter().build(result)


def _position_value(
    positions: Mapping[AssetId, float],
    prices: Mapping[AssetId, float],
) -> float:
    value = 0.0
    for asset_id, quantity in positions.items():
        price = prices.get(asset_id)
        if price is None:
            raise ValueError(f"missing price for held asset {asset_id}")
        value += quantity * price
    return value


def _metrics(
    equity_curve: Sequence[LedgerState],
    initial_cash: float,
    turnover_notional: float,
) -> Mapping[str, float]:
    ending_equity = equity_curve[-1].equity
    net_value = ending_equity / initial_cash
    total_return = net_value - 1.0
    max_drawdown = _max_drawdown(tuple(state.equity for state in equity_curve))
    turnover = turnover_notional / initial_cash
    return {
        "net_value": net_value,
        "total_return": total_return,
        "max_drawdown": max_drawdown,
        "turnover": turnover,
    }


def _max_drawdown(equity_values: Sequence[float]) -> float:
    peak = equity_values[0]
    max_drawdown = 0.0
    for equity in equity_values:
        peak = max(peak, equity)
        if peak > 0.0:
            max_drawdown = min(max_drawdown, equity / peak - 1.0)
    return max_drawdown


__all__ = [
    "BasicRiskManager",
    "EqualWeightSignal",
    "SimpleAccountingLedger",
    "SimpleBacktester",
    "SimpleExecutionSimulator",
    "SimplePortfolioConstructor",
    "SimpleReporter",
    "SyntheticDataSource",
    "build_synthetic_demo",
    "run_synthetic_demo",
]
