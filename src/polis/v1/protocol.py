"""Frozen live-experiment protocol for POLIS v1.

The protocol is intentionally explicit. A completed result should be attributable to a
particular scenario set, institution configuration, model set, inference configuration,
and statistical plan. The canonical SHA-256 fingerprint is written into every live run.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ModelSpec(BaseModel):
    """One model included in the confirmatory live experiment."""

    model_config = ConfigDict(extra="forbid")

    id: str
    family: str
    provider_family: str
    rationale: str


class CommonsProtocol(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_path: str
    rounds: int = Field(default=2, ge=1)
    institutions: list[Literal["no_institution", "prompt_only", "hard_quota", "congestion_pricing"]]
    hard_quota: int = Field(default=30, ge=1)
    congestion_alpha: float = Field(default=0.20, ge=0)
    pilot_world_indices: list[int] = Field(default_factory=lambda: [0, 11, 23])


class DelegationProtocol(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_path: str
    institutions: list[Literal["no_institution", "prompt_only", "local_guard", "provenance_guard"]]
    max_actions: int = Field(default=4, ge=1)
    pilot_scenario_indices: list[int] = Field(default_factory=lambda: [0, 1, 2, 3])


class InferenceProtocol(BaseModel):
    model_config = ConfigDict(extra="forbid")

    temperature: float = 0.0
    max_tokens: int = Field(default=180, ge=32, le=1000)
    repetitions: int = Field(default=1, ge=1, le=10)
    max_cost_usd: float = Field(default=4.0, gt=0)
    reserve_per_request_usd: float = Field(default=0.01, ge=0)
    structured_outputs: bool = True
    cache_identical_requests: bool = True


class AnalysisProtocol(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bootstrap_samples: int = Field(default=10_000, ge=1000)
    confidence_level: float = Field(default=0.95, gt=0.5, lt=1.0)
    multiple_comparison_method: Literal["holm"] = "holm"
    primary_commons_endpoint: Literal["efficiency_ratio"] = "efficiency_ratio"
    secondary_commons_endpoints: list[str] = Field(
        default_factory=lambda: ["overclaim_ratio", "resource_waste", "total_charge"]
    )
    primary_delegation_endpoint: Literal["realized_violation"] = "realized_violation"
    secondary_delegation_endpoints: list[str] = Field(
        default_factory=lambda: [
            "task_completed",
            "violation_attempted",
            "violation_detected",
            "legitimate_action_blocked",
            "policy_laundering_succeeded",
        ]
    )


class LiveExperimentProtocol(BaseModel):
    """Complete confirmatory POLIS v1 protocol."""

    model_config = ConfigDict(extra="forbid")

    protocol_name: str
    protocol_version: str
    frozen_date: str
    research_question: str
    models: list[ModelSpec]
    commons: CommonsProtocol
    delegation: DelegationProtocol
    inference: InferenceProtocol
    analysis: AnalysisProtocol

    @model_validator(mode="after")
    def _validate_unique_models(self) -> LiveExperimentProtocol:
        model_ids = [model.id for model in self.models]
        if len(model_ids) != len(set(model_ids)):
            raise ValueError("Protocol model IDs must be unique")
        if not self.models:
            raise ValueError("Protocol must include at least one model")
        return self

    def canonical_dict(self) -> dict[str, object]:
        return self.model_dump(mode="json")

    def fingerprint(self) -> str:
        payload = json.dumps(
            self.canonical_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


def load_protocol(path: str | Path) -> LiveExperimentProtocol:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return LiveExperimentProtocol.model_validate(data)
