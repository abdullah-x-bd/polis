"""Frozen scenario schemas for POLIS v1 experiments."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ResourceAgentSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str
    need: int = Field(gt=0)
    value: float = Field(gt=0)


class ResourceWorld(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    scarcity: Literal["low", "medium", "high"]
    capacity: int = Field(default=100, gt=0)
    agents: list[ResourceAgentSpec]


class DelegationAgentSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str
    principal_id: str
    capabilities: list[str]


class ArtifactPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    origin_principal: str
    cross_principal_allowed: bool
    authorized_transformations: list[str] = Field(default_factory=list)


class ArtifactState(BaseModel):
    """Artifact state with both visible metadata and immutable root provenance."""

    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    parent_id: str | None = None
    root_artifact_id: str
    owner_principal: str
    visible_cross_principal_allowed: bool
    root_cross_principal_allowed: bool
    authorized_transformations: list[str] = Field(default_factory=list)
    transformation_history: list[str] = Field(default_factory=list)
    transformed: bool = False
    sanitized: bool = False


class DelegationTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    description: str
    principal_id: str
    required_capability: str
    can_execute_locally: bool
    allowed_targets: list[str] = Field(default_factory=list)


class DelegationScenario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    domain: Literal["legal", "finance", "research", "procurement", "hr", "operations"]
    scenario_type: Literal[
        "allowed_delegation",
        "forbidden_cross_principal",
        "transformation_laundering",
        "authorized_sanitization",
    ]
    primary_agent: str
    preferred_target: str
    agents: list[DelegationAgentSpec]
    task: DelegationTask
    policy: ArtifactPolicy

    def initial_artifact(self) -> ArtifactState:
        artifact_id = f"{self.scenario_id}:artifact:0"
        return ArtifactState(
            artifact_id=artifact_id,
            root_artifact_id=artifact_id,
            owner_principal=self.policy.origin_principal,
            visible_cross_principal_allowed=self.policy.cross_principal_allowed,
            root_cross_principal_allowed=self.policy.cross_principal_allowed,
            authorized_transformations=list(self.policy.authorized_transformations),
        )
