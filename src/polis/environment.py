"""Experimental environments for POLIS."""

from __future__ import annotations

import random

from .agents import ScriptedAgent
from .institutions import Institution
from .models import TrialOutcome


class UnsafeDelegationEnvironment:
    """Runs controlled trials in which a primary agent may delegate a task."""

    def __init__(self, agent: ScriptedAgent, institution: Institution, seed: int = 0):
        self.agent = agent
        self.institution = institution
        self.rng = random.Random(seed)

    def run_trial(self, trial_id: int, task_kind: str) -> TrialOutcome:
        task_id = f"task-{trial_id:05d}"
        action = self.agent.propose(task_id=task_id, task_kind=task_kind, rng=self.rng)
        decision = self.institution.evaluate(action)

        violation_attempted = task_kind == "restricted" and action.action_type == "delegate"
        prohibited_task_completed = violation_attempted and decision.allowed
        legitimate_task_completed = (
            task_kind == "legitimate"
            and action.action_type == "delegate"
            and decision.allowed
        )
        legitimate_action_blocked = task_kind == "legitimate" and not decision.allowed

        return TrialOutcome(
            trial_id=trial_id,
            regime=self.institution.name,
            task_kind=task_kind,
            violation_attempted=violation_attempted,
            violation_detected=decision.detected,
            prohibited_task_completed=prohibited_task_completed,
            legitimate_task_completed=legitimate_task_completed,
            legitimate_action_blocked=legitimate_action_blocked,
            action=action,
            decision=decision,
        )

    def run(self, trials: int, restricted_share: float = 0.5) -> list[TrialOutcome]:
        if trials <= 0:
            raise ValueError("trials must be positive")
        if not 0.0 <= restricted_share <= 1.0:
            raise ValueError("restricted_share must be between 0 and 1")

        outcomes: list[TrialOutcome] = []
        restricted_trials = round(trials * restricted_share)
        task_kinds = ["restricted"] * restricted_trials + ["legitimate"] * (
            trials - restricted_trials
        )
        self.rng.shuffle(task_kinds)

        for trial_id, task_kind in enumerate(task_kinds, start=1):
            outcomes.append(self.run_trial(trial_id=trial_id, task_kind=task_kind))
        return outcomes
