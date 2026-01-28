"""
PostgreSQL Database Handler for Robo Nexus Bot
Handles all database operations for auctions, bids, and requests
"""
import psycopg2
import psycopg2.extras
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

class PostgreSQLHandler:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish connection to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            self.connection.autocommit = True
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def create_tables(self):
        """Create necessary tables for the bot"""
        try:
            cursor = self.connection.cursor()
            
            # Birthdays table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS birthdays (
                    user_id VARCHAR(20) PRIMARY KEY,
                    birthday VARCHAR(10) NOT NULL,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User profiles table (for welcome system)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id VARCHAR(20) PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    display_name VARCHAR(100),
                    email VARCHAR(200),
                    phone VARCHAR(20),
                    class_year VARCHAR(10),
                    birthday VARCHAR(10),
                    social_links JSONB,
                    verification_status VARCHAR(20) DEFAULT 'pending',
                    verification_stage VARCHAR(20) DEFAULT 'name',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Welcome data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS welcome_data (
                    user_id VARCHAR(20) PRIMARY KEY,
                    stage VARCHAR(20) NOT NULL,
                    data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id SERIAL PRIMARY KEY,
                    event_type VARCHAR(50) NOT NULL,
                    user_id VARCHAR(20),
                    data JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Deploy info table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deploy_info (
                    key VARCHAR(50) PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Auctions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auctions (
                    id SERIAL PRIMARY KEY,
                    seller_id VARCHAR(20) NOT NULL,
                    seller_name VARCHAR(100) NOT NULL,
                    product_name VARCHAR(200) NOT NULL,
                    description TEXT,
                    starting_price DECIMAL(10,2) NOT NULL,
                    current_price DECIMAL(10,2) NOT NULL,
                    buy_now_price DECIMAL(10,2),
                    category VARCHAR(50),
                    condition VARCHAR(50),
                    image_url TEXT,
                    duration VARCHAR(20) DEFAULT 'forever',
                    end_time TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Bids table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bids (
                    id SERIAL PRIMARY KEY,
                    auction_id INTEGER REFERENCES auctions(id) ON DELETE CASCADE,
                    bidder_id VARCHAR(20) NOT NULL,
                    bidder_name VARCHAR(100) NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Auction requests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auction_requests (
                    id SERIAL PRIMARY KEY,
                    requester_id VARCHAR(20) NOT NULL,
                    requester_name VARCHAR(100) NOT NULL,
                    product_name VARCHAR(200) NOT NULL,
                    description TEXT,
                    budget DECIMAL(10,2),
                    category VARCHAR(50),
                    status VARCHAR(20) DEFAULT 'open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Seller interests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS seller_interests (
                    id SERIAL PRIMARY KEY,
                    request_id INTEGER REFERENCES auction_requests(id) ON DELETE CASCADE,
                    seller_id VARCHAR(20) NOT NULL,
                    seller_name VARCHAR(100) NOT NULL,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Settings table for configuration
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_settings (
                    key VARCHAR(50) PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert default settings
            cursor.execute("""
                INSERT INTO bot_settings (key, value) 
                VALUES ('auction_channel_id', '1458741960134230091')
                ON CONFLICT (key) DO NOTHING
            """)
            
            cursor.close()
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def get_cursor(self):
        """Get a database cursor"""
        if not self.connection or self.connection.closed:
            self.connect()
        return self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Auction methods
    def create_auction(self, auction_data: Dict[str, Any]) -> int:
        """Create a new auction"""
        cursor = self.get_cursor()
        try:
            cursor.execute("""
                INSERT INTO auctions (seller_id, seller_name, product_name, description, 
                                    starting_price, current_price, buy_now_price, category, 
                                    condition, image_url, duration, end_time)
                VALUES (%(seller_id)s, %(seller_name)s, %(product_name)s, %(description)s,
                        %(starting_price)s, %(current_price)s, %(buy_now_price)s, %(category)s,
                        %(condition)s, %(image_url)s, %(duration)s, %(end_time)s)
                RETURNING id
            """, auction_data)
            
            auction_id = cursor.fetchone()['id']
            cursor.close()
            return auction_id
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to create auction: {e}")
            raise
    
    def get_auction(self, auction_id: int) -> Optional[Dict[str, Any]]:
        """Get auction by ID"""
        cursor = self.get_cursor()
        try:
            cursor.execute("SELECT * FROM auctions WHERE id = %s", (auction_id,))
            auction = cursor.fetchone()
            cursor.close()
            return dict(auction) if auction else None
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to get auction: {e}")
            return None
    
    def get_all_auctions(self, status: str = 'active') -> List[Dict[str, Any]]:
        """Get all auctions with specified status"""
        cursor = self.get_cursor()
        try:
            cursor.execute("SELECT * FROM auctions WHERE status = %s ORDER BY created_at DESC", (status,))
            auctions = cursor.fetchall()
            cursor.close()
            return [dict(auction) for auction in auctions]
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to get auctions: {e}")
            return []
    
    def update_auction(self, auction_id: int, updates: Dict[str, Any]) -> bool:
        """Update auction fields"""
        cursor = self.get_cursor()
        try:
            # Build dynamic update query
            set_clause = ", ".join([f"{key} = %({key})s" for key in updates.keys()])
            updates['auction_id'] = auction_id
            
            cursor.execute(f"""
                UPDATE auctions SET {set_clause} 
                WHERE id = %(auction_id)s
            """, updates)
            
            success = cursor.rowcount > 0
            cursor.close()
            return success
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to update auction: {e}")
            return False
    
    def delete_auction(self, auction_id: int) -> bool:
        """Delete auction"""
        cursor = self.get_cursor()
        try:
            cursor.execute("DELETE FROM auctions WHERE id = %s", (auction_id,))
            success = cursor.rowcount > 0
            cursor.close()
            return success
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to delete auction: {e}")
            return False
    
    # Bid methods
    def place_bid(self, auction_id: int, bidder_id: str, bidder_name: str, amount: float) -> bool:
        """Place a bid on an auction"""
        cursor = self.get_cursor()
        try:
            # Insert bid
            cursor.execute("""
                INSERT INTO bids (auction_id, bidder_id, bidder_name, amount)
                VALUES (%s, %s, %s, %s)
            """, (auction_id, bidder_id, bidder_name, amount))
            
            # Update auction current price
            cursor.execute("""
                UPDATE auctions SET current_price = %s WHERE id = %s
            """, (amount, auction_id))
            
            cursor.close()
            return True
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to place bid: {e}")
            return False
    
    def get_auction_bids(self, auction_id: int) -> List[Dict[str, Any]]:
        """Get all bids for an auction"""
        cursor = self.get_cursor()
        try:
            cursor.execute("""
                SELECT * FROM bids WHERE auction_id = %s ORDER BY created_at DESC
            """, (auction_id,))
            bids = cursor.fetchall()
            cursor.close()
            return [dict(bid) for bid in bids]
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to get bids: {e}")
            return []
    
    # Settings methods
    def get_setting(self, key: str) -> Optional[str]:
        """Get a bot setting"""
        cursor = self.get_cursor()
        try:
            cursor.execute("SELECT value FROM bot_settings WHERE key = %s", (key,))
            result = cursor.fetchone()
            cursor.close()
            return result['value'] if result else None
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to get setting: {e}")
            return None
    
    def set_setting(self, key: str, value: str) -> bool:
        """Set a bot setting"""
        cursor = self.get_cursor()
        try:
            cursor.execute("""
                INSERT INTO bot_settings (key, value) VALUES (%s, %s)
                ON CONFLICT (key) DO UPDATE SET value = %s, updated_at = CURRENT_TIMESTAMP
            """, (key, value, value))
            cursor.close()
            return True
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to set setting: {e}")
            return False
    
    # Birthday methods
    def add_birthday(self, user_id: str, birthday: str) -> bool:
        """Add or update a user's birthday"""
        cursor = self.get_cursor()
        try:
            cursor.execute("""
                INSERT INTO birthdays (user_id, birthday) VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE SET birthday = %s
            """, (user_id, birthday, birthday))
            cursor.close()
            return True
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to add birthday: {e}")
            return False
    
    def get_birthday(self, user_id: str) -> Optional[str]:
        """Get a user's birthday"""
        cursor = self.get_cursor()
        try:
            cursor.execute("SELECT birthday FROM birthdays WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            cursor.close()
            return result['birthday'] if result else None
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to get birthday: {e}")
            return None
    
    def get_all_birthdays(self) -> List[Dict[str, Any]]:
        """Get all birthdays"""
        cursor = self.get_cursor()
        try:
            cursor.execute("SELECT * FROM birthdays ORDER BY registered_at")
            birthdays = cursor.fetchall()
            cursor.close()
            return [dict(birthday) for birthday in birthdays]
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to get birthdays: {e}")
            return []
    
    def delete_birthday(self, user_id: str) -> bool:
        """Delete a user's birthday"""
        cursor = self.get_cursor()
        try:
            cursor.execute("DELETE FROM birthdays WHERE user_id = %s", (user_id,))
            success = cursor.rowcount > 0
            cursor.close()
            return success
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to delete birthday: {e}")
            return False
    
    # User profile methods
    def create_user_profile(self, user_data: Dict[str, Any]) -> bool:
        """Create or update user profile"""
        cursor = self.get_cursor()
        try:
            cursor.execute("""
                INSERT INTO user_profiles (user_id, username, display_name, email, phone, 
                                         class_year, birthday, social_links, verification_status, verification_stage)
                VALUES (%(user_id)s, %(username)s, %(display_name)s, %(email)s, %(phone)s,
                        %(class_year)s, %(birthday)s, %(social_links)s, %(verification_status)s, %(verification_stage)s)
                ON CONFLICT (user_id) DO UPDATE SET
                    username = %(username)s,
                    display_name = %(display_name)s,
                    email = %(email)s,
                    phone = %(phone)s,
                    class_year = %(class_year)s,
                    birthday = %(birthday)s,
                    social_links = %(social_links)s,
                    verification_status = %(verification_status)s,
                    verification_stage = %(verification_stage)s,
                    updated_at = CURRENT_TIMESTAMP
            """, user_data)
            cursor.close()
            return True
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to create user profile: {e}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        cursor = self.get_cursor()
        try:
            cursor.execute("SELECT * FROM user_profiles WHERE user_id = %s", (user_id,))
            profile = cursor.fetchone()
            cursor.close()
            return dict(profile) if profile else None
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to get user profile: {e}")
            return None
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile fields"""
        cursor = self.get_cursor()
        try:
            set_clause = ", ".join([f"{key} = %({key})s" for key in updates.keys()])
            updates['user_id'] = user_id
            updates['updated_at'] = 'CURRENT_TIMESTAMP'
            
            cursor.execute(f"""
                UPDATE user_profiles SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %(user_id)s
            """, updates)
            
            success = cursor.rowcount > 0
            cursor.close()
            return success
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to update user profile: {e}")
            return False
    
    # Welcome data methods
    def set_welcome_data(self, user_id: str, stage: str, data: Dict[str, Any]) -> bool:
        """Set welcome verification data"""
        cursor = self.get_cursor()
        try:
            cursor.execute("""
                INSERT INTO welcome_data (user_id, stage, data) VALUES (%s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET 
                    stage = %s, data = %s, updated_at = CURRENT_TIMESTAMP
            """, (user_id, stage, json.dumps(data), stage, json.dumps(data)))
            cursor.close()
            return True
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to set welcome data: {e}")
            return False
    
    def get_welcome_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get welcome verification data"""
        cursor = self.get_cursor()
        try:
            cursor.execute("SELECT * FROM welcome_data WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                return {
                    'user_id': result['user_id'],
                    'stage': result['stage'],
                    'data': result['data'],
                    'created_at': result['created_at'],
                    'updated_at': result['updated_at']
                }
            return None
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to get welcome data: {e}")
            return None
    
    def delete_welcome_data(self, user_id: str) -> bool:
        """Delete welcome verification data"""
        cursor = self.get_cursor()
        try:
            cursor.execute("DELETE FROM welcome_data WHERE user_id = %s", (user_id,))
            success = cursor.rowcount > 0
            cursor.close()
            return success
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to delete welcome data: {e}")
            return False
    
    # Analytics methods
    def log_analytics(self, event_type: str, user_id: str = None, data: Dict[str, Any] = None) -> bool:
        """Log an analytics event"""
        cursor = self.get_cursor()
        try:
            cursor.execute("""
                INSERT INTO analytics (event_type, user_id, data) VALUES (%s, %s, %s)
            """, (event_type, user_id, json.dumps(data) if data else None))
            cursor.close()
            return True
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to log analytics: {e}")
            return False
    
    def get_analytics(self, event_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get analytics data"""
        cursor = self.get_cursor()
        try:
            if event_type:
                cursor.execute("""
                    SELECT * FROM analytics WHERE event_type = %s 
                    ORDER BY timestamp DESC LIMIT %s
                """, (event_type, limit))
            else:
                cursor.execute("""
                    SELECT * FROM analytics ORDER BY timestamp DESC LIMIT %s
                """, (limit,))
            
            analytics = cursor.fetchall()
            cursor.close()
            return [dict(analytic) for analytic in analytics]
            
        except Exception as e:
            cursor.close()
            logger.error(f"Failed to get analytics: {e}")
            return []

# Global database instance
db = None

def get_db() -> PostgreSQLHandler:
    """Get database instance"""
    global db
    if db is None:
        from config import Config
        database_url = Config.DATABASE_URL
        db = PostgreSQLHandler(database_url)
    return db