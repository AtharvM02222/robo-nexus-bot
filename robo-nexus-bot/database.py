"""
Database Manager for Robo Nexus Birthday Bot
Handles SQLite database operations for birthday storage and server configuration
"""
import aiosqlite
import logging
from datetime import date, datetime
from typing import List, Optional, Tuple
from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for birthday data"""
    
    def __init__(self, db_path: str = None):
        """Initialize database manager with path from config"""
        self.db_path = db_path or Config.DATABASE_PATH
        logger.info(f"Database manager initialized with path: {self.db_path}")
    
    async def init_database(self):
        """Initialize database tables if they don't exist"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Create birthdays table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS birthdays (
                        user_id INTEGER PRIMARY KEY,
                        birthday TEXT NOT NULL,
                        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create server configuration table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS server_config (
                        guild_id INTEGER PRIMARY KEY,
                        birthday_channel_id INTEGER,
                        notification_time TEXT DEFAULT '09:00',
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                await db.commit()
                logger.info("Database tables initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    async def register_birthday(self, user_id: int, birthday: date) -> bool:
        """
        Register or update a user's birthday
        
        Args:
            user_id: Discord user ID
            birthday: Birthday date object
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert date to MM-DD format for storage
            birthday_str = birthday.strftime("%m-%d")
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO birthdays (user_id, birthday, registered_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (user_id, birthday_str))
                
                await db.commit()
                logger.info(f"Birthday registered for user {user_id}: {birthday_str}")
                return True
                
        except Exception as e:
            logger.error(f"Error registering birthday for user {user_id}: {e}")
            return False
    
    async def get_birthday(self, user_id: int) -> Optional[date]:
        """
        Get a user's registered birthday
        
        Args:
            user_id: Discord user ID
            
        Returns:
            date object if found, None otherwise
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT birthday FROM birthdays WHERE user_id = ?",
                    (user_id,)
                )
                result = await cursor.fetchone()
                
                if result:
                    # Parse MM-DD format back to date object (using current year)
                    birthday_str = result[0]
                    month, day = map(int, birthday_str.split('-'))
                    current_year = datetime.now().year
                    return date(current_year, month, day)
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting birthday for user {user_id}: {e}")
            return None
    
    async def remove_birthday(self, user_id: int) -> bool:
        """
        Remove a user's birthday registration
        
        Args:
            user_id: Discord user ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "DELETE FROM birthdays WHERE user_id = ?",
                    (user_id,)
                )
                await db.commit()
                
                deleted = cursor.rowcount > 0
                if deleted:
                    logger.info(f"Birthday removed for user {user_id}")
                else:
                    logger.info(f"No birthday found to remove for user {user_id}")
                
                return deleted
                
        except Exception as e:
            logger.error(f"Error removing birthday for user {user_id}: {e}")
            return False
    
    async def get_todays_birthdays(self) -> List[Tuple[int, date]]:
        """
        Get all users with birthdays today
        
        Returns:
            List of tuples (user_id, birthday_date)
        """
        try:
            today = datetime.now()
            today_str = today.strftime("%m-%d")
            
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT user_id, birthday FROM birthdays WHERE birthday = ?",
                    (today_str,)
                )
                results = await cursor.fetchall()
                
                # Convert back to date objects
                birthdays = []
                for user_id, birthday_str in results:
                    month, day = map(int, birthday_str.split('-'))
                    birthday_date = date(today.year, month, day)
                    birthdays.append((user_id, birthday_date))
                
                logger.info(f"Found {len(birthdays)} birthdays for today ({today_str})")
                return birthdays
                
        except Exception as e:
            logger.error(f"Error getting today's birthdays: {e}")
            return []
    
    async def get_all_birthdays(self) -> List[Tuple[int, date]]:
        """
        Get all registered birthdays sorted chronologically
        
        Returns:
            List of tuples (user_id, birthday_date) sorted by upcoming birthdays
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT user_id, birthday FROM birthdays ORDER BY birthday"
                )
                results = await cursor.fetchall()
                
                # Convert to date objects and sort by next occurrence
                current_year = datetime.now().year
                birthdays = []
                
                for user_id, birthday_str in results:
                    month, day = map(int, birthday_str.split('-'))
                    birthday_date = date(current_year, month, day)
                    
                    # If birthday already passed this year, use next year
                    if birthday_date < date.today():
                        birthday_date = date(current_year + 1, month, day)
                    
                    birthdays.append((user_id, birthday_date))
                
                # Sort by date
                birthdays.sort(key=lambda x: x[1])
                
                logger.info(f"Retrieved {len(birthdays)} registered birthdays")
                return birthdays
                
        except Exception as e:
            logger.error(f"Error getting all birthdays: {e}")
            return []
    
    async def set_birthday_channel(self, guild_id: int, channel_id: int) -> bool:
        """
        Set the birthday announcement channel for a server
        
        Args:
            guild_id: Discord server ID
            channel_id: Discord channel ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO server_config 
                    (guild_id, birthday_channel_id, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (guild_id, channel_id))
                
                await db.commit()
                logger.info(f"Birthday channel set for guild {guild_id}: {channel_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error setting birthday channel for guild {guild_id}: {e}")
            return False
    
    async def get_birthday_channel(self, guild_id: int) -> Optional[int]:
        """
        Get the configured birthday channel for a server
        
        Args:
            guild_id: Discord server ID
            
        Returns:
            Channel ID if configured, None otherwise
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT birthday_channel_id FROM server_config WHERE guild_id = ?",
                    (guild_id,)
                )
                result = await cursor.fetchone()
                
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"Error getting birthday channel for guild {guild_id}: {e}")
            return None
    
    async def close(self):
        """Close database connections (cleanup method)"""
        # aiosqlite connections are automatically closed, but this method
        # is here for future cleanup if needed
        logger.info("Database manager closed")