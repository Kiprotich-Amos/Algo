file = open("200k.txt", 'r')
search_String = '3;0;1;28;0;7;5;0;'.strip()
import os
import sys
import pickle
import socket
import threading
import subprocess  # Import subprocess for running system commands

# Global cache for file content (if needed)
file_cache = {}

# Global flag for rereading the file on each query
REREAD_ON_QUERY = False

def create_server(host, port):
    """Create and configure the server socket."""
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        """Binding to address & port."""
        server_socket.bind((host, port))
        
        """Enable connection."""
        server_socket.listen(5)
        
        return server_socket
    except Exception as e:
        print(f"Error creating server: {e}")
        return None

def search_in_file_with_grep(linuxpath, search_string):
    """Search for a string in the file using the `grep` command via subprocess."""
    try:
        # Use grep command to search for the string in the file
        result = subprocess.run(
            ['grep', '-q', search_string, linuxpath], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        if result.returncode == 0:  # grep returns 0 if a match is found
            return "STRING EXISTS"
        else:
            return "STRING NOT FOUND"
    except Exception as e:
        return f"Error running grep on file {linuxpath}: {str(e)}"

def handle_client_connection(client_socket, client_address):
    """This function will be run in a separate thread for each client connection."""
    try:
        """Receive the data (pickle)."""
        data = client_socket.recv(4096)
        if data:
            """Deserialize the data (linuxpath and search_string)."""
            linuxpath, search_string = pickle.loads(data)
            
            print(f"Received request from {client_address}: Searching for '{search_string}' in file {linuxpath}")
            
            """Search in the file using grep."""
            result = search_in_file_with_grep(linuxpath, search_string)
            
            """Send the result back to the client."""
            client_socket.sendall(result.encode('utf-8'))
        else:
            client_socket.close()
    except Exception as e:
        print(f"Error with client {client_address}: {e}")
        client_socket.close()

def accept_connections(server_socket):
    """This function will accept client connections and spawn a new thread to handle each one."""
    while True:
        """Wait for a connection."""
        client_socket, client_address = server_socket.accept()
        print(f"New connection from {client_address}")
        
        """Start a new thread to handle the client."""
        client_thread = threading.Thread(target=handle_client_connection, args=(client_socket, client_address))
        client_thread.start()

def main():
    """Accept host and port as command-line arguments."""
    if len(sys.argv) != 3:
        print("Usage: python server.py <host> <port>")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
        
    server_socket = create_server(host, port)
    if server_socket is None:
        print("Failed to start the server.")
        return
    
    print(f"Server started on {host}:{port}")
    
    """Accept client connections concurrently using threads."""
    accept_connections(server_socket)

if __name__ == "__main__":
    main()

for line in file:
    if search_String in line.strip():
        print( f"STRING EXIST")
    else:
        print (f"STRING NOT FOUND")
        
        
        
