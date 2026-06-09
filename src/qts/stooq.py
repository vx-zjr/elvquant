"""Read-only Stooq EOD data ingestion and research helpers."""

from __future__ import annotations

import csv
import json
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, time, timedelta
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlencode

from qts.config import load_core_config
from qts.contracts import AssetId, BacktestResult, DataSnapshot, DataSource, Report, SignalModel
from qts.costs import (
    CompositeCostModel,
    FixedCommissionCostModel,
    ProportionalCommissionCostModel,
    SlippageCostModel,
)
from qts.historical import CsvHistoricalDataSource
from qts.providers import ValidatedDataSource
from qts.reporting import current_git_commit, stable_config_hash
from qts.simple import (
    BasicRiskManager,
    EqualWeightSignal,
    SimpleAccountingLedger,
    SimpleBacktester,
    SimpleExecutionSimulator,
    SimplePortfolioConstructor,
)
from qts.strategies import MomentumSignal, TrailingReturnFeatureDataSource

FetchText = Callable[[str], str]

_STOOQ_DOWNLOAD_BASE_URL = "https://stooq.com/q/d/l/"
_STOOQ_REQUIRED_COLUMNS = {"Date", "Close"}
_DEFAULT_STOOQ_ASSETS = ("SPY.US", "QQQ.US", "IWM.US", "TLT.US", "GLD.US")


@dataclass(frozen=True)
class StooqHistoricalDataSource:
    """Read normalized Stooq EOD prices from local CSV through the DataSource contract."""

    path: Path
    asset_ids: tuple[AssetId, ...]
    _validated_source: ValidatedDataSource = field(init=False)
    data_version: str = field(init=False)

    def __post_init__(self) -> None:
        base = CsvHistoricalDataSource(path=self.path, asset_ids=self.asset_ids)
        object.__setattr__(self, "_validated_source", ValidatedDataSource(base))
        object.__setattr__(self, "data_version", base.data_version)

    def snapshot(self, decision_time: datetime) -> DataSnapshot:
        return self._validated_source.snapshot(decision_time)


@dataclass(frozen=True)
class StooqResearchConfig:
    """Configuration for the first Stooq ETF out-of-sample research run."""

    data_path: Path = Path("data/processed/stooq_etf_eod.csv")
    reports_dir: Path = Path("reports")
    asset_ids: tuple[AssetId, ...] = _DEFAULT_STOOQ_ASSETS
    start: str = "2015-01-01"
    end: str = "2025-12-31"
    train_start: str = "2015-01-01"
    train_end: str = "2022-01-01"
    validation_start: str = "2022-01-01"
    validation_end: str = "2024-01-01"
    test_start: str = "2024-01-01"
    test_end: str = "2025-12-31"
    lookback_observations: int = 20
    top_n: int = 1
    initial_cash: float = 10_000.0
    fixed_commission: float = 1.0
    proportional_commission_rate: float = 0.0005
    slippage_rate: float = 0.001
    seed: str = "stooq-etf-momentum-v1"

    def as_summary(self, data_version: str, data_file_hash: str) -> dict[str, str]:
        return {
            "provider": "stooq",
            "asset_ids": ",".join(self.asset_ids),
            "start": self.start,
            "end": self.end,
            "train": f"{self.train_start}:{self.train_end}",
            "validation": f"{self.validation_start}:{self.validation_end}",
            "test": f"{self.test_start}:{self.test_end}",
            "strategy": "momentum_vs_equal_weight",
            "lookback_observations": str(self.lookback_observations),
            "top_n": str(self.top_n),
            "initial_cash": f"{self.initial_cash:.2f}",
            "fixed_commission": str(self.fixed_commission),
            "proportional_commission_rate": str(self.proportional_commission_rate),
            "slippage_rate": str(self.slippage_rate),
            "seed": self.seed,
            "data_version": data_version,
            "data_file_hash": data_file_hash,
        }


def stooq_daily_csv_url(asset_id: str, start: str, end: str) -> str:
    """Return the Stooq daily CSV URL for one asset and inclusive date range."""

    query = urlencode(
        {
            "s": asset_id.lower(),
            "i": "d",
            "d1": start.replace("-", ""),
            "d2": end.replace("-", ""),
        }
    )
    return f"{_STOOQ_DOWNLOAD_BASE_URL}?{query}"


def cache_stooq_daily_csv(
    asset_id: str,
    start: str,
    end: str,
    cache_dir: Path,
    fetch_text: FetchText | None = None,
) -> Path:
    """Download one Stooq daily CSV into a local cache after validating CSV shape."""

    cache_dir.mkdir(parents=True, exist_ok=True)
    url = stooq_daily_csv_url(asset_id, start, end)
    text = (fetch_text or _fetch_text)(url)
    _ensure_stooq_csv(text, asset_id)

    path = cache_dir / f"{asset_id.lower().replace('.', '_')}_{start}_{end}.csv"
    path.write_text(text, encoding="utf-8")
    return path


def write_stooq_normalized_csv(
    raw_csv_by_asset: Mapping[str, str],
    output_path: Path,
    data_version: str,
    source_urls: Mapping[str, str],
) -> Path:
    """Write Stooq raw CSV payloads into the normalized historical CSV shape."""

    if not data_version:
        raise ValueError("data_version must not be empty")

    rows: list[dict[str, str]] = []
    for asset_id, text in raw_csv_by_asset.items():
        _ensure_stooq_csv(text, asset_id)
        reader = csv.DictReader(text.splitlines())
        if reader.fieldnames is None:
            raise ValueError(f"Stooq CSV for {asset_id} has no header")
        missing_columns = _STOOQ_REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing_columns:
            raise ValueError(f"Stooq CSV for {asset_id} missing columns: {sorted(missing_columns)}")

        for row_number, row in enumerate(reader, start=2):
            date = _required(row, "Date", asset_id, row_number)
            close_text = _required(row, "Close", asset_id, row_number)
            close = float(close_text)
            if close <= 0.0:
                raise ValueError(
                    f"Stooq CSV for {asset_id} has non-positive close at row {row_number}"
                )
            rows.append(
                {
                    "date": date,
                    "asset_id": asset_id,
                    "close": close_text,
                    "source": "Stooq",
                    "source_url": source_urls.get(asset_id, ""),
                    "data_version": data_version,
                }
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("date", "asset_id", "close", "source", "source_url", "data_version"),
        )
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: (row["date"], row["asset_id"])))
    return output_path


def write_stooq_normalized_csv_from_files(
    raw_paths_by_asset: Mapping[str, Path],
    output_path: Path,
    data_version: str,
    source_urls: Mapping[str, str],
) -> Path:
    """Normalize cached Stooq raw CSV files into the local historical CSV shape."""

    return write_stooq_normalized_csv(
        raw_csv_by_asset={
            asset_id: path.read_text(encoding="utf-8")
            for asset_id, path in raw_paths_by_asset.items()
        },
        output_path=output_path,
        data_version=data_version,
        source_urls=source_urls,
    )


def run_stooq_etf_momentum_research(config: StooqResearchConfig) -> Report:
    """Run equal-weight and momentum research on a local normalized Stooq CSV."""

    base_source = StooqHistoricalDataSource(path=config.data_path, asset_ids=config.asset_ids)
    available_times = _complete_times(config.data_path, config.asset_ids)
    data_file_hash = _file_hash(config.data_path)
    config_summary = config.as_summary(base_source.data_version, data_file_hash)
    config_hash = stable_config_hash(config_summary)

    segments = {
        "train": (config.train_start, config.train_end),
        "validation": (config.validation_start, config.validation_end),
        "test": (config.test_start, config.test_end),
    }
    metrics: dict[str, float] = {}
    segment_payload: dict[str, dict[str, object]] = {}

    for segment_name, (start_text, end_text) in segments.items():
        start = _parse_utc_date(start_text)
        end = _parse_utc_date(end_text)
        decision_times = _decision_times(
            available_times,
            start,
            end,
            config.lookback_observations,
        )
        equal_weight = _run_stooq_segment(
            config=config,
            data_source=base_source,
            signal_model=EqualWeightSignal(),
            decision_times=decision_times,
            start=start,
            end=end,
            segment_name=segment_name,
            strategy_name="equal_weight",
            data_version=base_source.data_version,
        )
        momentum = _run_stooq_segment(
            config=config,
            data_source=TrailingReturnFeatureDataSource(
                base=base_source,
                available_times=available_times,
                lookback_observations=config.lookback_observations,
                feature_name=f"momentum_{config.lookback_observations}",
            ),
            signal_model=MomentumSignal(
                feature_name=f"momentum_{config.lookback_observations}",
                top_n=config.top_n,
            ),
            decision_times=decision_times,
            start=start,
            end=end,
            segment_name=segment_name,
            strategy_name="momentum",
            data_version=base_source.data_version,
        )
        _add_segment_metrics(metrics, segment_name, equal_weight, momentum, len(decision_times))
        segment_payload[segment_name] = {
            "start": start_text,
            "end": end_text,
            "decision_count": len(decision_times),
        }

    run_id = f"stooq-etf-momentum-{config.start.replace('-', '')}-{config.end.replace('-', '')}"
    payload = {
        "run_id": run_id,
        "metadata": {
            "git_commit": current_git_commit(),
            "config_hash": config_hash,
            "data_file_hash": data_file_hash,
            "data_version": base_source.data_version,
            "seed": config.seed,
        },
        "config_summary": config_summary,
        "sample_splits": segment_payload,
        "metrics": metrics,
        "notes": [
            "Stooq v1 uses local normalized CSV only; no runtime network access in snapshots.",
            "Execution keeps the current next-calendar-day assumption and skips dates "
            "without next-day prices.",
        ],
    }
    markdown = _stooq_research_markdown(payload)
    run_dir = config.reports_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / f"{run_id}.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (run_dir / f"{run_id}.md").write_text(markdown, encoding="utf-8")
    return Report(run_id=run_id, text=markdown, metrics=metrics)


def load_stooq_research_config(path: Path) -> StooqResearchConfig:
    """Load a commit-safe TOML file into the typed Stooq research config."""

    core_config = load_core_config(path)
    params = core_config.parameters
    return StooqResearchConfig(
        data_path=Path(_param(params, "data_path", "data/processed/stooq_etf_eod.csv")),
        reports_dir=Path(_param(params, "reports_dir", "reports")),
        asset_ids=core_config.asset_ids,
        start=core_config.start,
        end=core_config.end,
        train_start=_param(params, "train_start", "2015-01-01"),
        train_end=_param(params, "train_end", "2022-01-01"),
        validation_start=_param(params, "validation_start", "2022-01-01"),
        validation_end=_param(params, "validation_end", "2024-01-01"),
        test_start=_param(params, "test_start", "2024-01-01"),
        test_end=_param(params, "test_end", core_config.end),
        lookback_observations=int(_param(params, "lookback_observations", "20")),
        top_n=int(_param(params, "top_n", "1")),
        initial_cash=float(_param(params, "initial_cash", "10000.0")),
        fixed_commission=float(_param(params, "fixed_commission", "1.0")),
        proportional_commission_rate=float(
            _param(params, "proportional_commission_rate", "0.0005")
        ),
        slippage_rate=float(_param(params, "slippage_rate", "0.001")),
        seed=core_config.seed,
    )


def _fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "elvquant-core/0.1 research data downloader"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
    if not isinstance(raw, bytes):
        raise TypeError("Stooq response body must be bytes")
    return raw.decode("utf-8")


def _ensure_stooq_csv(text: str, asset_id: str) -> None:
    first_line = text.splitlines()[0] if text.splitlines() else ""
    if not first_line.startswith("Date,"):
        raise ValueError(f"Stooq download for {asset_id} did not return CSV")


def _required(
    row: Mapping[str, str | None],
    column: str,
    asset_id: str,
    row_number: int,
) -> str:
    value = row.get(column)
    if value is None or not value.strip():
        raise ValueError(f"Stooq CSV for {asset_id} missing {column} at row {row_number}")
    return value.strip()


def _run_stooq_segment(
    config: StooqResearchConfig,
    data_source: DataSource,
    signal_model: SignalModel,
    decision_times: tuple[datetime, ...],
    start: datetime,
    end: datetime,
    segment_name: str,
    strategy_name: str,
    data_version: str,
) -> BacktestResult:
    backtester = SimpleBacktester(
        data_source=data_source,
        signal_model=signal_model,
        portfolio_constructor=SimplePortfolioConstructor(),
        risk_manager=BasicRiskManager(),
        execution_simulator=SimpleExecutionSimulator(
            cost_model=CompositeCostModel(
                (
                    FixedCommissionCostModel(config.fixed_commission),
                    ProportionalCommissionCostModel(config.proportional_commission_rate),
                    SlippageCostModel(config.slippage_rate),
                )
            )
        ),
        ledger=SimpleAccountingLedger(),
        decision_times=decision_times,
        initial_cash=config.initial_cash,
    )
    return backtester.run(
        start=start,
        end=end,
        config={
            "seed": config.seed,
            "provider": "stooq",
            "data_source": "stooq_normalized_csv",
            "data_version": data_version,
            "segment": segment_name,
            "strategy": strategy_name,
            "lookback_observations": str(config.lookback_observations),
            "top_n": str(config.top_n),
        },
    )


def _add_segment_metrics(
    metrics: dict[str, float],
    segment_name: str,
    equal_weight: BacktestResult,
    momentum: BacktestResult,
    decision_count: int,
) -> None:
    prefix = f"{segment_name}_"
    metrics[f"{prefix}decision_count"] = float(decision_count)
    metrics[f"{prefix}equal_weight_net_value"] = equal_weight.metrics["net_value"]
    metrics[f"{prefix}momentum_net_value"] = momentum.metrics["net_value"]
    metrics[f"{prefix}equal_weight_total_return"] = equal_weight.metrics["total_return"]
    metrics[f"{prefix}momentum_total_return"] = momentum.metrics["total_return"]
    metrics[f"{prefix}momentum_minus_equal_weight_return"] = (
        momentum.metrics["total_return"] - equal_weight.metrics["total_return"]
    )
    metrics[f"{prefix}momentum_max_drawdown"] = momentum.metrics["max_drawdown"]
    metrics[f"{prefix}momentum_turnover"] = momentum.metrics["turnover"]
    metrics[f"{prefix}momentum_total_cost"] = momentum.metrics["total_cost"]


def _complete_times(path: Path, asset_ids: tuple[AssetId, ...]) -> tuple[datetime, ...]:
    assets_by_time: dict[datetime, set[str]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            as_of = _parse_utc_date(row["date"])
            assets_by_time.setdefault(as_of, set()).add(row["asset_id"])
    required_assets = set(asset_ids)
    return tuple(
        sorted(
            as_of
            for as_of, present_assets in assets_by_time.items()
            if required_assets.issubset(present_assets)
        )
    )


def _decision_times(
    available_times: tuple[datetime, ...],
    start: datetime,
    end: datetime,
    lookback_observations: int,
) -> tuple[datetime, ...]:
    available_set = set(available_times)
    return tuple(
        as_of
        for index, as_of in enumerate(available_times)
        if start <= as_of < end
        and index >= lookback_observations
        and as_of + timedelta(days=1) in available_set
    )


def _parse_utc_date(value: str) -> datetime:
    return datetime.combine(datetime.strptime(value, "%Y-%m-%d").date(), time.min, tzinfo=UTC)


def _file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()[:12]


def _stooq_research_markdown(payload: Mapping[str, object]) -> str:
    metadata = payload["metadata"]
    metrics = payload["metrics"]
    sample_splits = payload["sample_splits"]
    config_summary = payload["config_summary"]
    if not isinstance(metadata, Mapping):
        raise TypeError("metadata must be a mapping")
    if not isinstance(metrics, Mapping):
        raise TypeError("metrics must be a mapping")
    if not isinstance(sample_splits, Mapping):
        raise TypeError("sample_splits must be a mapping")
    if not isinstance(config_summary, Mapping):
        raise TypeError("config_summary must be a mapping")

    lines = [f"# {payload['run_id']}", "", "## Metadata"]
    lines.extend(f"- {key}: {value}" for key, value in metadata.items())
    lines.extend(["", "## Sample Splits"])
    for name, split in sample_splits.items():
        if not isinstance(split, Mapping):
            raise TypeError("split must be a mapping")
        lines.append(
            f"- {name}: {split['start']} to {split['end']} "
            f"({split['decision_count']} decisions)"
        )
    lines.extend(["", "## Cost Assumptions"])
    for key in ("fixed_commission", "proportional_commission_rate", "slippage_rate"):
        lines.append(f"- {key}: {config_summary[key]}")
    lines.extend(["", "## Metrics"])
    lines.extend(f"- {key}: {value:.6f}" for key, value in metrics.items())
    lines.extend(["", "## Notes"])
    notes = payload["notes"]
    if isinstance(notes, list):
        lines.extend(f"- {note}" for note in notes)
    lines.append("")
    return "\n".join(lines)


def _param(params: Mapping[str, str], key: str, default: str) -> str:
    return params.get(key, default)


__all__ = [
    "StooqResearchConfig",
    "StooqHistoricalDataSource",
    "cache_stooq_daily_csv",
    "load_stooq_research_config",
    "run_stooq_etf_momentum_research",
    "stooq_daily_csv_url",
    "write_stooq_normalized_csv",
    "write_stooq_normalized_csv_from_files",
]
