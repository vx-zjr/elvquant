from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from pytest import approx

from qts.contracts import DataSnapshot

SAMPLE_PATH = Path("data/historical/fred_index_sample.csv")


def test_momentum_signal_selects_strongest_visible_past_performer() -> None:
    from qts.strategies import MomentumSignal

    snapshot = DataSnapshot(
        as_of=datetime(2026, 1, 4, tzinfo=UTC),
        asset_ids=("AAA", "BBB", "CCC"),
        prices={"AAA": 103.0, "BBB": 102.0, "CCC": 99.0},
        data_version="unit",
        features={
            "AAA": {"momentum_3": 0.03},
            "BBB": {"momentum_3": 0.08},
            "CCC": {"momentum_3": -0.01},
        },
    )

    signals = MomentumSignal(feature_name="momentum_3", top_n=1).generate(snapshot)

    assert signals.model_name == "momentum"
    assert signals.scores == {"BBB": 1.0}
    assert signals.metadata["feature_name"] == "momentum_3"


def test_trailing_return_feature_source_uses_prior_observations_only() -> None:
    from qts.historical import CsvHistoricalDataSource
    from qts.strategies import TrailingReturnFeatureDataSource

    available_times = (
        datetime(2024, 1, 2, tzinfo=UTC),
        datetime(2024, 1, 3, tzinfo=UTC),
    )
    source = TrailingReturnFeatureDataSource(
        base=CsvHistoricalDataSource(path=SAMPLE_PATH, asset_ids=("SP500", "NASDAQCOM")),
        available_times=available_times,
        lookback_observations=1,
        feature_name="momentum_1",
    )

    snapshot = source.snapshot(datetime(2024, 1, 3, tzinfo=UTC))

    assert snapshot.features["SP500"]["momentum_1"] == approx(4704.81 / 4742.83 - 1.0)
    assert snapshot.features["NASDAQCOM"]["momentum_1"] == approx(14592.210 / 14765.940 - 1.0)


def test_momentum_end_to_end_and_comparison_report() -> None:
    from qts.strategies import compare_momentum_to_equal_weight, run_momentum_smoke

    momentum_report = run_momentum_smoke(SAMPLE_PATH)
    comparison_report = compare_momentum_to_equal_weight(SAMPLE_PATH)

    assert momentum_report.run_id == "momentum-fred-20240102-20240110"
    assert "net_value" in momentum_report.text
    assert comparison_report.run_id == "comparison-momentum-equal-weight-20240102-20240110"
    assert "equal_weight_net_value" in comparison_report.text
    assert "momentum_net_value" in comparison_report.text
    assert "momentum_minus_equal_weight_return" in comparison_report.text
