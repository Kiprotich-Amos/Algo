import sys
import pickle
import socket
import ssl
import configparser

def read_config(config_file):
    """Reads the configuration file and returns the necessary parameters."""
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def create_secure_client_socket(host, port, ssl_enabled):
    """Create a secure client socket with SSL enabled or disabled."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if ssl_enabled:
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations('server-cert.pem')
        client_socket = context.wrap_socket(client_socket, server_hostname=host)
    client_socket.connect((host, port))
    return client_socket

def client(host, port, linuxpath, ssl_enabled):
    """Client logic to connect to the server and request data."""
    client_socket = create_secure_client_socket(host, port, ssl_enabled)

    # Prepare data to send to the server
    search_string = "3;0;1;28;0;7;5;0;"
    data = (linuxpath, search_string)
    message = pickle.dumps(data)
    client_socket.sendall(message)

    # Receive and print the server's response
    response = client_socket.recv(1024)
    print("Server response:", response.decode('utf-8'))

    client_socket.close()

if __name__ == "__main__":
    config_file = "config.txt"
    config = read_config(config_file)

    host = config.get("Server", "host", fallback="127.0.0.1")
    port = int(config.get("Server", "port", fallback="8080"))
    linuxpath = config.get("Server", "linuxpath")
    ssl_enabled = config.getboolean("SSL", "enabled", fallback=True)

    if not linuxpath:
        print("Error: linuxpath is missing from configuration.")
        sys.exit(1)

    # Run the client with SSL support
    client(host, port, linuxpath, ssl_enabled)
