"""
Startup Script for Robo Nexus Birthday Bot on Replit
Handles automatic backup/restore to protect against GitHub updates
"""
import os
import sys
import asyncio
import logging
from backup_manager import BackupManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def startup_sequence():
    """Complete startup sequence with backup protection"""
    
    print("🤖 Robo Nexus Birthday Bot - Protected Startup")
    print("=" * 50)
    
    # Initialize backup manager
    backup_manager = BackupManager()
    
    # Step 1: Check if databases exist, restore if missing
    print("\n🔍 Step 1: Checking database integrity...")
    backup_manager.check_and_restore_after_update()
    
    # Step 2: Show current database stats
    print("\n📊 Step 2: Database Statistics")
    stats = backup_manager.get_database_stats()
    if stats:
        for key, value in stats.items():
            print(f"  • {key.replace('_', ' ').title()}: {value}")
    else:
        print("  • No existing data found (fresh installation)")
    
    # Step 3: Create startup backup
    print("\n💾 Step 3: Creating startup backup...")
    backup_folder = backup_manager.create_backup("startup")
    
    # Step 4: Start the bot
    print("\n🚀 Step 4: Starting Robo Nexus Birthday Bot...")
    print("=" * 50)
    
    # Import and run the main bot
    try:
        from main import main
        await main()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        print(f"\n❌ Bot error: {e}")
    finally:
        # Create shutdown backup
        print("\n💾 Creating shutdown backup...")
        backup_manager.create_backup("shutdown")
        print("✅ Shutdown backup complete")

def check_replit_environment():
    """Check if running on Replit and show helpful info"""
    if os.getenv('REPL_ID'):
        print("🔧 Replit Environment Detected")
        print(f"  • Repl ID: {os.getenv('REPL_ID')}")
        print(f"  • Repl Owner: {os.getenv('REPL_OWNER')}")
        print(f"  • Repl Slug: {os.getenv('REPL_SLUG')}")
        
        # Check if this is a fresh GitHub import
        if not os.path.exists("birthdays.db") and not os.path.exists("user_profiles.json"):
            print("⚠️  Fresh GitHub import detected - will restore from backup if available")
        
        return True
    return False

def show_backup_commands():
    """Show helpful backup commands for Replit console"""
    print("\n📋 Backup Management Commands (use in Replit console):")
    print("  python backup_manager.py backup          # Manual backup")
    print("  python backup_manager.py restore         # Restore latest backup") 
    print("  python backup_manager.py list            # List all backups")
    print("  python backup_manager.py stats           # Show database stats")
    print("\n💡 Pro Tip: Run 'python backup_manager.py backup' before updating from GitHub!")

if __name__ == "__main__":
    # Check environment
    is_replit = check_replit_environment()
    
    if is_replit:
        show_backup_commands()
    
    # Run startup sequence
    try:
        asyncio.run(startup_sequence())
    except Exception as e:
        logger.error(f"Startup error: {e}")
        print(f"❌ Startup failed: {e}")