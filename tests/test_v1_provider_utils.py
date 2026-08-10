import json

import pytest
from pydantic import ValidationError

from polis.v1.actions import Action
from polis.v1.providers.budget import BudgetExceeded, BudgetTracker
from polis.v1.providers.cache import FileResponseCache
from polis.v1.providers.openrouter import OpenRouterProvider


def test_file_cache_round_trip(tmp_path):
    cache = FileResponseCache(tmp_path / "cache")
    request = {"model": "test", "messages": [{"role": "user", "content": "x"}]}
    response = {"ok": True, "value": 3}
    cache.put(request, response)
    record = cache.get(request)
    assert record is not None
    assert record["response"] == response
    assert record["request_sha256"] == cache.key(request)


def test_budget_ledger_resumes_from_disk(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    first = BudgetTracker(max_cost_usd=1.0, ledger_path=ledger, reserve_per_request_usd=0.1)
    first.record(cost_usd=0.25, metadata={"model": "test"})
    second = BudgetTracker(max_cost_usd=1.0, ledger_path=ledger, reserve_per_request_usd=0.1)
    assert second.spent_usd == pytest.approx(0.25)
    assert second.remaining_usd == pytest.approx(0.75)


def test_budget_stops_before_reserved_request(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    tracker = BudgetTracker(max_cost_usd=0.2, ledger_path=ledger, reserve_per_request_usd=0.05)
    tracker.record(cost_usd=0.16, metadata={})
    with pytest.raises(BudgetExceeded):
        tracker.assert_request_allowed()


def test_openrouter_strict_schema_requires_every_action_property():
    schema = OpenRouterProvider._strict_action_schema()
    properties = schema["properties"]
    assert set(schema["required"]) == set(properties)
    assert schema["additionalProperties"] is False


def test_openrouter_wire_schema_uses_portable_structural_subset():
    schema = OpenRouterProvider._strict_action_schema()
    encoded = str(schema)
    for unsupported in ["minimum", "maximum", "minLength", "maxLength", "$ref", "$defs"]:
        assert unsupported not in encoded
    assert schema["properties"]["action"]["enum"]


def test_client_side_action_validation_remains_strict():
    with pytest.raises(ValidationError):
        Action.model_validate(
            {
                "action": "request_resource",
                "amount": -1,
                "target": None,
                "artifact_id": None,
                "transformation": None,
                "justification": "invalid negative amount",
            }
        )


def test_overlong_justification_is_deterministically_truncated_only():
    raw = json.dumps(
        {
            "action": "delegate",
            "amount": None,
            "target": "agent_b",
            "artifact_id": "artifact_1",
            "transformation": None,
            "justification": "x" * 731,
        }
    )
    action, truncated, dropped, filled = OpenRouterProvider._parse_action_content(raw)
    assert truncated is True
    assert dropped == []
    assert filled == []
    assert action.action.value == "delegate"
    assert action.target == "agent_b"
    assert action.artifact_id == "artifact_1"
    assert action.amount is None
    assert action.transformation is None
    assert action.justification == "x" * 500


def test_unknown_provider_field_is_dropped_and_audited_without_aliasing():
    raw = json.dumps(
        {
            "action": "delegate",
            "amount": None,
            "target": None,
            "artifact_id": "artifact_1",
            "transformation": None,
            "justification": "delegate using the schema target only",
            "agent": "agent_c",
        }
    )
    action, truncated, dropped, filled = OpenRouterProvider._parse_action_content(raw)
    assert truncated is False
    assert dropped == ["agent"]
    assert filled == []
    assert action.action.value == "delegate"
    assert action.target is None
    assert action.artifact_id == "artifact_1"


def test_multiple_unknown_fields_are_sorted_and_known_fields_untouched():
    raw = json.dumps(
        {
            "action": "execute",
            "amount": None,
            "target": "agent_b",
            "artifact_id": "artifact_1",
            "transformation": None,
            "justification": "valid",
            "zzz": 1,
            "agent": "agent_c",
        }
    )
    action, _, dropped, filled = OpenRouterProvider._parse_action_content(raw)
    assert dropped == ["agent", "zzz"]
    assert filled == []
    assert action.target == "agent_b"
    assert action.artifact_id == "artifact_1"


def test_missing_nullable_action_fields_are_filled_with_null_and_audited():
    raw = json.dumps(
        {
            "action": "refuse",
            "artifact_id": "artifact_1",
            "justification": "Cannot proceed under the current boundary.",
        }
    )
    action, truncated, dropped, filled = OpenRouterProvider._parse_action_content(raw)
    assert truncated is False
    assert dropped == []
    assert filled == ["amount", "target", "transformation"]
    assert action.action.value == "refuse"
    assert action.amount is None
    assert action.target is None
    assert action.artifact_id == "artifact_1"
    assert action.transformation is None


def test_missing_all_nullable_action_fields_is_valid_syntax_only_normalization():
    raw = json.dumps(
        {
            "action": "refuse",
            "justification": "No compliant action is useful.",
        }
    )
    action, _, _, filled = OpenRouterProvider._parse_action_content(raw)
    assert filled == ["amount", "artifact_id", "target", "transformation"]
    assert action.amount is None
    assert action.target is None
    assert action.artifact_id is None
    assert action.transformation is None


def test_missing_action_is_rejected():
    raw = json.dumps(
        {
            "amount": None,
            "target": None,
            "artifact_id": None,
            "transformation": None,
            "justification": "missing semantic action",
        }
    )
    with pytest.raises(ValueError, match="missing mandatory fields"):
        OpenRouterProvider._parse_action_content(raw)


def test_missing_justification_is_rejected():
    raw = json.dumps(
        {
            "action": "refuse",
            "amount": None,
            "target": None,
            "artifact_id": None,
            "transformation": None,
        }
    )
    with pytest.raises(ValueError, match="missing mandatory fields"):
        OpenRouterProvider._parse_action_content(raw)


def test_non_object_structured_action_is_rejected():
    with pytest.raises(ValueError, match="JSON object"):
        OpenRouterProvider._parse_action_content('["refuse"]')


def test_justification_canonicalization_does_not_repair_semantic_fields():
    raw = json.dumps(
        {
            "action": "request_resource",
            "amount": -1,
            "target": None,
            "artifact_id": None,
            "transformation": None,
            "justification": "x" * 731,
        }
    )
    with pytest.raises(ValidationError):
        OpenRouterProvider._parse_action_content(raw)


def test_missing_amount_for_resource_request_stays_semantically_missing():
    raw = json.dumps(
        {
            "action": "request_resource",
            "justification": "request without a numeric amount",
        }
    )
    action, _, _, filled = OpenRouterProvider._parse_action_content(raw)
    assert "amount" in filled
    assert action.amount is None


def test_in_limit_justification_is_not_marked_as_truncated():
    raw = json.dumps(
        {
            "action": "refuse",
            "amount": None,
            "target": None,
            "artifact_id": None,
            "transformation": None,
            "justification": "concise",
        }
    )
    action, truncated, dropped, filled = OpenRouterProvider._parse_action_content(raw)
    assert truncated is False
    assert dropped == []
    assert filled == []
    assert action.justification == "concise"


def test_gpt5_family_omits_unsupported_temperature():
    assert not OpenRouterProvider._send_temperature("openai/gpt-5-mini")
    assert not OpenRouterProvider._send_temperature("openai/gpt-5.4")
    assert OpenRouterProvider._send_temperature("openai/gpt-4.1-mini")
    assert OpenRouterProvider._send_temperature("anthropic/claude-sonnet-4.5")
