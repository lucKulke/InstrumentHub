# instrument_hub.py
from fastapi import Depends, HTTPException, Query, APIRouter
from typing import List
from src.db.db_init import get_db
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from src.db import models
from src import utils
from src.pydantic_models import (
    CalibrationData,
)
from datetime import datetime


router = APIRouter(
    prefix="/calibration",
    tags=["Instrument-Calibration"],
)


@router.post("/instrument/calibrate", response_model=CalibrationData)
async def calibrate(
    instrument_name: str,
    inspector_name: str,
    value: float,
    db: Session = Depends(get_db),
):
    instrument = db.query(models.Instrument).filter_by(name=instrument_name).first()
    if not instrument:
        raise HTTPException(
            status_code=404,
            detail=f"Instrument with name '{instrument_name}' not found.",
        )
    new_calibration = models.Calibrate(
        instrument_name=instrument_name,
        instrument_id=instrument.id,
        inspector=inspector_name,
        value=value,
    )
    db.add(new_calibration)
    db.commit()
    return new_calibration


@router.get("/instrument/calibration_data", response_model=List[CalibrationData])
async def calibration_data(
    instrument_name: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    instrument = db.query(models.Instrument).filter_by(name=instrument_name).first()
    if not instrument:
        raise HTTPException(
            status_code=404,
            detail=f"Instrument with name '{instrument_name}' not found.",
        )
    return (
        db.query(models.Calibrate)
        .filter_by(instrument_name=instrument_name)
        .offset(skip)
        .limit(limit)
        .all()
    )


def parse_timestamp(timestamp_str: str):
    try:
        return datetime.fromisoformat(timestamp_str)
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid timestamp format: {timestamp_str}"
        )


@router.get("/instrument/calibration_data_report")
async def calibration_data_report(
    instrument_name: str,
    start_timestamp: str = Query(None, description="Start timestamp (ISO 8601 format)"),
    end_timestamp: str = Query(None, description="End timestamp (ISO 8601 format)"),
    db: Session = Depends(get_db),
):
    instrument = db.query(models.Instrument).filter_by(name=instrument_name).first()
    if not instrument:
        raise HTTPException(
            status_code=404,
            detail=f"Instrument with name '{instrument_name}' not found.",
        )

    filters = [models.Calibrate.instrument_name == instrument_name]

    if start_timestamp:
        start_time = parse_timestamp(start_timestamp)
        filters.append(models.Calibrate.timestamp >= start_time)

    if end_timestamp:
        end_time = parse_timestamp(end_timestamp)
        filters.append(models.Calibrate.timestamp <= end_time)

    # Fetch data from the database using SQLAlchemy with filters
    data = db.query(models.Calibrate).filter(and_(*filters)).all()

    return utils.create_pdf(
        data=data,
        name=instrument_name,
        timestamp_start=start_timestamp,
        timestamp_end=end_timestamp,
    )


@router.get("/instrument/last_calibration")
async def get_last_calibration(instrument_name: str, db: Session = Depends(get_db)):
    # Fetch the latest calibration log for the specified instrument
    last_calibration = (
        db.query(models.Calibrate)
        .filter(models.Calibrate.instrument_name == instrument_name)
        .order_by(desc(models.Calibrate.timestamp))
        .first()
    )

    if not last_calibration:
        raise HTTPException(
            status_code=404, detail="No calibration records found for this instrument"
        )

    # Return the last calibration timestamp
    return {
        "instrument_name": instrument_name,
        "last_calibration": last_calibration.timestamp,
    }
