# POLIS v2 Model Smoke Plan

Before confirmatory v2 collection, run one strict structured-action request against every endpoint in the executable v2.0.1 panel.

Cheap backbone:

- `google/gemini-2.5-flash-lite`
- `mistralai/mistral-small-2603`
- `openai/gpt-4.1-mini`
- `deepseek/deepseek-v4-flash`

Frontier diagnostic panel:

- `qwen/qwen3.7-plus`
- `anthropic/claude-sonnet-4.5`
- `openai/gpt-5-mini`

The smoke calls are technical compatibility checks only. They are never included in the research dataset or statistical analysis.

A model passes only if the production OpenRouter adapter returns a non-empty response that validates against the exact POLIS `Action` JSON schema. Any failure stops confirmatory launch. A replacement made before collection requires a protocol version increment, documentation, a new study fingerprint, and a complete repeat of this seven-model gate.
