"""
Simple memory-based storage module to replace MongoDB functionality.
This module provides a drop-in replacement for the MongoDB database,
but stores all data in memory (which means data is lost on restart).
"""

import os
import json
import time
import logging
import datetime
from typing import Dict, List, Any, Optional, Union

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memory-db")

class MemoryStorage:
    """In-memory database replacement for MongoDB"""
    
    def __init__(self):
        self.collections = {
            "guilds": {},
            "users": {},
            "commands": [],
            "stats": {},
            "settings": {}
        }
        self.connected = True
        logger.info("Initialized memory storage")
    
    def insert_one(self, collection: str, document: Dict[str, Any]) -> bool:
        """Insert a document into a collection"""
        if collection not in self.collections:
            self.collections[collection] = {}
        
        # Ensure document has _id
        if "_id" not in document:
            document["_id"] = str(int(time.time())) + str(hash(str(document)))
        
        self.collections[collection][document["_id"]] = document
        return True
    
    def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a document in a collection"""
        if collection not in self.collections:
            return None
            
        # Simple query matching
        for doc_id, doc in self.collections[collection].items():
            matches = True
            for key, value in query.items():
                if key not in doc or doc[key] != value:
                    matches = False
                    break
            if matches:
                return doc
        return None
    
    def update_one(self, collection: str, query: Dict[str, Any], 
                  update: Dict[str, Any], upsert: bool = False) -> bool:
        """Update a document in a collection"""
        if collection not in self.collections:
            if not upsert:
                return False
            self.collections[collection] = {}
            
        # Find the document
        doc = self.find_one(collection, query)
        
        # Handle upsert case
        if doc is None and upsert:
            # Create new document with query fields
            new_doc = query.copy()
            # Apply updates
            if "$set" in update:
                for key, value in update["$set"].items():
                    new_doc[key] = value
            # Insert new document
            self.insert_one(collection, new_doc)
            return True
        
        # Update existing document
        if doc is not None:
            if "$set" in update:
                for key, value in update["$set"].items():
                    doc[key] = value
            if "$inc" in update:
                for key, value in update["$inc"].items():
                    if key not in doc:
                        doc[key] = 0
                    doc[key] += value
            return True
            
        return False
    
    def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        """Delete a document from a collection"""
        if collection not in self.collections:
            return False
            
        # Find the document
        doc = self.find_one(collection, query)
        if doc is None:
            return False
            
        # Delete the document
        del self.collections[collection][doc["_id"]]
        return True
    
    def find(self, collection: str, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Find documents in a collection"""
        if collection not in self.collections:
            return []
            
        if query is None:
            # Return all documents
            return list(self.collections[collection].values())
            
        # Simple query matching
        results = []
        for doc_id, doc in self.collections[collection].items():
            matches = True
            for key, value in query.items():
                if key not in doc or doc[key] != value:
                    matches = False
                    break
            if matches:
                results.append(doc)
        return results
    
    def count_documents(self, collection: str, query: Dict[str, Any] = None) -> int:
        """Count documents in a collection"""
        return len(self.find(collection, query))
    
    def aggregate(self, collection: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple aggregation support"""
        if collection not in self.collections:
            return []
            
        # Very basic aggregation support - just return all documents
        logger.warning("Memory storage has limited aggregation support")
        return list(self.collections[collection].values())
    
    def drop_collection(self, collection: str) -> bool:
        """Drop a collection"""
        if collection in self.collections:
            self.collections[collection] = {}
            return True
        return False
    
    def save_to_file(self, filename: str = "memory_db_backup.json") -> bool:
        """Save the current database state to a file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.collections, f, indent=2, default=str)
            logger.info(f"Saved memory database to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save database to file: {e}")
            return False
    
    def load_from_file(self, filename: str = "memory_db_backup.json") -> bool:
        """Load database state from a file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    self.collections = json.load(f)
                logger.info(f"Loaded memory database from {filename}")
                return True
            else:
                logger.warning(f"Database file {filename} not found")
                return False
        except Exception as e:
            logger.error(f"Failed to load database from file: {e}")
            return False

class Database:
    """Database interface that provides MongoDB-compatible API but uses MemoryStorage"""
    
    def __init__(self):
        """Initialize the database connection"""
        self.db = None
        self.client = None
        self.storage = MemoryStorage()
        self.connected = True
        self.debug_mode = os.environ.get("DB_DEBUG", "false").lower() == "true"
        
        if self.debug_mode:
            logger.setLevel(logging.DEBUG)
        
        logger.info("Database initialized with memory storage")
        
    def connect(self) -> bool:
        """Connect to the database (no-op for memory storage)"""
        self.connected = True
        logger.info("Database connection simulated (using memory storage)")
        return True
        
    def disconnect(self) -> bool:
        """Disconnect from the database"""
        self.connected = False
        logger.info("Database disconnected")
        return True
    
    def is_connected(self) -> bool:
        """Check if the database is connected"""
        return self.connected
    
    def get_guild_data(self, guild_id: Union[int, str]) -> Optional[Dict[str, Any]]:
        """Get guild data from the database"""
        guild_id = str(guild_id)
        return self.storage.find_one("guilds", {"guild_id": guild_id})
    
    def set_guild_data(self, guild_id: Union[int, str], data: Dict[str, Any]) -> bool:
        """Set guild data in the database"""
        guild_id = str(guild_id)
        return self.storage.update_one(
            "guilds", 
            {"guild_id": guild_id}, 
            {"$set": data}, 
            upsert=True
        )
    
    def get_user_data(self, user_id: Union[int, str]) -> Optional[Dict[str, Any]]:
        """Get user data from the database"""
        user_id = str(user_id)
        return self.storage.find_one("users", {"user_id": user_id})
    
    def set_user_data(self, user_id: Union[int, str], data: Dict[str, Any]) -> bool:
        """Set user data in the database"""
        user_id = str(user_id)
        return self.storage.update_one(
            "users", 
            {"user_id": user_id}, 
            {"$set": data}, 
            upsert=True
        )
    
    def log_command(self, guild_id: Optional[Union[int, str]], 
                   user_id: Union[int, str], command: str) -> bool:
        """Log a command execution to the database"""
        log_entry = {
            "guild_id": str(guild_id) if guild_id else None,
            "user_id": str(user_id),
            "command": command,
            "timestamp": datetime.datetime.now()
        }
        return self.storage.insert_one("commands", log_entry)
    
    def get_command_stats(self) -> Dict[str, Any]:
        """Get command usage statistics"""
        commands = self.storage.find("commands")
        
        # Count total commands
        total_commands = len(commands)
        
        # Count unique users and guilds
        unique_users = set()
        unique_guilds = set()
        command_counts = {}
        
        for cmd in commands:
            unique_users.add(cmd.get("user_id"))
            if cmd.get("guild_id"):
                unique_guilds.add(cmd.get("guild_id"))
            
            command_name = cmd.get("command")
            if command_name not in command_counts:
                command_counts[command_name] = 0
            command_counts[command_name] += 1
        
        return {
            "total_commands": total_commands,
            "unique_users": len(unique_users),
            "unique_guilds": len(unique_guilds),
            "command_distribution": command_counts
        }
    
    def get_guild_setting(self, guild_id: Union[int, str], key: str) -> Any:
        """Get a guild setting"""
        guild_id = str(guild_id)
        guild_data = self.storage.find_one("guilds", {"guild_id": guild_id})
        if guild_data and "settings" in guild_data and key in guild_data["settings"]:
            return guild_data["settings"][key]
        return None
    
    def set_guild_setting(self, guild_id: Union[int, str], key: str, value: Any) -> bool:
        """Set a guild setting"""
        guild_id = str(guild_id)
        guild_data = self.storage.find_one("guilds", {"guild_id": guild_id})
        
        if not guild_data:
            guild_data = {"guild_id": guild_id, "settings": {}}
            self.storage.insert_one("guilds", guild_data)
        
        if "settings" not in guild_data:
            guild_data["settings"] = {}
        
        guild_data["settings"][key] = value
        
        return self.storage.update_one(
            "guilds", 
            {"guild_id": guild_id}, 
            {"$set": {"settings": guild_data["settings"]}}, 
            upsert=True
        )
    
    def get_guild_language(self, guild_id: Union[int, str]) -> str:
        """Get a guild's language setting"""
        lang = self.get_guild_setting(guild_id, "language")
        return lang if lang else "id"  # Default to Indonesian
    
    def set_guild_language(self, guild_id: Union[int, str], language: str) -> bool:
        """Set a guild's language setting"""
        return self.set_guild_setting(guild_id, "language", language)
    
    def get_guild_prefix(self, guild_id: Union[int, str]) -> str:
        """Get a guild's prefix setting"""
        prefix = self.get_guild_setting(guild_id, "prefix")
        return prefix if prefix else "!"  # Default prefix
    
    def set_guild_prefix(self, guild_id: Union[int, str], prefix: str) -> bool:
        """Set a guild's prefix setting"""
        return self.set_guild_setting(guild_id, "prefix", prefix)
    
    def backup(self) -> bool:
        """Backup the database to a file"""
        return self.storage.save_to_file()
    
    def restore(self) -> bool:
        """Restore the database from a file"""
        return self.storage.load_from_file()
    
    def status(self) -> Dict[str, Any]:
        """Get database status information"""
        return {
            "connected": self.connected,
            "storage_type": "memory",
            "collections": {
                name: len(collection) 
                for name, collection in self.storage.collections.items()
                if isinstance(collection, dict)
            },
            "total_documents": sum(
                len(collection) 
                for collection in self.storage.collections.values() 
                if isinstance(collection, dict)
            ),
            "debug_mode": self.debug_mode
        }
    
    def rebuild(self) -> bool:
        """Rebuild the database"""
        for collection in self.storage.collections:
            if isinstance(self.storage.collections[collection], dict):
                self.storage.collections[collection] = {}
            elif isinstance(self.storage.collections[collection], list):
                self.storage.collections[collection] = []
        logger.info("Database rebuilt (memory storage cleared)")
        return True 