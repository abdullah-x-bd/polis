# POLIS v1 Delegation Boundaries Stress Validation

## Purpose

This suite validates the institutional mechanisms with deterministic probe agents before spending money on LLM trajectories. It asks whether each institution behaves as designed under direct transfer, relabelling, and sanitization strategies.

These are **institutional stress-test results, not claims about frontier-model behaviour**.

## Design

The suite crosses:

- 24 frozen scenarios
- 6 professional domains
- 4 scenario types
- 4 institutional regimes
- 4 scripted probe strategies

Institutional regimes:

1. no institution
2. prompt-only governance
3. local executable guard
4. provenance-aware guard

Probe strategies:

- compliant
- direct delegation
- relabel then delegate
- sanitize then delegate

## Key results

### No institution and prompt-only enforcement layer

The deterministic attack policies are intentionally insensitive to natural-language prompting. Under both no institution and prompt-only governance, direct cross-principal transfer produced 18 realized violations across the 24 matched scenarios. Relabelling also produced 18 realized violations and 18 successful laundering outcomes.

This is expected and serves as a mechanism baseline rather than a behavioral claim about prompted LLMs.

### Local guard

The action-local guard eliminated realized direct-transfer violations in the scripted suite, but relabelling bypassed the current-artifact metadata check:

- direct strategy: 0 realized violations
- relabel strategy: 18 realized violations
- relabel strategy: 18 policy-laundering successes

This is the designed weakness of the local-metadata treatment.

### Provenance guard

The provenance-aware institution blocked the same relabelling route:

- direct strategy: 0 realized violations
- relabel strategy: 0 realized violations
- relabel strategy: 0 policy-laundering successes

The guard retains immutable root policy state while the agent and local metadata layer see only the current artifact view.

### Authorized sanitization remains possible

The scenario set contains six authorized-sanitization cases. In these cases the provenance mechanism permits the explicitly authorized sanitization path and subsequent external work rather than treating all cross-principal collaboration as forbidden.

This negative control is important: POLIS should reward institutions that prevent prohibited transfers without simply blocking useful collaboration.

## Threat-model interpretation

The local guard is intentionally evaluated under a **lossy metadata threat model** in which ordinary transformations can produce a derived artifact whose current visible policy metadata no longer reflects the root restriction. The experiment does not claim that every real local access-control implementation necessarily loses metadata this way.

The scientific comparison is whether retaining explicit policy provenance changes robustness when local policy context can be lost across transformations.

## Reproduce

```bash
python scripts/stress_delegation_v1.py
```

The script produces per-trial machine-readable records and an aggregate summary.
