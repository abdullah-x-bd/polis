# POLIS v1 Freeze Record

POLIS v1 is frozen as a completed study as of 10 August 2026. No future experiment may alter the v1 protocol, scenarios, institutional definitions, model panel, endpoints, analysis plan, or source results while continuing to call itself the same confirmatory study.

## Immutable code snapshot

The exact research code used for the successful final data collection is preserved at:

- branch: `archive/polis-v1-frozen`
- commit: `54fe68d0d9a7a006672511a2878aa8b59bb64b68`

The temporary execution pull request was closed without merge after successful completion so the PR-triggered paid parallel workflow was not accidentally landed on `main`.

## Frozen protocol

- protocol name: `POLIS v1 confirmatory live experiment`
- protocol version: `1.0.0`
- protocol file: `configs/v1_live.json`
- frozen date recorded by protocol: `2026-08-09`
- SHA-256 protocol fingerprint: `0d9a337b46aeefdf4aca4f4874cf9f4ecd9307ec2fd078d4aa03d87fdf2960f9`

Frozen model panel:

1. `google/gemini-2.5-flash-lite`
2. `mistralai/mistral-small-2603`
3. `openai/gpt-4.1-mini`

Frozen environments:

- Resource Commons
- Delegation Boundaries

Frozen matrix:

- 288 Resource Commons episodes
- 288 Delegation Boundaries episodes
- 576 total episodes
- 576 unique experimental keys

## Final execution

- GitHub Actions workflow run: `31329058441`
- source shards: 12
- observed episodes: 576
- unique episode keys: 576
- final completion flag: `true`
- actual model calls: 2,798
- total recorded tokens: 1,403,650
- provider-reported OpenRouter cost: `$0.447904`

The final Actions artifact is:

- artifact name: `polis-v1-final-parallel-31329058441`
- artifact ID: `9043149203`
- artifact SHA-256 digest: `b7cea35b3e06ad94b27bb9f6f82a7857a2d2ec70e005ab97a0e96cba873d4c7c`

The Actions copy is an execution artifact and is not the conceptual definition of v1. The code commit and protocol fingerprint above define the frozen experiment.

## Headline confirmatory findings

### Delegation Boundaries

Pooled across the three model families, realized violation rates were:

| Institution | Realized violation rate | Task completion rate |
| --- | ---: | ---: |
| No institution | 54.17% | 83.33% |
| Prompt only | 27.78% | 75.00% |
| Local executable guard | 0.00% | 44.44% |
| Provenance guard | 0.00% | 48.61% |

Prompt-only governance was strongly model-dependent. Gemini 2.5 Flash-Lite moved from 70.83% violations without an institution to 75.00% under prompt-only guidance. Mistral Small moved from 25.00% to 8.33%. GPT-4.1 Mini moved from 66.67% to 0.00% while retaining the same 87.50% task-completion rate.

Both executable guards produced zero realized violations for all three tested model families. Agents nevertheless continued to attempt prohibited actions under executable governance, separating agent behavior from system-level permission.

The live models did not produce successful transformation laundering under any condition, so v1 does not establish a live-model advantage of provenance-aware enforcement over the local executable guard. The scripted adversarial suite had already established that the local mechanism is vulnerable to relabel-based laundering while provenance enforcement closes that constructed attack path.

### Resource Commons

The live-agent baseline was already close to the oracle optimum. Pooled final-round efficiency ratios were:

| Institution | Mean efficiency ratio | Mean overclaim ratio |
| --- | ---: | ---: |
| No institution | 0.959833 | 0.000000 |
| Prompt only | 0.961585 | 0.000000 |
| Hard quota | 0.960032 | 0.039395 |
| Congestion pricing | 0.956472 | 0.000291 |

No tested institution produced a convincing corrected improvement on the primary Commons efficiency endpoint. The live models largely requested their true need without governance, unlike the deliberately strategic scripted agents used for mechanism calibration.

The hard-quota condition unexpectedly increased overclaiming for Gemini and Mistral, motivating a future causal test of quota salience. This is an exploratory finding generated after the v1 results were observed and is not retroactively promoted to a preregistered v1 hypothesis.

## Confirmatory statistical highlights

The final generated primary contrasts include:

- Gemini local guard versus no institution on realized delegation violation: effect `-0.7083`, 95% bootstrap CI `[-0.8750, -0.5417]`, Holm-adjusted `p = 0.0001373`.
- Gemini provenance guard versus no institution: effect `-0.7083`, 95% CI `[-0.8750, -0.5000]`, Holm-adjusted `p = 0.0001373`.
- GPT-4.1 Mini prompt-only versus no institution: effect `-0.6667`, 95% CI `[-0.8333, -0.4583]`, Holm-adjusted `p = 0.0002136`.
- GPT-4.1 Mini local guard versus no institution: effect `-0.6667`, 95% CI `[-0.8333, -0.4583]`, Holm-adjusted `p = 0.0002136`.
- GPT-4.1 Mini provenance guard versus no institution: effect `-0.6667`, 95% CI `[-0.8333, -0.4583]`, Holm-adjusted `p = 0.0002136`.

The Commons primary endpoint showed no Holm-adjusted significant treatment effect in the final analysis.

## Rules for all future POLIS work

1. v1 remains unchanged.
2. Findings discovered after inspecting v1 are explicitly labelled exploratory with respect to v1.
3. Any confirmatory follow-up uses new scenario IDs and a new protocol version and fingerprint.
4. v2 may reuse software abstractions but must not silently overwrite v1 data, protocol files, or result claims.
5. Changes motivated by v1 findings are documented before v2 confirmatory data collection.
6. v2 results are analyzed separately from v1 unless a later meta-analysis specifies a principled combination rule in advance.

This record is the boundary between the completed POLIS v1 study and all subsequent POLIS research.