"""Model-backed agents with complete per-action audit traces."""

from __future__ import annotations

from dataclasses import dataclass, field

from .actions import Action, Observation
from .providers.base import ModelProvider, ModelResponse


@dataclass
class ModelAgent:
    """Adapter from a model provider to the environment-level ``Agent`` protocol.

    The environment sees only an ``act`` method returning a structured ``Action``. The
    experiment runner can separately retrieve every ``ModelResponse`` for token, cost,
    cache, generation-ID, and raw-output auditing.
    """

    agent_id: str
    principal_id: str
    provider: ModelProvider
    model: str
    responses: list[ModelResponse] = field(default_factory=list)

    def act(self, observation: Observation) -> Action:
        response = self.provider.act(observation, self.model)
        self.responses.append(response)
        return response.action

    @property
    def total_cost_usd(self) -> float:
        return sum(response.usage.cost_usd for response in self.responses)

    @property
    def total_tokens(self) -> int:
        return sum(response.usage.total_tokens for response in self.responses)
