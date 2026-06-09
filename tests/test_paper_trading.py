from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import pytest

from qts.simple import (
    BasicRiskManager,
    EqualWeightSignal,
    SimpleAccountingLedger,
    SimpleExecutionSimulator,
    SimplePortfolioConstructor,
    SyntheticDataSource,
)


def test_paper_trading_runs_multiple_days_and_writes_local_orders_and_reports(tmp_path):
    from qts.paper import PaperTradingConfig, PaperTradingEngine

    start = datetime(2026, 1, 1, tzinfo=UTC)
    engine = PaperTradingEngine(
        data_source=SyntheticDataSource(asset_ids=("AAA", "BBB"), start=start, periods=4),
        signal_model=EqualWeightSignal(),
        portfolio_constructor=SimplePortfolioConstructor(),
        risk_manager=BasicRiskManager(),
        execution_simulator=SimpleExecutionSimulator(),
        ledger=SimpleAccountingLedger(),
        config=PaperTradingConfig(output_dir=tmp_path, initial_cash=10_000.0),
    )

    results = engine.run_days(tuple(start + timedelta(days=offset) for offset in range(3)))

    assert len(results) == 3
    assert (tmp_path / "orders.jsonl").is_file()
    assert all(result.daily_report_path.is_file() for result in results)
    order_lines = [
        json.loads(line)
        for line in (tmp_path / "orders.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert order_lines
    assert all(line["broker_submission"] == "disabled" for line in order_lines)
    assert "broker: disabled" in results[0].daily_report_path.read_text(encoding="utf-8")


def test_paper_trading_uses_risk_and_logs_rejections(tmp_path):
    from qts.paper import PaperTradingConfig, PaperTradingEngine

    start = datetime(2026, 1, 1, tzinfo=UTC)
    engine = PaperTradingEngine(
        data_source=SyntheticDataSource(asset_ids=("AAA", "BBB", "CCC"), start=start, periods=2),
        signal_model=EqualWeightSignal(),
        portfolio_constructor=SimplePortfolioConstructor(),
        risk_manager=BasicRiskManager(max_asset_weight=0.2, max_gross_exposure=0.95),
        execution_simulator=SimpleExecutionSimulator(),
        ledger=SimpleAccountingLedger(),
        config=PaperTradingConfig(output_dir=tmp_path, initial_cash=10_000.0),
    )

    result = engine.run_day(start)
    order_line = json.loads((tmp_path / "orders.jsonl").read_text(encoding="utf-8").splitlines()[0])

    assert result.risk_decision.allowed is False
    assert order_line["risk_allowed"] is False
    assert "risk_rejected" in result.daily_report_path.read_text(encoding="utf-8")


def test_paper_trading_failure_is_logged(tmp_path):
    from qts.paper import PaperTradingConfig, PaperTradingEngine

    start = datetime(2026, 1, 1, tzinfo=UTC)
    engine = PaperTradingEngine(
        data_source=SyntheticDataSource(asset_ids=("AAA",), start=start, periods=1),
        signal_model=EqualWeightSignal(),
        portfolio_constructor=SimplePortfolioConstructor(),
        risk_manager=BasicRiskManager(),
        execution_simulator=SimpleExecutionSimulator(),
        ledger=SimpleAccountingLedger(),
        config=PaperTradingConfig(output_dir=tmp_path, initial_cash=10_000.0),
    )

    with pytest.raises(ValueError, match="no synthetic data"):
        engine.run_day(start + timedelta(days=3))

    failures = (tmp_path / "failures.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(failures) == 1
    assert "failed" in json.loads(failures[0])["status"]


def test_synthetic_paper_demo_runner_returns_report_and_artifacts(tmp_path):
    from qts.paper import run_synthetic_paper_demo

    report = run_synthetic_paper_demo(output_dir=tmp_path)

    assert report.run_id == "paper-synthetic-20260101-20260105"
    assert report.metrics["ending_equity"] > 10_000.0
    assert report.metrics["total_orders"] == 10.0
    assert report.metrics["risk_rejections"] == 0.0
    assert (tmp_path / "orders.jsonl").is_file()
    assert (tmp_path / "daily_reports" / "2026-01-05.md").is_file()
    assert "broker_submission: disabled" in report.text
    assert "| 2026-01-05 |" in report.text
