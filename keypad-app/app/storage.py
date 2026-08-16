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

    def get_users(self) -> list:
        return [{"id": u["id"], "name": u["name"]} for u in self._users.values()]

    def add_user(self, name: str, code: str) -> dict:
        user_id = str(uuid.uuid4())
        hashed = bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode()
        self._users[user_id] = {"id": user_id, "name": name, "code": hashed}
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

    def delete_user(self, user_id: str) -> bool:
        if user_id not in self._users:
            return False
        del self._users[user_id]
        self._save_users()
        return True

    def find_user_by_code(self, code: str) -> Optional[dict]:
        for user in self._users.values():
            try:
                if bcrypt.checkpw(code.encode(), user["code"].encode()):
                    return {"id": user["id"], "name": user["name"]}
            except Exception:
                continue
        return None

    def add_history_entry(self, entry: dict):
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()
        self._history.insert(0, entry)
        self._history = self._history[:1000]  # keep last 1000 entries
        self._save_history()

    def get_history(self, limit: int = 50) -> list:
        return self._history[:limit]
