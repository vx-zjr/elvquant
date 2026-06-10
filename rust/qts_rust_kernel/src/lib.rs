use std::collections::HashMap;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

#[pyfunction]
fn position_value(positions: HashMap<String, f64>, prices: HashMap<String, f64>) -> PyResult<f64> {
    let mut value = 0.0;
    for (asset_id, quantity) in positions.iter() {
        let price = prices
            .get(asset_id)
            .ok_or_else(|| PyValueError::new_err(format!("missing price for held asset {asset_id}")))?;
        value += quantity * price;
    }
    Ok(value)
}

#[pyfunction]
fn max_drawdown(equity_values: Vec<f64>) -> PyResult<f64> {
    if equity_values.is_empty() {
        return Err(PyValueError::new_err("equity series must not be empty"));
    }
    let mut peak = equity_values[0];
    let mut drawdown = 0.0;
    for equity in equity_values {
        if equity > peak {
            peak = equity;
        }
        if peak > 0.0 {
            let current = equity / peak - 1.0;
            if current < drawdown {
                drawdown = current;
            }
        }
    }
    Ok(drawdown)
}

#[pyfunction]
fn total_return(equity_values: Vec<f64>) -> PyResult<f64> {
    if equity_values.is_empty() {
        return Err(PyValueError::new_err("equity series must not be empty"));
    }
    let first = equity_values[0];
    if first == 0.0 {
        return Err(PyValueError::new_err("first equity value must not be zero"));
    }
    Ok(equity_values[equity_values.len() - 1] / first - 1.0)
}

#[pymodule]
fn qts_rust_kernel(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(position_value, m)?)?;
    m.add_function(wrap_pyfunction!(max_drawdown, m)?)?;
    m.add_function(wrap_pyfunction!(total_return, m)?)?;
    Ok(())
}
