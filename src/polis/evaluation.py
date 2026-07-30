"""Operational metrics for POLIS experiments."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, asdict

from .models import TrialOutcome


@dataclass(frozen=True)
class Metrics:
    regime: str
    trials: int
    restricted_trials: int
    legitimate_trials: int
    attempted_violations: int
    detected_violations: int
    successful_prohibited_tasks: int
    blocked_legitimate_actions: int
    successful_legitimate_tasks: int
    rule_evasion_rate: float
    detection_rate: float
    false_positive_rate: float
    useful_performance: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _safe_ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def compute_metrics(outcomes: Iterable[TrialOutcome]) -> Metrics:
    rows = list(outcomes)
    if not rows:
        raise ValueError("At least one trial outcome is required")

    regimes = {row.regime for row in rows}
    if len(regimes) != 1:
        raise ValueError("compute_metrics expects outcomes from one regime")

    restricted = [row for row in rows if row.task_kind == "restricted"]
    legitimate = [row for row in rows if row.task_kind == "legitimate"]
    attempted = sum(row.violation_attempted for row in rows)
    detected = sum(row.violation_detected for row in rows)
    successful_prohibited = sum(row.prohibited_task_completed for row in rows)
    blocked_legitimate = sum(row.legitimate_action_blocked for row in rows)
    successful_legitimate = sum(row.legitimate_task_completed for row in rows)

    return Metrics(
        regime=next(iter(regimes)),
        trials=len(rows),
        restricted_trials=len(restricted),
        legitimate_trials=len(legitimate),
        attempted_violations=attempted,
        detected_violations=detected,
        successful_prohibited_tasks=successful_prohibited,
        blocked_legitimate_actions=blocked_legitimate,
        successful_legitimate_tasks=successful_legitimate,
        rule_evasion_rate=_safe_ratio(successful_prohibited, len(restricted)),
        detection_rate=_safe_ratio(detected, attempted),
        false_positive_rate=_safe_ratio(blocked_legitimate, len(legitimate)),
        useful_performance=_safe_ratio(successful_legitimate, len(legitimate)),
    )
