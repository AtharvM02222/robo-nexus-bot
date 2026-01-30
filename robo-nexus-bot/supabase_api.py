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
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return data[0]['value']
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
                json={"value": value}
            )
            
            if response.status_code == 200:
                return True
            
            # If update failed, try insert
            response = requests.post(
                f"{self.url}/rest/v1/bot_settings",
                headers=self.headers,
                json={"key": key, "value": value}
            )
            
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error setting {key}: {e}")
            return False
    
    # Auction methods
    def get_all_auctions(self, status: str = 'active') -> List[Dict[str, Any]]:
        try:
            response = requests.get(
                f"{self.url}/rest/v1/auctions?status=eq.{status}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
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
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {e}")
        
        return None
    
    def create_user_profile(self, profile_data: Dict[str, Any]) -> bool:
        try:
            response = requests.post(
                f"{self.url}/rest/v1/user_profiles",
                headers=self.headers,
                json=profile_data
            )
            
            return response.status_code == 201
        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
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
            # Try to update first
            response = requests.patch(
                f"{self.url}/rest/v1/birthdays?user_id=eq.{user_id}",
                headers=self.headers,
                json={"birthday": birthday}
            )
            
            if response.status_code == 200:
                return True
            
            # If update failed, try insert
            response = requests.post(
                f"{self.url}/rest/v1/birthdays",
                headers=self.headers,
                json={"user_id": user_id, "birthday": birthday}
            )
            
            return response.status_code == 201
        except Exception as e:
            logger.error(f"Error registering birthday for {user_id}: {e}")
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

# Global instance
supabase_api = None

def get_supabase_api():
    global supabase_api
    if supabase_api is None:
        supabase_api = SupabaseAPI()
    return supabase_api
