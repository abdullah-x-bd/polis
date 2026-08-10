# POLIS v2.0.8 Freeze Record

The final confirmatory scientific protocol was frozen before the canonical v2.0.8 execution.

- Protocol version: `2.0.8`
- Status: `frozen`
- Freeze date: `2026-08-10`
- Study fingerprint: `f169dc157fd6f31d0f0ce0a76a0c51049f9b0a28eba08fc3201b616e1ce001e3`
- Config digest: `f72f6d683b88d1f11b7ec1d840413f805a619a5433ce431c445b16831aa3346b`
- Design digest: `c5d6a750c495d14d0d745a9ee317cd40fa20ecd5c2e3e735fd74b195363182e8`
- Seed: `20260810`

## Frozen model panel

Backbone:

- `google/gemini-2.5-flash-lite`
- `mistralai/mistral-small-2603`
- `openai/gpt-4.1-mini`
- `deepseek/deepseek-v3.2` with reasoning disabled

Frontier diagnostic:

- `qwen/qwen3-235b-a22b-2507`
- `anthropic/claude-sonnet-4.5`
- `openai/gpt-4.1`

## Frozen study sizes

- Delegation main: 2,304
- Wording robustness: 1,152
- Heterogeneous teams: 576
- Commons salience: 960
- Frontier diagnostic: 288
- Total: **5,280 episodes**

The canonical execution checked out research SHA `4431fa5ceb5f9700cf9a650dba2d0478ea08c267`. Release and documentation commits occur after outcome collection and therefore are intentionally different from the execution SHA. Any future substantive design change requires a new protocol version and fingerprint.
