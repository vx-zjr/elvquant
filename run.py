from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from qts.reports import run_structured_workflow


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run elvquant core workflows.")
    parser.add_argument("workflow", nargs="?", default="synthetic_demo")
    parser.add_argument("--json", action="store_true", help="emit structured JSON payload")
    args = parser.parse_args(argv)

    report = run_structured_workflow(args.workflow)
    if args.json:
        print(json.dumps(report.to_payload(), indent=2, sort_keys=True))
        return
    print(f"run_id: {report.run_id}")
    for key, value in report.metrics.items():
        print(f"{key}: {value:.6f}")


if __name__ == "__main__":
    main()
