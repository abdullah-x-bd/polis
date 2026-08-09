#!/usr/bin/env python3
"""Analyse POLIS v1 live results and generate publication-ready tables and figures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from polis.v1.analysis import analyse_records, records_to_frames
from polis.v1.live import load_records
from polis.v1.protocol import load_protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", nargs="+", help="One or more POLIS v1 JSONL result files")
    parser.add_argument("--protocol", default="configs/v1_live.json")
    parser.add_argument("--output", default="results/analysis")
    args = parser.parse_args()

    protocol = load_protocol(args.protocol)
    records = []
    for path in args.results:
        records.extend(load_records(path))
    if not records:
        raise SystemExit("No POLIS v1 episode records were found")

    fingerprints = {record.protocol_fingerprint for record in records}
    if fingerprints != {protocol.fingerprint()}:
        raise SystemExit(
            "Result fingerprint does not match the supplied frozen protocol. "
            f"Observed={sorted(fingerprints)}, expected={protocol.fingerprint()}"
        )

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    analysis = analyse_records(records, protocol)
    (output / "analysis.json").write_text(
        json.dumps(analysis, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    summaries = pd.DataFrame(analysis["summaries"])
    contrasts = pd.DataFrame(analysis["contrasts"])
    summaries.to_csv(output / "summary_table.csv", index=False)
    contrasts.to_csv(output / "contrast_table.csv", index=False)

    commons, delegation = records_to_frames(records)
    if not commons.empty:
        commons.to_csv(output / "commons_episode_table.csv", index=False)
        _commons_figure(commons, output)
    if not delegation.empty:
        delegation.to_csv(output / "delegation_episode_table.csv", index=False)
        _delegation_figure(delegation, output)

    _write_markdown_summary(analysis, output / "RESULTS_SUMMARY.md")
    print(json.dumps(analysis["costs"], indent=2))
    print(f"Wrote analysis artifacts to {output}")


def _commons_figure(frame: pd.DataFrame, output: Path) -> None:
    order = ["no_institution", "prompt_only", "hard_quota", "congestion_pricing"]
    models = list(dict.fromkeys(frame["model"].tolist()))
    x = range(len(order))
    fig, ax = plt.subplots(figsize=(9, 5))
    width = 0.8 / max(1, len(models))
    for index, model in enumerate(models):
        means = [
            frame[(frame["model"] == model) & (frame["institution"] == institution)][
                "efficiency_ratio"
            ].mean()
            for institution in order
        ]
        positions = [value - 0.4 + width / 2 + index * width for value in x]
        ax.bar(positions, means, width=width, label=model)
    ax.set_xticks(list(x), [label.replace("_", "\n") for label in order])
    ax.set_ylabel("Mean final-round efficiency ratio")
    ax.set_xlabel("Institution")
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output / "figure_commons_efficiency.png", dpi=220)
    fig.savefig(output / "figure_commons_efficiency.pdf")
    plt.close(fig)


def _delegation_figure(frame: pd.DataFrame, output: Path) -> None:
    order = ["no_institution", "prompt_only", "local_guard", "provenance_guard"]
    models = list(dict.fromkeys(frame["model"].tolist()))
    x = range(len(order))
    fig, ax = plt.subplots(figsize=(9, 5))
    width = 0.8 / max(1, len(models))
    for index, model in enumerate(models):
        rates = [
            frame[(frame["model"] == model) & (frame["institution"] == institution)][
                "realized_violation"
            ].astype(float).mean()
            for institution in order
        ]
        positions = [value - 0.4 + width / 2 + index * width for value in x]
        ax.bar(positions, rates, width=width, label=model)
    ax.set_xticks(list(x), [label.replace("_", "\n") for label in order])
    ax.set_ylabel("Realized violation rate")
    ax.set_xlabel("Institution")
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output / "figure_delegation_violations.png", dpi=220)
    fig.savefig(output / "figure_delegation_violations.pdf")
    plt.close(fig)


def _write_markdown_summary(analysis: dict, path: Path) -> None:
    costs = analysis["costs"]
    lines = [
        "# POLIS v1 generated results summary",
        "",
        f"Protocol fingerprint `{analysis['protocol_fingerprint']}`",
        "",
        f"Total model calls: {costs['total_model_calls']}",
        f"Total tokens: {costs['total_tokens']}",
        f"Recorded OpenRouter cost: ${costs['total_cost_usd']:.6f}",
        "",
        "## Primary contrasts",
        "",
        "| Environment | Model | Treatment | Endpoint | Effect | 95% CI | Holm p |",
        "| --- | --- | --- | --- | ---: | --- | ---: |",
    ]
    for row in analysis["contrasts"]:
        if row["endpoint"] not in {"efficiency_ratio", "realized_violation"}:
            continue
        lines.append(
            "| {environment} | {model} | {treatment} | {endpoint} | {effect:.4f} | "
            "[{ci_low:.4f}, {ci_high:.4f}] | {p_adjusted:.4g} |".format(**row)
        )
    lines.extend(
        [
            "",
            "Effects are treatment minus the no-institution condition on matched scenarios.",
            "This file is generated by `scripts/analyse_v1.py`; do not hand-edit numerical results.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
