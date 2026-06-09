import inspect
from datetime import UTC, datetime

import pytest


def test_core_contracts_import_and_dataclasses_construct() -> None:
    from qts.contracts import (
        BacktestResult,
        DataSnapshot,
        Fill,
        LedgerState,
        Order,
        Report,
        RiskDecision,
        SignalSet,
        TargetPortfolio,
    )

    decision_time = datetime(2026, 1, 2, tzinfo=UTC)
    snapshot = DataSnapshot(
        as_of=decision_time,
        asset_ids=("AAA",),
        prices={"AAA": 100.0},
        data_version="test-fixture",
    )
    signals = SignalSet(as_of=decision_time, scores={"AAA": 1.0}, model_name="test")
    target = TargetPortfolio(as_of=decision_time, weights={"AAA": 1.0})
    order = Order(as_of=decision_time, asset_id="AAA", quantity=10.0, reason="test")
    decision = RiskDecision(as_of=decision_time, allowed=True, reasons=())
    fill = Fill(
        as_of=decision_time,
        order=order,
        price=100.0,
        quantity=10.0,
        cost=0.0,
    )
    state = LedgerState(
        as_of=decision_time,
        cash=0.0,
        positions={"AAA": 10.0},
        equity=1000.0,
        cumulative_cost=0.0,
    )
    result = BacktestResult(
        run_id="run-test",
        config_summary={"seed": "1"},
        equity_curve=(state,),
        metrics={"total_return": 0.0},
    )
    report = Report(run_id="run-test", text="ok", metrics={"total_return": 0.0})

    assert snapshot.prices["AAA"] == 100.0
    assert signals.scores["AAA"] == 1.0
    assert target.weights["AAA"] == 1.0
    assert decision.allowed is True
    assert fill.order is order
    assert result.run_id == report.run_id


@pytest.mark.parametrize(
    "protocol_name",
    [
        "DataSource",
        "SignalModel",
        "PortfolioConstructor",
        "RiskManager",
        "Backtester",
        "ExecutionSimulator",
        "AccountingLedger",
        "Reporter",
    ],
)
def test_protocol_docstrings_explain_time_and_future_data(protocol_name: str) -> None:
    import qts.contracts as contracts

    protocol = getattr(contracts, protocol_name)
    text = inspect.getdoc(protocol)

    assert text is not None
    normalized = text.lower()
    assert "decision time" in normalized
    assert "future data" in normalized
    assert "visible" in normalized
