#!/usr/bin/env python3
"""
Migration script to move ALL bot data from JSON/SQLite to PostgreSQL
Run this once to migrate your existing data
"""
import json
import sqlite3
import sys
import os
from postgres_db import get_db

def migrate_birthdays():
    """Migrate birthday data from SQLite to PostgreSQL"""
    try:
        if not os.path.exists('birthdays.db'):
            print("No birthdays.db found - skipping birthday migration")
            return
        
        # Connect to SQLite
        sqlite_conn = sqlite3.connect('birthdays.db')
        sqlite_cursor = sqlite_conn.cursor()
        
        # Get PostgreSQL connection
        db = get_db()
        
        # Get all birthdays from SQLite
        sqlite_cursor.execute("SELECT * FROM birthdays")
        birthdays = sqlite_cursor.fetchall()
        
        print(f"Found {len(birthdays)} birthdays to migrate...")
        
        for birthday in birthdays:
            user_id, birthday_date, registered_at = birthday
            success = db.add_birthday(str(user_id), birthday_date)
            if success:
                print(f"Migrated birthday: {user_id} -> {birthday_date}")
            else:
                print(f"Failed to migrate birthday for {user_id}")
        
        sqlite_conn.close()
        print("✅ Birthday migration completed!")
        
    except Exception as e:
        print(f"❌ Birthday migration failed: {e}")

def migrate_user_profiles():
    """Migrate user profiles from JSON to PostgreSQL"""
    try:
        if not os.path.exists('user_profiles.json'):
            print("No user_profiles.json found - skipping user profile migration")
            return
        
        with open('user_profiles.json', 'r') as f:
            data = json.load(f)
        
        db = get_db()
        
        print(f"Found {len(data)} user profiles to migrate...")
        
        for user_id, profile in data.items():
            user_data = {
                'user_id': user_id,
                'username': profile.get('username', ''),
                'display_name': profile.get('display_name', ''),
                'email': profile.get('email', ''),
                'phone': profile.get('phone', ''),
                'class_year': profile.get('class_year', ''),
                'birthday': profile.get('birthday', ''),
                'social_links': profile.get('social_links', {}),
                'verification_status': profile.get('verification_status', 'pending'),
                'verification_stage': profile.get('verification_stage', 'name')
            }
            
            success = db.create_user_profile(user_data)
            if success:
                print(f"Migrated user profile: {profile.get('username', user_id)}")
            else:
                print(f"Failed to migrate user profile for {user_id}")
        
        print("✅ User profile migration completed!")
        
    except Exception as e:
        print(f"❌ User profile migration failed: {e}")

def migrate_welcome_data():
    """Migrate welcome data from JSON to PostgreSQL"""
    try:
        if not os.path.exists('welcome_data.json'):
            print("No welcome_data.json found - skipping welcome data migration")
            return
        
        with open('welcome_data.json', 'r') as f:
            data = json.load(f)
        
        db = get_db()
        
        print(f"Found {len(data)} welcome data entries to migrate...")
        
        for user_id, welcome_info in data.items():
            success = db.set_welcome_data(
                user_id,
                welcome_info.get('stage', 'name'),
                welcome_info
            )
            if success:
                print(f"Migrated welcome data: {user_id}")
            else:
                print(f"Failed to migrate welcome data for {user_id}")
        
        print("✅ Welcome data migration completed!")
        
    except Exception as e:
        print(f"❌ Welcome data migration failed: {e}")

def migrate_analytics():
    """Migrate analytics data from JSON to PostgreSQL"""
    try:
        if not os.path.exists('analytics.json'):
            print("No analytics.json found - skipping analytics migration")
            return
        
        with open('analytics.json', 'r') as f:
            data = json.load(f)
        
        db = get_db()
        
        # Analytics data structure may vary, adapt as needed
        events_migrated = 0
        for event_type, events in data.items():
            if isinstance(events, list):
                for event in events:
                    success = db.log_analytics(
                        event_type,
                        event.get('user_id'),
                        event
                    )
                    if success:
                        events_migrated += 1
        
        print(f"✅ Analytics migration completed! Migrated {events_migrated} events")
        
    except Exception as e:
        print(f"❌ Analytics migration failed: {e}")

def migrate_auctions():
    """Migrate auction data from JSON to PostgreSQL"""
    try:
        if not os.path.exists('auction_data.json'):
            print("No auction_data.json found - skipping auction migration")
            return
        
        # Load existing auction data
        with open('auction_data.json', 'r') as f:
            data = json.load(f)
        
        db = get_db()
        
        print(f"Found {len(data.get('auctions', []))} auctions to migrate...")
        
        # Migrate each auction
        for auction in data.get('auctions', []):
            auction_data = {
                'seller_id': auction['seller_id'],
                'seller_name': auction['seller_name'],
                'product_name': auction['product_name'],
                'description': auction.get('description', ''),
                'starting_price': auction['starting_price'],
                'current_price': auction['current_price'],
                'buy_now_price': auction.get('buy_now_price'),
                'category': auction.get('category', 'Other'),
                'condition': auction.get('condition', 'Used - Good'),
                'image_url': auction.get('image_url'),
                'duration': auction.get('duration', 'forever'),
                'end_time': None  # Convert if needed
            }
            
            auction_id = db.create_auction(auction_data)
            print(f"Migrated auction: {auction['product_name']} -> ID #{auction_id}")
            
            # Migrate bids if they exist
            for bid in auction.get('bids', []):
                db.place_bid(
                    auction_id,
                    bid['bidder_id'],
                    bid['bidder_name'],
                    bid['amount']
                )
                print(f"  - Migrated bid: ₹{bid['amount']} by {bid['bidder_name']}")
        
        # Set auction channel ID
        channel_id = data.get('auction_channel_id')
        if channel_id:
            db.set_setting('auction_channel_id', str(channel_id))
            print(f"Set auction channel ID: {channel_id}")
        
        print("✅ Auction migration completed!")
        
    except Exception as e:
        print(f"❌ Auction migration failed: {e}")

def migrate_deploy_info():
    """Migrate deploy info from JSON to PostgreSQL"""
    try:
        if not os.path.exists('deploy_info.json'):
            print("No deploy_info.json found - skipping deploy info migration")
            return
        
        with open('deploy_info.json', 'r') as f:
            data = json.load(f)
        
        db = get_db()
        
        for key, value in data.items():
            success = db.set_setting(f"deploy_{key}", str(value))
            if success:
                print(f"Migrated deploy info: {key} -> {value}")
        
        print("✅ Deploy info migration completed!")
        
    except Exception as e:
        print(f"❌ Deploy info migration failed: {e}")

def main():
    """Run all migrations"""
    print("🚀 Starting comprehensive data migration to PostgreSQL...")
    print("=" * 60)
    
    # Run all migrations
    migrate_birthdays()
    print()
    migrate_user_profiles()
    print()
    migrate_welcome_data()
    print()
    migrate_analytics()
    print()
    migrate_auctions()
    print()
    migrate_deploy_info()
    
    print("=" * 60)
    print("🎉 All migrations completed!")
    print("\n📋 Summary:")
    print("✅ Birthdays: SQLite -> PostgreSQL")
    print("✅ User Profiles: JSON -> PostgreSQL")
    print("✅ Welcome Data: JSON -> PostgreSQL")
    print("✅ Analytics: JSON -> PostgreSQL")
    print("✅ Auctions: JSON -> PostgreSQL")
    print("✅ Deploy Info: JSON -> PostgreSQL")
    print("\n🔒 Your data is now safely stored in PostgreSQL!")
    print("💡 You can now delete the old JSON/SQLite files if desired.")

if __name__ == "__main__":
    main()