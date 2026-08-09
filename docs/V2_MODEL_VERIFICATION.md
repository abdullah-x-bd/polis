# POLIS v2 Model Endpoint Verification

POLIS v2 uses a strict structured-action interface. A model is eligible for confirmatory collection only if a live OpenRouter compatibility request succeeds under the same provider adapter and strict JSON-schema response format used by the experiment runner.

## First compatibility gate

The original seven-model panel was tested after the zero-cost v2 design had passed CI.

Passed:

- `google/gemini-2.5-flash-lite`
- `mistralai/mistral-small-2603`
- `openai/gpt-4.1-mini`
- `deepseek/deepseek-v4-flash`

Technically incompatible at the time of the gate:

- `qwen/qwen3.7-max` returned an empty completion body under the strict action request.
- `anthropic/claude-sonnet-5` had no OpenRouter endpoint able to satisfy the required structured-output parameters.
- `openai/gpt-5.5` failed the strict compatibility smoke.

No confirmatory v2 research episodes were collected before these failures were observed. The failures are therefore infrastructure/model-interface compatibility information, not behavioral outcomes.

## Replacement rule

A pre-collection endpoint substitution is allowed only when the frozen endpoint cannot satisfy the required machine interface. A substitution must:

1. occur before any confirmatory v2 episode is collected,
2. preserve the intended provider/model-family role where practicable,
3. be documented explicitly,
4. trigger a protocol version increment and a new study fingerprint,
5. pass the same seven-model smoke before paid collection begins.

## v2.0.1 replacement panel

The three failed frontier endpoints were replaced by currently available endpoints whose OpenRouter model metadata exposes the output-format capability required by POLIS:

- Qwen role: `qwen/qwen3.7-plus`
- Anthropic role: `anthropic/claude-sonnet-4.5`
- OpenAI frontier role: `openai/gpt-5-mini`

The four cheap backbone models are unchanged.

The resulting seven-model panel must pass a fresh live compatibility smoke before the v2.0.1 fingerprint is treated as the executable confirmatory protocol.
