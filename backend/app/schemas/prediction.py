from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

RiskLevel = Literal["HEALTHY", "LOW", "MEDIUM", "HIGH", "CRITICAL"]


class TelemetryInput(BaseModel):
    machine_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{2,63}$")
    type: Literal["L", "M", "H"]
    air_temperature: float = Field(ge=200, le=500)
    process_temperature: float = Field(ge=200, le=600)
    rotational_speed: float = Field(gt=0, le=20_000)
    torque: float = Field(ge=0, le=1_000)
    tool_wear: float = Field(ge=0, le=100_000)
    timestamp: datetime | None = None

    @field_validator("machine_id")
    @classmethod
    def normalize_id(cls, value: str) -> str:
        return value.upper()


class FeatureContribution(BaseModel):
    feature: str
    value: str | float
    contribution: float
    direction: Literal["increases", "decreases"]


class PredictionResponse(BaseModel):
    record_id: int
    timestamp: datetime
    machine_id: str
    type: str
    air_temperature: float
    process_temperature: float
    rotational_speed: float
    torque: float
    tool_wear: float
    failure_probability: float
    risk_level: RiskLevel
    failure_prediction: bool
    predicted_failure_modes: list[str] = []
    top_contributing_features: list[FeatureContribution]
    warnings: list[str]
    model_version: str
    inference_ms: float


class MachineSummary(BaseModel):
    machine_id: str
    type: str
    timestamp: datetime
    risk_level: RiskLevel
    failure_probability: float
    air_temperature: float
    process_temperature: float
    rotational_speed: float
    torque: float
    tool_wear: float


class AlertResponse(BaseModel):
    id: int
    timestamp: datetime
    machine_id: str
    severity: str
    risk_score: float
    message: str
    acknowledged: bool


class MonitoringResponse(BaseModel):
    inference_count: int
    average_latency_ms: float
    out_of_range_count: int
    high_risk_percentage: float
    prediction_distribution: dict[str, int]
