from __future__ import annotations

import logging
from datetime import UTC, datetime
from time import perf_counter

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from backend.app.models.database import AlertRecord, TelemetryRecord
from backend.app.schemas.prediction import TelemetryInput
from backend.app.services.model_service import get_model

logger = logging.getLogger(__name__)
ALERT_LEVELS = {"HIGH", "CRITICAL"}


def predict_and_store(payload: TelemetryInput, session: Session, request_id: str) -> TelemetryRecord:
    started = perf_counter()
    result = get_model().predict(payload.model_dump())
    elapsed_ms = (perf_counter() - started) * 1_000
    record = TelemetryRecord(
        timestamp=payload.timestamp or datetime.now(UTC),
        machine_id=payload.machine_id,
        machine_type=payload.type,
        air_temperature=payload.air_temperature,
        process_temperature=payload.process_temperature,
        rotational_speed=payload.rotational_speed,
        torque=payload.torque,
        tool_wear=payload.tool_wear,
        failure_probability=result["failure_probability"],
        failure_prediction=result["failure_prediction"],
        risk_level=result["risk_level"],
        explanation=result["top_contributing_features"],
        warnings=result["warnings"],
        inference_ms=elapsed_ms,
    )
    session.add(record)
    session.flush()
    _create_transition_alert(session, record)
    session.commit()
    session.refresh(record)
    logger.info(
        "inference_complete",
        extra={
            "request_id": request_id, "machine_id": record.machine_id,
            "model_version": result["model_version"], "duration_ms": round(elapsed_ms, 2),
            "risk_level": record.risk_level,
        },
    )
    return record


def _create_transition_alert(session: Session, record: TelemetryRecord) -> None:
    if record.risk_level not in ALERT_LEVELS:
        return
    previous = session.scalar(
        select(TelemetryRecord)
        .where(TelemetryRecord.machine_id == record.machine_id, TelemetryRecord.id != record.id)
        .order_by(desc(TelemetryRecord.timestamp)).limit(1)
    )
    if previous and previous.risk_level == record.risk_level:
        return
    session.add(
        AlertRecord(
            timestamp=record.timestamp, machine_id=record.machine_id,
            severity=record.risk_level, risk_score=record.failure_probability,
            message=f"{record.machine_id} entered {record.risk_level} risk state",
        )
    )


def monitoring_summary(session: Session) -> dict[str, object]:
    rows = session.execute(
        select(
            func.count(TelemetryRecord.id), func.avg(TelemetryRecord.inference_ms),
            func.sum(func.json_array_length(TelemetryRecord.warnings)),
        )
    ).one()
    counts = dict(session.execute(select(TelemetryRecord.risk_level, func.count()).group_by(TelemetryRecord.risk_level)).all())
    total = int(rows[0] or 0)
    high = counts.get("HIGH", 0) + counts.get("CRITICAL", 0)
    return {
        "inference_count": total,
        "average_latency_ms": float(rows[1] or 0),
        "out_of_range_count": int(rows[2] or 0),
        "high_risk_percentage": (100 * high / total) if total else 0,
        "prediction_distribution": counts,
    }
