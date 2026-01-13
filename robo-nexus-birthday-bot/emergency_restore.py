"""
Emergency Restore Script - Run AFTER GitHub update to restore your data
"""
import os
import shutil
import glob

def find_emergency_backups():
    """Find all emergency backup directories"""
    backup_dirs = glob.glob("emergency_backup_*")
    backup_dirs.sort(reverse=True)  # Newest first
    return backup_dirs

def emergency_restore():
    """Restore from emergency backup"""
    
    print("🔄 EMERGENCY RESTORE - After GitHub Update")
    print("=" * 50)
    
    # Find backup directories
    backup_dirs = find_emergency_backups()
    
    if not backup_dirs:
        print("❌ No emergency backup directories found!")
        print("💡 Make sure you ran 'python emergency_backup.py' before the GitHub update")
        return False
    
    print(f"📁 Found {len(backup_dirs)} emergency backup(s):")
    for i, backup_dir in enumerate(backup_dirs):
        print(f"  {i+1}. {backup_dir}")
    
    # Use the newest backup by default
    selected_backup = backup_dirs[0]
    
    if len(backup_dirs) > 1:
        try:
            choice = input(f"\nSelect backup to restore (1-{len(backup_dirs)}, or Enter for newest): ").strip()
            if choice and choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(backup_dirs):
                    selected_backup = backup_dirs[idx]
        except:
            pass
    
    print(f"\n🔄 Restoring from: {selected_backup}")
    
    # Files to restore
    files_to_restore = [
        "birthdays.db",
        "user_profiles.json", 
        "welcome_data.json",
        "analytics.json",
        "auction_data.json",
        "deploy_info.json"
    ]
    
    restored_files = []
    missing_files = []
    
    # Restore each file
    for filename in files_to_restore:
        backup_file = os.path.join(selected_backup, filename)
        
        if os.path.exists(backup_file):
            try:
                shutil.copy2(backup_file, filename)
                restored_files.append(filename)
                
                # Get file size
                size = os.path.getsize(filename)
                print(f"✅ Restored: {filename} ({size} bytes)")
                
            except Exception as e:
                print(f"❌ Failed to restore {filename}: {e}")
        else:
            missing_files.append(filename)
            print(f"⚠️  Not in backup: {filename}")
    
    # Show summary
    print(f"\n📊 RESTORE SUMMARY:")
    print(f"✅ Files restored: {len(restored_files)}")
    print(f"⚠️  Files not found in backup: {len(missing_files)}")
    
    if restored_files:
        print(f"\n📦 Restored files:")
        for filename in restored_files:
            print(f"  • {filename}")
    
    # Verify restoration with new backup system
    print(f"\n🔍 Verifying restoration...")
    
    try:
        from backup_manager import BackupManager
        backup_manager = BackupManager()
        stats = backup_manager.get_database_stats()
        
        if stats:
            print(f"📊 Verified data:")
            for key, value in stats.items():
                print(f"  • {key.replace('_', ' ').title()}: {value}")
        else:
            print("⚠️  No data found after restore")
        
        # Create first protected backup
        print(f"\n💾 Creating first protected backup...")
        backup_folder = backup_manager.create_backup("post_migration")
        
        if backup_folder:
            print(f"✅ Protected backup created!")
            print(f"🛡️  Future GitHub updates will now be safe!")
        
    except Exception as e:
        print(f"⚠️  Could not verify with backup system: {e}")
        print(f"💡 Try running: python backup_manager.py stats")
    
    print(f"\n🎉 RESTORE COMPLETE!")
    print(f"🚀 Next step: python main.py")
    print(f"🛡️  Your bot now has automatic backup protection!")
    
    return True

if __name__ == "__main__":
    emergency_restore()