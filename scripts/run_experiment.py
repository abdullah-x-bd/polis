#!/usr/bin/env python3
"""Run one POLIS unsafe-delegation regime."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

from polis.evaluation import compute_metrics
from polis.io import load_json, write_run


def _load_experiment_factory():
    path = Path(__file__).resolve().parents[1] / "experiments" / "unsafe_delegation.py"
    spec = importlib.util.spec_from_file_location("unsafe_delegation", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load unsafe_delegation experiment")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_environment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to a JSON configuration file")
    parser.add_argument("--output", default="results/runs", help="Directory for run outputs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_json(args.config)
    build_environment = _load_experiment_factory()
    environment = build_environment(config)
    outcomes = environment.run(
        trials=int(config.get("trials", 100)),
        restricted_share=float(config.get("restricted_share", 0.5)),
    )
    metrics = compute_metrics(outcomes)
    run_dir = write_run(args.output, metrics, outcomes, config)
    print(f"Wrote {metrics.trials} trials to {run_dir}")
    print(metrics.to_dict())


if __name__ == "__main__":
    main()
