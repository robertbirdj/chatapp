import json
from datetime import datetime, timedelta
from typing import List, Optional

from .message import Message

class Chat:
    """Manages the chat history and participants."""

    def __init__(self, history_file: str = "chat_history.json"):
        self.history_file = history_file
        self.messages: List[Message] = []
        self.participants: List[str] = []
        # Initial load when the object is created.
        self._load_data()

    def _load_data(self):
        """
        Loads chat history and participants from the JSON file.
        This is called before every operation to ensure data is fresh.
        """
        try:
            with open(self.history_file, 'r') as f:
                # Use a lock here in a multi-threaded server, but for separate
                # processes, file system atomicity is what we rely on.
                data = json.load(f)
                self.participants = data.get("participants", [])
                self.messages = [
                    Message(
                        id=msg["id"],
                        name=msg["name"],
                        timestamp=datetime.fromisoformat(msg["timestamp"]),
                        content=msg["content"]
                    ) for msg in data.get("messages", [])
                ]
        except (FileNotFoundError, json.JSONDecodeError):
            self.participants = []
            self.messages = []

    def _save_data(self):
        """Saves the current chat state to the JSON file."""
        with open(self.history_file, 'w') as f:
            self.messages.sort(key=lambda m: m.timestamp)
            data = {
                "participants": self.participants,
                "messages": [
                    {
                        "id": msg.id,
                        "name": msg.name,
                        "timestamp": msg.timestamp.isoformat(),
                        "content": msg.content
                    } for msg in self.messages
                ]
            }
            json.dump(data, f, indent=4)

    def get_participants(self) -> List[str]:
        self._load_data()
        return self.participants

    def add_participant(self, name: str) -> None:
        self._load_data()
        if name and name not in self.participants:
            self.participants.append(name)
            self._save_data()

    def remove_participant(self, name: str) -> None:
        self._load_data()
        if name in self.participants:
            self.participants.remove(name)
            self._save_data()

    def get_messages(self) -> List[Message]:
        self._load_data()
        return sorted(self.messages, key=lambda m: m.timestamp)

    def _get_next_message_id(self) -> int:
        # This is an internal method, it assumes data is already loaded.
        if not self.messages:
            return 1
        return max(msg.id for msg in self.messages) + 1

    def add_message(self, name: str, content: str) -> Message:
        self._load_data()
        if name not in self.participants:
            raise ValueError(f"'{name}' is not an approved participant.")

        now = datetime.now()
        last_timestamp = self.messages[-1].timestamp if self.messages else None
        if last_timestamp and now <= last_timestamp:
            now = last_timestamp + timedelta(microseconds=1)

        new_message = Message(
            id=self._get_next_message_id(),
            name=name,
            timestamp=now,
            content=content
        )
        self.messages.append(new_message)
        self._save_data()
        return new_message

    def get_message_by_id(self, message_id: int) -> Optional[Message]:
        self._load_data()
        for msg in self.messages:
            if msg.id == message_id:
                return msg
        return None

    def edit_message(self, message_id: int, new_content: str) -> None:
        self._load_data()
        message_to_edit = None
        for msg in self.messages:
            if msg.id == message_id:
                message_to_edit = msg
                break

        if message_to_edit:
            message_to_edit.content = new_content
            self._save_data()
        else:
            raise ValueError(f"Message with ID {message_id} not found.")

    def delete_message(self, message_id: int) -> None:
        self._load_data()
        initial_len = len(self.messages)
        self.messages = [msg for msg in self.messages if msg.id != message_id]
        if len(self.messages) == initial_len:
             raise ValueError(f"Message with ID {message_id} not found.")
        self._save_data()
