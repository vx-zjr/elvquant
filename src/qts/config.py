"""Commit-safe core configuration loading."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

_SECRET_KEY_MARKERS = ("secret", "token", "api_key", "apikey", "password", "credential")


@dataclass(frozen=True)
class CoreRunConfig:
    """Sanitized run configuration that is safe to record with reports."""

    provider: str
    asset_ids: tuple[str, ...]
    start: str
    end: str
    strategy: str
    seed: str
    parameters: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.provider:
            raise ValueError("provider must not be empty")
        if not self.asset_ids:
            raise ValueError("asset_ids must not be empty")
        if not self.strategy:
            raise ValueError("strategy must not be empty")
        if not self.seed:
            raise ValueError("seed must not be empty")

    def as_summary(self) -> dict[str, str]:
        """Return a stable, secret-free string map suitable for report hashes."""

        summary = {
            "provider": self.provider,
            "asset_ids": ",".join(self.asset_ids),
            "start": self.start,
            "end": self.end,
            "strategy": self.strategy,
            "seed": self.seed,
        }
        for key, value in sorted(self.parameters.items()):
            summary[f"parameter.{key}"] = value
        return summary


def load_core_config(path: Path) -> CoreRunConfig:
    """Load a commit-safe TOML config and reject secret-like fields."""

    payload = tomllib.loads(path.read_text(encoding="utf-8"))
    _reject_secret_like_keys(payload, ())

    asset_ids = payload.get("asset_ids")
    if not isinstance(asset_ids, list) or not all(isinstance(item, str) for item in asset_ids):
        raise ValueError("asset_ids must be a list of strings")

    parameters = payload.get("parameters", {})
    if not isinstance(parameters, dict):
        raise ValueError("parameters must be a table")

    return CoreRunConfig(
        provider=_required_string(payload, "provider"),
        asset_ids=tuple(asset_ids),
        start=_required_string(payload, "start"),
        end=_required_string(payload, "end"),
        strategy=_required_string(payload, "strategy"),
        seed=_required_string(payload, "seed"),
        parameters=_string_map(parameters),
    )


def _required_string(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _string_map(payload: Mapping[str, object]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in payload.items():
        if not isinstance(key, str):
            raise ValueError("configuration keys must be strings")
        if isinstance(value, bool):
            result[key] = str(value).lower()
        elif isinstance(value, int | float | str):
            result[key] = str(value)
        else:
            raise ValueError(f"parameter {key} must be a scalar")
    return result


def _reject_secret_like_keys(value: object, path: tuple[str, ...]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise ValueError("configuration keys must be strings")
            normalized = key.lower().replace("-", "_")
            if any(marker in normalized for marker in _SECRET_KEY_MARKERS):
                dotted = ".".join((*path, key))
                raise ValueError(f"secret-like configuration key is not allowed: {dotted}")
            _reject_secret_like_keys(nested, (*path, key))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _reject_secret_like_keys(nested, (*path, str(index)))


__all__ = ["CoreRunConfig", "load_core_config"]
