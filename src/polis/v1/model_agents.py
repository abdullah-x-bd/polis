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
    cache, generation-ID, raw-output, actor, and decision-step auditing.
    """

    agent_id: str
    principal_id: str
    provider: ModelProvider
    model: str
    responses: list[ModelResponse] = field(default_factory=list)

    def act(self, observation: Observation) -> Action:
        response = self.provider.act(observation, self.model)
        metadata = {
            **response.response_metadata,
            "polis_environment": observation.environment,
            "polis_episode_id": observation.episode_id,
            "polis_round_index": observation.round_index,
            "polis_agent_id": observation.agent_id,
            "polis_principal_id": observation.principal_id,
            "polis_institution": observation.institution,
        }
        audited = response.model_copy(update={"response_metadata": metadata})
        self.responses.append(audited)
        return audited.action

    @property
    def total_cost_usd(self) -> float:
        return sum(response.usage.cost_usd for response in self.responses)

    @property
    def total_tokens(self) -> int:
        return sum(response.usage.total_tokens for response in self.responses)
