"""Server management module."""
from typing import Dict, List, Optional
from dataclasses import dataclass
from colorama import Fore, Style

@dataclass
class ServerEntry:
    """Server entry data."""
    title: str
    username: str
    password: str
    url: str
    hostname: str
    port: int
    description: str

class ServerManager:
    """Server entry manager."""
    
    DEFAULT_PORT = 22
    
    @staticmethod
    def parse_server_url(url: str) -> tuple[str, int]:
        """Parse server URL into hostname and port."""
        if ':' in url:
            hostname, port = url.split(':')
            return hostname, int(port)
        return url, ServerManager.DEFAULT_PORT
    
    @classmethod
    def from_keepass_entry(cls, entry) -> ServerEntry:
        """Create ServerEntry from KeePass entry."""
        hostname, port = cls.parse_server_url(entry.url)
        return ServerEntry(
            title=entry.title,
            username=entry.username,
            password=entry.password,
            url=entry.url,
            hostname=hostname,
            port=port,
            description=entry.notes
        )
    
    @staticmethod
    def list_servers(servers: List[ServerEntry]) -> None:
        """Display server list with colors."""
        for i, server in enumerate(servers, 1):
            print(f"{i}. {Fore.GREEN}{server.title}{Style.RESET_ALL}")
            print(f"   URL: {Fore.BLUE}{server.url}{Style.RESET_ALL}")
            if server.description:
                print(f"   Description: {Fore.YELLOW}{server.description}{Style.RESET_ALL}")
            print()
    
    @staticmethod
    def select_server(servers: List[ServerEntry], selection: str) -> Optional[ServerEntry]:
        """Select server from list."""
        try:
            index = int(selection) - 1
            if 0 <= index < len(servers):
                return servers[index]
        except ValueError:
            pass
        return None
