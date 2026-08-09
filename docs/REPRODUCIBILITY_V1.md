# Reproducing POLIS v1

POLIS v1 is designed so that the complete zero-cost mechanism validation can be reproduced without an API key and the live-model study can be reproduced with an OpenRouter key under a hard software budget.

## Environment

Recommended:

- Python 3.11
- a clean virtual environment
- the repository commit associated with the run manifest

Install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

On Windows PowerShell, activate with:

```powershell
.venv\Scripts\Activate.ps1
```

## Verify the repository

```bash
ruff check src/polis/v1 tests scripts
python -m compileall -q src/polis/v1 scripts
pytest
```

The GitHub Actions workflow `.github/workflows/v1-ci.yml` runs the same checks from a clean Ubuntu runner.

## Reproduce the zero-cost mechanism validation

Resource Commons calibration:

```bash
python scripts/calibrate_commons_v1.py --output results/calibration/commons_v1.json
```

Delegation Boundaries stress suite:

```bash
python scripts/stress_delegation_v1.py --output results/calibration/delegation_v1.json
```

These experiments use scripted policies. They test the environments, institutional mechanisms, metrics, and known attack paths without making claims about live language-model behavior.

## Inspect the frozen live matrix without spending money

```bash
python scripts/run_v1_live.py --mode pilot --dry-run
python scripts/run_v1_live.py --mode full --dry-run
```

The full protocol should report:

- 3 models
- 288 Resource Commons episodes
- 288 Delegation Boundaries episodes
- 576 total episodes
- at most 3,456 model calls

The protocol fingerprint printed by the command is the identifier that must appear in every record used in one confirmatory analysis.

## Configure OpenRouter

Create a local `.env` file that is never committed:

```text
OPENROUTER_API_KEY=your_key_here
```

The repository ignores `.env`, live cache files, live result files, cost ledgers, and generated analysis directories by default.

For GitHub Actions, configure `OPENROUTER_API_KEY` as an Actions repository secret. The manual live workflow additionally requires the explicit `RUN_ROTATED_KEY` confirmation string before inference is attempted.

## One-request API smoke test

```bash
python scripts/test_openrouter.py --model google/gemini-2.5-flash-lite --max-cost-usd 0.25
```

This checks connectivity and the structured-action schema without starting the benchmark.

## Pilot

All frozen models:

```bash
python scripts/run_v1_live.py --mode pilot --max-cost-usd 0.75
```

One frozen model:

```bash
python scripts/run_v1_live.py \
  --mode pilot \
  --model google/gemini-2.5-flash-lite \
  --max-cost-usd 0.30
```

The runner appends each completed episode immediately. Re-running the same command resumes from completed keys rather than purchasing completed episodes again.

## Full confirmatory run

Sequential execution:

```bash
python scripts/run_v1_live.py --mode full --max-cost-usd 4.00
```

A model override is allowed only for model slugs already frozen in `configs/v1_live.json`. Changing the model panel requires editing the protocol, which necessarily changes its fingerprint.

## Deterministic sharding

Long live runs can be partitioned by scenario without changing the protocol or its fingerprint. `--shard-count N` assigns scenario-list indices deterministically by `index mod N`, and `--shard-index` selects one disjoint partition.

For example, four disjoint shards of one model are:

```bash
python scripts/run_v1_live.py --mode full \
  --model google/gemini-2.5-flash-lite \
  --shard-count 4 --shard-index 0 --max-cost-usd 0.25

python scripts/run_v1_live.py --mode full \
  --model google/gemini-2.5-flash-lite \
  --shard-count 4 --shard-index 1 --max-cost-usd 0.25

python scripts/run_v1_live.py --mode full \
  --model google/gemini-2.5-flash-lite \
  --shard-count 4 --shard-index 2 --max-cost-usd 0.25

python scripts/run_v1_live.py --mode full \
  --model google/gemini-2.5-flash-lite \
  --shard-count 4 --shard-index 3 --max-cost-usd 0.25
```

For the frozen 24-scenario environments, four shards contain six Resource Commons worlds and six Delegation Boundaries scenarios each. Across all four shards the episode keys are exactly the same as one unsharded run. Sharding changes scheduling only.

## Semantic invalid actions

JSON-schema structured output guarantees shape and types, not that a live model will always choose a semantically admissible value. POLIS therefore treats semantic mistakes as agent behavior rather than infrastructure failures.

- In Resource Commons, an action other than `request_resource` or a request without an amount becomes a zero-unit request for that agent and is counted as an invalid action.
- In Delegation Boundaries, a `delegate` action with a missing or unknown agent identifier is recorded as an `environment_validation` failure, leaves the artifact unchanged, does not complete the task, and ends that episode.
- Irrelevant optional fields on otherwise valid actions do not invalidate the action.

Invalid-action counts are diagnostic outputs. They are not post hoc replacements for any pre-specified primary or secondary endpoint.

## Live-result files

`results/live/` contains:

- `<run-id>.jsonl`: one source-data record per completed episode
- `<run-id>.manifest.json`: run metadata and completeness
- `openrouter_ledger.jsonl`: actual provider-reported cost ledger
- `cache/`: request-hash response cache

The cache is part of run resilience but the JSONL episode data and manifest are the scientific source artifacts.

## Analyse a run

```bash
python scripts/analyse_v1.py \
  results/live/polis-v1-full-<fingerprint-prefix>.jsonl \
  --output results/analysis
```

For a sharded run, supply every disjoint JSONL source file in one invocation. The analysis script rejects duplicate completion keys and refuses to combine results whose protocol fingerprints do not match the supplied protocol.

## Generated analysis artifacts

The analysis directory contains:

- `analysis.json`
- `summary_table.csv`
- `contrast_table.csv`
- episode-level CSV tables
- two primary figures in PNG and PDF
- generated `RESULTS_SUMMARY.md`

`analysis.json` also reports invalid-action diagnostics by model and institution. All statistical results are regenerated from source JSONL rather than manually maintained.

## GitHub Actions live workflow

The manual workflow `.github/workflows/v1-live.yml` provides pilot and full modes. It uploads the source JSONL, manifest, ledger, and generated analysis as a GitHub Actions artifact.

The workflow is deliberately not triggered by pushes or pull requests because live inference costs money and uses a secret.

## Provenance checklist for a result

A result is fully attributable when the following are retained together:

1. Git commit SHA
2. frozen protocol file
3. protocol fingerprint
4. source JSONL
5. run manifest
6. OpenRouter cost ledger
7. generated analysis directory
8. model slugs and routed provider metadata embedded in the model-call records
9. shard index/count when execution was partitioned

## Re-analysis without API access

Once source JSONL records exist, statistical analysis and figure generation require no API access. Re-analysis therefore does not consume model credits and does not depend on model availability changing later.
