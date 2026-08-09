# POLIS v2 Reproducibility

## Scientific firewall

POLIS v1 is frozen at `archive/polis-v1-frozen`. V2 lives in separate code and uses new scenario identifiers, new protocol fingerprinting, and separate result directories.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Zero-cost validation

```bash
ruff check src/polis/v2 tests/test_v2.py scripts/run_v2.py scripts/analyse_v2.py scripts/stress_v2.py
python -m compileall -q src/polis/v2 scripts/run_v2.py scripts/analyse_v2.py scripts/stress_v2.py
pytest tests/test_v2.py
python scripts/stress_v2.py --output results/v2/calibration/scripted_stress.json
```

## Inspect the complete design without API calls

```bash
python scripts/run_v2.py --study delegation_main --dry-run
python scripts/run_v2.py --study wording_robustness --dry-run
python scripts/run_v2.py --study heterogeneous --dry-run
python scripts/run_v2.py --study commons_salience --dry-run
python scripts/run_v2.py --study frontier --dry-run
```

The dry-run output includes the protocol version, study fingerprint, deterministic design digest, exact episode count, call ceiling, model/composition list, and governance treatments.

## Protocol freeze

Paid v2 execution is blocked while `configs/v2_protocol.json` has `status: draft`.

After zero-cost validation:

1. change status to `frozen`
2. insert the freeze date
3. commit that exact protocol
4. record the generated study fingerprint and design digest in `docs/V2_FREEZE_RECORD.md`
5. run CI again against the frozen commit
6. make no substantive design change under the same protocol version

## Live execution

Set `OPENROUTER_API_KEY` locally or configure it as a GitHub Actions repository secret.

Example shard:

```bash
python scripts/run_v2.py \
  --study delegation_main \
  --shard-index 0 \
  --shard-count 16 \
  --max-cost-usd 0.50
```

The runner writes one JSONL record immediately after each episode and resumes completed experimental keys when restarted with the same shard definition.

## Source records

Every record stores:

- protocol version
- study fingerprint
- study name
- scenario ID
- governance condition
- homogeneous model or heterogeneous composition name
- complete deterministic environment result
- every model response used in the episode
- raw structured output
- generation ID
- routed provider metadata when returned
- input/output/reasoning/cache token accounting when returned
- provider-reported API cost
- completion timestamp

The accompanying manifest stores Git commit SHA in GitHub Actions, Python/platform information, shard definition, expected/completed episode counts and maximum-call ceiling.

## Analyze

```bash
python scripts/analyse_v2.py results/v2/live/*.jsonl --output results/v2/analysis
```

The analysis refuses mixed study fingerprints and duplicate experimental keys.

Generated artifacts include:

- `analysis.json`
- one episode CSV per study
- CSV result tables
- delegation pressure-violation curves
- delegation pressure-completion curves
- institutional safety-performance figure
- quota-salience figure
- heterogeneous-composition heatmap
- generated `RESULTS_SUMMARY.md`

## Exact-coverage rule

A final v2 result is complete only when every episode in all studies selected by the frozen protocol is present exactly once. The final GitHub workflow performs this coverage check before generating the combined analysis artifact.

## Provider prices

Provider prices are intentionally not part of the scientific fingerprint. Actual provider-reported cost is stored for each request because model pricing can change independently of the frozen scientific design. Model slugs themselves are part of the frozen protocol.
