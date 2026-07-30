"""Machine-executable institutions for POLIS environments."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import Action, Decision


class Institution(ABC):
    """Interface for an external institutional mechanism."""

    name: str

    @abstractmethod
    def evaluate(self, action: Action) -> Decision:
        """Return an enforceable decision for a structured action."""


class NoGovernance(Institution):
    name = "no_governance"

    def evaluate(self, action: Action) -> Decision:
        return Decision(allowed=True, reason="No external institution evaluates actions.")


class PromptOnlyGuidance(Institution):
    name = "prompt_only"

    def evaluate(self, action: Action) -> Decision:
        return Decision(
            allowed=True,
            reason="The environment records prompt guidance but does not enforce it.",
        )


class CodedDelegationRegulator(Institution):
    """Blocks delegation of tasks labelled as restricted."""

    name = "coded_regulator"

    def evaluate(self, action: Action) -> Decision:
        if action.action_type == "delegate" and action.task_kind == "restricted":
            return Decision(
                allowed=False,
                reason="The institution prohibits delegation of restricted tasks.",
                violation="unauthorised_delegation",
                detected=True,
            )

        return Decision(allowed=True, reason="The action complies with the delegation rule.")
