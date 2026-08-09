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
        else:
            raise ValueError(f"Unknown resource strategy: {self.strategy}")

        return Action(
            action=ActionType.REQUEST_RESOURCE,
            amount=amount,
            justification=f"scripted:{self.strategy}",
        )

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
