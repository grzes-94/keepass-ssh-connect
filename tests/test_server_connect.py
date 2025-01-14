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
    load_keepass_db,
    parse_server_url
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

@pytest.fixture
def mock_group():
    """Create a mock KeePass group for testing."""
    group = Mock()
    group.entries = [mock_keepass_entry()]
    return group

@pytest.fixture
def mock_root_group():
    """Create a mock KeePass root group."""
    root = Mock()
    root.name = "Root"
    return root

@pytest.fixture
def mock_entry_with_group(mock_keepass_entry, mock_root_group):
    """Create a mock entry with a non-root group."""
    entry = mock_keepass_entry
    group = Mock()
    group.name = "Servers"
    group.entries = [entry]
    entry.group = group
    return entry

@pytest.fixture
def mock_root_entry(mock_keepass_entry, mock_root_group):
    """Create a mock entry at root level."""
    entry = mock_keepass_entry
    entry.group = mock_root_group
    return entry

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

def test_parse_server_url():
    """Test server URL parsing with and without port."""
    from server_connect import parse_server_url
    
    # Test URL with port
    hostname, port = parse_server_url("example.com:2222")
    assert hostname == "example.com"
    assert port == 2222
    
    # Test URL without port
    hostname, port = parse_server_url("example.com")
    assert hostname == "example.com"
    assert port == 22

@patch('server_connect.PyKeePass')
def test_get_server_entries_with_group(mock_keepass_class, mock_group, mock_keepass_db):
    """Test getting server entries from a specific group."""
    mock_keepass_db.find_groups.return_value = mock_group
    
    servers = get_server_entries(mock_keepass_db, "Root/Servers/Production")
    
    mock_keepass_db.find_groups.assert_called_once_with(path="Root/Servers/Production", first=True)
    assert len(servers) == 1
    assert servers[0]["hostname"] == "test.server.com"
    assert servers[0]["port"] == 22

@patch('server_connect.PyKeePass')
def test_get_server_entries_group_not_found(mock_keepass_class, mock_keepass_db):
    """Test behavior when specified group is not found."""
    mock_keepass_db.find_groups.return_value = None
    
    with pytest.raises(SystemExit):
        get_server_entries(mock_keepass_db, "NonexistentGroup")

@patch('server_connect.PyKeePass')
def test_get_root_level_entries(mock_keepass_class, mock_keepass_db, mock_root_entry, mock_root_group):
    """Test getting only root-level entries."""
    mock_keepass_db.entries = [mock_root_entry]
    mock_keepass_db.root_group = mock_root_group
    
    servers = get_server_entries(mock_keepass_db, "root")
    
    assert len(servers) == 1
    assert servers[0]["title"] == TEST_SERVER["title"]
    assert servers[0]["hostname"] == "test.server.com"

@patch('server_connect.PyKeePass')
def test_get_entries_with_group(mock_keepass_class, mock_keepass_db, mock_entry_with_group):
    """Test getting entries from a specific group."""
    mock_keepass_db.entries = [mock_entry_with_group]
    mock_keepass_db.find_groups.return_value = mock_entry_with_group.group
    
    servers = get_server_entries(mock_keepass_db, "Servers")
    
    assert len(servers) == 1
    assert servers[0]["title"] == TEST_SERVER["title"]
