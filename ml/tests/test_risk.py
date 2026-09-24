from maintai_ml.risk import risk_level


def test_risk_bands_are_threshold_relative() -> None:
    assert risk_level(0.01, 0.2) == "HEALTHY"
    assert risk_level(0.08, 0.2) == "LOW"
    assert risk_level(0.15, 0.2) == "MEDIUM"
    assert risk_level(0.22, 0.2) == "HIGH"
    assert risk_level(0.35, 0.2) == "CRITICAL"
