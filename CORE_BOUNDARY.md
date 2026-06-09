# Core Boundary

## Iron Rule

`elvquant_core` owns trading-system business logic. UI clients, notebooks, API
servers, schedulers, and dashboards are thin replaceable clients above this
core. They may select configurations, call public core entrypoints, and render
outputs; they must not implement strategy, risk, data normalization, order
generation, broker routing, accounting, reporting metrics, or secret handling.

## Replaceable Edges

- Data providers must satisfy the `DataSource` contract and the data visibility
  policy before a strategy can consume their snapshots.
- UI clients are replaceable adapters, just like data providers. Streamlit is
  the first local client, not a business-logic layer.
- Broker or exchange integrations must enter through explicit core interfaces
  and remain disabled by default until a future task explicitly allows them.
- One real provider plus the existing synthetic and CSV stubs is enough for the
  next provider phase. Do not create unused adapters in advance.

## Configuration And Secrets

Configuration and secrets are separate things:

- Commit configuration that is needed for reproducibility: provider name, asset
  universe, strategy parameters, run dates, risk parameters, and seeds.
- Never commit secrets: API tokens, secret keys, account IDs, passwords, or
  bearer credentials.
- Secret values must come from environment variables, a gitignored `.env`, or a
  secret manager. `.env.example` may document variable names only.
- Every run report must record a sanitized configuration summary and stable
  configuration hash alongside code commit, data version, date range, and seed.

## Data Policy At The Interface

Point-in-time and no-future-data rules belong at the data interface boundary.
Every real provider must validate that returned snapshots are visible at the
requested decision time, include a non-empty data version, and expose complete
prices only for requested visible assets. This prevents live or third-party data
adapters from reopening look-ahead risk.
