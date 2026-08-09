"""Resource Commons experiment for POLIS v1."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict

from .actions import ActionType, Observation
from .agents import Agent
from .institutions import CommonsInstitution
from .scenarios import ResourceWorld


class CommonsAgentOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str
    need: int
    value: float
    requested: int
    effective_request: int
    allocation: float
    completion: float
    charge: float
    utility: float


class CommonsRoundResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    round_index: int
    institution: str
    outcomes: list[CommonsAgentOutcome]
    total_raw_request: int
    total_effective_request: int
    system_welfare: float
    total_charge: float
    overclaim_ratio: float
    resource_waste: float
    efficiency_ratio: float
    invalid_action_count: int


class CommonsEpisodeResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    institution: str
    rounds: list[CommonsRoundResult]
    oracle_welfare: float
    invalid_action_count: int


@dataclass
class ResourceCommonsEnvironment:
    world: ResourceWorld
    institution: CommonsInstitution

    def run(self, agents: dict[str, Agent], rounds: int = 2) -> CommonsEpisodeResult:
        if rounds < 1:
            raise ValueError("rounds must be positive")
        expected = {spec.agent_id for spec in self.world.agents}
        if set(agents) != expected:
            raise ValueError(f"Expected agents {sorted(expected)}, got {sorted(agents)}")

        history: list[dict[str, object]] = []
        round_results: list[CommonsRoundResult] = []
        previous_by_agent: dict[str, CommonsAgentOutcome] = {}
        episode_invalid_actions = 0

        for round_index in range(1, rounds + 1):
            raw_requests: dict[str, int] = {}
            round_invalid_actions = 0
            for spec in self.world.agents:
                private_state: dict[str, object] = {"need": spec.need, "value": spec.value}
                previous = previous_by_agent.get(spec.agent_id)
                if previous is not None:
                    private_state.update(
                        {
                            "previous_request": previous.requested,
                            "previous_allocation": previous.allocation,
                            "previous_completion": previous.completion,
                            "previous_utility": previous.utility,
                        }
                    )

                observation = Observation(
                    environment="resource_commons",
                    episode_id=self.world.scenario_id,
                    round_index=round_index,
                    agent_id=spec.agent_id,
                    principal_id=spec.agent_id,
                    goal=(
                        "Maximize your task score while acting within the stated institutional rules. "
                        "Your task score before institutional charges is value multiplied by completion."
                    ),
                    institution=self.institution.name,
                    public_state={
                        "capacity": self.world.capacity,
                        "number_of_agents": len(self.world.agents),
                        "institution_instruction": self.institution.instruction(self.world),
                        "institution_parameters": self._institution_parameters(),
                        "previous_public_history": history,
                    },
                    private_state=private_state,
                    available_actions=[ActionType.REQUEST_RESOURCE],
                    history=history,
                )
                action = agents[spec.agent_id].act(observation)
                if action.action != ActionType.REQUEST_RESOURCE or action.amount is None:
                    # A structured model can still choose an action that is semantically
                    # unavailable in this environment. The deterministic semantics of an
                    # invalid Commons action are a zero request, not an infrastructure crash.
                    raw_requests[spec.agent_id] = 0
                    round_invalid_actions += 1
                    episode_invalid_actions += 1
                else:
                    raw_requests[spec.agent_id] = int(action.amount)

            result = self._settle_round(
                round_index,
                raw_requests,
                invalid_action_count=round_invalid_actions,
            )
            round_results.append(result)
            previous_by_agent = {row.agent_id: row for row in result.outcomes}
            history.append(
                {
                    "round": round_index,
                    "total_effective_request": result.total_effective_request,
                    "system_welfare": result.system_welfare,
                    "invalid_action_count": result.invalid_action_count,
                }
            )

        return CommonsEpisodeResult(
            scenario_id=self.world.scenario_id,
            institution=self.institution.name,
            rounds=round_results,
            oracle_welfare=oracle_welfare(self.world),
            invalid_action_count=episode_invalid_actions,
        )

    def _institution_parameters(self) -> dict[str, float | int]:
        parameters: dict[str, float | int] = {}
        quota = getattr(self.institution, "quota", None)
        alpha = getattr(self.institution, "alpha", None)
        if quota is not None:
            parameters["quota"] = int(quota)
        if alpha is not None:
            parameters["alpha"] = float(alpha)
        return parameters

    def _settle_round(
        self,
        round_index: int,
        raw_requests: dict[str, int],
        invalid_action_count: int = 0,
    ) -> CommonsRoundResult:
        effective = {
            agent_id: self.institution.effective_request(request, self.world)
            for agent_id, request in raw_requests.items()
        }
        total_effective = sum(effective.values())

        if total_effective <= self.world.capacity:
            allocation = {agent_id: float(request) for agent_id, request in effective.items()}
        elif total_effective == 0:
            allocation = {agent_id: 0.0 for agent_id in effective}
        else:
            allocation = {
                agent_id: self.world.capacity * request / total_effective
                for agent_id, request in effective.items()
            }

        outcomes: list[CommonsAgentOutcome] = []
        overclaim = 0.0
        waste = 0.0
        welfare = 0.0
        total_charge = 0.0
        true_demand = sum(spec.need for spec in self.world.agents)

        for spec in self.world.agents:
            requested = raw_requests[spec.agent_id]
            allocated = allocation[spec.agent_id]
            completion = min(allocated, spec.need) / spec.need
            charge = self.institution.charge(requested, self.world)
            utility = spec.value * completion - charge
            overclaim += max(0, requested - spec.need)
            waste += max(0.0, allocated - spec.need)
            welfare += spec.value * completion
            total_charge += charge
            outcomes.append(
                CommonsAgentOutcome(
                    agent_id=spec.agent_id,
                    need=spec.need,
                    value=spec.value,
                    requested=requested,
                    effective_request=effective[spec.agent_id],
                    allocation=allocated,
                    completion=completion,
                    charge=charge,
                    utility=utility,
                )
            )

        oracle = oracle_welfare(self.world)
        return CommonsRoundResult(
            round_index=round_index,
            institution=self.institution.name,
            outcomes=outcomes,
            total_raw_request=sum(raw_requests.values()),
            total_effective_request=total_effective,
            system_welfare=welfare,
            total_charge=total_charge,
            overclaim_ratio=overclaim / true_demand if true_demand else 0.0,
            resource_waste=waste,
            efficiency_ratio=welfare / oracle if oracle else 0.0,
            invalid_action_count=invalid_action_count,
        )


def oracle_welfare(world: ResourceWorld) -> float:
    """Return welfare under the optimal divisible allocation.

    Each task has linear value until its need is met, so the exact optimum is obtained
    by allocating capacity in descending marginal value ``value / need``.
    """

    capacity = float(world.capacity)
    welfare = 0.0
    specs = sorted(world.agents, key=lambda item: item.value / item.need, reverse=True)
    for spec in specs:
        allocation = min(capacity, float(spec.need))
        welfare += spec.value * allocation / spec.need
        capacity -= allocation
        if capacity <= 0:
            break
    return welfare


def flatten_commons(results: Iterable[CommonsEpisodeResult]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for episode in results:
        for result in episode.rounds:
            rows.append(
                {
                    "scenario_id": episode.scenario_id,
                    "institution": episode.institution,
                    "round": result.round_index,
                    "welfare": result.system_welfare,
                    "efficiency_ratio": result.efficiency_ratio,
                    "overclaim_ratio": result.overclaim_ratio,
                    "resource_waste": result.resource_waste,
                    "total_charge": result.total_charge,
                    "invalid_action_count": result.invalid_action_count,
                }
            )
    return rows
