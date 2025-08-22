import unittest
import os
import sys
from datetime import datetime, timedelta

# Add the project root to the Python path to allow importing from 'model'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.chat import Chat
from model.chat_manager import ChatManager
from model.message import Message

TEST_CHAT_NAME = "test_chat"

class TestChatModel(unittest.TestCase):

    def setUp(self):
        """Set up a clean environment for each test."""
        self.chat_manager = ChatManager(history_dir=".")
        # Ensure the test file does not exist before a test
        history_file = self.chat_manager.get_chat_history_file(TEST_CHAT_NAME)
        if os.path.exists(history_file):
            os.remove(history_file)

        self.chat_manager.create_chat(TEST_CHAT_NAME)
        self.chat = Chat(TEST_CHAT_NAME, self.chat_manager)

    def tearDown(self):
        """Clean up the environment after each test."""
        history_file = self.chat_manager.get_chat_history_file(TEST_CHAT_NAME)
        if os.path.exists(history_file):
            os.remove(history_file)

    def test_add_and_get_participant(self):
        """Test adding participants to the chat."""
        self.chat.add_participant("Alice")
        self.assertIn("Alice", self.chat.get_participants())
        self.assertEqual(len(self.chat.get_participants()), 1)

        # Test adding a duplicate participant
        self.chat.add_participant("Alice")
        self.assertEqual(len(self.chat.get_participants()), 1)

    def test_remove_participant(self):
        """Test removing participants from the chat."""
        self.chat.add_participant("Alice")
        self.chat.add_participant("Bob")
        self.chat.remove_participant("Alice")
        self.assertNotIn("Alice", self.chat.get_participants())
        self.assertIn("Bob", self.chat.get_participants())

        # Test removing a non-existent participant
        self.chat.remove_participant("Charlie")
        self.assertEqual(len(self.chat.get_participants()), 1)

    def test_add_message_success(self):
        """Test successfully adding a new message."""
        self.chat.add_participant("Alice")
        message = self.chat.add_message("Alice", "Hello, world!")
        self.assertEqual(len(self.chat.get_messages()), 1)
        self.assertEqual(message.name, "Alice")
        self.assertEqual(message.content, "Hello, world!")
        self.assertEqual(self.chat.get_messages()[0], message)

    def test_add_message_unapproved_participant(self):
        """Test that adding a message from an unapproved participant fails."""
        with self.assertRaises(ValueError):
            self.chat.add_message("Eve", "Sneaky message")
        self.assertEqual(len(self.chat.get_messages()), 0)

    def test_sequential_timestamps(self):
        """Test that message timestamps are always sequential."""
        self.chat.add_participant("Alice")
        msg1 = self.chat.add_message("Alice", "First message")
        # To simulate a message arriving very quickly, we manually set the second one
        # In the Chat class logic, it will handle this.
        msg2 = self.chat.add_message("Alice", "Second message")
        self.assertGreater(msg2.timestamp, msg1.timestamp)

    def test_edit_message(self):
        """Test editing an existing message."""
        self.chat.add_participant("Alice")
        message = self.chat.add_message("Alice", "Original content")
        self.chat.edit_message(message.id, "Edited content")
        edited_message = self.chat.get_message_by_id(message.id)
        self.assertIsNotNone(edited_message)
        self.assertEqual(edited_message.content, "Edited content")

    def test_edit_non_existent_message(self):
        """Test that editing a non-existent message raises an error."""
        with self.assertRaises(ValueError):
            self.chat.edit_message(999, "This should fail")

    def test_delete_message(self):
        """Test deleting an existing message."""
        self.chat.add_participant("Alice")
        message_to_keep = self.chat.add_message("Alice", "Keep this one")
        message_to_delete = self.chat.add_message("Alice", "Delete this one")
        self.chat.delete_message(message_to_delete.id)
        self.assertEqual(len(self.chat.get_messages()), 1)
        self.assertEqual(self.chat.get_messages()[0], message_to_keep)

    def test_delete_non_existent_message(self):
        """Test that deleting a non-existent message raises an error."""
        self.chat.add_participant("Alice")
        self.chat.add_message("Alice", "A message")
        with self.assertRaises(ValueError):
            self.chat.delete_message(999)
        self.assertEqual(len(self.chat.get_messages()), 1)

    def test_data_persistence(self):
        """Test that chat data is correctly saved and loaded."""
        self.chat.add_participant("Alice")
        self.chat.add_message("Alice", "This is a test.")

        # Create a new Chat instance with the same chat name and manager
        new_chat = Chat(TEST_CHAT_NAME, self.chat_manager)
        self.assertIn("Alice", new_chat.get_participants())
        self.assertEqual(len(new_chat.get_messages()), 1)
        self.assertEqual(new_chat.get_messages()[0].content, "This is a test.")

if __name__ == "__main__":
    unittest.main()
