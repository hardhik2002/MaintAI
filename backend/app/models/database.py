from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TelemetryRecord(Base):
    __tablename__ = "telemetry_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)
    machine_id: Mapped[str] = mapped_column(String(64), index=True)
    machine_type: Mapped[str] = mapped_column(String(1))
    air_temperature: Mapped[float] = mapped_column(Float)
    process_temperature: Mapped[float] = mapped_column(Float)
    rotational_speed: Mapped[float] = mapped_column(Float)
    torque: Mapped[float] = mapped_column(Float)
    tool_wear: Mapped[float] = mapped_column(Float)
    failure_probability: Mapped[float] = mapped_column(Float)
    failure_prediction: Mapped[bool] = mapped_column(Boolean)
    risk_level: Mapped[str] = mapped_column(String(16), index=True)
    explanation: Mapped[list[dict]] = mapped_column(JSON)
    warnings: Mapped[list[str]] = mapped_column(JSON)
    inference_ms: Mapped[float] = mapped_column(Float)


class AlertRecord(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)
    machine_id: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[str] = mapped_column(String(16), index=True)
    risk_score: Mapped[float] = mapped_column(Float)
    message: Mapped[str] = mapped_column(String(255))
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)

