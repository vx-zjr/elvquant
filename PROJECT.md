# elvquant_core Project

## Goal

Build the modular, document-driven core of an auditable quantitative trading
system. The first priority is trustworthiness: no look-ahead bias, explicit risk
controls, reproducible results, and a project state that a new code agent can
understand from repository documents.

## Current Stage

The document-defined business plan is complete through Phase 12. The core can
generate traceable manual order recommendations, enforce risk and kill-switch
controls, require human confirmation, and record dry-run order submissions
locally. Broker integration and real-money order submission remain disabled.
The next project stage is hardening `elvquant_core` as a reusable core under a
replaceable thin UI such as `elvquant_front`.

The active post-review direction is Rust-led core reconstruction. Python remains
the reference implementation and research compatibility layer while Rust takes
over typed report/API contracts, deterministic portfolio math, and a service
boundary in verified slices. Do not migrate strategy, risk, accounting, data
provider, or report semantics unless the Rust result has parity tests against
the Python behavior.

## Explicit Non-Goals

- No live market data feed.
- No live broker connection.
- No live trading or real-money order submission.
- No ML or AI-driven live trading.
- No production strategy implementation.
- No broker data source implementation.
- No secrets, API keys, account identifiers, or passwords in code or docs.
- No UI business logic. UI clients must call public core interfaces and render
  results only.

## Strategy Disclaimer

The momentum strategy is a research fixture for exercising the pipeline. It is
not trading advice and must not be used for live orders.

The ML-style signal is also research-only. It cannot place orders, alter risk
checks, alter the backtest engine, or connect to live trading.

## Required Start Protocol

Every agent must read these files before editing:

- `../PROJECT_MEMORY.md`
- `docs/source/quant_trading_agent_plan.md`
- `CORE_BOUNDARY.md`
- `PROJECT.md`
- `ARCHITECTURE.md`
- `CONTRACTS.md`
- `DATA_POLICY.md`
- `RISK_POLICY.md`
- `TASKS.md`
- `REVIEW.md`

Then execute only the first `Pending` task in `TASKS.md`.

## Durable Memory Rule

Development context must be preserved in maintained documents, not only in model
memory or chat history. When architecture, public interfaces, local commands,
deployment assumptions, or known limitations change, update the relevant docs in
the same change set. `../PROJECT_MEMORY.md` is the cross-project memory index for
the paired core/front repositories.
