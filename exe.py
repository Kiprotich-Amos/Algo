import subprocess
import time
import os

def read_config(config_file):
    """Reads the configuration file and returns the necessary parameters."""
    config = {}
    try:
        with open(config_file, "r") as file:
            for line in file:
                """Ignore comment lines or empty lines"""
                if line.strip() == "" or line.startswith("#"):
                    continue
                """Split the line at '=' to get the key-value pair"""
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Error: The configuration file {config_file} was not found.")
    except Exception as e:
        print(f"Error reading configuration file: {e}")
    return config

def run_server(server_path, host, port, linuxpath):
    """Run the server in a subprocess, passing the necessary arguments"""
    print(f"Starting server from {server_path}...")
    server_process = subprocess.Popen(
        ["python", server_path, host, port, linuxpath]
    )
    return server_process

def run_client(client_path, host, port, linuxpath):
    """Give the server some time to start and then run the client"""
    time.sleep(1)  
    print(f"Starting client from {client_path}...")
    client_process = subprocess.Popen(
        ["python", client_path, host, port, linuxpath]
    )
    return client_process

def main():
    """Run both the server and client based on config file."""
    config_file = "config.txt" 
    config = read_config(config_file)
    
    if not config:
        print("Error: Could not read valid configurations from the file.")
        return

    """Extract the configuration details"""
    linuxpath = config.get("linuxpath")
    client_path = config.get("client")
    server_path = config.get("server")
    host = config.get("host", "127.0.0.1") 
    port = config.get("port", "8080")
    
    if not all([linuxpath, client_path, server_path]):
        print("Error: Missing critical configuration parameters (linuxpath, client, or server).")
        return

    """ Run the server and client with the extracted paths and parameters"""
    server_process = run_server(server_path, host, port, linuxpath)
    client_process = run_client(client_path, host, port, linuxpath)
    
    """ Wait for the client to finish and terminate the server"""
    client_process.wait()
    server_process.terminate()
    
    print("Server and client processes completed.")

if __name__ == "__main__":
    main()
