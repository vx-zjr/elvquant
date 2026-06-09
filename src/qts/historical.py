"""Read-only historical CSV data source for Phase 4."""

from __future__ import annotations

import csv
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, time
from pathlib import Path

from qts.contracts import AssetId, DataSnapshot, Report
from qts.simple import (
    BasicRiskManager,
    EqualWeightSignal,
    SimpleAccountingLedger,
    SimpleBacktester,
    SimpleExecutionSimulator,
    SimplePortfolioConstructor,
    SimpleReporter,
)

_DEFAULT_ASSETS = ("SP500", "NASDAQCOM")
_DEFAULT_SAMPLE = Path("data/historical/fred_index_sample.csv")
_REQUIRED_COLUMNS = {"date", "asset_id", "close", "data_version"}


@dataclass(frozen=True)
class CsvHistoricalDataSource:
    """Read historical prices from a normalized CSV file without writing data."""

    path: Path
    asset_ids: tuple[AssetId, ...]
    _prices_by_time: Mapping[datetime, Mapping[AssetId, float]] = field(init=False)
    data_version: str = field(init=False)

    def __post_init__(self) -> None:
        prices_by_time: dict[datetime, dict[AssetId, float]] = {}
        versions: set[str] = set()
        selected_assets = set(self.asset_ids)

        with self.path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ValueError("historical CSV has no header")
            missing_columns = _REQUIRED_COLUMNS.difference(reader.fieldnames)
            if missing_columns:
                raise ValueError(f"historical CSV missing columns: {sorted(missing_columns)}")

            for row_number, row in enumerate(reader, start=2):
                asset_id = _required(row, "asset_id", row_number)
                if asset_id not in selected_assets:
                    continue

                as_of = _parse_date(_required(row, "date", row_number), row_number)
                close_text = _required(row, "close", row_number)
                if close_text in {"", "."}:
                    raise ValueError(f"missing close at row {row_number}")
                close = float(close_text)
                if close <= 0.0:
                    raise ValueError(f"close must be positive at row {row_number}")

                versions.add(_required(row, "data_version", row_number))
                prices_by_time.setdefault(as_of, {})[asset_id] = close

        if not versions:
            raise ValueError("historical CSV contains no selected asset rows")
        if len(versions) != 1:
            raise ValueError("historical CSV contains multiple data versions")

        object.__setattr__(self, "_prices_by_time", prices_by_time)
        object.__setattr__(self, "data_version", versions.pop())

    def snapshot(self, decision_time: datetime) -> DataSnapshot:
        if decision_time.tzinfo is None:
            raise ValueError("decision_time must be timezone-aware")
        as_of = decision_time.astimezone(UTC)
        if as_of.timetz() != time(0, tzinfo=UTC):
            raise ValueError("decision_time must be a UTC midnight timestamp")

        prices = self._prices_by_time.get(as_of)
        if prices is None:
            raise ValueError(f"missing historical prices for {as_of.date().isoformat()}")

        missing_assets = [asset_id for asset_id in self.asset_ids if asset_id not in prices]
        if missing_assets:
            raise ValueError(
                "missing historical prices for "
                f"{as_of.date().isoformat()}: {', '.join(missing_assets)}"
            )

        return DataSnapshot(
            as_of=as_of,
            asset_ids=self.asset_ids,
            prices={asset_id: prices[asset_id] for asset_id in self.asset_ids},
            data_version=self.data_version,
        )


def build_historical_smoke_backtester(
    path: Path = _DEFAULT_SAMPLE,
) -> tuple[SimpleBacktester, datetime, datetime, CsvHistoricalDataSource]:
    """Build an equal-weight smoke run over the fixed FRED sample."""

    start = datetime(2024, 1, 2, tzinfo=UTC)
    end = datetime(2024, 1, 10, tzinfo=UTC)
    data_source = CsvHistoricalDataSource(path=path, asset_ids=_DEFAULT_ASSETS)
    decision_times = (
        datetime(2024, 1, 2, tzinfo=UTC),
        datetime(2024, 1, 3, tzinfo=UTC),
        datetime(2024, 1, 4, tzinfo=UTC),
        datetime(2024, 1, 8, tzinfo=UTC),
        datetime(2024, 1, 9, tzinfo=UTC),
    )
    backtester = SimpleBacktester(
        data_source=data_source,
        signal_model=EqualWeightSignal(),
        portfolio_constructor=SimplePortfolioConstructor(),
        risk_manager=BasicRiskManager(),
        execution_simulator=SimpleExecutionSimulator(),
        ledger=SimpleAccountingLedger(),
        decision_times=decision_times,
        initial_cash=10_000.0,
    )
    return backtester, start, end, data_source


def run_historical_smoke(path: Path = _DEFAULT_SAMPLE) -> Report:
    """Run the fixed historical smoke test and return a report."""

    backtester, start, end, data_source = build_historical_smoke_backtester(path)
    result = backtester.run(
        start=start,
        end=end,
        config={
            "seed": "fred-smoke",
            "data_source": "fred_csv",
            "historical_data_source": "FRED",
            "data_version": data_source.data_version,
        },
    )
    result = replace(result, run_id=f"historical-fred-{start:%Y%m%d}-{end:%Y%m%d}")
    return SimpleReporter().build(result)


def _required(row: Mapping[str, str | None], column: str, row_number: int) -> str:
    value = row.get(column)
    if value is None:
        raise ValueError(f"missing {column} at row {row_number}")
    value = value.strip()
    if not value:
        raise ValueError(f"missing {column} at row {row_number}")
    return value


def _parse_date(value: str, row_number: int) -> datetime:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"invalid date at row {row_number}: {value}") from exc
    return datetime.combine(parsed, time.min, tzinfo=UTC)


__all__ = [
    "CsvHistoricalDataSource",
    "build_historical_smoke_backtester",
    "run_historical_smoke",
]
