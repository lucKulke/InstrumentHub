from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class InstrumentData(BaseModel):
    id: UUID
    data: str


class InstrumentCreate(BaseModel):
    id: UUID
    name: Optional[str] = f"New Instrument {datetime.now()}"
    description: Optional[str] = None
    registerd: Optional[int] = 0
    enabled: Optional[int] = 0
    online: Optional[int] = 0
    group: Optional[str] = None
    last_logon: Optional[datetime] = datetime.now()
    profile: Optional[UUID] = None


class InstrumentRegister(BaseModel):
    id: UUID
    name: str
    description: str
    group: str
    profile: UUID


class InstrumentRead(BaseModel):
    id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    registerd: int
    enabled: int
    online: int
    group: Optional[str] = None
    last_logon: datetime
    profile: Optional[UUID] = None

    class Config:
        from_attributes = True


class InstrumentDataLog(BaseModel):
    data: str
    timestamp: datetime

    class Config:
        form_attributes = True


class CalibrationData(BaseModel):
    instrument_name: str
    inspector: str
    timestamp: datetime
    value: float

    class Config:
        form_attributes = True

class LastCalibration(BaseModel):
    instrument_name: str
    inspector: str
    timestamp: datetime


class InstrumentProfileRead(BaseModel):
    id: UUID
    brand: str
    model: str
    category: str
    commands: Optional[str] = None
    created_at: datetime

    class Config:
        form_attributes = True


class InstrumentProfileCreate(BaseModel):
    brand: str
    model: str
    category: str
    commands: Optional[dict] = None
