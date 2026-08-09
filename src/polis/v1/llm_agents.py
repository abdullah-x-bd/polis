"""LLM-backed agent implementation for POLIS v1."""

from __future__ import annotations

from dataclasses import dataclass, field

from .actions import Action, Observation
from .providers.base import ModelProvider, ModelResponse


@dataclass
class LLMAgent:
    """One model endpoint acting under one principal identity."""

    agent_id: str
    principal_id: str
    model: str
    provider: ModelProvider
    responses: list[ModelResponse] = field(default_factory=list)

    def act(self, observation: Observation) -> Action:
        response = self.provider.act(observation, self.model)
        self.responses.append(response)
        return response.action

    @property
    def total_cost_usd(self) -> float:
        return sum(response.usage.cost_usd for response in self.responses if not response.cached)
