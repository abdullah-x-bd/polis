# POLIS v2.0.8 Reproducibility

## Scientific firewall

POLIS v1 is frozen separately. V2 uses fresh scenario identifiers, a new machine-readable protocol, new fingerprints, and separate result artifacts. V1 and v2 episode outcomes are not pooled.

## Final identifiers

- protocol version `2.0.8`
- fingerprint `f169dc157fd6f31d0f0ce0a76a0c51049f9b0a28eba08fc3201b616e1ce001e3`
- config digest `f72f6d683b88d1f11b7ec1d840413f805a619a5433ce431c445b16831aa3346b`
- design digest `c5d6a750c495d14d0d745a9ee317cd40fa20ecd5c2e3e735fd74b195363182e8`
- canonical execution SHA `4431fa5ceb5f9700cf9a650dba2d0478ea08c267`
- canonical workflow run `31359824031`

The execution SHA is intentionally different from later documentation/release SHAs. Scientific outcomes were collected against the frozen execution commit.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Zero-cost validation

```bash
ruff check src/polis/v2 tests scripts/run_v2.py scripts/analyse_v2.py scripts/stress_v2.py
python -m compileall -q src/polis/v2 scripts/run_v2.py scripts/analyse_v2.py scripts/stress_v2.py
pytest
python scripts/stress_v2.py --output results/v2/calibration/scripted_stress.json
```

## Inspect the frozen study matrix without API calls

```bash
python scripts/run_v2.py --study delegation_main --dry-run
python scripts/run_v2.py --study wording_robustness --dry-run
python scripts/run_v2.py --study heterogeneous --dry-run
python scripts/run_v2.py --study commons_salience --dry-run
python scripts/run_v2.py --study frontier --dry-run
```

Expected sizes are 2,304, 1,152, 576, 960, and 288 respectively. Total expected episodes are 5,280.

## Reproduce the final statistical analysis

Download and extract the exact `v0.3.0` source-bundle release asset. Its expected ZIP SHA-256 is:

`9f0eb0db21e32a0e72f266069634899af5814589608426504acbce9414c3064c`

The extracted bundle contains 40 final study JSONL files under `source/`, plus manifests and ledgers. Re-run:

```bash
mapfile -t SOURCES < <(find source -type f -name 'polis-v208-final-*.jsonl' | sort)
python scripts/analyse_v2.py "${SOURCES[@]}" --protocol configs/v2_protocol.json --output reproduced-analysis
```

On PowerShell, collect the files and pass them explicitly to `scripts/analyse_v2.py`. No provider key or new model call is required for reanalysis.

The analyzer rejects mixed study fingerprints and duplicate experimental keys.

## Canonical completeness checks

The final collection audit passed before analysis:

- 5,280 expected episodes
- 5,280 observed episodes
- 5,280 unique experimental keys
- 0 duplicate keys
- exact per-study counts
- protocol version 2.0.8 throughout
- one frozen fingerprint throughout
- no unexpected model IDs

## Exact-response cache provenance

The final execution used an audited cache to avoid paying twice for byte-for-byte equivalent provider requests. The cache audit made zero provider calls. It admitted 3,596 v2.0.8-compatible exact response objects, excluded 43 objects associated with the obsolete `deepseek-v4-flash` interface, and rejected one response that did not satisfy final semantic validation.

Cache admission was based on request identity and interface/semantic validity, not on favorable or unfavorable scientific outcomes. The final 5,280 episode records were reconstructed under v2.0.8.

## Source records

Every episode stores protocol version, fingerprint, study, scenario, governance, model composition, deterministic environment result, model responses, generation/provider metadata, token usage, provider-reported cost, and completion timestamp. Manifests preserve execution SHA, Python/platform information, shard definition, and expected/completed episode counts.

## Provider normalization

The final parser uses a portable structured-action schema across providers. Free-text `justification` metadata has an existing 500-character local representation limit. If a provider returns a longer justification, it is deterministically truncated before local Pydantic validation while the full raw provider text remains retained. This field does not determine institutional permissions, environment transitions, safety labels, task completion, or welfare.

The final source contains 97 such truncations, 9 filled missing nullable fields, 6 dropped extra fields, zero routed-model mismatches, and 48 semantic invalid actions handled by the deterministic environment.

## Published artifacts

`results/published/v2.0.8/` contains compact permanent evidence suitable for repository browsing. The GitHub release asset carries the complete raw source records, episode-level tables, generated figures, manifests, and ledgers.

See `V2_FINAL_EXECUTION_RECORD.md` and `V2_EXECUTION_INCIDENT_2026-08-10.md` for the audit trail.
