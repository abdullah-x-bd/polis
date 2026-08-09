# POLIS v2.0.2 execution incident record

Date: 2026-08-10 IST

## Scope

This note was committed before any scientific outcome analysis from the confirmatory study.
It records a technical execution failure discovered during the first attempt to collect the
frozen POLIS v2.0.2 matrix and fixes the inclusion rule before the replacement run is
analysed.

## Frozen scientific design

The incident did not change the scientific design. The following values remain fixed:

- protocol version: `2.0.2`
- config digest: `b947c916ace60ae3e64f5ca047b9bb10b10ce02b6151badd2c248838387e1aa5`
- design digest: `6efba6e49955923ce13d70e7e4e672f3173a83c1bed0522b7eae65452023b964`
- study fingerprint: `e49d69fb88fed250268aba7d9e9912b98bbb07cacbc114a1a0ba05e4480e44f2`
- planned episode count: 5,280
- model panel, scenarios, governance regimes, repetitions, metrics, and preregistered analyses: unchanged

## Aborted technical launch

Initial workflow run: `31337384458`

Initial execution SHA: `d55b82e7dbfa01d139daa21a7021e3b270a796e1`

Several live batches terminated when a model returned an otherwise structurally valid
action whose free-text `justification` exceeded the local `Action` representation's
500-character maximum. The portable provider wire schema intentionally omits unsupported
string-length keywords, so provider-side structured output could not enforce this local
metadata bound. The provider attempted Pydantic validation directly and raised instead of
canonicalizing the non-outcome metadata.

The observed exception was consistently:

`ValidationError: justification: String should have at most 500 characters`

Before choosing the recovery rule, inspection was limited to workflow status, exception
logs, result counts, manifests, cache counts, model identifiers, and spend ledgers. No
scientific outcome comparison, treatment effect, headline metric, table, or figure from
this run was inspected.

## Technical correction

Provider parsing now applies one deterministic normalization before Pydantic validation:
if and only if `justification` is a string longer than 500 characters, the stored action
representation is truncated to the already-defined 500-character limit.

This field is explanatory metadata. POLIS institutions, environment transitions, action
admissibility, task completion, violation logic, welfare calculations, and statistical
metrics do not consume justification text.

The correction therefore does not repair or alter any action-bearing field. In particular:

- action enum remains unchanged
- amount validation remains unchanged
- targets and artifact identifiers remain unchanged
- transformation semantics remain unchanged
- governance rules remain unchanged
- environment validation remains unchanged
- negative or otherwise semantically invalid action fields still fail validation

The complete provider response remains preserved in `ModelResponse.raw_text`, and each
normalization is marked with `response_metadata.justification_truncated=true` plus the
500-character canonical limit. Unit tests explicitly verify both truncation and the
continued rejection of semantically invalid fields.

Provider patch commit: `8f521dad4881a3b752b19c11bfb96f8d60358d2d`

Test commit: `06fa86735355dd1756a8a1c34671c44da1eb39e1`

## Dataset inclusion rule fixed before analysis

The entire initial run `31337384458` is an excluded technical pre-run.

**No episode from that run may enter the final POLIS v2.0.2 inferential dataset, even if an
episode completed successfully.** This avoids mixing executions across the parser patch and
prevents outcome-dependent cherry-picking of completed records.

The replacement clean run is workflow run `31337778389`, launched from the patched execution
revision. It starts all frozen episode keys from scratch and is the only live-run candidate
for the final 5,280-episode dataset. Its evidence is admissible only if all frozen completeness,
uniqueness, fingerprint, manifest, and analysis gates pass.

## Orchestration hardening

The full confirmatory workflow was subsequently changed to explicit `workflow_dispatch`
only so ordinary code, documentation, or result commits cannot accidentally launch another
paid sample. This orchestration change does not alter the frozen scientific fingerprint.

## Reporting obligation

The final v2 methods/reproducibility material must disclose:

1. the aborted technical launch,
2. the exact failure class,
3. the deterministic non-outcome metadata normalization,
4. the full-run exclusion rule,
5. the clean replacement execution SHA and workflow run,
6. the number of normalized justifications in the final sample,
7. the final provider-reported token and cost totals.
