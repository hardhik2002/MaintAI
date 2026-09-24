import joblib


def test_saved_artifact_runs_inference() -> None:
    artifact = joblib.load("ml/artifacts/model.joblib")
    result = artifact.predict(
        {
            "type": "M",
            "air_temperature": 300.0,
            "process_temperature": 310.0,
            "rotational_speed": 1500.0,
            "torque": 40.0,
            "tool_wear": 80.0,
        }
    )
    assert 0 <= result["failure_probability"] <= 1
    assert result["risk_level"] in {"HEALTHY", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
    assert len(result["top_contributing_features"]) == 4
