from pykeepass import PyKeePass
import sys
import getpass
from typing import List, Dict
import os
from dotenv import load_dotenv
import paramiko

# Load environment variables
load_dotenv()

def load_keepass_db(db_path: str, key_path: str = None) -> PyKeePass:
    """
    Load the KeePass database with optional key file
    """
    try:
        kp = PyKeePass(db_path, keyfile=key_path)
        return kp
    except Exception as e:
        print(f"Error opening KeePass database: {e}")
        sys.exit(1)

def get_server_entries(kp: PyKeePass) -> List[Dict]:
    """
    Get all server entries from the database
    """
    # Assuming server entries are tagged with 'server' or are in a 'Servers' group
    servers = []
    for entry in kp.entries:
        servers.append({
            'title': entry.title,
            'username': entry.username,
            'password': entry.password,
            'url': entry.url
        })
    return servers

def list_servers(servers: List[Dict]) -> None:
    """
    Display available servers
    """
    print("\nAvailable servers:")
    for idx, server in enumerate(servers, 1):
        print(f"{idx}. {server['title']} ({server['url']})")

def select_server(servers: List[Dict]) -> Dict:
    """
    Let user select a server
    """
    while True:
        try:
            choice = int(input("\nSelect server number: "))
            if 1 <= choice <= len(servers):
                return servers[choice - 1]
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def connect_to_server(hostname: str, username: str, password: str, port: int = 22) -> None:
    """
    Connect to server using SSH
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"\nConnecting to {hostname}...")
        ssh.connect(hostname, port, username, password)
        print("Successfully connected!")
        
        # Keep the connection open for interaction
        while True:
            command = input("Enter command (or 'exit' to quit): ")
            if command.lower() == 'exit':
                break
                
            stdin, stdout, stderr = ssh.exec_command(command)
            print(stdout.read().decode())
            print(stderr.read().decode())
            
    except Exception as e:
        print(f"Error connecting to server: {e}")
    finally:
        if 'ssh' in locals():
            ssh.close()
            print("Connection closed.")

def main():
    # Get paths from environment variables
    db_path = os.getenv('KEEPASS_DB_PATH')
    key_path = os.getenv('KEEPASS_KEY_PATH')

    if not db_path:
        print("Error: KeePass database path not provided in .env file or command line")
        sys.exit(1)

    if not os.path.exists(db_path):
        print(f"Error: KeePass database file not found: {db_path}")
        sys.exit(1)

    if key_path and not os.path.exists(key_path):
        print(f"Error: Key file not found: {key_path}")
        sys.exit(1)

    # Load the database
    kp = load_keepass_db(db_path, key_path)

    # Get and list servers
    servers = get_server_entries(kp)
    
    if not servers:
        print("No server entries found in the database.")
        sys.exit(1)

    list_servers(servers)
    selected_server = select_server(servers)

    print(f"\nSelected server: {selected_server['title']}")
    print(f"Username: {selected_server['username']}")
    print(f"URL: {selected_server['url']}")
    
    hostname, port = selected_server['url'].split(':')
    connect_to_server(hostname, selected_server['username'], selected_server['password'], int(port))

if __name__ == "__main__":
    main()
