
import socket
import threading
import os
import sys
import gzip
import io


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

        # Extract headers
        headers = request.split('\r\n')[1:]
        accept_encoding = ""
        for header in headers:
            if header.startswith("Accept-Encoding:"):
                accept_encoding = header.split("Accept-Encoding: ")[1]
                break

        # Determine the response based on the path and method
        if method == "GET":
            if path == "/":
                response = "HTTP/1.1 200 OK\r\n\r\n"
            elif path.startswith("/echo/"):
                echo_str = path[len("/echo/"):]
                response_body = echo_str.encode('utf-8')
                if "gzip" in accept_encoding:
                    response_body = gzip.compress(response_body)
                    response_headers = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain\r\n"
                        "Content-Encoding: gzip\r\n"
                        f"Content-Length: {len(response_body)}\r\n"
                        "\r\n"
                    )
                else:
                    response_headers = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain\r\n"
                        f"Content-Length: {len(response_body)}\r\n"
                        "\r\n"
                    )
                response = response_headers.encode('utf-8') + response_body
            elif path == "/user-agent":
                # Extract the User-Agent header
                user_agent = ""
                for header in headers:
                    if header.startswith("User-Agent:"):
                        user_agent = header.split("User-Agent: ")[1]
                        break

                response_body = user_agent.encode('utf-8')
                if "gzip" in accept_encoding:
                    response_body = gzip.compress(response_body)
                    response_headers = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain\r\n"
                        "Content-Encoding: gzip\r\n"
                        f"Content-Length: {len(response_body)}\r\n"
                        "\r\n"
                    )
                else:
                    response_headers = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain\r\n"
                        f"Content-Length: {len(response_body)}\r\n"
                        "\r\n"
                    )
                response = response_headers.encode('utf-8') + response_body
            elif path.startswith("/files/"):
                filename = path[len("/files/"):]
                file_path = os.path.join(base_directory, filename)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    response_body = file_content
                    if "gzip" in accept_encoding:
                        response_body = gzip.compress(response_body)
                        response_headers = (
                            "HTTP/1.1 200 OK\r\n"
                            "Content-Type: application/octet-stream\r\n"
                            "Content-Encoding: gzip\r\n"
                            f"Content-Length: {len(response_body)}\r\n"
                            "\r\n"
                        )
                    else:
                        response_headers = (
                            "HTTP/1.1 200 OK\r\n"
                            "Content-Type: application/octet-stream\r\n"
                            f"Content-Length: {len(response_body)}\r\n"
                            "\r\n"
                        )
                    response = response_headers.encode('utf-8') + response_body
                else:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n".encode('utf-8')
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n".encode('utf-8')
        elif method == "POST" and path.startswith("/files/"):
            filename = path[len("/files/"):]
            file_path = os.path.join(base_directory, filename)

            # Extract the headers and request body
            headers, body = request.split('\r\n\r\n', 1)
            content_length = 0
            for header in headers.split('\r\n')[1:]:
                if header.startswith("Content-Length:"):
                    content_length = int(header.split("Content-Length: ")[1])
                    break

            # Read the remaining body if not fully received
            while len(body) < content_length:
                body += client_socket.recv(1024).decode('utf-8')

            # Write the body to the file
            with open(file_path, 'wb') as f:
                f.write(body.encode('utf-8'))

            response = "HTTP/1.1 201 Created\r\n\r\n".encode('utf-8')
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n".encode('utf-8')

        # Send the response
        client_socket.sendall(response)
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
    if len(sys.argv) == 3 and sys.argv[1] == "--directory":
        base_directory = sys.argv[2]
    else:
        base_directory = "/tmp"  # Default directory

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
