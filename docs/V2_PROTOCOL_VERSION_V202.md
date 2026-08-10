# POLIS v2.0.2 protocol amendment

No confirmatory POLIS v2 episode had been collected when this amendment was made.

The second seven-model compatibility gate identified three interface-level problems rather than behavioral research outcomes:

1. Anthropic's structured-output implementation rejected Pydantic validation keywords such as `minimum` in the wire JSON schema.
2. Qwen returned a truncated otherwise-structured JSON action under the 180-token completion ceiling.
3. GPT-5 Mini exposes structured outputs but not a temperature parameter, so `provider.require_parameters=true` rejected every route when POLIS unnecessarily required temperature support.

v2.0.2 makes only measurement-interface changes:

- The outbound action schema now specifies object structure, nullability, and action enum only. The existing Pydantic `Action` model still enforces semantic constraints such as non-negative amounts after generation.
- OpenRouter response healing is enabled for non-streaming structured responses to repair syntax-only formatting defects without changing action semantics.
- The completion ceiling is raised from 180 to 512 tokens to prevent technical JSON truncation. Agents are still instructed to return one concise action only.
- `temperature=0` continues to be sent to endpoints that expose temperature. GPT-5-family endpoints omit the unsupported parameter instead of failing provider routing.

The scientific design is unchanged: scenarios, governance regimes, pressure levels, hypotheses, endpoints, sample sizes, friction values, bootstrap plan, confidence level, and random seed are identical.

Because inference configuration and provider serialization are part of measurement, the protocol version is incremented to 2.0.2 and a new study fingerprint is required before confirmatory collection.
