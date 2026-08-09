# POLIS Steps 21 through 30 Completion Record

This file records the final research-engineering phase of POLIS v0.2.0.

## Step 21: Freeze the live model panel

Complete.

The confirmatory panel is fixed in `configs/v1_live.json`:

- `google/gemini-2.5-flash-lite`
- `mistralai/mistral-small-2603`
- `openai/gpt-4.1-mini`

The selection gives three provider/model families at sufficiently low cost for the full matched design.

## Step 22: Build the pilot protocol

Complete.

`pilot` mode is a frozen subset containing three Commons worlds and four Delegation scenarios representing all four delegation scenario types. Across all three models it contains 84 episodes and at most 480 model calls.

The pilot uses the same schemas, institutions, endpoints, cache, budget ledger, and action interface as the full run.

## Step 23: Convert model calls into auditable environment agents

Complete.

`src/polis/v1/model_agents.py` adapts a provider to the environment-level `Agent` interface while retaining every `ModelResponse`. The live runner therefore records model text and usage without allowing the model to determine the evaluation label.

`src/polis/v1/providers/openrouter.py` enforces a strict action JSON schema, requires compatible provider routing, records generation and provider metadata, uses the deterministic request cache, and writes actual reported cost to the budget ledger.

## Step 24: Build the full confirmatory matrix runner

Complete.

`src/polis/v1/live.py` and `scripts/run_v1_live.py` implement:

- pilot and full modes
- all frozen models
- both environments
- all matched institutions
- protocol fingerprinting
- per-episode source records
- atomic append after every episode
- run manifests
- resume from completed keys
- rejection of mixed protocol fingerprints
- model override restricted to the frozen panel
- maximum-call planning without API use

The full matrix contains 576 episodes and at most 3,456 model calls.

## Step 25: Freeze the protocol and hypotheses

Complete.

`configs/v1_live.json` is the machine-readable source of truth. `src/polis/v1/protocol.py` validates and fingerprints it. `docs/EXPERIMENT_PROTOCOL_V1.md` records the research question, treatments, endpoints, expectations, model panel, pilot, full matrix, inference settings, and interpretation boundary.

Any substantive protocol change produces a new fingerprint.

## Step 26: Pre-specify statistical analysis

Complete.

`src/polis/v1/analysis.py` implements the statistical plan in code.

Resource Commons:

- paired treatment-minus-baseline effects
- 10,000-sample paired bootstrap confidence intervals
- paired Wilcoxon signed-rank tests

Delegation Boundaries:

- paired risk differences
- 10,000-sample paired bootstrap confidence intervals
- exact discordant-pair binomial tests

Holm correction is applied within environment and endpoint. Cost and completeness are also reported.

The written plan is `docs/STATISTICAL_ANALYSIS_V1.md`.

## Step 27: Complete adversarial and robustness validation

Complete.

The zero-cost suite already covers:

- truthful resource claiming
- greedy claiming
- max requesting
- adaptive greedy behavior
- price-aware best response
- quota calibration
- congestion-price calibration
- direct prohibited delegation
- metadata relabel laundering
- unauthorized sanitization
- authorized sanitization
- local policy enforcement
- immutable provenance enforcement
- no-leakage tests for root provenance

The mechanism-validation results are summarized in `docs/RESULTS_V1.md` without presenting them as LLM findings.

## Step 28: Automate tables, figures, and result export

Complete.

`scripts/analyse_v1.py` generates:

- `analysis.json`
- `summary_table.csv`
- `contrast_table.csv`
- Commons episode CSV
- Delegation episode CSV
- generated results summary Markdown
- Commons primary PNG/PDF figure
- Delegation primary PNG/PDF figure

These outputs are generated directly from source JSONL records.

## Step 29: Complete reproducibility, CI, and paid-run orchestration

Complete.

`docs/REPRODUCIBILITY_V1.md` provides end-to-end commands.

`.github/workflows/v1-ci.yml` runs:

- lint
- compile check
- complete tests
- zero-cost Commons calibration
- zero-cost delegation stress suite
- full live-matrix dry run without API calls

`.github/workflows/v1-live.yml` is manual-only. It provides pilot/full selection, optional frozen-model selection, an explicit rotated-key confirmation gate, hard dollar caps, automatic analysis after a successful run, and research-artifact upload.

## Step 30: Final repository release and validation

Complete in the v0.2.0 codebase.

The release phase includes:

- stable `0.2.0` package version
- updated project metadata
- expanded tests for the live pipeline
- final README and citation metadata
- changelog
- zero-cost reproducibility path
- gated live reproducibility path
- final clean GitHub Actions validation

A live-model data collection run is deliberately separate from repository completeness because it consumes an external secret and credits. The repository contains the frozen, executable protocol needed to produce those records without further research-design changes.
