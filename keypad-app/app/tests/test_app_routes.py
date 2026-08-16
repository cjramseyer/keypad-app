from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app import create_app
from storage import UserStorage


def _make_client(tmp_path):
    test_storage = UserStorage(data_dir=str(tmp_path))
    templates_dir = Path(__file__).resolve().parents[1] / "templates"
    mqtt_handler = MagicMock()
    app = create_app(
        storage=test_storage,
        mqtt_handler=mqtt_handler,
        templates_dir=str(templates_dir),
        api_key="",
    )
    return TestClient(app, root_path="/api/hassio_ingress/test"), test_storage


def test_dashboard_form_actions_include_ingress_root_path(tmp_path):
    client, _ = _make_client(tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert 'action="http://testserver/api/hassio_ingress/test/users/add"' in response.text


def test_add_user_redirect_preserves_ingress_root_path(tmp_path):
    client, _ = _make_client(tmp_path)

    response = client.post(
        "/users/add",
        data={"name": "Alice", "code": "1234"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "http://testserver/api/hassio_ingress/test/"


def test_delete_user_redirect_preserves_ingress_root_path(tmp_path):
    client, storage = _make_client(tmp_path)
    user = storage.add_user("Alice", "1234")

    response = client.post(f"/users/{user['id']}/delete", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "http://testserver/api/hassio_ingress/test/"