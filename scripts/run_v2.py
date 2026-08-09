#!/usr/bin/env python3
"""Run or inspect any POLIS v2 study."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from polis.v1.providers.budget import BudgetTracker
from polis.v1.providers.cache import FileResponseCache
from polis.v1.providers.openrouter import OpenRouterProvider
from polis.v2.live import build_episode_specs, run_study, shard_specs
from polis.v2.protocol import load_protocol
from polis.v2.scenarios import design_digest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", default="configs/v2_protocol.json")
    parser.add_argument(
        "--study",
        required=True,
        choices=["delegation_main", "wording_robustness", "heterogeneous", "commons_salience", "frontier"],
    )
    parser.add_argument("--output", default="results/v2/live")
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--run-id")
    parser.add_argument("--max-cost-usd", type=float, default=4.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    protocol = load_protocol(args.protocol)
    all_specs = build_episode_specs(protocol, args.study)
    specs = shard_specs(all_specs, args.shard_index, args.shard_count)
    plan = {
        "protocol_version": protocol.protocol_version,
        "status": protocol.status,
        "study_fingerprint": protocol.study_fingerprint(),
        "design_digest": design_digest(),
        "study": args.study,
        "all_episodes": len(all_specs),
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "shard_episodes": len(specs),
        "maximum_shard_calls": sum(item.maximum_calls for item in specs),
        "models_or_compositions": sorted({item.composition_name for item in specs}),
        "governance": sorted({item.governance for item in specs}),
    }
    print(json.dumps(plan, indent=2))
    if args.dry_run:
        return

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    budget = BudgetTracker(
        max_cost_usd=args.max_cost_usd,
        ledger_path=output / f"ledger-{args.study}-s{args.shard_index}of{args.shard_count}.jsonl",
        reserve_per_request_usd=0.01,
    )
    provider = OpenRouterProvider(
        cache=FileResponseCache(output / "cache"),
        budget=budget,
        max_tokens=protocol.max_tokens,
        temperature=protocol.temperature,
    )
    manifest = run_study(
        protocol=protocol,
        provider=provider,
        study=args.study,
        output_dir=output,
        shard_index=args.shard_index,
        shard_count=args.shard_count,
        run_id=args.run_id,
    )
    print(json.dumps(manifest.model_dump(mode="json"), indent=2))
    print(f"Recorded spend for this ledger: ${budget.spent_usd:.6f}")


if __name__ == "__main__":
    main()
