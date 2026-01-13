"""
Pre-Update Script for Robo Nexus Birthday Bot
Run this BEFORE updating from GitHub to backup your data
"""
from backup_manager import BackupManager
import os

def pre_update_backup():
    """Create backup before GitHub update"""
    
    print("🔄 PRE-UPDATE BACKUP SCRIPT")
    print("=" * 40)
    
    backup_manager = BackupManager()
    
    # Show current data
    print("\n📊 Current Database Status:")
    stats = backup_manager.get_database_stats()
    
    if not stats:
        print("  ⚠️  No databases found - nothing to backup")
        return
    
    for key, value in stats.items():
        print(f"  • {key.replace('_', ' ').title()}: {value}")
    
    # Create backup
    print(f"\n💾 Creating backup before GitHub update...")
    backup_folder = backup_manager.create_backup("pre_github_update")
    
    if backup_folder:
        print(f"\n✅ BACKUP SUCCESSFUL!")
        print(f"📁 Backup location: {backup_folder}")
        print("\n🔒 Your data is now protected!")
        print("\n📋 Next steps:")
        print("  1. ✅ Backup complete - you can now update from GitHub")
        print("  2. 🔄 After update, run: python startup.py")
        print("  3. 🤖 The bot will auto-restore your data if needed")
        
        # Show what was backed up
        print(f"\n📦 Files backed up:")
        for db_file in backup_manager.database_files:
            if os.path.exists(db_file):
                size = os.path.getsize(db_file)
                print(f"  • {db_file} ({size} bytes)")
    else:
        print("\n❌ BACKUP FAILED!")
        print("⚠️  DO NOT UPDATE FROM GITHUB YET!")
        print("🔧 Check the error messages above and try again")

if __name__ == "__main__":
    pre_update_backup()