from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from qts.simple import EqualWeightSignal, SimpleReporter

SAMPLE_PATH = Path("data/historical/fred_index_sample.csv")


def test_csv_historical_data_source_returns_visible_snapshot() -> None:
    from qts.historical import CsvHistoricalDataSource

    source = CsvHistoricalDataSource(
        path=SAMPLE_PATH,
        asset_ids=("SP500", "NASDAQCOM"),
    )
    snapshot = source.snapshot(datetime(2024, 1, 3, tzinfo=UTC))

    assert snapshot.as_of == datetime(2024, 1, 3, tzinfo=UTC)
    assert snapshot.asset_ids == ("SP500", "NASDAQCOM")
    assert snapshot.prices == {"SP500": 4704.81, "NASDAQCOM": 14592.210}
    assert snapshot.data_version == "fred-index-sample-20240102-20240110-v1"


def test_csv_historical_data_source_rejects_missing_dates() -> None:
    from qts.historical import CsvHistoricalDataSource

    source = CsvHistoricalDataSource(
        path=SAMPLE_PATH,
        asset_ids=("SP500", "NASDAQCOM"),
    )

    with pytest.raises(ValueError, match="missing historical prices"):
        source.snapshot(datetime(2024, 1, 6, tzinfo=UTC))


def test_csv_historical_data_source_rejects_blank_or_dot_values(tmp_path: Path) -> None:
    from qts.historical import CsvHistoricalDataSource

    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text(
        "date,asset_id,close,source,source_url,data_version\n"
        "2024-01-02,SP500,.,FRED,https://fred.stlouisfed.org/series/SP500,bad\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing close"):
        CsvHistoricalDataSource(path=bad_csv, asset_ids=("SP500",))


def test_equal_weight_strategy_runs_on_historical_csv_without_backtester_changes() -> None:
    from qts.historical import build_historical_smoke_backtester

    backtester, start, end, data_source = build_historical_smoke_backtester(SAMPLE_PATH)
    result = backtester.run(
        start=start,
        end=end,
        config={
            "seed": "fred-smoke",
            "historical_data_source": "FRED",
            "data_version": data_source.data_version,
        },
    )
    report = SimpleReporter().build(result)

    assert isinstance(backtester.signal_model, EqualWeightSignal)
    assert result.config_summary["data_version"] == "fred-index-sample-20240102-20240110-v1"
    assert result.metrics["net_value"] > 0.0
    assert "net_value" in report.text


def test_historical_smoke_report_uses_historical_run_id() -> None:
    from qts.historical import run_historical_smoke

    report = run_historical_smoke(SAMPLE_PATH)

    assert report.run_id == "historical-fred-20240102-20240110"
    assert "historical-fred-20240102-20240110" in report.text
