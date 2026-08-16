from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from fastapi.templating import Jinja2Templates

import app as app_module
from storage import UserStorage


def _make_client(tmp_path, monkeypatch):
    test_storage = UserStorage(data_dir=str(tmp_path))
    templates_dir = Path(__file__).resolve().parents[1] / "templates"
    monkeypatch.setattr(app_module, "storage", test_storage)
    monkeypatch.setattr(app_module, "templates", Jinja2Templates(directory=str(templates_dir)))
    monkeypatch.setattr(app_module.mqtt_handler, "start", MagicMock())
    monkeypatch.setattr(app_module.mqtt_handler, "stop", MagicMock())
    return TestClient(app_module.app, root_path="/api/hassio_ingress/test")


def test_dashboard_form_actions_include_ingress_root_path(tmp_path, monkeypatch):
    client = _make_client(tmp_path, monkeypatch)

    response = client.get("/")

    assert response.status_code == 200
    assert 'action="http://testserver/api/hassio_ingress/test/users/add"' in response.text


def test_add_user_redirect_preserves_ingress_root_path(tmp_path, monkeypatch):
    client = _make_client(tmp_path, monkeypatch)

    response = client.post(
        "/users/add",
        data={"name": "Alice", "code": "1234"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "http://testserver/api/hassio_ingress/test/"


def test_delete_user_redirect_preserves_ingress_root_path(tmp_path, monkeypatch):
    client = _make_client(tmp_path, monkeypatch)
    user = app_module.storage.add_user("Alice", "1234")

    response = client.post(f"/users/{user['id']}/delete", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "http://testserver/api/hassio_ingress/test/"