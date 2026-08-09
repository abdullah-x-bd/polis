# Changelog

All notable POLIS research-platform changes are recorded here.

## 0.2.0 - 2026-08-09

### Research architecture

- Added Resource Commons as a four-agent shared-resource institutional benchmark.
- Expanded Delegation Boundaries into 24 matched scenarios across six domains and four policy conditions.
- Added no-institution, prompt-only, hard-quota, and congestion-pricing Commons treatments.
- Added no-institution, prompt-only, local-guard, and immutable-provenance Delegation treatments.
- Separated attempted, detected, and realized policy violations.
- Separated agent-visible local metadata from hidden immutable root provenance.
- Added authorized sanitization as a legitimate policy-changing transformation.

### Mechanism validation

- Added truthful, greedy, max-requester, adaptive-greedy, random, and price-aware scripted Commons strategies.
- Added zero-cost quota and congestion-pricing sweeps.
- Added direct-delegation, relabel-laundering, and sanitization attack paths.
- Added tests for local-guard laundering vulnerability and provenance-guard resistance.

### Live-model experiments

- Added a frozen three-family OpenRouter model panel.
- Added strict JSON-schema action generation.
- Added provider metadata, generation IDs, token accounting, provider-reported costs, caching, and hard budget guards.
- Added frozen pilot and full experiment modes.
- Added protocol SHA-256 fingerprints and run manifests.
- Added atomic, resumable episode-level JSONL source data.
- Added a 576-episode full confirmatory matrix with a conservative 3,456-call ceiling.

### Statistical analysis

- Added paired treatment contrasts against matched no-institution scenarios.
- Added paired bootstrap confidence intervals.
- Added Wilcoxon signed-rank inference for continuous Commons endpoints.
- Added exact discordant-pair inference for binary Delegation endpoints.
- Added Holm multiple-comparison adjustment.
- Added automatic cost summaries, CSV tables, Markdown summaries, and primary figures in PNG/PDF.

### Reproducibility and operations

- Added a frozen machine-readable protocol and written experiment protocol.
- Added a written statistical analysis plan and reproducibility guide.
- Added a complete Steps 21-30 implementation record.
- Expanded clean GitHub Actions CI to validate the entire zero-cost research pipeline and the full live-matrix dry run.
- Added a manual-only paid live workflow with explicit rotated-key confirmation and artifact upload.
- Added a gated OpenRouter smoke-test workflow.
- Added a Makefile for common validation, calibration, live-run, and analysis commands.
- Updated README, citation metadata, package metadata, and generated-artifact ignore rules.

## 0.1.0 - 2026-07-31

- Initial unsafe-delegation pilot.
- Scripted baseline, prompt-only, and coded-regulator regimes.
- Initial metrics, JSONL audit logs, tests, and research documentation.
