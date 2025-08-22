import sys
import os
from typing import List

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.chat import Chat
from model.message import Message

class Presenter:
    """
    The Presenter acts as a bridge between the Model (Chat) and the Views.
    """
    def __init__(self):
        # The presenter creates and owns the model instance
        self.model = Chat()

    def get_participants(self) -> List[str]:
        """Gets the list of participants from the model."""
        return self.model.get_participants()

    def add_participant(self, name: str) -> None:
        """Adds a participant via the model."""
        # Basic validation can happen here if needed,
        # but for now, we delegate to the model.
        self.model.add_participant(name)

    def remove_participant(self, name: str) -> None:
        """Removes a participant via the model."""
        self.model.remove_participant(name)

    def get_messages(self) -> List[Message]:
        """Gets the list of messages from the model."""
        return self.model.get_messages()

    def add_message(self, name: str, content: str) -> Message:
        """Adds a message via the model."""
        return self.model.add_message(name, content)

    def edit_message(self, message_id: int, new_content: str) -> None:
        """Edits a message via the model."""
        # The user approval logic will be handled by the view
        # before this method is ever called.
        self.model.edit_message(message_id, new_content)

    def delete_message(self, message_id: int) -> None:
        """Deletes a message via the model."""
        # The user approval logic will be handled by the view
        # before this method is ever called.
        self.model.delete_message(message_id)

    def get_message_by_id(self, message_id: int):
        """Finds a message by its ID via the model."""
        return self.model.get_message_by_id(message_id)
