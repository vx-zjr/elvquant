from pathlib import Path

REQUIRED_DOCS = {
    "PROJECT.md",
    "ARCHITECTURE.md",
    "CONTRACTS.md",
    "DATA_POLICY.md",
    "RISK_POLICY.md",
    "TASKS.md",
    "DECISIONS.md",
    "REVIEW.md",
    "RUNBOOK.md",
    "EXPERIMENTS.md",
    "CHANGELOG.md",
    "CORE_BOUNDARY.md",
    "AGDR.md",
    "PROGRESS.md",
}


def test_package_imports() -> None:
    import qts

    assert qts.__version__ == "0.1.0"


def test_required_project_documents_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    missing = sorted(name for name in REQUIRED_DOCS if not (root / name).is_file())

    assert missing == []
