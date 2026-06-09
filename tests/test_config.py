from pathlib import Path


def test_example_config_loads_without_secrets() -> None:
    from qts.config import load_core_config

    config = load_core_config(Path("configs/local.example.toml"))

    assert config.provider == "synthetic"
    assert config.asset_ids == ("AAA", "BBB")
    assert config.as_summary()["parameter.initial_cash"] == "10000"
    assert not any("secret" in key or "token" in key for key in config.as_summary())


def test_stooq_research_config_loads_without_secrets() -> None:
    from qts.config import load_core_config

    config = load_core_config(Path("configs/stooq_etf_momentum.example.toml"))

    assert config.provider == "stooq"
    assert config.asset_ids == ("SPY.US", "QQQ.US", "IWM.US", "TLT.US", "GLD.US")
    assert config.strategy == "momentum_vs_equal_weight"
    assert config.as_summary()["parameter.lookback_observations"] == "20"
    assert not any("secret" in key or "token" in key for key in config.as_summary())


def test_stooq_typed_research_config_loads_from_example() -> None:
    from qts.stooq import load_stooq_research_config

    config = load_stooq_research_config(Path("configs/stooq_etf_momentum.example.toml"))

    assert config.asset_ids == ("SPY.US", "QQQ.US", "IWM.US", "TLT.US", "GLD.US")
    assert config.data_path == Path("data/processed/stooq_etf_eod.csv")
    assert config.lookback_observations == 20
    assert config.fixed_commission == 1.0


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
