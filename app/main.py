import socket  # Add this import statement


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Create server socket
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server is listening on port 4221")

    while True:
        client_socket, client_address = server_socket.accept()  # wait for client
        print(f"Connection from {client_address}")

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
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"

            # Send the response
            client_socket.sendall(response.encode('utf-8'))
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


if __name__ == "__main__":
    main()