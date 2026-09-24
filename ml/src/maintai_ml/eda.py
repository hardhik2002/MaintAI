from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

from maintai_ml.data import FAILURE_MODE_COLUMNS, load_dataset, validate_dataset
from maintai_ml.features import RAW_FEATURES


def run(data_path: Path, report_dir: Path) -> None:
    frame = load_dataset(data_path)
    report_dir.mkdir(parents=True, exist_ok=True)
    figures = report_dir / "figures"
    figures.mkdir(exist_ok=True)
    quality = validate_dataset(frame)
    (report_dir / "data_quality.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")
    frame.describe(include="all").transpose().to_csv(report_dir / "feature_summary.csv")

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    for column, axis in zip([f for f in RAW_FEATURES if f != "type"], axes.flat, strict=False):
        sns.histplot(frame, x=column, hue="machine_failure", stat="density", common_norm=False, ax=axis)
        axis.set_title(f"{column.replace('_', ' ').title()} by outcome")
    axes.flat[-1].axis("off")
    fig.tight_layout()
    fig.savefig(figures / "feature_distributions.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 6))
    numeric = [f for f in RAW_FEATURES if f != "type"] + ["machine_failure"] + FAILURE_MODE_COLUMNS
    sns.heatmap(frame[numeric].corr(), cmap="vlag", center=0, ax=ax)
    ax.set_title("Numeric correlations (subtype flags are labels, not features)")
    fig.tight_layout()
    fig.savefig(figures / "correlations.png", dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("ml/data/raw/ai4i2020.csv"))
    parser.add_argument("--reports", type=Path, default=Path("ml/reports"))
    args = parser.parse_args()
    run(args.data, args.reports)


if __name__ == "__main__":
    main()

