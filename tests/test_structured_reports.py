from __future__ import annotations

from datetime import UTC, datetime


def test_synthetic_runner_returns_structured_report_payload() -> None:
    from qts.reports import StructuredReport, structured_synthetic_demo

    report = structured_synthetic_demo()

    assert isinstance(report, StructuredReport)
    assert report.run_id.startswith("synthetic-")
    assert report.workflow == "synthetic_demo"
    assert report.status == "completed"
    assert report.metadata["seed"] == "deterministic"
    assert report.metrics["total_return"] > 0.0
    assert report.equity_curve
    assert report.final_positions
    assert report.to_payload()["run_id"] == report.run_id


def test_public_structured_workflows_expose_uniform_payloads() -> None:
    from qts.reports import public_structured_workflows

    workflows = public_structured_workflows()

    assert {workflow.workflow_id for workflow in workflows} >= {
        "synthetic_demo",
        "historical_smoke",
        "momentum_compare",
        "ml_compare",
        "paper_demo",
        "readiness_report",
        "stooq_research",
    }
    for workflow in workflows:
        assert workflow.label
        assert workflow.description
        assert isinstance(workflow.requires_data, bool)


def test_readiness_structured_report_uses_compatible_contract() -> None:
    from qts.reports import structured_readiness_report

    report = structured_readiness_report()

    assert report.workflow == "readiness_report"
    assert report.status in {"completed", "blocked"}
    assert "readiness_blockers" in report.metrics
    assert report.metadata["data_version"] == "none"


def test_structured_report_payload_is_json_ready() -> None:
    from qts.reports import ArtifactRef, EquityPoint, StructuredReport

    report = StructuredReport(
        run_id="run-1",
        workflow="synthetic_demo",
        status="completed",
        metadata={"git_commit": "unknown", "seed": "deterministic"},
        config_summary={"data_source": "synthetic"},
        metrics={"total_return": 0.1},
        equity_curve=(
            EquityPoint(
                as_of=datetime(2026, 1, 1, tzinfo=UTC),
                cash=100.0,
                positions={"AAA": 1.0},
                equity=200.0,
                cumulative_cost=0.0,
            ),
        ),
        final_positions={"AAA": 1.0},
        artifacts=(
            ArtifactRef(
                kind="markdown",
                path_or_url="reports/run-1.md",
                content_type="text/markdown",
            ),
        ),
        warnings=("demo only",),
    )

    payload = report.to_payload()

    assert payload == {
        "run_id": "run-1",
        "workflow": "synthetic_demo",
        "status": "completed",
        "metadata": {"git_commit": "unknown", "seed": "deterministic"},
        "config_summary": {"data_source": "synthetic"},
        "metrics": {"total_return": 0.1},
        "equity_curve": [
            {
                "as_of": "2026-01-01T00:00:00+00:00",
                "cash": 100.0,
                "positions": {"AAA": 1.0},
                "equity": 200.0,
                "cumulative_cost": 0.0,
            }
        ],
        "final_positions": {"AAA": 1.0},
        "artifacts": [
            {
                "kind": "markdown",
                "path_or_url": "reports/run-1.md",
                "content_type": "text/markdown",
            }
        ],
        "warnings": ["demo only"],
    }
