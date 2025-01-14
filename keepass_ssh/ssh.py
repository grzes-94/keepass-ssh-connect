"""SSH connection module."""
import os
import subprocess
from .server import ServerEntry

class SSHConnector:
    """SSH connection handler."""
    
    @staticmethod
    def connect(server: ServerEntry) -> None:
        """
        Connect to server using SSH with platform-specific command.
        
        :param server: Server entry with connection details
        """
        # Prepare SSH command based on operating system
        if os.name == 'nt':  # Windows
            # Use Plink (PuTTY's command-line SSH client)
            ssh_command = f'plink -ssh -P {server.port} {server.username}@{server.hostname}'
            
            # Add password if available
            if server.password:
                ssh_command += f' -pw "{server.password}"'
        else:  # Unix-like systems
            # Use standard SSH command
            ssh_command = f'ssh -p {server.port} {server.username}@{server.hostname}'
            
            # Add sshpass for password if available
            if server.password:
                ssh_command = f'sshpass -p "{server.password}" {ssh_command}'
        
        try:
            # Run the SSH connection
            subprocess.run(ssh_command, shell=True, check=True)
        
        except subprocess.CalledProcessError as e:
            raise SSHConnectionError(f"Failed to connect to {server.hostname}: {e}")
        except FileNotFoundError:
            raise SSHConnectionError(f"SSH client not found on {os.name}. "
                                     "Please install OpenSSH or PuTTY.")

class SSHConnectionError(Exception):
    """SSH connection error."""
    pass
