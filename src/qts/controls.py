"""Non-broker readiness controls."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from qts.contracts import Order


@dataclass(frozen=True)
class KillSwitch:
    """Local kill switch for stopping trading workflows."""

    enabled: bool
    reason: str

    def assert_can_continue(self) -> None:
        if self.enabled:
            raise RuntimeError(f"kill switch enabled: {self.reason}")


@dataclass(frozen=True)
class OrderAmountLimit:
    """Maximum absolute notional for a single order."""

    max_notional: float

    def __post_init__(self) -> None:
        if self.max_notional <= 0.0:
            raise ValueError("max_notional must be positive")

    def validate(self, order: Order, price: float) -> None:
        notional = abs(order.quantity * price)
        if notional > self.max_notional:
            raise ValueError(f"order notional {notional:.2f} exceeds limit {self.max_notional:.2f}")


@dataclass(frozen=True)
class ConfirmationRecord:
    """Local human confirmation record for simulated/manual review."""

    order_id: str
    confirmed_by: str
    confirmed_at: datetime
    decision: str
    notes: str


def write_confirmation_record(output_dir: Path, record: ConfirmationRecord) -> Path:
    """Append a local confirmation record without broker submission."""

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "confirmations.jsonl"
    payload = {
        "order_id": record.order_id,
        "confirmed_by": record.confirmed_by,
        "confirmed_at": record.confirmed_at.isoformat(),
        "decision": record.decision,
        "notes": record.notes,
        "broker_submission": "disabled",
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
    return path


__all__ = [
    "ConfirmationRecord",
    "KillSwitch",
    "OrderAmountLimit",
    "write_confirmation_record",
]
