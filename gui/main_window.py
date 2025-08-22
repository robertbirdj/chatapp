import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from presenter.presenter import Presenter

class ChatWindow(tk.Tk):
    """
    The main GUI for the chat application.
    """
    def __init__(self, presenter: Presenter, username: str = "GUI_User"):
        super().__init__()
        self.presenter = presenter
        self.username = username

        if self.username not in self.presenter.get_participants():
            self.presenter.add_participant(self.username)

        self.title(f"Local Chat - Logged in as {self.username}")
        self.geometry("600x500")

        self._setup_widgets()
        self._create_menu()

        self.after(100, self._update_chat_display)

    def _setup_widgets(self):
        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.chat_display = scrolledtext.ScrolledText(
            main_frame, state=tk.DISABLED, wrap=tk.WORD, font=("Arial", 10)
        )
        self.chat_display.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        input_frame = tk.Frame(main_frame)
        input_frame.pack(padx=5, pady=5, fill=tk.X, expand=False)

        self.message_input = tk.Entry(input_frame, font=("Arial", 12))
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.message_input.bind("<Return>", self._on_send_message)

        self.send_button = tk.Button(
            input_frame, text="Send", command=self._on_send_message, font=("Arial", 10, "bold")
        )
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))

    def _create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        participants_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Participants", menu=participants_menu)
        participants_menu.add_command(label="View Participants", command=self._view_participants)
        participants_menu.add_command(label="Add Participant...", command=self._add_participant)
        participants_menu.add_command(label="Remove Participant...", command=self._remove_participant)

        message_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Message", menu=message_menu)
        message_menu.add_command(label="Edit Message by ID...", command=self._edit_message)
        message_menu.add_command(label="Delete Message by ID...", command=self._delete_message)

    def _update_chat_display(self):
        should_autoscroll = self.chat_display.yview()[1] > 0.99
        current_content = self.chat_display.get('1.0', tk.END).strip()

        messages = self.presenter.get_messages()
        new_content_list = []
        for msg in messages:
            # Display message ID along with other info
            new_content_list.append(
                f"[ID:{msg.id}] [{msg.timestamp.strftime('%H:%M:%S')}] {msg.name}: {msg.content}"
            )
        new_content = "\n".join(new_content_list)

        if current_content != new_content:
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete('1.0', tk.END)
            self.chat_display.insert(tk.END, new_content + '\n')
            self.chat_display.config(state=tk.DISABLED)

            if should_autoscroll:
                self.chat_display.yview(tk.END)

        self.after(1000, self._update_chat_display)

    def _on_send_message(self, event=None):
        content = self.message_input.get()
        if content.strip():
            try:
                self.presenter.add_message(self.username, content)
                self.message_input.delete(0, tk.END)
                self._update_chat_display()
                self.chat_display.yview(tk.END)
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def _add_participant(self):
        name = simpledialog.askstring("Add Participant", "Enter participant's name:")
        if name:
            self.presenter.add_participant(name)
            messagebox.showinfo("Success", f"Participant '{name}' added.")

    def _remove_participant(self):
        name = simpledialog.askstring("Remove Participant", "Enter participant's name to remove:")
        if name:
            self.presenter.remove_participant(name)
            messagebox.showinfo("Success", f"Participant '{name}' removed.")

    def _view_participants(self):
        participants = self.presenter.get_participants()
        if participants:
            messagebox.showinfo("Participants", "\n".join(participants))
        else:
            messagebox.showinfo("Participants", "No participants in the chat.")

    def _edit_message(self):
        message_id = simpledialog.askinteger("Edit Message", "Enter the ID of the message to edit:")
        if message_id is None:
            return

        message = self.presenter.get_message_by_id(message_id)
        if not message:
            messagebox.showerror("Error", f"Message with ID {message_id} not found.")
            return

        # Optional: Check if the user is allowed to edit the message
        # For this project, we allow any GUI user to edit any message.

        new_content = simpledialog.askstring(
            "Edit Message",
            "Enter the new content:",
            initialvalue=message.content
        )

        if new_content is not None:
            if messagebox.askyesno("Confirm Edit", "Are you sure you want to edit this message?"):
                self.presenter.edit_message(message_id, new_content)
                self._update_chat_display()

    def _delete_message(self):
        message_id = simpledialog.askinteger("Delete Message", "Enter the ID of the message to delete:")
        if message_id is None:
            return

        # Verify message exists before asking for confirmation
        if not self.presenter.get_message_by_id(message_id):
            messagebox.showerror("Error", f"Message with ID {message_id} not found.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to permanently delete this message?"):
            self.presenter.delete_message(message_id)
            self._update_chat_display()

    def run(self):
        self.mainloop()
