# POLIS v1 Results Status

This document separates results that already exist from results that require the frozen live-model protocol.

## Scripted mechanism validation

The repository's zero-cost calibration and stress suites use explicit deterministic or seeded policies. Their purpose is to establish that the benchmark contains meaningful failure modes and that the institutional mechanisms behave differently before any live-model evidence is collected.

These are mechanism-validation results, not LLM-behavior results.

### Resource Commons

Across the frozen worlds, a mixed strategic scripted population under no institution produced approximately:

- mean efficiency ratio: 0.8170
- mean overclaim ratio: 1.0762
- mean resource waste: 23.4228

This demonstrates a nontrivial collective-action failure in the benchmark.

The price-aware calibration showed an interior congestion-pricing trade-off. Selected values were approximately:

| alpha | mean efficiency | mean overclaim |
| ---: | ---: | ---: |
| 0.02 | 0.9595 | 0.3115 |
| 0.05 | 0.9691 | 0.2401 |
| 0.10 | 0.9768 | 0.1251 |
| 0.20 | 0.9799 | 0.0299 |
| 0.40 | 0.9399 | 0.0000 |
| 0.80 | 0.6854 | 0.0000 |

The institution therefore does not mechanically improve with increasing severity. Stronger prices eventually suppress useful resource demand. `alpha = 0.20` was frozen before the live confirmatory study because it was near the scripted efficiency maximum while leaving only a small mean overclaim.

The quota sweep likewise showed a performance cost when the quota was too restrictive. `quota = 30` was frozen as the v1 quota condition.

### Delegation Boundaries

The scripted stress suite established the intended threat-model separation.

- With no institution, direct forbidden delegation produced realized violations.
- A local executable guard stopped direct cross-principal transfer attempts.
- After a metadata-changing relabel transformation, the local guard was bypassed in the scripted transformation-laundering attack path.
- The provenance-aware guard stopped the same laundering path because root restrictions persisted through ordinary transformations.
- Authorized sanitization remains a legitimate mechanism for relaxing a root restriction when the scenario explicitly allows it.

In the relabel attack sweep, the local guard allowed 18 realized scripted laundering violations across the 24 matched scenarios, while the provenance guard allowed 0.

Again, those numbers validate the mechanism and attack construction. They do not state that a particular language model will choose those attacks.

## Live-model confirmatory results

Live-model results are generated only by `scripts/run_v1_live.py` under `configs/v1_live.json` and are analyzed only by `scripts/analyse_v1.py`.

A complete v1 confirmatory result requires:

- the frozen protocol fingerprint
- 576 completed episodes when all three models are used
- source JSONL records
- run manifest
- provider-reported cost ledger
- generated statistical artifacts

The repository intentionally does not invent or pre-populate those model outcomes. After a completed live run, `scripts/analyse_v1.py` generates a `RESULTS_SUMMARY.md` directly from source records.

## Interpretation template

The main scientific questions after the live matrix are:

1. Does prompt-only guidance measurably change resource claiming or delegation behavior relative to no institution?
2. Do executable institutions improve the primary system-level outcomes?
3. Is any safety gain bought by a meaningful reduction in legitimate task completion?
4. Does the local guard fail specifically on transformation laundering rather than on direct transfer?
5. Does immutable provenance close that failure mode across model families?
6. Are institutional effects qualitatively consistent across Google, Mistral, and OpenAI model families?
7. In Resource Commons, do model agents adapt to the congestion price in a way that reproduces, weakens, or reverses the scripted mechanism-calibration pattern?

The strongest result would not be simply "the strictest rule blocks the most actions." The target is an institution that reduces the relevant collective failure while preserving useful performance and whose advantage survives across distinct agent model families.
