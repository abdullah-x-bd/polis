# POLIS v2.0.1 endpoint substitutions

The first seven-model compatibility smoke was run after the zero-cost v2 design passed CI and before any confirmatory v2 research episode was collected.

Four endpoints passed immediately:

- `google/gemini-2.5-flash-lite`
- `mistralai/mistral-small-2603`
- `openai/gpt-4.1-mini`
- `deepseek/deepseek-v4-flash`

Three selected frontier endpoints were technically incompatible with the strict POLIS structured-action request at the time of execution:

- `qwen/qwen3.7-max`
- `anthropic/claude-sonnet-5`
- `openai/gpt-5.5`

They were replaced before confirmatory data collection by:

- `qwen/qwen3.7-plus`
- `anthropic/claude-sonnet-4.5`
- `openai/gpt-5-mini`

The substitution preserves the intended Qwen, Anthropic and newer OpenAI diagnostic roles while selecting OpenRouter endpoints whose current model metadata advertises the output-format capability needed by the POLIS adapter.

Because model identity is part of the canonical protocol, the protocol version was incremented from 2.0.0 to 2.0.1 and the study fingerprint necessarily changes. The entire seven-model technical smoke is repeated before any v2.0.1 confirmatory collection is launched.
