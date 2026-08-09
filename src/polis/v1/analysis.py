"""Pre-specified paired statistical analysis for POLIS v1 live results."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Iterable

import numpy as np
import pandas as pd
from scipy.stats import binomtest, wilcoxon

from .live import LiveEpisodeRecord
from .protocol import LiveExperimentProtocol


COMMONS_COLUMNS = [
    "efficiency_ratio",
    "overclaim_ratio",
    "resource_waste",
    "total_charge",
]

DELEGATION_COLUMNS = [
    "realized_violation",
    "task_completed",
    "violation_attempted",
    "violation_detected",
    "legitimate_action_blocked",
    "policy_laundering_succeeded",
]


def records_to_frames(
    records: Iterable[LiveEpisodeRecord],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Convert atomic episode records into one-row-per-episode analysis frames."""

    commons_rows: list[dict[str, Any]] = []
    delegation_rows: list[dict[str, Any]] = []

    for record in records:
        base = {
            "run_id": record.run_id,
            "protocol_fingerprint": record.protocol_fingerprint,
            "model": record.model,
            "scenario_id": record.scenario_id,
            "institution": record.institution,
            "repetition": record.repetition,
            "episode_cost_usd": record.episode_cost_usd,
            "episode_tokens": record.episode_tokens,
            "model_calls": len(record.model_calls),
        }
        if record.environment == "resource_commons":
            rounds = record.result["rounds"]
            if not rounds:
                raise ValueError(f"Commons episode {record.scenario_id} contains no rounds")
            final = rounds[-1]
            commons_rows.append(
                {
                    **base,
                    "round": final["round_index"],
                    "efficiency_ratio": float(final["efficiency_ratio"]),
                    "overclaim_ratio": float(final["overclaim_ratio"]),
                    "resource_waste": float(final["resource_waste"]),
                    "total_charge": float(final["total_charge"]),
                    "system_welfare": float(final["system_welfare"]),
                }
            )
        elif record.environment == "delegation_boundaries":
            delegation_rows.append(
                {
                    **base,
                    "scenario_type": record.result["scenario_type"],
                    "domain": record.result["domain"],
                    "realized_violation": bool(record.result["realized_violation"]),
                    "task_completed": bool(record.result["task_completed"]),
                    "violation_attempted": bool(record.result["violation_attempted"]),
                    "violation_detected": bool(record.result["violation_detected"]),
                    "legitimate_action_blocked": bool(record.result["legitimate_action_blocked"]),
                    "policy_laundering_succeeded": bool(record.result["policy_laundering_succeeded"]),
                    "path_length": int(record.result["path_length"]),
                }
            )
        else:
            raise ValueError(f"Unknown environment {record.environment}")

    return pd.DataFrame(commons_rows), pd.DataFrame(delegation_rows)


def analyse_records(
    records: Iterable[LiveEpisodeRecord],
    protocol: LiveExperimentProtocol,
) -> dict[str, Any]:
    """Run the frozen descriptive and paired inferential analysis."""

    commons, delegation = records_to_frames(records)
    summaries = _summaries(commons, delegation)
    contrasts: list[dict[str, Any]] = []

    if not commons.empty:
        for endpoint in COMMONS_COLUMNS:
            contrasts.extend(
                _continuous_contrasts(
                    commons,
                    endpoint=endpoint,
                    bootstrap_samples=protocol.analysis.bootstrap_samples,
                    confidence_level=protocol.analysis.confidence_level,
                )
            )

    if not delegation.empty:
        for endpoint in DELEGATION_COLUMNS:
            contrasts.extend(
                _binary_contrasts(
                    delegation,
                    endpoint=endpoint,
                    bootstrap_samples=protocol.analysis.bootstrap_samples,
                    confidence_level=protocol.analysis.confidence_level,
                )
            )

    _apply_holm_by_endpoint(contrasts)
    costs = _cost_summary(commons, delegation)
    completeness = _completeness(records, protocol)

    return {
        "protocol_fingerprint": protocol.fingerprint(),
        "protocol_version": protocol.protocol_version,
        "analysis_method": {
            "continuous": "paired mean difference with percentile bootstrap CI and paired Wilcoxon signed-rank test",
            "binary": "paired risk difference with percentile bootstrap CI and exact discordant-pair binomial test",
            "multiple_comparisons": "Holm adjustment within environment and endpoint",
            "confidence_level": protocol.analysis.confidence_level,
            "bootstrap_samples": protocol.analysis.bootstrap_samples,
        },
        "completeness": completeness,
        "costs": costs,
        "summaries": summaries,
        "contrasts": contrasts,
    }


def _summaries(commons: pd.DataFrame, delegation: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not commons.empty:
        grouped = commons.groupby(["model", "institution"], dropna=False)
        for (model, institution), group in grouped:
            row: dict[str, Any] = {
                "environment": "resource_commons",
                "model": model,
                "institution": institution,
                "n": int(len(group)),
            }
            for endpoint in COMMONS_COLUMNS:
                row[f"mean_{endpoint}"] = float(group[endpoint].mean())
                row[f"sd_{endpoint}"] = float(group[endpoint].std(ddof=1)) if len(group) > 1 else 0.0
            rows.append(row)

    if not delegation.empty:
        grouped = delegation.groupby(["model", "institution"], dropna=False)
        for (model, institution), group in grouped:
            row = {
                "environment": "delegation_boundaries",
                "model": model,
                "institution": institution,
                "n": int(len(group)),
            }
            for endpoint in DELEGATION_COLUMNS:
                row[f"rate_{endpoint}"] = float(group[endpoint].astype(float).mean())
            row["mean_path_length"] = float(group["path_length"].mean())
            rows.append(row)
    return rows


def _continuous_contrasts(
    frame: pd.DataFrame,
    *,
    endpoint: str,
    bootstrap_samples: int,
    confidence_level: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for model, model_frame in frame.groupby("model"):
        for treatment in sorted(set(model_frame["institution"]) - {"no_institution"}):
            paired = _paired_values(model_frame, endpoint, treatment)
            if paired.empty:
                continue
            baseline = paired["baseline"].to_numpy(dtype=float)
            treated = paired["treatment"].to_numpy(dtype=float)
            diff = treated - baseline
            ci_low, ci_high = _paired_bootstrap_ci(
                diff,
                samples=bootstrap_samples,
                confidence_level=confidence_level,
                seed=_stable_seed(str(model), endpoint, treatment),
            )
            if np.allclose(diff, 0):
                p_value = 1.0
            else:
                p_value = float(wilcoxon(treated, baseline, alternative="two-sided").pvalue)
            rows.append(
                {
                    "environment": "resource_commons",
                    "model": model,
                    "endpoint": endpoint,
                    "baseline": "no_institution",
                    "treatment": treatment,
                    "n_pairs": int(len(diff)),
                    "baseline_mean": float(baseline.mean()),
                    "treatment_mean": float(treated.mean()),
                    "effect": float(diff.mean()),
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "p_value": p_value,
                    "p_adjusted": None,
                    "test": "paired_wilcoxon",
                }
            )
    return rows


def _binary_contrasts(
    frame: pd.DataFrame,
    *,
    endpoint: str,
    bootstrap_samples: int,
    confidence_level: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for model, model_frame in frame.groupby("model"):
        for treatment in sorted(set(model_frame["institution"]) - {"no_institution"}):
            paired = _paired_values(model_frame, endpoint, treatment)
            if paired.empty:
                continue
            baseline = paired["baseline"].astype(bool).to_numpy()
            treated = paired["treatment"].astype(bool).to_numpy()
            diff = treated.astype(float) - baseline.astype(float)
            ci_low, ci_high = _paired_bootstrap_ci(
                diff,
                samples=bootstrap_samples,
                confidence_level=confidence_level,
                seed=_stable_seed(str(model), endpoint, treatment),
            )
            baseline_only = int(np.sum(baseline & ~treated))
            treatment_only = int(np.sum(~baseline & treated))
            discordant = baseline_only + treatment_only
            p_value = (
                1.0
                if discordant == 0
                else float(
                    binomtest(
                        min(baseline_only, treatment_only),
                        n=discordant,
                        p=0.5,
                        alternative="two-sided",
                    ).pvalue
                )
            )
            rows.append(
                {
                    "environment": "delegation_boundaries",
                    "model": model,
                    "endpoint": endpoint,
                    "baseline": "no_institution",
                    "treatment": treatment,
                    "n_pairs": int(len(diff)),
                    "baseline_mean": float(baseline.mean()),
                    "treatment_mean": float(treated.mean()),
                    "effect": float(diff.mean()),
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "p_value": p_value,
                    "p_adjusted": None,
                    "test": "exact_discordant_pair",
                    "baseline_only_discordant": baseline_only,
                    "treatment_only_discordant": treatment_only,
                }
            )
    return rows


def _paired_values(frame: pd.DataFrame, endpoint: str, treatment: str) -> pd.DataFrame:
    keys = ["model", "scenario_id", "repetition"]
    subset = frame[frame["institution"].isin(["no_institution", treatment])]
    pivot = subset.pivot_table(
        index=keys,
        columns="institution",
        values=endpoint,
        aggfunc="first",
    )
    if "no_institution" not in pivot or treatment not in pivot:
        return pd.DataFrame(columns=["baseline", "treatment"])
    paired = pivot[["no_institution", treatment]].dropna().copy()
    return paired.rename(columns={"no_institution": "baseline", treatment: "treatment"})


def _paired_bootstrap_ci(
    differences: np.ndarray,
    *,
    samples: int,
    confidence_level: float,
    seed: int,
) -> tuple[float, float]:
    if differences.size == 0:
        return math.nan, math.nan
    if differences.size == 1:
        value = float(differences[0])
        return value, value
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, differences.size, size=(samples, differences.size))
    estimates = differences[indices].mean(axis=1)
    alpha = 1.0 - confidence_level
    low, high = np.quantile(estimates, [alpha / 2, 1 - alpha / 2])
    return float(low), float(high)


def _apply_holm_by_endpoint(contrasts: list[dict[str, Any]]) -> None:
    groups: defaultdict[tuple[str, str], list[int]] = defaultdict(list)
    for index, row in enumerate(contrasts):
        groups[(str(row["environment"]), str(row["endpoint"]))].append(index)

    for indices in groups.values():
        p_values = [float(contrasts[index]["p_value"]) for index in indices]
        adjusted = _holm_adjust(p_values)
        for index, value in zip(indices, adjusted, strict=True):
            contrasts[index]["p_adjusted"] = value


def _holm_adjust(p_values: list[float]) -> list[float]:
    if not p_values:
        return []
    order = sorted(range(len(p_values)), key=p_values.__getitem__)
    adjusted = [1.0] * len(p_values)
    running = 0.0
    m = len(p_values)
    for rank, original_index in enumerate(order):
        candidate = min(1.0, (m - rank) * p_values[original_index])
        running = max(running, candidate)
        adjusted[original_index] = running
    return adjusted


def _cost_summary(commons: pd.DataFrame, delegation: pd.DataFrame) -> dict[str, Any]:
    frames = [frame for frame in [commons, delegation] if not frame.empty]
    if not frames:
        return {
            "total_cost_usd": 0.0,
            "total_tokens": 0,
            "total_model_calls": 0,
            "by_model": [],
        }
    combined = pd.concat(frames, ignore_index=True)
    by_model = []
    for model, group in combined.groupby("model"):
        by_model.append(
            {
                "model": model,
                "cost_usd": float(group["episode_cost_usd"].sum()),
                "tokens": int(group["episode_tokens"].sum()),
                "model_calls": int(group["model_calls"].sum()),
            }
        )
    return {
        "total_cost_usd": float(combined["episode_cost_usd"].sum()),
        "total_tokens": int(combined["episode_tokens"].sum()),
        "total_model_calls": int(combined["model_calls"].sum()),
        "by_model": by_model,
    }


def _completeness(
    records: Iterable[LiveEpisodeRecord],
    protocol: LiveExperimentProtocol,
) -> dict[str, Any]:
    records = list(records)
    by_mode: defaultdict[str, int] = defaultdict(int)
    by_environment: defaultdict[str, int] = defaultdict(int)
    fingerprints = set()
    for record in records:
        by_mode[record.mode] += 1
        by_environment[record.environment] += 1
        fingerprints.add(record.protocol_fingerprint)
    return {
        "records": len(records),
        "modes": dict(by_mode),
        "environments": dict(by_environment),
        "single_protocol_fingerprint": fingerprints in [set(), {protocol.fingerprint()}],
        "observed_fingerprints": sorted(fingerprints),
    }


def _stable_seed(*parts: str) -> int:
    value = 0
    for part in parts:
        for char in part:
            value = (value * 131 + ord(char)) % (2**32)
    return value
