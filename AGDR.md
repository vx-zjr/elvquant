# Agent Governance Decision Record

## AGDR-001: Use Stooq EOD As The First Real-Data Test Source

Date: 2026-06-09

Decision: The first real-data provider path is Stooq-format EOD daily data,
cached and normalized into local CSV before research runs. Official Stooq
downloads remain supported, while local debugging currently uses the public
Kaggle mirror `borismarjanovic/price-volume-data-for-all-us-stocks-etfs` to
avoid blocking on Stooq's apikey/captcha flow.

Rationale: The immediate goal is to prove the core can ingest real historical
market data without broker access or UI business logic. Official Stooq scripted
downloads may require a provider `apikey`; the Kaggle mirror supplies
Stooq-format historical OHLCV files with no project secret, which unblocks
local research workflow testing.

Boundaries:

- No broker integration.
- No live or intraday feed.
- No secret value in committed Stooq config; optional `STOOQ_API_KEY` may be
  supplied only through the local runtime environment.
- Kaggle mirror data is for local debugging and first research plumbing only;
  it is not current-market data and currently ends at 2017-11-10 for the chosen
  ETF universe.
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
