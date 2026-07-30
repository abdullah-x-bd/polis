"""Agent policies for POLIS research environments."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .models import Action


@dataclass
class ScriptedAgent:
    """A reproducible policy used to validate the experimental pipeline.

    This agent is not a model of frontier-agent behaviour. It creates controlled
    actions so researchers can test institutions, metrics, and logging before
    adding model-backed agents.
    """

    name: str
    delegate_name: str
    prompt_compliance_probability: float = 0.0

    def propose(self, task_id: str, task_kind: str, rng: random.Random) -> Action:
        if task_kind not in {"legitimate", "restricted"}:
            raise ValueError(f"Unsupported task kind: {task_kind}")

        if task_kind == "restricted" and rng.random() < self.prompt_compliance_probability:
            return Action(
                actor=self.name,
                action_type="refuse",
                task_id=task_id,
                task_kind=task_kind,
                metadata={"basis": "prompt_guidance"},
            )

        return Action(
            actor=self.name,
            action_type="delegate",
            task_id=task_id,
            task_kind=task_kind,
            target=self.delegate_name,
        )
