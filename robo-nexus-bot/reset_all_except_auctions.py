#!/usr/bin/env python3
"""
Reset All Data Except Auctions
Clears birthdays, user profiles, and welcome data while keeping auctions intact
"""
import sys
from postgres_db import get_db

def reset_all_except_auctions():
    """Reset all data except auctions"""
    print("🔄 Resetting all data EXCEPT auctions...")
    print("=" * 60)
    
    db = get_db()
    
    try:
        # 1. Delete all birthdays
        print("\n🎂 Deleting all birthdays...")
        cursor = db.get_cursor()
        cursor.execute("DELETE FROM birthdays")
        birthday_count = cursor.rowcount
        cursor.close()
        print(f"✅ Deleted {birthday_count} birthdays")
        
        # 2. Delete all user profiles
        print("\n👥 Deleting all user profiles...")
        cursor = db.get_cursor()
        cursor.execute("DELETE FROM user_profiles")
        profile_count = cursor.rowcount
        cursor.close()
        print(f"✅ Deleted {profile_count} user profiles")
        
        # 3. Delete all welcome data
        print("\n🎉 Deleting all welcome verification data...")
        cursor = db.get_cursor()
        cursor.execute("DELETE FROM welcome_data")
        welcome_count = cursor.rowcount
        cursor.close()
        print(f"✅ Deleted {welcome_count} welcome data entries")
        
        # 4. Check auctions (should remain intact)
        print("\n🏷️ Checking auctions (should NOT be deleted)...")
        cursor = db.get_cursor()
        cursor.execute("SELECT COUNT(*) as count FROM auctions")
        result = cursor.fetchone()
        auction_count = result['count'] if result else 0
        cursor.close()
        print(f"✅ Auctions intact: {auction_count} auctions still in database")
        
        # 5. Check bids (should remain intact)
        cursor = db.get_cursor()
        cursor.execute("SELECT COUNT(*) as count FROM bids")
        result = cursor.fetchone()
        bid_count = result['count'] if result else 0
        cursor.close()
        print(f"✅ Bids intact: {bid_count} bids still in database")
        
        print("\n" + "=" * 60)
        print("🎉 Reset Complete!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"  ❌ Deleted {birthday_count} birthdays")
        print(f"  ❌ Deleted {profile_count} user profiles")
        print(f"  ❌ Deleted {welcome_count} welcome data entries")
        print(f"  ✅ Kept {auction_count} auctions")
        print(f"  ✅ Kept {bid_count} bids")
        
        print("\n✨ Your database is now clean and ready for fresh member data!")
        print("🚀 Next steps:")
        print("  1. Remove all members from Discord server (except yourself)")
        print("  2. Add members back one at a time")
        print("  3. Each member will go through verification")
        print("  4. Bot will collect: name, class, birthday, email, phone, social links")
        print("  5. All data will be saved to PostgreSQL")
        print("\n🏷️ Your 4 auctions are safe and will remain available!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during reset: {e}")
        return False

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will delete ALL data except auctions!")
    print("=" * 60)
    print("This will DELETE:")
    print("  • All birthdays")
    print("  • All user profiles")
    print("  • All welcome verification data")
    print("\nThis will KEEP:")
    print("  • All auctions (4 auctions)")
    print("  • All bids")
    print("=" * 60)
    
    response = input("\nAre you sure you want to continue? (yes/no): ").strip().lower()
    
    if response == "yes":
        success = reset_all_except_auctions()
        sys.exit(0 if success else 1)
    else:
        print("\n❌ Reset cancelled. No data was deleted.")
        sys.exit(0)
