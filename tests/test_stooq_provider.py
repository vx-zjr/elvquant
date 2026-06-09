from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest


def test_stooq_normalized_csv_returns_visible_validated_snapshot(tmp_path: Path) -> None:
    from qts.stooq import StooqHistoricalDataSource, write_stooq_normalized_csv

    output_path = tmp_path / "stooq.csv"
    write_stooq_normalized_csv(
        raw_csv_by_asset={
            "SPY.US": _raw_stooq_csv((100.0, 101.0)),
            "QQQ.US": _raw_stooq_csv((200.0, 202.0)),
        },
        output_path=output_path,
        data_version="stooq-test-v1",
        source_urls={
            "SPY.US": "https://stooq.com/q/d/l/?s=spy.us&i=d",
            "QQQ.US": "https://stooq.com/q/d/l/?s=qqq.us&i=d",
        },
    )

    source = StooqHistoricalDataSource(path=output_path, asset_ids=("SPY.US", "QQQ.US"))
    snapshot = source.snapshot(datetime(2024, 1, 3, tzinfo=UTC))

    assert snapshot.asset_ids == ("SPY.US", "QQQ.US")
    assert snapshot.prices == {"SPY.US": 101.0, "QQQ.US": 202.0}
    assert snapshot.data_version == "stooq-test-v1"


def test_stooq_source_snapshot_does_not_download_at_runtime(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from qts.stooq import StooqHistoricalDataSource, write_stooq_normalized_csv

    output_path = tmp_path / "stooq.csv"
    write_stooq_normalized_csv(
        raw_csv_by_asset={"SPY.US": _raw_stooq_csv((100.0, 101.0))},
        output_path=output_path,
        data_version="stooq-test-v1",
        source_urls={"SPY.US": "https://stooq.com/q/d/l/?s=spy.us&i=d"},
    )

    def fail_if_network_is_used(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("snapshot must not use network")

    monkeypatch.setattr("urllib.request.urlopen", fail_if_network_is_used)

    source = StooqHistoricalDataSource(path=output_path, asset_ids=("SPY.US",))
    assert source.snapshot(datetime(2024, 1, 2, tzinfo=UTC)).prices["SPY.US"] == 100.0


def test_stooq_normalizer_rejects_non_positive_close(tmp_path: Path) -> None:
    from qts.stooq import write_stooq_normalized_csv

    with pytest.raises(ValueError, match="positive close"):
        write_stooq_normalized_csv(
            raw_csv_by_asset={"SPY.US": _raw_stooq_csv((0.0, 101.0))},
            output_path=tmp_path / "bad.csv",
            data_version="stooq-test-v1",
            source_urls={"SPY.US": "https://stooq.com/q/d/l/?s=spy.us&i=d"},
        )


def test_stooq_downloader_rejects_non_csv_responses(tmp_path: Path) -> None:
    from qts.stooq import cache_stooq_daily_csv

    with pytest.raises(ValueError, match="did not return CSV"):
        cache_stooq_daily_csv(
            asset_id="SPY.US",
            start="2024-01-01",
            end="2024-01-05",
            cache_dir=tmp_path,
            fetch_text=lambda _url: "<html>verification required</html>",
        )


def test_stooq_normalizer_can_read_cached_raw_files(tmp_path: Path) -> None:
    from qts.stooq import StooqHistoricalDataSource, write_stooq_normalized_csv_from_files

    raw_path = tmp_path / "spy.csv"
    raw_path.write_text(_raw_stooq_csv((100.0, 101.0)), encoding="utf-8")
    normalized_path = tmp_path / "normalized.csv"

    write_stooq_normalized_csv_from_files(
        raw_paths_by_asset={"SPY.US": raw_path},
        output_path=normalized_path,
        data_version="stooq-file-test-v1",
        source_urls={"SPY.US": "https://stooq.com/q/d/l/?s=spy.us&i=d"},
    )

    source = StooqHistoricalDataSource(path=normalized_path, asset_ids=("SPY.US",))
    assert source.snapshot(datetime(2024, 1, 3, tzinfo=UTC)).prices == {"SPY.US": 101.0}


def _raw_stooq_csv(closes: tuple[float, float]) -> str:
    return "\n".join(
        [
            "Date,Open,High,Low,Close,Volume",
            f"2024-01-02,1,1,1,{closes[0]},100",
            f"2024-01-03,1,1,1,{closes[1]},100",
            "",
        ]
    )
