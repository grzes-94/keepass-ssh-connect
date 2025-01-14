"""Tests for database module."""
import pytest
from unittest.mock import Mock, patch
from keepass_ssh.database import KeePassDatabase, DatabaseError, GroupNotFoundError

@pytest.fixture
def mock_keepass_entry():
    """Create a mock KeePass entry."""
    entry = Mock()
    entry.title = "Test Server"
    entry.username = "test_user"
    entry.password = "test_pass"
    entry.url = "test.server.com:22"
    entry.notes = "Test server description"
    return entry

@pytest.fixture
def mock_db():
    """Create a mock PyKeePass database."""
    db = Mock()
    db.entries = []
    db.root_group = Mock()
    return db

def test_database_initialization():
    """Test database initialization."""
    with patch('keepass_ssh.database.PyKeePass') as mock_keepass:
        db = KeePassDatabase("test.kdbx", "test.key")
        mock_keepass.assert_called_once_with("test.kdbx", keyfile="test.key")

def test_database_error():
    """Test database error handling."""
    with patch('keepass_ssh.database.PyKeePass', side_effect=Exception("Test error")):
        with pytest.raises(DatabaseError, match="Error opening KeePass database: Test error"):
            KeePassDatabase("test.kdbx")

def test_get_entries_all(mock_db, mock_keepass_entry):
    """Test getting all entries."""
    mock_db.entries = [mock_keepass_entry]
    with patch('keepass_ssh.database.PyKeePass', return_value=mock_db):
        db = KeePassDatabase("test.kdbx")
        entries = db.get_entries()
        assert len(entries) == 1
        assert entries[0] == mock_keepass_entry

def test_get_entries_root(mock_db, mock_keepass_entry):
    """Test getting root entries."""
    mock_keepass_entry.group = mock_db.root_group
    mock_db.entries = [mock_keepass_entry]
    with patch('keepass_ssh.database.PyKeePass', return_value=mock_db):
        db = KeePassDatabase("test.kdbx")
        entries = db.get_entries("root")
        assert len(entries) == 1
        assert entries[0] == mock_keepass_entry

def test_get_entries_group(mock_db, mock_keepass_entry):
    """Test getting entries from a specific group."""
    group = Mock()
    group.entries = [mock_keepass_entry]
    mock_db.find_groups.return_value = group
    with patch('keepass_ssh.database.PyKeePass', return_value=mock_db):
        db = KeePassDatabase("test.kdbx")
        entries = db.get_entries("Test/Group")
        assert len(entries) == 1
        assert entries[0] == mock_keepass_entry

def test_get_entries_group_not_found(mock_db):
    """Test error when group is not found."""
    mock_db.find_groups.return_value = None
    with patch('keepass_ssh.database.PyKeePass', return_value=mock_db):
        db = KeePassDatabase("test.kdbx")
        with pytest.raises(GroupNotFoundError):
            db.get_entries("NonExistent/Group")
