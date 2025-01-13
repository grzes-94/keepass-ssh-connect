from pykeepass import PyKeePass
import sys
import getpass
from typing import List, Dict
import os
from dotenv import load_dotenv
import subprocess
from colorama import init, Fore, Style

# Initialize colorama for Windows
init()

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
    servers = []
    for entry in kp.entries:
        servers.append({
            'title': entry.title,
            'username': entry.username,
            'password': entry.password,
            'url': entry.url,
            'description': entry.notes or 'No description available'
        })
    return servers

def list_servers(servers: List[Dict]) -> None:
    """
    Display available servers with colors
    """
    print("\nAvailable servers:")
    for idx, server in enumerate(servers, 1):
        print(f"{Fore.GREEN}[{idx}]{Style.RESET_ALL} {Fore.CYAN}{server['title']}{Style.RESET_ALL} - "
              f"{Fore.YELLOW}{server['url']}{Style.RESET_ALL} - "
              f"{Fore.WHITE}{server['description']}{Style.RESET_ALL}")

def select_server(servers: List[Dict]) -> Dict:
    """
    Let user select a server
    """
    try:
        choice = int(input("\nSelect server number: "))
        if 1 <= choice <= len(servers):
            return servers[choice - 1]
        print(f"Error: Please select a number between 1 and {len(servers)}")
        sys.exit(1)
    except ValueError:
        print("Error: Please enter a valid number")
        sys.exit(1)

def connect_to_server(hostname: str, username: str, password: str, port: int = 22) -> None:
    """
    Connect to server using PLINK (Windows) or sshpass (Unix-like systems)
    """
    try:
        print(f"\nConnecting to {hostname}...")
        
        # Choose command based on operating system
        if os.name == 'nt':  # Windows
            ssh_command = f'plink -ssh -P {port} {username}@{hostname} -pw "{password}"'
        else:  # Unix-like systems
            ssh_command = f'sshpass -p "{password}" ssh -p {port} {username}@{hostname}'
        
        subprocess.run(ssh_command, shell=True)
    except Exception as e:
        print(f"Error connecting to server: {e}")

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
    print(f"Description: {selected_server['description']}")
    
    hostname, port = selected_server['url'].split(':')
    connect_to_server(hostname, selected_server['username'], selected_server['password'], int(port))

if __name__ == "__main__":
    main()
