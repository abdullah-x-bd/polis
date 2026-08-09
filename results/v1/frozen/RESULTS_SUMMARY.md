# POLIS v1 generated results summary

Protocol fingerprint `0d9a337b46aeefdf4aca4f4874cf9f4ecd9307ec2fd078d4aa03d87fdf2960f9`

Total model calls: 2798
Total tokens: 1403650
Recorded OpenRouter cost: $0.447904

## Primary contrasts

| Environment | Model | Treatment | Endpoint | Effect | 95% CI | Holm p |
| --- | --- | --- | --- | ---: | --- | ---: |
| resource_commons | google/gemini-2.5-flash-lite | congestion_pricing | efficiency_ratio | 0.0000 | [0.0000, 0.0000] | 1 |
| resource_commons | google/gemini-2.5-flash-lite | hard_quota | efficiency_ratio | -0.0001 | [-0.0043, 0.0043] | 1 |
| resource_commons | google/gemini-2.5-flash-lite | prompt_only | efficiency_ratio | 0.0000 | [0.0000, 0.0000] | 1 |
| resource_commons | mistralai/mistral-small-2603 | congestion_pricing | efficiency_ratio | -0.0004 | [-0.0019, 0.0007] | 1 |
| resource_commons | mistralai/mistral-small-2603 | hard_quota | efficiency_ratio | -0.0026 | [-0.0097, 0.0037] | 1 |
| resource_commons | mistralai/mistral-small-2603 | prompt_only | efficiency_ratio | 0.0053 | [0.0000, 0.0140] | 1 |
| resource_commons | openai/gpt-4.1-mini | congestion_pricing | efficiency_ratio | -0.0097 | [-0.0252, 0.0025] | 1 |
| resource_commons | openai/gpt-4.1-mini | hard_quota | efficiency_ratio | 0.0033 | [0.0005, 0.0065] | 0.1964 |
| resource_commons | openai/gpt-4.1-mini | prompt_only | efficiency_ratio | 0.0000 | [0.0000, 0.0000] | 1 |
| delegation_boundaries | google/gemini-2.5-flash-lite | local_guard | realized_violation | -0.7083 | [-0.8750, -0.5417] | 0.0001373 |
| delegation_boundaries | google/gemini-2.5-flash-lite | prompt_only | realized_violation | 0.0417 | [0.0000, 0.1250] | 1 |
| delegation_boundaries | google/gemini-2.5-flash-lite | provenance_guard | realized_violation | -0.7083 | [-0.8750, -0.5000] | 0.0001373 |
| delegation_boundaries | mistralai/mistral-small-2603 | local_guard | realized_violation | -0.2500 | [-0.4167, -0.0833] | 0.125 |
| delegation_boundaries | mistralai/mistral-small-2603 | prompt_only | realized_violation | -0.1667 | [-0.3750, 0.0000] | 0.4375 |
| delegation_boundaries | mistralai/mistral-small-2603 | provenance_guard | realized_violation | -0.2500 | [-0.4167, -0.0833] | 0.125 |
| delegation_boundaries | openai/gpt-4.1-mini | local_guard | realized_violation | -0.6667 | [-0.8333, -0.4583] | 0.0002136 |
| delegation_boundaries | openai/gpt-4.1-mini | prompt_only | realized_violation | -0.6667 | [-0.8333, -0.4583] | 0.0002136 |
| delegation_boundaries | openai/gpt-4.1-mini | provenance_guard | realized_violation | -0.6667 | [-0.8333, -0.4583] | 0.0002136 |

Effects are treatment minus the no-institution condition on matched scenarios.
This file is copied verbatim from the generated final analysis artifact.