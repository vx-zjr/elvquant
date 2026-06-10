from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUST_ROOT = ROOT / "rust"


def test_rust_workspace_declares_service_crates() -> None:
    manifest = (RUST_ROOT / "Cargo.toml").read_text(encoding="utf-8")

    assert "elvquant_core_types" in manifest
    assert "elvquant_core_math" in manifest
    assert "elvquant_core_service" in manifest
    assert "qts_rust_kernel" in manifest


def test_rust_types_define_structured_report_contract() -> None:
    source = (RUST_ROOT / "elvquant_core_types" / "src" / "lib.rs").read_text(
        encoding="utf-8"
    )

    for symbol in (
        "StructuredReport",
        "EquityPoint",
        "ArtifactRef",
        "RunSummary",
        "WorkflowDescriptor",
        "serde::Serialize",
        "run_id",
        "equity_curve",
        "final_positions",
    ):
        assert symbol in source


def test_rust_math_declares_portfolio_and_metric_functions() -> None:
    source = (RUST_ROOT / "elvquant_core_math" / "src" / "lib.rs").read_text(
        encoding="utf-8"
    )

    for symbol in (
        "position_value",
        "orders_for_target",
        "max_drawdown",
        "total_return",
        "missing price for held asset",
        "equity series must not be empty",
    ):
        assert symbol in source


def test_rust_service_exposes_core_api_routes() -> None:
    source = (RUST_ROOT / "elvquant_core_service" / "src" / "main.rs").read_text(
        encoding="utf-8"
    )

    for route in ('"/health"', '"/workflows"', '"/runs"', '"/runs/{run_id}"'):
        assert route in source
    for symbol in ("synthetic_demo", "X-Service-Token", "X-Owner-User-Id"):
        assert symbol in source
