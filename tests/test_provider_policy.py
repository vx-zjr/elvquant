from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import pytest

from qts.contracts import DataSnapshot


def test_validated_data_source_rejects_future_snapshot() -> None:
    from qts.providers import ValidatedDataSource

    decision_time = datetime(2026, 1, 1, tzinfo=UTC)
    source = _FixedSnapshotSource(
        DataSnapshot(
            as_of=decision_time + timedelta(days=1),
            asset_ids=("AAA",),
            prices={"AAA": 100.0},
            data_version="unit",
        )
    )

    with pytest.raises(ValueError, match="snapshot time"):
        ValidatedDataSource(source).snapshot(decision_time)


def test_validated_data_source_accepts_visible_versioned_snapshot() -> None:
    from qts.providers import ValidatedDataSource

    decision_time = datetime(2026, 1, 1, tzinfo=UTC)
    snapshot = DataSnapshot(
        as_of=decision_time,
        asset_ids=("AAA",),
        prices={"AAA": 100.0},
        data_version="unit",
    )

    assert ValidatedDataSource(_FixedSnapshotSource(snapshot)).snapshot(decision_time) == snapshot


@dataclass(frozen=True)
class _FixedSnapshotSource:
    snapshot_value: DataSnapshot

    def snapshot(self, decision_time: datetime) -> DataSnapshot:
        return self.snapshot_value
