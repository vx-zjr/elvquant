# Risk Policy

## Current Risk State

Phase 2 includes `BasicRiskManager`.

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
