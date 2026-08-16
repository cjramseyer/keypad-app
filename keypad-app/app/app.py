import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import Depends, FastAPI, Form, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from keypad import KeypadMQTT
from storage import UserStorage

LOG_LEVEL = os.environ.get("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

def create_app(
    *,
    data_dir: Optional[str] = None,
    templates_dir: Optional[str] = None,
    api_key: Optional[str] = None,
    mqtt_handler: Optional[KeypadMQTT] = None,
    storage: Optional[UserStorage] = None,
) -> FastAPI:
    resolved_storage = storage or UserStorage(data_dir=data_dir)
    resolved_mqtt_handler = mqtt_handler or KeypadMQTT(resolved_storage)
    resolved_templates_dir = templates_dir or str(Path("/app/templates"))
    resolved_templates = Jinja2Templates(directory=resolved_templates_dir)
    resolved_api_key = os.environ.get("API_KEY", "") if api_key is None else api_key

    def require_api_key(x_api_key: str = Header(default=None)):
        if resolved_api_key and x_api_key != resolved_api_key:
            raise HTTPException(status_code=401, detail="Unauthorized")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        resolved_mqtt_handler.start()
        yield
        resolved_mqtt_handler.stop()

    app = FastAPI(title="Keypad Manager", lifespan=lifespan)
    app.state.storage = resolved_storage
    app.state.mqtt_handler = resolved_mqtt_handler
    app.state.templates = resolved_templates

    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request):
        return resolved_templates.TemplateResponse(request, "index.html", {
            "request": request,
            "users": resolved_storage.get_users(),
            "history": resolved_storage.get_history(limit=50),
        })

    @app.post("/users/add")
    async def add_user(request: Request, name: str = Form(...), code: str = Form(...)):
        if not name.strip():
            raise HTTPException(status_code=400, detail="Name is required")
        if not code.strip().isdigit():
            raise HTTPException(status_code=400, detail="Code must be digits only")
        resolved_storage.add_user(name.strip(), code.strip())
        return RedirectResponse(url=str(request.url_for("dashboard")), status_code=303)

    @app.post("/users/{user_id}/delete")
    async def delete_user(request: Request, user_id: str):
        if not resolved_storage.delete_user(user_id):
            raise HTTPException(status_code=404, detail="User not found")
        return RedirectResponse(url=str(request.url_for("dashboard")), status_code=303)

    @app.post("/users/{user_id}/update")
    async def update_user(request: Request, user_id: str, name: str = Form(None), code: str = Form(None)):
        if code and not code.strip().isdigit():
            raise HTTPException(status_code=400, detail="Code must be digits only")
        user = resolved_storage.update_user(user_id, name=name, code=code)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return RedirectResponse(url=str(request.url_for("dashboard")), status_code=303)

    # JSON API endpoints — protected by API key when api_key option is set
    @app.get("/api/users", dependencies=[Depends(require_api_key)])
    async def api_list_users():
        return resolved_storage.get_users()

    @app.get("/api/history", dependencies=[Depends(require_api_key)])
    async def api_get_history(limit: int = 50):
        return resolved_storage.get_history(limit=limit)

    return app


if __name__ == "__main__":
    ingress_path = os.environ.get("INGRESS_PATH", "")
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        root_path=ingress_path,
        proxy_headers=True,
        forwarded_allow_ips="*",
        log_level=LOG_LEVEL.lower(),
    )
