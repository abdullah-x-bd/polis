# POLIS v2 Paper Outline

Working paper claim:

**Algorithmic institutions create model-dependent safety-performance frontiers in multi-agent AI systems. Their effectiveness changes with optimization pressure, information, agent composition, and the behavioral salience of the institution itself.**

## 1 Introduction

Motivate increasingly autonomous multi-agent systems as institutional environments rather than isolated model-alignment problems. Introduce the distinction between agent policy and externally executable rules of interaction.

## 2 POLIS

Define an algorithmic institution as a machine-executable mechanism that changes permissions, information, incentives, or collective decision procedures outside the governed agent policy.

Define the institutional safety-performance frontier.

## 3 V1 motivating study

Briefly report the frozen v1 observations as motivation rather than mixing them into the new confirmatory sample:

- executable delegation guards produced zero realized violations across three model families
- prompt governance was highly model-dependent
- terminal enforcement imposed completion costs
- local/provenance behavioral separation was not observed in live agents despite scripted vulnerability
- Commons was largely null for live agents
- visible quota unexpectedly induced cap seeking in some model families

These observations motivate v2 hypotheses.

## 4 Recoverable Delegation Stress Test

96 fresh scenarios. Six governance regimes. Four model families. Four pressure levels. Report violation-pressure and completion-pressure curves plus safe recovery.

## 5 Information versus Enforcement

Compare constitutional prompt, provenance-informed prompt, local executable enforcement and provenance executable enforcement.

## 6 Transformation and Provenance

Focus on laundering scenarios and authorized sanitization. Distinguish metadata-local and lineage-aware institutions.

## 7 Heterogeneous Agent Societies

Test planner/specialist composition and whether institutions reduce composition-sensitive failure variance.

## 8 Institutions as Behavioral Signals

Present hidden-cap versus visible-cap quota-salience experiment and self-interested versus social-welfare objectives.

## 9 Surface Robustness and Frontier Models

Report wording-equivalent perturbations and the separate Qwen/Claude/GPT frontier diagnostic.

## 10 Discussion

Institutional design can provide model-agnostic safety but is not costless. Softer governance can be superior for some agents. Institutions themselves may alter behavior. Governance should therefore be evaluated as a mechanism-design problem rather than as a binary rule-presence variable.

## 11 Limitations

Synthetic environments, model/provider dependence, finite transformations, no guarantee against arbitrary strategic adversaries, narrow institutional classes, and changing commercial model endpoints.

## Candidate headline figures

1. Realized violation versus goal-policy conflict pressure, six governance curves.
2. Compliant completion versus pressure.
3. Safety-performance frontier by institution.
4. Safe recovery after a blocked action by model.
5. Local versus provenance laundering outcomes.
6. Heterogeneous-team violation heatmap.
7. Hidden versus visible quota cap-seeking rates.
8. Wording-robustness consistency.
9. Frontier-model diagnostic.
