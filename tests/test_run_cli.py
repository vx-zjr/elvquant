from __future__ import annotations


def test_cli_can_emit_structured_json(capsys) -> None:  # type: ignore[no-untyped-def]
    import json

    from run import main

    main(["synthetic_demo", "--json"])

    payload = json.loads(capsys.readouterr().out)
    assert payload["workflow"] == "synthetic_demo"
    assert payload["status"] == "completed"


def test_git_commit_prefers_injected_environment(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    from qts.reporting import current_git_commit

    monkeypatch.setenv("ELVQUANT_GIT_COMMIT", "abc1234")

    assert current_git_commit() == "abc1234"
