"""Configuration and output helpers."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .evaluation import Metrics
from .models import TrialOutcome


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Configuration must contain a JSON object")
    return data


def write_run(
    output_dir: str | Path,
    metrics: Metrics,
    outcomes: list[TrialOutcome],
    config: dict[str, Any],
) -> Path:
    run_dir = Path(output_dir) / metrics.regime
    run_dir.mkdir(parents=True, exist_ok=True)

    with (run_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump({"config": config, "metrics": metrics.to_dict()}, handle, indent=2)

    with (run_dir / "interactions.jsonl").open("w", encoding="utf-8") as handle:
        for outcome in outcomes:
            handle.write(json.dumps(outcome.to_dict()) + "\n")

    with (run_dir / "trials.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "trial_id",
                "regime",
                "task_kind",
                "violation_attempted",
                "violation_detected",
                "prohibited_task_completed",
                "legitimate_task_completed",
                "legitimate_action_blocked",
            ],
        )
        writer.writeheader()
        for outcome in outcomes:
            data = outcome.to_dict()
            writer.writerow({key: data[key] for key in writer.fieldnames})

    return run_dir
