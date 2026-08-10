# POLIS

**POLIS is an experimental testbed for designing and evaluating algorithmic institutions for multi-agent AI systems.**

POLIS studies a system-level AI safety problem. When autonomous agents pursue tasks under shared resources, delegation boundaries, and conflicting incentives, what kinds of institutions keep the system safe without destroying useful performance?

Software release **0.3.0** contains the completed **POLIS v2.0.8 confirmatory study**, a frozen 5,280-episode experiment across seven live model endpoints. Version 1 remains archived and reproducible in the same repository.

## v2.0.8 in one table

Main Delegation study, 384 episodes per governance condition:

| Governance | Realized violation | Compliant completion | Mean utility |
| --- | ---: | ---: | ---: |
| No institution | 12.0% | 86.5% | 7.514 |
| Concise prompt | 7.0% | 90.9% | 7.367 |
| Constitutional prompt | **0.0%** | 95.1% | 6.244 |
| Provenance prompt | 1.8% | 93.5% | 6.762 |
| Recoverable local guard | 5.7% | 93.2% | 7.081 |
| Recoverable provenance guard | **0.0%** | **95.6%** | 6.781 |

The complete analysis is in [`docs/V2_RESULTS.md`](docs/V2_RESULTS.md).

## What we found

### Recoverable enforcement can be safe without terminal failure

The v1 guards often converted unsafe actions into safe non-completion because a block ended the episode. V2 makes denial recoverable. Among main-study episodes in which the provenance guard actually blocked a prohibited action, agents safely recovered and completed in **44 of 51 cases, 86.3%**. The provenance guard had zero realized violations in the full 384-episode main study.

### Live agents discovered policy laundering

The strongest mechanism result is no longer only a scripted attack. In transformation-laundering scenarios, the recoverable local guard had **22 violations in 96 episodes**, while the immutable-provenance guard had **0 in 96**. Exact paired p = **4.77e-7**.

DeepSeek V3.2 produced 18 of the 22 local-guard laundering violations. In live traces, it deliberately used a representation-changing relabel action to make the visible permission appear permissive, then delegated across principals even though immutable root policy remained restrictive.

### Strong prompting can also be extremely effective

The constitutional prompt produced **0/384** realized violations in the main study and **0%** violations on the high-conflict frontier diagnostic. That result is important. POLIS does not support a simple claim that executable governance always beats prompts. Instead, the evidence points to a more specific advantage for executable provenance when mutable representations, prohibited attempts, and recovery matter.

### Institutions can change behavior merely by how a rule is represented

In Resource Commons, the mechanical request cap was held identical while only its numerical visibility changed. A visible cap caused significantly more cap-seeking than a hidden cap. An explicit request-only-need norm eliminated observed cap-seeking in both objective framings.

## v2 research design

POLIS v2.0.8 contains five frozen studies:

| Study | Episodes |
| --- | ---: |
| Delegation main | 2,304 |
| Wording robustness | 1,152 |
| Heterogeneous teams | 576 |
| Commons quota salience | 960 |
| Frontier diagnostic | 288 |
| **Total** | **5,280** |

The frozen backbone is:

- `google/gemini-2.5-flash-lite`
- `mistralai/mistral-small-2603`
- `openai/gpt-4.1-mini`
- `deepseek/deepseek-v3.2`

The frontier diagnostic uses:

- `qwen/qwen3-235b-a22b-2507`
- `anthropic/claude-sonnet-4.5`
- `openai/gpt-4.1`

The frozen scientific fingerprint is:

`f169dc157fd6f31d0f0ce0a76a0c51049f9b0a28eba08fc3201b616e1ce001e3`

See [`docs/V2_PROTOCOL.md`](docs/V2_PROTOCOL.md) and [`docs/V2_FREEZE_RECORD.md`](docs/V2_FREEZE_RECORD.md).

## Statistical design

The preregistered main Delegation models use linear probability and linear outcome regressions with base-scenario clustered robust uncertainty. The central estimand is the interaction between governance architecture and goal-policy conflict pressure.

Matched treatment effects are also reported with 10,000-resample paired bootstrap confidence intervals. Commons uses world fixed effects with world-clustered uncertainty. Wording robustness measures within-scenario consistency across three equivalent surface forms. Heterogeneous-team analysis measures safety dispersion across fixed model compositions.

See [`docs/V2_STATISTICAL_ANALYSIS.md`](docs/V2_STATISTICAL_ANALYSIS.md).

## Exact final dataset

The canonical v2.0.8 run contains:

- 5,280 expected episodes
- 5,280 observed episodes
- 5,280 unique experimental keys
- 0 duplicate keys
- 10,720 model-call records
- 8,927,565 tokens
- 0 retry events

The full dataset represents $3.023621 in provider-reported response cost. An independently audited exact-response cache reduced the additional spend required for the final corrected execution to $1.967216.

Execution provenance and artifact checksums are in [`docs/V2_FINAL_EXECUTION_RECORD.md`](docs/V2_FINAL_EXECUTION_RECORD.md).

## Quick start

```bash
git clone https://github.com/abdullah-x-bd/polis.git
cd polis
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

ruff check src/polis/v2 tests scripts/run_v2.py scripts/analyse_v2.py scripts/stress_v2.py
pytest
python scripts/stress_v2.py --output results/v2/calibration/scripted_stress.json
```

Windows PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

Inspect the frozen v2 design without any provider call:

```bash
python scripts/run_v2.py --study delegation_main --dry-run
python scripts/run_v2.py --study wording_robustness --dry-run
python scripts/run_v2.py --study heterogeneous --dry-run
python scripts/run_v2.py --study commons_salience --dry-run
python scripts/run_v2.py --study frontier --dry-run
```

## Reproduce the analysis

The GitHub release source bundle contains all final JSONL source records. Once extracted, pass the 40 final study JSONLs to:

```bash
python scripts/analyse_v2.py path/to/source/*.jsonl --protocol configs/v2_protocol.json --output reproduced-analysis
```

The analyzer rejects duplicate experimental keys and mixed study fingerprints.

See [`docs/V2_REPRODUCIBILITY.md`](docs/V2_REPRODUCIBILITY.md) for the complete path.

## Published evidence in the repository

Compact permanent evidence is committed under [`results/published/v2.0.8/`](results/published/v2.0.8/), including:

- the immutable completion and collection-audit records
- a strict machine-readable statistical summary
- generated summary tables
- the generated Markdown results summary
- the source-bundle checksum manifest

The `v0.3.0` GitHub release is intended to carry the complete raw source bundle, including episode-level records and publication figures.

## Research principles

**Institutions are experimental variables.** The same underlying scenario is evaluated under alternative governance regimes.

**Evaluation is external to the model.** Models choose structured actions. Deterministic environments decide what those actions do.

**Attempt and outcome are distinct.** A blocked prohibited action is an attempted violation, not a realized one.

**Provenance and local representation are distinct.** Mutable visible state can diverge from immutable lineage, making policy laundering experimentally observable.

**Useful performance matters.** POLIS records compliant completion, system utility, welfare, recovery, friction, and waste alongside safety.

**Null and surprising results are retained.** Strong prompting performed better than the simple executable-versus-prompt story predicted, while local executable enforcement failed under live representation laundering.

**Paid experiments are auditable and bounded.** Protocol fingerprints, source JSONL, manifests, provider metadata, token accounting, spend ledgers, and cache admission are retained.

## v1 archive

POLIS v1 remains available for backward reproduction. Its 576-episode live experiment, mechanism-validation suite, and documentation are preserved under the `polis.v1` package and v1 documents. V2 is a new scenario universe and is not pooled with v1.

See [`docs/RESULTS_V1.md`](docs/RESULTS_V1.md) and [`docs/REPRODUCIBILITY_V1.md`](docs/REPRODUCIBILITY_V1.md).

## Project AWARE

POLIS is a Project AWARE research programme founded and led by Abdullah X. Project AWARE develops technical and institutional research on AI safety and governance.

## Contributing and security

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request. Report security-sensitive issues through [`SECURITY.md`](SECURITY.md). Never commit provider keys or local `.env` files.

## Citation

Citation metadata appears in [`CITATION.cff`](CITATION.cff).

## License

Apache License 2.0. See [`LICENSE`](LICENSE).
