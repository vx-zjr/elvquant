use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Debug, PartialEq)]
pub struct OrderDelta {
    pub asset_id: String,
    pub quantity: f64,
}

const EPSILON: f64 = 1e-9;

pub fn position_value(
    positions: &BTreeMap<String, f64>,
    prices: &BTreeMap<String, f64>,
) -> Result<f64, String> {
    let mut value = 0.0;
    for (asset_id, quantity) in positions {
        let price = prices
            .get(asset_id)
            .ok_or_else(|| format!("missing price for held asset {asset_id}"))?;
        value += quantity * price;
    }
    Ok(value)
}

pub fn orders_for_target(
    positions: &BTreeMap<String, f64>,
    equity: f64,
    asset_ids: &[String],
    prices: &BTreeMap<String, f64>,
    target_weights: &BTreeMap<String, f64>,
) -> Result<Vec<OrderDelta>, String> {
    let mut ordered_assets = BTreeSet::new();
    for asset_id in asset_ids {
        ordered_assets.insert(asset_id.clone());
    }
    for asset_id in positions.keys() {
        ordered_assets.insert(asset_id.clone());
    }

    let mut orders = Vec::new();
    for asset_id in ordered_assets {
        let price = prices
            .get(&asset_id)
            .ok_or_else(|| format!("missing decision price for {asset_id}"))?;
        let current_quantity = positions.get(&asset_id).copied().unwrap_or(0.0);
        let target_weight = target_weights.get(&asset_id).copied().unwrap_or(0.0);
        let quantity = (target_weight * equity - current_quantity * price) / price;
        if quantity.abs() > EPSILON {
            orders.push(OrderDelta { asset_id, quantity });
        }
    }
    Ok(orders)
}

pub fn max_drawdown(equity_values: &[f64]) -> Result<f64, String> {
    if equity_values.is_empty() {
        return Err("equity series must not be empty".to_string());
    }
    let mut peak = equity_values[0];
    let mut drawdown = 0.0;
    for equity in equity_values {
        if *equity > peak {
            peak = *equity;
        }
        if peak > 0.0 {
            let current = *equity / peak - 1.0;
            if current < drawdown {
                drawdown = current;
            }
        }
    }
    Ok(drawdown)
}

pub fn total_return(equity_values: &[f64]) -> Result<f64, String> {
    if equity_values.is_empty() {
        return Err("equity series must not be empty".to_string());
    }
    let first = equity_values[0];
    if first == 0.0 {
        return Err("first equity value must not be zero".to_string());
    }
    Ok(equity_values[equity_values.len() - 1] / first - 1.0)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn computes_position_value() {
        let positions = BTreeMap::from([("AAA".to_string(), 2.0), ("BBB".to_string(), -1.0)]);
        let prices = BTreeMap::from([("AAA".to_string(), 10.0), ("BBB".to_string(), 3.0)]);
        assert_eq!(position_value(&positions, &prices).unwrap(), 17.0);
    }

    #[test]
    fn computes_target_order_deltas() {
        let positions = BTreeMap::from([("AAA".to_string(), 1.0)]);
        let prices = BTreeMap::from([("AAA".to_string(), 10.0), ("BBB".to_string(), 20.0)]);
        let target = BTreeMap::from([("AAA".to_string(), 0.5), ("BBB".to_string(), 0.5)]);
        let assets = vec!["AAA".to_string(), "BBB".to_string()];
        let orders = orders_for_target(&positions, 100.0, &assets, &prices, &target).unwrap();
        assert_eq!(orders.len(), 2);
    }

    #[test]
    fn computes_metrics() {
        assert_eq!(max_drawdown(&[100.0, 120.0, 90.0, 110.0]).unwrap(), -0.25);
        assert_eq!(total_return(&[100.0, 110.0]).unwrap(), 0.1);
    }
}
