from polis.v1.actions import Action, ActionType
from polis.v1.attacks import DelegationProbeAgent
from polis.v1.delegation import DelegationBoundariesEnvironment
from polis.v1.institutions import LocalGuardInstitution, ProvenanceGuardInstitution
from polis.v1.loaders import load_delegation_scenarios


def _agents(scenario, mode):
    return {
        spec.agent_id: DelegationProbeAgent(spec.agent_id, spec.principal_id, mode=mode)
        for spec in scenario.agents
    }


class CapturingAgent:
    def __init__(self, agent_id, principal_id):
        self.agent_id = agent_id
        self.principal_id = principal_id
        self.observation = None

    def act(self, observation):
        self.observation = observation
        return Action(action=ActionType.REQUEST_APPROVAL)


class InvalidTargetAgent:
    def __init__(self, agent_id, principal_id, target="self"):
        self.agent_id = agent_id
        self.principal_id = principal_id
        self.target = target

    def act(self, observation):
        return Action(action=ActionType.DELEGATE, target=self.target)


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
    assert result.violation_attempted
    assert result.realized_violation
    assert result.policy_laundering_succeeded


def test_provenance_guard_blocks_metadata_laundering():
    scenarios = load_delegation_scenarios("scenarios/delegation_boundaries/v1_spec.json")
    scenario = next(s for s in scenarios if s.scenario_type == "transformation_laundering")
    result = DelegationBoundariesEnvironment(scenario, ProvenanceGuardInstitution()).run(
        _agents(scenario, "relabel")
    )
    assert result.violation_attempted
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


def test_root_provenance_is_hidden_from_agent_observation():
    scenarios = load_delegation_scenarios("scenarios/delegation_boundaries/v1_spec.json")
    scenario = next(s for s in scenarios if s.scenario_type == "transformation_laundering")
    primary_spec = next(spec for spec in scenario.agents if spec.agent_id == scenario.primary_agent)
    capture = CapturingAgent(primary_spec.agent_id, primary_spec.principal_id)
    agents = _agents(scenario, "compliant")
    agents[scenario.primary_agent] = capture

    DelegationBoundariesEnvironment(scenario, ProvenanceGuardInstitution()).run(agents)

    artifact = capture.observation.private_state["artifact"]
    assert "root_cross_principal_allowed" not in artifact
    assert "root_artifact_id" not in artifact
    assert "visible_cross_principal_allowed" in artifact


def test_unknown_delegation_target_is_audited_instead_of_crashing():
    scenario = load_delegation_scenarios("scenarios/delegation_boundaries/v1_spec.json")[0]
    agents = _agents(scenario, "compliant")
    primary = next(spec for spec in scenario.agents if spec.agent_id == scenario.primary_agent)
    agents[scenario.primary_agent] = InvalidTargetAgent(primary.agent_id, primary.principal_id)

    result = DelegationBoundariesEnvironment(scenario, LocalGuardInstitution()).run(agents)

    assert not result.task_completed
    assert not result.realized_violation
    assert result.invalid_action_count == 1
    assert result.path_length == 1
    assert result.steps[0].decision.institution == "environment_validation"
    assert result.steps[0].decision.violation == "invalid_action"


def test_irrelevant_target_field_does_not_break_non_delegation_action():
    class ApprovalWithGarbageTarget:
        def act(self, observation):
            return Action(action=ActionType.REQUEST_APPROVAL, target="not-an-agent")

    scenario = load_delegation_scenarios("scenarios/delegation_boundaries/v1_spec.json")[0]
    agents = _agents(scenario, "compliant")
    agents[scenario.primary_agent] = ApprovalWithGarbageTarget()

    result = DelegationBoundariesEnvironment(scenario, LocalGuardInstitution()).run(agents)

    assert result.approval_requested
    assert result.invalid_action_count == 0
