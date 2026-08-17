import bcrypt
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

_DEFAULT_DATA_DIR = os.environ.get("DATA_DIR", "/data")


class UserStorage:
    def __init__(self, data_dir: str = None):
        self._dir = data_dir or _DEFAULT_DATA_DIR
        self._users_path = os.path.join(self._dir, "users.json")
        self._history_path = os.path.join(self._dir, "history.json")
        os.makedirs(self._dir, exist_ok=True)
        self._users: dict = self._load(self._users_path, {})
        self._history: list = self._load(self._history_path, [])

    @staticmethod
    def _load(path: str, default):
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return default

    def _save_users(self):
        with open(self._users_path, "w") as f:
            json.dump(self._users, f, indent=2)

    def _save_history(self):
        with open(self._history_path, "w") as f:
            json.dump(self._history, f, indent=2)

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def get_users(self) -> list:
        users = []
        for user in self._users.values():
            users.append({
                "id": user["id"],
                "name": user["name"],
                "enabled": user.get("enabled", True),
                "created_at": user.get("created_at"),
                "last_used_at": user.get("last_used_at"),
            })
        return users

    def add_user(self, name: str, code: str) -> dict:
        user_id = str(uuid.uuid4())
        hashed = bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode()
        self._users[user_id] = {
            "id": user_id,
            "name": name,
            "code": hashed,
            "enabled": True,
            "created_at": self._now_iso(),
            "last_used_at": None,
        }
        self._save_users()
        return {"id": user_id, "name": name}

    def update_user(self, user_id: str, name: Optional[str], code: Optional[str]) -> Optional[dict]:
        if user_id not in self._users:
            return None
        if name:
            self._users[user_id]["name"] = name
        if code:
            self._users[user_id]["code"] = bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode()
        self._save_users()
        return {"id": user_id, "name": self._users[user_id]["name"]}

    def mark_user_used(self, user_id: str) -> bool:
        if user_id not in self._users:
            return False
        self._users[user_id]["last_used_at"] = self._now_iso()
        self._save_users()
        return True

    def set_user_enabled(self, user_id: str, enabled: bool) -> bool:
        if user_id not in self._users:
            return False
        self._users[user_id]["enabled"] = enabled
        self._save_users()
        return True

    def delete_user(self, user_id: str) -> bool:
        if user_id not in self._users:
            return False
        del self._users[user_id]
        self._save_users()
        return True

    def find_user_by_code(self, code: str) -> Optional[dict]:
        for user in self._users.values():
            try:
                if not user.get("enabled", True):
                    continue
                if bcrypt.checkpw(code.encode(), user["code"].encode()):
                    return {"id": user["id"], "name": user["name"]}
            except Exception:
                continue
        return None

    def add_history_entry(self, entry: dict):
        entry["timestamp"] = self._now_iso()
        self._history.insert(0, entry)
        self._history = self._history[:1000]  # keep last 1000 entries
        self._save_history()

    def get_history(self, limit: int = 50) -> list:
        return self._history[:limit]
