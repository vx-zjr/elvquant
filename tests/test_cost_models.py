from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import pytest

from qts.contracts import DataSnapshot
from qts.simple import (
    BasicRiskManager,
    EqualWeightSignal,
    SimpleAccountingLedger,
    SimpleBacktester,
    SimpleExecutionSimulator,
    SimplePortfolioConstructor,
    SimpleReporter,
)


@dataclass(frozen=True)
class FlatCostDataSource:
    asset_ids: tuple[str, ...]
    start: datetime
    periods: int
    price: float = 100.0

    def snapshot(self, decision_time: datetime) -> DataSnapshot:
        offset = (decision_time - self.start).days
        if offset < 0 or offset >= self.periods:
            raise ValueError(f"missing flat cost data for {decision_time.isoformat()}")
        return DataSnapshot(
            as_of=decision_time,
            asset_ids=self.asset_ids,
            prices={asset_id: self.price for asset_id in self.asset_ids},
            data_version="flat-cost",
        )


def test_cost_model_contract_imports() -> None:
    from qts.contracts import CostModel

    assert CostModel.__name__ == "CostModel"


def test_explicit_cost_models_feed_execution_and_report_metrics() -> None:
    from qts.costs import (
        CompositeCostModel,
        FixedCommissionCostModel,
        ProportionalCommissionCostModel,
        SlippageCostModel,
    )

    result = _run_flat_cost_backtest(
        execution_simulator=SimpleExecutionSimulator(
            cost_model=CompositeCostModel(
                models=(
                    FixedCommissionCostModel(amount_per_order=1.0),
                    ProportionalCommissionCostModel(rate=0.001),
                    SlippageCostModel(rate=0.002),
                )
            )
        )
    )
    report = SimpleReporter().build(result)

    assert result.metrics["total_cost"] > 0.0
    assert result.metrics["cost_to_return"] >= 0.0
    assert "total_cost" in report.text
    assert "cost_to_return" in report.text


def test_cost_enabled_result_differs_and_does_not_improve_return() -> None:
    from qts.costs import CompositeCostModel, ProportionalCommissionCostModel

    no_cost = _run_flat_cost_backtest(execution_simulator=SimpleExecutionSimulator())
    with_cost = _run_flat_cost_backtest(
        execution_simulator=SimpleExecutionSimulator(
            cost_model=CompositeCostModel(
                models=(ProportionalCommissionCostModel(rate=0.001),)
            )
        )
    )

    assert with_cost.metrics["total_cost"] > no_cost.metrics["total_cost"]
    assert with_cost.metrics["net_value"] != no_cost.metrics["net_value"]
    assert with_cost.metrics["total_return"] <= no_cost.metrics["total_return"]


@pytest.mark.parametrize(
    ("factory", "kwargs"),
    [
        ("FixedCommissionCostModel", {"amount_per_order": -0.01}),
        ("ProportionalCommissionCostModel", {"rate": -0.01}),
        ("SlippageCostModel", {"rate": -0.01}),
    ],
)
def test_cost_models_reject_negative_parameters(factory: str, kwargs: dict[str, float]) -> None:
    import qts.costs as costs

    with pytest.raises(ValueError, match="negative"):
        getattr(costs, factory)(**kwargs)


def _run_flat_cost_backtest(execution_simulator: SimpleExecutionSimulator):
    start = datetime(2026, 1, 1, tzinfo=UTC)
    data_source = FlatCostDataSource(asset_ids=("AAA", "BBB"), start=start, periods=4)
    backtester = SimpleBacktester(
        data_source=data_source,
        signal_model=EqualWeightSignal(),
        portfolio_constructor=SimplePortfolioConstructor(),
        risk_manager=BasicRiskManager(),
        execution_simulator=execution_simulator,
        ledger=SimpleAccountingLedger(),
        decision_times=tuple(start + timedelta(days=offset) for offset in range(3)),
        initial_cash=10_000.0,
    )
    return backtester.run(start=start, end=start + timedelta(days=3), config={"seed": "cost"})
