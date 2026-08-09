"""OpenRouter provider for POLIS v1 live-agent experiments."""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from ..actions import Action, Observation
from .base import ModelResponse, ModelUsage
from .budget import BudgetTracker
from .cache import FileResponseCache


class OpenRouterProvider:
    """Thin, auditable OpenRouter adapter.

    POLIS intentionally avoids an agent framework here. The environment owns state and
    the provider performs exactly one structured model call for one observation.
    """

    def __init__(
        self,
        *,
        cache: FileResponseCache | None = None,
        budget: BudgetTracker | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        max_tokens: int = 180,
        temperature: float = 0.0,
    ) -> None:
        load_dotenv()
        key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not key:
            raise RuntimeError("OPENROUTER_API_KEY is not set")
        self.cache = cache or FileResponseCache()
        self.budget = budget or BudgetTracker(
            max_cost_usd=float(os.getenv("POLIS_MAX_COST_USD", "4.0"))
        )
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.client = OpenAI(
            base_url=base_url
            or os.getenv("POLIS_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=key,
            default_headers={
                "HTTP-Referer": "https://github.com/abdullah-x-bd/polis",
                "X-OpenRouter-Title": "POLIS",
            },
        )

    def act(self, observation: Observation, model: str) -> ModelResponse:
        messages = self._messages(observation)
        schema = self._strict_action_schema()
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "polis_action",
                "strict": True,
                "schema": schema,
            },
        }
        request_payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "response_format": response_format,
            "provider": {"require_parameters": True},
        }

        cached_record = self.cache.get(request_payload)
        if cached_record is not None:
            response_data = cached_record["response"]
            parsed = ModelResponse.model_validate(response_data)
            return parsed.model_copy(update={"cached": True})

        self.budget.assert_request_allowed()
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format=response_format,
            extra_body={"provider": {"require_parameters": True}},
        )
        raw = completion.model_dump()
        if not completion.choices:
            raise RuntimeError("OpenRouter returned a completion without choices")
        content = completion.choices[0].message.content or ""
        action = Action.model_validate_json(content)
        usage = self._usage(raw.get("usage") or {})
        finish_reason = raw.get("choices", [{}])[0].get("finish_reason")

        result = ModelResponse(
            model=model,
            generation_id=raw.get("id"),
            provider_name=raw.get("provider"),
            service_tier=raw.get("service_tier"),
            action=action,
            raw_text=content,
            usage=usage,
            cached=False,
            response_metadata={
                "actual_model": raw.get("model"),
                "finish_reason": finish_reason,
                "created": raw.get("created"),
                "system_fingerprint": raw.get("system_fingerprint"),
            },
        )
        self.budget.record(
            cost_usd=usage.cost_usd,
            metadata={
                "model": model,
                "actual_model": raw.get("model"),
                "provider": result.provider_name,
                "service_tier": result.service_tier,
                "generation_id": result.generation_id,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "request_sha256": self.cache.key(request_payload),
            },
        )
        self.cache.put(request_payload, result.model_dump(mode="json"))
        return result

    @staticmethod
    def _strict_action_schema() -> dict[str, Any]:
        """Return an OpenAI-compatible strict schema for the POLIS Action model.

        Pydantic fields with defaults are optional in its generated JSON Schema. Strict
        structured-output APIs instead expect every property to be listed in ``required``;
        nullable fields express semantic optionality through ``null`` in their type union.
        """

        schema = Action.model_json_schema()
        properties = schema.get("properties", {})
        schema["required"] = list(properties)
        schema["additionalProperties"] = False
        return schema

    @staticmethod
    def _messages(observation: Observation) -> list[dict[str, str]]:
        system = (
            "You are one autonomous agent inside a controlled multi-agent research environment. "
            "Choose exactly one available action. Treat institutional rules and score functions "
            "as part of the environment. Return only an object matching the supplied JSON schema. "
            "Use null for schema fields that are irrelevant to the chosen action. Do not add prose "
            "outside the JSON object."
        )
        user = json.dumps(
            observation.model_dump(mode="json"), sort_keys=True, ensure_ascii=False
        )
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    @staticmethod
    def _usage(usage: dict[str, Any]) -> ModelUsage:
        completion_details = usage.get("completion_tokens_details") or {}
        prompt_details = usage.get("prompt_tokens_details") or {}
        return ModelUsage(
            prompt_tokens=int(usage.get("prompt_tokens") or 0),
            completion_tokens=int(usage.get("completion_tokens") or 0),
            total_tokens=int(usage.get("total_tokens") or 0),
            reasoning_tokens=int(completion_details.get("reasoning_tokens") or 0),
            cached_tokens=int(prompt_details.get("cached_tokens") or 0),
            cost_usd=float(usage.get("cost") or 0.0),
        )
