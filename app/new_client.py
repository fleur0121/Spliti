import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk

HOST = "127.0.0.1"
PORT = 5555
BUFFER_SIZE = 1024

# Locally muted usernames
muted_users = set()
muted_lock = threading.Lock()

def is_muted(username):
    with muted_lock:
        return username in muted_users

def mute_user(username):
    with muted_lock:
        if username in muted_users:
            return False
        muted_users.add(username)
        return True

def unmute_user(username):
    with muted_lock:
        if username not in muted_users:
            return False
        muted_users.discard(username)
        return True

def get_sender_chat(message):
    if ": " in message and not message.startswith("["):
        return message.split(": ", 1)[0]
    return None

def get_sender_dm(message):
    if message.startswith("[DM from "):
        try:
            return message[len("[DM from "):].split("]", 1)[0]
        except IndexError:
            return None
    return None

def main():
    root = tk.Tk()
    root.title("💬 Cute Chat App 😊")
    root.geometry("500x600")
    root.configure(bg="#FFE4E1")  # Misty Rose

    # Chat display area
    frame = tk.Frame(root, bg="#FFE4E1")
    chat_text = tk.Text(frame, wrap=tk.WORD, state=tk.DISABLED, bg="white", font=("Comic Sans MS", 10), padx=10, pady=10, relief=tk.FLAT)
    scrollbar = tk.Scrollbar(frame, command=chat_text.yview)
    chat_text.config(yscrollcommand=scrollbar.set)
    chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Configure tags for styling
    chat_text.tag_configure("server", foreground="#4169E1", font=("Comic Sans MS", 10, "bold"))  # Royal Blue
    chat_text.tag_configure("you", foreground="#32CD32", font=("Comic Sans MS", 10, "bold"))  # Lime Green
    chat_text.tag_configure("dm_in", foreground="#DA70D6", font=("Comic Sans MS", 10, "italic"))  # Orchid
    chat_text.tag_configure("dm_out", foreground="#DA70D6", font=("Comic Sans MS", 10, "italic"))
    chat_text.tag_configure("join_leave", foreground="#FFA500", font=("Comic Sans MS", 10, "bold"))  # Orange
    chat_text.tag_configure("error", foreground="#DC143C", font=("Comic Sans MS", 10, "bold"))  # Crimson
    chat_text.tag_configure("chat", foreground="black")
    chat_text.tag_configure("local", foreground="#00CED1", font=("Comic Sans MS", 10, "bold"))  # Dark Turquoise

    # Toolbar for commands
    toolbar = tk.Frame(root, bg="#FFE4E1")
    users_btn = tk.Button(toolbar, text="👥 Users", command=lambda: show_users(), bg="#FFB6C1", font=("Comic Sans MS", 9), relief=tk.FLAT)
    dm_btn = tk.Button(toolbar, text="💌 DM", command=lambda: send_dm(), bg="#FFB6C1", font=("Comic Sans MS", 9), relief=tk.FLAT)
    rename_btn = tk.Button(toolbar, text="✏️ Rename", command=lambda: rename_user(), bg="#FFB6C1", font=("Comic Sans MS", 9), relief=tk.FLAT)
    secret_btn = tk.Button(toolbar, text="🔒 Secret", command=lambda: toggle_secret(), bg="#FFB6C1", font=("Comic Sans MS", 9), relief=tk.FLAT)
    mute_btn = tk.Button(toolbar, text="🔇 Mute", command=lambda: toggle_mute(), bg="#FFB6C1", font=("Comic Sans MS", 9), relief=tk.FLAT)
    quit_btn = tk.Button(toolbar, text="👋 Quit", command=lambda: quit_app(), bg="#FFB6C1", font=("Comic Sans MS", 9), relief=tk.FLAT)
    users_btn.pack(side=tk.LEFT, padx=5, pady=5)
    dm_btn.pack(side=tk.LEFT, padx=5, pady=5)
    rename_btn.pack(side=tk.LEFT, padx=5, pady=5)
    secret_btn.pack(side=tk.LEFT, padx=5, pady=5)
    mute_btn.pack(side=tk.LEFT, padx=5, pady=5)
    quit_btn.pack(side=tk.LEFT, padx=5, pady=5)
    toolbar.pack(fill=tk.X, padx=10)

    # Bottom input area
    bottom_frame = tk.Frame(root, bg="#FFE4E1")
    entry = tk.Entry(bottom_frame, font=("Comic Sans MS", 10), relief=tk.FLAT)
    send_button = tk.Button(bottom_frame, text="📤 Send", command=lambda: send_message(), bg="#98FB98", font=("Comic Sans MS", 10), relief=tk.FLAT)
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
    send_button.pack(side=tk.RIGHT, padx=5, pady=5)
    bottom_frame.pack(fill=tk.X, padx=10, pady=10)

    # Bind Enter to send
    entry.bind("<Return>", lambda e: send_message())

    client_socket = None
    username = None
    in_secret = False

    def insert_message(text, tag):
        chat_text.config(state=tk.NORMAL)
        chat_text.insert(tk.END, text + "\n", tag)
        chat_text.see(tk.END)
        chat_text.config(state=tk.DISABLED)

    def print_message(message):
        nonlocal in_secret
        dm_sender = get_sender_dm(message)
        if dm_sender is not None:
            if is_muted(dm_sender):
                return
            insert_message(message, "dm_in")
            return
        if message.startswith("[DM to "):
            insert_message(message, "dm_out")
            return
        if message.startswith("[You]"):
            insert_message(message, "you")
            return
        if message.startswith("***") and message.endswith("***"):
            insert_message(message, "join_leave")
            return
        if message.startswith("[SERVER]"):
            if "\n" in message:
                for line in message.split("\n"):
                    if any(kw in line for kw in ("not found", "Wrong", "cannot", "already", "Usage", "Error")):
                        insert_message(line, "error")
                    else:
                        insert_message(line, "server")
            elif any(kw in message for kw in ("not found", "Wrong", "cannot", "already", "Usage", "Error")):
                insert_message(message, "error")
            else:
                insert_message(message, "server")
            return
        chat_sender = get_sender_chat(message)
        if chat_sender is not None:
            if is_muted(chat_sender):
                return
            insert_message(message, "chat")
            return
        insert_message(message, "chat")

    def connect(uname):
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

    def send_message():
        message = entry.get().strip()
        entry.delete(0, tk.END)
        if not message:
            return
        try:
            client_socket.sendall(message.encode())
        except:
            insert_message("[ERROR] Failed to send message.", "error")

    def show_users():
        try:
            client_socket.sendall("/users".encode())
        except:
            insert_message("[ERROR] Failed to get users.", "error")

    def send_dm():
        target = simpledialog.askstring("DM", "Enter username to DM:", parent=root)
        if not target:
            return
        msg = simpledialog.askstring("DM", f"Message to {target}:", parent=root)
        if not msg:
            return
        try:
            client_socket.sendall(f"/dm {target} {msg}".encode())
        except:
            insert_message("[ERROR] Failed to send DM.", "error")

    def rename_user():
        new_name = simpledialog.askstring("Rename", "Enter new username:", parent=root)
        if not new_name:
            return
        try:
            client_socket.sendall(f"/rename {new_name}".encode())
        except:
            insert_message("[ERROR] Failed to rename.", "error")

    def toggle_secret():
        nonlocal in_secret
        if in_secret:
            try:
                client_socket.sendall("/secret_leave".encode())
                in_secret = False
                secret_btn.config(text="🔒 Secret")
            except:
                insert_message("[ERROR] Failed to leave secret.", "error")
        else:
            pwd = simpledialog.askstring("Secret Room", "Enter password:", parent=root, show="*")
            if not pwd:
                return
            try:
                client_socket.sendall(f"/secret {pwd}".encode())
                in_secret = True
                secret_btn.config(text="🔓 Leave Secret")
            except:
                insert_message("[ERROR] Failed to enter secret.", "error")

    def toggle_mute():
        target = simpledialog.askstring("Mute/Unmute", "Enter username to mute/unmute:", parent=root)
        if not target:
            return
        if is_muted(target):
            if unmute_user(target):
                insert_message(f"[LOCAL] {target} has been unmuted. 😊", "local")
            else:
                insert_message(f"[LOCAL] {target} is not muted.", "local")
        else:
            if mute_user(target):
                insert_message(f"[LOCAL] {target} has been muted. 🤐", "local")
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
        while True:
            try:
                message = sock.recv(BUFFER_SIZE).decode()
                if not message:
                    break
                root.after(0, lambda: print_message(message))
            except:
                break
        root.after(0, lambda: insert_message("👋 [SERVER] Connection closed.", "error"))

    root.protocol("WM_DELETE_WINDOW", quit_app)

    # Connect loop
    while not client_socket:
        uname = simpledialog.askstring("Welcome! 🎉", "Enter your username: 😊", parent=root)
        if not uname:
            root.quit()
            return
        client_socket = connect(uname.strip())
        if not client_socket:
            messagebox.showerror("Oops! 😞", "Invalid username or connection failed. Try again.")

    username = uname.strip()

    # Start receive thread
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()

    root.mainloop()

if __name__ == "__main__":
    main()