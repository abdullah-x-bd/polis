# POLIS v2 Evaluation Principle

No POLIS v2 safety or task-success label is assigned by an LLM judge.

Models choose structured actions. The environment has ground-truth principals, capabilities, artifact lineage, policy state, task values and resource needs. Institutional code decides whether executable actions are permitted. Environment transitions then determine realized policy violation, completion, utility and resource outcomes.

This makes the evaluation target inspectable and avoids conflating the behavior being measured with a second model's subjective interpretation of that behavior.
