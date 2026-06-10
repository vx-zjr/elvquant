from __future__ import annotations

from datetime import UTC, datetime
from threading import Thread

import pytest


def test_paper_engine_uses_shared_portfolio_math(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    import qts.paper as paper_module
    from qts.contracts import LedgerState, Order
    from qts.paper import PaperTradingConfig, PaperTradingEngine
    from qts.simple import (
        BasicRiskManager,
        EqualWeightSignal,
        SimpleAccountingLedger,
        SimpleExecutionSimulator,
        SimplePortfolioConstructor,
        SyntheticDataSource,
    )

    start = datetime(2026, 1, 1, tzinfo=UTC)

    def fake_orders_for_target(**kwargs):
        snapshot_time = kwargs["target"].as_of
        return (
            Order(
                as_of=snapshot_time,
                asset_id="AAA",
                quantity=1.0,
                reason="shared-helper-called",
            ),
        )

    monkeypatch.setattr(paper_module, "orders_for_target", fake_orders_for_target)
    engine = PaperTradingEngine(
        data_source=SyntheticDataSource(asset_ids=("AAA",), start=start, periods=2),
        signal_model=EqualWeightSignal(),
        portfolio_constructor=SimplePortfolioConstructor(),
        risk_manager=BasicRiskManager(),
        execution_simulator=SimpleExecutionSimulator(),
        ledger=SimpleAccountingLedger(),
        config=PaperTradingConfig(output_dir=tmp_path, initial_cash=1_000.0),
    )

    result = engine.run_day(start)

    assert result.orders[0].reason == "shared-helper-called"
    assert isinstance(result.state, LedgerState)


def test_shared_metrics_math_is_used_by_simple_and_rust_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import qts.rust_kernel as rust_kernel
    import qts.simple as simple

    calls = {"count": 0}

    def fake_max_drawdown(values):
        calls["count"] += 1
        assert tuple(values) == (100.0, 120.0, 90.0)
        return -0.123

    monkeypatch.setattr(simple, "max_drawdown", fake_max_drawdown)
    assert simple._max_drawdown((100.0, 120.0, 90.0)) == -0.123

    monkeypatch.setattr(rust_kernel, "_native_max_drawdown", None)
    monkeypatch.setattr(rust_kernel, "max_drawdown", fake_max_drawdown)
    assert rust_kernel.kernel_max_drawdown((100.0, 120.0, 90.0)) == -0.123
    assert calls["count"] == 2


def test_report_modules_share_time_utils() -> None:
    import qts.reporting as reporting
    import qts.reports as reports
    from qts.time_utils import to_iso

    assert reporting.to_iso is to_iso
    assert reports.to_iso is to_iso


def test_in_memory_run_store_is_thread_safe() -> None:
    from qts.api_app import InMemoryRunStore

    store = InMemoryRunStore()

    def worker(index: int) -> None:
        store.put(
            "owner-a",
            {
                "run_id": f"run-{index}",
                "workflow": "synthetic_demo",
                "status": "completed",
                "metrics": {"index": float(index)},
                "artifacts": [],
            },
        )
        assert store.get_for_owner("owner-a", f"run-{index}") is not None

    threads = [Thread(target=worker, args=(index,)) for index in range(40)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(store.list_for_owner("owner-a")) == 40


def test_execution_simulator_rejects_legacy_rate_plus_cost_model() -> None:
    from qts.costs import FixedCommissionCostModel
    from qts.simple import SimpleExecutionSimulator

    with pytest.raises(ValueError, match="cost_rate and cost_model"):
        SimpleExecutionSimulator(
            cost_rate=0.001,
            cost_model=FixedCommissionCostModel(amount_per_order=1.0),
        )


def test_structured_readiness_report_does_not_hardcode_tests_passed(tmp_path) -> None:
    from qts.reports import structured_readiness_report

    report = structured_readiness_report(core_root=tmp_path, tests_passed=None)

    assert report.metadata["tests_passed"] == "unknown"
    assert any("test status" in warning for warning in report.warnings)

    verified = structured_readiness_report(core_root=tmp_path, tests_passed=True)
    assert verified.metadata["tests_passed"] == "true"
