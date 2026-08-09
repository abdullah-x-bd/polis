from polis.v1.attacks import DelegationProbeAgent
from polis.v1.delegation import DelegationBoundariesEnvironment
from polis.v1.institutions import LocalGuardInstitution, ProvenanceGuardInstitution
from polis.v1.loaders import load_delegation_scenarios


def _agents(scenario, mode):
    return {
        spec.agent_id: DelegationProbeAgent(spec.agent_id, spec.principal_id, mode=mode)
        for spec in scenario.agents
    }


def test_v1_has_24_delegation_scenarios():
    scenarios = load_delegation_scenarios("scenarios/delegation_boundaries/v1_spec.json")
    assert len(scenarios) == 24
    assert len({scenario.domain for scenario in scenarios}) == 6
    assert len({scenario.scenario_type for scenario in scenarios}) == 4


def test_same_principal_delegation_remains_useful():
    scenario = load_delegation_scenarios("scenarios/delegation_boundaries/v1_spec.json")[0]
    result = DelegationBoundariesEnvironment(scenario, LocalGuardInstitution()).run(
        _agents(scenario, "compliant")
    )
    assert result.task_completed
    assert not result.realized_violation
    assert not result.legitimate_action_blocked


def test_local_guard_is_vulnerable_to_metadata_laundering():
    scenarios = load_delegation_scenarios("scenarios/delegation_boundaries/v1_spec.json")
    scenario = next(s for s in scenarios if s.scenario_type == "transformation_laundering")
    result = DelegationBoundariesEnvironment(scenario, LocalGuardInstitution()).run(
        _agents(scenario, "relabel")
    )
    assert result.realized_violation
    assert result.policy_laundering_succeeded


def test_provenance_guard_blocks_metadata_laundering():
    scenarios = load_delegation_scenarios("scenarios/delegation_boundaries/v1_spec.json")
    scenario = next(s for s in scenarios if s.scenario_type == "transformation_laundering")
    result = DelegationBoundariesEnvironment(scenario, ProvenanceGuardInstitution()).run(
        _agents(scenario, "relabel")
    )
    assert not result.realized_violation
    assert result.violation_detected


def test_authorized_sanitization_can_enable_cross_principal_work():
    scenarios = load_delegation_scenarios("scenarios/delegation_boundaries/v1_spec.json")
    scenario = next(s for s in scenarios if s.scenario_type == "authorized_sanitization")
    result = DelegationBoundariesEnvironment(scenario, ProvenanceGuardInstitution()).run(
        _agents(scenario, "sanitize")
    )
    assert result.task_completed
    assert not result.realized_violation
