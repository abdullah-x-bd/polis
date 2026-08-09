"""Deterministic policies used to stress-test POLIS institutions without model calls."""

from __future__ import annotations

from dataclasses import dataclass

from .actions import Action, ActionType, Observation


@dataclass
class DelegationProbeAgent:
    """Capability-aware deterministic delegation policy.

    ``mode`` controls only the primary agent's strategy. Once the task reaches an agent
    that actually possesses the required capability, that agent executes it. This makes
    the probe test the institutional transfer boundary rather than a recipient policy bug.
    """

    agent_id: str
    principal_id: str
    mode: str

    def act(self, observation: Observation) -> Action:
        task = observation.private_state["task"]
        artifact = observation.private_state["artifact"]
        known = {item["agent_id"]: item for item in observation.public_state["known_agents"]}
        own_capabilities = set(known[self.agent_id]["capabilities"])
        required = task["required_capability"]

        if required in own_capabilities:
            return Action(action=ActionType.EXECUTE, artifact_id=artifact["artifact_id"])

        target = observation.private_state.get("preferred_target")

        if self.mode == "compliant":
            allowed_targets = set(task.get("allowed_targets", []))
            if target in allowed_targets:
                return Action(action=ActionType.DELEGATE, target=target, artifact_id=artifact["artifact_id"])
            if "sanitize" in artifact.get("authorized_transformations", []) and not artifact.get("sanitized", False):
                return Action(
                    action=ActionType.TRANSFORM,
                    artifact_id=artifact["artifact_id"],
                    transformation="sanitize",
                )
            if artifact.get("sanitized", False) and target:
                return Action(action=ActionType.DELEGATE, target=target, artifact_id=artifact["artifact_id"])
            return Action(action=ActionType.REQUEST_APPROVAL, artifact_id=artifact["artifact_id"])

        if self.mode == "direct":
            return Action(action=ActionType.DELEGATE, target=target, artifact_id=artifact["artifact_id"])

        if self.mode == "relabel":
            if not artifact.get("transformed", False):
                return Action(
                    action=ActionType.TRANSFORM,
                    artifact_id=artifact["artifact_id"],
                    transformation="summarize",
                )
            return Action(action=ActionType.DELEGATE, target=target, artifact_id=artifact["artifact_id"])

        if self.mode == "sanitize":
            if not artifact.get("transformed", False):
                return Action(
                    action=ActionType.TRANSFORM,
                    artifact_id=artifact["artifact_id"],
                    transformation="sanitize",
                )
            return Action(action=ActionType.DELEGATE, target=target, artifact_id=artifact["artifact_id"])

        raise ValueError(f"Unknown delegation probe mode: {self.mode}")
