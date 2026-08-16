import json
import pytest
from unittest.mock import MagicMock


def _make_storage(tmp_path):
    from storage import UserStorage
    return UserStorage(data_dir=str(tmp_path))


def test_add_user_returns_without_code(tmp_path):
    s = _make_storage(tmp_path)
    user = s.add_user("Alice", "1234")
    assert user["name"] == "Alice"
    assert "code" not in user


def test_get_users_excludes_code(tmp_path):
    s = _make_storage(tmp_path)
    s.add_user("Alice", "1234")
    users = s.get_users()
    assert len(users) == 1
    assert "code" not in users[0]


def test_find_user_by_correct_code(tmp_path):
    s = _make_storage(tmp_path)
    s.add_user("Alice", "1234")
    user = s.find_user_by_code("1234")
    assert user is not None
    assert user["name"] == "Alice"
    assert "code" not in user


def test_find_user_by_wrong_code_returns_none(tmp_path):
    s = _make_storage(tmp_path)
    s.add_user("Alice", "1234")
    assert s.find_user_by_code("9999") is None


def test_delete_user(tmp_path):
    s = _make_storage(tmp_path)
    user = s.add_user("Alice", "1234")
    assert s.delete_user(user["id"]) is True
    assert s.find_user_by_code("1234") is None


def test_delete_nonexistent_user_returns_false(tmp_path):
    s = _make_storage(tmp_path)
    assert s.delete_user("does-not-exist") is False


def test_update_user_name_only(tmp_path):
    s = _make_storage(tmp_path)
    user = s.add_user("Alice", "1234")
    updated = s.update_user(user["id"], name="Bob", code=None)
    assert updated["name"] == "Bob"
    assert s.find_user_by_code("1234") is not None


def test_update_user_code(tmp_path):
    s = _make_storage(tmp_path)
    user = s.add_user("Alice", "1234")
    s.update_user(user["id"], name=None, code="5678")
    assert s.find_user_by_code("1234") is None
    assert s.find_user_by_code("5678") is not None


def test_update_nonexistent_user_returns_none(tmp_path):
    s = _make_storage(tmp_path)
    assert s.update_user("no-such-id", name="X", code=None) is None


def test_history_entry_has_timestamp(tmp_path):
    s = _make_storage(tmp_path)
    s.add_history_entry({"device_id": "front", "valid": True, "user_name": "Alice", "user_id": "x"})
    history = s.get_history()
    assert len(history) == 1
    assert "timestamp" in history[0]


def test_history_limit_respected(tmp_path):
    s = _make_storage(tmp_path)
    for i in range(10):
        s.add_history_entry({"device_id": "d", "valid": True, "user_name": "A", "user_id": "x"})
    assert len(s.get_history(limit=3)) == 3


def test_persistence_across_instances(tmp_path):
    s1 = _make_storage(tmp_path)
    s1.add_user("Alice", "1234")
    s2 = _make_storage(tmp_path)
    assert s2.find_user_by_code("1234") is not None
