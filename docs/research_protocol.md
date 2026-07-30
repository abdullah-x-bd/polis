# Research protocol: unsafe delegation

## Research question

Does a coded delegation regulator reduce rule evasion in a multi-agent system while preserving legitimate task completion?

## Unit of analysis

One trial contains a principal task, a primary agent, a delegate agent, and one institutional regime.

## Initial hypothesis

The coded regulator will reduce successful prohibited delegation relative to the no-governance baseline. It should preserve legitimate delegation because it evaluates task status rather than blocking delegation generally.

## Experimental conditions

### No governance

The environment records structured actions and permits every action.

### Prompt-only guidance

The primary agent receives a restriction through its policy context. The environment records the resulting action and imposes no external constraint.

### Coded regulator

An external institution evaluates each delegation request. It blocks requests labelled as restricted and records the decision in an audit log.

## Controlled variables

The initial scripted study holds the task distribution, action schema, agent roles, trial count, and random seed constant. Only the governance regime and prompt-compliance probability differ.

When model-backed agents replace the scripted policy, each comparison should hold model version, temperature, tool access, context, and task set constant.

## Primary outcome

Successful completion of a prohibited delegated task.

## Secondary outcomes

- Detection of attempted violations
- Blocking of legitimate actions
- Successful completion of legitimate tasks

## Interpretation

The scripted pilot validates the research pipeline. It does not estimate how often frontier agents will evade rules. Frontier-model experiments require preregistered tasks, repeated seeds, prompt leakage checks, and independent review.
