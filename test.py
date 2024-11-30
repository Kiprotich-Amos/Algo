import pytest
import socket
from server import search_in_file
import os
import sys
import pickle
import threading
import subprocess 

file = open("200k.txt", 'r')
search_String = '3;0;1;28;0;7;5;0;'.strip()
for line in file:
    if search_String in line.strip():
        print( f"STRING EXIST")
    else:
        print (f"STRING NOT FOUND")
        








def test_search_in_file_existing_file():
    result = search_in_file("config.txt", "search_term")
    assert result == "STRING EXISTS"

def test_search_in_file_non_existing_file():
    result = search_in_file("200k.txt", "search_term")
    assert result == "Error: The file at /path/to/non_existing_file.txt does not exist."

def test_server_connection():
    # Assuming a local server is running on port 8080
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", 8080))
        s.sendall(b"Test message")
        response = s.recv(1024)
    assert response == b"Expected server response"


# # Global cache for file content (if needed)
# file_cache = {}

# # Global flag for rereading the file on each query
# REREAD_ON_QUERY = False

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



        
