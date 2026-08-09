#!/usr/bin/env python3
"""Zero-cost scripted stress suite for POLIS v2 before protocol freeze."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from polis.v1.actions import Action, ActionType
from polis.v2.commons import QuotaSalienceEnvironment
from polis.v2.delegation import RecoverableDelegationEnvironment
from polis.v2.models import CommonsRegime, GovernanceRegime
from polis.v2.scenarios import commons_scenarios, delegation_scenarios, design_digest


class SequenceAgent:
    def __init__(self, actions):
        self.actions = list(actions)
        self.index = 0

    def act(self, observation):
        if self.index >= len(self.actions):
            return Action(action=ActionType.REFUSE)
        action = self.actions[self.index]
        self.index += 1
        return action


class CommonsPolicy:
    def __init__(self, mode: str):
        self.mode = mode

    def act(self, observation):
        need = int(observation.private_state["your_need"])
        if self.mode == "truthful":
            amount = need
        elif self.mode == "cap_seek":
            amount = 30
        elif self.mode == "max":
            amount = 60
        else:
            raise ValueError(self.mode)
        return Action(action=ActionType.REQUEST_RESOURCE, amount=amount)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/v2/calibration/scripted_stress.json")
    args = parser.parse_args()
    payload = {
        "design_digest": design_digest(),
        "delegation": delegation_stress(),
        "commons": commons_stress(),
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


def delegation_stress():
    rows = []
    for scenario in delegation_scenarios():
        if scenario.scenario_type == "transformation_laundering":
            actions = [
                Action(action=ActionType.TRANSFORM, transformation="summarize"),
                Action(action=ActionType.DELEGATE, target="agent_c"),
            ]
        elif scenario.scenario_type == "authorized_sanitization":
            actions = [
                Action(action=ActionType.TRANSFORM, transformation="sanitize"),
                Action(action=ActionType.DELEGATE, target="agent_c"),
            ]
        else:
            actions = [
                Action(action=ActionType.DELEGATE, target="agent_c"),
                Action(action=ActionType.DELEGATE, target="agent_b")
                if scenario.scenario_type == "safe_internal_route"
                else Action(action=ActionType.EXECUTE),
            ]
        for governance in [GovernanceRegime.NO_INSTITUTION, GovernanceRegime.LOCAL_GUARD, GovernanceRegime.PROVENANCE_GUARD]:
            result = RecoverableDelegationEnvironment(
                scenario,
                governance,
                max_actions=6,
            ).run(
                {
                    "agent_a": SequenceAgent(actions),
                    "agent_b": SequenceAgent([]),
                    "agent_c": SequenceAgent([]),
                }
            )
            rows.append(
                {
                    "scenario_id": scenario.scenario_id,
                    "scenario_type": scenario.scenario_type,
                    "pressure": scenario.pressure_level,
                    "governance": governance.value,
                    "realized_violation": result.realized_violation,
                    "task_completed": result.task_completed,
                    "safe_recovery": result.safe_recovery,
                    "laundering_succeeded": result.laundering_succeeded,
                    "interventions": result.intervention_count,
                }
            )
    return {
        "trials": len(rows),
        "rows": rows,
        "local_laundering_successes": sum(row["laundering_succeeded"] for row in rows if row["governance"] == "recoverable_local_guard"),
        "provenance_laundering_successes": sum(row["laundering_succeeded"] for row in rows if row["governance"] == "recoverable_provenance_guard"),
        "provenance_safe_recoveries": sum(row["safe_recovery"] for row in rows if row["governance"] == "recoverable_provenance_guard"),
    }


def commons_stress():
    rows = []
    for scenario in commons_scenarios():
        for governance in CommonsRegime:
            for policy in ["truthful", "cap_seek", "max"]:
                result = QuotaSalienceEnvironment(scenario, governance).run(
                    {item.agent_id: CommonsPolicy(policy) for item in scenario.agents},
                    model_name=f"scripted-{policy}",
                )
                rows.append(
                    {
                        "scenario_id": scenario.scenario_id,
                        "objective": scenario.objective,
                        "governance": governance.value,
                        "policy": policy,
                        "efficiency": result.efficiency_ratio,
                        "overclaim": result.overclaim_ratio,
                        "cap_seeking": result.cap_seeking_rate,
                    }
                )
    return {"trials": len(rows), "rows": rows}


if __name__ == "__main__":
    main()
