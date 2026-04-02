import socket
import threading

HOST = "127.0.0.1"
PORT = 5555
BUFFER_SIZE = 1024

def receive_messages(client_socket):
    # loop forever waiting for messages
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode()
            # empty, server disconnected
            if not message:
                print("[SERVER] Connection closed.")
                break
            print(message)
        # unexpected connection lost
        except:
            print("[SERVER] Connection lost.")
            break


def main():
    username = "Unknown" 
    client_socket = None 
    try:
        # 1. Create a TCP socket and connect 
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))

        # 2. Ask user to type a username and send it to server
        # get username until we get a valid response
        while True:
            username = input("Enter your username: ")
            client_socket.sendall(username.encode()) 
        
            response = client_socket.recv(BUFFER_SIZE).decode()
            print(response)

            # check if username is taken
            if "already taken" in response:
                print("That username is taken, try different username.")
                # reconnect for next attempt
                client_socket.close()
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((HOST, PORT))
                continue
            # check if username is empty
            elif "cannot be empty" in response:
                # reconnect for next attempt
                client_socket.close()
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((HOST, PORT))
                continue
            # welcome response
            elif "Welcome" in response:
                break

        # 3. Create a background thread to receive messages from the server
        receiver_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receiver_thread.daemon = True
        receiver_thread.start()    
        print(f"Connected to server at {HOST}:{PORT}")

        # 4. Main threa dreads user niput and sends it to the server
        # get messages until user types /quit
        while True:
            message = input()

            # skips empty messages
            if message.strip() == "":
                continue

            # send the message to the server
            client_socket.sendall(message.encode())

            # quit the session
            if message == "/quit":
                break
      
    # 5. Handle errors 
    except KeyboardInterrupt:
        print(f"\n[DISCONNECTED] {username} disconnected.")
    except ConnectionResetError:
        print(f"[DISCONNECTED] {username} connection was reset.")
    except Exception as error:
        print(f"[ERROR] Problem with {username}: {error}")
    finally:
        print(f"[LEFT] {username} left the chat.")
        client_socket.close()


if __name__ == "__main__":
    main()
