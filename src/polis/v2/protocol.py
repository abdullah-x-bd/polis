"""Frozen-protocol handling for POLIS v2."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .scenarios import design_digest


class ModelSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    family: str
    provider_family: str


class V2Protocol(BaseModel):
    model_config = ConfigDict(extra="forbid")

    protocol_name: str
    protocol_version: str
    status: Literal["draft", "frozen"]
    frozen_date: str | None = None
    research_question: str
    cheap_models: list[ModelSpec]
    frontier_models: list[ModelSpec]
    main_governance: list[str]
    wording_governance: list[str]
    heterogeneous_governance: list[str]
    frontier_governance: list[str]
    commons_governance: list[str]
    max_delegation_actions: int = Field(default=6, ge=2, le=12)
    block_friction: float = Field(default=0.02, ge=0)
    invalid_friction: float = Field(default=0.01, ge=0)
    approval_friction: float = Field(default=0.03, ge=0)
    transform_friction: float = Field(default=0.01, ge=0)
    temperature: float = 0.0
    max_tokens: int = Field(default=180, ge=64, le=1000)
    bootstrap_samples: int = Field(default=10_000, ge=1000)
    confidence_level: float = Field(default=0.95, gt=0.5, lt=1)
    seed: int = 20260810

    @model_validator(mode="after")
    def _validate_models(self) -> V2Protocol:
        ids = [item.id for item in [*self.cheap_models, *self.frontier_models]]
        if len(ids) != len(set(ids)):
            raise ValueError("Model IDs must be unique across cheap and frontier panels")
        if len(self.cheap_models) < 3:
            raise ValueError("V2 requires at least three cheap-model families")
        return self

    def canonical_config(self) -> dict[str, object]:
        return self.model_dump(mode="json")

    def config_digest(self) -> str:
        raw = json.dumps(self.canonical_config(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def study_fingerprint(self) -> str:
        payload = {
            "config": self.canonical_config(),
            "design_digest": design_digest(),
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_protocol(path: str | Path = "configs/v2_protocol.json") -> V2Protocol:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return V2Protocol.model_validate(data)
