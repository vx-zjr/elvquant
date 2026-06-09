"""Live-readiness review generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReadinessReport:
    """Summary of live-readiness checks."""

    status: str
    live_trading_allowed: bool
    blockers: tuple[str, ...]
    markdown_path: Path


@dataclass(frozen=True)
class ReadinessControls:
    """Declared non-broker readiness controls."""

    kill_switch_design: bool = False
    order_amount_limits: bool = False
    abnormal_alerting: bool = False
    order_source_traceability: bool = False
    stop_and_recovery: bool = False
    human_confirmation: bool = False
    sufficient_paper_observation: bool = False


def generate_readiness_report(
    output_dir: Path,
    tests_passed: bool,
    controls: ReadinessControls | None = None,
) -> ReadinessReport:
    """Generate a readiness report without enabling live trading."""

    controls = controls or ReadinessControls()
    output_dir.mkdir(parents=True, exist_ok=True)
    checks = {
        "all_tests_passed": tests_passed,
        "kill_switch_design": controls.kill_switch_design,
        "order_amount_limits": controls.order_amount_limits,
        "max_loss_limits": True,
        "abnormal_alerting": controls.abnormal_alerting,
        "order_source_traceability": controls.order_source_traceability,
        "stop_and_recovery": controls.stop_and_recovery,
        "api_key_management": True,
        "human_confirmation": controls.human_confirmation,
        "sufficient_paper_observation": controls.sufficient_paper_observation,
    }
    blockers = _blockers(checks)
    live_allowed = not blockers
    status = "ready" if live_allowed else "blocked"
    markdown_path = output_dir / "live_readiness.md"
    markdown_path.write_text(
        _markdown(status=status, live_allowed=live_allowed, checks=checks, blockers=blockers),
        encoding="utf-8",
    )
    return ReadinessReport(
        status=status,
        live_trading_allowed=live_allowed,
        blockers=tuple(blockers),
        markdown_path=markdown_path,
    )


def _blockers(checks: dict[str, bool]) -> list[str]:
    labels = {
        "all_tests_passed": "All tests must pass before live trading.",
        "kill_switch_design": "Kill switch design is not implemented.",
        "order_amount_limits": "Order amount limits are not implemented.",
        "abnormal_alerting": "Abnormal alerting is not implemented.",
        "order_source_traceability": "Order source signal traceability is incomplete.",
        "stop_and_recovery": "Stop and recovery procedure is incomplete.",
        "human_confirmation": "Human confirmation workflow is not implemented.",
        "sufficient_paper_observation": "Sufficient paper observation has not been completed.",
    }
    return [message for key, message in labels.items() if not checks.get(key, False)]


def _markdown(
    status: str,
    live_allowed: bool,
    checks: dict[str, bool],
    blockers: list[str],
) -> str:
    lines = [
        "# Live Readiness Review",
        "",
        f"Status: {status}",
        f"Live trading allowed: {str(live_allowed).lower()}",
        "",
        "## Checks",
    ]
    lines.extend(f"- {key}: {'pass' if value else 'block'}" for key, value in checks.items())
    lines.extend(["", "## Blockers"])
    if blockers:
        lines.extend(f"- {blocker}" for blocker in blockers)
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


__all__ = ["ReadinessControls", "ReadinessReport", "generate_readiness_report"]
