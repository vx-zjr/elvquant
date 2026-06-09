"""Structured experiment report file generation."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from qts.contracts import BacktestResult, LedgerState


@dataclass(frozen=True)
class ReportFileSet:
    """Paths and identifiers produced by a structured report write."""

    json_path: Path
    markdown_path: Path
    config_hash: str


def stable_config_hash(config: Mapping[str, str]) -> str:
    """Return a stable short hash for a string configuration mapping."""

    encoded = json.dumps(dict(config), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()[:12]


def write_experiment_report(
    result: BacktestResult,
    output_dir: Path,
    start: object,
    end: object,
    git_commit: str | None = None,
) -> ReportFileSet:
    """Write machine-readable JSON and human-readable Markdown reports."""

    config_hash = stable_config_hash(result.config_summary)
    commit = git_commit if git_commit is not None else current_git_commit()
    run_dir = output_dir / result.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "run_id": result.run_id,
        "metadata": {
            "git_commit": commit,
            "config_hash": config_hash,
            "data_version": result.config_summary.get("data_version", "unknown"),
            "seed": result.config_summary.get("seed", "unknown"),
            "start": _to_iso(start),
            "end": _to_iso(end),
        },
        "config_summary": dict(result.config_summary),
        "metrics": dict(result.metrics),
        "equity_curve": [_ledger_state_payload(state) for state in result.equity_curve],
        "final_positions": dict(result.equity_curve[-1].positions),
        "monthly_returns": _monthly_returns(result.equity_curve),
    }

    json_path = run_dir / f"{result.run_id}.json"
    markdown_path = run_dir / f"{result.run_id}.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(_markdown_report(payload), encoding="utf-8")
    return ReportFileSet(
        json_path=json_path,
        markdown_path=markdown_path,
        config_hash=config_hash,
    )


def current_git_commit() -> str:
    """Return the current short git commit, or unknown outside a git checkout."""

    completed = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        cwd=_core_repository_root(),
    )
    if completed.returncode != 0:
        return "unknown"
    return completed.stdout.strip() or "unknown"


def _core_repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _ledger_state_payload(state: LedgerState) -> dict[str, object]:
    return {
        "as_of": state.as_of.isoformat(),
        "cash": state.cash,
        "positions": dict(state.positions),
        "equity": state.equity,
        "cumulative_cost": state.cumulative_cost,
    }


def _monthly_returns(equity_curve: Sequence[LedgerState]) -> dict[str, float]:
    by_month: dict[str, list[float]] = {}
    for state in equity_curve:
        month = state.as_of.strftime("%Y-%m")
        by_month.setdefault(month, []).append(state.equity)
    return {
        month: round(values[-1] / values[0] - 1.0, 12)
        for month, values in by_month.items()
        if values and values[0] != 0.0
    }


def _markdown_report(payload: Mapping[str, object]) -> str:
    metadata = payload["metadata"]
    metrics = payload["metrics"]
    final_positions = payload["final_positions"]
    monthly_returns = payload["monthly_returns"]
    if not isinstance(metadata, Mapping):
        raise TypeError("metadata must be a mapping")
    if not isinstance(metrics, Mapping):
        raise TypeError("metrics must be a mapping")
    if not isinstance(final_positions, Mapping):
        raise TypeError("final_positions must be a mapping")
    if not isinstance(monthly_returns, Mapping):
        raise TypeError("monthly_returns must be a mapping")

    lines = [f"# {payload['run_id']}", "", "## Metadata"]
    lines.extend(f"- {key}: {value}" for key, value in metadata.items())
    lines.extend(["", "## Metrics"])
    lines.extend(
        f"- {key}: {value:.6f}" if isinstance(value, float) else f"- {key}: {value}"
        for key, value in metrics.items()
    )
    lines.extend(["", "## Monthly Returns"])
    lines.extend(f"- {key}: {value:.6f}" for key, value in monthly_returns.items())
    lines.extend(["", "## Final Positions"])
    lines.extend(f"- {key}: {value}" for key, value in final_positions.items())
    lines.append("")
    return "\n".join(lines)


def _to_iso(value: object) -> str:
    if hasattr(value, "isoformat"):
        return str(value.isoformat())
    return str(value)


__all__ = [
    "ReportFileSet",
    "current_git_commit",
    "stable_config_hash",
    "write_experiment_report",
]
