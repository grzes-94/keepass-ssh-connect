"""Tests for server module."""
import pytest
from unittest.mock import Mock, patch
from keepass_ssh.server import ServerManager, ServerEntry

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

def test_parse_server_url():
    """Test server URL parsing."""
    # Test URL with port
    hostname, port = ServerManager.parse_server_url("test.server.com:2222")
    assert hostname == "test.server.com"
    assert port == 2222
    
    # Test URL without port
    hostname, port = ServerManager.parse_server_url("test.server.com")
    assert hostname == "test.server.com"
    assert port == 22

def test_from_keepass_entry():
    """Test creating ServerEntry from KeePass entry."""
    entry = Mock()
    entry.title = "Test Server"
    entry.username = "test_user"
    entry.password = "test_pass"
    entry.url = "test.server.com:22"
    entry.notes = "Test server description"
    
    server = ServerManager.from_keepass_entry(entry)
    assert isinstance(server, ServerEntry)
    assert server.title == entry.title
    assert server.username == entry.username
    assert server.password == entry.password
    assert server.url == entry.url
    assert server.hostname == "test.server.com"
    assert server.port == 22
    assert server.description == entry.notes

def test_list_servers(capsys, server_entry):
    """Test server listing output."""
    ServerManager.list_servers([server_entry])
    captured = capsys.readouterr()
    assert server_entry.title in captured.out
    assert server_entry.url in captured.out
    assert server_entry.description in captured.out

def test_select_server_valid(server_entry):
    """Test valid server selection."""
    servers = [server_entry]
    selected = ServerManager.select_server(servers, "1")
    assert selected == server_entry

def test_select_server_invalid(server_entry):
    """Test invalid server selection."""
    servers = [server_entry]
    # Test invalid index
    assert ServerManager.select_server(servers, "0") is None
    assert ServerManager.select_server(servers, "2") is None
    # Test invalid input
    assert ServerManager.select_server(servers, "invalid") is None
