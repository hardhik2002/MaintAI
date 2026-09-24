from __future__ import annotations


def risk_level(probability: float, decision_threshold: float) -> str:
    """Map calibrated probability to stable, threshold-relative operational bands."""
    if probability >= min(1.0, decision_threshold * 1.5):
        return "CRITICAL"
    if probability >= decision_threshold:
        return "HIGH"
    if probability >= decision_threshold * 0.6:
        return "MEDIUM"
    if probability >= decision_threshold * 0.25:
        return "LOW"
    return "HEALTHY"

