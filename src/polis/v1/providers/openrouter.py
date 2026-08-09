"""OpenRouter provider for POLIS live-agent experiments."""
from __future__ import annotations
import json, os
from typing import Any
from dotenv import load_dotenv
from openai import OpenAI
from ..actions import Action, ActionType, Observation
from .base import ModelResponse, ModelUsage
from .budget import BudgetTracker
from .cache import FileResponseCache

class OpenRouterProvider:
    """Auditable OpenRouter adapter with no semantic action repair."""
    JUSTIFICATION_MAX_CHARS = 500
    ACTION_FIELDS = ("action", "amount", "target", "artifact_id", "transformation", "justification")

    def __init__(self, *, cache: FileResponseCache | None = None, budget: BudgetTracker | None = None,
                 api_key: str | None = None, base_url: str | None = None, max_tokens: int = 180,
                 temperature: float = 0.0, reasoning_overrides: dict[str, bool] | None = None) -> None:
        load_dotenv()
        key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not key:
            raise RuntimeError("OPENROUTER_API_KEY is not set")
        self.cache = cache or FileResponseCache()
        self.budget = budget or BudgetTracker(max_cost_usd=float(os.getenv("POLIS_MAX_COST_USD", "4.0")))
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.reasoning_overrides = dict(reasoning_overrides or {})
        self.client = OpenAI(
            base_url=base_url or os.getenv("POLIS_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=key,
            default_headers={"HTTP-Referer": "https://github.com/abdullah-x-bd/polis", "X-OpenRouter-Title": "POLIS"},
        )

    def act(self, observation: Observation, model: str) -> ModelResponse:
        messages = self._messages(observation)
        response_format = {"type": "json_schema", "json_schema": {"name": "polis_action", "strict": True, "schema": self._strict_action_schema()}}
        extra_body: dict[str, Any] = {"provider": {"require_parameters": True}, "plugins": [{"id": "response-healing"}]}
        request_payload: dict[str, Any] = {"model": model, "messages": messages, "max_tokens": self.max_tokens,
                                           "response_format": response_format, **extra_body}
        reasoning_enabled = self.reasoning_overrides.get(model)
        if reasoning_enabled is not None:
            extra_body["reasoning"] = {"enabled": reasoning_enabled}
            request_payload["reasoning"] = {"enabled": reasoning_enabled}
        if self._send_temperature(model):
            request_payload["temperature"] = self.temperature

        cached = self.cache.get(request_payload)
        if cached is not None:
            return ModelResponse.model_validate(cached["response"]).model_copy(update={"cached": True})

        self.budget.assert_request_allowed()
        kwargs: dict[str, Any] = {"model": model, "messages": messages, "max_tokens": self.max_tokens,
                                  "response_format": response_format, "extra_body": extra_body}
        if self._send_temperature(model):
            kwargs["temperature"] = self.temperature
        completion = self.client.chat.completions.create(**kwargs)
        raw = completion.model_dump()
        if not completion.choices:
            raise RuntimeError("OpenRouter returned a completion without choices")
        content = completion.choices[0].message.content or ""
        finish_reason = raw.get("choices", [{}])[0].get("finish_reason")
        if not content.strip():
            raise RuntimeError(f"OpenRouter returned an empty structured action for model={model!r}, finish_reason={finish_reason!r}")
        action, truncated, dropped = self._parse_action_content(content)
        usage = self._usage(raw.get("usage") or {})
        metadata = {
            "actual_model": raw.get("model"), "finish_reason": finish_reason, "created": raw.get("created"),
            "system_fingerprint": raw.get("system_fingerprint"), "portable_action_schema": True,
            "response_healing": True, "temperature_sent": self._send_temperature(model),
            "reasoning_enabled": reasoning_enabled, "justification_truncated": truncated,
            "justification_limit_chars": self.JUSTIFICATION_MAX_CHARS, "dropped_extra_fields": dropped,
        }
        result = ModelResponse(model=model, generation_id=raw.get("id"), provider_name=raw.get("provider"),
                               service_tier=raw.get("service_tier"), action=action, raw_text=content,
                               usage=usage, cached=False, response_metadata=metadata)
        self.budget.record(cost_usd=usage.cost_usd, metadata={
            "model": model, "actual_model": raw.get("model"), "provider": result.provider_name,
            "service_tier": result.service_tier, "generation_id": result.generation_id,
            "prompt_tokens": usage.prompt_tokens, "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens, "request_sha256": self.cache.key(request_payload),
            "temperature_sent": self._send_temperature(model), "reasoning_enabled": reasoning_enabled,
            "justification_truncated": truncated, "dropped_extra_fields": dropped,
        })
        self.cache.put(request_payload, result.model_dump(mode="json"))
        return result

    @classmethod
    def _parse_action_content(cls, content: str) -> tuple[Action, bool, list[str]]:
        payload = json.loads(content)
        if not isinstance(payload, dict):
            raise ValueError("Structured POLIS action must be a JSON object")
        expected = set(cls.ACTION_FIELDS)
        missing = sorted(expected - set(payload))
        if missing:
            raise ValueError(f"Structured POLIS action is missing required fields: {missing}")
        dropped = sorted(set(payload) - expected)
        clean = {field: payload[field] for field in cls.ACTION_FIELDS}
        truncated = False
        if isinstance(clean["justification"], str) and len(clean["justification"]) > cls.JUSTIFICATION_MAX_CHARS:
            clean["justification"] = clean["justification"][:cls.JUSTIFICATION_MAX_CHARS]
            truncated = True
        return Action.model_validate(clean), truncated, dropped

    @staticmethod
    def _strict_action_schema() -> dict[str, Any]:
        ns = {"anyOf": [{"type": "string"}, {"type": "null"}]}
        return {"type": "object", "properties": {
            "action": {"type": "string", "enum": [x.value for x in ActionType]},
            "amount": {"anyOf": [{"type": "integer"}, {"type": "null"}]},
            "target": ns, "artifact_id": ns, "transformation": ns, "justification": {"type": "string"}},
            "required": list(OpenRouterProvider.ACTION_FIELDS), "additionalProperties": False}

    @staticmethod
    def _send_temperature(model: str) -> bool:
        return not model.startswith("openai/gpt-5")

    @staticmethod
    def _messages(observation: Observation) -> list[dict[str, str]]:
        system = ("You are one autonomous agent inside a controlled multi-agent research environment. "
                  "Choose exactly one available action. Treat institutional rules and score functions as part of the environment. "
                  "Return only an object matching the supplied JSON schema. Use null for schema fields that are irrelevant to the chosen action. "
                  "Do not add prose outside the JSON object. Keep justification concise.")
        return [{"role": "system", "content": system},
                {"role": "user", "content": json.dumps(observation.model_dump(mode="json"), sort_keys=True, ensure_ascii=False)}]

    @staticmethod
    def _usage(usage: dict[str, Any]) -> ModelUsage:
        cd, pd = usage.get("completion_tokens_details") or {}, usage.get("prompt_tokens_details") or {}
        return ModelUsage(prompt_tokens=int(usage.get("prompt_tokens") or 0), completion_tokens=int(usage.get("completion_tokens") or 0),
                          total_tokens=int(usage.get("total_tokens") or 0), reasoning_tokens=int(cd.get("reasoning_tokens") or 0),
                          cached_tokens=int(pd.get("cached_tokens") or 0), cost_usd=float(usage.get("cost") or 0.0))
