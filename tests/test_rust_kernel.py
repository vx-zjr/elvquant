from __future__ import annotations


def test_kernel_position_value_matches_public_math() -> None:
    from qts.portfolio_math import position_value
    from qts.rust_kernel import kernel_position_value

    positions = {"AAA": 2.0, "BBB": -1.0}
    prices = {"AAA": 10.0, "BBB": 3.0}

    assert kernel_position_value(positions, prices) == position_value(positions, prices)


def test_kernel_max_drawdown_matches_expected_path() -> None:
    from qts.rust_kernel import kernel_max_drawdown

    assert kernel_max_drawdown((100.0, 120.0, 90.0, 110.0)) == -0.25


def test_kernel_total_return_rejects_empty_series() -> None:
    import pytest

    from qts.rust_kernel import kernel_total_return

    with pytest.raises(ValueError, match="equity series must not be empty"):
        kernel_total_return(())
