# Scripted smoke test

These outputs validate the POLIS experiment runner, institutional interface, metrics, and audit pipeline. They use a deterministic scripted policy. They do not constitute evidence about frontier-model behaviour.

Reproduce them with:

```bash
python scripts/run_experiment.py --config configs/baseline.json --output results/pilot_run/runs
python scripts/run_experiment.py --config configs/prompt_only.json --output results/pilot_run/runs
python scripts/run_experiment.py --config configs/regulator.json --output results/pilot_run/runs
python scripts/analyse_results.py results/pilot_run/runs
```
