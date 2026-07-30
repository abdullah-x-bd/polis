from polis.institutions import CodedDelegationRegulator
from polis.models import Action


def test_regulator_blocks_restricted_delegation() -> None:
    regulator = CodedDelegationRegulator()
    action = Action(
        actor="primary",
        action_type="delegate",
        task_id="restricted-1",
        task_kind="restricted",
        target="delegate",
    )
    decision = regulator.evaluate(action)
    assert decision.allowed is False
    assert decision.detected is True
    assert decision.violation == "unauthorised_delegation"


def test_regulator_allows_legitimate_delegation() -> None:
    regulator = CodedDelegationRegulator()
    action = Action(
        actor="primary",
        action_type="delegate",
        task_id="legitimate-1",
        task_kind="legitimate",
        target="delegate",
    )
    decision = regulator.evaluate(action)
    assert decision.allowed is True
    assert decision.detected is False
