# Main client class to handle connection and communication with the server

import socket
import threading


class ChatClient:
    def __init__(self, host, port, buffer_size):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.socket = None
        self._lock = threading.Lock()  # protect socket across threads

    def is_connected(self):
        """
        # Description
        Checks if the client is currently connected to the server.

        # Returns
        `True` if connected, `False` otherwise.
        """
        return self.socket is not None

    def connect(self, username):
        """
        # Description
        Connects to the chat server with the given username.
        If already connected, it will first close the existing connection.

        # Arguments
        username: The username to register with the server

        # Returns
        A tuple of (response_message, success) where:
        - response_message: The server's response message after attempting to connect
        - success: `True` if connection was successful, `False` otherwise
        """
        with self._lock:
            if self.socket is not None:
                self.close()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.host, self.port))
                sock.sendall(username.encode())
                response = sock.recv(self.buffer_size).decode()
                if "Welcome" in response:
                    self.socket = sock
                    return response, True
                sock.close()
                return response, False
            except Exception as error:
                return f"[ERROR] {error}", False

    def send(self, message):
        """
        # Description
        Sends a message to the chat server. Raises an error if not connected.

        # Arguments
        message: The message to send to the server
        """
        with self._lock:
            if self.socket is None:
                raise RuntimeError("Not connected")
            self.socket.sendall(message.encode())

    def start_receiver(self, on_message, on_disconnect):
        """
        # Description
        Starts a background thread to receive messages from the server.
        Calls `on_message` callback for each received message and `on_disconnect` if the connection is lost.

        # Arguments
        on_message: A callback function that takes a single string argument (the received message)
        on_disconnect: A callback function that takes no arguments, called when the connection is lost
        """

        def receive_loop():
            while True:
                try:
                    with self._lock:
                        sock = self.socket
                    if sock is None:
                        break
                    data = sock.recv(self.buffer_size)
                    if not data:
                        break
                    on_message(data.decode())
                except Exception:
                    break
            on_disconnect()

        thread = threading.Thread(target=receive_loop, daemon=True)
        thread.start()

    def close(self):
        """
        # Description
        Closes the connection to the server if it is open.
        """
        with self._lock:
            sock = self.socket
            self.socket = None
        if sock:
            try:
                sock.close()
            except Exception:
                pass
