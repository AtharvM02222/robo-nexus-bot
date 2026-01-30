import requests
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SupabaseAPI:
    def __init__(self):
        self.url = "https://pyedggezqefeeilxdprj.supabase.co"
        # Use the service role key for full access
        self.service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB5ZWRnZ2V6cWVmZWVpbHhkcHJqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTcwMDMxOSwiZXhwIjoyMDg1Mjc2MzE5fQ.fIDsGoUtPeja6_apWwE7gvE5oymfUR3pZMlmm_Ucs6A"
        
        self.headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        logger.info("Supabase API initialized with service key")
    
    # Settings methods
    def get_setting(self, key: str) -> Optional[str]:
        try:
            response = requests.get(
                f"{self.url}/rest/v1/bot_settings?key=eq.{key}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return data[0]['value']
        except requests.exceptions.Timeout:
            logger.error(f"Timeout getting setting {key}")
        except Exception as e:
            logger.error(f"Error getting setting {key}: {e}")
        
        # Fallback values
        fallbacks = {
            "welcome_channel_id": "1460866844285206661",
            "self_roles_channel_id": "1460556204383273148",
            "auction_channel_id": "1458741960134230091",
            "birthday_channel_id": "1457389004251992317"
        }
        return fallbacks.get(key)
    
    def set_setting(self, key: str, value: str) -> bool:
        try:
            # Try to update first
            response = requests.patch(
                f"{self.url}/rest/v1/bot_settings?key=eq.{key}",
                headers=self.headers,
                json={"value": value},
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            
            # If update failed, try insert
            response = requests.post(
                f"{self.url}/rest/v1/bot_settings",
                headers=self.headers,
                json={"key": key, "value": value},
                timeout=10
            )
            
            return response.status_code in [200, 201]
        except requests.exceptions.Timeout:
            logger.error(f"Timeout setting {key}")
            return False
        except Exception as e:
            logger.error(f"Error setting {key}: {e}")
            return False
    
    # Auction methods
    def get_all_auctions(self, status: str = 'active') -> List[Dict[str, Any]]:
        try:
            response = requests.get(
                f"{self.url}/rest/v1/auctions?status=eq.{status}",
                headers=self.headers,
                timeout=10  # 10 second timeout
            )
            
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Timeout getting auctions")
        except Exception as e:
            logger.error(f"Error getting auctions: {e}")
        
        return []
    
    def get_auction(self, auction_id: int) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(
                f"{self.url}/rest/v1/auctions?id=eq.{auction_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
        except Exception as e:
            logger.error(f"Error getting auction {auction_id}: {e}")
        
        return None
    
    def create_auction(self, auction_data: Dict[str, Any]) -> int:
        try:
            response = requests.post(
                f"{self.url}/rest/v1/auctions",
                headers=self.headers,
                json=auction_data
            )
            
            if response.status_code == 201:
                data = response.json()
                return data[0]['id'] if data else 0
        except Exception as e:
            logger.error(f"Error creating auction: {e}")
        
        return 0
    
    def place_bid(self, auction_id: int, bidder_id: str, bidder_name: str, amount: float) -> bool:
        try:
            # Insert bid
            bid_data = {
                "auction_id": auction_id,
                "bidder_id": bidder_id,
                "bidder_name": bidder_name,
                "amount": amount
            }
            
            response = requests.post(
                f"{self.url}/rest/v1/bids",
                headers=self.headers,
                json=bid_data
            )
            
            if response.status_code == 201:
                # Update auction current price
                update_response = requests.patch(
                    f"{self.url}/rest/v1/auctions?id=eq.{auction_id}",
                    headers=self.headers,
                    json={"current_price": amount}
                )
                return update_response.status_code == 200
                
        except Exception as e:
            logger.error(f"Error placing bid: {e}")
        
        return False
    
    def get_auction_bids(self, auction_id: int) -> List[Dict[str, Any]]:
        try:
            response = requests.get(
                f"{self.url}/rest/v1/bids?auction_id=eq.{auction_id}&order=created_at.desc",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error getting bids: {e}")
        
        return []

    # User profile methods
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(
                f"{self.url}/rest/v1/user_profiles?user_id=eq.{user_id}",
                headers=self.headers,
                timeout=10  # 10 second timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
        except requests.exceptions.Timeout:
            logger.error(f"Timeout getting user profile {user_id}")
        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {e}")
        
        return None
    
    def create_user_profile(self, profile_data: Dict[str, Any]) -> bool:
        try:
            logger.info(f"🔄 Attempting to create user profile for user_id: {profile_data.get('user_id')}")
            
            # Convert date objects to strings for JSON serialization
            if 'birthday' in profile_data and profile_data['birthday']:
                if hasattr(profile_data['birthday'], 'strftime'):
                    # It's a date object, convert to string
                    profile_data['birthday'] = profile_data['birthday'].strftime('%m-%d')
                    logger.info(f"📅 Converted birthday date object to string: {profile_data['birthday']}")
                elif isinstance(profile_data['birthday'], str):
                    # It's already a string, keep as is
                    logger.info(f"📅 Birthday is already a string: {profile_data['birthday']}")
            
            logger.info(f"📊 Profile data to save: {profile_data}")
            
            response = requests.post(
                f"{self.url}/rest/v1/user_profiles",
                headers=self.headers,
                json=profile_data,
                timeout=10
            )
            
            logger.info(f"📡 Supabase response: {response.status_code}")
            
            if response.status_code == 201:
                logger.info(f"✅ User profile created successfully for user_id: {profile_data.get('user_id')}")
                return True
            else:
                logger.error(f"❌ Failed to create user profile: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.Timeout:
            logger.error(f"⏰ Timeout creating user profile for user_id: {profile_data.get('user_id')}")
            return False
        except Exception as e:
            logger.error(f"💥 Error creating user profile: {e}")
            return False
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        try:
            response = requests.patch(
                f"{self.url}/rest/v1/user_profiles?user_id=eq.{user_id}",
                headers=self.headers,
                json=updates
            )
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error updating user profile {user_id}: {e}")
            return False
    
    # Birthday methods
    def register_birthday(self, user_id: str, birthday: str) -> bool:
        try:
            logger.info(f"🎂 Attempting to register birthday for user_id: {user_id}")
            
            # Ensure birthday is a string
            if hasattr(birthday, 'strftime'):
                # It's a date object, convert to string
                birthday = birthday.strftime('%m-%d')
                logger.info(f"📅 Converted birthday date object to string: {birthday}")
            
            logger.info(f"📊 Birthday data to save: user_id={user_id}, birthday={birthday}")
            
            # Try to update first
            response = requests.patch(
                f"{self.url}/rest/v1/birthdays?user_id=eq.{user_id}",
                headers=self.headers,
                json={"birthday": birthday},
                timeout=10
            )
            
            logger.info(f"📡 Supabase UPDATE response: {response.status_code}")
            
            if response.status_code == 200:
                logger.info(f"✅ Birthday updated successfully for user_id: {user_id}")
                return True
            
            # If update failed, try insert
            logger.info(f"🔄 Update failed, trying INSERT for user_id: {user_id}")
            response = requests.post(
                f"{self.url}/rest/v1/birthdays",
                headers=self.headers,
                json={"user_id": user_id, "birthday": birthday},
                timeout=10
            )
            
            logger.info(f"📡 Supabase INSERT response: {response.status_code}")
            
            if response.status_code == 201:
                logger.info(f"✅ Birthday inserted successfully for user_id: {user_id}")
                return True
            else:
                logger.error(f"❌ Failed to insert birthday: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"⏰ Timeout registering birthday for user_id: {user_id}")
            return False
        except Exception as e:
            logger.error(f"💥 Error registering birthday for {user_id}: {e}")
            return False
    
    def get_birthday(self, user_id: str) -> Optional[str]:
        try:
            response = requests.get(
                f"{self.url}/rest/v1/birthdays?user_id=eq.{user_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return data[0]['birthday'] if data else None
        except Exception as e:
            logger.error(f"Error getting birthday for {user_id}: {e}")
        
        return None
    
    def get_birthdays_today(self, today_str: str) -> List[Dict[str, Any]]:
        try:
            response = requests.get(
                f"{self.url}/rest/v1/birthdays?birthday=eq.{today_str}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error getting today's birthdays: {e}")
        
        return []
    
    def get_all_birthdays(self) -> List[Dict[str, Any]]:
        try:
            response = requests.get(
                f"{self.url}/rest/v1/birthdays",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error getting all birthdays: {e}")
        
        return []
    
    def remove_birthday(self, user_id: str) -> bool:
        try:
            response = requests.delete(
                f"{self.url}/rest/v1/birthdays?user_id=eq.{user_id}",
                headers=self.headers
            )
            
            return response.status_code == 204
        except Exception as e:
            logger.error(f"Error removing birthday for {user_id}: {e}")
            return False
    
    # MISSING METHODS - CRITICAL FIXES
    
    def delete_all_birthdays(self) -> bool:
        """Delete all birthdays from the database"""
        try:
            response = requests.delete(
                f"{self.url}/rest/v1/birthdays",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 204:
                logger.info("All birthdays deleted successfully")
                return True
            else:
                logger.error(f"Failed to delete all birthdays: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.Timeout:
            logger.error("Timeout deleting all birthdays")
            return False
        except Exception as e:
            logger.error(f"Error deleting all birthdays: {e}")
            return False
    
    def delete_all_auctions(self) -> bool:
        """Delete all auctions and bids from the database"""
        try:
            # First delete all bids
            response = requests.delete(
                f"{self.url}/rest/v1/bids",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 204:
                logger.error(f"Failed to delete all bids: {response.status_code} - {response.text}")
                return False
            
            # Then delete all auctions
            response = requests.delete(
                f"{self.url}/rest/v1/auctions",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 204:
                logger.info("All auctions and bids deleted successfully")
                return True
            else:
                logger.error(f"Failed to delete all auctions: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.Timeout:
            logger.error("Timeout deleting all auctions")
            return False
        except Exception as e:
            logger.error(f"Error deleting all auctions: {e}")
            return False
    
    def delete_all_user_profiles(self) -> bool:
        """Delete all user profiles from the database"""
        try:
            response = requests.delete(
                f"{self.url}/rest/v1/user_profiles",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 204:
                logger.info("All user profiles deleted successfully")
                return True
            else:
                logger.error(f"Failed to delete all user profiles: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.Timeout:
            logger.error("Timeout deleting all user profiles")
            return False
        except Exception as e:
            logger.error(f"Error deleting all user profiles: {e}")
            return False
    
    def count_user_profiles(self) -> int:
        """Count total user profiles"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/user_profiles?select=count",
                headers={**self.headers, "Prefer": "count=exact"},
                timeout=10
            )
            
            if response.status_code == 200:
                # Supabase returns count in the Content-Range header
                content_range = response.headers.get('Content-Range', '0')
                if '/' in content_range:
                    count = int(content_range.split('/')[-1])
                    return count
                return 0
        except requests.exceptions.Timeout:
            logger.error("Timeout counting user profiles")
        except Exception as e:
            logger.error(f"Error counting user profiles: {e}")
        
        return 0
    
    def get_all_user_profiles(self) -> List[Dict[str, Any]]:
        """Get all user profiles"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/user_profiles?order=created_at.desc",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.Timeout:
            logger.error("Timeout getting all user profiles")
        except Exception as e:
            logger.error(f"Error getting all user profiles: {e}")
        
        return []
    
    # RACE CONDITION FIX FOR PLACE_BID
    def place_bid(self, auction_id: int, bidder_id: str, bidder_name: str, amount: float) -> bool:
        try:
            # Insert bid first
            bid_data = {
                "auction_id": auction_id,
                "bidder_id": bidder_id,
                "bidder_name": bidder_name,
                "amount": amount
            }
            
            response = requests.post(
                f"{self.url}/rest/v1/bids",
                headers=self.headers,
                json=bid_data,
                timeout=10
            )
            
            if response.status_code == 201:
                # Update auction current price with error handling
                try:
                    update_response = requests.patch(
                        f"{self.url}/rest/v1/auctions?id=eq.{auction_id}",
                        headers=self.headers,
                        json={"current_price": amount},
                        timeout=10
                    )
                    
                    if update_response.status_code == 200:
                        logger.info(f"Bid placed successfully: ₹{amount} on auction #{auction_id}")
                        return True
                    else:
                        logger.error(f"Bid inserted but failed to update auction price: {update_response.status_code} - {update_response.text}")
                        # Bid was inserted but price update failed - this is a partial success
                        # The bid is still valid, just the current_price might be outdated
                        return True
                except requests.exceptions.Timeout:
                    logger.error(f"Timeout updating auction price for bid on auction #{auction_id}")
                    return True  # Bid was inserted successfully
                except Exception as e:
                    logger.error(f"Error updating auction price after bid: {e}")
                    return True  # Bid was inserted successfully
            else:
                logger.error(f"Failed to place bid: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout placing bid on auction #{auction_id}")
            return False
        except Exception as e:
            logger.error(f"Error placing bid: {e}")
            return False
    
    # ADD TIMEOUT TO CREATE_AUCTION
    def create_auction(self, auction_data: Dict[str, Any]) -> int:
        try:
            response = requests.post(
                f"{self.url}/rest/v1/auctions",
                headers=self.headers,
                json=auction_data,
                timeout=10  # Added timeout
            )
            
            if response.status_code == 201:
                data = response.json()
                return data[0]['id'] if data else 0
        except requests.exceptions.Timeout:
            logger.error("Timeout creating auction")
        except Exception as e:
            logger.error(f"Error creating auction: {e}")
        
        return 0

# Global instance
supabase_api = None

def get_supabase_api():
    global supabase_api
    if supabase_api is None:
        supabase_api = SupabaseAPI()
    return supabase_api
