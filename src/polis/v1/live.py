"""Resumable live-model experiment execution for POLIS v1."""

from __future__ import annotations

import json
import os
import platform
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .delegation import DelegationBoundariesEnvironment
from .institutions import (
    CongestionPricingInstitution,
    HardQuotaInstitution,
    LocalGuardInstitution,
    NoCommonsInstitution,
    NoDelegationInstitution,
    PromptCommonsInstitution,
    PromptDelegationInstitution,
    ProvenanceGuardInstitution,
)
from .loaders import load_delegation_scenarios, load_resource_worlds
from .model_agents import ModelAgent
from .protocol import LiveExperimentProtocol
from .providers.base import ModelProvider, ModelResponse
from .resource_commons import ResourceCommonsEnvironment


class LiveEpisodeRecord(BaseModel):
    """One atomic confirmatory episode plus every model call that generated it."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    protocol_fingerprint: str
    protocol_version: str
    mode: Literal["pilot", "full"]
    environment: Literal["resource_commons", "delegation_boundaries"]
    model: str
    scenario_id: str
    institution: str
    repetition: int = Field(ge=0)
    result: dict[str, Any]
    model_calls: list[ModelResponse]
    episode_cost_usd: float
    episode_tokens: int
    completed_at: str

    def completion_key(self) -> tuple[str, str, str, str, int]:
        return (
            self.environment,
            self.model,
            self.scenario_id,
            self.institution,
            self.repetition,
        )


class RunManifest(BaseModel):
    model_config = ConfigDict(extra="allow")

    run_id: str
    protocol_fingerprint: str
    protocol_version: str
    mode: Literal["pilot", "full"]
    selected_models: list[str]
    shard_index: int = 0
    shard_count: int = 1
    started_at: str
    finished_at: str | None = None
    status: Literal["running", "complete", "partial", "failed"] = "running"
    git_sha: str | None = None
    python_version: str
    platform: str
    expected_episodes: int
    completed_episodes: int = 0
    maximum_model_calls: int
    result_file: str
    notes: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class MatrixPlan:
    mode: Literal["pilot", "full"]
    models: tuple[str, ...]
    commons_worlds: int
    commons_institutions: int
    commons_rounds: int
    commons_agents_per_world: int
    delegation_scenarios: int
    delegation_institutions: int
    delegation_max_actions: int
    repetitions: int
    shard_index: int = 0
    shard_count: int = 1

    @property
    def commons_episodes(self) -> int:
        return (
            len(self.models)
            * self.commons_worlds
            * self.commons_institutions
            * self.repetitions
        )

    @property
    def delegation_episodes(self) -> int:
        return (
            len(self.models)
            * self.delegation_scenarios
            * self.delegation_institutions
            * self.repetitions
        )

    @property
    def episodes(self) -> int:
        return self.commons_episodes + self.delegation_episodes

    @property
    def maximum_model_calls(self) -> int:
        commons_calls = (
            self.commons_episodes
            * self.commons_rounds
            * self.commons_agents_per_world
        )
        delegation_calls = self.delegation_episodes * self.delegation_max_actions
        return commons_calls + delegation_calls

    def to_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "models": list(self.models),
            "shard_index": self.shard_index,
            "shard_count": self.shard_count,
            "commons_worlds": self.commons_worlds,
            "commons_institutions": self.commons_institutions,
            "commons_rounds": self.commons_rounds,
            "commons_agents_per_world": self.commons_agents_per_world,
            "delegation_scenarios": self.delegation_scenarios,
            "delegation_institutions": self.delegation_institutions,
            "delegation_max_actions": self.delegation_max_actions,
            "repetitions": self.repetitions,
            "episodes": self.episodes,
            "maximum_model_calls": self.maximum_model_calls,
        }


def build_plan(
    protocol: LiveExperimentProtocol,
    mode: Literal["pilot", "full"],
    selected_models: Iterable[str] | None = None,
    shard_index: int = 0,
    shard_count: int = 1,
) -> MatrixPlan:
    _validate_shard(shard_index, shard_count)
    models = _selected_model_ids(protocol, selected_models)
    worlds = load_resource_worlds(protocol.commons.scenario_path)
    delegation = load_delegation_scenarios(protocol.delegation.scenario_path)
    if mode == "pilot":
        worlds = _select_indices(worlds, protocol.commons.pilot_world_indices, "commons pilot")
        delegation = _select_indices(
            delegation,
            protocol.delegation.pilot_scenario_indices,
            "delegation pilot",
        )
    worlds = _apply_shard(worlds, shard_index, shard_count)
    delegation = _apply_shard(delegation, shard_index, shard_count)
    if not worlds or not delegation:
        raise ValueError("Shard contains no Commons worlds or no Delegation scenarios")
    return MatrixPlan(
        mode=mode,
        models=tuple(models),
        commons_worlds=len(worlds),
        commons_institutions=len(protocol.commons.institutions),
        commons_rounds=protocol.commons.rounds,
        commons_agents_per_world=len(worlds[0].agents),
        delegation_scenarios=len(delegation),
        delegation_institutions=len(protocol.delegation.institutions),
        delegation_max_actions=protocol.delegation.max_actions,
        repetitions=protocol.inference.repetitions,
        shard_index=shard_index,
        shard_count=shard_count,
    )


def run_live_matrix(
    *,
    protocol: LiveExperimentProtocol,
    provider: ModelProvider,
    output_dir: str | Path,
    mode: Literal["pilot", "full"] = "pilot",
    selected_models: Iterable[str] | None = None,
    run_id: str | None = None,
    shard_index: int = 0,
    shard_count: int = 1,
) -> RunManifest:
    """Run or resume a frozen live matrix or a disjoint scenario shard.

    Results are appended after each episode. A rerun against the same output file skips
    completed episode keys. Sharding partitions the scenario lists by stable list index;
    it does not alter scenarios, institutions, models, prompts, or the protocol fingerprint.
    """

    _validate_shard(shard_index, shard_count)
    model_ids = _selected_model_ids(protocol, selected_models)
    plan = build_plan(protocol, mode, model_ids, shard_index, shard_count)
    fingerprint = protocol.fingerprint()
    run_id = run_id or _default_run_id(fingerprint, mode, shard_index, shard_count)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    result_path = out / f"{run_id}.jsonl"
    manifest_path = out / f"{run_id}.manifest.json"
    completed = _load_completed(result_path, fingerprint)

    manifest = RunManifest(
        run_id=run_id,
        protocol_fingerprint=fingerprint,
        protocol_version=protocol.protocol_version,
        mode=mode,
        selected_models=model_ids,
        shard_index=shard_index,
        shard_count=shard_count,
        started_at=_now(),
        git_sha=os.getenv("GITHUB_SHA"),
        python_version=sys.version.split()[0],
        platform=platform.platform(),
        expected_episodes=plan.episodes,
        completed_episodes=len(completed),
        maximum_model_calls=plan.maximum_model_calls,
        result_file=result_path.name,
        notes=[
            "Each record contains structured environment outcomes and raw model-call audit data.",
            "Existing completion keys are skipped on resume; provider-level identical calls are separately cached.",
            f"Scenario shard {shard_index + 1} of {shard_count}; sharding does not change the frozen protocol fingerprint.",
        ],
    )
    _write_manifest(manifest_path, manifest)

    worlds = load_resource_worlds(protocol.commons.scenario_path)
    delegation_scenarios = load_delegation_scenarios(protocol.delegation.scenario_path)
    if mode == "pilot":
        worlds = _select_indices(worlds, protocol.commons.pilot_world_indices, "commons pilot")
        delegation_scenarios = _select_indices(
            delegation_scenarios,
            protocol.delegation.pilot_scenario_indices,
            "delegation pilot",
        )
    worlds = _apply_shard(worlds, shard_index, shard_count)
    delegation_scenarios = _apply_shard(delegation_scenarios, shard_index, shard_count)

    try:
        for model in model_ids:
            for repetition in range(protocol.inference.repetitions):
                for world in worlds:
                    for institution_name in protocol.commons.institutions:
                        key = (
                            "resource_commons",
                            model,
                            world.scenario_id,
                            institution_name,
                            repetition,
                        )
                        if key in completed:
                            continue
                        institution = _commons_institution(protocol, institution_name)
                        agents = {
                            spec.agent_id: ModelAgent(
                                agent_id=spec.agent_id,
                                principal_id=spec.agent_id,
                                provider=provider,
                                model=model,
                            )
                            for spec in world.agents
                        }
                        result = ResourceCommonsEnvironment(world, institution).run(
                            agents,
                            rounds=protocol.commons.rounds,
                        )
                        calls = _collect_calls(agents.values())
                        record = LiveEpisodeRecord(
                            run_id=run_id,
                            protocol_fingerprint=fingerprint,
                            protocol_version=protocol.protocol_version,
                            mode=mode,
                            environment="resource_commons",
                            model=model,
                            scenario_id=world.scenario_id,
                            institution=institution_name,
                            repetition=repetition,
                            result=result.model_dump(mode="json"),
                            model_calls=calls,
                            episode_cost_usd=sum(call.usage.cost_usd for call in calls),
                            episode_tokens=sum(call.usage.total_tokens for call in calls),
                            completed_at=_now(),
                        )
                        _append_record(result_path, record)
                        completed.add(record.completion_key())
                        manifest.completed_episodes = len(completed)
                        _write_manifest(manifest_path, manifest)

                for scenario in delegation_scenarios:
                    for institution_name in protocol.delegation.institutions:
                        key = (
                            "delegation_boundaries",
                            model,
                            scenario.scenario_id,
                            institution_name,
                            repetition,
                        )
                        if key in completed:
                            continue
                        institution = _delegation_institution(institution_name)
                        agents = {
                            spec.agent_id: ModelAgent(
                                agent_id=spec.agent_id,
                                principal_id=spec.principal_id,
                                provider=provider,
                                model=model,
                            )
                            for spec in scenario.agents
                        }
                        result = DelegationBoundariesEnvironment(
                            scenario,
                            institution,
                            max_actions=protocol.delegation.max_actions,
                        ).run(agents)
                        calls = _collect_calls(agents.values())
                        record = LiveEpisodeRecord(
                            run_id=run_id,
                            protocol_fingerprint=fingerprint,
                            protocol_version=protocol.protocol_version,
                            mode=mode,
                            environment="delegation_boundaries",
                            model=model,
                            scenario_id=scenario.scenario_id,
                            institution=institution_name,
                            repetition=repetition,
                            result=result.model_dump(mode="json"),
                            model_calls=calls,
                            episode_cost_usd=sum(call.usage.cost_usd for call in calls),
                            episode_tokens=sum(call.usage.total_tokens for call in calls),
                            completed_at=_now(),
                        )
                        _append_record(result_path, record)
                        completed.add(record.completion_key())
                        manifest.completed_episodes = len(completed)
                        _write_manifest(manifest_path, manifest)

        manifest.finished_at = _now()
        manifest.status = "complete" if len(completed) == plan.episodes else "partial"
        _write_manifest(manifest_path, manifest)
        return manifest
    except Exception:
        manifest.finished_at = _now()
        manifest.status = "partial" if completed else "failed"
        manifest.completed_episodes = len(completed)
        _write_manifest(manifest_path, manifest)
        raise


def load_records(path: str | Path) -> list[LiveEpisodeRecord]:
    records: list[LiveEpisodeRecord] = []
    source = Path(path)
    if not source.exists():
        return records
    with source.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(LiveEpisodeRecord.model_validate_json(line))
    return records


def _commons_institution(protocol: LiveExperimentProtocol, name: str):
    if name == "no_institution":
        return NoCommonsInstitution()
    if name == "prompt_only":
        return PromptCommonsInstitution()
    if name == "hard_quota":
        return HardQuotaInstitution(quota=protocol.commons.hard_quota)
    if name == "congestion_pricing":
        return CongestionPricingInstitution(alpha=protocol.commons.congestion_alpha)
    raise ValueError(f"Unknown Commons institution: {name}")


def _delegation_institution(name: str):
    if name == "no_institution":
        return NoDelegationInstitution()
    if name == "prompt_only":
        return PromptDelegationInstitution()
    if name == "local_guard":
        return LocalGuardInstitution()
    if name == "provenance_guard":
        return ProvenanceGuardInstitution()
    raise ValueError(f"Unknown delegation institution: {name}")


def _selected_model_ids(
    protocol: LiveExperimentProtocol,
    selected_models: Iterable[str] | None,
) -> list[str]:
    allowed = [model.id for model in protocol.models]
    if selected_models is None:
        return allowed
    selected = list(selected_models)
    unknown = sorted(set(selected) - set(allowed))
    if unknown:
        raise ValueError(f"Models are not in the frozen protocol: {unknown}")
    if not selected:
        raise ValueError("At least one model must be selected")
    return selected


def _select_indices(items: list[Any], indices: list[int], label: str) -> list[Any]:
    if not indices:
        raise ValueError(f"{label} indices may not be empty")
    try:
        return [items[index] for index in indices]
    except IndexError as exc:
        raise ValueError(f"{label} contains an out-of-range index") from exc


def _validate_shard(shard_index: int, shard_count: int) -> None:
    if shard_count < 1:
        raise ValueError("shard_count must be at least 1")
    if shard_index < 0 or shard_index >= shard_count:
        raise ValueError("shard_index must satisfy 0 <= shard_index < shard_count")


def _apply_shard(items: list[Any], shard_index: int, shard_count: int) -> list[Any]:
    if shard_count == 1:
        return items
    return [item for index, item in enumerate(items) if index % shard_count == shard_index]


def _collect_calls(agents: Iterable[ModelAgent]) -> list[ModelResponse]:
    calls: list[ModelResponse] = []
    for agent in agents:
        calls.extend(agent.responses)
    return calls


def _load_completed(
    path: Path,
    expected_fingerprint: str,
) -> set[tuple[str, str, str, str, int]]:
    records = load_records(path)
    completed: set[tuple[str, str, str, str, int]] = set()
    for record in records:
        if record.protocol_fingerprint != expected_fingerprint:
            raise ValueError(
                "Existing result file was produced with a different protocol fingerprint; "
                "use a different run ID rather than mixing protocols."
            )
        completed.add(record.completion_key())
    return completed


def _append_record(path: Path, record: LiveEpisodeRecord) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(record.model_dump_json() + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _write_manifest(path: Path, manifest: RunManifest) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(manifest.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _default_run_id(
    fingerprint: str,
    mode: str,
    shard_index: int = 0,
    shard_count: int = 1,
) -> str:
    base = f"polis-v1-{mode}-{fingerprint[:12]}"
    if shard_count > 1:
        return f"{base}-s{shard_index + 1}of{shard_count}"
    return base


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
