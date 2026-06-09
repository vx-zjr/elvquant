"""Research-only rule strategies for Phase 5."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path

from qts.contracts import AssetId, BacktestResult, DataSnapshot, DataSource, Report, SignalSet
from qts.historical import CsvHistoricalDataSource, build_historical_smoke_backtester
from qts.simple import (
    BasicRiskManager,
    SimpleAccountingLedger,
    SimpleBacktester,
    SimpleExecutionSimulator,
    SimplePortfolioConstructor,
    SimpleReporter,
)

_FRED_SAMPLE = Path("data/historical/fred_index_sample.csv")
_FRED_ASSETS = ("SP500", "NASDAQCOM")
_FRED_TIMES = (
    datetime(2024, 1, 2, tzinfo=UTC),
    datetime(2024, 1, 3, tzinfo=UTC),
    datetime(2024, 1, 4, tzinfo=UTC),
    datetime(2024, 1, 5, tzinfo=UTC),
    datetime(2024, 1, 8, tzinfo=UTC),
    datetime(2024, 1, 9, tzinfo=UTC),
    datetime(2024, 1, 10, tzinfo=UTC),
)
_MOMENTUM_DECISION_TIMES = (
    datetime(2024, 1, 3, tzinfo=UTC),
    datetime(2024, 1, 4, tzinfo=UTC),
    datetime(2024, 1, 8, tzinfo=UTC),
    datetime(2024, 1, 9, tzinfo=UTC),
)


@dataclass(frozen=True)
class MomentumSignal:
    """Select assets with the strongest visible trailing-return feature."""

    feature_name: str = "momentum_1"
    top_n: int = 1
    model_name: str = "momentum"

    def __post_init__(self) -> None:
        if self.top_n <= 0:
            raise ValueError("top_n must be positive")

    def generate(self, snapshot: DataSnapshot) -> SignalSet:
        ranked: list[tuple[float, AssetId]] = []
        for asset_id in snapshot.asset_ids:
            feature_value = snapshot.features.get(asset_id, {}).get(self.feature_name)
            if feature_value is not None:
                ranked.append((feature_value, asset_id))

        selected = sorted(ranked, key=lambda item: (-item[0], item[1]))[: self.top_n]
        return SignalSet(
            as_of=snapshot.as_of,
            scores={asset_id: 1.0 for _, asset_id in selected},
            model_name=self.model_name,
            metadata={
                "feature_name": self.feature_name,
                "top_n": str(self.top_n),
            },
        )


@dataclass(frozen=True)
class TrailingReturnFeatureDataSource:
    """Decorate a data source with visible trailing-return features."""

    base: DataSource
    available_times: Sequence[datetime]
    lookback_observations: int
    feature_name: str = "momentum_1"
    data_version: str = field(init=False)
    _time_index: Mapping[datetime, int] = field(init=False)

    def __post_init__(self) -> None:
        if self.lookback_observations <= 0:
            raise ValueError("lookback_observations must be positive")
        normalized_times = tuple(time.astimezone(UTC) for time in self.available_times)
        object.__setattr__(
            self,
            "_time_index",
            {time: index for index, time in enumerate(normalized_times)},
        )
        object.__setattr__(self, "available_times", normalized_times)
        object.__setattr__(self, "data_version", getattr(self.base, "data_version", "unknown"))

    def snapshot(self, decision_time: datetime) -> DataSnapshot:
        snapshot = self.base.snapshot(decision_time)
        index = self._time_index.get(snapshot.as_of)
        if index is None:
            raise ValueError(f"decision time not in feature calendar: {snapshot.as_of}")

        features = {
            asset_id: dict(snapshot.features.get(asset_id, {}))
            for asset_id in snapshot.asset_ids
        }
        if index >= self.lookback_observations:
            past_time = self.available_times[index - self.lookback_observations]
            past_snapshot = self.base.snapshot(past_time)
            for asset_id in snapshot.asset_ids:
                past_price = past_snapshot.prices[asset_id]
                current_price = snapshot.prices[asset_id]
                features[asset_id][self.feature_name] = current_price / past_price - 1.0

        return DataSnapshot(
            as_of=snapshot.as_of,
            asset_ids=snapshot.asset_ids,
            prices=snapshot.prices,
            data_version=snapshot.data_version,
            features=features,
        )


def build_momentum_smoke_backtester(
    path: Path = _FRED_SAMPLE,
) -> tuple[SimpleBacktester, datetime, datetime, TrailingReturnFeatureDataSource]:
    """Build a FRED-sample momentum smoke run."""

    start = datetime(2024, 1, 2, tzinfo=UTC)
    end = datetime(2024, 1, 10, tzinfo=UTC)
    base = CsvHistoricalDataSource(path=path, asset_ids=_FRED_ASSETS)
    data_source = TrailingReturnFeatureDataSource(
        base=base,
        available_times=_FRED_TIMES,
        lookback_observations=1,
        feature_name="momentum_1",
    )
    backtester = SimpleBacktester(
        data_source=data_source,
        signal_model=MomentumSignal(feature_name="momentum_1", top_n=1),
        portfolio_constructor=SimplePortfolioConstructor(),
        risk_manager=BasicRiskManager(),
        execution_simulator=SimpleExecutionSimulator(),
        ledger=SimpleAccountingLedger(),
        decision_times=_MOMENTUM_DECISION_TIMES,
        initial_cash=10_000.0,
    )
    return backtester, start, end, data_source


def run_momentum_smoke(path: Path = _FRED_SAMPLE) -> Report:
    """Run the FRED-sample momentum smoke test."""

    backtester, start, end, data_source = build_momentum_smoke_backtester(path)
    result = backtester.run(
        start=start,
        end=end,
        config={
            "seed": "momentum-fred-smoke",
            "strategy": "momentum",
            "feature_name": "momentum_1",
            "lookback_observations": "1",
            "data_version": data_source.data_version,
        },
    )
    result = replace(result, run_id=f"momentum-fred-{start:%Y%m%d}-{end:%Y%m%d}")
    return SimpleReporter().build(result)


def compare_momentum_to_equal_weight(path: Path = _FRED_SAMPLE) -> Report:
    """Compare the momentum smoke run with the equal-weight baseline."""

    baseline_backtester, start, end, baseline_data_source = build_historical_smoke_backtester(path)
    baseline_result = baseline_backtester.run(
        start=start,
        end=end,
        config={
            "seed": "fred-smoke",
            "strategy": "equal_weight",
            "data_version": baseline_data_source.data_version,
        },
    )
    momentum_backtester, _, _, momentum_data_source = build_momentum_smoke_backtester(path)
    momentum_result = momentum_backtester.run(
        start=start,
        end=end,
        config={
            "seed": "momentum-fred-smoke",
            "strategy": "momentum",
            "feature_name": "momentum_1",
            "lookback_observations": "1",
            "data_version": momentum_data_source.data_version,
        },
    )

    metrics = _comparison_metrics(baseline_result, momentum_result)
    run_id = f"comparison-momentum-equal-weight-{start:%Y%m%d}-{end:%Y%m%d}"
    metric_lines = (f"{key}: {value:.6f}" for key, value in metrics.items())
    text = "\n".join([f"run_id: {run_id}", *metric_lines])
    return Report(run_id=run_id, text=text, metrics=metrics)


def _comparison_metrics(
    baseline_result: BacktestResult,
    momentum_result: BacktestResult,
) -> Mapping[str, float]:
    return {
        "equal_weight_net_value": baseline_result.metrics["net_value"],
        "momentum_net_value": momentum_result.metrics["net_value"],
        "equal_weight_total_return": baseline_result.metrics["total_return"],
        "momentum_total_return": momentum_result.metrics["total_return"],
        "momentum_minus_equal_weight_return": (
            momentum_result.metrics["total_return"] - baseline_result.metrics["total_return"]
        ),
    }


__all__ = [
    "MomentumSignal",
    "TrailingReturnFeatureDataSource",
    "build_momentum_smoke_backtester",
    "compare_momentum_to_equal_weight",
    "run_momentum_smoke",
]
