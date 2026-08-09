"""Provider contracts for model-backed POLIS agents."""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field

from ..actions import Action, Observation


class ModelUsage(BaseModel):
    model_config = ConfigDict(extra="allow")

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    reasoning_tokens: int = 0
    cached_tokens: int = 0
    cost_usd: float = 0.0


class ModelResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str
    generation_id: str | None = None
    provider_name: str | None = None
    service_tier: str | None = None
    action: Action
    raw_text: str
    usage: ModelUsage
    cached: bool = False
    response_metadata: dict[str, Any] = Field(default_factory=dict)


class ModelProvider(Protocol):
    def act(self, observation: Observation, model: str) -> ModelResponse:
        """Return one structured model action."""
