from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from maintai_ml.features import RAW_FEATURES
from maintai_ml.risk import risk_level


@dataclass
class ModelArtifact:
    pipeline: Any
    metadata: dict[str, Any]
    reference_values: dict[str, Any]
    training_ranges: dict[str, dict[str, float]]

    def predict(self, payload: dict[str, Any]) -> dict[str, Any]:
        frame = pd.DataFrame([{name: payload[name] for name in RAW_FEATURES}])
        probability = float(self.pipeline.predict_proba(frame)[0, 1])
        threshold = float(self.metadata["decision_threshold"])
        warnings = self._range_warnings(payload)
        return {
            "failure_probability": probability,
            "failure_prediction": probability >= threshold,
            "risk_level": risk_level(probability, threshold),
            "top_contributing_features": self._local_contributions(frame, probability),
            "warnings": warnings,
            "model_version": self.metadata["model_version"],
        }

    def _range_warnings(self, payload: dict[str, Any]) -> list[str]:
        warnings = []
        for feature, bounds in self.training_ranges.items():
            value = float(payload[feature])
            if value < bounds["min"] or value > bounds["max"]:
                warnings.append(
                    f"{feature}={value:g} is outside the training range "
                    f"[{bounds['min']:g}, {bounds['max']:g}]."
                )
        return warnings

    def _local_contributions(
        self, frame: pd.DataFrame, probability: float, limit: int = 4
    ) -> list[dict[str, Any]]:
        """Model-agnostic local perturbations; directional influence, not causality."""
        contributions = []
        for feature in RAW_FEATURES:
            reference = frame.copy()
            reference.loc[0, feature] = self.reference_values[feature]
            reference_probability = float(self.pipeline.predict_proba(reference)[0, 1])
            delta = probability - reference_probability
            contributions.append(
                {
                    "feature": feature,
                    "value": frame.loc[0, feature],
                    "contribution": delta,
                    "direction": "increases" if delta >= 0 else "decreases",
                }
            )
        return sorted(contributions, key=lambda item: abs(item["contribution"]), reverse=True)[:limit]
