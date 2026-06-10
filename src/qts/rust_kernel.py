"""Optional Rust-backed pure calculation kernel with Python fallback."""

from __future__ import annotations

import importlib
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from qts.metrics_math import max_drawdown, total_return
from qts.portfolio_math import position_value

NativeFunction = Callable[..., Any]

try:  # pragma: no cover - covered when the optional native module is built.
    _native_module = importlib.import_module("qts_rust_kernel")
    _native_position_value: NativeFunction | None = _native_module.position_value
    _native_max_drawdown: NativeFunction | None = _native_module.max_drawdown
    _native_total_return: NativeFunction | None = _native_module.total_return
except ImportError:  # pragma: no cover - fallback behavior is covered through public functions.
    _native_position_value = None
    _native_max_drawdown = None
    _native_total_return = None


def kernel_position_value(
    positions: Mapping[str, float],
    prices: Mapping[str, float],
) -> float:
    """Return marked position value, using Rust when the native module exists."""

    if _native_position_value is not None:
        return float(_native_position_value(dict(positions), dict(prices)))
    return position_value(positions, prices)


def kernel_max_drawdown(equity_values: Sequence[float]) -> float:
    """Return maximum drawdown for an equity series."""

    values = tuple(equity_values)
    if not values:
        raise ValueError("equity series must not be empty")
    if _native_max_drawdown is not None:
        return float(_native_max_drawdown(values))
    return max_drawdown(values)


def kernel_total_return(equity_values: Sequence[float]) -> float:
    """Return total return from first to last equity value."""

    values = tuple(equity_values)
    if not values:
        raise ValueError("equity series must not be empty")
    if values[0] == 0.0:
        raise ValueError("first equity value must not be zero")
    if _native_total_return is not None:
        return float(_native_total_return(values))
    return total_return(values)


__all__ = ["kernel_max_drawdown", "kernel_position_value", "kernel_total_return"]
