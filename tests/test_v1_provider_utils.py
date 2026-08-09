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


def test_gpt5_family_omits_unsupported_temperature():
    assert not OpenRouterProvider._send_temperature("openai/gpt-5-mini")
    assert not OpenRouterProvider._send_temperature("openai/gpt-5.4")
    assert OpenRouterProvider._send_temperature("openai/gpt-4.1-mini")
    assert OpenRouterProvider._send_temperature("anthropic/claude-sonnet-4.5")
