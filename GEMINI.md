# Gemini Agent Instructions for Local Chat Application

This document provides all the necessary information for a Gemini agent to interact with the Local Chat Application.

## 1. Overview

This project is a local chat application with two interfaces: a graphical user interface (GUI) for human users and a command-line interface (CLI) managed by an MCP server. Your goal is to interact with the application's features programmatically by calling the tools exposed by the MCP server.

## 2. Setup and Execution

Before you can use the tools, the MCP server must be running.

**Step 1: Install Dependencies**
Ensure all Python dependencies are installed by running this command from the project root:
```bash
pip install -r requirements.txt
```

**Step 2: Run the MCP Server**
The server exposes the tools via a Flask API. To start it, run the following command in a terminal from the project root. It is recommended to run it in the background.

```bash
python3 mcp_server/server.py &
```
The server will run on `http://localhost:5000`.

## 3. Tool Manifest

The MCP server exposes the following tools. Use these tools to interact with the chat application.

---

### **Tool: `view_chats`**
- **Description**: Returns the entire chat history, sorted by timestamp.
- **Method**: `GET`
- **Endpoint**: `http://localhost:5000/chats`
- **Parameters**: None

### **Tool: `view_participants`**
- **Description**: Returns the current list of approved participants in the chat.
- **Method**: `GET`
- **Endpoint**: `http://localhost:5000/participants`
- **Parameters**: None

### **Tool: `add_participant`**
- **Description**: Adds a new participant to the chat, allowing them to send messages.
- **Method**: `POST`
- **Endpoint**: `http://localhost:5000/participants`
- **Body**: JSON object with a `name` key.
- **Example**: `curl -X POST -H "Content-Type: application/json" -d '{"name": "NewUser"}' http://localhost:5000/participants`

### **Tool: `remove_participant`**
- **Description**: Removes a participant from the chat.
- **Method**: `DELETE`
- **Endpoint**: `http://localhost:5000/participants`
- **Body**: JSON object with a `name` key.
- **Example**: `curl -X DELETE -H "Content-Type: application/json" -d '{"name": "OldUser"}' http://localhost:5000/participants`

### **Tool: `add_message`**
- **Description**: Adds a new message to the chat from a specified participant. The sender must be on the participant list.
- **Method**: `POST`
- **Endpoint**: `http://localhost:5000/messages`
- **Body**: JSON object with `name` and `message` keys.
- **Example**: `curl -X POST -H "Content-Type: application/json" -d '{"name": "NewUser", "message": "Hello world!"}' http://localhost:5000/messages`

### **Tool: `edit_message`**
- **Description**: Edits the content of a specific message. **This action requires a two-step confirmation.**
- **Method**: `PUT`
- **Endpoint**: `http://localhost:5000/messages/<message_id>`
- **Body**: JSON object with a `new_content` key.
- **Confirmation Flow**:
    1.  **Initial Call**: Make a `PUT` request to the endpoint. The server will respond with `{"confirmation_required": true, ...}`.
    2.  **User Confirmation**: You must prompt the human user for confirmation.
    3.  **Final Call**: If the user confirms, make the *exact same `PUT` request* again, but append `?confirm=true` to the URL.
- **Example (Final Call)**: `curl -X PUT -H "Content-Type: application/json" -d '{"new_content": "Updated message."}' "http://localhost:5000/messages/1?confirm=true"`

### **Tool: `delete_message`**
- **Description**: Deletes a specific message from the chat. **This action requires a two-step confirmation.**
- **Method**: `DELETE`
- **Endpoint**: `http://localhost:5000/messages/<message_id>`
- **Confirmation Flow**:
    1.  **Initial Call**: Make a `DELETE` request to the endpoint. The server will respond with `{"confirmation_required": true, ...}`.
    2.  **User Confirmation**: You must prompt the human user for confirmation.
    3.  **Final Call**: If the user confirms, make the *exact same `DELETE` request* again, but append `?confirm=true` to the URL.
- **Example (Final Call)**: `curl -X DELETE "http://localhost:5000/messages/1?confirm=true"`
