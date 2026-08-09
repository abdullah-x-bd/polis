#!/usr/bin/env python3
"""Zero-cost adversarial stress suite for POLIS v1 Delegation Boundaries."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from polis.v1.attacks import DelegationProbeAgent
from polis.v1.delegation import DelegationBoundariesEnvironment
from polis.v1.institutions import (
    LocalGuardInstitution,
    NoDelegationInstitution,
    PromptDelegationInstitution,
    ProvenanceGuardInstitution,
)
from polis.v1.loaders import load_delegation_scenarios


def make_agents(scenario, mode: str):
    return {
        spec.agent_id: DelegationProbeAgent(spec.agent_id, spec.principal_id, mode=mode)
        for spec in scenario.agents
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default="scenarios/delegation_boundaries/v1_spec.json")
    parser.add_argument("--output", default="results/calibration/delegation_v1.json")
    args = parser.parse_args()

    scenarios = load_delegation_scenarios(args.spec)
    institutions = [
        NoDelegationInstitution(),
        PromptDelegationInstitution(),
        LocalGuardInstitution(),
        ProvenanceGuardInstitution(),
    ]
    modes = ["compliant", "direct", "relabel", "sanitize"]

    records = []
    for scenario in scenarios:
        for institution in institutions:
            for mode in modes:
                episode = DelegationBoundariesEnvironment(scenario, institution).run(
                    make_agents(scenario, mode)
                )
                records.append(
                    {
                        "scenario_id": scenario.scenario_id,
                        "scenario_type": scenario.scenario_type,
                        "domain": scenario.domain,
                        "institution": institution.name,
                        "probe": mode,
                        "task_completed": episode.task_completed,
                        "violation_attempted": episode.violation_attempted,
                        "realized_violation": episode.realized_violation,
                        "violation_detected": episode.violation_detected,
                        "legitimate_action_blocked": episode.legitimate_action_blocked,
                        "policy_laundering_succeeded": episode.policy_laundering_succeeded,
                        "path_length": episode.path_length,
                    }
                )

    summary = defaultdict(lambda: {"trials": 0, "violations": 0, "completed": 0, "laundered": 0, "blocked_legitimate": 0})
    for row in records:
        key = f"{row['institution']}::{row['probe']}"
        bucket = summary[key]
        bucket["trials"] += 1
        bucket["violations"] += int(row["realized_violation"])
        bucket["completed"] += int(row["task_completed"])
        bucket["laundered"] += int(row["policy_laundering_succeeded"])
        bucket["blocked_legitimate"] += int(row["legitimate_action_blocked"])

    payload = {"records": records, "summary": dict(summary)}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))


if __name__ == "__main__":
    main()
