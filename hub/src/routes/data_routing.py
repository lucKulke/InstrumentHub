from fastapi import (
    WebSocket,
    WebSocketDisconnect,
    Depends,
    Request,
    APIRouter,
)
from starlette.websockets import WebSocketDisconnect
from typing import Dict, List
from src.db.db_init import get_db
from sqlalchemy.orm import Session
from src.db import models
from src.pydantic_models import (
    InstrumentCreate,
    InstrumentData,
)
from .instrument_management import create_instrument, get_instrument_profile
import json
from uuid import UUID
from datetime import datetime
from sqlalchemy import func
from src.utils import convert_commands_string_to_dict
import re

router = APIRouter(
    prefix="/data_routing",
    tags=["Data-Routing"],
)


class ConnectionManager:
    def __init__(self):
        # Separate dictionaries for clients and instruments
        self.active_client_connections: Dict[WebSocket, str] = {}
        self.active_instrument_connections: Dict[WebSocket, str] = {}

    async def connect_client(self, websocket: WebSocket, instrument_id: UUID):
        await websocket.accept()
        self.active_client_connections[websocket] = instrument_id

    async def connect_instrument(self, websocket: WebSocket, instrument_id: UUID):
        await websocket.accept()
        self.active_instrument_connections[websocket] = instrument_id

    def disconnect(self, websocket: WebSocket):
        # Remove from both dictionaries if present
        self.active_client_connections.pop(websocket, None)
        self.active_instrument_connections.pop(websocket, None)

    async def send_message(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)

    async def broadcast_to_clients(self, instrument_id: UUID, message: str):
        # Broadcast message to all clients subscribed to this instrument
        for websocket, subscribed_id in self.active_client_connections.items():
            if subscribed_id == instrument_id:
                await self.send_message(websocket, message)

    async def broadcast_to_instrument(self, instrument_id: UUID, message: str, db):
        if not self.check_if_led_command(message=message):
            is_valid_command = await self.validate_command(
                message=message, instrument_id=instrument_id, db=db
            )
  
            if not is_valid_command:
                await self.broadcast_to_clients(
                    instrument_id=instrument_id, message="Error: unknown command"
                )
              
                return False
        
        for websocket, subscribed_id in self.active_instrument_connections.items():
            if subscribed_id == instrument_id:
                await self.send_message(websocket, message)

    async def validate_command(self, message: str, instrument_id: UUID, db):
        profile = await get_instrument_profile(instrument_id=instrument_id, db=db)
        commands = profile[0].commands
        if not commands:
            return False
        commands = convert_commands_string_to_dict(profile[0].commands)
        if message in commands:
            return True
        else:
            return False

    def check_if_led_command(self, message: str):
        pattern = r"find_my_instrument_(red|green)_(\d+(\.\d+)?)_(\d+)"
        match = re.match(pattern, message)
        if match:
            return True
        else:
            return False


manager = ConnectionManager()


@router.websocket("/ws/client/{instrument_id}")
async def websocket_client_endpoint(
    websocket: WebSocket, instrument_id: UUID, db: Session = Depends(get_db)
):
    await manager.connect_client(websocket, instrument_id)
    try:
        while True:
            command = await websocket.receive_text()
            print(command)
            await manager.broadcast_to_instrument(
                instrument_id=instrument_id, message=command, db=db
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Instrument WebSocket endpoint
@router.websocket("/ws/instrument/{instrument_id}")
async def websocket_instrument_endpoint(
    websocket: WebSocket, instrument_id: UUID, db: Session = Depends(get_db)
):

    await manager.connect_instrument(websocket, instrument_id)
    await manager.broadcast_to_clients(instrument_id, "online")
    instrument_in_db = db.query(models.Instrument).filter_by(id=instrument_id).first()
    if instrument_in_db:
        instrument_in_db.online = 1
        instrument_in_db.last_logon = datetime.now()
        db.commit()
    else:
        # register instrument in database
        instrument_create = InstrumentCreate(
            id=instrument_id,
        )
        await create_instrument(instrument=instrument_create, db=db)

    try:
        while True:
            # Receive data from instrument
            # await websocket.send_text("hi")
            instrument_text = await websocket.receive_text()
            print(instrument_text)
            instrument_data = json.loads(instrument_text)

            await manager.broadcast_to_clients(
                instrument_id, str(instrument_data["data"])
            )

            # log data
            new_data = models.InstrumentData(
                instrument_id=instrument_id, data=str(instrument_data["data"])
            )

            db.add(new_data)
            db.commit()

    except Exception as e:
        print("offline")
        await manager.broadcast_to_clients(instrument_id, "offline")
        if instrument_in_db:
            instrument_in_db.online = 0
        else:  # only during initial connection
            db.query(models.Instrument).filter_by(id=instrument_id).first().online = 0
        db.commit()
        print(f"error: {e}")
        manager.disconnect(websocket)
