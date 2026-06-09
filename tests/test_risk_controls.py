from __future__ import annotations

from datetime import UTC, datetime, timedelta
from math import nan

from qts.contracts import DataSnapshot, LedgerState, Order, TargetPortfolio
from qts.simple import (
    BasicRiskManager,
    EqualWeightSignal,
    SimpleAccountingLedger,
    SimpleBacktester,
    SimpleExecutionSimulator,
    SimplePortfolioConstructor,
    SimpleReporter,
    SyntheticDataSource,
)


def test_risk_rejects_single_asset_weight_above_twenty_percent() -> None:
    decision = _strict_risk().evaluate(
        snapshot=_snapshot({"AAA": 100.0}),
        target=TargetPortfolio(as_of=_AS_OF, weights={"AAA": 0.21}),
        orders=(),
    )

    assert decision.allowed is False
    assert "single asset" in " ".join(decision.reasons)


def test_risk_rejects_total_exposure_above_ninety_five_percent() -> None:
    decision = _strict_risk().evaluate(
        snapshot=_snapshot({"AAA": 100.0, "BBB": 100.0, "CCC": 100.0}),
        target=TargetPortfolio(
            as_of=_AS_OF,
            weights={"AAA": 0.2, "BBB": 0.2, "CCC": 0.6},
        ),
        orders=(),
    )

    assert decision.allowed is False
    assert "total exposure" in " ".join(decision.reasons)


def test_risk_rejects_daily_turnover_above_fifty_percent() -> None:
    decision = _strict_risk().evaluate(
        snapshot=_snapshot({"AAA": 100.0}),
        target=TargetPortfolio(as_of=_AS_OF, weights={"AAA": 0.2}),
        orders=(Order(as_of=_AS_OF, asset_id="AAA", quantity=60.0, reason="unit"),),
        portfolio_state=LedgerState(
            as_of=_AS_OF,
            cash=10_000.0,
            positions={},
            equity=10_000.0,
            cumulative_cost=0.0,
        ),
    )

    assert decision.allowed is False
    assert "turnover" in " ".join(decision.reasons)


def test_risk_stops_new_buys_after_daily_loss_threshold() -> None:
    decision = _strict_risk().evaluate(
        snapshot=_snapshot({"AAA": 80.0}),
        target=TargetPortfolio(as_of=_AS_OF, weights={"AAA": 0.2}),
        orders=(Order(as_of=_AS_OF, asset_id="AAA", quantity=1.0, reason="unit"),),
        portfolio_state=LedgerState(
            as_of=_AS_OF - timedelta(days=1),
            cash=0.0,
            positions={"AAA": 100.0},
            equity=10_000.0,
            cumulative_cost=0.0,
        ),
    )

    assert decision.allowed is False
    assert "daily loss" in " ".join(decision.reasons)


def test_risk_rejects_missing_or_abnormal_prices() -> None:
    missing_decision = _strict_risk().evaluate(
        snapshot=_snapshot({}),
        target=TargetPortfolio(as_of=_AS_OF, weights={"AAA": 0.1}),
        orders=(Order(as_of=_AS_OF, asset_id="AAA", quantity=1.0, reason="unit"),),
    )
    abnormal_decision = _strict_risk().evaluate(
        snapshot=_snapshot({"AAA": nan}),
        target=TargetPortfolio(as_of=_AS_OF, weights={"AAA": 0.1}),
        orders=(Order(as_of=_AS_OF, asset_id="AAA", quantity=1.0, reason="unit"),),
    )

    assert missing_decision.allowed is False
    assert "missing price" in " ".join(missing_decision.reasons)
    assert abnormal_decision.allowed is False
    assert "abnormal price" in " ".join(abnormal_decision.reasons)


def test_backtest_report_includes_risk_rejection_counts_and_reasons() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    data_source = SyntheticDataSource(asset_ids=("AAA", "BBB", "CCC"), start=start, periods=4)
    backtester = SimpleBacktester(
        data_source=data_source,
        signal_model=EqualWeightSignal(),
        portfolio_constructor=SimplePortfolioConstructor(),
        risk_manager=_strict_risk(),
        execution_simulator=SimpleExecutionSimulator(),
        ledger=SimpleAccountingLedger(),
        decision_times=tuple(start + timedelta(days=offset) for offset in range(3)),
        initial_cash=10_000.0,
    )

    result = backtester.run(start=start, end=start + timedelta(days=3), config={"seed": "risk"})
    report = SimpleReporter().build(result)

    assert result.metrics["risk_rejections"] > 0.0
    assert "risk_rejections" in report.text
    assert "single_asset" in report.text


_AS_OF = datetime(2026, 1, 2, tzinfo=UTC)


def _strict_risk() -> BasicRiskManager:
    return BasicRiskManager(
        max_asset_weight=0.2,
        max_gross_exposure=0.95,
        max_daily_turnover=0.5,
        daily_loss_limit=0.05,
    )


def _snapshot(prices: dict[str, float]) -> DataSnapshot:
    return DataSnapshot(
        as_of=_AS_OF,
        asset_ids=tuple(prices),
        prices=prices,
        data_version="unit",
    )
