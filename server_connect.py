#!/usr/bin/env python3
"""KeePass SSH Connection Tool."""

import os
import sys
from dotenv import load_dotenv
from colorama import init as init_colorama

from keepass_ssh.database import KeePassDatabase, DatabaseError, GroupNotFoundError
from keepass_ssh.server import ServerManager
from keepass_ssh.ssh import SSHConnector, SSHConnectionError

def main():
    """Main entry point."""
    init_colorama()
    load_dotenv()
    
    # Get database configuration
    db_path = os.getenv('KEEPASS_DB_PATH')
    key_path = os.getenv('KEEPASS_KEY_PATH')
    group_path = os.getenv('KEEPASS_GROUP_PATH')
    
    if not db_path:
        print("Error: KEEPASS_DB_PATH environment variable not set")
        sys.exit(1)
    
    try:
        # Initialize database connection
        db = KeePassDatabase(db_path, key_path)
        
        # Get server entries
        keepass_entries = db.get_entries(group_path)
        servers = [ServerManager.from_keepass_entry(entry) for entry in keepass_entries]
        
        if not servers:
            print("No server entries found")
            sys.exit(1)
        
        # Display servers
        ServerManager.list_servers(servers)
        
        # Get user selection
        selection = input("\nSelect server (enter number): ")
        server = ServerManager.select_server(servers, selection)
        
        if not server:
            print("Invalid selection")
            sys.exit(1)
        
        # Connect to server
        SSHConnector.connect(server)
        
    except (DatabaseError, GroupNotFoundError) as e:
        print(f"Database error: {e}")
        sys.exit(1)
    except SSHConnectionError as e:
        print(f"SSH error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)

if __name__ == '__main__':
    main()
