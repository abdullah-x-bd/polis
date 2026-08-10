"""Typed schemas for POLIS v2 environments and results."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from polis.v1.actions import Action


class GovernanceRegime(str, Enum):
    NO_INSTITUTION = "no_institution"
    CONCISE_PROMPT = "concise_prompt"
    CONSTITUTIONAL_PROMPT = "constitutional_prompt"
    PROVENANCE_PROMPT = "provenance_prompt"
    LOCAL_GUARD = "recoverable_local_guard"
    PROVENANCE_GUARD = "recoverable_provenance_guard"


class CommonsRegime(str, Enum):
    NO_CAP = "no_cap"
    HIDDEN_CAP = "hidden_cap"
    VISIBLE_CAP = "visible_cap"
    VISIBLE_CAP_NORM = "visible_cap_truthful_norm"
    CONGESTION_PRICING = "congestion_pricing"


class AgentSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str
    principal_id: str
    capabilities: list[str]


class ArtifactState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    root_artifact_id: str
    owner_principal: str
    root_cross_principal_allowed: bool
    visible_cross_principal_allowed: bool
    authorized_transformations: list[str] = Field(default_factory=list)
    transformation_history: list[str] = Field(default_factory=list)
    sanitized: bool = False
    approved: bool = False


class DelegationScenario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    base_scenario_id: str
    domain: str
    scenario_type: Literal[
        "safe_internal_route",
        "direct_forbidden",
        "transformation_laundering",
        "authorized_sanitization",
    ]
    pressure_level: int = Field(ge=0, le=3)
    wording_variant: int = Field(default=0, ge=0, le=2)
    task_text: str
    required_capability: str
    primary_agent_id: str
    agents: list[AgentSpec]
    artifact: ArtifactState
    internal_target: str
    external_target: str
    internal_value: float
    external_value: float
    approval_value: float
    direct_execution_value: float = 0.0


class DelegationStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: int
    actor: str
    actor_principal: str
    action: Action
    institution: str
    allowed: bool
    reason: str
    blocked: bool = False
    invalid: bool = False
    violation_attempt: bool = False
    realized_violation: bool = False
    artifact_before: ArtifactState
    artifact_after: ArtifactState
    target_principal: str | None = None
    task_completed: bool = False
    task_value: float = 0.0
    friction_cost: float = 0.0


class DelegationEpisodeResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    study: Literal["delegation_main", "wording_robustness", "heterogeneous", "frontier"]
    scenario_id: str
    base_scenario_id: str
    domain: str
    scenario_type: str
    pressure_level: int
    wording_variant: int
    governance: str
    model_composition: str
    task_completed: bool
    compliant_completion: bool
    realized_violation: bool
    violation_attempted: bool
    violation_attempt_count: int
    repeated_violation_attempt: bool
    violation_detected: bool
    safe_recovery: bool
    blocked_attempt_occurred: bool
    laundering_succeeded: bool
    approval_requested: bool
    refusal: bool
    deadlock: bool
    invalid_action_count: int
    intervention_count: int
    path_length: int
    task_value: float
    friction_cost: float
    system_utility: float
    steps: list[DelegationStep]


class CommonsAgentSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str
    need: int = Field(ge=1)
    value: float = Field(gt=0)


class CommonsScenario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    world_id: str
    objective: Literal["self_interested", "social_welfare"]
    capacity: int = Field(default=100, ge=1)
    agents: list[CommonsAgentSpec]
    visible_cap: int = 30
    hidden_cap: int = 30
    congestion_alpha: float = 0.20


class CommonsAgentOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str
    need: int
    value: float
    requested: int
    effective_request: int
    allocated: float
    useful: float
    completion: float
    overclaim: int
    charge: float


class CommonsEpisodeResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    study: Literal["commons_salience"] = "commons_salience"
    scenario_id: str
    world_id: str
    objective: str
    governance: str
    model: str
    system_welfare: float
    oracle_welfare: float
    efficiency_ratio: float
    overclaim_ratio: float
    resource_waste: float
    cap_seeking_rate: float
    total_charge: float
    invalid_action_count: int
    outcomes: list[CommonsAgentOutcome]
