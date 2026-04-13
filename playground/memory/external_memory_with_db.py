# external_memory.py
import json
import anthropic
from datetime import datetime
from pathlib import Path

client = anthropic.Anthropic()

# import sqlite3
# instead of sqlite db , storing json in file


class PersistentMemoryAgent:
    def __init__(self, db_path: str = "agent_memory.json", user_id: str = "default"):
        self.db_path = Path(db_path)
        self.user_id = user_id
        self._init_store()

    def _init_store(self):
        if not self.db_path.exists():
            self.db_path.write_text(json.dumps({}))

    def _load_store(self) -> dict:
        return json.loads(self.db_path.read_text())

    def _save_store(self, store: dict):
        self.db_path.write_text(json.dumps(store, indent=2))

    def _load_history(self, limit: int = 20) -> list:
        store = self._load_store()
        messages = store.get(self.user_id, [])
        # Take last `limit` messages
        return [{"role": m["role"], "content": m["content"]} for m in messages[-limit:]]

    def _save_message(self, role: str, content: str):
        store = self._load_store()
        if self.user_id not in store:
            store[self.user_id] = []
        store[self.user_id].append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )
        self._save_store(store)

    def chat(self, user_input: str) -> str:
        self._save_message("user", user_input)

        history = self._load_history()

        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system="You are a persistent assistant. You remember past conversations.",
            messages=history,
        )

        assistant_msg = response.content[0].text
        self._save_message("assistant", assistant_msg)
        return assistant_msg

    def clear_memory(self):
        store = self._load_store()
        store.pop(self.user_id, None)
        self._save_store(store)
        print(f"Memory cleared for user: {self.user_id}")


# Test across "sessions"
agent = PersistentMemoryAgent(user_id="kiran_k_saravana")
print(agent.chat("My favorite programming language is Python."))
print(agent.chat("I prefer dark mode in all my editors."))

# Simulate new session — memory persists from file
agent2 = PersistentMemoryAgent(user_id="kiran_k_saravana")
print(agent2.chat("What do you know about my preferences?"))  # Remembers!
