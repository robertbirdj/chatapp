import sys
import os
from flask import Flask, jsonify, request

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from presenter.presenter import Presenter
from model.message import Message # Needed for type hinting

# Create the Flask app and the Presenter
app = Flask(__name__)
# We create a single presenter instance that all requests will share.
# This ensures that all interactions go through the same model instance.
presenter = Presenter()

# --- Helper Functions ---

def format_message(message: Message) -> dict:
    """Converts a Message object to a JSON-serializable dictionary."""
    return {
        "id": message.id,
        "name": message.name,
        "timestamp": message.timestamp.isoformat(),
        "content": message.content
    }

# --- API Endpoints ---

@app.route("/", methods=["GET"])
def index():
    """A simple route to confirm the server is running."""
    return jsonify({"status": "MCP Server is running"}), 200

@app.route("/chats", methods=["GET"])
def list_chats():
    """Returns a list of available chats."""
    chats = presenter.get_chat_list()
    return jsonify(chats), 200

@app.route("/chats/<string:chat_name>", methods=["GET"])
def view_chat(chat_name: str):
    """Returns the entire chat history for a given chat."""
    try:
        presenter.switch_chat(chat_name)
        messages = presenter.get_messages()
        return jsonify([format_message(msg) for msg in messages]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route("/chats", methods=["POST"])
def create_chat():
    """Creates a new chat and returns its details."""
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Missing 'name' in request body"}), 400

    chat_name = data["name"]
    try:
        presenter.create_chat(chat_name)
        # After creating the chat, switch to it and get its (empty) details
        chat_details = presenter.get_chat(chat_name)
        # We also need to add the chat name to the response
        chat_details["name"] = chat_name
        return jsonify(chat_details), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/participants", methods=["GET"])
def view_participants():
    """Returns the current list of participants."""
    participants = presenter.get_participants()
    return jsonify(participants), 200

@app.route("/participants", methods=["POST"])
def add_participant():
    """Adds a new participant to the chat."""
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Missing 'name' in request body"}), 400

    name = data["name"]
    presenter.add_participant(name)
    return jsonify({"message": f"Participant '{name}' added successfully."}), 201

@app.route("/participants", methods=["DELETE"])
def remove_participant():
    """Removes a participant from the chat."""
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Missing 'name' in request body"}), 400

    name = data["name"]
    # The current model doesn't error on removing a non-existent user,
    # but we can add a check here for a more robust API.
    if name not in presenter.get_participants():
        return jsonify({"error": f"Participant '{name}' not found."}), 404

    presenter.remove_participant(name)
    return jsonify({"message": f"Participant '{name}' removed successfully."}), 200

@app.route("/messages", methods=["POST"])
def add_message():
    """Adds a new message to the chat."""
    data = request.get_json()
    if not data or "name" not in data or "message" not in data:
        return jsonify({"error": "Request body must contain 'name' and 'message'"}), 400

    name = data["name"]
    content = data["message"]

    try:
        new_message = presenter.add_message(name, content)
        return jsonify(format_message(new_message)), 201
    except ValueError as e:
        # This happens if the participant is not approved
        return jsonify({"error": str(e)}), 400

@app.route("/messages/insert", methods=["POST"])
def insert_message():
    """Inserts a new message after a specified message ID."""
    data = request.get_json()
    if not data or "name" not in data or "message" not in data or "after_id" not in data:
        return jsonify({"error": "Request body must contain 'name', 'message', and 'after_id'"}), 400

    name = data["name"]
    content = data["message"]
    after_id = data["after_id"]

    try:
        new_message = presenter.insert_message(name, content, after_id)
        return jsonify(format_message(new_message)), 201
    except ValueError as e:
        # This happens if the participant is not approved or the after_id is not found
        return jsonify({"error": str(e)}), 400

@app.route("/messages/<int:message_id>", methods=["PUT"])
def edit_message(message_id: int):
    """Edits a specified message, requiring confirmation."""
    data = request.get_json()
    if not data or "new_content" not in data:
        return jsonify({"error": "Missing 'new_content' in request body"}), 400

    new_content = data["new_content"]

    # Check for confirmation
    is_confirmed = request.args.get('confirm') == 'true'

    try:
        message = presenter.get_message_by_id(message_id)
        if not message:
            raise ValueError(f"Message with ID {message_id} not found.")

        if not is_confirmed:
            # Step 1: Request confirmation from the client
            return jsonify({
                "confirmation_required": True,
                "message": "Please confirm that you want to edit this message.",
                "details": {
                    "id": message.id,
                    "current_content": message.content,
                    "new_content": new_content
                }
            }), 200 # 200 OK, but with a special body for the tool to interpret
        else:
            # Step 2: Perform the action
            presenter.edit_message(message_id, new_content)
            return jsonify({"message": f"Message {message_id} edited successfully."}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route("/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id: int):
    """Deletes a specified message, requiring confirmation."""
    is_confirmed = request.args.get('confirm') == 'true'

    try:
        message = presenter.get_message_by_id(message_id)
        if not message:
            raise ValueError(f"Message with ID {message_id} not found.")

        if not is_confirmed:
            # Step 1: Request confirmation
            return jsonify({
                "confirmation_required": True,
                "message": "Please confirm that you want to delete this message.",
                "details": format_message(message)
            }), 200
        else:
            # Step 2: Perform the action
            presenter.delete_message(message_id)
            return jsonify({"message": f"Message {message_id} deleted successfully."}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)
