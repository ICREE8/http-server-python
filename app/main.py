
import socket
import threading
import os
import sys


def handle_client(client_socket, base_directory):
    try:
        # Receive the request
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Request received: {request}")

        # Extract the request line
        request_line = request.split('\r\n')[0]
        print(f"Request line: {request_line}")

        # Extract the URL path
        method, path, http_version = request_line.split()
        print(f"Method: {method}, Path: {path}, HTTP Version: {http_version}")

        # Determine the response based on the path
        if path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"
        elif path.startswith("/echo/"):
            echo_str = path[len("/echo/"):]
            response_body = echo_str
            response = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "\r\n"
                f"{response_body}"
            )
        elif path == "/user-agent":
            # Extract the User-Agent header
            headers = request.split('\r\n')[1:]
            user_agent = ""
            for header in headers:
                if header.startswith("User-Agent:"):
                    user_agent = header.split("User-Agent: ")[1]
                    break

            response_body = user_agent
            response = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "\r\n"
                f"{response_body}"
            )
        elif path.startswith("/files/"):
            filename = path[len("/files/"):]
            file_path = os.path.join(base_directory, filename)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                response_body = file_content
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/octet-stream\r\n"
                    f"Content-Length: {len(response_body)}\r\n"
                    "\r\n"
                ).encode('utf-8') + response_body
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"

        # Send the response
        client_socket.sendall(response if isinstance(response, bytes) else response.encode('utf-8'))
        print("Response sent")
    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        # Ensure the response is flushed and then close the client connection
        try:
            client_socket.shutdown(socket.SHUT_WR)
        except Exception as e:
            print(f"Error shutting down socket: {e}")
        client_socket.close()
        print("Client connection closed")


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Parse command line arguments
    if len(sys.argv) != 3 or sys.argv[1] != "--directory":
        print("Usage: ./your_server.sh --directory <path>")
        sys.exit(1)

    base_directory = sys.argv[2]

    # Create server socket
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server is listening on port 4221")

    while True:
        client_socket, client_address = server_socket.accept()  # wait for client
        print(f"Connection from {client_address}")

        # Handle the client connection in a new thread
        client_thread = threading.Thread(target=handle_client, args=(client_socket, base_directory))
        client_thread.start()


if __name__ == "__main__":
    main()
