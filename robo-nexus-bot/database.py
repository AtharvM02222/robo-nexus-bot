"""
Supabase Database Interface for Robo Nexus Bot
Uses Supabase REST API instead of direct PostgreSQL connections
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from supabase_api import get_supabase_api

logger = logging.getLogger(__name__)

class BirthdayDatabase:
    """Supabase-based birthday database"""
    
    def __init__(self):
        self.db = get_supabase_api()
    
    def add_birthday(self, user_id: int, birthday: str) -> bool:
        """Add a birthday to the database"""
        try:
            logger.info(f"🎂 [database.py] Adding birthday for user_id: {user_id}, birthday: {birthday}")
            result = self.db.register_birthday(str(user_id), birthday)
            if result:
                logger.info(f"✅ [database.py] Birthday added successfully for user_id: {user_id}")
            else:
                logger.error(f"❌ [database.py] Failed to add birthday for user_id: {user_id}")
            return result
        except Exception as e:
            logger.error(f"💥 [database.py] Error adding birthday: {e}")
            return False
    
    def get_birthday(self, user_id: int) -> Optional[str]:
        """Get a user's birthday"""
        try:
            return self.db.get_birthday(str(user_id))
        except Exception as e:
            logger.error(f"Error getting birthday: {e}")
            return None
    
    def get_all_birthdays(self) -> List[Dict[str, Any]]:
        """Get all birthdays"""
        try:
            birthdays = self.db.get_all_birthdays()
            return [
                {
                    'user_id': int(b['user_id']),
                    'birthday': b['birthday'],
                    'registered_at': b.get('registered_at', datetime.now().isoformat())
                }
                for b in birthdays
            ]
        except Exception as e:
            logger.error(f"Error getting all birthdays: {e}")
            return []
    
    def remove_birthday(self, user_id: int) -> bool:
        """Remove a birthday from the database"""
        try:
            return self.db.remove_birthday(str(user_id))
        except Exception as e:
            logger.error(f"Error removing birthday: {e}")
            return False
    
    def get_birthdays_today(self, today_str: str) -> List[Dict[str, Any]]:
        """Get birthdays for today"""
        try:
            return self.db.get_birthdays_today(today_str)
        except Exception as e:
            logger.error(f"Error getting today's birthdays: {e}")
            return []
    
    def birthday_exists(self, user_id: int) -> bool:
        """Check if a birthday exists for a user"""
        return self.get_birthday(user_id) is not None
    
    def get_birthday_count(self) -> int:
        """Get total number of birthdays"""
        try:
            birthdays = self.get_all_birthdays()
            return len(birthdays)
        except Exception as e:
            logger.error(f"Error getting birthday count: {e}")
            return 0
    
    def get_birthday_channel(self, guild_id: int) -> Optional[int]:
        """Get the configured birthday channel for a server"""
        try:
            channel_id = self.db.get_setting(f'birthday_channel_{guild_id}')
            return int(channel_id) if channel_id else None
        except Exception as e:
            logger.error(f"Error getting birthday channel: {e}")
            return None
    
    def set_birthday_channel(self, guild_id: int, channel_id: int) -> bool:
        """Set the birthday announcement channel for a server"""
        try:
            return self.db.set_setting(f'birthday_channel_{guild_id}', str(channel_id))
        except Exception as e:
            logger.error(f"Error setting birthday channel: {e}")
            return False

# Global instances for backward compatibility
birthday_db = BirthdayDatabase()

# Legacy functions for backward compatibility
def add_birthday(user_id: int, birthday: str) -> bool:
    return birthday_db.add_birthday(user_id, birthday)

def get_birthday(user_id: int) -> Optional[str]:
    return birthday_db.get_birthday(user_id)

def get_all_birthdays() -> List[Dict[str, Any]]:
    return birthday_db.get_all_birthdays()

def remove_birthday(user_id: int) -> bool:
    return birthday_db.remove_birthday(user_id)

def birthday_exists(user_id: int) -> bool:
    return birthday_db.birthday_exists(user_id)

def get_birthday_count() -> int:
    return birthday_db.get_birthday_count()

def get_birthday_channel(guild_id: int) -> Optional[int]:
    return birthday_db.get_birthday_channel(guild_id)

def set_birthday_channel(guild_id: int, channel_id: int) -> bool:
    return birthday_db.set_birthday_channel(guild_id, channel_id)