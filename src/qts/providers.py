"""Provider boundary helpers for enforcing data visibility policy."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from math import isfinite

from qts.contracts import DataSnapshot, DataSource


@dataclass(frozen=True)
class DataVisibilityPolicy:
    """Validate that provider snapshots are visible at a decision time."""

    require_exact_decision_time: bool = True

    def validate(self, snapshot: DataSnapshot, decision_time: datetime) -> DataSnapshot:
        """Reject future, incomplete, or unversioned provider snapshots."""

        if decision_time.tzinfo is None:
            raise ValueError("decision_time must be timezone-aware")
        if snapshot.as_of.tzinfo is None:
            raise ValueError("snapshot.as_of must be timezone-aware")
        if self.require_exact_decision_time and snapshot.as_of != decision_time:
            raise ValueError("snapshot time must equal the requested decision time")
        if not self.require_exact_decision_time and snapshot.as_of > decision_time:
            raise ValueError("snapshot time must not be after the decision time")
        if not snapshot.data_version:
            raise ValueError("snapshot data_version must not be empty")

        missing_prices = [
            asset_id for asset_id in snapshot.asset_ids if asset_id not in snapshot.prices
        ]
        if missing_prices:
            raise ValueError(f"snapshot missing prices for: {', '.join(missing_prices)}")

        for asset_id in snapshot.asset_ids:
            price = snapshot.prices[asset_id]
            if not isfinite(price) or price <= 0.0:
                raise ValueError(f"snapshot price for {asset_id} must be finite and positive")

        unexpected_feature_assets = set(snapshot.features).difference(snapshot.asset_ids)
        if unexpected_feature_assets:
            raise ValueError(
                "snapshot features include assets outside asset_ids: "
                f"{', '.join(sorted(unexpected_feature_assets))}"
            )
        return snapshot


@dataclass(frozen=True)
class ValidatedDataSource:
    """Wrap a data source and enforce visibility policy at the provider edge."""

    data_source: DataSource
    policy: DataVisibilityPolicy = field(default_factory=DataVisibilityPolicy)

    def snapshot(self, decision_time: datetime) -> DataSnapshot:
        return self.policy.validate(self.data_source.snapshot(decision_time), decision_time)


__all__ = ["DataVisibilityPolicy", "ValidatedDataSource"]
