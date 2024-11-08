from fastapi import Depends, HTTPException, APIRouter
from typing import List
from src.db.db_init import get_db
from sqlalchemy.orm import Session
from src.db import models
from src.pydantic_models import (
    InstrumentDataLog,
)
from datetime import datetime


router = APIRouter(
    prefix="/data_logs",
    tags=["Data-Logging"],
)


@router.get("/instrument/data_log", response_model=List[InstrumentDataLog])
async def data_log(
    name: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    "Route for getting a log of data trafic"
    instrument = db.query(models.Instrument).filter_by(name=name).first()
    if not instrument:
        raise HTTPException(
            status_code=404, detail=f"No instrument with name '{name}' found."
        )

    return (
        db.query(models.InstrumentData)
        .filter_by(instrument_id=instrument.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.delete("/instrument/data_logs")
async def delete_data_logs(older_than_year: str, db: Session = Depends(get_db)):
    "Route for cleaning database"
    try:
        # Parse the year input
        year = int(older_than_year)
        cutoff_date = datetime(year, 1, 1)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid year format. Please provide a valid year."
        )

    logs_to_delete = db.query(models.InstrumentData).filter(
        models.InstrumentData.timestamp < cutoff_date
    )
    count = logs_to_delete.count()

    # Perform the deletion
    logs_to_delete.delete(synchronize_session=False)
    db.commit()

    return {"message": f"Deleted {count} data logs older than {older_than_year}"}
