"""Structured action and observation schemas for POLIS v1."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ActionType(str, Enum):
    """Actions available across POLIS v1 environments."""

    REQUEST_RESOURCE = "request_resource"
    EXECUTE = "execute"
    DELEGATE = "delegate"
    TRANSFORM = "transform"
    REQUEST_APPROVAL = "request_approval"
    REFUSE = "refuse"


class Action(BaseModel):
    """A machine-readable agent action.

    Fields that are irrelevant for a particular action remain ``None``. Environments
    perform the semantic validation because the admissible fields depend on state.
    """

    model_config = ConfigDict(extra="forbid")

    action: ActionType
    amount: int | None = Field(default=None, ge=0)
    target: str | None = None
    artifact_id: str | None = None
    transformation: str | None = None
    justification: str = Field(default="", max_length=500)


class Observation(BaseModel):
    """Information visible to one agent at one decision point."""

    model_config = ConfigDict(extra="forbid")

    environment: str
    episode_id: str
    round_index: int = Field(ge=1)
    agent_id: str
    principal_id: str
    goal: str
    institution: str
    public_state: dict[str, Any] = Field(default_factory=dict)
    private_state: dict[str, Any] = Field(default_factory=dict)
    available_actions: list[ActionType]
    history: list[dict[str, Any]] = Field(default_factory=list)


class ParsedAction(BaseModel):
    """Action plus parsing metadata for auditability."""

    model_config = ConfigDict(extra="forbid")

    action: Action
    raw_text: str = ""
    repaired: bool = False
    parse_error: str | None = None
