from __future__ import annotations

from pathlib import Path


def test_readiness_report_lists_blockers_and_disallows_live_trading(tmp_path: Path) -> None:
    from qts.readiness import generate_readiness_report

    report = generate_readiness_report(output_dir=tmp_path, tests_passed=True)

    assert report.status == "blocked"
    assert report.live_trading_allowed is False
    assert any("kill switch" in blocker.lower() for blocker in report.blockers)
    assert any("human confirmation" in blocker.lower() for blocker in report.blockers)
    assert any("paper observation" in blocker.lower() for blocker in report.blockers)


def test_readiness_report_writes_markdown(tmp_path: Path) -> None:
    from qts.readiness import generate_readiness_report

    report = generate_readiness_report(output_dir=tmp_path, tests_passed=True)
    text = report.markdown_path.read_text(encoding="utf-8")

    assert report.markdown_path.is_file()
    assert "# Live Readiness Review" in text
    assert "Status: blocked" in text
    assert "Live trading allowed: false" in text
    assert "Blockers" in text
