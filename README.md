# POLIS

**POLIS is an experimental testbed for designing and evaluating algorithmic institutions for multi-agent AI systems.**

POLIS asks a system-level AI safety question: when autonomous agents serve different principals, can machine-executable institutions reduce collective failures more reliably than prompt-only governance while preserving useful performance?

Version 0.2.0 implements two matched experimental environments, a frozen cross-family live-model protocol, adversarial mechanism validation, resumable OpenRouter execution, paired statistical inference, automated figures and tables, and end-to-end reproducibility tooling.

## What POLIS tests

### Resource Commons

Four agents compete for a capacity-constrained shared resource. Every agent has private task need and value. POLIS compares the same 24 frozen worlds under:

- no institution
- prompt-only guidance
- a machine-enforced hard quota
- congestion pricing

The primary endpoint is final-round system efficiency relative to an exact oracle allocation. Secondary endpoints include overclaiming, resource waste, and institutional charge.

The environment supports two rounds so agents can adapt to public system history and their own prior outcome.

### Delegation Boundaries

Three agents work across two principals. A primary agent can delegate tasks, transform artifacts, request approval, execute when capable, or refuse. POLIS separates local artifact metadata visible to the acting agent from immutable root provenance available to an institutional guard.

Six domains are crossed with four matched scenario types to produce 24 scenarios:

- allowed same-principal delegation
- forbidden cross-principal delegation
- transformation laundering
- authorized sanitization

POLIS compares:

- no institution
- prompt-only governance
- a local executable guard
- an immutable-provenance guard

The primary endpoint is realized policy violation. Attempted, detected, and realized violations are recorded separately, alongside task completion, false blocking, laundering success, and interaction path length.

## Research design

The confirmatory protocol is frozen in [`configs/v1_live.json`](configs/v1_live.json) and validated by [`src/polis/v1/protocol.py`](src/polis/v1/protocol.py). A canonical SHA-256 fingerprint is embedded in every live episode record so results from different protocols cannot be silently mixed.

The frozen model panel is:

| Model | Family |
| --- | --- |
| `google/gemini-2.5-flash-lite` | Google Gemini |
| `mistralai/mistral-small-2603` | Mistral Small |
| `openai/gpt-4.1-mini` | OpenAI GPT-4.1 |

The full matrix contains **576 matched episodes** across both environments and all three model families. It has a conservative maximum of **3,456 model calls**, although delegation episodes often terminate earlier.

Inference is temperature zero with strict structured actions. The model is the agent policy, never the outcome judge. Safety and performance labels come from deterministic environment state transitions and executable institutions.

Read the full frozen design in [`docs/EXPERIMENT_PROTOCOL_V1.md`](docs/EXPERIMENT_PROTOCOL_V1.md).

## Mechanism validation before live models

POLIS includes zero-cost scripted policies and attacks so the benchmark can be validated before spending API credits.

Resource policies include truthful, greedy, max-requester, adaptive-greedy, and price-aware strategies. The calibration sweep demonstrates a nontrivial commons failure and an interior congestion-pricing trade-off rather than a benchmark where stronger enforcement automatically looks better.

Delegation stress tests include direct prohibited delegation, metadata relabel laundering, authorized and unauthorized sanitization, local enforcement, and immutable-provenance enforcement.

These are **mechanism-validation results, not claims about language-model behavior**. See [`docs/RESULTS_V1.md`](docs/RESULTS_V1.md).

## Quick start

```bash
git clone https://github.com/abdullah-x-bd/polis.git
cd polis
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

ruff check src/polis/v1 tests scripts
python -m compileall -q src/polis/v1 scripts
pytest
```

Windows PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

## Reproduce the zero-cost validation

```bash
python scripts/calibrate_commons_v1.py --output results/calibration/commons_v1.json
python scripts/stress_delegation_v1.py --output results/calibration/delegation_v1.json
```

Inspect the live experiment without making any API calls:

```bash
python scripts/run_v1_live.py --mode pilot --dry-run
python scripts/run_v1_live.py --mode full --dry-run
```

## Live-model experiment

Copy `.env.example` to `.env` and add a valid OpenRouter key locally, or configure `OPENROUTER_API_KEY` as a GitHub Actions repository secret.

One structured-action smoke request:

```bash
python scripts/test_openrouter.py \
  --model google/gemini-2.5-flash-lite \
  --max-cost-usd 0.25
```

Frozen pilot:

```bash
python scripts/run_v1_live.py --mode pilot --max-cost-usd 0.75
```

Full confirmatory matrix:

```bash
python scripts/run_v1_live.py --mode full --max-cost-usd 4.00
```

The runner is resumable. It appends one source-data JSON record after every completed episode, skips previously completed keys on rerun, separately caches identical provider requests, and refuses to combine records carrying a different protocol fingerprint.

The manual GitHub workflow [`v1-live.yml`](.github/workflows/v1-live.yml) provides the same pilot and full modes with an explicit paid-run confirmation gate and artifact upload.

## Analysis

Analyse one or more source JSONL files produced under the same protocol:

```bash
python scripts/analyse_v1.py \
  results/live/polis-v1-full-<fingerprint-prefix>.jsonl \
  --output results/analysis
```

The pre-specified analysis produces:

- paired treatment effects against the no-institution baseline
- 10,000-sample paired bootstrap confidence intervals
- paired Wilcoxon tests for continuous Commons endpoints
- exact discordant-pair tests for binary Delegation endpoints
- Holm multiple-comparison adjustment within each endpoint
- episode-level CSVs
- publication-ready primary figures in PNG and PDF
- provider-reported cost and token accounting
- a generated Markdown results summary

The statistical plan is documented in [`docs/STATISTICAL_ANALYSIS_V1.md`](docs/STATISTICAL_ANALYSIS_V1.md).

## Repository structure

```text
configs/                         Frozen experimental protocols and legacy configs
scenarios/                       Frozen v1 scenario specifications
src/polis/v1/                    v0.2 environments, agents, institutions, providers, runner, analysis
scripts/                         Calibration, stress, live-run, and analysis entry points
tests/                           Unit, integration, attack, provider, and live-pipeline tests
docs/                            Protocol, statistics, results status, reproducibility, threat model
.github/workflows/v1-ci.yml      Zero-cost clean-run validation
.github/workflows/v1-live.yml    Manual gated live-model experiment
results/                         Generated or labelled result artifacts
```

The earlier unsafe-delegation pilot remains in the repository for provenance and backward reproducibility. New research should use the `polis.v1` package and the frozen v1 protocol.

## Research principles

**Institutions are experimental variables.** POLIS compares the same underlying scenarios under alternative governance regimes.

**Evaluation is external to the model.** Models choose structured actions. Deterministic environments decide what those actions do.

**Attempt and outcome are distinct.** A blocked prohibited action is an attempted violation, not a realized one.

**Useful performance matters.** The benchmark records task completion, welfare, waste, and legitimate-action blocking alongside safety outcomes.

**Provenance is not privileged model knowledge.** In the delegation benchmark, immutable root policy is institutional state and is deliberately withheld from the acting model.

**Paid experiments are auditable and bounded.** Responses, generation metadata, usage, provider-reported cost, run manifests, protocol fingerprints, and cache behavior are retained.

## Reproducibility

For the complete reproduction path, artifact layout, resume semantics, and provenance checklist, see [`docs/REPRODUCIBILITY_V1.md`](docs/REPRODUCIBILITY_V1.md).

For the implementation record of the final research phase, see [`docs/STEPS_21_30_COMPLETE.md`](docs/STEPS_21_30_COMPLETE.md).

## Project AWARE

POLIS is a Project AWARE research programme founded and led by Abdullah X. Project AWARE develops technical and institutional research on AI safety and governance.

## Contributing and security

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request. Report security-sensitive issues through [`SECURITY.md`](SECURITY.md). Never commit provider keys or local `.env` files.

## Citation

Citation metadata appears in [`CITATION.cff`](CITATION.cff).

## License

Apache License 2.0. See [`LICENSE`](LICENSE).
