"""Research-only ML-style signal layer."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from qts.contracts import DataSnapshot, Report, SignalSet
from qts.simple import (
    BasicRiskManager,
    SimpleAccountingLedger,
    SimpleBacktester,
    SimpleExecutionSimulator,
    SimplePortfolioConstructor,
)
from qts.strategies import build_momentum_smoke_backtester

_FRED_SAMPLE = Path("data/historical/fred_index_sample.csv")
_ML_DECISION_TIMES = (
    datetime(2024, 1, 3, tzinfo=UTC),
    datetime(2024, 1, 4, tzinfo=UTC),
    datetime(2024, 1, 8, tzinfo=UTC),
    datetime(2024, 1, 9, tzinfo=UTC),
)


@dataclass(frozen=True)
class TimeSplit:
    """Chronological train, validation, and test dates."""

    train: tuple[datetime, ...]
    validation: tuple[datetime, ...]
    test: tuple[datetime, ...]


@dataclass(frozen=True)
class SimpleMLSignalModel:
    """A deterministic ML-style SignalModel using visible snapshot features."""

    feature_name: str
    coefficient: float
    seed: int
    feature_version: str
    top_n: int = 1
    model_name: str = "simple_ml"

    def generate(self, snapshot: DataSnapshot) -> SignalSet:
        ranked: list[tuple[float, str]] = []
        for asset_id in snapshot.asset_ids:
            feature_value = snapshot.features.get(asset_id, {}).get(self.feature_name)
            if feature_value is not None:
                ranked.append((feature_value * self.coefficient, asset_id))

        selected = sorted(ranked, key=lambda item: (-item[0], item[1]))[: self.top_n]
        return SignalSet(
            as_of=snapshot.as_of,
            scores={asset_id: 1.0 for _, asset_id in selected},
            model_name=self.model_name,
            metadata={
                "feature_name": self.feature_name,
                "feature_version": self.feature_version,
                "seed": str(self.seed),
                "coefficient": f"{self.coefficient:.6f}",
            },
        )


def time_ordered_split(
    dates: Sequence[datetime],
    train_count: int,
    validation_count: int,
) -> TimeSplit:
    """Split ordered dates into train, validation, and test windows."""

    ordered = tuple(sorted(dates))
    if train_count <= 0 or validation_count <= 0:
        raise ValueError("train_count and validation_count must be positive")
    if train_count + validation_count >= len(ordered):
        raise ValueError("split must leave at least one test observation")
    return TimeSplit(
        train=ordered[:train_count],
        validation=ordered[train_count : train_count + validation_count],
        test=ordered[train_count + validation_count :],
    )


def assert_feature_visibility(
    snapshot: DataSnapshot,
    visible_at: Mapping[str, Mapping[str, datetime]],
) -> None:
    """Raise if a supplied feature was not visible by the snapshot time."""

    for asset_id, features in snapshot.features.items():
        for feature_name in features:
            feature_visible_at = visible_at.get(asset_id, {}).get(feature_name)
            if feature_visible_at is not None and feature_visible_at > snapshot.as_of:
                raise ValueError(
                    f"future feature {asset_id}.{feature_name} visible at "
                    f"{feature_visible_at.isoformat()}"
                )


def train_simple_ml_signal(
    snapshots: Sequence[DataSnapshot],
    feature_name: str,
    seed: int,
) -> SimpleMLSignalModel:
    """Train a deterministic sign-only model from visible feature values."""

    values: list[float] = []
    for snapshot in snapshots:
        for asset_id in snapshot.asset_ids:
            feature_value = snapshot.features.get(asset_id, {}).get(feature_name)
            if feature_value is not None:
                values.append(feature_value)
    if not values:
        raise ValueError("no training features available")
    average_value = sum(values) / len(values)
    coefficient = 1.0 if average_value >= 0.0 else -1.0
    return SimpleMLSignalModel(
        feature_name=feature_name,
        coefficient=coefficient,
        seed=seed,
        feature_version=f"{feature_name}-v1",
    )


def compare_ml_to_momentum(path: Path = _FRED_SAMPLE) -> Report:
    """Compare the simple ML-style signal with the momentum rule strategy."""

    momentum_backtester, start, end, feature_source = build_momentum_smoke_backtester(path)
    split = time_ordered_split(_ML_DECISION_TIMES, train_count=2, validation_count=1)
    training_snapshots = tuple(feature_source.snapshot(date) for date in split.train)
    ml_model = train_simple_ml_signal(training_snapshots, feature_name="momentum_1", seed=11)

    ml_backtester = SimpleBacktester(
        data_source=feature_source,
        signal_model=ml_model,
        portfolio_constructor=SimplePortfolioConstructor(),
        risk_manager=BasicRiskManager(),
        execution_simulator=SimpleExecutionSimulator(),
        ledger=SimpleAccountingLedger(),
        decision_times=_ML_DECISION_TIMES,
        initial_cash=10_000.0,
    )
    momentum_result = momentum_backtester.run(
        start=start,
        end=end,
        config={
            "seed": "momentum-fred-smoke",
            "strategy": "momentum",
            "data_version": feature_source.data_version,
        },
    )
    ml_result = ml_backtester.run(
        start=start,
        end=end,
        config={
            "seed": "11",
            "strategy": "simple_ml",
            "feature_version": ml_model.feature_version,
            "data_version": feature_source.data_version,
        },
    )
    metrics = {
        "ml_net_value": ml_result.metrics["net_value"],
        "momentum_net_value": momentum_result.metrics["net_value"],
        "ml_total_return": ml_result.metrics["total_return"],
        "momentum_total_return": momentum_result.metrics["total_return"],
        "ml_minus_momentum_return": (
            ml_result.metrics["total_return"] - momentum_result.metrics["total_return"]
        ),
    }
    run_id = f"comparison-ml-momentum-{start:%Y%m%d}-{end:%Y%m%d}"
    lines = [f"run_id: {run_id}", *(f"{key}: {value:.6f}" for key, value in metrics.items())]
    return Report(run_id=run_id, text="\n".join(lines), metrics=metrics)


__all__ = [
    "SimpleMLSignalModel",
    "TimeSplit",
    "assert_feature_visibility",
    "compare_ml_to_momentum",
    "time_ordered_split",
    "train_simple_ml_signal",
]
