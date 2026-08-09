# POLIS v2 Freeze Criteria

The draft protocol may be changed to `frozen` only after all of the following hold on a clean GitHub Actions checkout:

- package installation succeeds
- Ruff passes
- Python compilation passes
- every v2 unit/integration test passes
- scripted Delegation stress suite runs to completion
- scripted Commons stress suite runs to completion
- all five dry-run study plans produce their pre-specified episode counts
- no paid v2 model result has been observed

The freeze is then recorded by protocol version, Git commit, design digest and study fingerprint before paid inference begins.
