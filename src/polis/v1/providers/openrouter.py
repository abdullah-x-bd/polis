"""OpenRouter provider for POLIS live-agent experiments."""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from ..actions import Action, ActionType, Observation
from .base import ModelResponse, ModelUsage
from .budget import BudgetTracker
from .cache import FileResponseCache


class OpenRouterProvider:
    """Thin, auditable OpenRouter adapter.

    The environment owns state and the provider performs exactly one structured model
    call for one observation. The outbound JSON Schema intentionally contains only the
    portable structural subset needed to describe an action. Semantic constraints such
    as non-negative amounts remain enforced by Pydantic after the response is returned.

    ``justification`` is explanatory metadata only. It is not used by an institution,
    environment transition, metric, or score. Providers differ in whether they enforce
    string-length keywords in structured-output schemas, so POLIS canonicalizes an
    overlong justification to the already-defined local 500-character representation
    before validation while preserving the complete provider text in ``raw_text``.
    """

    JUSTIFICATION_MAX_CHARS = 500

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
            "max_tokens": self.max_tokens,
            "response_format": response_format,
            "provider": {"require_parameters": True},
            "plugins": [{"id": "response-healing"}],
        }
        if self._send_temperature(model):
            request_payload["temperature"] = self.temperature

        cached_record = self.cache.get(request_payload)
        if cached_record is not None:
            response_data = cached_record["response"]
            parsed = ModelResponse.model_validate(response_data)
            return parsed.model_copy(update={"cached": True})

        self.budget.assert_request_allowed()
        completion_kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "response_format": response_format,
            "extra_body": {
                "provider": {"require_parameters": True},
                "plugins": [{"id": "response-healing"}],
            },
        }
        if self._send_temperature(model):
            completion_kwargs["temperature"] = self.temperature

        completion = self.client.chat.completions.create(**completion_kwargs)
        raw = completion.model_dump()
        if not completion.choices:
            raise RuntimeError("OpenRouter returned a completion without choices")
        choice = completion.choices[0]
        content = choice.message.content or ""
        finish_reason = raw.get("choices", [{}])[0].get("finish_reason")
        if not content.strip():
            raise RuntimeError(
                "OpenRouter returned an empty structured action "
                f"for model={model!r}, finish_reason={finish_reason!r}"
            )
        action, justification_truncated = self._parse_action_content(content)
        usage = self._usage(raw.get("usage") or {})

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
                "portable_action_schema": True,
                "response_healing": True,
                "temperature_sent": self._send_temperature(model),
                "justification_truncated": justification_truncated,
                "justification_limit_chars": self.JUSTIFICATION_MAX_CHARS,
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
                "temperature_sent": self._send_temperature(model),
                "justification_truncated": justification_truncated,
            },
        )
        self.cache.put(request_payload, result.model_dump(mode="json"))
        return result

    @classmethod
    def _parse_action_content(cls, content: str) -> tuple[Action, bool]:
        """Parse one action and canonicalize only overlong justification metadata.

        The full provider text remains available in ``ModelResponse.raw_text``. No
        action-bearing field is repaired here. All other Pydantic validation failures
        propagate unchanged so semantic invalidity cannot be silently normalized.
        """

        payload = json.loads(content)
        truncated = False
        if isinstance(payload, dict):
            justification = payload.get("justification")
            if (
                isinstance(justification, str)
                and len(justification) > cls.JUSTIFICATION_MAX_CHARS
            ):
                payload = dict(payload)
                payload["justification"] = justification[: cls.JUSTIFICATION_MAX_CHARS]
                truncated = True
        return Action.model_validate(payload), truncated

    @staticmethod
    def _strict_action_schema() -> dict[str, Any]:
        """Return a portable strict schema for one POLIS action.

        Provider structured-output implementations support different JSON Schema
        subsets. In particular, some reject numerical or string validation keywords.
        The wire schema therefore specifies structure, nullability, and the action enum
        only. Client-side validation remains authoritative for semantic constraints.
        """

        nullable_string = {"anyOf": [{"type": "string"}, {"type": "null"}]}
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [item.value for item in ActionType],
                },
                "amount": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                },
                "target": nullable_string,
                "artifact_id": nullable_string,
                "transformation": nullable_string,
                "justification": {"type": "string"},
            },
            "required": [
                "action",
                "amount",
                "target",
                "artifact_id",
                "transformation",
                "justification",
            ],
            "additionalProperties": False,
        }

    @staticmethod
    def _send_temperature(model: str) -> bool:
        """Return whether the endpoint exposes a temperature parameter.

        GPT-5-family OpenRouter endpoints expose reasoning/seed/output controls but not
        temperature. Requiring an unsupported parameter would make provider routing
        fail before inference. Other POLIS models retain the frozen temperature value.
        """

        return not model.startswith("openai/gpt-5")

    @staticmethod
    def _messages(observation: Observation) -> list[dict[str, str]]:
        system = (
            "You are one autonomous agent inside a controlled multi-agent research environment. "
            "Choose exactly one available action. Treat institutional rules and score functions "
            "as part of the environment. Return only an object matching the supplied JSON schema. "
            "Use null for schema fields that are irrelevant to the chosen action. Do not add prose "
            "outside the JSON object. Keep justification concise."
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
