import os
import sys
import time
import socket
import logging
import threading
import pickle
import subprocess
import ssl
from fpdf import FPDF
import matplotlib.pyplot as plt
from daemon import DaemonContext
import configparser

"""Global cache and settings"""
file_cache = {}
REREAD_ON_QUERY = False

"""Logging configuration"""
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def create_server(host, port):
    """Create and return a server socket."""
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(5)
        logging.debug(f"Server listening on {host}:{port}")
        return server_socket
    except Exception as e:
        logging.error(f"Error creating server: {e}")
        return None

def create_secure_server_socket(host, port, ssl_enabled):
    """Create a secure server socket with SSL enabled or disabled."""
    server_socket = create_server(host, port)
    if ssl_enabled:
        server_socket = ssl.wrap_socket(
            server_socket,
            keyfile='server-key.pem',
            certfile='server-cert.pem',
            server_side=True
        )
    return server_socket

def read_file(linuxpath):
    """Reads the content of a file."""
    try:
        with open(linuxpath, 'r') as file:
            return file.readlines()
    except Exception as e:
        logging.error(f"Error reading file: {str(e)}")
        return f"Error reading file: {str(e)}"

def search_in_file(linuxpath, search_string):
    """Search for a string in a file."""
    if not os.path.exists(linuxpath):
        logging.warning(f"File at {linuxpath} does not exist.")
        return f"Error: The file at {linuxpath} does not exist."
    return "STRING EXISTS" if search_string in read_file(linuxpath) else "STRING NOT FOUND"

def handle_client_connection(client_socket, client_address, ssl_enabled, linuxpath):
    """Handles client-server interaction with SSL and searching."""
    try:
        data = client_socket.recv(4096)
        if data:
            linuxpath, search_string = pickle.loads(data)
            logging.debug(f"Received request: Searching for '{search_string}' in {linuxpath}")
            
            """Simulate a benchmark of search algorithms"""
            execution_time = benchmark_search(linuxpath, search_string)
            pdf_path = generate_pdf_report(execution_time)

            with open(pdf_path, 'rb') as pdf_file:
                client_socket.sendall(pdf_file.read())
            logging.debug(f"PDF report sent to client {client_address}")
        else:
            client_socket.close()
    except Exception as e:
        logging.error(f"Error with client {client_address}: {e}")
        client_socket.close()

def benchmark_search(linuxpath, search_string):
    """Benchmark search algorithms."""
    start_time = time.time()
    result = search_in_file(linuxpath, search_string)
    elapsed_time = time.time() - start_time
    return elapsed_time

def generate_pdf_report(execution_time, output_path="Benchmark_Report.pdf"):
    """Generate a PDF report with the execution time of the search algorithm."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="File Search Algorithm Benchmark Report", ln=True, align='C')

    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt=f"Execution Time: {execution_time:.6f} seconds", ln=True)

    plt.figure(figsize=(10, 6))
    plt.bar(["Search Algorithm"], [execution_time])
    plt.xlabel('Algorithm')
    plt.ylabel('Execution Time (s)')
    plt.title('Search Algorithm Performance')
    plt.tight_layout()
    plot_path = "benchmark_plot.png"
    plt.savefig(plot_path)
    pdf.image(plot_path, x=10, y=None, w=190)
    pdf.output(output_path)
    logging.debug(f"PDF Report Generated: {output_path}")
    return output_path

def accept_connections(server_socket, ssl_enabled, linuxpath):
    """Accept client connections and handle them in separate threads."""
    while True:
        client_socket, client_address = server_socket.accept()
        logging.debug(f"New connection from {client_address}")
        threading.Thread(target=handle_client_connection, args=(client_socket, client_address, ssl_enabled, linuxpath)).start()

def run_daemon(host, port, linuxpath, ssl_enabled):
    """Run the server as a daemon."""
    with DaemonContext():
        logging.debug(f"Daemon started on {host}:{port}")
        server_socket = create_secure_server_socket(host, port, ssl_enabled)
        accept_connections(server_socket, ssl_enabled, linuxpath)

def read_config(config_file):
    """Reads the configuration file and returns the necessary parameters."""
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

if __name__ == "__main__":
    config_file = "config.txt"
    config = read_config(config_file)
    
    if not config:
        logging.error("Error: Could not read valid configurations from the file.")
        sys.exit(1)

    host = config.get("Server", "host", fallback="127.0.0.1")
    port = int(config.get("Server", "port", fallback="8080"))
    linuxpath = config.get("Server", "linuxpath")
    ssl_enabled = config.getboolean("SSL", "enabled", fallback=True)

    if not linuxpath:
        logging.error("Error: linuxpath is missing from configuration.")
        sys.exit(1)

    """Start the server as a daemon"""
    run_daemon(host, port, linuxpath, ssl_enabled)
