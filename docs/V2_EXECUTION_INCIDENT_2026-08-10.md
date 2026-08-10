# POLIS v2 Execution Incident and Compatibility Record

Date: 2026-08-10

This document records technical execution failures and compatibility repairs separately from scientific outcomes. Historical technical runs are not silently pooled into the final v2.0.8 episode-level inferential dataset.

## Scientific invariants

Across the execution-repair sequence, POLIS preserved the core research question, deterministic governance mechanisms, fresh scenario universe, endpoint definitions, and preregistered analysis families. Any technical change that affected an executable model endpoint or protocol interface received a new protocol version/fingerprint rather than being hidden under an old freeze.

## Excluded v2.0.2 technical launch 1

Workflow run `31337384458`, execution SHA `d55b82e7dbfa01d139daa21a7021e3b270a796e1`.

The run exposed two interface failures. Some structurally valid model actions had a free-text `justification` longer than the local 500-character representation limit, and a Qwen endpoint returned empty structured output after reaching the bounded output budget.

The justification fix is deterministic metadata normalization only. If the provider returns more than 500 characters, the stored action representation is truncated while full raw provider text remains retained. Justification does not drive permissions, state transitions, task completion, violation labels, or welfare. No action-bearing field is repaired.

## Excluded v2.0.2 technical launch 2

Workflow run `31337778389`, execution SHA `06fa86735355dd1756a8a1c34671c44da1eb39e1`.

The recurring blocker was the reasoning-enabled Qwen3.7 Plus endpoint consuming its bounded output allowance without returning a usable structured action. Rather than silently alter its reasoning budget after collection began, the endpoint was replaced under a new protocol version and passed the common compatibility gate.

## Later endpoint verification and refreezes

Subsequent technical validation established the final executable panel and provider controls. Historical v2.0.1 through v2.0.7 notes remain in the repository as an audit trail and should not be read as the current protocol.

The final v2.0.8 panel is:

- `google/gemini-2.5-flash-lite`
- `mistralai/mistral-small-2603`
- `openai/gpt-4.1-mini`
- `deepseek/deepseek-v3.2`, reasoning disabled
- `qwen/qwen3-235b-a22b-2507`
- `anthropic/claude-sonnet-4.5`
- `openai/gpt-4.1`

Final frozen identifiers:

- protocol `2.0.8`
- config digest `f72f6d683b88d1f11b7ec1d840413f805a619a5433ce431c445b16831aa3346b`
- design digest `c5d6a750c495d14d0d745a9ee317cd40fa20ecd5c2e3e735fd74b195363182e8`
- fingerprint `f169dc157fd6f31d0f0ce0a76a0c51049f9b0a28eba08fc3201b616e1ce001e3`

## v2.0.7 technical collection and cache admission

A later technical collection produced provider responses that could potentially be reused, but the final v2.0.8 analysis does not simply treat those earlier episode records as the final dataset.

Before the final run, a zero-provider-call cache audit revalidated exact request/response objects under the v2.0.8 parser and final model panel. It:

- admitted 3,596 exact response objects
- excluded 43 requests associated with obsolete `deepseek-v4-flash`
- rejected one legacy response that failed final semantic validation
- made zero provider calls

Admission depended on exact request identity and v2.0.8 interface/semantic validity, not on scientific outcomes. The canonical final execution then reconstructed all 5,280 v2.0.8 episode records under the frozen environment and fingerprint.

## Canonical v2.0.8 execution

Workflow run `31359824031`, execution SHA `4431fa5ceb5f9700cf9a650dba2d0478ea08c267`.

The pre-analysis gate verified:

- 5,280 expected episodes
- 5,280 observed episodes
- 5,280 unique keys
- zero duplicate keys
- exact per-study counts
- one v2.0.8 fingerprint throughout
- no unexpected model IDs

Final provider/interface diagnostics:

- 10,720 model-call records
- 97 deterministic justification truncations
- 9 filled missing nullable fields
- 6 dropped extra non-action fields
- zero routed-model identity mismatches
- 48 semantic invalid actions handled by frozen environment semantics
- zero retry events

The full dataset represents $3.023621 in provider-reported response cost. The incremental spend for the final run was $1.967216 because audited exact responses were reused.

## Canonical artifact

Artifact ID `9053667558`, name `polis-v208-final-complete-31359824031`, SHA-256 `9f0eb0db21e32a0e72f266069634899af5814589608426504acbce9414c3064c`.

The final GitHub release should preserve this bundle as the permanent source archive.

## Post-run sealing

The final paid collector, legacy paid recovery workflows, and historical paid endpoint smoke workflows are sealed after successful completion. They make no provider calls in the release branch.
