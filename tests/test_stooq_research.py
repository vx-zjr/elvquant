from __future__ import annotations

import json
from pathlib import Path


def test_stooq_research_writes_oos_comparison_report(tmp_path: Path) -> None:
    from qts.stooq import (
        StooqResearchConfig,
        run_stooq_etf_momentum_research,
        write_stooq_normalized_csv,
    )

    data_path = tmp_path / "stooq.csv"
    write_stooq_normalized_csv(
        raw_csv_by_asset={
            "SPY.US": _raw_stooq_csv((100, 101, 102, 103, 104, 105, 106)),
            "QQQ.US": _raw_stooq_csv((200, 203, 202, 206, 208, 207, 212)),
        },
        output_path=data_path,
        data_version="stooq-test-v1",
        source_urls={
            "SPY.US": "https://stooq.com/q/d/l/?s=spy.us&i=d",
            "QQQ.US": "https://stooq.com/q/d/l/?s=qqq.us&i=d",
        },
    )
    config = StooqResearchConfig(
        data_path=data_path,
        reports_dir=tmp_path / "reports",
        asset_ids=("SPY.US", "QQQ.US"),
        start="2024-01-02",
        end="2024-01-11",
        train_start="2024-01-02",
        train_end="2024-01-06",
        validation_start="2024-01-08",
        validation_end="2024-01-10",
        test_start="2024-01-09",
        test_end="2024-01-11",
        lookback_observations=1,
        top_n=1,
        initial_cash=10_000.0,
        fixed_commission=0.0,
        proportional_commission_rate=0.0,
        slippage_rate=0.0,
        seed="unit-stooq",
    )

    report = run_stooq_etf_momentum_research(config)

    assert report.run_id == "stooq-etf-momentum-20240102-20240111"
    assert report.metrics["test_decision_count"] > 0.0
    assert "test_momentum_minus_equal_weight_return" in report.metrics
    assert "config_hash:" in report.text
    assert "data_file_hash:" in report.text
    assert "data_version: stooq-test-v1" in report.text
    assert "fixed_commission: 0.0" in report.text
    assert "test: 2024-01-09 to 2024-01-11" in report.text

    payload = json.loads(
        (
            tmp_path
            / "reports"
            / "stooq-etf-momentum-20240102-20240111"
            / "stooq-etf-momentum-20240102-20240111.json"
        ).read_text(encoding="utf-8")
    )
    assert payload["metadata"]["data_file_hash"]
    assert payload["metadata"]["config_hash"]
    assert payload["metadata"]["data_version"] == "stooq-test-v1"
    assert payload["sample_splits"]["test"] == {
        "start": "2024-01-09",
        "end": "2024-01-11",
        "decision_count": 1,
    }


def _raw_stooq_csv(closes: tuple[int, ...]) -> str:
    dates = (
        "2024-01-02",
        "2024-01-03",
        "2024-01-04",
        "2024-01-05",
        "2024-01-08",
        "2024-01-09",
        "2024-01-10",
    )
    rows = ["Date,Open,High,Low,Close,Volume"]
    rows.extend(f"{date},1,1,1,{close},100" for date, close in zip(dates, closes, strict=True))
    return "\n".join([*rows, ""])
