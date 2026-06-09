# Risk Policy

## Current Risk State

No order generation or risk manager exists in Phase 0.

## Standing Rules

- No real-money trading is allowed.
- No broker API integration is allowed.
- No leverage is allowed unless a later documented task explicitly changes this.
- Any future order or target position must pass through `RiskManager`.
- Risk rules must be tested before they are relied on.
