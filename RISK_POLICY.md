# Risk Policy

## Current Risk State

Phase 7 expands `BasicRiskManager` with configurable hard checks.

## Standing Rules

- No real-money trading is allowed.
- No broker API integration is allowed.
- No leverage is allowed unless a later documented task explicitly changes this.
- Any future order or target position must pass through `RiskManager`.
- Risk rules must be tested before they are relied on.

## Phase 2 Rules

- Short target weights are rejected.
- Gross target exposure above 100% is rejected.
- Orders with missing decision-time prices are rejected.

## Phase 7 Rules

Strict policy profile values:

- No short target weights.
- Single asset maximum target weight: 20%.
- Total target exposure maximum: 95%.
- Daily turnover maximum: 50% of portfolio equity.
- Stop new buy orders when daily mark-to-market loss exceeds 5%.
- Reject missing, non-positive, NaN, or infinite prices for target assets,
  orders, or held assets.

Risk rejections must return explicit reasons. Backtest reports must include the
number of rejections and reason counts.
