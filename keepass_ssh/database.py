"""Database management module."""
from typing import Optional, List, Dict
from pykeepass import PyKeePass

class KeePassDatabase:
    """KeePass database handler."""
    
    def __init__(self, db_path: str, key_path: Optional[str] = None):
        """Initialize database connection."""
        self.db_path = db_path
        self.key_path = key_path
        self.db = self._load_database()
    
    def _load_database(self) -> PyKeePass:
        """Load the KeePass database."""
        try:
            return PyKeePass(self.db_path, keyfile=self.key_path)
        except Exception as e:
            raise DatabaseError(f"Error opening KeePass database: {e}")
    
    def get_entries(self, group_path: Optional[str] = None) -> List[Dict]:
        """Get entries from the database."""
        entries = []
        
        if group_path == "root":
            # Get only root-level entries
            entries = [e for e in self.db.entries if e.group == self.db.root_group]
        elif group_path:
            # Get entries from specific group
            group = self.db.find_groups(path=group_path, first=True)
            if not group:
                raise GroupNotFoundError(f"Group {group_path} not found")
            entries = group.entries
        else:
            # Get all entries
            entries = self.db.entries
            
        return entries

class DatabaseError(Exception):
    """Database operation error."""
    pass

class GroupNotFoundError(Exception):
    """Group not found in database."""
    pass
