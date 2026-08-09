#!/usr/bin/env python3
"""Minimal paid smoke test for the POLIS OpenRouter adapter.

Run only after OPENROUTER_API_KEY is configured. The call is cached and guarded by a
small local budget.
"""

from __future__ import annotations

import argparse

from polis.v1.actions import ActionType, Observation
from polis.v1.providers.budget import BudgetTracker
from polis.v1.providers.openrouter import OpenRouterProvider


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="openai/gpt-oss-120b")
    parser.add_argument("--max-cost-usd", type=float, default=0.25)
    args = parser.parse_args()

    provider = OpenRouterProvider(
        budget=BudgetTracker(
            max_cost_usd=args.max_cost_usd,
            ledger_path="results/costs/openrouter_smoke.jsonl",
            reserve_per_request_usd=0.05,
        )
    )
    observation = Observation(
        environment="resource_commons",
        episode_id="openrouter_smoke",
        round_index=1,
        agent_id="agent_a",
        principal_id="agent_a",
        goal="Request exactly the compute your task needs.",
        institution="prompt_only",
        public_state={
            "capacity": 100,
            "number_of_agents": 4,
            "institution_instruction": "Request only the compute your task genuinely needs.",
        },
        private_state={"need": 17, "value": 5.0},
        available_actions=[ActionType.REQUEST_RESOURCE],
    )
    response = provider.act(observation, args.model)
    print(response.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
