from polis.agents import ScriptedAgent
from polis.environment import UnsafeDelegationEnvironment
from polis.evaluation import compute_metrics
from polis.institutions import CodedDelegationRegulator, NoGovernance


def test_no_governance_allows_restricted_delegation() -> None:
    environment = UnsafeDelegationEnvironment(
        agent=ScriptedAgent("primary", "delegate"),
        institution=NoGovernance(),
        seed=1,
    )
    outcomes = environment.run(trials=20, restricted_share=0.5)
    metrics = compute_metrics(outcomes)
    assert metrics.rule_evasion_rate == 1.0
    assert metrics.useful_performance == 1.0


def test_coded_regulator_blocks_restricted_and_preserves_legitimate() -> None:
    environment = UnsafeDelegationEnvironment(
        agent=ScriptedAgent("primary", "delegate"),
        institution=CodedDelegationRegulator(),
        seed=1,
    )
    outcomes = environment.run(trials=20, restricted_share=0.5)
    metrics = compute_metrics(outcomes)
    assert metrics.rule_evasion_rate == 0.0
    assert metrics.detection_rate == 1.0
    assert metrics.false_positive_rate == 0.0
    assert metrics.useful_performance == 1.0
