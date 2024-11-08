from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Depends,
    HTTPException,
    Request,
    Response,
)
from typing import List, Optional
from src.db import models
from src.db.db_init import get_db
from sqlalchemy.orm import Session
from src.pydantic_models import (
    InstrumentRead,
    InstrumentCreate,
    InstrumentRegister,
    InstrumentProfileRead,
    InstrumentProfileCreate,
)
from uuid import UUID
from src.utils import convert_dict_to_commands_string


DEFAULT_INSTRUMENT_PORT = 8080


# Create a router instance
router = APIRouter(
    prefix="/instruments",
    tags=["Instrument-Management"],
)

# Define your routes here


@router.get("/", response_model=List[InstrumentRead])
async def all_instruments(
    group: str = "", skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    "Route that returns a list of all instruments"

    if len(group) > 0:
        return (
            db.query(models.Instrument)
            .filter_by(group=group)
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        return db.query(models.Instrument).offset(skip).limit(limit).all()


@router.post("/create", response_model=InstrumentRead)
async def create_instrument(
    instrument: InstrumentCreate, db: Session = Depends(get_db)
):
    "Route for creating new instruments"
    print(f"creating instrument: ({instrument})")
    allready_existing_instrument = (
        db.query(models.Instrument).filter_by(id=instrument.id).first()
    )
    if allready_existing_instrument:
        raise HTTPException(
            status_code=400,
            detail=f"Instrument with id '{instrument.id}' allready registerd and is named: '{allready_existing_instrument.name}'!",
        )

    new_instrument = models.Instrument(
        id=instrument.id,
        name=instrument.name,
        description=instrument.description,
        registerd=instrument.registerd,
        enabled=instrument.enabled,
        online=instrument.online,
        group=instrument.group,
        last_logon=instrument.last_logon,
        profile=instrument.profile,
    )
    db.add(new_instrument)
    db.commit()
    db.refresh(new_instrument)
    return new_instrument


@router.post("/registration", response_model=InstrumentRead)
async def register_instrument(
    instrument: InstrumentRegister, db: Session = Depends(get_db)
):
    "Registers and enables instrument"
    instrument_in_db = db.query(models.Instrument).filter_by(id=instrument.id).first()
    if not instrument_in_db:
        raise HTTPException(
            status_code=404,
            detail=f"No instrument with instrument id: '{instrument.id}' found.",
        )
    print(f"register instrument: ({instrument})")
    instrument_in_db.name = instrument.name
    instrument_in_db.description = instrument.description
    instrument_in_db.registerd = 1
    instrument_in_db.enabled = 1
    instrument_in_db.group = instrument.group
    instrument_in_db.profile = instrument.profile
    db.add(instrument_in_db)
    db.commit()
    return instrument_in_db


@router.delete("/delete")
async def delete_instrument(id: UUID, db: Session = Depends(get_db)):
    "Route for deleting instrument profiles"
    instrument = db.query(models.Instrument).filter_by(id=id).first()
    if not instrument:
        raise HTTPException(
            status_code=404, detail=f"No instrument found with id '{id}'"
        )

    instrument_name = instrument.name
    db.delete(instrument)
    db.commit()
    return (
        f"Successfully deleted instrument with name '{instrument_name}' and id '{id}'"
    )


@router.get("/profile", response_model=List[InstrumentProfileRead])
async def get_instrument_profile(
    instrument_id: Optional[UUID] = None,
    profile_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
):
    "Route for getting instrument profiles"
    if instrument_id == None and profile_id == None:
        profiles = db.query(models.InstrumentProfile).all()
        return profiles

    profile = None

    if instrument_id:
        instrument = db.query(models.Instrument).filter_by(id=instrument_id).first()
        if not instrument:
            raise HTTPException(
                status_code=404, detail=f"No instrument found with id '{id}'"
            )
        profile = (
            db.query(models.InstrumentProfile).filter_by(id=instrument.profile).first()
        )
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Instrument with name {instrument.name} has no valid profile",
            )

    elif profile_id:
        profile = db.query(models.InstrumentProfile).filter_by(id=profile_id).first()
        print("test")
        if not profile:
            raise HTTPException(
                status_code=404, detail=f"No profile found with name '{profile_id}'"
            )

    return [profile]


@router.post("/profile/create", response_model=InstrumentProfileRead)
async def create_instrument_profile(
    new_instrument_profile: InstrumentProfileCreate,
    db: Session = Depends(get_db),
):
    "Route for creating instrument profiles"
    commands = ""
    if new_instrument_profile.commands:
        commands = convert_dict_to_commands_string(new_instrument_profile.commands)
    else:
        commands = None
    new_profile = models.InstrumentProfile(
        brand=new_instrument_profile.brand,
        model=new_instrument_profile.model,
        category=new_instrument_profile.category,
        commands=commands,
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


@router.post("/profil/update_commands", response_model=InstrumentProfileRead)
async def update_instrument_profile(
    id: UUID,
    new_commands: dict,
    db: Session = Depends(get_db),
):
    "Route for updateing instrument profiles"
    profile = db.query(models.InstrumentProfile).filter_by(id=id).first()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"No profile found with id: {id}",
        )
    profile.commands = convert_dict_to_commands_string(new_commands)
    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/profil/delete", response_model=str)
async def delete_instrument_profile(
    id: UUID,
    db: Session = Depends(get_db),
):
    "Route for updateing instrument profiles"
    profile = db.query(models.InstrumentProfile).filter_by(id=id).first()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"No profile found with id: {id}",
        )
    db.delete(profile)
    db.commit()

    return Response(
        content=f"Successfully deleted profile with id: {id}", status_code=200
    )
