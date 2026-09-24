from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

RAW_FEATURES = [
    "type",
    "air_temperature",
    "process_temperature",
    "rotational_speed",
    "torque",
    "tool_wear",
]

ENGINEERED_FEATURES = [
    "temperature_difference",
    "mechanical_power_kw",
    "wear_torque_interaction",
    "torque_speed_ratio",
]


def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Create deterministic, physically motivated features used by train and serve."""
    missing = set(RAW_FEATURES) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing model features: {sorted(missing)}")
    result = frame[RAW_FEATURES].copy()
    result["temperature_difference"] = result["process_temperature"] - result["air_temperature"]
    # Angular velocity (rad/s) times torque (N.m), converted to kW.
    result["mechanical_power_kw"] = (
        2 * np.pi * result["rotational_speed"] * result["torque"] / 60_000
    )
    result["wear_torque_interaction"] = result["tool_wear"] * result["torque"]
    result["torque_speed_ratio"] = result["torque"] / result["rotational_speed"].clip(lower=1)
    return result


class PhysicalFeatureEngineer(BaseEstimator, TransformerMixin):
    """Sklearn-compatible wrapper that keeps feature logic in the saved pipeline."""

    def fit(self, X: pd.DataFrame, y: object = None) -> PhysicalFeatureEngineer:
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return build_features(pd.DataFrame(X))

    def get_feature_names_out(self, input_features: object = None) -> np.ndarray:
        return np.asarray(RAW_FEATURES + ENGINEERED_FEATURES, dtype=object)
