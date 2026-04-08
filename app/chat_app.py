# Main GUI chat client implementation using Tkinter

import threading
import tkinter as tk
from datetime import datetime
from tkinter import simpledialog, messagebox

from chat_client import ChatClient
from chat_ui import ChatUI

HOST = "127.0.0.1"
PORT = 5555
BUFFER_SIZE = 1024

# Locally muted usernames
muted_users = set()
muted_lock = threading.Lock()


def is_muted(username):
    """
    # Description
    Check if a username is muted locally.

    # Arguments
    username: the username to check

    # Returns
    True if the username is muted, False otherwise
    """
    with muted_lock:
        return username in muted_users


def mute_user(username):
    """
    # Description
    Add a username to the local mute list.

    # Arguments
    username: the username to mute

    # Returns
    True if successfully muted, False if already muted
    """
    with muted_lock:
        if username in muted_users:
            return False
        muted_users.add(username)
        return True


def unmute_user(username):
    """
    # Description
    Remove a username from the local mute list.

    # Arguments
    username: the username to unmute

    # Returns
    True if successfully unmuted, False if not muted
    """
    with muted_lock:
        if username not in muted_users:
            return False
        muted_users.discard(username)
        return True


def get_sender_chat(message):
    """
    # Description
    Extract the sender username from a group chat message.

    # Arguments
    message: the message string

    # Returns
    The sender username if it's a group message, None otherwise
    """
    if ": " in message and not message.startswith("["):
        return message.split(": ", 1)[0]
    return None


def get_sender_dm(message):
    """
    # Description
    Extract the sender username from a DM message.

    # Arguments
    message: the message string

    # Returns
    The sender username if it's a DM, None otherwise
    """
    if message.startswith("[DM from "):
        try:
            return message[len("[DM from ") :].split("]", 1)[0]
        except IndexError:
            return None
    return None


def main():
    """
    # Description
    Main entry point for the GUI chat client.
    """
    # Initialize the main application window and UI components
    root = tk.Tk()
    root.title("TermKaiwa 🌸")
    root.geometry("860x680")
    root.configure(bg="#FFF5F8")

    ui = ChatUI(root)
    colors = ui.colors
    view_label = ui.view_label
    public_view_btn = ui.public_view_btn
    secret_view_btn = ui.secret_view_btn
    chat_text = ui.chat_text
    entry = ui.entry
    status_label = ui.status_label
    users_container = ui.users_container
    secret_btn = ui.secret_btn
    users_refresh = ui.users_refresh
    connect_btn = ui.connect_btn
    disconnect_btn = ui.disconnect_btn
    users_btn = ui.users_btn
    dm_btn = ui.dm_btn
    rename_btn = ui.rename_btn
    mute_btn = ui.mute_btn
    quit_btn = ui.quit_btn
    send_button = ui.send_button

    # Client Implementation Section
    client = ChatClient(HOST, PORT, BUFFER_SIZE)
    username = None
    in_secret = False
    connected = False
    current_view = "public"
    histories = {"public": [], "secret": []}
    # Keep a per-view history so switching tabs redraws correctly.
    refresh_job = None  # Tkinter after() job id

    def get_message_parts(text, tag):
        """
        # Description
        Parse a message into sender, body, and sender tag for display formatting.

        # Arguments
        text: the message text
        tag: the message tag (e.g., "chat", "dm_in")

        # Returns
        A tuple of (sender, body, sender_tag) or (None, text, None) if not parsed
        """
        if tag == "join_leave":
            return None, text, None
        if tag == "you" and text.startswith("[You] "):
            return "You", text[len("[You] ") :], "you_sender"
        if tag == "dm_in" and text.startswith("[DM from "):
            sender, body = text.split("] ", 1)
            return f"DM from {sender[1:]}", body, "dm_in_sender"
        if tag == "dm_out" and text.startswith("[DM to "):
            sender, body = text.split("] ", 1)
            return f"To {sender[1:]}", body, "dm_out_sender"
        if tag == "chat":
            sender = get_sender_chat(text)
            if sender is not None:
                body = text.split(": ", 1)[1]
                return sender, body, "chat_sender"
        return None, text, None

    def current_timestamp():
        """
        # Description
        Get the current time formatted as HH:MM.

        # Returns
        A string representing the current time in HH:MM format
        """
        return datetime.now().strftime("%H:%M")

    def insert_history_item(item):
        """
        # Description
        Insert a message item into the chat text widget with proper formatting.

        # Arguments
        item: a dictionary with 'text', 'tag', and 'timestamp' keys
        """
        text = item["text"]
        tag = item["tag"]
        timestamp = item["timestamp"]
        sender, body, sender_tag = get_message_parts(text, tag)
        if sender and sender_tag:
            chat_text.insert(tk.END, sender + "\n", sender_tag)
        chat_text.insert(tk.END, body + "\n", tag)
        chat_text.insert(tk.END, timestamp + "\n", f"{tag}_time")

    def insert_message(text, tag):
        """
        # Description
        Insert a message into the chat text widget and scroll to the end.

        # Arguments
        text: the message text
        tag: the tag for styling the message
        """
        chat_text.config(state=tk.NORMAL)
        insert_history_item(
            {
                "text": text,
                "tag": tag,
                "timestamp": current_timestamp(),
            }
        )
        chat_text.see(tk.END)
        chat_text.config(state=tk.DISABLED)

    def set_status(text):
        """
        # Description
        Update the status label text.

        # Arguments
        text: the new status text
        """
        status_label.config(text=f"Status: {text}")

    def append_history(view_key, text, tag):
        """
        # Description
        Append a message to the history for a specific view.

        # Arguments
        view_key: the key for the view (e.g., "public", "dm:user")
        text: the message text
        tag: the message tag
        """
        history = histories.setdefault(view_key, [])
        history.append(
            {
                "text": text,
                "tag": tag,
                "timestamp": current_timestamp(),
            }
        )
        # Limit history size to keep UI snappy.
        if len(history) > 200:
            del history[: len(history) - 200]

    def render_view(view_key):
        """
        # Description
        Render the chat history for a specific view in the text widget.

        # Arguments
        view_key: the key for the view to render
        """
        chat_text.config(state=tk.NORMAL)
        chat_text.delete("1.0", tk.END)
        for item in histories.get(view_key, []):
            insert_history_item(item)
        chat_text.see(tk.END)
        chat_text.config(state=tk.DISABLED)

    def set_view(view_key):
        """
        # Description
        Set the current view to the specified view key, update UI labels, and render the view.

        # Arguments
        view_key: the key for the view to set (e.g., 'public', 'secret', 'dm:user')
        """
        nonlocal current_view
        if view_key == "secret" and not in_secret:
            insert_message("[LOCAL] Enter secret room first. 🌼", "local")
            return
        current_view = view_key
        if view_key.startswith("dm:"):
            dm_user = view_key.split(":", 1)[1]
            view_label.config(text=f"Now chatting: DM with {dm_user}")
        elif view_key == "secret":
            view_label.config(text="Now chatting: Secret Room")
        else:
            view_label.config(text="Now chatting: Public")
        render_view(view_key)

    def print_message(message):
        """
        # Description
        Process and display incoming messages from the server, handling different message types.

        # Arguments
        message: the message string received from the server
        """
        nonlocal in_secret, username

        # Helper functions to identify message types for special handling
        def is_command_help_line(line):
            trimmed = line.strip()
            if trimmed.startswith("[SERVER] Commands:"):
                return True
            if trimmed.startswith("/"):
                return True
            return False

        # Check if line is a history header
        def is_history_header(line):
            trimmed = line.strip()
            return trimmed.startswith(
                "[SERVER] Last 15 public messages:"
            ) or trimmed.startswith("[SERVER] Last 15 secret messages:")

        # Check if line is a welcome message
        def is_welcome_line(line):
            return line.strip().startswith("[SERVER] Welcome,")

        # Route messages by type: DM, server notice, join/leave, or normal chat.
        dm_sender = get_sender_dm(message)

        if dm_sender is not None:
            if is_muted(dm_sender):
                return
            view_key = f"dm:{dm_sender}"
            append_history(view_key, message, "dm_in")
            if current_view == view_key:
                insert_message(message, "dm_in")
            else:
                append_history(
                    current_view, f"[LOCAL] New DM from {dm_sender} 🌸", "local"
                )
                if current_view == "public" or current_view == "secret":
                    render_view(current_view)
            return

        if message.startswith("[DM to "):
            target = message[len("[DM to ") :].split("]", 1)[0]
            view_key = f"dm:{target}"
            append_history(view_key, message, "dm_out")
            if current_view == view_key:
                insert_message(message, "dm_out")
            return

        if message.startswith("[You]"):
            append_history(current_view, message, "you")
            if (
                current_view == "public"
                or current_view == "secret"
                or current_view.startswith("dm:")
            ):
                insert_message(message, "you")
            return

        if message.startswith("***") and message.endswith("***"):
            append_history("public", message, "join_leave")
            if current_view == "public":
                insert_message(message, "join_leave")
            return

        if message.startswith("[SERVER]"):
            if "\n" in message:
                if message.startswith("[SERVER] Online users:"):
                    users = message.split(":", 1)[1].strip()
                    update_user_list(users)
                for line in message.split("\n"):
                    if (
                        is_command_help_line(line)
                        or is_history_header(line)
                        or is_welcome_line(line)
                    ):
                        continue
                    if any(
                        kw in line
                        for kw in (
                            "not found",
                            "Wrong",
                            "cannot",
                            "already",
                            "Usage",
                            "Error",
                        )
                    ):
                        append_history("public", line, "error")
                        if current_view == "public":
                            insert_message(line, "error")
                    else:
                        append_history("public", line, "server")
                        if current_view == "public":
                            insert_message(line, "server")

            elif any(
                kw in message
                for kw in (
                    "not found",
                    "Wrong",
                    "cannot",
                    "already",
                    "Usage",
                    "Error",
                )
            ):
                append_history("public", message, "error")
                if current_view == "public":
                    insert_message(message, "error")
            elif (
                is_command_help_line(message)
                or is_history_header(message)
                or is_welcome_line(message)
            ):
                return

            elif message.startswith("[SERVER] Online users:"):
                users = message.split(":", 1)[1].strip()
                update_user_list(users)

            elif message.startswith("[SERVER] Username changed to "):
                new_name = message[
                    len("[SERVER] Username changed to ") :
                ].strip()
                if new_name.endswith("."):
                    new_name = new_name[:-1]
                if new_name:
                    username = new_name
                    set_status(f"Connected as {username}")
                    show_users()
                append_history("public", message, "server")
                if current_view == "public":
                    insert_message(message, "server")

            elif message == "[SERVER] Entered the secret room.":
                in_secret = True
                secret_btn.config(text="🔓 Leave Secret")
                secret_view_btn.config(state=tk.NORMAL)
                public_view_btn.config(state=tk.DISABLED)
                set_view("secret")
                # Show secret history if any
                secret_history = histories.get("secret", [])
                if secret_history:
                    insert_message(
                        "[SERVER] Last 15 secret messages:\n"
                        + "\n".join(secret_history),
                        "server",
                    )

            elif message == "[SERVER] Left the secret room.":
                in_secret = False
                secret_btn.config(text="🔒 Secret")
                secret_view_btn.config(state=tk.DISABLED)
                public_view_btn.config(state=tk.NORMAL)
                set_view("public")

            elif message == "[SERVER] Wrong password.":
                in_secret = False
                secret_btn.config(text="🔒 Secret")
                secret_view_btn.config(state=tk.DISABLED)
                public_view_btn.config(state=tk.NORMAL)
                set_view("public")
            else:
                append_history("public", message, "server")
                if current_view == "public":
                    insert_message(message, "server")
            return
        chat_sender = get_sender_chat(message)

        # For normal chat messages, check if the sender is muted and route to the appropriate view.
        if chat_sender is not None:
            if is_muted(chat_sender):
                return
            room_key = "secret" if in_secret else "public"
            append_history(room_key, message, "chat")
            if current_view == room_key:
                insert_message(message, "chat")
            return
        room_key = "secret" if in_secret else "public"
        append_history(room_key, message, "chat")
        if current_view == room_key:
            insert_message(message, "chat")

    def connect_flow():
        """
        # Description
        Handle the connection process: get username, connect to server, start receiving messages.
        """
        nonlocal username, connected
        if connected:
            insert_message("[LOCAL] Already connected. 🌼", "local")
            return
        uname = simpledialog.askstring(
            "Welcome! 🎉", "Enter your username: 😊", parent=root
        )
        if not uname:
            return
        response, ok = client.connect(uname.strip())
        if not ok:
            messagebox.showerror(
                "Oops! 😞",
                "Invalid username or connection failed. Try again.",
            )
            return
        root.after(0, lambda: print_message(response))
        username = uname.strip()
        connected = True
        set_status(f"Connected as {username}")
        start_receiver()
        show_users()
        start_auto_refresh()

    def disconnect_flow():
        """
        # Description
        Handle the disconnection process: send quit command, close socket, reset state.
        """
        nonlocal connected, in_secret
        if not connected:
            insert_message("[LOCAL] Not connected. 🌼", "local")
            return
        try:
            client.send("/quit")
        except:
            pass
        client.close()
        connected = False
        in_secret = False
        secret_btn.config(text="🔒 Secret")
        secret_view_btn.config(state=tk.DISABLED)
        set_status("Disconnected")
        set_view("public")
        stop_auto_refresh()

    def send_message():
        """
        # Description
        Send a message to the server based on the current view (public, secret, or DM).
        """
        if not connected or not client.is_connected():
            insert_message("[LOCAL] Connect first. 🌼", "local")
            return
        message = entry.get().strip()
        entry.delete(0, tk.END)
        if not message:
            return
        try:
            if current_view.startswith("dm:"):
                target = current_view.split(":", 1)[1]
                client.send(f"/dm {target} {message}")
            else:
                client.send(message)
        except:
            insert_message("[ERROR] Failed to send message.", "error")

    def show_users():
        """
        # Description
        Request the list of online users from the server.
        """
        if not connected or not client.is_connected():
            insert_message("[LOCAL] Connect first. 🌼", "local")
            return
        try:
            client.send("/users")
        except:
            insert_message("[ERROR] Failed to get users.", "error")

    def update_user_list(users_line):
        """
        # Description
        Update the user list display with the received user list.

        # Arguments
        users_line: the string containing the list of users
        """
        # Clear existing labels
        for widget in users_container.winfo_children():
            widget.destroy()

        if users_line == "No users connected." or users_line == "":
            return

        # Process user list and prioritize current user at the top
        user_list = [u.strip() for u in users_line.split(",") if u.strip()]
        if username and username in user_list:
            user_list.remove(username)
            user_list.insert(0, f"{username} (You)")

        for user in user_list:
            if user.endswith(" (You)"):
                fg = colors["text"]
                font = ("Comic Sans MS", 10, "bold")
            else:
                fg = colors["text"]
                font = ("Comic Sans MS", 10)

            label = tk.Label(
                users_container,
                text=user,
                bg=colors["white"],
                fg=fg,
                font=font,
                anchor="w",
                padx=5,
                pady=1,
            )
            label.pack(fill=tk.X)
            # Bind double-click to open DM
            clean_user = user.replace(" (You)", "")
            label.bind(
                "<Double-Button-1>",
                lambda e, u=clean_user: open_dm_from_list(u),
            )

    def start_auto_refresh():
        """
        # Description
        Start the automatic refresh of the user list every 5 seconds.
        """
        nonlocal refresh_job

        def refresh():
            nonlocal refresh_job
            if connected and client.is_connected():
                show_users()
            refresh_job = root.after(5000, refresh)  # 5 seconds

        refresh_job = root.after(5000, refresh)

    def stop_auto_refresh():
        """
        # Description
        Stop the automatic refresh of the user list.
        """
        nonlocal refresh_job
        if refresh_job:
            root.after_cancel(refresh_job)
            refresh_job = None

    def send_dm():
        """
        # Description
        Open a dialog to select a user to DM and switch to DM view.
        """
        if not connected or not client.is_connected():
            insert_message("[LOCAL] Connect first. 🌼", "local")
            return
        target = simpledialog.askstring(
            "DM", "Enter username to DM:", parent=root
        )
        if not target:
            return
        target = target.strip()
        if not target:
            return
        # Check if user exists
        users = []
        for child in users_container.winfo_children():
            if isinstance(child, tk.Label):
                text = child.cget("text")
                if text.endswith(" (You)"):
                    text = text[:-6]  # remove " (You)"
                users.append(text)
        if target not in users:
            messagebox.showerror(
                "Invalid User 😞", f"User '{target}' not found."
            )
            return
        if target == username:
            messagebox.showerror("Invalid", "You cannot DM yourself. 😊")
            return
        set_view(f"dm:{target}")

    def rename_user():
        """
        # Description
        Open a dialog to change the username.
        """
        if not connected or not client.is_connected():
            insert_message("[LOCAL] Connect first. 🌼", "local")
            return
        new_name = simpledialog.askstring(
            "Rename", "Enter new username:", parent=root
        )
        if not new_name:
            return
        try:
            client.send(f"/rename {new_name}")
        except:
            insert_message("[ERROR] Failed to rename.", "error")

    def toggle_secret():
        """
        # Description
        Toggle between entering and leaving the secret room based on the current state.
        """
        if not connected or not client.is_connected():
            insert_message("[LOCAL] Connect first. 🌼", "local")
            return
        if in_secret:
            try:
                client.send("/secret_leave")
            except:
                insert_message("[ERROR] Failed to leave secret.", "error")
        else:
            pwd = simpledialog.askstring(
                "Secret Room", "Enter password:", parent=root, show="*"
            )
            if not pwd:
                return
            try:
                client.send(f"/secret {pwd}")
            except:
                insert_message("[ERROR] Failed to enter secret.", "error")

    def toggle_mute():
        """
        # Description
        Toggle the mute status of a user.
        """
        if not connected or not client.is_connected():
            insert_message("[LOCAL] Connect first. 🌼", "local")
            return
        target = simpledialog.askstring(
            "Mute/Unmute", "Enter username to mute/unmute:", parent=root
        )
        if not target:
            return
        if is_muted(target):
            if unmute_user(target):
                insert_message(
                    f"[LOCAL] {target} has been unmuted. 🌼", "local"
                )
            else:
                insert_message(f"[LOCAL] {target} is not muted.", "local")
        else:
            if mute_user(target):
                insert_message(f"[LOCAL] {target} has been muted. 🌙", "local")
            else:
                insert_message(f"[LOCAL] {target} is already muted.", "local")

    def quit_app():
        """
        # Description
        Quit the application and close the connection to the server.
        """
        if connected and client.is_connected():
            try:
                client.send("/quit")
                client.close()
            except:
                pass
        root.quit()

    root.protocol("WM_DELETE_WINDOW", quit_app)

    def start_receiver():
        """
        # Description
        Start the background thread to receive messages from the server and handle them with callbacks.
        """

        def on_message(raw_message):
            for line in raw_message.splitlines():
                line = line.strip()
                if not line:
                    continue
                # Tkinter updates must run on the UI thread.
                root.after(0, lambda msg=line: print_message(msg))

        def on_disconnect():
            """
            # Description
            Handle the disconnection event by updating the UI and status.
            """
            root.after(
                0,
                lambda: insert_message(
                    "👋 [SERVER] Connection closed.", "error"
                ),
            )
            root.after(0, lambda: set_status("Disconnected"))

        client.start_receiver(on_message, on_disconnect)

    def open_dm_from_list(target):
        if target:
            set_view(f"dm:{target}")

    public_view_btn.config(command=lambda: set_view("public"))
    secret_view_btn.config(command=lambda: set_view("secret"))
    users_btn.config(command=show_users)
    dm_btn.config(command=send_dm)
    rename_btn.config(command=rename_user)
    secret_btn.config(command=toggle_secret)
    mute_btn.config(command=toggle_mute)
    quit_btn.config(command=quit_app)
    send_button.config(command=send_message)
    connect_btn.config(command=connect_flow)
    disconnect_btn.config(command=disconnect_flow)
    users_refresh.config(command=show_users)
    entry.bind("<Return>", lambda e: send_message())

    secret_view_btn.config(state=tk.DISABLED)

    root.mainloop()


if __name__ == "__main__":
    main()
