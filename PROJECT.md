# Project

## Goal

Build a modular, document-driven quantitative trading research system that can
grow in small, audited steps. The first priority is trustworthiness: no
look-ahead bias, explicit risk controls, reproducible results, and a project
state that a new code agent can understand from repository documents.

## Current Stage

Phase 1 is complete once the core Protocol interfaces and dataclass payloads are
defined. The next task is Phase 2: implement the thinnest end-to-end loop using
synthetic data only.

## Explicit Non-Goals

- No real market data.
- No live broker connection.
- No live trading or real-money order submission.
- No ML or AI-driven signal generation.
- No real strategy implementation.
- No real data source implementation.
- No secrets, API keys, account identifiers, or passwords in code or docs.

## Required Start Protocol

Every agent must read these files before editing:

- `PROJECT.md`
- `ARCHITECTURE.md`
- `CONTRACTS.md`
- `DATA_POLICY.md`
- `RISK_POLICY.md`
- `TASKS.md`
- `REVIEW.md`

Then execute only the first `Pending` task in `TASKS.md`.
