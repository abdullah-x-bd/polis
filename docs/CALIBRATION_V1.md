# POLIS v1 Resource Commons Calibration

## Purpose

This calibration is performed with deterministic scripted policies before confirmatory LLM runs. It is used to establish that the environment contains a meaningful strategic resource-allocation problem and to select fixed institutional parameters without tuning on model outcomes.

These numbers are **mechanism-calibration evidence, not evidence about LLM behaviour**.

## Calibration design

The sweep uses all 24 frozen Resource Commons worlds across low, medium, and high scarcity.

Scripted populations:

- truthful
- greedy
- mixed: truthful, greedy, max-requester, and adaptive-greedy agents
- price-aware: agents that compute a one-step best response to the announced quadratic congestion charge using an equal-share prior in round one and the previous aggregate demand in round two

Institutional sweep:

- no institution
- prompt-only governance
- hard quota: 20, 25, 30, 35, 40 units
- congestion pricing alpha: 0.02, 0.05, 0.10, 0.20, 0.40, 0.80

The scripted policies do not interpret natural-language prompt governance, so no-institution and prompt-only outcomes are intentionally identical in this calibration. The prompt treatment is evaluated behaviorally only with LLM agents.

## Key calibration observations

### Strategic failure exists

Under the mixed scripted population with no institution:

- mean welfare: 19.6762
- mean efficiency relative to the allocation oracle: 0.8170
- mean overclaim ratio: 1.0762
- mean resource waste: 23.4228

This confirms that local request strategies can create a substantial system-level coordination failure.

### Hard quota has a real rigidity trade-off

With truthful agents, quota 20 reduced mean efficiency to 0.8238, while quota 30 achieved 0.9631. This is useful for the experiment because a constraint can improve discipline while still creating legitimate-performance costs when set too tightly.

### Congestion pricing has an interior calibration

For the adaptive price-aware population:

| alpha | mean efficiency | mean overclaim | mean waste |
|---:|---:|---:|---:|
| 0.02 | 0.9595 | 0.3115 | 0.1198 |
| 0.05 | 0.9691 | 0.2401 | 0.0752 |
| 0.10 | 0.9768 | 0.1251 | 0.1434 |
| **0.20** | **0.9799** | **0.0299** | 0.1929 |
| 0.40 | 0.9399 | 0.0000 | 0.0000 |
| 0.80 | 0.6854 | 0.0000 | 0.0000 |

The sweep therefore shows the desired non-monotonic trade-off. Stronger pricing eventually eliminates overclaiming by inducing under-requesting and reducing useful welfare.

## Frozen v1 mechanism parameters

For the first LLM pilot, POLIS freezes:

- **Hard quota: 30 units**
- **Congestion pricing alpha: 0.20**

These are the existing defaults in the v1 institution implementations.

They may be revisited only if the pilot reveals an implementation ambiguity or an obvious scale mismatch that makes the treatment unintelligible to model agents. Any such change must be documented before confirmatory runs.

## Reproduce

```bash
python scripts/calibrate_commons_v1.py
```

The script evaluates every mechanism/population combination against all frozen v1 worlds and writes a machine-readable JSON result.
