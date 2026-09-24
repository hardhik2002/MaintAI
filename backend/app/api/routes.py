from __future__ import annotations

from collections.abc import Sequence
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from backend.app.core.database import get_session
from backend.app.models.database import AlertRecord, TelemetryRecord
from backend.app.schemas.prediction import (
    AlertResponse,
    MachineSummary,
    MonitoringResponse,
    PredictionResponse,
    TelemetryInput,
)
from backend.app.services.model_service import get_model
from backend.app.services.prediction_service import monitoring_summary, predict_and_store

router = APIRouter()


def prediction_response(record: TelemetryRecord) -> PredictionResponse:
    return PredictionResponse(
        record_id=record.id,
        timestamp=record.timestamp,
        machine_id=record.machine_id,
        type=record.machine_type,
        air_temperature=record.air_temperature,
        process_temperature=record.process_temperature,
        rotational_speed=record.rotational_speed,
        torque=record.torque,
        tool_wear=record.tool_wear,
        failure_probability=record.failure_probability,
        risk_level=record.risk_level,
        failure_prediction=record.failure_prediction,
        predicted_failure_modes=[],
        top_contributing_features=record.explanation,
        warnings=record.warnings,
        model_version=get_model().metadata["model_version"],
        inference_ms=record.inference_ms,
    )


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready(session: Session = Depends(get_session)) -> dict[str, str]:
    try:
        get_model()
        session.execute(select(1))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"status": "ready"}


@router.post("/api/v1/predict", response_model=PredictionResponse, status_code=201)
def predict(
    payload: TelemetryInput, request: Request, session: Session = Depends(get_session)
) -> PredictionResponse:
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    return prediction_response(predict_and_store(payload, session, request_id))


@router.get("/api/v1/machines", response_model=list[MachineSummary])
def machines(session: Session = Depends(get_session)) -> list[MachineSummary]:
    latest_ids = select(func.max(TelemetryRecord.id)).group_by(TelemetryRecord.machine_id)
    records = session.scalars(
        select(TelemetryRecord)
        .where(TelemetryRecord.id.in_(latest_ids))
        .order_by(desc(TelemetryRecord.failure_probability))
    ).all()
    return [
        MachineSummary(
            machine_id=row.machine_id,
            type=row.machine_type,
            timestamp=row.timestamp,
            risk_level=row.risk_level,
            failure_probability=row.failure_probability,
            air_temperature=row.air_temperature,
            process_temperature=row.process_temperature,
            rotational_speed=row.rotational_speed,
            torque=row.torque,
            tool_wear=row.tool_wear,
        )
        for row in records
    ]


@router.get("/api/v1/machines/{machine_id}", response_model=PredictionResponse)
def machine(machine_id: str, session: Session = Depends(get_session)) -> PredictionResponse:
    record = session.scalar(
        select(TelemetryRecord)
        .where(TelemetryRecord.machine_id == machine_id.upper())
        .order_by(desc(TelemetryRecord.timestamp))
        .limit(1)
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    return prediction_response(record)


@router.get("/api/v1/machines/{machine_id}/history", response_model=list[PredictionResponse])
def history(
    machine_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
) -> list[PredictionResponse]:
    records: Sequence[TelemetryRecord] = session.scalars(
        select(TelemetryRecord)
        .where(TelemetryRecord.machine_id == machine_id.upper())
        .order_by(desc(TelemetryRecord.timestamp))
        .limit(limit)
    ).all()
    return [prediction_response(row) for row in reversed(records)]


@router.get("/api/v1/alerts", response_model=list[AlertResponse])
def alerts(
    limit: int = Query(default=50, ge=1, le=200), session: Session = Depends(get_session)
) -> list[AlertRecord]:
    return list(
        session.scalars(
            select(AlertRecord).order_by(desc(AlertRecord.timestamp)).limit(limit)
        ).all()
    )


@router.get("/api/v1/model/info")
def model_info() -> dict[str, object]:
    return get_model().metadata


@router.get("/api/v1/model/metrics")
def model_metrics() -> dict[str, object]:
    metadata = get_model().metadata
    return {
        "model_version": metadata["model_version"],
        "algorithm": metadata["algorithm"],
        "decision_threshold": metadata["decision_threshold"],
        "test_metrics": metadata["test_metrics"],
        "model_comparison": metadata["model_comparison"],
        "feature_importance": metadata["feature_importance"],
        "calibration_curve": metadata["calibration_curve"],
    }


@router.get("/api/v1/monitoring", response_model=MonitoringResponse)
def monitoring(session: Session = Depends(get_session)) -> dict[str, object]:
    return monitoring_summary(session)
