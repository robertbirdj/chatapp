import sys
from presenter.presenter import Presenter
from gui.main_window import ChatWindow

def main():
    """
    Main entry point for the Local Chat application.
    This script launches the graphical user interface (GUI).
    """
    print("Launching Local Chat GUI...")

    # The Presenter is the core of the application's logic
    presenter = Presenter()

    # The ChatWindow is the GUI view, driven by the presenter
    app = ChatWindow(presenter, username="User") # You can change the username here

    # Start the GUI event loop
    app.run()

    print("GUI closed. Exiting.")

if __name__ == "__main__":
    # To run the MCP server for the Gemini CLI, execute the following command
    # in your terminal from the project root directory:
    # python3 mcp_server/server.py

    main()
