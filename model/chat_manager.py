import os
import json
from typing import List

class ChatManager:
    """Manages the different chat histories."""

    def __init__(self, history_dir: str = "."):
        self.history_dir = history_dir
        self.chat_history_prefix = "chat_history_"

    def get_chat_list(self) -> List[str]:
        """Returns a list of available chat names."""
        chats = []
        for filename in os.listdir(self.history_dir):
            if filename.startswith(self.chat_history_prefix) and filename.endswith(".json"):
                chat_name = filename[len(self.chat_history_prefix):-len(".json")]
                chats.append(chat_name)
        return chats

    def get_chat_history_file(self, chat_name: str) -> str:
        """Returns the full path to the chat history file."""
        return os.path.join(self.history_dir, f"{self.chat_history_prefix}{chat_name}.json")

    def create_chat(self, chat_name: str):
        """Creates a new chat history file."""
        history_file = self.get_chat_history_file(chat_name)
        if os.path.exists(history_file):
            raise ValueError(f"Chat '{chat_name}' already exists.")

        with open(history_file, 'w') as f:
            json.dump({"participants": [], "messages": []}, f, indent=4)
