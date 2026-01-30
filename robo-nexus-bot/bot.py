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
from database import birthday_db
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
        intents.members = True  # Required to detect member joins!
        
        # Initialize bot with proper settings
        super().__init__(
            command_prefix='!',  # Fallback prefix (we'll use slash commands)
            intents=intents,
            help_command=None,  # We'll create our own help system
            case_insensitive=True
        )
        
        # Initialize components
        self.db_manager = birthday_db
        self.scheduler_started = False
        
        logger.info("Robo Nexus Birthday Bot initialized")
    
    async def setup_hook(self):
        """Called when the bot is starting up"""
        try:
            # Database is already initialized in postgres_db.py
            logger.info("Database connection ready")
            
            # Load command cogs
            await self.load_extension('commands')
            await self.load_extension('admin_commands')
            await self.load_extension('help_commands')
            await self.load_extension('dev_commands')
            await self.load_extension('github_integration')
            await self.load_extension('analytics')
            await self.load_extension('auction')
            await self.load_extension('welcome_system')
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
            name="For Robo Nexus :rx:"
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
            
            # Get today's birthdays using synchronous method
            from datetime import date
            today_str = date.today().strftime("%m-%d")
            todays_birthdays = self.db_manager.get_birthdays_today(today_str)
            
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
        Send birthday messages to the configured channel and announcements
        
        Args:
            guild: Discord guild object
            birthdays: List of birthday dictionaries
        """
        try:
            # For now, use a default channel (you can configure this later)
            birthday_channel = None
            
            # Look for a suitable channel
            for channel in guild.text_channels:
                if any(keyword in channel.name.lower() for keyword in ['birthday', 'celebration', 'general']):
                    birthday_channel = channel
                    break
            
            if not birthday_channel:
                logger.warning(f"No suitable birthday channel found in guild {guild.name}")
                return
            
            # Send birthday message for each user
            for birthday_info in birthdays:
                try:
                    user_id = birthday_info['user_id']
                    
                    # Get the user from the guild
                    try:
                        member = await guild.fetch_member(user_id)
                    except:
                        member = guild.get_member(user_id)
                    
                    if member:
                        # Create birthday message
                        birthday_message = f"🎉🎂 **HAPPY BIRTHDAY {member.mention}!** 🎂🎉\n\nEveryone wish them a fantastic day! 🎈🎁🥳"
                        
                        # Send to birthday channel
                        await birthday_channel.send(birthday_message)
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
        """Handle command errors with analytics tracking"""
        if isinstance(error, commands.CommandNotFound):
            # Ignore unknown commands
            return
        
        logger.error(f"Command error: {error}")
        
        # Track error in analytics
        analytics_cog = self.get_cog('Analytics')
        if analytics_cog:
            analytics_cog.track_error(error, f"Command: {ctx.command}")
            await analytics_cog.report_error_to_dev(error, f"Command: {ctx.command}")
        
        # Send error message to user
        try:
            await ctx.send("❌ An error occurred while processing your command. The developers have been notified.")
        except:
            pass  # Channel might not be accessible
    
    async def on_application_command_error(self, interaction: discord.Interaction, error):
        """Handle slash command errors with analytics tracking"""
        logger.error(f"Slash command error: {error}")
        
        # Track error in analytics
        analytics_cog = self.get_cog('Analytics')
        if analytics_cog:
            analytics_cog.track_error(error, f"Slash command: {interaction.command}")
            await analytics_cog.report_error_to_dev(error, f"Slash command: {interaction.command}")
        
        # Send error message to user
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An error occurred while processing your command. The developers have been notified.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ An error occurred while processing your command. The developers have been notified.",
                    ephemeral=True
                )
        except:
            pass
    
    async def on_error(self, event, *args, **kwargs):
        """Handle general bot errors with analytics tracking"""
        logger.error(f"Bot error in event {event}", exc_info=True)
        
        # Track error in analytics
        analytics_cog = self.get_cog('Analytics')
        if analytics_cog:
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if exc_value:
                analytics_cog.track_error(exc_value, f"Event: {event}")
                await analytics_cog.report_error_to_dev(exc_value, f"Event: {event}")
    
    async def close(self):
        """Clean shutdown of the bot"""
        logger.info("Shutting down Robo Nexus Birthday Bot...")
        
        # Stop the birthday scheduler
        if hasattr(self, 'daily_birthday_check'):
            self.daily_birthday_check.cancel()
        
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