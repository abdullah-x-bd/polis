# POLIS v2 Model Endpoint Verification

POLIS requires every live model endpoint to satisfy the same strict structured-action interface used by the experiment runner. Endpoint compatibility checks are technical gates, not behavioral research outcomes.

## Historical compatibility repairs

Earlier v2 protocol versions encountered endpoint-specific incompatibilities, including empty structured output under bounded reasoning and unavailable or unsupported frontier interfaces. These failures occurred during technical execution work and triggered documented protocol-version changes rather than silent substitutions. Historical version-specific model-panel files are retained for auditability.

## Final frozen v2.0.8 panel

Backbone:

- `google/gemini-2.5-flash-lite`
- `mistralai/mistral-small-2603`
- `openai/gpt-4.1-mini`
- `deepseek/deepseek-v3.2`, reasoning disabled

Frontier diagnostic:

- `qwen/qwen3-235b-a22b-2507`
- `anthropic/claude-sonnet-4.5`
- `openai/gpt-4.1`

The final frozen preflight independently checked model-panel alignment, exact protocol/config/design hashes, provider adapter tests, and the complete 5,280-episode dry-run before the canonical execution.

## Final execution validation

Workflow run `31359824031` produced exactly 5,280 unique v2.0.8 episodes with no unexpected model IDs. The post-run audit also found zero routed-model identity mismatches among 10,720 model-call records.

The final paid collection and historical paid smoke workflows are sealed after completion.
