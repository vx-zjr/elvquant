"""Shared time formatting helpers for report payloads."""

from __future__ import annotations


def to_iso(value: object) -> str:
    """Return an ISO-like string for datetime-like values and plain strings otherwise."""

    if hasattr(value, "isoformat"):
        return str(value.isoformat())
    return str(value)


__all__ = ["to_iso"]
