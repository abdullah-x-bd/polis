# Contributing to POLIS

POLIS welcomes contributions that improve experimental validity, reproducibility, or institutional design.

## Before contributing

1. Open an issue that states the research problem.
2. Explain which assumption or mechanism the change tests.
3. Keep agent policy separate from institutional enforcement.
4. Add tests for every enforcement rule.
5. Record limitations directly in the pull request.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Research standards

- Never present scripted smoke tests as evidence about frontier models.
- Preserve raw configurations and audit logs.
- Predefine primary metrics before large runs.
- Report failed replications and null results.
- Avoid benchmarks that contain actionable harmful instructions.
