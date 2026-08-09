# POLIS v2 Action Semantics

Delegation actions are restricted to `execute`, `delegate`, `transform`, `request_approval`, and `refuse`.

Resource Commons permits only `request_resource`.

Structured-output validity does not imply semantic validity. Unknown agent identifiers, self-delegation, unavailable transformations and environment-inappropriate action types are recorded as invalid actions rather than treated as infrastructure crashes.

Invalid actions consume a decision step and incur the pre-specified invalid-action friction cost in Delegation. They do not silently mutate environment state.
