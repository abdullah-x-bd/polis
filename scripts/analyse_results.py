#!/usr/bin/env python3
"""Combine POLIS run summaries into a compact comparison table."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("results_dir", nargs="?", default="results/runs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.results_dir)
    summaries = sorted(root.glob("*/summary.json"))
    if not summaries:
        raise SystemExit(f"No summary.json files found under {root}")

    rows = []
    for path in summaries:
        with path.open("r", encoding="utf-8") as handle:
            rows.append(json.load(handle)["metrics"])

    output = root / "comparison.csv"
    fields = [
        "regime",
        "trials",
        "rule_evasion_rate",
        "detection_rate",
        "false_positive_rate",
        "useful_performance",
    ]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in rows)

    print(f"Wrote comparison to {output}")
    for row in rows:
        print(
            row["regime"],
            f"evasion={row['rule_evasion_rate']:.3f}",
            f"detection={row['detection_rate']:.3f}",
            f"false_positive={row['false_positive_rate']:.3f}",
            f"useful={row['useful_performance']:.3f}",
        )


if __name__ == "__main__":
    main()
