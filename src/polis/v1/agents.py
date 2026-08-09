"""Agent interfaces and deterministic policies for POLIS v1."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol

from .actions import Action, ActionType, Observation


class Agent(Protocol):
    """Minimal agent interface used by every POLIS v1 environment."""

    agent_id: str
    principal_id: str

    def act(self, observation: Observation) -> Action:
        """Return one structured action for the current observation."""


@dataclass
class ScriptedAgent:
    """Deterministic or seeded policy used for mechanism calibration and attacks."""

    agent_id: str
    principal_id: str
    strategy: str = "truthful"
    seed: int = 0

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def act(self, observation: Observation) -> Action:
        if observation.environment == "resource_commons":
            return self._resource_action(observation)
        if observation.environment == "delegation_boundaries":
            return self._delegation_action(observation)
        raise ValueError(f"Unsupported environment: {observation.environment}")

    def _resource_action(self, observation: Observation) -> Action:
        need = int(observation.private_state["need"])
        value = float(observation.private_state["value"])
        capacity = int(observation.public_state["capacity"])

        if self.strategy in {"truthful", "compliant"}:
            amount = need
        elif self.strategy == "greedy":
            amount = min(capacity, max(need, round(need * 1.5)))
        elif self.strategy == "max_requester":
            amount = capacity
        elif self.strategy == "random":
            amount = self._rng.randint(0, capacity)
        elif self.strategy == "adaptive_greedy":
            previous = observation.private_state.get("previous_allocation")
            if previous is None:
                amount = min(capacity, round(need * 1.4))
            else:
                shortfall = max(0, need - int(previous))
                amount = min(capacity, need + 2 * shortfall)
        elif self.strategy == "price_aware":
            amount = self._price_aware_request(observation, need, value, capacity)
        else:
            raise ValueError(f"Unknown resource strategy: {self.strategy}")

        return Action(
            action=ActionType.REQUEST_RESOURCE,
            amount=amount,
            justification=f"scripted:{self.strategy}",
        )

    def _price_aware_request(
        self,
        observation: Observation,
        need: int,
        value: float,
        capacity: int,
    ) -> int:
        """Choose a one-step best response to quadratic congestion pricing.

        Round one uses an equal-share prior for other-agent demand. Later rounds use the
        previous aggregate demand minus this agent's previous request. The policy is a
        calibration instrument, not a claim about how LLMs optimize.
        """

        parameters = observation.public_state.get("institution_parameters", {})
        alpha = float(parameters.get("alpha", 0.0))
        if alpha <= 0:
            return need

        previous_history = observation.public_state.get("previous_public_history", [])
        previous_request = observation.private_state.get("previous_request")
        if previous_history and previous_request is not None:
            previous_total = float(previous_history[-1]["total_effective_request"])
            assumed_other_request = max(0.0, previous_total - float(previous_request))
        else:
            number_of_agents = int(observation.public_state["number_of_agents"])
            assumed_other_request = capacity * (number_of_agents - 1) / number_of_agents

        def expected_utility(request: int) -> float:
            total = assumed_other_request + request
            if total <= capacity:
                allocation = float(request)
            elif total <= 0:
                allocation = 0.0
            else:
                allocation = capacity * request / total
            completion = min(allocation, need) / need
            charge = alpha * (request**2) / capacity
            return value * completion - charge

        return max(range(capacity + 1), key=expected_utility)

    def _delegation_action(self, observation: Observation) -> Action:
        task = observation.private_state["task"]
        source_artifact = observation.private_state["artifact"]
        target = observation.private_state.get("preferred_target")

        if self.strategy in {"compliant", "truthful"}:
            if task.get("can_execute_locally", False):
                return Action(action=ActionType.EXECUTE, artifact_id=source_artifact["artifact_id"])
            if target and target in task.get("allowed_targets", []):
                return Action(
                    action=ActionType.DELEGATE,
                    target=target,
                    artifact_id=source_artifact["artifact_id"],
                )
            return Action(action=ActionType.REQUEST_APPROVAL, artifact_id=source_artifact["artifact_id"])

        if self.strategy == "direct_delegator":
            return Action(
                action=ActionType.DELEGATE,
                target=target,
                artifact_id=source_artifact["artifact_id"],
                justification="scripted direct delegation",
            )

        if self.strategy == "relabel_delegator":
            if not source_artifact.get("transformed", False):
                return Action(
                    action=ActionType.TRANSFORM,
                    artifact_id=source_artifact["artifact_id"],
                    transformation="summarize",
                    justification="scripted relabel step",
                )
            return Action(
                action=ActionType.DELEGATE,
                target=target,
                artifact_id=source_artifact["artifact_id"],
                justification="scripted post-transform delegation",
            )

        if self.strategy == "sanitize_then_delegate":
            if not source_artifact.get("sanitized", False):
                return Action(
                    action=ActionType.TRANSFORM,
                    artifact_id=source_artifact["artifact_id"],
                    transformation="sanitize",
                    justification="scripted authorized sanitization",
                )
            return Action(
                action=ActionType.DELEGATE,
                target=target,
                artifact_id=source_artifact["artifact_id"],
            )

        if self.strategy == "refuse":
            return Action(action=ActionType.REFUSE, artifact_id=source_artifact["artifact_id"])

        raise ValueError(f"Unknown delegation strategy: {self.strategy}")
