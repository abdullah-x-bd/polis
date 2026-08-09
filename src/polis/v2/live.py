"""Resumable live execution for all frozen POLIS v2 studies."""

from __future__ import annotations

import json
import os
import platform
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from polis.v1.model_agents import ModelAgent
from polis.v1.providers.base import ModelProvider, ModelResponse

from .commons import QuotaSalienceEnvironment
from .delegation import RecoverableDelegationEnvironment
from .models import CommonsRegime, GovernanceRegime
from .protocol import V2Protocol
from .scenarios import (
    HETEROGENEOUS_COMPOSITIONS,
    commons_scenarios,
    delegation_scenarios,
    frontier_scenarios,
    heterogeneous_scenarios,
    wording_robustness_scenarios,
)

StudyName = Literal["delegation_main", "wording_robustness", "heterogeneous", "commons_salience", "frontier"]


class V2EpisodeRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    protocol_version: str
    study_fingerprint: str
    study: StudyName
    scenario_id: str
    governance: str
    model_composition: str
    result: dict[str, Any]
    model_calls: list[ModelResponse]
    episode_cost_usd: float
    episode_tokens: int
    completed_at: str

    def completion_key(self) -> tuple[str, str, str, str]:
        return (self.study, self.scenario_id, self.governance, self.model_composition)


class V2RunManifest(BaseModel):
    model_config = ConfigDict(extra="allow")

    run_id: str
    study: StudyName
    protocol_version: str
    study_fingerprint: str
    git_sha: str | None
    python_version: str
    platform: str
    shard_index: int
    shard_count: int
    expected_episodes: int
    completed_episodes: int
    maximum_model_calls: int
    status: Literal["running", "complete", "partial", "failed"]
    started_at: str
    finished_at: str | None = None
    result_file: str


@dataclass(frozen=True)
class EpisodeSpec:
    study: StudyName
    scenario: Any
    governance: str
    composition_name: str
    model_map: dict[str, str]
    maximum_calls: int

    @property
    def scenario_id(self) -> str:
        return self.scenario.scenario_id

    @property
    def key(self) -> tuple[str, str, str, str]:
        return (self.study, self.scenario_id, self.governance, self.composition_name)


def build_episode_specs(protocol: V2Protocol, study: StudyName) -> list[EpisodeSpec]:
    cheap_models = [item.id for item in protocol.cheap_models]
    frontier_models = [item.id for item in protocol.frontier_models]
    specs: list[EpisodeSpec] = []

    if study == "delegation_main":
        for scenario in delegation_scenarios():
            for governance in protocol.main_governance:
                for model in cheap_models:
                    specs.append(
                        EpisodeSpec(
                            study=study,
                            scenario=scenario,
                            governance=governance,
                            composition_name=model,
                            model_map={item.agent_id: model for item in scenario.agents},
                            maximum_calls=protocol.max_delegation_actions,
                        )
                    )
    elif study == "wording_robustness":
        for scenario in wording_robustness_scenarios():
            for governance in protocol.wording_governance:
                for model in cheap_models:
                    specs.append(
                        EpisodeSpec(
                            study=study,
                            scenario=scenario,
                            governance=governance,
                            composition_name=model,
                            model_map={item.agent_id: model for item in scenario.agents},
                            maximum_calls=protocol.max_delegation_actions,
                        )
                    )
    elif study == "heterogeneous":
        for scenario in heterogeneous_scenarios():
            for governance in protocol.heterogeneous_governance:
                for composition in HETEROGENEOUS_COMPOSITIONS:
                    specs.append(
                        EpisodeSpec(
                            study=study,
                            scenario=scenario,
                            governance=governance,
                            composition_name=composition["name"],
                            model_map={key: value for key, value in composition.items() if key.startswith("agent_")},
                            maximum_calls=protocol.max_delegation_actions,
                        )
                    )
    elif study == "commons_salience":
        for scenario in commons_scenarios():
            for governance in protocol.commons_governance:
                for model in cheap_models:
                    specs.append(
                        EpisodeSpec(
                            study=study,
                            scenario=scenario,
                            governance=governance,
                            composition_name=model,
                            model_map={item.agent_id: model for item in scenario.agents},
                            maximum_calls=len(scenario.agents),
                        )
                    )
    elif study == "frontier":
        for scenario in frontier_scenarios():
            for governance in protocol.frontier_governance:
                for model in frontier_models:
                    specs.append(
                        EpisodeSpec(
                            study=study,
                            scenario=scenario,
                            governance=governance,
                            composition_name=model,
                            model_map={item.agent_id: model for item in scenario.agents},
                            maximum_calls=protocol.max_delegation_actions,
                        )
                    )
    else:
        raise ValueError(study)
    return specs


def shard_specs(specs: list[EpisodeSpec], shard_index: int, shard_count: int) -> list[EpisodeSpec]:
    if shard_count < 1 or not 0 <= shard_index < shard_count:
        raise ValueError("Invalid shard index/count")
    return [spec for index, spec in enumerate(specs) if index % shard_count == shard_index]


def run_study(
    *,
    protocol: V2Protocol,
    provider: ModelProvider,
    study: StudyName,
    output_dir: str | Path,
    shard_index: int = 0,
    shard_count: int = 1,
    run_id: str | None = None,
) -> V2RunManifest:
    if protocol.status != "frozen":
        raise RuntimeError("Paid v2 collection is forbidden until configs/v2_protocol.json has status='frozen'")
    fingerprint = protocol.study_fingerprint()
    all_specs = build_episode_specs(protocol, study)
    specs = shard_specs(all_specs, shard_index, shard_count)
    run_id = run_id or f"polis-v2-{study}-{fingerprint[:12]}-s{shard_index}of{shard_count}"
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    result_path = out / f"{run_id}.jsonl"
    manifest_path = out / f"{run_id}.manifest.json"
    completed = _completed_keys(result_path, fingerprint)

    manifest = V2RunManifest(
        run_id=run_id,
        study=study,
        protocol_version=protocol.protocol_version,
        study_fingerprint=fingerprint,
        git_sha=os.getenv("GITHUB_SHA"),
        python_version=sys.version.split()[0],
        platform=platform.platform(),
        shard_index=shard_index,
        shard_count=shard_count,
        expected_episodes=len(specs),
        completed_episodes=len(completed),
        maximum_model_calls=sum(item.maximum_calls for item in specs),
        status="running",
        started_at=_now(),
        result_file=result_path.name,
    )
    _write_manifest(manifest_path, manifest)

    try:
        for spec in specs:
            if spec.key in completed:
                continue
            agents = {
                agent_id: ModelAgent(
                    agent_id=agent_id,
                    principal_id=_principal_for(spec.scenario, agent_id),
                    provider=provider,
                    model=model,
                )
                for agent_id, model in spec.model_map.items()
            }
            if study == "commons_salience":
                result = QuotaSalienceEnvironment(
                    spec.scenario,
                    CommonsRegime(spec.governance),
                ).run(agents, model_name=spec.composition_name)
            else:
                result = RecoverableDelegationEnvironment(
                    spec.scenario,
                    GovernanceRegime(spec.governance),
                    study=study,
                    max_actions=protocol.max_delegation_actions,
                    model_composition=spec.composition_name,
                ).run(agents)
            calls = [response for agent in agents.values() for response in agent.responses]
            record = V2EpisodeRecord(
                run_id=run_id,
                protocol_version=protocol.protocol_version,
                study_fingerprint=fingerprint,
                study=study,
                scenario_id=spec.scenario_id,
                governance=spec.governance,
                model_composition=spec.composition_name,
                result=result.model_dump(mode="json"),
                model_calls=calls,
                episode_cost_usd=sum(item.usage.cost_usd for item in calls),
                episode_tokens=sum(item.usage.total_tokens for item in calls),
                completed_at=_now(),
            )
            _append_record(result_path, record)
            completed.add(record.completion_key())
            manifest.completed_episodes = len(completed)
            _write_manifest(manifest_path, manifest)

        manifest.status = "complete" if len(completed) == len(specs) else "partial"
        manifest.finished_at = _now()
        _write_manifest(manifest_path, manifest)
        return manifest
    except Exception:
        manifest.status = "partial" if completed else "failed"
        manifest.finished_at = _now()
        manifest.completed_episodes = len(completed)
        _write_manifest(manifest_path, manifest)
        raise


def load_records(path: str | Path) -> list[V2EpisodeRecord]:
    source = Path(path)
    if not source.exists():
        return []
    return [V2EpisodeRecord.model_validate_json(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _completed_keys(path: Path, fingerprint: str) -> set[tuple[str, str, str, str]]:
    result = set()
    for record in load_records(path):
        if record.study_fingerprint != fingerprint:
            raise ValueError("Existing result file has a different v2 study fingerprint")
        result.add(record.completion_key())
    return result


def _principal_for(scenario: Any, agent_id: str) -> str:
    for item in scenario.agents:
        if item.agent_id == agent_id:
            return getattr(item, "principal_id", item.agent_id)
    raise ValueError(agent_id)


def _append_record(path: Path, record: V2EpisodeRecord) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(record.model_dump_json() + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _write_manifest(path: Path, manifest: V2RunManifest) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(manifest.model_dump(mode="json"), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
