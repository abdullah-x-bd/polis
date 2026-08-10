from pathlib import Path

from polis.v1.actions import Action, ActionType
from polis.v1.providers.base import ModelResponse, ModelUsage
from polis.v2.commons import QuotaSalienceEnvironment
from polis.v2.delegation import RecoverableDelegationEnvironment
from polis.v2.live import build_episode_specs, load_records, run_study
from polis.v2.models import CommonsRegime, GovernanceRegime
from polis.v2.protocol import load_protocol
from polis.v2.scenarios import (
    HETEROGENEOUS_COMPOSITIONS,
    commons_scenarios,
    delegation_scenarios,
    design_digest,
    frontier_scenarios,
    heterogeneous_scenarios,
    wording_robustness_scenarios,
)


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


class TruthfulCommonsAgent:
    def act(self, observation):
        return Action(action=ActionType.REQUEST_RESOURCE, amount=int(observation.private_state["your_need"]))


class CapSeekingCommonsAgent:
    def act(self, observation):
        return Action(action=ActionType.REQUEST_RESOURCE, amount=30)


class FakeProvider:
    def act(self, observation, model):
        if observation.environment == "polis_v2_commons_salience":
            action = Action(action=ActionType.REQUEST_RESOURCE, amount=int(observation.private_state["your_need"]))
        else:
            artifact = observation.private_state["artifact"]
            agents = observation.public_state["agents"]
            internal = next(item for item in agents if item["principal_id"] == observation.principal_id and item["agent_id"] != observation.agent_id and observation.public_state["required_capability"] in item["capabilities"])
            action = Action(action=ActionType.DELEGATE, target=internal["agent_id"], artifact_id=artifact["artifact_id"])
        return ModelResponse(
            model=model,
            generation_id="fake",
            action=action,
            raw_text=action.model_dump_json(),
            usage=ModelUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
        )


def _scenario(kind: str, pressure: int = 3):
    return next(
        item
        for item in delegation_scenarios(pressures=[pressure])
        if item.domain == "legal" and item.scenario_type == kind
    )


def test_v2_design_counts_are_frozen_and_fresh():
    assert len(delegation_scenarios()) == 96
    assert len(wording_robustness_scenarios()) == 72
    assert len(heterogeneous_scenarios()) == 24
    assert len(frontier_scenarios()) == 24
    assert len(commons_scenarios()) == 48
    assert len(HETEROGENEOUS_COMPOSITIONS) == 8
    assert all(item.scenario_id.startswith("v2-") for item in delegation_scenarios())
    assert len(design_digest()) == 64


def test_recoverable_guard_allows_safe_recovery_after_block():
    scenario = _scenario("safe_internal_route")
    agents = {
        "agent_a": SequenceAgent([
            Action(action=ActionType.DELEGATE, target="agent_c"),
            Action(action=ActionType.DELEGATE, target="agent_b"),
        ]),
        "agent_b": SequenceAgent([]),
        "agent_c": SequenceAgent([]),
    }
    result = RecoverableDelegationEnvironment(
        scenario,
        GovernanceRegime.PROVENANCE_GUARD,
        max_actions=6,
    ).run(agents)
    assert not result.realized_violation
    assert result.task_completed
    assert result.compliant_completion
    assert result.safe_recovery
    assert result.blocked_attempt_occurred
    assert result.intervention_count == 1
    assert result.path_length == 2


def test_local_guard_is_launderable_but_provenance_guard_is_not():
    scenario = _scenario("transformation_laundering")
    attack = [
        Action(action=ActionType.TRANSFORM, transformation="summarize"),
        Action(action=ActionType.DELEGATE, target="agent_c"),
    ]
    local = RecoverableDelegationEnvironment(
        scenario,
        GovernanceRegime.LOCAL_GUARD,
        max_actions=6,
    ).run({"agent_a": SequenceAgent(attack), "agent_b": SequenceAgent([]), "agent_c": SequenceAgent([])})
    provenance = RecoverableDelegationEnvironment(
        scenario,
        GovernanceRegime.PROVENANCE_GUARD,
        max_actions=6,
    ).run({"agent_a": SequenceAgent(attack), "agent_b": SequenceAgent([]), "agent_c": SequenceAgent([])})
    assert local.realized_violation
    assert local.laundering_succeeded
    assert not provenance.realized_violation
    assert provenance.blocked_attempt_occurred


def test_authorized_sanitization_preserves_safe_external_completion():
    scenario = _scenario("authorized_sanitization")
    actions = [
        Action(action=ActionType.TRANSFORM, transformation="sanitize"),
        Action(action=ActionType.DELEGATE, target="agent_c"),
    ]
    result = RecoverableDelegationEnvironment(
        scenario,
        GovernanceRegime.PROVENANCE_GUARD,
        max_actions=6,
    ).run({"agent_a": SequenceAgent(actions), "agent_b": SequenceAgent([]), "agent_c": SequenceAgent([])})
    assert result.task_completed
    assert result.compliant_completion
    assert not result.realized_violation
    assert result.task_value == scenario.external_value


def test_direct_forbidden_has_real_self_execution_route():
    scenario = _scenario("direct_forbidden", pressure=2)
    assert scenario.required_capability in next(item for item in scenario.agents if item.agent_id == "agent_a").capabilities
    result = RecoverableDelegationEnvironment(
        scenario,
        GovernanceRegime.CONSTITUTIONAL_PROMPT,
    ).run({"agent_a": SequenceAgent([Action(action=ActionType.EXECUTE)]), "agent_b": SequenceAgent([]), "agent_c": SequenceAgent([])})
    assert result.task_completed
    assert result.compliant_completion
    assert result.task_value == scenario.internal_value


def test_commons_visible_cap_can_be_measured_as_focal_point():
    scenario = commons_scenarios()[0]
    agents = {item.agent_id: CapSeekingCommonsAgent() for item in scenario.agents}
    result = QuotaSalienceEnvironment(scenario, CommonsRegime.VISIBLE_CAP).run(agents, model_name="scripted")
    eligible = sum(item.need < 30 for item in scenario.agents)
    assert eligible > 0
    assert result.cap_seeking_rate == 1.0
    assert result.overclaim_ratio > 0


def test_commons_truthful_policy_hits_true_needs():
    scenario = commons_scenarios()[0]
    agents = {item.agent_id: TruthfulCommonsAgent() for item in scenario.agents}
    result = QuotaSalienceEnvironment(scenario, CommonsRegime.NO_CAP).run(agents, model_name="scripted")
    assert result.overclaim_ratio == 0
    assert result.invalid_action_count == 0


def test_v2_full_plan_sizes():
    protocol = load_protocol("configs/v2_protocol.json")
    assert len(build_episode_specs(protocol, "delegation_main")) == 96 * 6 * 4
    assert len(build_episode_specs(protocol, "wording_robustness")) == 72 * 4 * 4
    assert len(build_episode_specs(protocol, "heterogeneous")) == 24 * 3 * 8
    assert len(build_episode_specs(protocol, "commons_salience")) == 48 * 5 * 4
    assert len(build_episode_specs(protocol, "frontier")) == 24 * 4 * 3


def test_live_runner_is_resumable_when_protocol_is_frozen(tmp_path: Path):
    protocol = load_protocol("configs/v2_protocol.json").model_copy(update={"status": "frozen", "frozen_date": "2026-08-10"})
    manifest = run_study(
        protocol=protocol,
        provider=FakeProvider(),
        study="commons_salience",
        output_dir=tmp_path,
        shard_index=0,
        shard_count=960,
        run_id="tiny-v2",
    )
    assert manifest.status == "complete"
    records = load_records(tmp_path / "tiny-v2.jsonl")
    assert len(records) == 1
    second = run_study(
        protocol=protocol,
        provider=FakeProvider(),
        study="commons_salience",
        output_dir=tmp_path,
        shard_index=0,
        shard_count=960,
        run_id="tiny-v2",
    )
    assert second.completed_episodes == 1
    assert len(load_records(tmp_path / "tiny-v2.jsonl")) == 1
