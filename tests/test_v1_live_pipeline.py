from pathlib import Path

from polis.v1.actions import Action, ActionType
from polis.v1.analysis import analyse_records
from polis.v1.live import build_plan, load_records, run_live_matrix
from polis.v1.protocol import load_protocol
from polis.v1.providers.base import ModelResponse, ModelUsage


class FakeProvider:
    def act(self, observation, model):
        if observation.environment == "resource_commons":
            action = Action(
                action=ActionType.REQUEST_RESOURCE,
                amount=int(observation.private_state["need"]),
            )
        else:
            task = observation.private_state["task"]
            target = observation.private_state["preferred_target"]
            artifact_id = observation.private_state["artifact"]["artifact_id"]
            if target in task.get("allowed_targets", []):
                action = Action(
                    action=ActionType.DELEGATE,
                    target=target,
                    artifact_id=artifact_id,
                )
            else:
                action = Action(
                    action=ActionType.REQUEST_APPROVAL,
                    artifact_id=artifact_id,
                )
        return ModelResponse(
            model=model,
            generation_id="fake",
            action=action,
            raw_text=action.model_dump_json(),
            usage=ModelUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
        )


def test_frozen_protocol_has_three_cross_family_models():
    protocol = load_protocol("configs/v1_live.json")
    assert len(protocol.models) == 3
    assert len({model.provider_family for model in protocol.models}) == 3
    assert len(protocol.fingerprint()) == 64


def test_full_plan_has_expected_episode_and_call_ceiling():
    protocol = load_protocol("configs/v1_live.json")
    plan = build_plan(protocol, "full")
    assert plan.commons_episodes == 3 * 24 * 4
    assert plan.delegation_episodes == 3 * 24 * 4
    assert plan.episodes == 576
    assert plan.maximum_model_calls == 3456


def test_four_shards_exactly_partition_full_matrix():
    protocol = load_protocol("configs/v1_live.json")
    plans = [
        build_plan(protocol, "full", shard_index=index, shard_count=4)
        for index in range(4)
    ]
    assert [plan.commons_worlds for plan in plans] == [6, 6, 6, 6]
    assert [plan.delegation_scenarios for plan in plans] == [6, 6, 6, 6]
    assert sum(plan.episodes for plan in plans) == 576
    assert sum(plan.maximum_model_calls for plan in plans) == 3456


def test_pilot_runner_is_resumable_and_analysis_ready(tmp_path: Path):
    protocol = load_protocol("configs/v1_live.json")
    model = protocol.models[0].id
    manifest = run_live_matrix(
        protocol=protocol,
        provider=FakeProvider(),
        output_dir=tmp_path,
        mode="pilot",
        selected_models=[model],
        run_id="test-pilot",
    )
    assert manifest.status == "complete"
    assert manifest.expected_episodes == 28
    assert manifest.completed_episodes == 28

    records = load_records(tmp_path / "test-pilot.jsonl")
    assert len(records) == 28
    assert {record.protocol_fingerprint for record in records} == {protocol.fingerprint()}

    second = run_live_matrix(
        protocol=protocol,
        provider=FakeProvider(),
        output_dir=tmp_path,
        mode="pilot",
        selected_models=[model],
        run_id="test-pilot",
    )
    assert second.completed_episodes == 28
    assert len(load_records(tmp_path / "test-pilot.jsonl")) == 28

    analysis = analyse_records(records, protocol)
    assert analysis["completeness"]["single_protocol_fingerprint"]
    assert analysis["costs"]["total_model_calls"] > 0
    primary = [
        row
        for row in analysis["contrasts"]
        if row["endpoint"] in {"efficiency_ratio", "realized_violation"}
    ]
    assert primary
    assert all(row["p_adjusted"] is not None for row in primary)
