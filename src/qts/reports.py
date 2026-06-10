"""Stable structured report payloads for UI and API clients."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

from qts.contracts import BacktestResult, LedgerState, Report
from qts.historical import run_historical_smoke
from qts.ml import compare_ml_to_momentum
from qts.paper import run_synthetic_paper_demo
from qts.readiness import ReadinessControls, generate_readiness_report
from qts.reporting import current_git_commit, stable_config_hash
from qts.simple import build_synthetic_demo
from qts.stooq import load_stooq_research_config, run_stooq_etf_momentum_research
from qts.strategies import compare_momentum_to_equal_weight
from qts.time_utils import to_iso

ReportStatus = Literal["completed", "failed", "blocked"]
ReportRunner = Literal[
    "synthetic_demo",
    "historical_smoke",
    "momentum_compare",
    "ml_compare",
    "paper_demo",
    "readiness_report",
    "stooq_research",
]


@dataclass(frozen=True)
class StructuredWorkflow:
    """Public workflow metadata exposed to UI and API clients."""

    workflow_id: str
    label: str
    description: str
    requires_data: bool = False


@dataclass(frozen=True)
class EquityPoint:
    """JSON-ready ledger point for report consumers."""

    as_of: datetime
    cash: float
    positions: Mapping[str, float]
    equity: float
    cumulative_cost: float

    def to_payload(self) -> dict[str, object]:
        return {
            "as_of": self.as_of.isoformat(),
            "cash": self.cash,
            "positions": dict(self.positions),
            "equity": self.equity,
            "cumulative_cost": self.cumulative_cost,
        }


@dataclass(frozen=True)
class ArtifactRef:
    """Reference to a report artifact stored locally or remotely."""

    kind: str
    path_or_url: str
    content_type: str

    def to_payload(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "path_or_url": self.path_or_url,
            "content_type": self.content_type,
        }


@dataclass(frozen=True)
class StructuredReport:
    """Stable report contract shared by core, API, and front-end clients."""

    run_id: str
    workflow: str
    status: ReportStatus
    metadata: Mapping[str, str]
    config_summary: Mapping[str, str]
    metrics: Mapping[str, float]
    equity_curve: Sequence[EquityPoint] = field(default_factory=tuple)
    final_positions: Mapping[str, float] = field(default_factory=dict)
    artifacts: Sequence[ArtifactRef] = field(default_factory=tuple)
    warnings: Sequence[str] = field(default_factory=tuple)

    def to_payload(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "workflow": self.workflow,
            "status": self.status,
            "metadata": dict(self.metadata),
            "config_summary": dict(self.config_summary),
            "metrics": dict(self.metrics),
            "equity_curve": [point.to_payload() for point in self.equity_curve],
            "final_positions": dict(self.final_positions),
            "artifacts": [artifact.to_payload() for artifact in self.artifacts],
            "warnings": list(self.warnings),
        }


def structured_report_from_backtest(
    result: BacktestResult,
    workflow: str,
    start: object,
    end: object,
    git_commit: str | None = None,
    artifacts: Sequence[ArtifactRef] = (),
    warnings: Sequence[str] = (),
) -> StructuredReport:
    """Convert a backtest result into the stable UI/API report contract."""

    metadata = {
        "git_commit": git_commit if git_commit is not None else current_git_commit(),
        "config_hash": stable_config_hash(result.config_summary),
        "data_version": result.config_summary.get("data_version", "unknown"),
        "seed": result.config_summary.get("seed", "unknown"),
        "start": to_iso(start),
        "end": to_iso(end),
    }
    final_positions = dict(result.equity_curve[-1].positions) if result.equity_curve else {}
    return StructuredReport(
        run_id=result.run_id,
        workflow=workflow,
        status="completed",
        metadata=metadata,
        config_summary=dict(result.config_summary),
        metrics=dict(result.metrics),
        equity_curve=tuple(_equity_point(state) for state in result.equity_curve),
        final_positions=final_positions,
        artifacts=tuple(artifacts),
        warnings=tuple(warnings),
    )


def structured_synthetic_demo() -> StructuredReport:
    """Run the deterministic synthetic workflow and return a structured payload."""

    backtester, start, end = build_synthetic_demo()
    result = backtester.run(start=start, end=end, config={"seed": "deterministic"})
    return structured_report_from_backtest(
        result=result,
        workflow="synthetic_demo",
        start=start,
        end=end,
    )


def public_structured_workflows() -> tuple[StructuredWorkflow, ...]:
    """Return the public workflow catalog exposed above the core boundary."""

    return (
        StructuredWorkflow("synthetic_demo", "Synthetic demo", "Deterministic synthetic backtest."),
        StructuredWorkflow(
            "historical_smoke",
            "Historical smoke",
            "FRED CSV equal-weight smoke test.",
        ),
        StructuredWorkflow(
            "momentum_compare",
            "Momentum compare",
            "Momentum versus equal-weight comparison.",
        ),
        StructuredWorkflow("ml_compare", "ML compare", "ML-style research signal versus momentum."),
        StructuredWorkflow("paper_demo", "Paper demo", "Local dry-run paper trading workflow."),
        StructuredWorkflow(
            "readiness_report",
            "Readiness report",
            "Live-readiness blocker summary.",
        ),
        StructuredWorkflow(
            "stooq_research",
            "Stooq research",
            "Local-cache Stooq ETF momentum research.",
            True,
        ),
    )


def run_structured_workflow(workflow_id: str, core_root: Path | None = None) -> StructuredReport:
    """Run a public workflow and return the stable structured report contract."""

    root = core_root or Path.cwd()
    fred_sample = root / "data/historical/fred_index_sample.csv"
    if workflow_id == "synthetic_demo":
        return structured_synthetic_demo()
    if workflow_id == "historical_smoke":
        return _structured_text_report(
            run_historical_smoke(fred_sample),
            workflow="historical_smoke",
            data_version="fred-sample",
            seed="none",
        )
    if workflow_id == "momentum_compare":
        return _structured_text_report(
            compare_momentum_to_equal_weight(fred_sample),
            workflow="momentum_compare",
            data_version="fred-sample",
            seed="none",
        )
    if workflow_id == "ml_compare":
        return _structured_text_report(
            compare_ml_to_momentum(fred_sample),
            workflow="ml_compare",
            data_version="fred-sample",
            seed="deterministic",
        )
    if workflow_id == "paper_demo":
        return _structured_text_report(
            run_synthetic_paper_demo(output_dir=root / "paper_runs/api-synthetic-paper-demo"),
            workflow="paper_demo",
            data_version="synthetic-v1",
            seed="deterministic",
        )
    if workflow_id == "readiness_report":
        return structured_readiness_report(core_root=root, tests_passed=None)
    if workflow_id == "stooq_research":
        config_path = root / "configs/stooq_etf_momentum.example.toml"
        config = load_stooq_research_config(config_path)
        return _structured_text_report(
            run_stooq_etf_momentum_research(config),
            workflow="stooq_research",
            data_version="stooq-local-cache",
            seed=config.seed,
        )
    raise ValueError(f"unknown workflow: {workflow_id}")


def structured_readiness_report(
    core_root: Path | None = None,
    tests_passed: bool | None = None,
) -> StructuredReport:
    """Build the live-readiness report as a structured API payload."""

    root = core_root or Path.cwd()
    readiness = generate_readiness_report(
        output_dir=root / "reports/readiness",
        tests_passed=bool(tests_passed),
        controls=ReadinessControls(
            kill_switch_design=True,
            order_amount_limits=True,
            abnormal_alerting=True,
            order_source_traceability=True,
            stop_and_recovery=True,
            human_confirmation=True,
            sufficient_paper_observation=False,
        ),
    )
    blocker_count = float(len(readiness.blockers))
    test_status = "unknown" if tests_passed is None else str(tests_passed).lower()
    warnings = list(readiness.blockers)
    if tests_passed is None:
        warnings.append("readiness test status is unknown; inject tests_passed after fresh checks")
    return StructuredReport(
        run_id="live-readiness",
        workflow="readiness_report",
        status="blocked" if blocker_count else "completed",
        metadata={
            "git_commit": current_git_commit(),
            "config_hash": stable_config_hash({"workflow": "readiness_report"}),
            "data_version": "none",
            "seed": "none",
            "start": "not-applicable",
            "end": "not-applicable",
            "tests_passed": test_status,
        },
        config_summary={"workflow": "readiness_report"},
        metrics={"readiness_blockers": blocker_count},
        artifacts=(
            ArtifactRef(
                kind="markdown",
                path_or_url="reports/readiness/live_readiness.md",
                content_type="text/markdown",
            ),
        ),
        warnings=tuple(warnings),
    )


def _structured_text_report(
    report: Report,
    workflow: str,
    data_version: str,
    seed: str,
) -> StructuredReport:
    return StructuredReport(
        run_id=report.run_id,
        workflow=workflow,
        status="completed",
        metadata={
            "git_commit": current_git_commit(),
            "config_hash": stable_config_hash({"workflow": workflow, "run_id": report.run_id}),
            "data_version": data_version,
            "seed": seed,
            "start": "unknown",
            "end": "unknown",
        },
        config_summary={"workflow": workflow},
        metrics=dict(report.metrics),
        final_positions={},
        artifacts=(ArtifactRef(kind="text", path_or_url="inline", content_type="text/plain"),),
        warnings=(),
    )


def _equity_point(state: LedgerState) -> EquityPoint:
    return EquityPoint(
        as_of=state.as_of,
        cash=state.cash,
        positions=dict(state.positions),
        equity=state.equity,
        cumulative_cost=state.cumulative_cost,
    )


__all__ = [
    "ArtifactRef",
    "EquityPoint",
    "ReportStatus",
    "StructuredReport",
    "StructuredWorkflow",
    "public_structured_workflows",
    "run_structured_workflow",
    "structured_report_from_backtest",
    "structured_readiness_report",
    "structured_synthetic_demo",
    "to_iso",
]
