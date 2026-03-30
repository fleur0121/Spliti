import socket
import threading

HOST = "127.0.0.1"
PORT = 5555
BUFFER_SIZE = 1024

# Shared data
clients = []
socket_to_username = {}
username_to_socket = {}

# Lock for thread-safe access
clients_lock = threading.Lock()


def send_to_client(client_socket, message):
    """
    Send one message to one client.
    Return True if successful, False otherwise.
    # Arguments:
    client_socket: the socket to send to
    message: the string message to send
    """
    try:
        client_socket.sendall(message.encode())
        return True
    except:
        return False


def broadcast(message, exclude_client=None):
    """
    Send a message to all connected clients.
    If exclude_client is provided, that client will not receive the message.
    # Arguments:
    message: the string message to send
    exclude_client: a socket to exclude from receiving the message (optional)
    """
    with clients_lock:
        disconnected_clients = []

        for client_socket in clients:
            if client_socket == exclude_client:
                continue

            try:
                client_socket.sendall(message.encode())
            except:
                disconnected_clients.append(client_socket)

    for dead_client in disconnected_clients:
        remove_client(dead_client)


def remove_client(client_socket):
    """
    Remove a client from all shared structures and close its socket.
    # Arguments:
    client_socket: the socket to remove
    """
    with clients_lock:
        username = socket_to_username.get(client_socket)

        if client_socket in clients:
            clients.remove(client_socket)

        if client_socket in socket_to_username:
            del socket_to_username[client_socket]

        if username in username_to_socket:
            del username_to_socket[username]

    try:
        client_socket.close()
    except:
        pass


def get_user_list_string():
    """
    Return a comma-separated string of online usernames.
    """
    with clients_lock:
        if not username_to_socket:
            return "No users connected."
        return ", ".join(username_to_socket.keys())


def send_help(client_socket):
    """
    Send command help text to one client.
    # Arguments:
    client_socket: the socket to send the help text to
    """
    help_text = (
        "[SERVER] Commands:\n"
        "/users                  -> show online users\n"
        "/dm <username> <msg>    -> send a private message\n"
        "/help                   -> show commands\n"
        "/quit                   -> leave the chat"
    )
    send_to_client(client_socket, help_text)


def handle_dm(sender_socket, sender_username, message):
    """
    Handle a private message command of the form:
    /dm username message
    # Arguments:
    sender_socket: the socket of the sender
    sender_username: the username of the sender
    message: the full command message string
    """
    parts = message.split(" ", 2)

    if len(parts) < 3:
        send_to_client(
            sender_socket, "[SERVER] Usage: /dm <username> <message>"
        )
        return

    target_username = parts[1].strip()
    dm_text = parts[2].strip()

    if dm_text == "":
        send_to_client(
            sender_socket, "[SERVER] Your private message cannot be empty."
        )
        return

    with clients_lock:
        target_socket = username_to_socket.get(target_username)

    if target_socket is None:
        send_to_client(
            sender_socket, f"[SERVER] User '{target_username}' not found."
        )
        return

    if target_socket == sender_socket:
        send_to_client(sender_socket, "[SERVER] You cannot DM yourself.")
        return

    delivered_to_target = send_to_client(
        target_socket, f"[DM from {sender_username}] {dm_text}"
    )

    if not delivered_to_target:
        send_to_client(
            sender_socket,
            f"[SERVER] Could not deliver DM to '{target_username}'.",
        )
        return

    send_to_client(sender_socket, f"[DM to {target_username}] {dm_text}")


def handle_client(client_socket, client_address):
    """
    Handle all communication for one client.
    # Arguments:
    client_socket: the socket for this client
    client_address: the (ip, port) tuple of the client's address
    """
    username = "Unknown"

    try:
        # First message must be the username
        data = client_socket.recv(BUFFER_SIZE)
        if not data:
            remove_client(client_socket)
            return

        proposed_username = data.decode().strip()

        if proposed_username == "":
            send_to_client(client_socket, "[SERVER] Username cannot be empty.")
            remove_client(client_socket)
            return

        with clients_lock:
            if proposed_username in username_to_socket:
                send_to_client(
                    client_socket, "[SERVER] Username already taken."
                )
                remove_client(client_socket)
                return

            username = proposed_username
            clients.append(client_socket)
            socket_to_username[client_socket] = username
            username_to_socket[username] = client_socket

        print(f"[CONNECTED] {username} joined from {client_address}")
        send_to_client(client_socket, f"[SERVER] Welcome, {username}!")
        send_help(client_socket)
        broadcast(f"*** {username} joined the chat ***", exclude_client=None)

        while True:
            data = client_socket.recv(BUFFER_SIZE)

            if not data:
                break

            message = data.decode().strip()

            if message == "":
                continue

            # Command: /users
            if message == "/users":
                user_list = get_user_list_string()
                send_to_client(
                    client_socket, f"[SERVER] Online users: {user_list}"
                )
                continue

            # Command: /help
            if message == "/help":
                send_help(client_socket)
                continue

            # Command: /quit
            if message == "/quit":
                break

            # Command: /dm username message
            if message.startswith("/dm "):
                handle_dm(client_socket, username, message)
                continue

            # Otherwise: group chat message
            full_message = f"{username}: {message}"
            print(f"[GROUP] {full_message}")

            # Send to other users
            broadcast(full_message, exclude_client=client_socket)

            # Also echo to sender so they can see their own sent message nicely
            send_to_client(client_socket, f"[You] {message}")

    except ConnectionResetError:
        print(f"[DISCONNECTED] {username} connection was reset.")
    except Exception as error:
        print(f"[ERROR] Problem with {username}: {error}")
    finally:
        print(f"[LEFT] {username} left the chat.")
        remove_client(client_socket)
        broadcast(f"*** {username} left the chat ***", exclude_client=None)


def main():
    """
    Start the chat server and accept clients forever.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print("=" * 55)
    print(" Terminal Chat Server ")
    print("=" * 55)
    print(f"Listening on {HOST}:{PORT}")
    print("Features: group chat, direct messages, /users, /help, /quit")
    print("Press Ctrl+C to stop the server.")
    print("=" * 55)

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"[NEW CONNECTION] {client_address}")

            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address),
                daemon=True,
            )
            client_thread.start()

    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server is shutting down.")
    finally:
        with clients_lock:
            current_clients = clients[:]

        for client_socket in current_clients:
            try:
                client_socket.close()
            except:
                pass

        server_socket.close()


if __name__ == "__main__":
    main()
