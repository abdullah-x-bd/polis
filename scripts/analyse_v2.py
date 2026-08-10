#!/usr/bin/env python3
"""Analyse one or more complete POLIS v2 source-data files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from polis.v2.analysis import analyse, records_to_frames, write_json
from polis.v2.live import load_records
from polis.v2.protocol import load_protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", nargs="+", help="V2 JSONL source files")
    parser.add_argument("--protocol", default="configs/v2_protocol.json")
    parser.add_argument("--output", default="results/v2/analysis")
    args = parser.parse_args()

    protocol = load_protocol(args.protocol)
    records = [record for path in args.results for record in load_records(path)]
    if not records:
        raise SystemExit("No POLIS v2 records found")
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    payload = analyse(records, protocol)
    write_json(output / "analysis.json", payload)
    frames = records_to_frames(records)
    for study, frame in frames.items():
        csv_frame = frame.copy()
        if "outcomes" in csv_frame:
            csv_frame["outcomes"] = csv_frame["outcomes"].map(json.dumps)
        csv_frame.to_csv(output / f"episodes_{study}.csv", index=False)

    _write_tables(payload, output)
    _make_figures(frames, output)
    _write_summary(payload, output / "RESULTS_SUMMARY.md")
    print(json.dumps(payload["costs"], indent=2))
    print(f"Wrote POLIS v2 analysis artifacts to {output}")


def _write_tables(payload: dict, output: Path) -> None:
    for study, study_payload in payload["studies"].items():
        for key, value in study_payload.items():
            if isinstance(value, list) and (not value or isinstance(value[0], dict)):
                pd.DataFrame(value).to_csv(output / f"table_{study}_{key}.csv", index=False)


def _make_figures(frames: dict[str, pd.DataFrame], output: Path) -> None:
    if "delegation_main" in frames:
        frame = frames["delegation_main"]
        for endpoint, ylabel, filename in [
            ("realized_violation", "Realized violation rate", "figure_delegation_pressure_violations"),
            ("compliant_completion", "Compliant task completion rate", "figure_delegation_pressure_completion"),
        ]:
            grouped = frame.groupby(["governance", "pressure_level"])[endpoint].mean().reset_index()
            fig, ax = plt.subplots(figsize=(9, 5.5))
            for governance, cell in grouped.groupby("governance"):
                cell = cell.sort_values("pressure_level")
                ax.plot(cell["pressure_level"], cell[endpoint], marker="o", label=governance)
            ax.set_xlabel("Goal-policy conflict pressure")
            ax.set_ylabel(ylabel)
            ax.set_xticks([0, 1, 2, 3])
            ax.set_ylim(-0.03, 1.03)
            ax.legend(fontsize=8)
            fig.tight_layout()
            fig.savefig(output / f"{filename}.png", dpi=240)
            fig.savefig(output / f"{filename}.pdf")
            plt.close(fig)

        frontier = frame.groupby("governance", as_index=False).agg(
            completion=("compliant_completion", "mean"),
            violation=("realized_violation", "mean"),
        )
        fig, ax = plt.subplots(figsize=(7.5, 5.5))
        ax.scatter(frontier["completion"], frontier["violation"], s=75)
        for _, row in frontier.iterrows():
            ax.annotate(row["governance"], (row["completion"], row["violation"]), fontsize=8, xytext=(4, 4), textcoords="offset points")
        ax.set_xlabel("Compliant task completion rate")
        ax.set_ylabel("Realized violation rate")
        ax.set_xlim(-0.03, 1.03)
        ax.set_ylim(-0.03, 1.03)
        fig.tight_layout()
        fig.savefig(output / "figure_safety_performance_frontier.png", dpi=240)
        fig.savefig(output / "figure_safety_performance_frontier.pdf")
        plt.close(fig)

    if "commons_salience" in frames:
        frame = frames["commons_salience"]
        grouped = frame.groupby(["governance", "objective"])["cap_seeking_rate"].mean().unstack("objective")
        ax = grouped.plot(kind="bar", figsize=(9, 5.5))
        ax.set_ylabel("Mean cap-seeking rate")
        ax.set_xlabel("Institutional representation")
        ax.set_ylim(0, 1)
        plt.tight_layout()
        plt.savefig(output / "figure_commons_quota_salience.png", dpi=240)
        plt.savefig(output / "figure_commons_quota_salience.pdf")
        plt.close()

    if "heterogeneous" in frames:
        frame = frames["heterogeneous"]
        pivot = frame.pivot_table(index="model_composition", columns="governance", values="realized_violation", aggfunc="mean")
        fig, ax = plt.subplots(figsize=(9, 6))
        image = ax.imshow(pivot.to_numpy(), aspect="auto", vmin=0, vmax=1)
        ax.set_xticks(range(len(pivot.columns)), pivot.columns, rotation=35, ha="right")
        ax.set_yticks(range(len(pivot.index)), pivot.index)
        ax.set_title("Violation rate by heterogeneous team composition")
        fig.colorbar(image, ax=ax, label="Realized violation rate")
        fig.tight_layout()
        fig.savefig(output / "figure_heterogeneous_heatmap.png", dpi=240)
        fig.savefig(output / "figure_heterogeneous_heatmap.pdf")
        plt.close(fig)


def _write_summary(payload: dict, path: Path) -> None:
    lines = [
        "# POLIS v2 Generated Results Summary",
        "",
        f"Study fingerprint `{payload['study_fingerprint']}`",
        "",
        f"Total episodes: {payload['records']}",
        f"Total model calls: {payload['costs']['total_model_calls']}",
        f"Total tokens: {payload['costs']['total_tokens']}",
        f"Provider-reported cost: ${payload['costs']['total_cost_usd']:.6f}",
        "",
    ]
    main = payload["studies"].get("delegation_main")
    if main:
        lines.extend(["## Delegation main study", ""])
        pooled = defaultdict_summary(main["summary_by_model_governance_pressure"])
        lines.extend([
            "| Governance | Violation | Compliant completion | Safe recovery | Mean utility |",
            "| --- | ---: | ---: | ---: | ---: |",
        ])
        for governance, row in pooled.items():
            lines.append(
                f"| {governance} | {row['violation_rate']:.3f} | {row['compliant_completion_rate']:.3f} | {row['safe_recovery_rate']:.3f} | {row['mean_utility']:.3f} |"
            )
        lines.append("")
    commons = payload["studies"].get("commons_salience")
    if commons:
        lines.extend(["## Commons quota-salience study", ""])
        lines.append("See generated CSV tables and `analysis.json` for objective-by-model treatment effects and the cap-seeking model.")
        lines.append("")
    if "wording_robustness" in payload["studies"]:
        lines.extend(["## Wording robustness", "", "Surface-form consistency is reported by model and governance regime in the generated table.", ""])
    if "heterogeneous" in payload["studies"]:
        lines.extend(["## Heterogeneous teams", "", "Cross-composition violation variance is reported by governance regime in the generated table.", ""])
    if "frontier" in payload["studies"]:
        lines.extend(["## Frontier diagnostic", "", "High-conflict frontier-model confirmation is reported separately from the cheap-model confirmatory backbone.", ""])
    lines.extend([
        "All numerical values in this file are generated from source JSONL by `scripts/analyse_v2.py`. Do not hand-edit result values.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def defaultdict_summary(rows: list[dict]) -> dict[str, dict[str, float]]:
    buckets: dict[str, list[dict]] = {}
    for row in rows:
        buckets.setdefault(row["governance"], []).append(row)
    result = {}
    for governance, values in buckets.items():
        result[governance] = {
            key: sum(float(item[key]) * int(item["n"]) for item in values) / sum(int(item["n"]) for item in values)
            for key in ["violation_rate", "compliant_completion_rate", "safe_recovery_rate", "mean_utility"]
        }
    return result


if __name__ == "__main__":
    main()
