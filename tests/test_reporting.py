from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from qts.contracts import BacktestResult, LedgerState


def test_config_hash_is_stable_independent_of_key_order() -> None:
    from qts.reporting import stable_config_hash

    left = stable_config_hash({"seed": "1", "strategy": "momentum"})
    right = stable_config_hash({"strategy": "momentum", "seed": "1"})

    assert left == right
    assert len(left) == 12


def test_write_experiment_report_files_include_required_metadata(tmp_path: Path) -> None:
    from qts.reporting import write_experiment_report

    start = datetime(2026, 1, 1, tzinfo=UTC)
    end = datetime(2026, 1, 3, tzinfo=UTC)
    result = BacktestResult(
        run_id="unit-run",
        config_summary={
            "seed": "unit-seed",
            "data_version": "unit-data-v1",
            "strategy": "unit",
        },
        equity_curve=(
            LedgerState(
                as_of=start,
                cash=10_000.0,
                positions={},
                equity=10_000.0,
                cumulative_cost=0.0,
            ),
            LedgerState(
                as_of=end,
                cash=9_000.0,
                positions={"AAA": 10.0},
                equity=10_500.0,
                cumulative_cost=5.0,
            ),
        ),
        metrics={
            "net_value": 1.05,
            "total_return": 0.05,
            "max_drawdown": 0.0,
            "turnover": 1.0,
            "total_cost": 5.0,
            "risk_rejections": 0.0,
        },
    )

    files = write_experiment_report(
        result=result,
        output_dir=tmp_path,
        start=start,
        end=end,
        git_commit="abc123",
    )

    assert files.json_path.is_file()
    assert files.markdown_path.is_file()

    payload = json.loads(files.json_path.read_text(encoding="utf-8"))
    markdown = files.markdown_path.read_text(encoding="utf-8")

    assert payload["run_id"] == "unit-run"
    assert payload["metadata"]["git_commit"] == "abc123"
    assert payload["metadata"]["config_hash"] == files.config_hash
    assert payload["metadata"]["data_version"] == "unit-data-v1"
    assert payload["metadata"]["seed"] == "unit-seed"
    assert payload["metadata"]["start"] == "2026-01-01T00:00:00+00:00"
    assert payload["metadata"]["end"] == "2026-01-03T00:00:00+00:00"
    assert payload["metrics"]["net_value"] == 1.05
    assert payload["final_positions"] == {"AAA": 10.0}
    assert payload["monthly_returns"]["2026-01"] == 0.05
    assert "# unit-run" in markdown
    assert "git_commit: abc123" in markdown
    assert "net_value: 1.050000" in markdown
