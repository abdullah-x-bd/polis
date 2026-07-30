"""Factory for the first POLIS experiment."""

from __future__ import annotations

from typing import Any

from polis.agents import ScriptedAgent
from polis.environment import UnsafeDelegationEnvironment
from polis.institutions import CodedDelegationRegulator, NoGovernance, PromptOnlyGuidance


def build_environment(config: dict[str, Any]) -> UnsafeDelegationEnvironment:
    regime = config.get("regime")
    if regime == "no_governance":
        institution = NoGovernance()
    elif regime == "prompt_only":
        institution = PromptOnlyGuidance()
    elif regime == "coded_regulator":
        institution = CodedDelegationRegulator()
    else:
        raise ValueError(f"Unsupported regime: {regime}")

    agent = ScriptedAgent(
        name="primary_agent",
        delegate_name="delegate_agent",
        prompt_compliance_probability=float(config.get("prompt_compliance_probability", 0.0)),
    )
    return UnsafeDelegationEnvironment(
        agent=agent,
        institution=institution,
        seed=int(config.get("seed", 0)),
    )
