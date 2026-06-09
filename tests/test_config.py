from pathlib import Path


def test_example_config_loads_without_secrets() -> None:
    from qts.config import load_core_config

    config = load_core_config(Path("configs/local.example.toml"))

    assert config.provider == "synthetic"
    assert config.asset_ids == ("AAA", "BBB")
    assert config.as_summary()["parameter.initial_cash"] == "10000"
    assert not any("secret" in key or "token" in key for key in config.as_summary())


def test_config_rejects_secret_like_keys(tmp_path) -> None:
    from qts.config import load_core_config

    path = tmp_path / "bad.toml"
    path.write_text(
        "\n".join(
            [
                'provider = "synthetic"',
                'asset_ids = ["AAA"]',
                'start = "2026-01-01"',
                'end = "2026-01-02"',
                'strategy = "equal_weight"',
                'seed = "deterministic"',
                'api_key = "do-not-store-this"',
            ]
        ),
        encoding="utf-8",
    )

    try:
        load_core_config(path)
    except ValueError as exc:
        assert "secret-like" in str(exc)
    else:
        raise AssertionError("secret-like config key was accepted")
