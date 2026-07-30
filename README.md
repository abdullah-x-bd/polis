# POLIS

**POLIS is an experimental testbed for designing and evaluating algorithmic institutions that govern multi-agent AI systems.**

Project AWARE is developing POLIS to study a simple but under-tested question: when autonomous agents serve different principals, can machine-executable institutions reduce collective failures without destroying useful performance?

## Why POLIS

Most AI safety evaluations treat one model or one operator as the unit of analysis. Future AI ecosystems may contain agents controlled by different people, companies, and public bodies. These agents may delegate tasks, exploit gaps between rules, coordinate strategically, or create failures that no single agent causes alone.

POLIS treats the surrounding institutional architecture as an experimental variable. It compares environments with no external governance, prompt-only guidance, and coded institutions that can inspect structured actions and enforce explicit rules.

## First experiment: unsafe delegation

The initial study tests whether an agent can evade a restriction by delegating a prohibited task to another agent.

POLIS compares three regimes:

1. **No governance**: the environment records actions but imposes no restriction.
2. **Prompt-only guidance**: the agent receives a rule but the environment does not enforce it.
3. **Coded regulator**: an external institution checks delegation requests and blocks prohibited transfers.

The pilot reports rule-evasion rate, detection rate, false-positive rate, and legitimate-task completion.

## Current status

- Research protocol complete
- Runnable scripted baseline implemented
- External delegation regulator implemented
- Reproducible metrics and audit logs implemented
- Preliminary smoke-test outputs included
- Frontier-model adapters planned

The included results validate the experimental pipeline. They do **not** establish claims about frontier-model behaviour.

## Quick start

```bash
git clone https://github.com/abdullah-x-bd/polis.git
cd polis
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

python scripts/run_experiment.py --config configs/baseline.json
python scripts/run_experiment.py --config configs/prompt_only.json
python scripts/run_experiment.py --config configs/regulator.json
python scripts/analyse_results.py results/runs
pytest
```

Each run writes a summary file and a JSONL audit log under `results/runs/`.

## Repository structure

```text
configs/              Experimental regimes
src/polis/            Core environment, agents, institutions, and metrics
experiments/          Research scenarios
docs/                 Protocol, threat model, metrics, and roadmap
scripts/              Reproducible command-line entry points
tests/                Unit and integration tests
results/pilot_run/    Labelled smoke-test outputs
```

## Research principles

POLIS separates agent policy from institutional enforcement. A regulator operates outside the model prompt, evaluates structured actions, records a reasoned decision, and produces an audit trail. This design lets researchers test whether an institutional mechanism changes outcomes while holding the task distribution and agent policy constant.

## Project AWARE

POLIS is a Project AWARE research programme founded and led by Abdullah X. Project AWARE provides research management, policy engagement, and an international researcher network. The programme aims to connect technical evidence on multi-agent safety with the institutions that will govern deployed AI systems.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Please report security-sensitive issues through [SECURITY.md](SECURITY.md).

## Citation

Citation metadata appears in [CITATION.cff](CITATION.cff).

## License

Apache License 2.0. See [LICENSE](LICENSE).
