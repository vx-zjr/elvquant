from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from qts.contracts import Order


def test_readiness_can_pass_when_non_broker_controls_are_present(tmp_path):
    from qts.readiness import ReadinessControls, generate_readiness_report

    report = generate_readiness_report(
        output_dir=tmp_path,
        tests_passed=True,
        controls=ReadinessControls(
            kill_switch_design=True,
            order_amount_limits=True,
            abnormal_alerting=True,
            order_source_traceability=True,
            stop_and_recovery=True,
            human_confirmation=True,
            sufficient_paper_observation=True,
        ),
    )

    assert report.status == "ready"
    assert report.live_trading_allowed is True
    assert report.blockers == ()


def test_kill_switch_blocks_and_confirmation_records_are_local(tmp_path):
    from qts.controls import ConfirmationRecord, KillSwitch, write_confirmation_record

    with pytest.raises(RuntimeError, match="kill switch"):
        KillSwitch(enabled=True, reason="operator stop").assert_can_continue()

    path = write_confirmation_record(
        output_dir=tmp_path,
        record=ConfirmationRecord(
            order_id="paper-1",
            confirmed_by="researcher",
            confirmed_at=datetime(2026, 1, 1, tzinfo=UTC),
            decision="approved",
            notes="paper only",
        ),
    )

    payload = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    assert payload["order_id"] == "paper-1"
    assert payload["decision"] == "approved"
    assert payload["broker_submission"] == "disabled"


def test_order_amount_limit_blocks_large_orders() -> None:
    from qts.controls import OrderAmountLimit

    order = Order(
        as_of=datetime(2026, 1, 1, tzinfo=UTC),
        asset_id="AAA",
        quantity=101.0,
        reason="unit",
    )

    with pytest.raises(ValueError, match="order notional"):
        OrderAmountLimit(max_notional=10_000.0).validate(order, price=100.0)
