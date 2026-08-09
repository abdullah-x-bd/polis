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
OPENROUTER_API_KEY=your_rotated_key_here
```

The repository ignores `.env`, live cache files, live result files, cost ledgers, and generated analysis directories by default.

For GitHub Actions, configure `OPENROUTER_API_KEY` as an Actions repository secret. The manual live workflow additionally requires the explicit `RUN_ROTATED_KEY` confirmation string before any inference is attempted.

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

```bash
python scripts/run_v1_live.py --mode full --max-cost-usd 4.00
```

A model override is allowed only for model slugs already frozen in `configs/v1_live.json`. Changing the model panel requires editing the protocol, which necessarily changes its fingerprint.

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

If results were intentionally split across multiple files under the same protocol, provide each JSONL file as a positional argument.

The analysis script refuses to combine results whose protocol fingerprints do not match the supplied protocol.

## Generated analysis artifacts

The analysis directory contains:

- `analysis.json`
- `summary_table.csv`
- `contrast_table.csv`
- episode-level CSV tables
- two primary figures in PNG and PDF
- generated `RESULTS_SUMMARY.md`

All statistical results are regenerated from source JSONL rather than manually maintained.

## GitHub Actions live workflow

The manual workflow `.github/workflows/v1-live.yml` provides the same pilot and full modes. It uploads the source JSONL, manifest, ledger, and generated analysis as a 90-day GitHub Actions artifact.

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

## Re-analysis without API access

Once source JSONL records exist, statistical analysis and figure generation require no API access. Re-analysis therefore does not consume model credits and does not depend on model availability changing later.
