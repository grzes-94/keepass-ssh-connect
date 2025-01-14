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

def parse_server_url(url: str) -> tuple[str, int]:
    """
    Parse server URL to extract hostname and port.
    If port is not specified, returns default port 22.
    """
    if ':' in url:
        hostname, port = url.split(':', 1)
        return hostname, int(port)
    return url, 22

def get_server_entries(db: PyKeePass, group_path: str = None) -> list[dict]:
    """
    Get server entries from the KeePass database.
    Args:
        db: PyKeePass database instance
        group_path: Path to group or special values:
            - None: return entries from all groups
            - "root": return only root-level entries (no group)
            - "path/to/group": return entries from specific group
    """
    entries = []
    if group_path == "root":
        # Get only root-level entries (entries without a group)
        entries = [e for e in db.entries if e.group == db.root_group]
    elif group_path:
        # Get entries from specific group
        group = db.find_groups(path=group_path, first=True)
        if not group:
            print(f"Group {group_path} not found")
            sys.exit(1)
        entries = group.entries
    else:
        # Get all entries
        entries = db.entries

    servers = []
    for entry in entries:
        if entry.url:  # Only process entries with URLs
            hostname, port = parse_server_url(entry.url)
            servers.append({
                "title": entry.title,
                "username": entry.username,
                "password": entry.password,
                "url": entry.url,
                "hostname": hostname,
                "port": port,
                "description": entry.notes or ""
            })
    return servers

def list_servers(servers: List[Dict]) -> None:
    """
    Display available servers with colors
    """
    if not servers:
        print(Fore.YELLOW + "No servers found." + Style.RESET_ALL)
        return

    print("\nAvailable servers:")
    for idx, server in enumerate(servers, 1):
        description = server['description'] if server['description'] else 'No description available'
        print(f"{Fore.GREEN}[{idx}]{Style.RESET_ALL} {Fore.CYAN}{server['title']}{Style.RESET_ALL} - "
              f"{Fore.YELLOW}{server['url']}{Style.RESET_ALL} - "
              f"{Fore.WHITE}{description}{Style.RESET_ALL}")

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
    group_path = os.getenv('KEEPASS_GROUP_PATH')

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
    servers = get_server_entries(kp, group_path)
    
    if not servers:
        print("No server entries found in the database.")
        sys.exit(1)

    list_servers(servers)
    selected_server = select_server(servers)

    print(f"\nSelected server: {selected_server['title']}")
    print(f"Username: {selected_server['username']}")
    print(f"URL: {selected_server['url']}")
    print(f"Description: {selected_server['description']}")
    
    connect_to_server(selected_server['hostname'], selected_server['username'], selected_server['password'], selected_server['port'])

if __name__ == "__main__":
    main()
