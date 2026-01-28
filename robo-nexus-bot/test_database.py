"""
Test script for database functionality
Run this to verify your database setup is working
"""
import asyncio
from datetime import date
from database import birthday_db
from date_parser import DateParser

async def test_database():
    """Test database functionality"""
    print("🧪 Testing Robo Nexus Birthday Bot Database...")
    
    # Initialize database
    db = birthday_db
    print("✅ Database initialized")
    
    # Test date parsing
    print("\n📅 Testing date parsing...")
    test_dates = ["12-25", "03/15", "12-25-1995", "02/29/2024"]
    
    for date_str in test_dates:
        parsed = DateParser.parse_birthday(date_str)
        if parsed:
            formatted = DateParser.format_birthday(parsed)
            print(f"✅ '{date_str}' → {formatted}")
        else:
            print(f"❌ Failed to parse '{date_str}'")
    
    # Test birthday registration
    print("\n🎂 Testing birthday registration...")
    test_user_id = 123456789
    test_birthday = DateParser.parse_birthday("12-25")
    
    if test_birthday:
        success = await db.register_birthday(test_user_id, test_birthday)
        if success:
            print(f"✅ Birthday registered for user {test_user_id}")
            
            # Test retrieval
            retrieved = await db.get_birthday(test_user_id)
            if retrieved:
                print(f"✅ Birthday retrieved: {DateParser.format_birthday(retrieved)}")
            else:
                print("❌ Failed to retrieve birthday")
        else:
            print("❌ Failed to register birthday")
    
    # Test server configuration
    print("\n⚙️ Testing server configuration...")
    test_guild_id = 1403310542030114898  # Your Robo Nexus server ID
    test_channel_id = 987654321
    
    success = await db.set_birthday_channel(test_guild_id, test_channel_id)
    if success:
        print(f"✅ Birthday channel configured for guild {test_guild_id}")
        
        # Test retrieval
        retrieved_channel = await db.get_birthday_channel(test_guild_id)
        if retrieved_channel == test_channel_id:
            print(f"✅ Channel configuration retrieved: {retrieved_channel}")
        else:
            print("❌ Failed to retrieve channel configuration")
    else:
        print("❌ Failed to configure birthday channel")
    
    # Test today's birthdays (should be empty unless you have Dec 25 birthdays)
    print("\n🎉 Testing today's birthday check...")
    todays_birthdays = await db.get_todays_birthdays()
    print(f"📊 Found {len(todays_birthdays)} birthdays today")
    
    # Test all birthdays
    all_birthdays = await db.get_all_birthdays()
    print(f"📊 Total registered birthdays: {len(all_birthdays)}")
    
    print("\n🎉 Database tests completed!")
    print("\nYour database is ready for the Robo Nexus Birthday Bot! 🤖")

if __name__ == "__main__":
    asyncio.run(test_database())