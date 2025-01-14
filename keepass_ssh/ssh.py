"""SSH connection module."""
import subprocess
from typing import Optional
from .server import ServerEntry

class SSHConnector:
    """SSH connection handler."""
    
    @staticmethod
    def connect(server: ServerEntry) -> None:
        """Connect to server using SSH."""
        command = [
            'ssh',
            '-p', str(server.port),
            f'{server.username}@{server.hostname}'
        ]
        
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            raise SSHConnectionError(f"Failed to connect to {server.hostname}: {e}")
        except FileNotFoundError:
            raise SSHConnectionError("SSH client not found. Please install OpenSSH.")

class SSHConnectionError(Exception):
    """SSH connection error."""
    pass
