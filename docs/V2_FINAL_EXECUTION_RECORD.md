# POLIS v2.0.8 Final Execution Record

Canonical workflow run: `31359824031`

Execution SHA: `4431fa5ceb5f9700cf9a650dba2d0478ea08c267`

Protocol fingerprint: `f169dc157fd6f31d0f0ce0a76a0c51049f9b0a28eba08fc3201b616e1ce001e3`

## Completeness

- expected episodes: 5,280
- observed episodes: 5,280
- unique episode keys: 5,280
- duplicate keys: 0
- unexpected model IDs: 0
- retry events: 0

Study counts match the frozen matrix exactly: 2,304 Delegation main, 1,152 wording robustness, 576 heterogeneous teams, 960 Commons salience, and 288 frontier diagnostic.

## Provider accounting

- model-call records in final dataset: 10,720
- total tokens: 8,927,565
- provider-reported response cost represented by the dataset: $3.02362104836
- newly paid calls in the final v2.0.8 run: 6,217
- incremental provider spend in that run: $1.96721641255

The difference exists because the final execution reused an independently audited cache of exact provider requests. The zero-spend audit admitted 3,596 exact response objects, excluded 43 requests from the obsolete `deepseek-v4-flash` interface, and rejected one legacy response that failed the frozen v2.0.8 semantic parser. Cache admission did not use scientific outcomes. Every final episode was reconstructed under the v2.0.8 environment and fingerprint.

## Provider-interface diagnostics

- justification metadata truncations: 97
- missing nullable fields filled by deterministic parser normalization: 9
- extra non-action fields dropped: 6
- routed model identity mismatches: 0
- semantic invalid actions handled by the environment: 48 actions across 48 episodes

Invalid actions were not imputed or silently repaired. The environment handled them using the frozen invalid-action semantics.

## Immutable research artifact

GitHub Actions artifact ID: `9053667558`

Artifact name: `polis-v208-final-complete-31359824031`

Artifact ZIP size: 2,985,360 bytes

Artifact ZIP SHA-256: `9f0eb0db21e32a0e72f266069634899af5814589608426504acbce9414c3064c`

The bundle contains source JSONL, manifests, spend ledgers, the collection audit, completion record, generated `analysis.json`, episode tables, result tables, and publication figures. It should be attached unchanged to the `v0.3.0` GitHub release as the permanent source bundle.

## Post-execution safety

The final paid collector and historical paid smoke workflows are sealed before merge. Subsequent result, documentation, tag, and release operations make no model-provider calls.
