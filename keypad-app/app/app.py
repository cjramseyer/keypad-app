import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI, Form, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from keypad import KeypadMQTT
from storage import UserStorage

API_KEY = os.environ.get("API_KEY", "")


def _require_api_key(x_api_key: str = Header(default=None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

storage = UserStorage()
mqtt_handler = KeypadMQTT(storage)


@asynccontextmanager
async def lifespan(app: FastAPI):
    mqtt_handler.start()
    yield
    mqtt_handler.stop()


app = FastAPI(title="Keypad Manager", lifespan=lifespan)
templates = Jinja2Templates(directory="/app/templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "users": storage.get_users(),
        "history": storage.get_history(limit=50),
    })


@app.post("/users/add")
async def add_user(name: str = Form(...), code: str = Form(...)):
    if not name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    if not code.strip().isdigit():
        raise HTTPException(status_code=400, detail="Code must be digits only")
    storage.add_user(name.strip(), code.strip())
    return RedirectResponse(url="/", status_code=303)


@app.post("/users/{user_id}/delete")
async def delete_user(user_id: str):
    if not storage.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return RedirectResponse(url="/", status_code=303)


@app.post("/users/{user_id}/update")
async def update_user(user_id: str, name: str = Form(None), code: str = Form(None)):
    if code and not code.strip().isdigit():
        raise HTTPException(status_code=400, detail="Code must be digits only")
    user = storage.update_user(user_id, name=name, code=code)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return RedirectResponse(url="/", status_code=303)


# JSON API endpoints — protected by API key when api_key option is set
@app.get("/api/users", dependencies=[Depends(_require_api_key)])
async def api_list_users():
    return storage.get_users()


@app.get("/api/history", dependencies=[Depends(_require_api_key)])
async def api_get_history(limit: int = 50):
    return storage.get_history(limit=limit)


if __name__ == "__main__":
    ingress_path = os.environ.get("INGRESS_PATH", "")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        root_path=ingress_path,
        proxy_headers=True,
        forwarded_allow_ips="*",
        log_level=LOG_LEVEL.lower(),
    )
