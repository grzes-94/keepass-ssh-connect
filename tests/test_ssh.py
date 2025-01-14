"""Tests for SSH module."""
import os
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

def test_ssh_connect_posix(server_entry, monkeypatch):
    """Test SSH connection on POSIX systems."""
    monkeypatch.setattr(os, 'name', 'posix')
    
    with patch('subprocess.run') as mock_run:
        SSHConnector.connect(server_entry)
        mock_run.assert_called_once_with(
            f'sshpass -p "{server_entry.password}" ssh -p {server_entry.port} {server_entry.username}@{server_entry.hostname}', 
            shell=True, 
            check=True
        )

def test_ssh_connect_windows(server_entry, monkeypatch):
    """Test SSH connection on Windows."""
    monkeypatch.setattr(os, 'name', 'nt')
    
    with patch('subprocess.run') as mock_run:
        SSHConnector.connect(server_entry)
        mock_run.assert_called_once_with(
            f'plink -ssh -P {server_entry.port} {server_entry.username}@{server_entry.hostname} -pw "{server_entry.password}"', 
            shell=True, 
            check=True
        )

def test_ssh_connect_no_password(server_entry, monkeypatch):
    """Test SSH connection without password."""
    server_entry.password = ''
    
    with patch('subprocess.run') as mock_run:
        # Test POSIX case
        monkeypatch.setattr(os, 'name', 'posix')
        SSHConnector.connect(server_entry)
        mock_run.assert_called_once_with(
            f'ssh -p {server_entry.port} {server_entry.username}@{server_entry.hostname}', 
            shell=True, 
            check=True
        )
        
        # Reset mock
        mock_run.reset_mock()
        
        # Test Windows case
        monkeypatch.setattr(os, 'name', 'nt')
        SSHConnector.connect(server_entry)
        mock_run.assert_called_once_with(
            f'plink -ssh -P {server_entry.port} {server_entry.username}@{server_entry.hostname}', 
            shell=True, 
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
