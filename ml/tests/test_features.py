import pandas as pd
import pytest
from maintai_ml.features import build_features


def test_physical_feature_engineering_is_deterministic() -> None:
    raw = pd.DataFrame(
        [
            {
                "type": "M",
                "air_temperature": 300.0,
                "process_temperature": 310.0,
                "rotational_speed": 1500.0,
                "torque": 40.0,
                "tool_wear": 100.0,
            }
        ]
    )
    features = build_features(raw)
    assert features.loc[0, "temperature_difference"] == pytest.approx(10.0)
    assert features.loc[0, "mechanical_power_kw"] == pytest.approx(6.283185, rel=1e-5)
    assert features.loc[0, "wear_torque_interaction"] == 4000.0


def test_feature_engineering_rejects_missing_fields() -> None:
    with pytest.raises(ValueError, match="Missing model features"):
        build_features(pd.DataFrame([{"type": "M"}]))
