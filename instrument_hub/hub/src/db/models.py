from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, FLOAT
import uuid

Base = declarative_base()


# Define the Item model
class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String, nullable=True, index=True)
    description = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime, server_default=func.now(), index=True)
    registerd = Column(Integer, index=True)
    enabled = Column(Integer, index=True)
    online = Column(Integer, index=True)
    group = Column(String, nullable=True, index=True)
    last_logon = Column(DateTime, nullable=True, index=True)
    profile = Column(UUID(as_uuid=True), nullable=True, index=True)


class InstrumentData(Base):
    __tablename__ = "data"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    instrument_id = Column(UUID, index=True)
    data = Column(String, index=True)
    timestamp = Column(DateTime, server_default=func.now(), index=True)


class Calibrate(Base):
    __tablename__ = "calibration"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    instrument_id = Column(UUID, index=True)
    instrument_name = Column(String, index=True)
    value = Column(String, index=True)
    inspector = Column(String, index=True)
    timestamp = Column(DateTime, server_default=func.now(), index=True)


class InstrumentProfile(Base):
    __tablename__ = "instrument_profile"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    brand = Column(String, index=True)
    model = Column(String, index=True)
    category = Column(String, index=True)
    commands = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
