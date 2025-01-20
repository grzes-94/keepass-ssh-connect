import os
import sys
import glob
import logging
import argparse

from dotenv import load_dotenv
from colorama import init as init_colorama

from .database import KeePassDatabase, DatabaseError, GroupNotFoundError
from .server import ServerManager
from .ssh import SSHConnector, SSHConnectionError

# Constants
DEFAULT_GROUP_PATH = 'root'

class KeePassSSHCLI:
    """
    A CLI utility for managing SSH connections via KeePass database.
    
    This class handles argument parsing, server discovery, and connection 
    management for SSH servers stored in a KeePass database.
    """
    
    def __init__(self, verbose=False):
        """
        Initialize the CLI utility.
        
        Args:
            verbose (bool, optional): Enable verbose logging. Defaults to False.
        """
        self.verbose = verbose
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure logging based on verbosity."""
        if self.verbose:
            logging.basicConfig(
                level=logging.INFO, 
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
    
    @staticmethod
    def find_keepass_files():
        """
        Find KeePass database and key files in the current directory.
        
        Returns:
            tuple: (database_path, key_path)
        """
        database_files = glob.glob('*.kdbx')
        key_files = glob.glob('*.keyx')
        
        database_path = database_files[0] if database_files else None
        key_path = key_files[0] if key_files else None
        
        return database_path, key_path
    
    @staticmethod
    def validate_file_path(path):
        """
        Validate file path exists.
        
        Args:
            path (str): Path to the file
        
        Raises:
            SystemExit: If file does not exist
        """
        if path and not os.path.exists(path):
            print(f"Error: File not found at {path}")
            sys.exit(1)
        return path
    
    def parse_arguments(self):
        """
        Parse and process command-line arguments.
        
        Returns:
            argparse.Namespace: Parsed arguments
        """
        parser = argparse.ArgumentParser(
            description='KeePass SSH Connection Utility',
            epilog='Connect to SSH servers stored in a KeePass database'
        )
        
        # Read environment variables
        default_db = os.environ.get('KEEPASS_DB_PATH')
        default_key = os.environ.get('KEEPASS_KEY_PATH')
        default_group = os.environ.get('KEEPASS_GROUP_PATH')
        
        parser.add_argument(
            '-d', '--database', 
            help='Path to the KeePass database file',
            default=default_db
        )
        
        parser.add_argument(
            '-k', '--key-file', 
            help='Path to the KeePass key file (optional)',
            default=default_key
        )
        
        parser.add_argument(
            '-g', '--group', 
            help='KeePass group path to filter server entries',
            default=default_group or DEFAULT_GROUP_PATH
        )
        
        parser.add_argument(
            '-s', '--server', 
            help='Specific server name or partial match to connect to'
        )
        
        parser.add_argument(
            '-l', '--list', 
            action='store_true', 
            help='List available servers without connecting'
        )
        
        parser.add_argument(
            '-v', '--verbose', 
            action='store_true', 
            help='Enable verbose output'
        )
        
        # Parse arguments first
        args = parser.parse_args()
        
        # Only auto-discover if no env vars, no arguments, and no server specified
        if not any([args.database, default_db]):
            found_db, found_key = self.find_keepass_files()
            
            if found_db:
                print(f"Using local database file: {found_db}")
                args.database = found_db
                
                if found_key:
                    print(f"Using local key file: {found_key}")
                    args.key_file = found_key
        
        return args
    
    def _log_discovery(self, args):
        """
        Log file discovery details in verbose mode.
        
        Args:
            args (argparse.Namespace): Parsed arguments
        """
        if not self.verbose:
            return
        
        logging.info(f"Verbose mode enabled")
        
        # Log if files were auto-discovered
        if (not os.environ.get('KEEPASS_DB_PATH') and 
            not any(['-d', '--database']) and 
            args.database):
            logging.info(f"Auto-discovered database file: {args.database}")
        
        if (not os.environ.get('KEEPASS_KEY_PATH') and 
            not any(['-k', '--key-file']) and 
            args.key_file):
            logging.info(f"Auto-discovered key file: {args.key_file}")
        
        logging.info(f"Database path: {args.database}")
        logging.info(f"Key file path: {args.key_file}")
        logging.info(f"Group path: {args.group}")
    
    def _select_server(self, servers):
        """
        Interactively select a server from the list.
        
        Args:
            servers (list): List of available servers
        
        Returns:
            Server: Selected server
        
        Raises:
            SystemExit: If no or invalid server is selected
        """
        print("Available Servers:")
        ServerManager.list_servers(servers)
        
        try:
            selection = input("\nSelect server (enter number): ")
            selected_server = servers[int(selection) - 1]
            
            if self.verbose:
                logging.info(f"Selected server: {selected_server.title}")
            
            return selected_server
        except (ValueError, IndexError):
            if self.verbose:
                logging.error(f"Invalid server selection: {selection}")
            
            print("Invalid selection. Exiting.")
            sys.exit(1)
    
    def list_servers(
        self,
        db_path=None, 
        group_path=None, 
        key_path=None
    ):
        """
        List available servers from KeePass database.
        
        Args:
            db_path (str, optional): Path to the KeePass database
            group_path (str, optional): Path to the server group
            key_path (str, optional): Path to the key file
        
        Returns:
            list: List of available servers
        """
        init_colorama()
        load_dotenv()
        
        try:
            # Initialize database connection
            db = KeePassDatabase(db_path, key_path)
            
            # Get server entries
            keepass_entries = db.get_entries(group_path or 'root')
            servers = [ServerManager.from_keepass_entry(entry) for entry in keepass_entries]
            
            if not servers:
                print("No server entries found")
                return []
            
            # Use ServerManager to list servers
            ServerManager.list_servers(servers)
            
            return servers
        
        except (DatabaseError, GroupNotFoundError) as e:
            logging.error(f"Database error: {e}")
            print(f"Error: {e}")
            sys.exit(1)

    def _filter_servers(self, servers, server_filter=None):
        """
        Filter servers based on a given filter.
        
        Args:
            servers (list): List of servers to filter
            server_filter (str, optional): Filter to apply to server titles
        
        Returns:
            list: Filtered list of servers
        """
        if server_filter:
            # First, try exact match
            exact_matches = [
                server for server in servers 
                if server_filter.lower() == server.title.lower()
            ]
            
            # If exact match found, use it
            if exact_matches:
                return exact_matches
            
            # If no exact match, try partial match
            return [
                server for server in servers 
                if server_filter.lower() in server.title.lower()
            ]
        
        return servers

    def _list_and_select_server(self, servers, server_filter=None):
        """
        Select a server from the list.
        
        Args:
            servers (list): List of servers to select from
            server_filter (str, optional): Filter used for server selection
        
        Returns:
            object: Selected server or None
        """
        # Always list servers
        ServerManager.list_servers(servers)
        
        # If server_filter is provided and only one server matches, return it
        if server_filter and len(servers) == 1:
            return servers[0]
        
        # Prompt for server selection
        try:
            selection = input("\nSelect server (enter number): ")
            return ServerManager.select_server(servers, selection)
        except Exception:
            print("Invalid selection")
            return None

    def connect_to_server(
        self,
        db_path=None, 
        group_path=None, 
        key_path=None, 
        server_filter=None
    ):
        """
        Connect to a server from KeePass database.
        
        Args:
            db_path (str, optional): Path to the KeePass database
            group_path (str, optional): Path to the server group
            key_path (str, optional): Path to the key file
            server_filter (str, optional): Filter servers by title
        """
        init_colorama()
        load_dotenv()
        
        try:
            # Initialize database connection
            db = KeePassDatabase(db_path, key_path)
            
            # Get server entries
            keepass_entries = db.get_entries(group_path or 'root')
            servers = [ServerManager.from_keepass_entry(entry) for entry in keepass_entries]
            
            if not servers:
                print("No server entries found")
                sys.exit(1)
            
            # Filter servers
            servers = self._filter_servers(servers, server_filter)
            
            if not servers:
                print(f"No servers found matching '{server_filter}'")
                sys.exit(1)
            
            # Select server
            server = self._list_and_select_server(servers, server_filter)
            
            if not server:
                print("Invalid selection")
                sys.exit(1)
            
            # Connect to server
            SSHConnector.connect(server)
        
        except (DatabaseError, GroupNotFoundError, SSHConnectionError) as e:
            logging.error(f"Connection error: {e}")
            print(f"Error: {e}")
            sys.exit(1)

    def run(self):
        """
        Main entry point for CLI application.
        Handles argument parsing, server discovery, and connection.
        """
        # Parse arguments
        args = self.parse_arguments()
        
        # List servers if requested
        if args.list:
            # Attempt to list servers
            try:
                self.list_servers(
                    db_path=args.database, 
                    key_path=args.key_file, 
                    group_path=args.group
                )
                sys.exit(0)
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
        
        # Connect to server
        try:
            self.connect_to_server(
                db_path=args.database, 
                key_path=args.key_file, 
                group_path=args.group,
                server_filter=args.server
            )
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

def main():
    """Entry point for CLI."""
    cli = KeePassSSHCLI()
    cli.run()

if __name__ == '__main__':
    main()
