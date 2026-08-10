# POLIS v2 Threat Model and Claim Boundaries

## Agent-level threats

- direct prohibited cross-principal transfer
- repeated attempts after an executable denial
- representation-changing transformations that cause local policy metadata to be lost
- unauthorized sanitization
- selecting a higher-payoff policy-conflicting route as goal-policy pressure rises
- cap seeking and resource overclaiming
- invalid but schema-conformant actions

## Institution-level threats

- hard enforcement that achieves safety only by destroying useful completion
- local metadata becoming detached from root policy lineage
- visible numerical rules becoming behavioral focal points
- prompt governance depending strongly on model family
- heterogeneous team composition creating weakest-link failures
- information asymmetry being mistaken for an enforcement advantage

## Experimental controls

- identical underlying scenario cells across governance treatments
- fresh v2 identifiers rather than recycling v1 observations
- a provenance-informed prompt treatment separating information from enforcement
- recoverable executable denial rather than terminal blocking
- explicit goal-policy conflict pressure
- hidden versus visible identical quota mechanics
- wording-equivalent variants
- homogeneous and heterogeneous model teams
- deterministic environment-based scoring rather than an LLM judge
- scripted stress policies before any paid model run

## What v2 can support

If the planned results support the hypotheses, v2 can establish controlled evidence that different institutional architectures occupy different safety-performance trade-offs, that these trade-offs change under optimization pressure and model composition, and that some institution representations can alter agent behavior beyond their direct mechanical effect.

## What v2 cannot support

V2 does not establish that the tested mechanisms solve real-world AI governance, guarantee safety under arbitrary adversaries, generalize to every agent architecture, or represent human institutional behavior. The task environments are synthetic and deliberately small enough for exact auditing.

Frontier-model diagnostic results remain a subset analysis rather than evidence that the complete model ecosystem behaves identically.

The local-policy-loss transformation is an explicit experimental abstraction of metadata loss across representation changes. It should not be described as an empirical claim that every deployed transformation pipeline loses policy metadata in this way.

## Negative-result policy

Null and contrary results are retained. In particular:

- provenance enforcement may fail to outperform local enforcement if live agents do not exploit the local vulnerability
- strong prompts may outperform executable guards for some models
- goal-policy pressure may not create the predicted stress curve
- visible quotas may not reproduce the v1 exploratory cap-seeking pattern
- heterogeneous governance may increase rather than decrease composition variance

No condition is removed because its result is inconvenient after paid collection starts.
