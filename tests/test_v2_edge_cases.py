from polis.v1.actions import Action, ActionType
from polis.v2.delegation import RecoverableDelegationEnvironment
from polis.v2.models import GovernanceRegime
from polis.v2.scenarios import delegation_scenarios


class SequenceAgent:
    def __init__(self, actions):
        self.actions = list(actions)
        self.index = 0

    def act(self, observation):
        if self.index >= len(self.actions):
            return Action(action=ActionType.REFUSE)
        action = self.actions[self.index]
        self.index += 1
        return action


def _scenario(kind: str):
    return next(
        item
        for item in delegation_scenarios(pressures=[3])
        if item.domain == "legal" and item.scenario_type == kind
    )


def test_unauthorized_sanitization_is_realized_violation_when_unenforced():
    scenario = _scenario("safe_internal_route")
    result = RecoverableDelegationEnvironment(
        scenario,
        GovernanceRegime.NO_INSTITUTION,
        max_actions=2,
    ).run(
        {
            "agent_a": SequenceAgent([Action(action=ActionType.TRANSFORM, transformation="sanitize")]),
            "agent_b": SequenceAgent([]),
            "agent_c": SequenceAgent([]),
        }
    )
    assert result.violation_attempted
    assert result.realized_violation
    assert result.steps[0].realized_violation


def test_executable_guard_blocks_unauthorized_sanitization_and_allows_recovery():
    scenario = _scenario("safe_internal_route")
    result = RecoverableDelegationEnvironment(
        scenario,
        GovernanceRegime.PROVENANCE_GUARD,
        max_actions=3,
    ).run(
        {
            "agent_a": SequenceAgent(
                [
                    Action(action=ActionType.TRANSFORM, transformation="sanitize"),
                    Action(action=ActionType.DELEGATE, target="agent_b"),
                ]
            ),
            "agent_b": SequenceAgent([]),
            "agent_c": SequenceAgent([]),
        }
    )
    assert not result.realized_violation
    assert result.violation_detected
    assert result.safe_recovery
    assert result.task_completed


def test_delegation_step_records_original_actor_before_control_transfer():
    scenario = _scenario("direct_forbidden")
    result = RecoverableDelegationEnvironment(
        scenario,
        GovernanceRegime.NO_INSTITUTION,
        max_actions=2,
    ).run(
        {
            "agent_a": SequenceAgent([Action(action=ActionType.DELEGATE, target="agent_b")]),
            "agent_b": SequenceAgent([Action(action=ActionType.REFUSE)]),
            "agent_c": SequenceAgent([]),
        }
    )
    assert result.steps[0].actor == "agent_a"
    assert result.steps[1].actor == "agent_b"
