from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app import create_app
from storage import UserStorage


INGRESS_PATH = "/api/hassio_ingress/test"


def _make_client(tmp_path):
    test_storage = UserStorage(data_dir=str(tmp_path))
    templates_dir = Path(__file__).resolve().parents[1] / "templates"
    mqtt_handler = MagicMock()
    app = create_app(
        storage=test_storage,
        mqtt_handler=mqtt_handler,
        templates_dir=str(templates_dir),
        ingress_path=INGRESS_PATH,
        api_key="",
    )
    return TestClient(app, root_path=INGRESS_PATH), TestClient(app), test_storage


def test_dashboard_form_actions_include_ingress_root_path(tmp_path):
    client, _, _ = _make_client(tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert 'action="http://testserver/api/hassio_ingress/test/users/add"' in response.text


def test_add_user_redirect_preserves_ingress_root_path(tmp_path):
    client, _, _ = _make_client(tmp_path)

    response = client.post(
        "/users/add",
        data={"name": "Alice", "code": "1234"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "http://testserver/api/hassio_ingress/test/"


def test_delete_user_redirect_preserves_ingress_root_path(tmp_path):
    client, _, storage = _make_client(tmp_path)
    user = storage.add_user("Alice", "1234")

    response = client.post(f"/users/{user['id']}/delete", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "http://testserver/api/hassio_ingress/test/"


def test_update_user_redirect_preserves_ingress_root_path(tmp_path):
    client, _, storage = _make_client(tmp_path)
    user = storage.add_user("Alice", "1234")

    response = client.post(
        f"/users/{user['id']}/update",
        data={"name": "Alice B", "code": "5678"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "http://testserver/api/hassio_ingress/test/"
    assert storage.find_user_by_code("1234") is None
    updated = storage.find_user_by_code("5678")
    assert updated is not None
    assert updated["name"] == "Alice B"


def test_disable_user_redirect_preserves_ingress_root_path(tmp_path):
    client, _, storage = _make_client(tmp_path)
    user = storage.add_user("Alice", "1234")

    response = client.post(f"/users/{user['id']}/disable", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "http://testserver/api/hassio_ingress/test/"
    assert storage.find_user_by_code("1234") is None


def test_enable_user_redirect_preserves_ingress_root_path(tmp_path):
    client, _, storage = _make_client(tmp_path)
    user = storage.add_user("Alice", "1234")
    storage.set_user_enabled(user["id"], False)

    response = client.post(f"/users/{user['id']}/enable", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "http://testserver/api/hassio_ingress/test/"
    assert storage.find_user_by_code("1234") is not None


def test_prefixed_request_path_is_served_when_proxy_does_not_strip_ingress_path(tmp_path):
    _, raw_client, _ = _make_client(tmp_path)

    response = raw_client.get(f"{INGRESS_PATH}/")

    assert response.status_code == 200
    assert 'action="http://testserver/api/hassio_ingress/test/users/add"' in response.text


def test_prefixed_post_redirect_preserves_ingress_root_path(tmp_path):
    _, raw_client, _ = _make_client(tmp_path)

    response = raw_client.post(
        f"{INGRESS_PATH}/users/add",
        data={"name": "Alice", "code": "1234"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "http://testserver/api/hassio_ingress/test/"


def test_prefixed_update_redirect_preserves_ingress_root_path(tmp_path):
    _, raw_client, storage = _make_client(tmp_path)
    user = storage.add_user("Alice", "1234")

    response = raw_client.post(
        f"{INGRESS_PATH}/users/{user['id']}/update",
        data={"name": "Alice C", "code": "9999"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "http://testserver/api/hassio_ingress/test/"
    assert storage.find_user_by_code("1234") is None
    updated = storage.find_user_by_code("9999")
    assert updated is not None
    assert updated["name"] == "Alice C"


def test_prefixed_disable_redirect_preserves_ingress_root_path(tmp_path):
    _, raw_client, storage = _make_client(tmp_path)
    user = storage.add_user("Alice", "1234")

    response = raw_client.post(
        f"{INGRESS_PATH}/users/{user['id']}/disable",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "http://testserver/api/hassio_ingress/test/"
    assert storage.find_user_by_code("1234") is None