"""Hard USD budget guard for POLIS live-model experiments."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class BudgetExceeded(RuntimeError):
    """Raised before a paid request would exceed the configured experiment budget."""


@dataclass
class BudgetTracker:
    max_cost_usd: float = 4.0
    ledger_path: Path = Path("results/costs/openrouter_ledger.jsonl")
    reserve_per_request_usd: float = 0.05
    spent_usd: float = field(init=False, default=0.0)

    def __post_init__(self) -> None:
        if self.max_cost_usd <= 0:
            raise ValueError("max_cost_usd must be positive")
        self.ledger_path = Path(self.ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self.spent_usd = self._load_spend()

    @property
    def remaining_usd(self) -> float:
        return max(0.0, self.max_cost_usd - self.spent_usd)

    def assert_request_allowed(self) -> None:
        if self.spent_usd + self.reserve_per_request_usd > self.max_cost_usd:
            raise BudgetExceeded(
                f"POLIS budget guard stopped the run: spent ${self.spent_usd:.6f}, "
                f"remaining ${self.remaining_usd:.6f}, reserve per request "
                f"${self.reserve_per_request_usd:.6f}."
            )

    def record(self, *, cost_usd: float, metadata: dict[str, Any]) -> None:
        if cost_usd < 0:
            raise ValueError("cost_usd cannot be negative")
        new_total = self.spent_usd + cost_usd
        if new_total > self.max_cost_usd + 1e-9:
            raise BudgetExceeded(
                f"Provider response would exceed budget: ${new_total:.6f} > ${self.max_cost_usd:.6f}"
            )
        record = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "cost_usd": cost_usd,
            "cumulative_cost_usd": new_total,
            **metadata,
        }
        with self.ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        self.spent_usd = new_total

    def _load_spend(self) -> float:
        if not self.ledger_path.exists():
            return 0.0
        total = 0.0
        with self.ledger_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                total = max(total, float(row.get("cumulative_cost_usd", 0.0)))
        return total
