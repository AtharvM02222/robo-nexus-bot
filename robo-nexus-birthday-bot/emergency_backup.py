"""
Emergency Backup Script - Run BEFORE uploading new code to GitHub
This will backup your current data so you can restore it after the GitHub update
"""
import os
import shutil
import json
import sqlite3
from datetime import datetime

def emergency_backup():
    """Create emergency backup before GitHub upload"""
    
    print("🚨 EMERGENCY BACKUP - Before GitHub Upload")
    print("=" * 50)
    
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"emergency_backup_{timestamp}"
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        print(f"📁 Created backup directory: {backup_dir}")
    except Exception as e:
        print(f"❌ Could not create backup directory: {e}")
        return False
    
    # Files to backup
    files_to_backup = [
        "birthdays.db",
        "user_profiles.json", 
        "welcome_data.json",
        "analytics.json",
        "auction_data.json",
        "deploy_info.json"
    ]
    
    backed_up_files = []
    missing_files = []
    
    # Backup each file
    for filename in files_to_backup:
        if os.path.exists(filename):
            try:
                shutil.copy2(filename, os.path.join(backup_dir, filename))
                backed_up_files.append(filename)
                
                # Get file size
                size = os.path.getsize(filename)
                print(f"✅ Backed up: {filename} ({size} bytes)")
                
            except Exception as e:
                print(f"❌ Failed to backup {filename}: {e}")
        else:
            missing_files.append(filename)
            print(f"⚠️  File not found: {filename}")
    
    # Show summary
    print(f"\n📊 BACKUP SUMMARY:")
    print(f"✅ Files backed up: {len(backed_up_files)}")
    print(f"⚠️  Files missing: {len(missing_files)}")
    
    if backed_up_files:
        print(f"\n📦 Backed up files:")
        for filename in backed_up_files:
            print(f"  • {filename}")
    
    if missing_files:
        print(f"\n⚠️  Missing files (normal if you haven't used these features):")
        for filename in missing_files:
            print(f"  • {filename}")
    
    # Export readable data
    print(f"\n📄 Exporting readable data...")
    
    # Export birthdays if database exists
    if "birthdays.db" in backed_up_files:
        try:
            conn = sqlite3.connect("birthdays.db")
            cursor = conn.cursor()
            
            # Export birthdays
            cursor.execute("SELECT user_id, birthday, registered_at FROM birthdays")
            birthdays = cursor.fetchall()
            
            if birthdays:
                with open(os.path.join(backup_dir, "birthdays_readable.txt"), 'w') as f:
                    f.write("User ID | Birthday | Registered At\n")
                    f.write("-" * 50 + "\n")
                    for user_id, birthday, registered_at in birthdays:
                        f.write(f"{user_id} | {birthday} | {registered_at}\n")
                
                print(f"✅ Exported {len(birthdays)} birthdays to readable format")
            
            # Export server configs
            cursor.execute("SELECT guild_id, birthday_channel_id, notification_time FROM server_config")
            configs = cursor.fetchall()
            
            if configs:
                with open(os.path.join(backup_dir, "server_config_readable.txt"), 'w') as f:
                    f.write("Guild ID | Birthday Channel | Notification Time\n")
                    f.write("-" * 60 + "\n")
                    for guild_id, channel_id, notif_time in configs:
                        f.write(f"{guild_id} | {channel_id} | {notif_time}\n")
                
                print(f"✅ Exported {len(configs)} server configs to readable format")
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Could not export database data: {e}")
    
    # Export user profiles if exists
    if "user_profiles.json" in backed_up_files:
        try:
            with open("user_profiles.json", 'r') as f:
                profiles = json.load(f)
            
            if profiles:
                with open(os.path.join(backup_dir, "user_profiles_readable.txt"), 'w') as f:
                    f.write("User Profiles Export\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for user_id, profile in profiles.items():
                        f.write(f"User ID: {user_id}\n")
                        f.write(f"Name: {profile.get('name', 'N/A')}\n")
                        f.write(f"Class: {profile.get('class', 'N/A')}\n")
                        f.write(f"Email: {profile.get('email', 'N/A')}\n")
                        f.write(f"Discord: {profile.get('discord_username', 'N/A')}\n")
                        
                        social_links = profile.get('social_links', {})
                        if social_links:
                            f.write("Social Links:\n")
                            for platform, url in social_links.items():
                                f.write(f"  {platform}: {url}\n")
                        
                        f.write("-" * 30 + "\n")
                
                print(f"✅ Exported {len(profiles)} user profiles to readable format")
        
        except Exception as e:
            print(f"⚠️  Could not export user profiles: {e}")
    
    # Create restore instructions
    restore_script = f"""#!/bin/bash
# Restore script for emergency backup {timestamp}
# Run this after GitHub update to restore your data

echo "🔄 Restoring data from emergency backup..."

# Copy files back
"""
    
    for filename in backed_up_files:
        restore_script += f'cp "{backup_dir}/{filename}" . && echo "✅ Restored {filename}"\n'
    
    restore_script += """
echo "✅ Restore complete!"
echo "🚀 Now run: python main.py"
"""
    
    with open(os.path.join(backup_dir, "restore.sh"), 'w') as f:
        f.write(restore_script)
    
    # Create restore commands for manual use
    with open(os.path.join(backup_dir, "restore_commands.txt"), 'w') as f:
        f.write("Manual Restore Commands\n")
        f.write("=" * 30 + "\n\n")
        f.write("Run these commands after GitHub update:\n\n")
        
        for filename in backed_up_files:
            f.write(f'cp "{backup_dir}/{filename}" .\n')
        
        f.write(f"\nThen run: python main.py\n")
    
    print(f"\n📋 BACKUP COMPLETE!")
    print(f"📁 Backup location: {backup_dir}")
    print(f"📄 Restore script: {backup_dir}/restore.sh")
    print(f"📄 Manual commands: {backup_dir}/restore_commands.txt")
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"1. ✅ Backup complete - your data is safe")
    print(f"2. 🔄 Upload new code to GitHub")
    print(f"3. 🔄 Update from GitHub in Replit")
    print(f"4. 🔄 Run restore commands to get your data back")
    print(f"5. 🚀 Start bot with: python main.py")
    
    print(f"\n🔒 Your data is now protected in: {backup_dir}")
    
    return True

if __name__ == "__main__":
    emergency_backup()