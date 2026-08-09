# POLIS v2 execution incident record

Date: 2026-08-10 IST

## Scope

This note is part of the protocol audit trail and was updated before scientific outcome
analysis of the final confirmatory dataset. It records two excluded v2.0.2 technical
launches, the technical corrections they motivated, the v2.0.3 model-panel refreeze, and
the inclusion rule fixed before the final run.

No treatment effect, headline outcome, inferential table, figure, or scientific comparison
from either excluded run was inspected before these rules were fixed. Inspection was limited
to workflow status, exception traces, episode/manifests counts, cache counts, model IDs,
provider metadata, and spend ledgers.

## Scientific design that did not change

The scientific design remained unchanged throughout the execution repair:

- planned episode count: 5,280
- scenario universe and scenario texts
- governance regimes
- repetitions
- random seed
- environment mechanics
- outcome definitions
- metrics
- preregistered statistical analyses
- 512-token structured-action output ceiling

The unchanged scenario/design digest is:

`6efba6e49955923ce13d70e7e4e672f3173a83c1bed0522b7eae65452023b964`

## Excluded technical launch 1

Workflow run: `31337384458`

Execution SHA: `d55b82e7dbfa01d139daa21a7021e3b270a796e1`

Frozen protocol: `2.0.2`

Several batches terminated when an otherwise structurally valid action contained a
free-text `justification` longer than the local `Action` representation's 500-character
maximum. The portable provider wire schema intentionally omits validation keywords that are
not accepted consistently by the selected providers, so provider-side structured output
could not enforce this local metadata bound.

Observed exception class:

`ValidationError: justification: String should have at most 500 characters`

A separate batch also exposed an empty structured action from `qwen/qwen3.7-plus` with
`finish_reason='length'`.

### Non-outcome metadata correction

Provider parsing now applies one deterministic normalization before Pydantic validation:
if and only if `justification` is a string longer than 500 characters, the stored action
representation is truncated to the already-defined 500-character local limit.

`justification` is explanatory metadata. Institutions, environment transitions, action
admissibility, task completion, policy-violation logic, welfare calculations, and
statistical metrics do not consume it. The complete provider text remains in
`ModelResponse.raw_text`, and normalization is explicitly marked in response metadata.

No action-bearing field is repaired. In particular, action enum, amount validation,
targets, artifact identifiers, transformations, governance semantics, and environment
validation are unchanged. Semantically invalid action fields still fail validation.

Provider patch commit: `8f521dad4881a3b752b19c11bfb96f8d60358d2d`

Validation tests commit: `06fa86735355dd1756a8a1c34671c44da1eb39e1`

## Excluded technical launch 2

Workflow run: `31337778389`

Execution SHA: `06fa86735355dd1756a8a1c34671c44da1eb39e1`

Frozen protocol: `2.0.2`

This launch started from scratch with deterministic justification canonicalization enabled.
All four live batches ultimately failed. The recurring blocking failure was the Qwen
endpoint returning no structured action after consuming the 512-token output allowance:

`RuntimeError: OpenRouter returned an empty structured action for model='qwen/qwen3.7-plus', finish_reason='length'`

Because Qwen3.7 Plus is a reasoning-enabled endpoint, its internal reasoning competes with
the structured action for the same bounded output budget. Rather than introduce an
endpoint-specific reasoning setting after collection had begun, POLIS replaced this one
model with a non-thinking Qwen-family instruction endpoint and refroze the panel.

## v2.0.3 endpoint replacement and refreeze

Only the Qwen endpoint changed:

- removed: `qwen/qwen3.7-plus`
- added: `qwen/qwen3-235b-a22b-2507`
- panel label: `Qwen3 235B A22B Instruct 2507`

The other six frozen endpoints are unchanged:

1. `google/gemini-2.5-flash-lite`
2. `mistralai/mistral-small-2603`
3. `openai/gpt-4.1-mini`
4. `deepseek/deepseek-v4-flash`
5. `anthropic/claude-sonnet-4.5`
6. `openai/gpt-5-mini`

The replacement Qwen endpoint and all six retained endpoints passed the same production
structured-action smoke gate in workflow run `31338155595` before confirmatory collection.

The refrozen v2.0.3 identifiers are:

- protocol version: `2.0.3`
- config digest: `28c392732c6f3b9bd122d91d3397f87bf2ecaf21e7a832c588f4dff652b7260c`
- design digest: `6efba6e49955923ce13d70e7e4e672f3173a83c1bed0522b7eae65452023b964`
- study fingerprint: `26dbae58963f556f048e91fb30ce2130f6bfe1cadbced258e1fb38caec9d40a8`

The unchanged design digest provides a machine-checkable record that the scenario and
experimental design were not tuned in response to the technical failures.

The v2.0.3 preflight in workflow run `31338255907` independently reproduced the hashes and
all five frozen study sizes before launch.

## Dataset inclusion rule fixed before analysis

Both v2.0.2 runs are excluded technical pre-runs:

- `31337384458`
- `31337778389`

**No episode from either run may enter any final POLIS v2 inferential dataset, even if that
episode completed successfully.** The exclusion is run-level, not outcome-level, which
prevents cherry-picking successful records across execution interfaces.

The only dataset eligible for the final v2 analysis is a fresh v2.0.3 execution that starts
all 5,280 frozen completion keys from scratch under fingerprint
`26dbae58963f556f048e91fb30ce2130f6bfe1cadbced258e1fb38caec9d40a8` and passes every
completeness, uniqueness, manifest, fingerprint, and analysis gate.

## Orchestration hardening

The full confirmatory workflow is explicit-launch only after freeze. Automatic endpoint
smoke execution is also disabled after the green seven-model gate. This prevents ordinary
code, documentation, or result commits from silently creating additional paid samples.

## Final reporting obligations

The final v2 methods and reproducibility material must disclose:

1. both excluded technical launches and their run IDs,
2. the justification-length failure and deterministic non-outcome normalization,
3. the Qwen3.7 Plus output-length failure,
4. the v2.0.3 Qwen endpoint replacement and seven-model smoke gate,
5. the old and new fingerprints and unchanged design digest,
6. the run-level exclusion rule,
7. the final clean execution SHA and workflow run ID,
8. the number of normalized justifications in the final sample,
9. provider-reported token and cost totals,
10. all final completeness and fingerprint checks.
