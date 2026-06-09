# Agent Governance Decision Record

## AGDR-001: Use Stooq EOD As The First Real-Data Test Source

Date: 2026-06-09

Decision: The first real-data provider is Stooq EOD daily data, cached and
normalized into local CSV before research runs. Stooq is used only as a
read-only historical data source.

Rationale: The immediate goal is to prove the core can ingest real historical
market data without broker access or UI business logic. Stooq is still the
lowest-friction provider for program testing, but scripted downloads may require
a provider `apikey`; that value is a secret and must stay outside committed
configuration.

Boundaries:

- No broker integration.
- No live or intraday feed.
- No secret value in committed Stooq config; optional `STOOQ_API_KEY` may be
  supplied only through the local runtime environment.
- No React frontend work until research output justifies it.
- Runtime `DataSource.snapshot()` reads only local normalized CSV and must not
  perform network access.

Consequences:

- Network download is a data-preparation step, not part of backtesting.
- Reports must record config hash, data file hash, data version, sample split,
  and cost assumptions.
- If Stooq proves unreliable, unavailable without an API key, or insufficient,
  the next provider candidate is a single Tiingo EOD adapter rather than a
  fleet of unused adapters.
