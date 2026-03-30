import socket

HOST = "127.0.0.1"
PORT = 5555


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    print(f"Connected to server at {HOST}:{PORT}")

    while True:
        message = input("Enter message: ")

        if message.lower() == "quit":
            break

        client_socket.sendall(message.encode())

    client_socket.close()


if __name__ == "__main__":
    main()
