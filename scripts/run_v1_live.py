#!/usr/bin/env python3
"""Run or dry-run the frozen POLIS v1 live-model matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from polis.v1.live import build_plan, run_live_matrix
from polis.v1.protocol import load_protocol
from polis.v1.providers.budget import BudgetTracker
from polis.v1.providers.cache import FileResponseCache
from polis.v1.providers.openrouter import OpenRouterProvider


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", default="configs/v1_live.json")
    parser.add_argument("--mode", choices=["pilot", "full"], default="pilot")
    parser.add_argument("--output", default="results/live")
    parser.add_argument("--model", action="append", dest="models")
    parser.add_argument("--run-id")
    parser.add_argument("--max-cost-usd", type=float)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    protocol = load_protocol(args.protocol)
    plan = build_plan(protocol, args.mode, args.models)

    print("Protocol fingerprint:", protocol.fingerprint())
    print(json.dumps(plan.to_dict(), indent=2))

    if args.dry_run:
        return

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    budget_limit = (
        args.max_cost_usd
        if args.max_cost_usd is not None
        else protocol.inference.max_cost_usd
    )
    budget = BudgetTracker(
        max_cost_usd=budget_limit,
        ledger_path=output / "openrouter_ledger.jsonl",
        reserve_per_request_usd=protocol.inference.reserve_per_request_usd,
    )
    cache = FileResponseCache(output / "cache")
    provider = OpenRouterProvider(
        cache=cache,
        budget=budget,
        max_tokens=protocol.inference.max_tokens,
        temperature=protocol.inference.temperature,
    )

    manifest = run_live_matrix(
        protocol=protocol,
        provider=provider,
        output_dir=output,
        mode=args.mode,
        selected_models=args.models,
        run_id=args.run_id,
    )
    print(json.dumps(manifest.model_dump(mode="json"), indent=2))
    print(f"Cumulative recorded OpenRouter spend: ${budget.spent_usd:.6f}")


if __name__ == "__main__":
    main()
