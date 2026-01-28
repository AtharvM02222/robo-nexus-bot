"""
PostgreSQL Database Interface for Robo Nexus Bot
Replaces the SQLite database.py with PostgreSQL functionality
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from postgres_db import get_db

logger = logging.getLogger(__name__)

class BirthdayDatabase:
    """PostgreSQL-based birthday database"""
    
    def __init__(self):
        self.db = get_db()
    
    def add_birthday(self, user_id: int, birthday: str) -> bool:
        """Add a birthday to the database"""
        try:
            return self.db.add_birthday(str(user_id), birthday)
        except Exception as e:
            logger.error(f"Error adding birthday: {e}")
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
                    'registered_at': b['registered_at']
                }
                for b in birthdays
            ]
        except Exception as e:
            logger.error(f"Error getting all birthdays: {e}")
            return []
    
    def remove_birthday(self, user_id: int) -> bool:
        """Remove a birthday from the database"""
        try:
            return self.db.delete_birthday(str(user_id))
        except Exception as e:
            logger.error(f"Error removing birthday: {e}")
            return False
    
    def get_birthdays_today(self, today_str: str) -> List[Dict[str, Any]]:
        """Get birthdays for today"""
        try:
            all_birthdays = self.get_all_birthdays()
            return [b for b in all_birthdays if b['birthday'] == today_str]
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

class UserProfileDatabase:
    """PostgreSQL-based user profile database"""
    
    def __init__(self):
        self.db = get_db()
    
    def create_profile(self, user_data: Dict[str, Any]) -> bool:
        """Create or update user profile"""
        try:
            if 'user_id' in user_data and isinstance(user_data['user_id'], int):
                user_data['user_id'] = str(user_data['user_id'])
            
            return self.db.create_user_profile(user_data)
        except Exception as e:
            logger.error(f"Error creating profile: {e}")
            return False
    
    def get_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        try:
            return self.db.get_user_profile(str(user_id))
        except Exception as e:
            logger.error(f"Error getting profile: {e}")
            return None
    
    def update_profile(self, user_id: int, updates: Dict[str, Any]) -> bool:
        """Update user profile"""
        try:
            return self.db.update_user_profile(str(user_id), updates)
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            return False
    
    def profile_exists(self, user_id: int) -> bool:
        """Check if profile exists"""
        return self.get_profile(user_id) is not None

class WelcomeDatabase:
    """PostgreSQL-based welcome system database"""
    
    def __init__(self):
        self.db = get_db()
    
    def set_user_data(self, user_id: int, stage: str, data: Dict[str, Any]) -> bool:
        """Set welcome verification data"""
        try:
            return self.db.set_welcome_data(str(user_id), stage, data)
        except Exception as e:
            logger.error(f"Error setting welcome data: {e}")
            return False
    
    def get_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get welcome verification data"""
        try:
            return self.db.get_welcome_data(str(user_id))
        except Exception as e:
            logger.error(f"Error getting welcome data: {e}")
            return None
    
    def remove_user_data(self, user_id: int) -> bool:
        """Remove welcome verification data"""
        try:
            return self.db.delete_welcome_data(str(user_id))
        except Exception as e:
            logger.error(f"Error removing welcome data: {e}")
            return False

class AnalyticsDatabase:
    """PostgreSQL-based analytics database"""
    
    def __init__(self):
        self.db = get_db()
    
    def log_event(self, event_type: str, user_id: int = None, data: Dict[str, Any] = None) -> bool:
        """Log an analytics event"""
        try:
            user_id_str = str(user_id) if user_id else None
            return self.db.log_analytics(event_type, user_id_str, data)
        except Exception as e:
            logger.error(f"Error logging analytics: {e}")
            return False
    
    def get_events(self, event_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get analytics events"""
        try:
            return self.db.get_analytics(event_type, limit)
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return []

# Global instances for backward compatibility
birthday_db = BirthdayDatabase()
profile_db = UserProfileDatabase()
welcome_db = WelcomeDatabase()
analytics_db = AnalyticsDatabase()

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