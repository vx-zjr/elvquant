"""Manual-confirmation dry-run order workflow."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from qts.contracts import Order, RiskDecision
from qts.controls import KillSwitch


@dataclass(frozen=True)
class ManualConfirmation:
    """Human approval record required before a dry-run manual submit."""

    confirmed_by: str
    confirmed_at: datetime
    decision: str
    notes: str


@dataclass(frozen=True)
class OrderRecommendation:
    """Traceable order recommendation generated before manual review."""

    order_id: str
    order: Order
    source_strategy: str
    signal: Mapping[str, float]
    target_weights: Mapping[str, float]
    risk_decision: RiskDecision


@dataclass
class ManualOrderWorkflow:
    """Record confirmed manual orders locally without broker submission."""

    output_dir: Path
    kill_switch: KillSwitch = field(
        default_factory=lambda: KillSwitch(enabled=False, reason="manual workflow active")
    )
    dry_run: bool = True

    def __post_init__(self) -> None:
        if not self.dry_run:
            raise ValueError("real broker submission is disabled")

    def submit(
        self,
        recommendation: OrderRecommendation,
        confirmation: ManualConfirmation | None,
    ) -> Path:
        """Append a traceable dry-run order record after mandatory controls."""

        self.kill_switch.assert_can_continue()
        if not recommendation.risk_decision.allowed:
            reasons = ", ".join(recommendation.risk_decision.reasons) or "unspecified"
            raise PermissionError(f"risk rejected manual order: {reasons}")
        if confirmation is None:
            raise PermissionError("manual confirmation is required")
        if confirmation.decision != "approved":
            raise PermissionError(f"manual confirmation not approved: {confirmation.decision}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / "manual_orders.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(_payload(recommendation, confirmation), sort_keys=True) + "\n")
        return path


def _payload(
    recommendation: OrderRecommendation,
    confirmation: ManualConfirmation,
) -> dict[str, object]:
    order = recommendation.order
    return {
        "order_id": recommendation.order_id,
        "order_as_of": order.as_of.isoformat(),
        "asset_id": order.asset_id,
        "quantity": order.quantity,
        "order_reason": order.reason,
        "source_strategy": recommendation.source_strategy,
        "signal": dict(recommendation.signal),
        "target_weights": dict(recommendation.target_weights),
        "risk_allowed": recommendation.risk_decision.allowed,
        "risk_reasons": list(recommendation.risk_decision.reasons),
        "risk_as_of": recommendation.risk_decision.as_of.isoformat(),
        "confirmed_by": confirmation.confirmed_by,
        "confirmed_at": confirmation.confirmed_at.isoformat(),
        "confirmation_decision": confirmation.decision,
        "confirmation_notes": confirmation.notes,
        "dry_run": True,
        "broker_submission": "disabled",
    }


__all__ = [
    "ManualConfirmation",
    "ManualOrderWorkflow",
    "OrderRecommendation",
]
