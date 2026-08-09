#!/usr/bin/env python3
"""Zero-cost calibration sweep for POLIS v1 Resource Commons."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean

from polis.v1.agents import ScriptedAgent
from polis.v1.institutions import (
    CongestionPricingInstitution,
    HardQuotaInstitution,
    NoCommonsInstitution,
    PromptCommonsInstitution,
)
from polis.v1.loaders import load_resource_worlds
from polis.v1.resource_commons import ResourceCommonsEnvironment


def agents_for(world, profile: str, seed: int):
    if profile == "truthful":
        strategies = ["truthful"] * 4
    elif profile == "greedy":
        strategies = ["greedy"] * 4
    elif profile == "mixed":
        strategies = ["truthful", "greedy", "max_requester", "adaptive_greedy"]
    else:
        raise ValueError(profile)
    return {
        spec.agent_id: ScriptedAgent(spec.agent_id, spec.agent_id, strategies[i], seed + i)
        for i, spec in enumerate(world.agents)
    }


def evaluate(institution, worlds, profile: str):
    rows = []
    for index, world in enumerate(worlds):
        episode = ResourceCommonsEnvironment(world, institution).run(
            agents_for(world, profile, 1000 + index), rounds=2
        )
        final = episode.rounds[-1]
        rows.append(final)
    return {
        "institution": institution.name,
        "profile": profile,
        "mean_welfare": mean(row.system_welfare for row in rows),
        "mean_efficiency": mean(row.efficiency_ratio for row in rows),
        "mean_overclaim": mean(row.overclaim_ratio for row in rows),
        "mean_waste": mean(row.resource_waste for row in rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worlds", default="scenarios/resource_commons/v1.json")
    parser.add_argument("--output", default="results/calibration/commons_v1.json")
    args = parser.parse_args()

    worlds = load_resource_worlds(args.worlds)
    mechanisms = [NoCommonsInstitution(), PromptCommonsInstitution()]
    mechanisms.extend(HardQuotaInstitution(quota=q) for q in [20, 25, 30, 35, 40])
    mechanisms.extend(CongestionPricingInstitution(alpha=a) for a in [0.05, 0.10, 0.20, 0.40])

    results = [
        evaluate(mechanism, worlds, profile)
        for profile in ["truthful", "greedy", "mixed"]
        for mechanism in mechanisms
    ]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
