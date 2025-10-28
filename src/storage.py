"""
Persistent storage for Career Coach Discord Bot.

Handles saving and loading user contexts, interview sessions, and other
persistent data using JSON files.
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from utils.logger import setup_logger


class BotStorage:
    """
    Handles persistent storage for Discord bot data.
    
    Features:
    - User conversation contexts
    - Interview sessions  
    - User profiles and preferences
    - Automatic backup and recovery
    """
    
    def __init__(self, data_dir: str = "data", log_level: str = "INFO"):
        """
        Initialize storage with data directory.
        
        Args:
            data_dir: Directory to store data files
            log_level: Logging level
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Storage file paths
        self.user_contexts_file = self.data_dir / "user_contexts.json"
        self.interview_sessions_file = self.data_dir / "interview_sessions.json"
        self.user_profiles_file = self.data_dir / "user_profiles.json"
        self.backup_dir = self.data_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        self.logger = setup_logger(__name__, log_level)
        self.logger.info(f"Storage initialized - Data dir: {self.data_dir}")
    
    def save_user_contexts(self, user_contexts: Dict[int, Dict[str, Any]]) -> bool:
        """
        Save user conversation contexts to file.
        
        Args:
            user_contexts: Dictionary of user contexts by user ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert int keys to strings for JSON serialization
            serializable_contexts = {
                str(user_id): context 
                for user_id, context in user_contexts.items()
            }
            
            # Add metadata
            data = {
                "saved_at": datetime.now().isoformat(),
                "user_count": len(serializable_contexts),
                "contexts": serializable_contexts
            }
            
            # Create backup of existing file
            if self.user_contexts_file.exists():
                self._create_backup(self.user_contexts_file)
            
            # Save to file
            with open(self.user_contexts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(serializable_contexts)} user contexts")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save user contexts: {e}")
            return False
    
    def load_user_contexts(self) -> Dict[int, Dict[str, Any]]:
        """
        Load user conversation contexts from file.
        
        Returns:
            Dictionary of user contexts by user ID
        """
        try:
            if not self.user_contexts_file.exists():
                self.logger.info("No existing user contexts file found")
                return {}
            
            with open(self.user_contexts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert string keys back to integers
            contexts = data.get("contexts", {})
            user_contexts = {
                int(user_id): context 
                for user_id, context in contexts.items()
            }
            
            saved_at = data.get("saved_at", "unknown")
            self.logger.info(f"Loaded {len(user_contexts)} user contexts (saved at: {saved_at})")
            return user_contexts
            
        except Exception as e:
            self.logger.error(f"Failed to load user contexts: {e}")
            return {}
    
    def save_interview_sessions(self, interview_sessions: Dict[int, Dict]) -> bool:
        """
        Save interview sessions to file.
        
        Args:
            interview_sessions: Dictionary of interview sessions by user ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert int keys to strings for JSON serialization
            serializable_sessions = {
                str(user_id): session 
                for user_id, session in interview_sessions.items()
            }
            
            # Add metadata
            data = {
                "saved_at": datetime.now().isoformat(),
                "active_sessions": len(serializable_sessions),
                "sessions": serializable_sessions
            }
            
            # Create backup
            if self.interview_sessions_file.exists():
                self._create_backup(self.interview_sessions_file)
            
            # Save to file
            with open(self.interview_sessions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(serializable_sessions)} interview sessions")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save interview sessions: {e}")
            return False
    
    def load_interview_sessions(self) -> Dict[int, Dict]:
        """
        Load interview sessions from file.
        
        Returns:
            Dictionary of interview sessions by user ID
        """
        try:
            if not self.interview_sessions_file.exists():
                self.logger.info("No existing interview sessions file found")
                return {}
            
            with open(self.interview_sessions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert string keys back to integers
            sessions = data.get("sessions", {})
            interview_sessions = {
                int(user_id): session 
                for user_id, session in sessions.items()
            }
            
            saved_at = data.get("saved_at", "unknown")
            self.logger.info(f"Loaded {len(interview_sessions)} interview sessions (saved at: {saved_at})")
            return interview_sessions
            
        except Exception as e:
            self.logger.error(f"Failed to load interview sessions: {e}")
            return {}
    
    def save_user_profile(self, user_id: int, profile: Dict[str, Any]) -> bool:
        """
        Save individual user profile.
        
        Args:
            user_id: Discord user ID
            profile: User profile data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing profiles
            profiles = self.load_all_user_profiles()
            
            # Update with new profile
            profiles[user_id] = {
                **profile,
                "updated_at": datetime.now().isoformat()
            }
            
            # Save back to file
            return self._save_user_profiles(profiles)
            
        except Exception as e:
            self.logger.error(f"Failed to save user profile for {user_id}: {e}")
            return False
    
    def load_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Load individual user profile.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            User profile data or None if not found
        """
        try:
            profiles = self.load_all_user_profiles()
            return profiles.get(user_id)
            
        except Exception as e:
            self.logger.error(f"Failed to load user profile for {user_id}: {e}")
            return None
    
    def load_all_user_profiles(self) -> Dict[int, Dict[str, Any]]:
        """Load all user profiles from file."""
        try:
            if not self.user_profiles_file.exists():
                return {}
            
            with open(self.user_profiles_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert string keys back to integers
            profiles = data.get("profiles", {})
            return {
                int(user_id): profile 
                for user_id, profile in profiles.items()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to load user profiles: {e}")
            return {}
    
    def _save_user_profiles(self, profiles: Dict[int, Dict[str, Any]]) -> bool:
        """Internal method to save all user profiles."""
        try:
            # Convert int keys to strings
            serializable_profiles = {
                str(user_id): profile 
                for user_id, profile in profiles.items()
            }
            
            # Add metadata
            data = {
                "saved_at": datetime.now().isoformat(),
                "profile_count": len(serializable_profiles),
                "profiles": serializable_profiles
            }
            
            # Create backup
            if self.user_profiles_file.exists():
                self._create_backup(self.user_profiles_file)
            
            # Save to file
            with open(self.user_profiles_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save user profiles: {e}")
            return False
    
    def _create_backup(self, file_path: Path) -> bool:
        """Create a timestamped backup of a file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_{timestamp}.json"
            backup_path = self.backup_dir / backup_name
            
            # Copy file to backup
            import shutil
            shutil.copy2(file_path, backup_path)
            
            # Keep only last 10 backups per file type
            self._cleanup_old_backups(file_path.stem)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return False
    
    def _cleanup_old_backups(self, file_stem: str, max_backups: int = 10):
        """Keep only the most recent backups."""
        try:
            pattern = f"{file_stem}_*.json"
            backup_files = list(self.backup_dir.glob(pattern))
            
            if len(backup_files) > max_backups:
                # Sort by modification time and remove oldest
                backup_files.sort(key=lambda x: x.stat().st_mtime)
                for old_backup in backup_files[:-max_backups]:
                    old_backup.unlink()
                    
        except Exception as e:
            self.logger.error(f"Failed to cleanup old backups: {e}")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get statistics about stored data."""
        try:
            stats = {
                "data_directory": str(self.data_dir),
                "files": {},
                "total_size_mb": 0
            }
            
            # Check each data file
            for file_path in [self.user_contexts_file, self.interview_sessions_file, self.user_profiles_file]:
                if file_path.exists():
                    size = file_path.stat().st_size
                    stats["files"][file_path.name] = {
                        "exists": True,
                        "size_bytes": size,
                        "size_mb": round(size / (1024 * 1024), 2),
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    }
                    stats["total_size_mb"] += size / (1024 * 1024)
                else:
                    stats["files"][file_path.name] = {"exists": False}
            
            stats["total_size_mb"] = round(stats["total_size_mb"], 2)
            
            # Count backups
            backup_count = len(list(self.backup_dir.glob("*.json")))
            stats["backup_count"] = backup_count
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get storage stats: {e}")
            return {"error": str(e)}
    
    def clear_all_data(self) -> bool:
        """Clear all stored data (use with caution!)."""
        try:
            files_removed = 0
            
            for file_path in [self.user_contexts_file, self.interview_sessions_file, self.user_profiles_file]:
                if file_path.exists():
                    file_path.unlink()
                    files_removed += 1
            
            self.logger.warning(f"Cleared all stored data ({files_removed} files removed)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear data: {e}")
            return False


# Convenience functions for quick usage
def save_bot_data(user_contexts: Dict[int, Dict], interview_sessions: Dict[int, Dict], 
                  data_dir: str = "data") -> bool:
    """Quick function to save both user contexts and interview sessions."""
    storage = BotStorage(data_dir)
    contexts_saved = storage.save_user_contexts(user_contexts)
    sessions_saved = storage.save_interview_sessions(interview_sessions)
    return contexts_saved and sessions_saved


def load_bot_data(data_dir: str = "data") -> tuple[Dict[int, Dict], Dict[int, Dict]]:
    """Quick function to load both user contexts and interview sessions."""
    storage = BotStorage(data_dir)
    user_contexts = storage.load_user_contexts()
    interview_sessions = storage.load_interview_sessions()
    return user_contexts, interview_sessions


# CLI testing function
def main():
    """Test storage functionality."""
    print("🗄️ Testing Bot Storage System")
    print("=" * 40)
    
    storage = BotStorage()
    
    # Test data
    test_contexts = {
        123456: {
            "state": "engaged",
            "conversation_history": [
                {"user": "Hi!", "timestamp": "2025-10-28T10:00:00"},
                {"bot": "Hello! How can I help?", "timestamp": "2025-10-28T10:00:01"}
            ],
            "skills": ["Python", "SQL"]
        }
    }
    
    test_sessions = {
        123456: {
            "role": "Software Engineer",
            "questions": ["Tell me about yourself", "What's your biggest strength?"],
            "current_question": 0,
            "answers": [],
            "session_id": "interview_test123"
        }
    }
    
    # Test saving
    print("\n1. Testing save functionality...")
    contexts_saved = storage.save_user_contexts(test_contexts)
    sessions_saved = storage.save_interview_sessions(test_sessions)
    print(f"   Contexts saved: {contexts_saved}")
    print(f"   Sessions saved: {sessions_saved}")
    
    # Test loading
    print("\n2. Testing load functionality...")
    loaded_contexts = storage.load_user_contexts()
    loaded_sessions = storage.load_interview_sessions()
    print(f"   Contexts loaded: {len(loaded_contexts)} users")
    print(f"   Sessions loaded: {len(loaded_sessions)} sessions")
    
    # Test stats
    print("\n3. Storage statistics:")
    stats = storage.get_storage_stats()
    print(f"   Data directory: {stats['data_directory']}")
    print(f"   Total size: {stats['total_size_mb']} MB")
    print(f"   Backup count: {stats['backup_count']}")
    
    print("\n✅ Storage system test completed!")


if __name__ == "__main__":
    main()