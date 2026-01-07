"""
Robo Nexus Birthday Bot - Main Bot Class
Discord bot for managing birthday celebrations in the Robo Nexus server
"""
import discord
from discord.ext import commands, tasks
import logging
from datetime import datetime, time
import asyncio
from typing import Optional

from config import Config
from database import DatabaseManager
from date_parser import DateParser

logger = logging.getLogger(__name__)

class RoboNexusBirthdayBot(commands.Bot):
    """Main Discord bot class for Robo Nexus Birthday Bot"""
    
    def __init__(self):
        """Initialize the Robo Nexus Birthday Bot"""
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        
        # Initialize bot with proper settings
        super().__init__(
            command_prefix='!',  # Fallback prefix (we'll use slash commands)
            intents=intents,
            help_command=None,  # We'll create our own help system
            case_insensitive=True
        )
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.scheduler_started = False
        
        logger.info("Robo Nexus Birthday Bot initialized")
    
    async def setup_hook(self):
        """Called when the bot is starting up"""
        try:
            # Initialize database
            await self.db_manager.init_database()
            logger.info("Database initialized successfully")
            
            # Load command cogs
            await self.load_extension('commands')
            await self.load_extension('admin_commands')
            await self.load_extension('help_commands')
            logger.info("Command cogs loaded successfully")
            
            # Sync slash commands
            if Config.GUILD_ID:
                # Sync to specific guild for faster updates during development
                guild = discord.Object(id=int(Config.GUILD_ID))
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                logger.info(f"Slash commands synced to guild {Config.GUILD_ID}")
            else:
                # Sync globally (takes up to 1 hour to propagate)
                await self.tree.sync()
                logger.info("Slash commands synced globally")
            
            logger.info("Bot setup completed successfully")
            
        except Exception as e:
            logger.error(f"Error during bot setup: {e}")
            raise
    
    async def on_ready(self):
        """Called when the bot is ready and connected to Discord"""
        logger.info(f"🤖 {self.user} is now online!")
        logger.info(f"Bot ID: {self.user.id}")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        
        # Log guild information
        for guild in self.guilds:
            logger.info(f"  - {guild.name} (ID: {guild.id}) - {guild.member_count} members")
        
        # Start the birthday scheduler if not already started
        if not self.scheduler_started:
            await self.start_birthday_scheduler()
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="for birthdays 🎂"
        )
        await self.change_presence(activity=activity)
        
        print(f"\n🎉 Robo Nexus Birthday Bot is ready!")
        print(f"📊 Connected to {len(self.guilds)} server(s)")
        print(f"🎂 Monitoring birthdays for Robo Nexus community")
        print(f"⏰ Daily birthday check scheduled for {Config.BIRTHDAY_CHECK_TIME}")
    
    async def start_birthday_scheduler(self):
        """Start the daily birthday check scheduler"""
        try:
            # Parse the configured time
            hour, minute = map(int, Config.BIRTHDAY_CHECK_TIME.split(':'))
            
            # Start the birthday check task
            self.daily_birthday_check.change_interval(time=time(hour=hour, minute=minute))
            self.daily_birthday_check.start()
            
            self.scheduler_started = True
            logger.info(f"Birthday scheduler started - daily check at {Config.BIRTHDAY_CHECK_TIME}")
            
        except Exception as e:
            logger.error(f"Error starting birthday scheduler: {e}")
    
    @tasks.loop(time=time(hour=9, minute=0))  # Default 9:00 AM, will be changed in start_birthday_scheduler
    async def daily_birthday_check(self):
        """Daily task to check for birthdays and send notifications"""
        try:
            logger.info("Running daily birthday check...")
            
            # Get today's birthdays
            todays_birthdays = await self.db_manager.get_todays_birthdays()
            
            if not todays_birthdays:
                logger.info("No birthdays today")
                return
            
            logger.info(f"Found {len(todays_birthdays)} birthday(s) today!")
            
            # Send birthday messages for each guild
            for guild in self.guilds:
                await self.send_birthday_messages(guild, todays_birthdays)
            
        except Exception as e:
            logger.error(f"Error during daily birthday check: {e}")
    
    async def send_birthday_messages(self, guild: discord.Guild, birthdays: list):
        """
        Send birthday messages to the configured channel in a guild
        
        Args:
            guild: Discord guild object
            birthdays: List of (user_id, birthday_date) tuples
        """
        try:
            # Get configured birthday channel for this guild
            channel_id = await self.db_manager.get_birthday_channel(guild.id)
            
            if not channel_id:
                logger.warning(f"No birthday channel configured for guild {guild.name}")
                return
            
            # Get the channel
            channel = guild.get_channel(channel_id)
            if not channel:
                logger.error(f"Birthday channel {channel_id} not found in guild {guild.name}")
                return
            
            # Send birthday message for each user
            for user_id, birthday_date in birthdays:
                try:
                    # Get the user from the guild
                    member = guild.get_member(user_id)
                    
                    if member:
                        # Create birthday message with Robo Nexus format
                        message = f"Hey Robo Nexus, it's {member.mention}'s birthday today! 🎉🎂"
                        
                        # Send the message
                        await channel.send(message)
                        logger.info(f"Birthday message sent for {member.display_name} in {guild.name}")
                        
                        # Add a small delay between messages to avoid rate limits
                        await asyncio.sleep(1)
                    else:
                        logger.warning(f"User {user_id} not found in guild {guild.name}")
                        
                except Exception as e:
                    logger.error(f"Error sending birthday message for user {user_id}: {e}")
            
        except Exception as e:
            logger.error(f"Error sending birthday messages to guild {guild.name}: {e}")
    
    @daily_birthday_check.before_loop
    async def before_birthday_check(self):
        """Wait for bot to be ready before starting birthday checks"""
        await self.wait_until_ready()
        logger.info("Bot is ready, birthday scheduler will start")
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            # Ignore unknown commands
            return
        
        logger.error(f"Command error: {error}")
        
        # Send error message to user
        try:
            await ctx.send("❌ An error occurred while processing your command. Please try again.")
        except:
            pass  # Channel might not be accessible
    
    async def on_error(self, event, *args, **kwargs):
        """Handle general bot errors"""
        logger.error(f"Bot error in event {event}", exc_info=True)
    
    async def close(self):
        """Clean shutdown of the bot"""
        logger.info("Shutting down Robo Nexus Birthday Bot...")
        
        # Stop the birthday scheduler
        if hasattr(self, 'daily_birthday_check'):
            self.daily_birthday_check.cancel()
        
        # Close database connections
        if hasattr(self, 'db_manager'):
            await self.db_manager.close()
        
        # Close the bot
        await super().close()
        logger.info("Bot shutdown complete")

# Helper function to create and run the bot
async def run_bot():
    """Create and run the Robo Nexus Birthday Bot"""
    bot = RoboNexusBirthdayBot()
    
    try:
        await bot.start(Config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.close()