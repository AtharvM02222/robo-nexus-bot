"""
Robo Nexus Birthday Bot - Main Entry Point
A Discord bot for managing birthday celebrations in the Robo Nexus server
"""
import asyncio
import logging
from config import Config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to start the Robo Nexus Birthday Bot with simple backup protection"""
    try:
        # Simple backup check - look for common backup folders
        backup_folders = []
        import os
        for folder in ['my_backup', 'backup', 'data_backup']:
            if os.path.exists(folder):
                backup_folders.append(folder)
        
        if backup_folders:
            print(f"📁 Found backup folder(s): {', '.join(backup_folders)}")
            
            # Check if we're missing databases and have backups
            missing_files = []
            for db_file in ['birthdays.db', 'user_profiles.json', 'analytics.json']:
                if not os.path.exists(db_file):
                    missing_files.append(db_file)
            
            if missing_files and backup_folders:
                print(f"⚠️  Missing files detected: {missing_files}")
                print(f"💡 To restore, run: cp {backup_folders[0]}/* .")
        
        # Show current database status
        db_files = []
        for pattern in ['*.db', '*.json']:
            import glob
            db_files.extend(glob.glob(pattern))
        
        if db_files:
            print(f"📊 Current database files: {len(db_files)} found")
            for db_file in sorted(db_files):
                size = os.path.getsize(db_file)
                print(f"  • {db_file} ({size} bytes)")
        else:
            print("📊 No database files found (fresh installation)")
        
        # Validate configuration
        Config.validate()
        logger.info("Configuration validated successfully")
        
        # Start keep-alive server for Replit
        try:
            from keep_alive import keep_alive
            keep_alive()
        except ImportError:
            # keep_alive not available, skip (for other hosting platforms)
            pass
        
        # Import and create bot instance
        from bot import run_bot
        
        logger.info("🤖 Starting Robo Nexus Birthday Bot...")
        print(f"🎂 Bot Name: {Config.BOT_NAME}")
        print(f"💾 Database: {Config.DATABASE_PATH}")
        print(f"⏰ Birthday Check Time: {Config.BIRTHDAY_CHECK_TIME}")
        print(f"🌐 Guild ID: {Config.GUILD_ID or 'Global (all servers)'}")
        print("\n🚀 Connecting to Discord...")
        
        # Start the bot
        await run_bot()
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print("\n❌ Configuration Error!")
        print("\n📋 Setup Instructions:")
        print("1. Copy .env.example to .env")
        print("2. Add your Discord bot token to .env")
        print("3. Optionally add your server ID for faster slash command sync")
        print("\n💡 Example .env file:")
        print("DISCORD_TOKEN=your_bot_token_here")
        print("GUILD_ID=1403310542030114898")
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
        print("\n👋 Bot stopped by user")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Unexpected error: {e}")
        print("Check the logs for more details.")

if __name__ == "__main__":
    asyncio.run(main())