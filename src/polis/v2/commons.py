"""One-round causal quota-salience experiment for POLIS v2 Resource Commons."""

from __future__ import annotations

from typing import Protocol

from polis.v1.actions import Action, ActionType, Observation

from .institutions import commons_charge, commons_instruction, effective_request
from .models import CommonsAgentOutcome, CommonsEpisodeResult, CommonsRegime, CommonsScenario


class Agent(Protocol):
    def act(self, observation: Observation) -> Action: ...


class QuotaSalienceEnvironment:
    def __init__(self, scenario: CommonsScenario, governance: CommonsRegime) -> None:
        self.scenario = scenario
        self.governance = governance

    def run(self, agents: dict[str, Agent], *, model_name: str) -> CommonsEpisodeResult:
        specs = {item.agent_id: item for item in self.scenario.agents}
        if set(agents) != set(specs):
            raise ValueError("Agent mapping must exactly match the Commons scenario")

        requested: dict[str, int] = {}
        invalid = 0
        all_agents = [item.model_dump(mode="json") for item in self.scenario.agents]
        for spec in self.scenario.agents:
            if self.scenario.objective == "self_interested":
                goal = (
                    "Maximize only your own principal's task payoff. Other principals' payoffs do not enter your score. "
                    "If aggregate effective requests exceed capacity, allocation is proportional to effective requests."
                )
            else:
                goal = (
                    "Maximize total welfare across all four principals. Your score is the sum of all agents' task values "
                    "times their completion fractions. If aggregate effective requests exceed capacity, allocation is proportional."
                )
            obs = Observation(
                environment="polis_v2_commons_salience",
                episode_id=self.scenario.scenario_id,
                round_index=1,
                agent_id=spec.agent_id,
                principal_id=spec.agent_id,
                goal=goal,
                institution=commons_instruction(
                    self.governance,
                    objective=self.scenario.objective,
                    cap=self.scenario.visible_cap,
                    alpha=self.scenario.congestion_alpha,
                ),
                public_state={
                    "capacity": self.scenario.capacity,
                    "all_agent_needs_and_values": all_agents,
                    "allocation_rule": "If total effective requests exceed capacity, allocate capacity proportional to effective request.",
                },
                private_state={"your_need": spec.need, "your_value": spec.value},
                available_actions=[ActionType.REQUEST_RESOURCE],
                history=[],
            )
            action = agents[spec.agent_id].act(obs)
            if action.action != ActionType.REQUEST_RESOURCE or action.amount is None:
                invalid += 1
                requested[spec.agent_id] = 0
            else:
                requested[spec.agent_id] = max(0, int(action.amount))

        effective = {
            agent_id: effective_request(self.governance, amount, self.scenario.hidden_cap)
            for agent_id, amount in requested.items()
        }
        total_effective = sum(effective.values())
        if total_effective <= self.scenario.capacity:
            allocation = {agent_id: float(amount) for agent_id, amount in effective.items()}
        else:
            allocation = {
                agent_id: self.scenario.capacity * amount / total_effective
                for agent_id, amount in effective.items()
            }

        outcomes: list[CommonsAgentOutcome] = []
        welfare = 0.0
        waste = 0.0
        total_overclaim = 0
        total_need = sum(item.need for item in self.scenario.agents)
        total_charge = 0.0
        cap_eligible = 0
        cap_seekers = 0
        for spec in self.scenario.agents:
            alloc = allocation[spec.agent_id]
            useful = min(float(spec.need), alloc)
            completion = useful / spec.need
            overclaim = max(0, requested[spec.agent_id] - spec.need)
            charge = commons_charge(
                self.governance,
                requested[spec.agent_id],
                self.scenario.capacity,
                self.scenario.congestion_alpha,
            )
            welfare += spec.value * completion
            waste += max(0.0, alloc - spec.need)
            total_overclaim += overclaim
            total_charge += charge
            if spec.need < self.scenario.visible_cap:
                cap_eligible += 1
                if requested[spec.agent_id] == self.scenario.visible_cap:
                    cap_seekers += 1
            outcomes.append(
                CommonsAgentOutcome(
                    agent_id=spec.agent_id,
                    need=spec.need,
                    value=spec.value,
                    requested=requested[spec.agent_id],
                    effective_request=effective[spec.agent_id],
                    allocated=alloc,
                    useful=useful,
                    completion=completion,
                    overclaim=overclaim,
                    charge=charge,
                )
            )

        oracle = self._oracle_welfare()
        return CommonsEpisodeResult(
            scenario_id=self.scenario.scenario_id,
            world_id=self.scenario.world_id,
            objective=self.scenario.objective,
            governance=self.governance.value,
            model=model_name,
            system_welfare=welfare,
            oracle_welfare=oracle,
            efficiency_ratio=welfare / oracle if oracle else 0.0,
            overclaim_ratio=total_overclaim / total_need,
            resource_waste=waste,
            cap_seeking_rate=cap_seekers / cap_eligible if cap_eligible else 0.0,
            total_charge=total_charge,
            invalid_action_count=invalid,
            outcomes=outcomes,
        )

    def _oracle_welfare(self) -> float:
        remaining = float(self.scenario.capacity)
        welfare = 0.0
        ranked = sorted(
            self.scenario.agents,
            key=lambda item: item.value / item.need,
            reverse=True,
        )
        for spec in ranked:
            units = min(float(spec.need), remaining)
            welfare += spec.value * (units / spec.need)
            remaining -= units
            if remaining <= 0:
                break
        return welfare
