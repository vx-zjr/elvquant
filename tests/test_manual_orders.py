from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from qts.contracts import Order, RiskDecision


def test_manual_order_submit_requires_confirmation(tmp_path):
    from qts.manual import ManualOrderWorkflow

    workflow = ManualOrderWorkflow(output_dir=tmp_path)

    with pytest.raises(PermissionError, match="confirmation"):
        workflow.submit(_recommendation(), confirmation=None)


def test_risk_rejection_prevents_manual_submit(tmp_path):
    from qts.manual import ManualOrderWorkflow

    rejected = _recommendation(
        risk_decision=RiskDecision(
            as_of=_AS_OF,
            allowed=False,
            reasons=("risk rejected",),
        )
    )

    with pytest.raises(PermissionError, match="risk"):
        ManualOrderWorkflow(output_dir=tmp_path).submit(rejected, _confirmation())


def test_kill_switch_prevents_manual_submit(tmp_path):
    from qts.controls import KillSwitch
    from qts.manual import ManualOrderWorkflow

    workflow = ManualOrderWorkflow(
        output_dir=tmp_path,
        kill_switch=KillSwitch(enabled=True, reason="operator stop"),
    )

    with pytest.raises(RuntimeError, match="kill switch"):
        workflow.submit(_recommendation(), _confirmation())


def test_confirmed_dry_run_records_traceability(tmp_path):
    from qts.manual import ManualOrderWorkflow

    record_path = ManualOrderWorkflow(output_dir=tmp_path).submit(
        _recommendation(),
        _confirmation(),
    )
    payload = json.loads(record_path.read_text(encoding="utf-8").splitlines()[0])

    assert payload["dry_run"] is True
    assert payload["broker_submission"] == "disabled"
    assert payload["source_strategy"] == "unit-strategy"
    assert payload["signal"] == {"AAA": 1.0}
    assert payload["target_weights"] == {"AAA": 0.1}
    assert payload["risk_allowed"] is True
    assert payload["confirmed_by"] == "researcher"


_AS_OF = datetime(2026, 1, 1, tzinfo=UTC)


def _recommendation(risk_decision: RiskDecision | None = None):
    from qts.manual import OrderRecommendation

    return OrderRecommendation(
        order_id="manual-1",
        order=Order(as_of=_AS_OF, asset_id="AAA", quantity=1.0, reason="unit"),
        source_strategy="unit-strategy",
        signal={"AAA": 1.0},
        target_weights={"AAA": 0.1},
        risk_decision=risk_decision
        or RiskDecision(as_of=_AS_OF, allowed=True, reasons=()),
    )


def _confirmation():
    from qts.manual import ManualConfirmation

    return ManualConfirmation(
        confirmed_by="researcher",
        confirmed_at=_AS_OF,
        decision="approved",
        notes="dry run only",
    )
