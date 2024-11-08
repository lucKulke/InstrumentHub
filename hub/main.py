# instrument_hub.py
from fastapi import FastAPI
import uvicorn
from src.routes import (
    instrument_management,
    calibration,
    data_logs,
    simulation,
    data_routing,
)


app = FastAPI()
app.include_router(instrument_management.router)
app.include_router(calibration.router)
app.include_router(data_logs.router)
app.include_router(simulation.router)
app.include_router(data_routing.router)


HOST = "0.0.0.0"
PORT = 9000
INSTRUMENT_DEFUALT_PORT = 8080


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, timeout_keep_alive=120)
