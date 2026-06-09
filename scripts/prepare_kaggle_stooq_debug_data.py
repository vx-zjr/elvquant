"""Prepare local Stooq-format ETF debug data from the public Kaggle mirror."""

from __future__ import annotations

import os
from pathlib import Path

from qts.stooq import write_stooq_normalized_csv_from_files

DATASET_HANDLE = "borismarjanovic/price-volume-data-for-all-us-stocks-etfs"
DATASET_URL = f"https://www.kaggle.com/datasets/{DATASET_HANDLE}"
ASSETS = ("SPY.US", "QQQ.US", "IWM.US", "TLT.US", "GLD.US")
START = "2015-01-01"
END = "2017-11-10"
DATA_VERSION = f"kaggle-stooq-etf-eod-{START}-{END}-v1"


def main() -> None:
    dataset_root = _dataset_root()
    etf_dir = _etf_dir(dataset_root)
    raw_dir = Path("data/raw/stooq")
    raw_dir.mkdir(parents=True, exist_ok=True)

    raw_paths: dict[str, Path] = {}
    for asset in ASSETS:
        source_path = etf_dir / f"{asset.lower()}.txt"
        output_path = raw_dir / f"{asset.lower().replace('.', '_')}_{START}_{END}.csv"
        _write_filtered_raw(source_path, output_path, START, END)
        raw_paths[asset] = output_path

    normalized_path = write_stooq_normalized_csv_from_files(
        raw_paths_by_asset=raw_paths,
        output_path=Path("data/processed/stooq_etf_eod.csv"),
        data_version=DATA_VERSION,
        source_urls={asset: DATASET_URL for asset in ASSETS},
    )
    print(f"normalized={normalized_path}")
    print(f"data_version={DATA_VERSION}")
    for asset, path in raw_paths.items():
        row_count = sum(1 for _ in path.open(encoding="utf-8")) - 1
        print(f"{asset} raw={path} rows={row_count}")


def _dataset_root() -> Path:
    override = os.environ.get("KAGGLE_STOOQ_DATASET_PATH")
    if override:
        return Path(override).expanduser().resolve()

    try:
        import kagglehub
    except ImportError as exc:
        raise SystemExit(
            "Install the optional data dependency first: "
            'python -m pip install -e ".[data]"'
        ) from exc
    return Path(kagglehub.dataset_download(DATASET_HANDLE))


def _etf_dir(dataset_root: Path) -> Path:
    candidates = (dataset_root / "Data" / "ETFs", dataset_root / "ETFs")
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Could not find ETFs directory under {dataset_root}")


def _write_filtered_raw(source_path: Path, output_path: Path, start: str, end: str) -> None:
    if not source_path.exists():
        raise FileNotFoundError(source_path)
    lines = source_path.read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("Date,"):
        raise ValueError(f"{source_path} is not a Stooq-format daily CSV")

    filtered = [row for row in lines[1:] if start <= row.split(",", 1)[0] <= end]
    if not filtered:
        raise ValueError(f"{source_path} has no rows between {start} and {end}")

    output_path.write_text("\n".join([lines[0], *filtered, ""]), encoding="utf-8")


if __name__ == "__main__":
    main()
