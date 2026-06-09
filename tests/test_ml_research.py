from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from qts.contracts import DataSnapshot

SAMPLE_PATH = Path("data/historical/fred_index_sample.csv")


def test_time_ordered_split_is_chronological() -> None:
    from qts.ml import time_ordered_split

    dates = tuple(datetime(2026, 1, day, tzinfo=UTC) for day in range(1, 7))
    split = time_ordered_split(dates, train_count=3, validation_count=1)

    assert split.train == dates[:3]
    assert split.validation == dates[3:4]
    assert split.test == dates[4:]
    assert max(split.train) < min(split.validation) < min(split.test)


def test_feature_visibility_rejects_future_visible_features() -> None:
    from qts.ml import assert_feature_visibility

    snapshot = DataSnapshot(
        as_of=datetime(2026, 1, 3, tzinfo=UTC),
        asset_ids=("AAA",),
        prices={"AAA": 100.0},
        data_version="unit",
        features={"AAA": {"ml_score": 1.0}},
    )

    with pytest.raises(ValueError, match="future feature"):
        assert_feature_visibility(
            snapshot,
            {"AAA": {"ml_score": datetime(2026, 1, 4, tzinfo=UTC)}},
        )


def test_simple_ml_signal_is_reproducible_and_compares_to_momentum() -> None:
    from qts.ml import compare_ml_to_momentum, train_simple_ml_signal

    snapshots = (
        DataSnapshot(
            as_of=datetime(2026, 1, 2, tzinfo=UTC),
            asset_ids=("AAA", "BBB"),
            prices={"AAA": 101.0, "BBB": 99.0},
            data_version="unit",
            features={"AAA": {"momentum_1": 0.01}, "BBB": {"momentum_1": -0.01}},
        ),
        DataSnapshot(
            as_of=datetime(2026, 1, 3, tzinfo=UTC),
            asset_ids=("AAA", "BBB"),
            prices={"AAA": 102.0, "BBB": 98.0},
            data_version="unit",
            features={"AAA": {"momentum_1": 0.02}, "BBB": {"momentum_1": -0.02}},
        ),
    )

    left = train_simple_ml_signal(snapshots, feature_name="momentum_1", seed=7)
    right = train_simple_ml_signal(snapshots, feature_name="momentum_1", seed=7)
    signals = left.generate(snapshots[-1])
    comparison = compare_ml_to_momentum(SAMPLE_PATH)

    assert left == right
    assert signals.model_name == "simple_ml"
    assert signals.scores == {"AAA": 1.0}
    assert comparison.run_id == "comparison-ml-momentum-20240102-20240110"
    assert "ml_net_value" in comparison.text
    assert "momentum_net_value" in comparison.text
