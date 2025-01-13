"""
Tests for the server_connect module.
"""
# Standard library imports
import os
import sys
import pytest
from unittest.mock import Mock, patch

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Local imports
from server_connect import (
    get_server_entries,
    list_servers,
    select_server,
    connect_to_server,
    load_keepass_db
)
from pykeepass import PyKeePass

# Test data
TEST_SERVER = {
    "title": "Test Server",
    "username": "test_user",
    "password": "test_pass",
    "url": "test.server.com:22",
    "description": "Test server description"
}

@pytest.fixture
def mock_keepass_entry():
    """Create a mock KeePass entry for testing."""
    entry = Mock()
    entry.title = TEST_SERVER["title"]
    entry.username = TEST_SERVER["username"]
    entry.password = TEST_SERVER["password"]
    entry.url = TEST_SERVER["url"]
    entry.notes = TEST_SERVER["description"]
    return entry

@pytest.fixture
def mock_keepass_db(mock_keepass_entry):
    """Create a mock KeePass database with test entries."""
    db = Mock()
    db.entries = [mock_keepass_entry]
    return db

def test_get_server_entries(mock_keepass_db):
    """Test that server entries are correctly extracted from the database."""
    servers = get_server_entries(mock_keepass_db)
    assert len(servers) == 1
    assert servers[0] == TEST_SERVER

@patch('builtins.print')
def test_list_servers(mock_print):
    """Test that servers are correctly displayed."""
    servers = [TEST_SERVER]
    list_servers(servers)
    mock_print.assert_called()

@patch('builtins.input', return_value='1')
def test_select_server_valid_input(mock_input):
    """Test server selection with valid input."""
    servers = [TEST_SERVER]
    selected = select_server(servers)
    assert selected == TEST_SERVER

@patch('builtins.input', return_value='2')
def test_select_server_invalid_input(mock_input):
    """Test server selection with invalid input exits the script."""
    servers = [TEST_SERVER]
    with pytest.raises(SystemExit):
        select_server(servers)

@patch('subprocess.run')
def test_connect_to_server(mock_subprocess):
    """Test SSH connection command execution."""
    connect_to_server("test.server.com", "test_user", "test_pass", 22)
    mock_subprocess.assert_called_once()

@patch('server_connect.PyKeePass')
def test_load_keepass_db(mock_keepass_class):
    """Test successful KeePass database loading."""
    db_path = "test.kdbx"
    key_path = "test.key"
    
    mock_db = Mock()
    mock_keepass_class.return_value = mock_db
    
    db = load_keepass_db(db_path, key_path)
    
    mock_keepass_class.assert_called_once_with(db_path, keyfile=key_path)
    assert db == mock_db

@patch('server_connect.PyKeePass')
def test_load_keepass_db_error(mock_keepass_class):
    """Test KeePass database loading with error."""
    db_path = "nonexistent.kdbx"
    mock_keepass_class.side_effect = Exception("Test error")
    
    with pytest.raises(SystemExit):
        load_keepass_db(db_path)
