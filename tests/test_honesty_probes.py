from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from math import isclose

import pytest

from qts.contracts import DataSnapshot, Fill, LedgerState, Order, SignalSet, TargetPortfolio
from qts.simple import (
    BasicRiskManager,
    EqualWeightSignal,
    SimpleAccountingLedger,
    SimpleBacktester,
    SimpleExecutionSimulator,
    SimplePortfolioConstructor,
)


@dataclass(frozen=True)
class FlatDataSource:
    asset_ids: tuple[str, ...]
    start: datetime
    periods: int
    price: float = 100.0

    def snapshot(self, decision_time: datetime) -> DataSnapshot:
        offset = (decision_time - self.start).days
        if offset < 0 or offset >= self.periods:
            raise ValueError(f"no flat data for {decision_time.isoformat()}")
        return DataSnapshot(
            as_of=decision_time,
            asset_ids=self.asset_ids,
            prices={asset_id: self.price for asset_id in self.asset_ids},
            data_version="flat-synthetic",
            features={asset_id: {} for asset_id in self.asset_ids},
        )


class FuturePriceCheater:
    def generate(self, snapshot: DataSnapshot) -> SignalSet:
        future_price = snapshot.features["AAA"]["future_price"]
        return SignalSet(
            as_of=snapshot.as_of,
            scores={"AAA": future_price},
            model_name="future_price_cheater",
        )


def test_equal_weight_flat_prices_after_costs_does_not_get_rich_from_nowhere() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    data_source = FlatDataSource(asset_ids=("AAA", "BBB"), start=start, periods=4)
    backtester = SimpleBacktester(
        data_source=data_source,
        signal_model=EqualWeightSignal(),
        portfolio_constructor=SimplePortfolioConstructor(),
        risk_manager=BasicRiskManager(),
        execution_simulator=SimpleExecutionSimulator(cost_rate=0.001),
        ledger=SimpleAccountingLedger(),
        decision_times=tuple(start + timedelta(days=offset) for offset in range(3)),
        initial_cash=10_000.0,
    )

    result = backtester.run(
        start=start,
        end=start + timedelta(days=3),
        config={"seed": "flat-cost"},
    )

    assert result.metrics["total_return"] <= 0.0
    assert result.equity_curve[-1].cumulative_cost > 0.0


def test_future_price_cheating_strategy_is_caught_by_absent_future_feature() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    data_source = FlatDataSource(asset_ids=("AAA",), start=start, periods=2)
    backtester = SimpleBacktester(
        data_source=data_source,
        signal_model=FuturePriceCheater(),
        portfolio_constructor=SimplePortfolioConstructor(),
        risk_manager=BasicRiskManager(),
        execution_simulator=SimpleExecutionSimulator(),
        ledger=SimpleAccountingLedger(),
        decision_times=(start,),
        initial_cash=10_000.0,
    )

    with pytest.raises(KeyError, match="future_price"):
        backtester.run(start=start, end=start + timedelta(days=1), config={})


def test_cash_plus_position_market_value_equals_total_equity() -> None:
    as_of = datetime(2026, 1, 2, tzinfo=UTC)
    snapshot = DataSnapshot(
        as_of=as_of,
        asset_ids=("AAA",),
        prices={"AAA": 110.0},
        data_version="unit",
    )
    order = Order(as_of=as_of, asset_id="AAA", quantity=10.0, reason="unit")
    fill = Fill(as_of=as_of, order=order, price=100.0, quantity=10.0, cost=1.0)
    state = SimpleAccountingLedger().apply_fills(
        previous_state=LedgerState(
            as_of=as_of,
            cash=1_000.0,
            positions={},
            equity=1_000.0,
            cumulative_cost=0.0,
        ),
        fills=(fill,),
        snapshot=snapshot,
    )

    position_value = state.positions["AAA"] * snapshot.prices["AAA"]
    assert isclose(state.cash + position_value, state.equity)


def test_costs_cannot_be_negative() -> None:
    as_of = datetime(2026, 1, 1, tzinfo=UTC)
    order = Order(as_of=as_of, asset_id="AAA", quantity=1.0, reason="unit")
    fill = Fill(as_of=as_of, order=order, price=100.0, quantity=1.0, cost=-0.01)

    with pytest.raises(ValueError, match="cost"):
        SimpleAccountingLedger().apply_fills(
            previous_state=LedgerState(
                as_of=as_of,
                cash=1_000.0,
                positions={},
                equity=1_000.0,
                cumulative_cost=0.0,
            ),
            fills=(fill,),
            snapshot=DataSnapshot(
                as_of=as_of,
                asset_ids=("AAA",),
                prices={"AAA": 100.0},
                data_version="unit",
            ),
        )


def test_positions_do_not_change_when_there_are_no_trades() -> None:
    as_of = datetime(2026, 1, 1, tzinfo=UTC)
    previous_state = LedgerState(
        as_of=as_of,
        cash=500.0,
        positions={"AAA": 5.0},
        equity=1_000.0,
        cumulative_cost=2.0,
    )
    next_state = SimpleAccountingLedger().apply_fills(
        previous_state=previous_state,
        fills=(),
        snapshot=DataSnapshot(
            as_of=as_of,
            asset_ids=("AAA",),
            prices={"AAA": 100.0},
            data_version="unit",
        ),
    )

    assert next_state.positions == previous_state.positions


def test_risk_rejects_targets_above_max_position() -> None:
    as_of = datetime(2026, 1, 1, tzinfo=UTC)
    decision = BasicRiskManager(max_gross_exposure=1.0).evaluate(
        snapshot=DataSnapshot(
            as_of=as_of,
            asset_ids=("AAA",),
            prices={"AAA": 100.0},
            data_version="unit",
        ),
        target=TargetPortfolio(as_of=as_of, weights={"AAA": 1.01}),
        orders=(),
    )

    assert decision.allowed is False
    assert "100%" in " ".join(decision.reasons)


def test_backtest_result_contains_run_id_and_config_summary() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    data_source = FlatDataSource(asset_ids=("AAA",), start=start, periods=2)
    result = SimpleBacktester(
        data_source=data_source,
        signal_model=EqualWeightSignal(),
        portfolio_constructor=SimplePortfolioConstructor(),
        risk_manager=BasicRiskManager(),
        execution_simulator=SimpleExecutionSimulator(),
        ledger=SimpleAccountingLedger(),
        decision_times=(start,),
        initial_cash=10_000.0,
    ).run(start=start, end=start + timedelta(days=1), config={"seed": "probe"})

    assert result.run_id
    assert result.config_summary["seed"] == "probe"
    assert result.config_summary["data_source"] == "synthetic"
