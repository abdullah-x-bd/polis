.PHONY: install test validate calibrate stress plan-pilot plan-full smoke pilot full analyse

install:
	python -m pip install -e ".[dev]"

test:
	pytest

validate:
	ruff check src/polis/v1 tests scripts
	python -m compileall -q src/polis/v1 scripts
	pytest
	python scripts/run_v1_live.py --mode full --dry-run

calibrate:
	python scripts/calibrate_commons_v1.py --output results/calibration/commons_v1.json

stress:
	python scripts/stress_delegation_v1.py --output results/calibration/delegation_v1.json

plan-pilot:
	python scripts/run_v1_live.py --mode pilot --dry-run

plan-full:
	python scripts/run_v1_live.py --mode full --dry-run

smoke:
	python scripts/test_openrouter.py --model google/gemini-2.5-flash-lite --max-cost-usd 0.25

pilot:
	python scripts/run_v1_live.py --mode pilot --max-cost-usd 0.75

full:
	python scripts/run_v1_live.py --mode full --max-cost-usd 4.00

analyse:
	@test -n "$(RESULTS)" || (echo "Set RESULTS to one or more POLIS v1 JSONL files" && exit 1)
	python scripts/analyse_v1.py $(RESULTS) --output results/analysis
