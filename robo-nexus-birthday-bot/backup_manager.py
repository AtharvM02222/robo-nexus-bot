"""
Backup Manager for Robo Nexus Birthday Bot
Protects databases from being wiped during GitHub updates on Replit
"""
import os
import json
import shutil
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BackupManager:
    """Manages database backups and restoration for Replit deployments"""
    
    def __init__(self):
        # Database files to protect
        self.database_files = [
            "birthdays.db",
            "user_profiles.json", 
            "welcome_data.json",
            "analytics.json",
            "auction_data.json",
            "deploy_info.json"
        ]
        
        # Backup directory (outside main code directory)
        # Use different paths for Replit vs local development
        if os.getenv('REPL_ID'):
            # Replit environment
            self.backup_dir = "/home/runner/robo_nexus_backups"
        else:
            # Local development
            self.backup_dir = os.path.expanduser("~/robo_nexus_backups")
        
        # Ensure backup directory exists
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            logger.info(f"Backup manager initialized - backup dir: {self.backup_dir}")
        except Exception as e:
            # Fallback to local directory if can't create in home
            self.backup_dir = "./backups"
            os.makedirs(self.backup_dir, exist_ok=True)
            logger.warning(f"Using fallback backup dir: {self.backup_dir}")
            print(f"⚠️ Using fallback backup directory: {self.backup_dir}")
    
    def create_backup(self, reason="manual"):
        """Create backup of all database files"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_folder = os.path.join(self.backup_dir, f"backup_{timestamp}_{reason}")
            os.makedirs(backup_folder, exist_ok=True)
            
            backed_up_files = []
            
            for db_file in self.database_files:
                if os.path.exists(db_file):
                    backup_path = os.path.join(backup_folder, db_file)
                    shutil.copy2(db_file, backup_path)
                    backed_up_files.append(db_file)
                    logger.info(f"Backed up: {db_file}")
            
            # Create backup info file
            backup_info = {
                "timestamp": timestamp,
                "reason": reason,
                "files": backed_up_files,
                "created_at": datetime.now().isoformat()
            }
            
            with open(os.path.join(backup_folder, "backup_info.json"), 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            print(f"✅ Backup created: {backup_folder}")
            print(f"📁 Files backed up: {len(backed_up_files)}")
            
            return backup_folder
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            print(f"❌ Backup failed: {e}")
            return None
    
    def restore_backup(self, backup_folder=None):
        """Restore from backup (latest if not specified)"""
        try:
            if not backup_folder:
                backup_folder = self.get_latest_backup()
            
            if not backup_folder or not os.path.exists(backup_folder):
                print("❌ No backup found to restore")
                return False
            
            # Load backup info
            backup_info_path = os.path.join(backup_folder, "backup_info.json")
            if os.path.exists(backup_info_path):
                with open(backup_info_path, 'r') as f:
                    backup_info = json.load(f)
                print(f"📅 Restoring backup from: {backup_info['created_at']}")
                print(f"📝 Reason: {backup_info['reason']}")
            
            restored_files = []
            
            for db_file in self.database_files:
                backup_file_path = os.path.join(backup_folder, db_file)
                if os.path.exists(backup_file_path):
                    shutil.copy2(backup_file_path, db_file)
                    restored_files.append(db_file)
                    logger.info(f"Restored: {db_file}")
            
            print(f"✅ Restore completed: {len(restored_files)} files")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            print(f"❌ Restore failed: {e}")
            return False
    
    def get_latest_backup(self):
        """Get the most recent backup folder"""
        try:
            if not os.path.exists(self.backup_dir):
                return None
            
            backup_folders = [
                f for f in os.listdir(self.backup_dir) 
                if f.startswith("backup_") and os.path.isdir(os.path.join(self.backup_dir, f))
            ]
            
            if not backup_folders:
                return None
            
            # Sort by timestamp (newest first)
            backup_folders.sort(reverse=True)
            latest = os.path.join(self.backup_dir, backup_folders[0])
            
            return latest
            
        except Exception as e:
            logger.error(f"Error finding latest backup: {e}")
            return None
    
    def list_backups(self):
        """List all available backups"""
        try:
            if not os.path.exists(self.backup_dir):
                print("📁 No backup directory found")
                return []
            
            backup_folders = [
                f for f in os.listdir(self.backup_dir) 
                if f.startswith("backup_") and os.path.isdir(os.path.join(self.backup_dir, f))
            ]
            
            if not backup_folders:
                print("📁 No backups found")
                return []
            
            backup_folders.sort(reverse=True)  # Newest first
            
            print(f"📋 Found {len(backup_folders)} backup(s):")
            
            backups_info = []
            for folder in backup_folders:
                folder_path = os.path.join(self.backup_dir, folder)
                backup_info_path = os.path.join(folder_path, "backup_info.json")
                
                if os.path.exists(backup_info_path):
                    with open(backup_info_path, 'r') as f:
                        info = json.load(f)
                    
                    print(f"  📅 {info['created_at']} - {info['reason']} ({len(info['files'])} files)")
                    backups_info.append({
                        "folder": folder_path,
                        "info": info
                    })
                else:
                    print(f"  📁 {folder} (no info available)")
                    backups_info.append({
                        "folder": folder_path,
                        "info": None
                    })
            
            return backups_info
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            print(f"❌ Error listing backups: {e}")
            return []
    
    def auto_backup_before_update(self):
        """Automatically backup before GitHub update"""
        print("🔄 GitHub update detected - creating automatic backup...")
        return self.create_backup("github_update")
    
    def check_and_restore_after_update(self):
        """Check if databases were wiped and restore if needed"""
        try:
            missing_files = []
            
            for db_file in self.database_files:
                if not os.path.exists(db_file):
                    missing_files.append(db_file)
            
            if missing_files:
                print(f"⚠️ Missing database files detected: {missing_files}")
                print("🔄 Attempting to restore from latest backup...")
                
                if self.restore_backup():
                    print("✅ Database files restored successfully!")
                    return True
                else:
                    print("❌ Failed to restore database files")
                    return False
            else:
                print("✅ All database files present")
                return True
                
        except Exception as e:
            logger.error(f"Error checking databases: {e}")
            print(f"❌ Error checking databases: {e}")
            return False
    
    def get_database_stats(self):
        """Get statistics about current databases"""
        try:
            stats = {}
            
            # SQLite databases
            if os.path.exists("birthdays.db"):
                conn = sqlite3.connect("birthdays.db")
                cursor = conn.cursor()
                
                # Count birthdays
                cursor.execute("SELECT COUNT(*) FROM birthdays")
                birthday_count = cursor.fetchone()[0]
                stats["birthdays"] = birthday_count
                
                # Count server configs
                cursor.execute("SELECT COUNT(*) FROM server_config")
                server_count = cursor.fetchone()[0]
                stats["servers_configured"] = server_count
                
                conn.close()
            
            # JSON databases
            json_files = {
                "user_profiles.json": "user_profiles",
                "analytics.json": "analytics_data", 
                "auction_data.json": "auction_items",
                "welcome_data.json": "welcome_config"
            }
            
            for file_name, key in json_files.items():
                if os.path.exists(file_name):
                    with open(file_name, 'r') as f:
                        data = json.load(f)
                    
                    if file_name == "user_profiles.json":
                        stats["user_profiles"] = len(data)
                    elif file_name == "auction_data.json":
                        auctions = data.get("auctions", [])
                        stats["auction_items"] = len(auctions)
                    elif file_name == "analytics.json":
                        stats["analytics_available"] = True
                    elif file_name == "welcome_data.json":
                        stats["welcome_configured"] = True
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}


def main():
    """Command line interface for backup management"""
    import sys
    
    backup_manager = BackupManager()
    
    if len(sys.argv) < 2:
        print("🤖 Robo Nexus Backup Manager")
        print("\nUsage:")
        print("  python backup_manager.py backup [reason]     # Create backup")
        print("  python backup_manager.py restore [folder]    # Restore backup")
        print("  python backup_manager.py list               # List backups")
        print("  python backup_manager.py check              # Check databases")
        print("  python backup_manager.py stats              # Database statistics")
        return
    
    command = sys.argv[1].lower()
    
    if command == "backup":
        reason = sys.argv[2] if len(sys.argv) > 2 else "manual"
        backup_manager.create_backup(reason)
    
    elif command == "restore":
        folder = sys.argv[2] if len(sys.argv) > 2 else None
        backup_manager.restore_backup(folder)
    
    elif command == "list":
        backup_manager.list_backups()
    
    elif command == "check":
        backup_manager.check_and_restore_after_update()
    
    elif command == "stats":
        stats = backup_manager.get_database_stats()
        print("📊 Database Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()