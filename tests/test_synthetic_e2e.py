from __future__ import annotations

import subprocess
import sys
from datetime import UTC, datetime, timedelta

from qts.contracts import DataSnapshot, Order, TargetPortfolio


def test_synthetic_end_to_end_backtest_outputs_required_metrics() -> None:
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

    start = datetime(2026, 1, 1, tzinfo=UTC)
    data_source = SyntheticDataSource(
        asset_ids=("AAA", "BBB", "CCC"),
        start=start,
        periods=6,
    )
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

    result = backtester.run(
        start=start,
        end=start + timedelta(days=5),
        config={"seed": "deterministic"},
    )
    report = SimpleReporter().build(result)

    assert result.run_id == "synthetic-20260101-20260106"
    assert result.config_summary["data_source"] == "synthetic"
    assert set(result.metrics) >= {"net_value", "total_return", "max_drawdown", "turnover"}
    assert result.metrics["net_value"] > 0.0
    assert len(result.equity_curve) == 6
    assert "net_value" in report.text
    assert "total_return" in report.text
    assert "max_drawdown" in report.text
    assert "turnover" in report.text


def test_basic_risk_manager_rejects_short_and_overallocated_targets() -> None:
    from qts.simple import BasicRiskManager

    as_of = datetime(2026, 1, 1, tzinfo=UTC)
    snapshot = DataSnapshot(
        as_of=as_of,
        asset_ids=("AAA", "BBB"),
        prices={"AAA": 100.0, "BBB": 50.0},
        data_version="synthetic",
    )
    orders = (Order(as_of=as_of, asset_id="AAA", quantity=1.0, reason="test"),)

    short_decision = BasicRiskManager().evaluate(
        snapshot=snapshot,
        target=TargetPortfolio(as_of=as_of, weights={"AAA": -0.1, "BBB": 0.5}),
        orders=orders,
    )
    overallocated_decision = BasicRiskManager().evaluate(
        snapshot=snapshot,
        target=TargetPortfolio(as_of=as_of, weights={"AAA": 0.7, "BBB": 0.4}),
        orders=orders,
    )

    assert short_decision.allowed is False
    assert "short" in " ".join(short_decision.reasons)
    assert overallocated_decision.allowed is False
    assert "100%" in " ".join(overallocated_decision.reasons)


def test_run_py_prints_required_metrics() -> None:
    completed = subprocess.run(
        [sys.executable, "run.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "net_value" in completed.stdout
    assert "total_return" in completed.stdout
    assert "max_drawdown" in completed.stdout
    assert "turnover" in completed.stdout
