import socket
import threading
import tkinter as tk
from datetime import datetime
from tkinter import simpledialog, messagebox, ttk

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
    root = tk.Tk()
    root.title("TermKaiwa 🌸")
    root.geometry("860x680")
    root.configure(bg="#FFF5F8")

    colors = {
        "bg": "#FFF5F8",
        "panel": "#FFE6F0",
        "accent": "#FFB3C7",
        "accent_dark": "#FF7AA2",
        "mint": "#D8F8E1",
        "mint_dark": "#7BD88F",
        "lavender": "#F1E7FF",
        "sky": "#E8F6FF",
        "cream": "#FFF7E3",
        "text": "#3B3B3B",
        "white": "#FFFFFF",
        "shadow": "#F7C6D6",
        "line_bg": "#F7F4EE",
    }

    root.option_add("*Button.borderWidth", 0)
    root.option_add("*Button.highlightThickness", 0)
    root.option_add("*Entry.highlightThickness", 0)
    root.option_add("*Listbox.highlightThickness", 0)
    root.option_add("*Text.highlightThickness", 0)
    root.option_add("*Scrollbar.borderWidth", 0)

    def make_button(parent, text, command, bg, fg, font):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=colors["panel"],
            activeforeground=fg,
            font=font,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            highlightbackground=colors["panel"],
            highlightcolor=colors["panel"],
            takefocus=0,
            overrelief=tk.FLAT,
        )

    # Top banner
    # Banner Section
    banner = tk.Frame(root, bg=colors["panel"], highlightthickness=0, bd=0)
    banner.pack(fill=tk.X, padx=12, pady=(12, 6))

    title = tk.Label(
        banner,
        text="TermKaiwa",
        bg=colors["panel"],
        fg=colors["accent_dark"],
        font=("Comic Sans MS", 18, "bold"),
    )
    subtitle = tk.Label(
        banner,
        text="Tiny chat app 🌷",
        bg=colors["panel"],
        fg=colors["text"],
        font=("Comic Sans MS", 10),
    )

    flower_canvas = tk.Canvas(
        banner,
        width=120,
        height=42,
        bg=colors["panel"],
        highlightthickness=0,
    )

    def draw_flower(canvas, x, y, petal, center, scale=1.0):
        r = 7 * scale
        canvas.create_oval(x - r, y - r, x + r, y + r, fill=center, outline="")
        offsets = [(-10, 0), (10, 0), (0, -10), (0, 10)]
        for dx, dy in offsets:
            canvas.create_oval(
                x + dx - r,
                y + dy - r,
                x + dx + r,
                y + dy + r,
                fill=petal,
                outline="",
            )

    draw_flower(flower_canvas, 20, 20, "#FFC6DD", "#FFDF6E", 0.9)
    draw_flower(flower_canvas, 55, 18, "#CDE7FF", "#FFD9F0", 0.8)
    draw_flower(flower_canvas, 90, 22, "#EAD7FF", "#FFE8A3", 0.95)

    title.pack(anchor="w", padx=10, pady=(6, 0))
    subtitle.pack(anchor="w", padx=10, pady=(0, 6))
    flower_canvas.pack(side=tk.RIGHT, padx=10, pady=6)

    # Main Layout Section
    main_frame = tk.Frame(root, bg=colors["bg"], highlightthickness=0, bd=0)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 6))

    left_panel = tk.Frame(
        main_frame, bg=colors["bg"], highlightthickness=0, bd=0
    )
    right_panel = tk.Frame(
        main_frame,
        bg=colors["panel"],
        width=220,
        relief=tk.FLAT,
        highlightthickness=0,
        bd=0,
    )
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    right_panel.pack(side=tk.RIGHT, fill=tk.Y)

    # View Selector Section
    view_frame = tk.Frame(
        left_panel, bg=colors["bg"], highlightthickness=0, bd=0
    )
    view_label = tk.Label(
        view_frame,
        text="Now chatting: Public",
        bg=colors["bg"],
        fg=colors["accent_dark"],
        font=("Comic Sans MS", 10, "bold"),
    )
    public_view_btn = make_button(
        view_frame,
        "🌸 Public",
        lambda: set_view("public"),
        colors["accent"],
        colors["text"],
        ("Comic Sans MS", 9),
    )
    secret_view_btn = make_button(
        view_frame,
        "🔒 Secret",
        lambda: set_view("secret"),
        colors["accent"],
        colors["text"],
        ("Comic Sans MS", 9),
    )
    view_label.pack(side=tk.LEFT, padx=(2, 8))
    public_view_btn.pack(side=tk.LEFT, padx=4)
    secret_view_btn.pack(side=tk.LEFT, padx=4)
    view_frame.pack(fill=tk.X, padx=2, pady=(0, 6))

    # Chat Display Area Section
    frame = tk.Frame(left_panel, bg=colors["bg"], highlightthickness=0, bd=0)
    chat_text = tk.Text(
        frame,
        wrap=tk.WORD,
        state=tk.DISABLED,
        bg=colors["line_bg"],
        fg=colors["text"],
        font=("Comic Sans MS", 10),
        padx=14,
        pady=14,
        relief=tk.FLAT,
        bd=0,
        highlightthickness=0,
        highlightbackground=colors["line_bg"],
    )
    scrollbar = tk.Scrollbar(
        frame,
        command=chat_text.yview,
        relief=tk.FLAT,
        bd=0,
        highlightthickness=0,
    )
    chat_text.config(yscrollcommand=scrollbar.set)
    chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=(2, 10))

    # Configure tags for styling
    chat_text.tag_configure(
        "server",
        foreground=colors["accent_dark"],
        background=colors["panel"],
        font=("Comic Sans MS", 9, "bold"),
        spacing1=10,
        spacing3=10,
        lmargin1=180,
        lmargin2=180,
        rmargin=180,
        justify=tk.CENTER,
    )
    chat_text.tag_configure(
        "server_time",
        foreground="#C7899B",
        background=colors["panel"],
        font=("Comic Sans MS", 8),
        spacing1=0,
        spacing3=10,
        lmargin1=180,
        lmargin2=180,
        rmargin=180,
        justify=tk.CENTER,
    )
    chat_text.tag_configure(
        "you_sender",
        foreground="#3F8D54",
        background=colors["mint"],
        font=("Comic Sans MS", 8, "bold"),
        spacing1=10,
        spacing3=0,
        lmargin1=280,
        lmargin2=280,
        rmargin=24,
        justify=tk.RIGHT,
    )
    chat_text.tag_configure(
        "you",
        foreground=colors["mint_dark"],
        background=colors["mint"],
        font=("Comic Sans MS", 11, "bold"),
        spacing1=2,
        spacing3=2,
        lmargin1=280,
        lmargin2=280,
        rmargin=24,
        justify=tk.RIGHT,
    )
    chat_text.tag_configure(
        "you_time",
        foreground="#5AA06A",
        background=colors["mint"],
        font=("Comic Sans MS", 8),
        spacing1=0,
        spacing3=10,
        lmargin1=280,
        lmargin2=280,
        rmargin=24,
        justify=tk.RIGHT,
    )
    chat_text.tag_configure(
        "dm_in",
        foreground="#7A4DD8",
        background=colors["lavender"],
        font=("Comic Sans MS", 11),
        spacing1=2,
        spacing3=2,
        lmargin1=24,
        lmargin2=24,
        rmargin=280,
    )
    chat_text.tag_configure(
        "dm_in_sender",
        foreground="#6B44BB",
        background=colors["lavender"],
        font=("Comic Sans MS", 8, "bold"),
        spacing1=10,
        spacing3=0,
        lmargin1=24,
        lmargin2=24,
        rmargin=280,
    )
    chat_text.tag_configure(
        "dm_in_time",
        foreground="#9C7EDB",
        background=colors["lavender"],
        font=("Comic Sans MS", 8),
        spacing1=0,
        spacing3=10,
        lmargin1=24,
        lmargin2=24,
        rmargin=280,
    )
    chat_text.tag_configure(
        "dm_out",
        foreground="#7A4DD8",
        background=colors["lavender"],
        font=("Comic Sans MS", 11),
        spacing1=2,
        spacing3=2,
        lmargin1=280,
        lmargin2=280,
        rmargin=24,
        justify=tk.RIGHT,
    )
    chat_text.tag_configure(
        "dm_out_sender",
        foreground="#6B44BB",
        background=colors["lavender"],
        font=("Comic Sans MS", 8, "bold"),
        spacing1=10,
        spacing3=0,
        lmargin1=280,
        lmargin2=280,
        rmargin=24,
        justify=tk.RIGHT,
    )
    chat_text.tag_configure(
        "dm_out_time",
        foreground="#9C7EDB",
        background=colors["lavender"],
        font=("Comic Sans MS", 8),
        spacing1=0,
        spacing3=10,
        lmargin1=280,
        lmargin2=280,
        rmargin=24,
        justify=tk.RIGHT,
    )
    chat_text.tag_configure(
        "join_leave",
        foreground="#C27700",
        background=colors["cream"],
        font=("Comic Sans MS", 9, "bold"),
        spacing1=10,
        spacing3=10,
        lmargin1=210,
        lmargin2=210,
        rmargin=210,
        justify=tk.CENTER,
    )
    chat_text.tag_configure(
        "join_leave_time",
        foreground="#D39C46",
        background=colors["cream"],
        font=("Comic Sans MS", 8),
        spacing1=0,
        spacing3=10,
        lmargin1=210,
        lmargin2=210,
        rmargin=210,
        justify=tk.CENTER,
    )
    chat_text.tag_configure(
        "error",
        foreground="#B00020",
        background="#FFE5EA",
        font=("Comic Sans MS", 9, "bold"),
        spacing1=10,
        spacing3=10,
        lmargin1=170,
        lmargin2=170,
        rmargin=170,
        justify=tk.CENTER,
    )
    chat_text.tag_configure(
        "error_time",
        foreground="#CC6B7F",
        background="#FFE5EA",
        font=("Comic Sans MS", 8),
        spacing1=0,
        spacing3=10,
        lmargin1=170,
        lmargin2=170,
        rmargin=170,
        justify=tk.CENTER,
    )
    chat_text.tag_configure(
        "chat",
        foreground=colors["text"],
        background=colors["sky"],
        font=("Comic Sans MS", 11),
        spacing1=2,
        spacing3=2,
        lmargin1=24,
        lmargin2=24,
        rmargin=280,
    )
    chat_text.tag_configure(
        "chat_sender",
        foreground="#53748C",
        background=colors["sky"],
        font=("Comic Sans MS", 8, "bold"),
        spacing1=10,
        spacing3=0,
        lmargin1=24,
        lmargin2=24,
        rmargin=280,
    )
    chat_text.tag_configure(
        "chat_time",
        foreground="#6F8B9B",
        background=colors["sky"],
        font=("Comic Sans MS", 8),
        spacing1=0,
        spacing3=10,
        lmargin1=24,
        lmargin2=24,
        rmargin=280,
    )
    chat_text.tag_configure(
        "local",
        foreground="#0D7F87",
        background="#D9FEFF",
        font=("Comic Sans MS", 9, "bold"),
        spacing1=10,
        spacing3=10,
        lmargin1=170,
        lmargin2=170,
        rmargin=170,
        justify=tk.CENTER,
    )
    chat_text.tag_configure(
        "local_time",
        foreground="#5FA8AD",
        background="#D9FEFF",
        font=("Comic Sans MS", 8),
        spacing1=0,
        spacing3=10,
        lmargin1=170,
        lmargin2=170,
        rmargin=170,
        justify=tk.CENTER,
    )

    # Toolbar Section
    toolbar = tk.Frame(left_panel, bg=colors["bg"], highlightthickness=0, bd=0)
    users_btn = make_button(
        toolbar,
        "👥 Users",
        lambda: show_users(),
        colors["accent"],
        colors["text"],
        ("Comic Sans MS", 9),
    )
    dm_btn = make_button(
        toolbar,
        "💌 DM",
        lambda: send_dm(),
        colors["accent"],
        colors["text"],
        ("Comic Sans MS", 9),
    )
    rename_btn = make_button(
        toolbar,
        "✏️ Rename",
        lambda: rename_user(),
        colors["accent"],
        colors["text"],
        ("Comic Sans MS", 9),
    )
    secret_btn = make_button(
        toolbar,
        "🔒 Secret",
        lambda: toggle_secret(),
        colors["accent"],
        colors["text"],
        ("Comic Sans MS", 9),
    )
    mute_btn = make_button(
        toolbar,
        "🔇 Mute",
        lambda: toggle_mute(),
        colors["accent"],
        colors["text"],
        ("Comic Sans MS", 9),
    )
    quit_btn = make_button(
        toolbar,
        "👋 Quit",
        lambda: quit_app(),
        colors["accent"],
        colors["text"],
        ("Comic Sans MS", 9),
    )
    users_btn.pack(side=tk.LEFT, padx=5, pady=5)
    dm_btn.pack(side=tk.LEFT, padx=5, pady=5)
    rename_btn.pack(side=tk.LEFT, padx=5, pady=5)
    secret_btn.pack(side=tk.LEFT, padx=5, pady=5)
    mute_btn.pack(side=tk.LEFT, padx=5, pady=5)
    quit_btn.pack(side=tk.LEFT, padx=5, pady=5)
    toolbar.pack(fill=tk.X)

    # Bottom Input Area Section
    bottom_frame = tk.Frame(
        left_panel, bg=colors["bg"], highlightthickness=0, bd=0
    )
    entry = tk.Entry(
        bottom_frame,
        font=("Comic Sans MS", 10),
        relief=tk.FLAT,
        bg=colors["white"],
        fg=colors["text"],
        insertbackground=colors["accent_dark"],
        bd=0,
        highlightthickness=0,
        highlightbackground=colors["white"],
    )
    send_button = make_button(
        bottom_frame,
        "📤 Send",
        lambda: send_message(),
        colors["mint"],
        colors["text"],
        ("Comic Sans MS", 10, "bold"),
    )
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
    send_button.pack(side=tk.RIGHT, padx=5, pady=5)
    bottom_frame.pack(fill=tk.X, padx=2, pady=(0, 10))

    # Bind Enter to send
    entry.bind("<Return>", lambda e: send_message())

    # Right Panel Section
    status_frame = tk.Frame(
        right_panel, bg=colors["panel"], highlightthickness=0, bd=0
    )
    status_frame.pack(fill=tk.X, padx=10, pady=(10, 4))

    status_label = tk.Label(
        status_frame,
        text="Status: Disconnected",
        bg=colors["panel"],
        fg=colors["text"],
        font=("Comic Sans MS", 10, "bold"),
    )
    status_label.pack(anchor="w")

    connect_btn = make_button(
        status_frame,
        "🔌 Connect",
        lambda: connect_flow(),
        colors["accent"],
        colors["text"],
        ("Comic Sans MS", 9),
    )
    disconnect_btn = make_button(
        status_frame,
        "⛔ Disconnect",
        lambda: disconnect_flow(),
        colors["accent"],
        colors["text"],
        ("Comic Sans MS", 9),
    )
    connect_btn.pack(fill=tk.X, pady=(6, 2))
    disconnect_btn.pack(fill=tk.X, pady=(2, 0))

    users_frame = tk.Frame(
        right_panel, bg=colors["panel"], highlightthickness=0, bd=0
    )
    users_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

    users_title = tk.Label(
        users_frame,
        text="Online Users",
        bg=colors["panel"],
        fg=colors["accent_dark"],
        font=("Comic Sans MS", 10, "bold"),
    )
    users_title.pack(anchor="w", pady=(0, 4))

    users_container = tk.Frame(
        users_frame,
        bg=colors["white"],
        relief=tk.FLAT,
        bd=0,
        highlightthickness=0,
    )
    users_container.pack(fill=tk.BOTH, expand=True)

    users_refresh = make_button(
        users_frame,
        "🔄 Refresh",
        lambda: show_users(),
        colors["accent"],
        colors["text"],
        ("Comic Sans MS", 9),
    )
    users_refresh.pack(fill=tk.X, pady=(6, 0))

    # Client Implementation Section
    client_socket = None
    username = None
    in_secret = False
    connected = False
    current_view = "public"
    current_dm_user = None
    histories = {"public": [], "secret": []}
    refresh_job = None

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
        nonlocal current_view, current_dm_user
        if view_key == "secret" and not in_secret:
            insert_message("[LOCAL] Enter secret room first. 🌼", "local")
            return
        current_view = view_key
        current_dm_user = None
        if view_key.startswith("dm:"):
            current_dm_user = view_key.split(":", 1)[1]
            view_label.config(text=f"Now chatting: DM with {current_dm_user}")
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
        nonlocal in_secret

        def is_command_help_line(line):
            trimmed = line.strip()
            if trimmed.startswith("[SERVER] Commands:"):
                return True
            if trimmed.startswith("/"):
                return True
            return False

        def is_history_header(line):
            trimmed = line.strip()
            return trimmed.startswith(
                "[SERVER] Last 15 public messages:"
            ) or trimmed.startswith("[SERVER] Last 15 secret messages:")

        def is_welcome_line(line):
            return line.strip().startswith("[SERVER] Welcome,")

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
            elif message == "[SERVER] Entered the secret room.":
                in_secret = True
                secret_btn.config(text="🔓 Leave Secret")
                secret_view_btn.config(state=tk.NORMAL)
                public_view_btn.config(state=tk.DISABLED)
                set_view("secret")
                # Show secret history if any
                secret_history = histories.get("secret", [])
                if secret_history:
                    insert_message("[SERVER] Last 15 secret messages:\n" + "\n".join(secret_history), "server")
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

    def connect(uname):
        """
        # Description
        Attempt to connect to the server with the given username.

        # Arguments
        uname: the username to connect with

        # Returns
        socket object if connection successful, None otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, PORT))
            sock.sendall(uname.encode())
            response = sock.recv(BUFFER_SIZE).decode()
            root.after(0, lambda: print_message(response))
            if "Welcome" in response:
                return sock
            else:
                sock.close()
                return None
        except:
            return None

    def connect_flow():
        """
        # Description
        Handle the connection process: get username, connect to server, start receiving messages.
        """
        nonlocal client_socket, username, connected
        if connected:
            insert_message("[LOCAL] Already connected. 🌼", "local")
            return
        uname = simpledialog.askstring(
            "Welcome! 🎉", "Enter your username: 😊", parent=root
        )
        if not uname:
            return
        client_socket = connect(uname.strip())
        if not client_socket:
            messagebox.showerror(
                "Oops! 😞",
                "Invalid username or connection failed. Try again.",
            )
            return
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
        nonlocal client_socket, connected, in_secret
        if not connected:
            insert_message("[LOCAL] Not connected. 🌼", "local")
            return
        try:
            client_socket.sendall("/quit".encode())
        except:
            pass
        try:
            client_socket.close()
        except:
            pass
        client_socket = None
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
        if not client_socket:
            insert_message("[LOCAL] Connect first. 🌼", "local")
            return
        message = entry.get().strip()
        entry.delete(0, tk.END)
        if not message:
            return
        try:
            if current_view.startswith("dm:"):
                target = current_view.split(":", 1)[1]
                client_socket.sendall(f"/dm {target} {message}".encode())
            else:
                client_socket.sendall(message.encode())
        except:
            insert_message("[ERROR] Failed to send message.", "error")

    def show_users():
        """
        # Description
        Request the list of online users from the server.
        """
        if not client_socket:
            insert_message("[LOCAL] Connect first. 🌼", "local")
            return
        try:
            client_socket.sendall("/users".encode())
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
        
        user_list = [u.strip() for u in users_line.split(",") if u.strip()]
        if username and username in user_list:
            user_list.remove(username)
            user_list.insert(0, f"{username} (You)")
        
        for user in user_list:
            if user.endswith(" (You)"):
                fg = colors["accent_dark"]
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
                pady=1
            )
            label.pack(fill=tk.X)
            # Bind double-click to open DM
            clean_user = user.replace(" (You)", "")
            label.bind("<Double-Button-1>", lambda e, u=clean_user: open_dm_from_list(u))

    def start_auto_refresh():
        """
        # Description
        Start the automatic refresh of the user list every 5 seconds.
        """
        nonlocal refresh_job
        def refresh():
            nonlocal refresh_job
            if connected and client_socket:
                show_users()
            refresh_job = root.after(5000, refresh)  # 5 seconds
        refresh_job = root.after(5000, refresh)

    def stop_auto_refresh():
        nonlocal refresh_job
        if refresh_job:
            root.after_cancel(refresh_job)
            refresh_job = None

    def send_dm():
        """
        # Description
        Open a dialog to select a user to DM and switch to DM view.
        """
        if not client_socket:
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
            messagebox.showerror("Invalid User 😞", f"User '{target}' not found.")
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
        if not client_socket:
            insert_message("[LOCAL] Connect first. 🌼", "local")
            return
        new_name = simpledialog.askstring(
            "Rename", "Enter new username:", parent=root
        )
        if not new_name:
            return
        try:
            client_socket.sendall(f"/rename {new_name}".encode())
        except:
            insert_message("[ERROR] Failed to rename.", "error")

    def toggle_secret():
        nonlocal in_secret
        if not client_socket:
            insert_message("[LOCAL] Connect first. 🌼", "local")
            return
        if in_secret:
            try:
                client_socket.sendall("/secret_leave".encode())
                in_secret = False
                secret_btn.config(text="🔒 Secret")
                secret_view_btn.config(state=tk.DISABLED)
                public_view_btn.config(state=tk.NORMAL)
                set_view("public")
            except:
                insert_message("[ERROR] Failed to leave secret.", "error")
        else:
            pwd = simpledialog.askstring(
                "Secret Room", "Enter password:", parent=root, show="*"
            )
            if not pwd:
                return
            try:
                client_socket.sendall(f"/secret {pwd}".encode())
                in_secret = True
                secret_btn.config(text="🔓 Leave Secret")
                secret_view_btn.config(state=tk.NORMAL)
                public_view_btn.config(state=tk.DISABLED)
                set_view("secret")
            except:
                insert_message("[ERROR] Failed to enter secret.", "error")

    def toggle_mute():
        if not client_socket:
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
        if client_socket:
            try:
                client_socket.sendall("/quit".encode())
                client_socket.close()
            except:
                pass
        root.quit()

    def receive_messages(sock):
        """
        # Description
        Receive messages from the server in a separate thread and process them.

        # Arguments
        sock: the client socket
        """
        while True:
            try:
                message = sock.recv(BUFFER_SIZE).decode()
                if not message:
                    break
                for line in message.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    root.after(0, lambda msg=line: print_message(msg))
            except:
                break
        root.after(
            0, lambda: insert_message("👋 [SERVER] Connection closed.", "error")
        )
        root.after(0, lambda: set_status("Disconnected"))

    root.protocol("WM_DELETE_WINDOW", quit_app)

    def start_receiver():
        receive_thread = threading.Thread(
            target=receive_messages, args=(client_socket,)
        )
        receive_thread.daemon = True
        receive_thread.start()

    def open_dm_from_list(target):
        if target:
            set_view(f"dm:{target}")

    secret_view_btn.config(state=tk.DISABLED)

    root.mainloop()


if __name__ == "__main__":
    main()
