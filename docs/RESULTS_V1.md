# POLIS v1 Results

POLIS v1 is complete and frozen. The formal freeze record is [`V1_FREEZE_RECORD.md`](V1_FREEZE_RECORD.md).

The confirmatory live experiment used protocol fingerprint:

`0d9a337b46aeefdf4aca4f4874cf9f4ecd9307ec2fd078d4aa03d87fdf2960f9`

The final matrix contained 576 episodes and 576 unique experimental keys across three model families. It used 2,798 model calls, 1,403,650 recorded tokens, and $0.447904 of provider-reported OpenRouter inference cost.

## Scripted mechanism validation

The zero-cost calibration and stress suites use explicit deterministic or seeded policies. Their purpose is to establish that the benchmark contains meaningful failure modes and that the institutional mechanisms behave differently before live-model evidence is interpreted.

These are mechanism-validation results, not LLM-behavior results.

### Resource Commons calibration

Across the frozen worlds, a mixed strategic scripted population under no institution produced approximately:

- mean efficiency ratio: 0.8170
- mean overclaim ratio: 1.0762
- mean resource waste: 23.4228

The price-aware calibration showed an interior congestion-pricing trade-off:

| alpha | mean efficiency | mean overclaim |
| ---: | ---: | ---: |
| 0.02 | 0.9595 | 0.3115 |
| 0.05 | 0.9691 | 0.2401 |
| 0.10 | 0.9768 | 0.1251 |
| 0.20 | 0.9799 | 0.0299 |
| 0.40 | 0.9399 | 0.0000 |
| 0.80 | 0.6854 | 0.0000 |

`alpha = 0.20` and quota `30` were frozen before the live confirmatory study.

### Delegation mechanism stress test

The scripted stress suite established the intended threat-model separation.

- A local executable guard stopped direct cross-principal transfer attempts.
- A metadata-changing relabel transformation could bypass the local guard in the scripted attack path.
- The provenance-aware guard stopped the same laundering path because root restrictions persisted through ordinary transformations.
- Authorized sanitization remained a legitimate route for policy change when explicitly permitted.

In the scripted relabel attack sweep, the local guard allowed 18 realized laundering violations across the 24 matched scenarios while the provenance guard allowed 0.

## Live-model confirmatory results

### Delegation Boundaries

Pooled results across all three model families were:

| Institution | Realized violation rate | Task completion | Violation attempted | Violation detected |
| --- | ---: | ---: | ---: | ---: |
| No institution | 54.17% | 83.33% | 54.17% | 0.00% |
| Prompt only | 27.78% | 75.00% | 27.78% | 0.00% |
| Local executable guard | 0.00% | 44.44% | 29.17% | 29.17% |
| Provenance guard | 0.00% | 48.61% | 30.56% | 30.56% |

The central system-level result is that both executable guards reduced realized violations to zero across the tested model families even though agents continued to attempt prohibited actions. POLIS therefore distinguishes an unsafe agent decision from an unsafe realized system transition.

#### Gemini 2.5 Flash-Lite

| Institution | Realized violations | Task completion |
| --- | ---: | ---: |
| No institution | 70.83% | 100.00% |
| Prompt only | 75.00% | 95.83% |
| Local guard | 0.00% | 45.83% |
| Provenance guard | 0.00% | 41.67% |

Prompt-only governance did not improve Gemini's violation rate. Local and provenance enforcement each reduced realized violations by 70.83 percentage points relative to no institution. The final Holm-adjusted p-value for both primary contrasts was approximately 0.0001373.

#### Mistral Small 2603

| Institution | Realized violations | Task completion |
| --- | ---: | ---: |
| No institution | 25.00% | 62.50% |
| Prompt only | 8.33% | 41.67% |
| Local guard | 0.00% | 20.83% |
| Provenance guard | 0.00% | 29.17% |

All treatments moved the realized-violation point estimate downward, but the corrected primary contrasts were not statistically decisive at the v1 sample size.

#### GPT-4.1 Mini

| Institution | Realized violations | Task completion |
| --- | ---: | ---: |
| No institution | 66.67% | 87.50% |
| Prompt only | 0.00% | 87.50% |
| Local guard | 0.00% | 66.67% |
| Provenance guard | 0.00% | 75.00% |

GPT-4.1 Mini exhibited a qualitatively different response. Prompt-only governance eliminated realized violations while preserving the same task-completion rate as the no-institution condition. The prompt-only primary effect was -66.67 percentage points with a 95% paired-bootstrap interval of approximately [-83.33, -45.83] percentage points and a Holm-adjusted p-value of approximately 0.0002136.

This creates an important v1 finding: prompt-level governance was highly model-dependent, while executable enforcement was more behaviorally robust across the tested model families.

#### Safety-performance trade-off

Executable governance was highly effective at preventing realized violations, but v1 also observed lower task completion under both executable guards. This must not be interpreted as a pure intrinsic cost of algorithmic institutions because v1 terminates an episode when a guard blocks an action rather than returning control to the agent for recovery. A recoverable-enforcement design is therefore a pre-specified motivation for v2 rather than a post-hoc reinterpretation of v1.

#### Provenance versus local enforcement

The live models produced zero successful policy-laundering episodes under all live conditions. Consequently, v1 does not establish a live-model advantage of provenance-aware enforcement over the local guard. The scripted adversarial suite establishes the mechanism-level vulnerability of local enforcement, but natural live-model behavior did not sufficiently exercise that attack path in v1.

### Resource Commons

Pooled final-round live results were:

| Institution | Mean efficiency ratio | Mean overclaim ratio | Mean resource waste |
| --- | ---: | ---: | ---: |
| No institution | 0.959833 | 0.000000 | 0.000000 |
| Prompt only | 0.961585 | 0.000000 | 0.000000 |
| Hard quota | 0.960032 | 0.039395 | 2.247846 |
| Congestion pricing | 0.956472 | 0.000291 | 0.000000 |

Unlike the deliberately strategic scripted policies, the live models were already close to the oracle welfare optimum and essentially truthful under the no-institution condition. No treatment produced a convincing Holm-adjusted improvement on the primary efficiency endpoint.

The correct v1 conclusion is therefore a null result for the primary Commons hypothesis: this particular live-agent setup did not generate enough endogenous resource overclaiming for the tested institutions to repair.

#### Exploratory quota-salience observation

The hard-quota condition increased mean overclaiming for Gemini and Mistral even though their no-institution overclaiming was zero. This suggests a possible behavioral focal-point effect in which a visible maximum can become an apparent target or entitlement. Because this interpretation was generated after inspecting v1 results, it is exploratory with respect to v1 and requires a fresh causal test under a new protocol.

## Confirmatory primary contrasts

Selected generated primary contrasts from the frozen statistical analysis were:

| Environment | Model | Treatment | Effect | 95% CI | Holm p |
| --- | --- | --- | ---: | --- | ---: |
| Delegation | Gemini 2.5 Flash-Lite | Local guard | -0.7083 | [-0.8750, -0.5417] | 0.0001373 |
| Delegation | Gemini 2.5 Flash-Lite | Provenance guard | -0.7083 | [-0.8750, -0.5000] | 0.0001373 |
| Delegation | GPT-4.1 Mini | Prompt only | -0.6667 | [-0.8333, -0.4583] | 0.0002136 |
| Delegation | GPT-4.1 Mini | Local guard | -0.6667 | [-0.8333, -0.4583] | 0.0002136 |
| Delegation | GPT-4.1 Mini | Provenance guard | -0.6667 | [-0.8333, -0.4583] | 0.0002136 |

Effects are treatment minus no institution on matched scenarios. Negative delegation effects indicate fewer realized violations.

## Interpretation

POLIS v1 does not support the crude claim that "algorithmic institutions are always better than prompts." It supports a more specific picture:

1. executable institutions can robustly prevent realized unsafe system transitions even when agents attempt them;
2. natural-language governance can be extremely effective for some agent models and ineffective for others;
3. institutional effectiveness must be evaluated jointly with useful task performance;
4. mechanism vulnerabilities demonstrated under adversarial scripted policies need not spontaneously appear in natural model behavior;
5. institutions can change agent behavior in unexpected ways, as suggested by quota-induced overclaiming;
6. negative results are informative: Resource Commons v1 did not show an institution-induced welfare improvement because the live agents were already largely truthful.

All future confirmatory extensions are treated as a new POLIS protocol rather than modifications to v1.