"""Load frozen POLIS v1 scenario specifications."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .scenarios import (
    ArtifactPolicy,
    DelegationAgentSpec,
    DelegationScenario,
    DelegationTask,
    ResourceWorld,
)


def _read_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_resource_worlds(path: str | Path) -> list[ResourceWorld]:
    data = _read_json(path)
    if not isinstance(data, list):
        raise ValueError("Resource Commons file must contain a list")
    worlds = [ResourceWorld.model_validate(item) for item in data]
    if len(worlds) != 24:
        raise ValueError(f"POLIS v1 expects 24 Resource Commons worlds, found {len(worlds)}")
    return worlds


def load_delegation_scenarios(path: str | Path) -> list[DelegationScenario]:
    """Expand the frozen six-domain by four-condition matched design into 24 scenarios."""

    spec = _read_json(path)
    domains = spec["domains"]
    scenario_types = spec["scenario_types"]
    internal = spec["principals"]["internal"]
    external = spec["principals"]["external"]

    scenarios: list[DelegationScenario] = []
    scenario_index = 1
    for domain_spec in domains:
        domain = domain_spec["domain"]
        capability = domain_spec["capability"]
        for scenario_type in scenario_types:
            same_principal = scenario_type == "allowed_delegation"
            preferred_target = "agent_b" if same_principal else "agent_c"
            authorized_transformations = ["sanitize"] if scenario_type == "authorized_sanitization" else []

            scenarios.append(
                DelegationScenario(
                    scenario_id=f"delegation_{scenario_index:02d}",
                    domain=domain,
                    scenario_type=scenario_type,
                    primary_agent="agent_a",
                    preferred_target=preferred_target,
                    agents=[
                        DelegationAgentSpec(
                            agent_id="agent_a",
                            principal_id=internal,
                            capabilities=["general_analysis"],
                        ),
                        DelegationAgentSpec(
                            agent_id="agent_b",
                            principal_id=internal,
                            capabilities=[capability],
                        ),
                        DelegationAgentSpec(
                            agent_id="agent_c",
                            principal_id=external,
                            capabilities=[capability],
                        ),
                    ],
                    task=DelegationTask(
                        task_id=f"{domain}_{scenario_type}",
                        description=domain_spec["description"],
                        principal_id=internal,
                        required_capability=capability,
                        can_execute_locally=False,
                        allowed_targets=["agent_b"] if same_principal else [],
                    ),
                    policy=ArtifactPolicy(
                        origin_principal=internal,
                        cross_principal_allowed=False,
                        authorized_transformations=authorized_transformations,
                    ),
                )
            )
            scenario_index += 1

    if len(scenarios) != 24:
        raise AssertionError(f"Expected 24 delegation scenarios, constructed {len(scenarios)}")
    return scenarios
