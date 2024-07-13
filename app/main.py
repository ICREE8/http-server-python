
import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Create server socket
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server is listening on port 4221")

    client, addr = server_socket.accept()  # wait for client
    while client:
        client.sendall(b"HTTP/1.1 200 OK\r\n\r\n")

if __name__ == "__main__":    main()

