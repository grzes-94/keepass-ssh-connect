"""Tests for SSH module."""
import pytest
from unittest.mock import patch
from subprocess import CalledProcessError
from keepass_ssh.ssh import SSHConnector, SSHConnectionError
from keepass_ssh.server import ServerEntry

@pytest.fixture
def server_entry():
    """Create a test server entry."""
    return ServerEntry(
        title="Test Server",
        username="test_user",
        password="test_pass",
        url="test.server.com:22",
        hostname="test.server.com",
        port=22,
        description="Test server description"
    )

def test_ssh_connect_success(server_entry):
    """Test successful SSH connection."""
    with patch('subprocess.run') as mock_run:
        SSHConnector.connect(server_entry)
        mock_run.assert_called_once_with(
            ['ssh', '-p', '22', 'test_user@test.server.com'],
            check=True
        )

def test_ssh_connect_error(server_entry):
    """Test SSH connection error."""
    with patch('subprocess.run', side_effect=FileNotFoundError()):
        with pytest.raises(SSHConnectionError, match="SSH client not found"):
            SSHConnector.connect(server_entry)

def test_ssh_connect_process_error(server_entry):
    """Test SSH process error."""
    with patch('subprocess.run', side_effect=CalledProcessError(1, "ssh")):
        with pytest.raises(SSHConnectionError):
            SSHConnector.connect(server_entry)
