import json
import pytest
from unittest.mock import MagicMock

from keypad import KeypadMQTT, MAX_CODE_LENGTH


def _make_handler(tmp_path):
    from storage import UserStorage
    storage = UserStorage(data_dir=str(tmp_path))
    handler = KeypadMQTT(storage)
    handler.client = MagicMock()
    return handler, storage


def test_valid_code_publishes_valid_event(tmp_path):
    handler, storage = _make_handler(tmp_path)
    storage.add_user("Alice", "1234")
    handler._handle_code("front-door", "1234")
    assert handler.client.publish.called
    payload = json.loads(handler.client.publish.call_args_list[0][0][1])
    assert payload["valid"] is True
    assert payload["user_name"] == "Alice"
    assert payload["device_id"] == "front-door"


def test_invalid_code_publishes_invalid_event(tmp_path):
    handler, storage = _make_handler(tmp_path)
    handler._handle_code("front-door", "9999")
    assert handler.client.publish.called
    payload = json.loads(handler.client.publish.call_args_list[0][0][1])
    assert payload["valid"] is False


def test_valid_code_recorded_in_history(tmp_path):
    handler, storage = _make_handler(tmp_path)
    storage.add_user("Alice", "1234")
    handler._handle_code("front-door", "1234")
    history = storage.get_history()
    assert len(history) == 1
    assert history[0]["valid"] is True
    assert history[0]["user_name"] == "Alice"


def test_invalid_code_recorded_in_history(tmp_path):
    handler, storage = _make_handler(tmp_path)
    handler._handle_code("front-door", "0000")
    history = storage.get_history()
    assert len(history) == 1
    assert history[0]["valid"] is False
    assert history[0]["user_name"] is None


def test_oversized_payload_ignored(tmp_path):
    handler, storage = _make_handler(tmp_path)
    msg = MagicMock()
    msg.topic = "keypad/front-door/code"
    msg.payload = b"1" * (MAX_CODE_LENGTH + 1)
    handler._on_message(None, None, msg)
    handler.client.publish.assert_not_called()


def test_normal_payload_processed(tmp_path):
    handler, storage = _make_handler(tmp_path)
    storage.add_user("Alice", "1234")
    msg = MagicMock()
    msg.topic = "keypad/front-door/code"
    msg.payload = b"1234"
    handler._on_message(None, None, msg)
    assert handler.client.publish.called


def test_event_published_to_both_topics(tmp_path):
    handler, storage = _make_handler(tmp_path)
    storage.add_user("Alice", "1234")
    handler._handle_code("front-door", "1234")
    topics = [call[0][0] for call in handler.client.publish.call_args_list]
    assert any("event" in t for t in topics)
    assert any("homeassistant" in t for t in topics)


def test_valid_code_updates_user_last_used_timestamp(tmp_path):
    handler, storage = _make_handler(tmp_path)
    storage.add_user("Alice", "1234")

    before = storage.get_users()[0]["last_used_at"]
    assert before is None

    handler._handle_code("front-door", "1234")

    after = storage.get_users()[0]["last_used_at"]
    assert after is not None
