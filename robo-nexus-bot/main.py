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
    """Main function to start the Robo Nexus Birthday Bot"""
    try:
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