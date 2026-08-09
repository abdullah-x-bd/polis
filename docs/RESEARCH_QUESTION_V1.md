# POLIS v1 Research Questions

## Central question

Can machine-executable institutions improve system-level safety and useful performance in multi-agent AI systems beyond what can be achieved through agent-level prompting alone?

POLIS treats institutional architecture as an experimental variable. The agents, tasks, information structure, model configuration, and random seeds are held fixed while the institution changes.

## RQ1: Emergence of collective failure

Do multi-agent systems exhibit measurable collective failures when individually controlled agents pursue local objectives under scarce resources, asymmetric capabilities, or cross-principal constraints?

## RQ2: Prompt governance

Does communicating a norm or policy through the agent prompt reduce the target failure relative to an otherwise identical system with no governance?

## RQ3: Executable institutions

Do machine-executable institutions reduce realized system-level failures more than prompt-only governance?

## RQ4: Institutional design

Do institutions matched to the structure of the underlying coordination problem occupy a better safety-performance frontier than blunt constraints?

## V1 experimental domains

POLIS v1 evaluates two distinct institutional problems.

1. **Resource Commons**: multiple agents compete for scarce compute. Local incentives can produce strategic overclaiming and inefficient allocation. POLIS compares no governance, prompt-only governance, hard quotas, and congestion pricing.
2. **Delegation Boundaries**: agents serving different principals collaborate across capability boundaries. Efficient delegation can conflict with information or authority constraints. POLIS compares no governance, prompt-only governance, action-local enforcement, and provenance-aware enforcement.

## Primary contribution

POLIS v1 is designed to establish an experimental methodology rather than a universal theorem about AI governance. Its core contribution is a controlled way to measure how institutional mechanisms change multi-agent outcomes while keeping the underlying system fixed.

## Claim boundary

Results from POLIS v1 apply to the tested synthetic environments, model endpoints, prompts, institutional mechanisms, and scenario distributions. They do not establish that the same mechanisms will govern arbitrary deployed autonomous systems.
