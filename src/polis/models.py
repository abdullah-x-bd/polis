"""Typed records used across POLIS experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Action:
    """A structured action proposed by an agent."""

    actor: str
    action_type: str
    task_id: str
    task_kind: str
    target: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Decision:
    """An institution's enforceable decision about an action."""

    allowed: bool
    reason: str
    violation: str | None = None
    detected: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TrialOutcome:
    """The observable result of one unsafe-delegation trial."""

    trial_id: int
    regime: str
    task_kind: str
    violation_attempted: bool
    violation_detected: bool
    prohibited_task_completed: bool
    legitimate_task_completed: bool
    legitimate_action_blocked: bool
    action: Action
    decision: Decision

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["action"] = self.action.to_dict()
        data["decision"] = self.decision.to_dict()
        return data
