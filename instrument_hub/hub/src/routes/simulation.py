# instrument_hub.py
from fastapi import Request, Form, APIRouter
import requests
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/simulation",
    tags=["Simulation"],
)


templates = Jinja2Templates(directory="src/test_client")


@router.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    "HTML page to simulate webclient"
    # Serve the form
    return templates.TemplateResponse("index.html", {"request": request})
