"""
Help Commands for Robo Nexus Birthday Bot
Help system and command guidance
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class HelpCommands(commands.Cog):
    """Cog containing help and guidance commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="birthday_help", description="Show all available birthday bot commands")
    async def birthday_help(self, interaction: discord.Interaction):
        """Show comprehensive help for the birthday bot"""
        try:
            await interaction.response.defer()
            
            # Create main help embed
            embed = discord.Embed(
                title="🎂 Robo Nexus Birthday Bot Help",
                description="Welcome to the Robo Nexus Birthday Bot! Here are all available commands:",
                color=discord.Color.purple()
            )
            
            # User Commands
            user_commands = [
                "**`/register_birthday`** - Register your birthday with the bot",
                "**`/my_birthday`** - Check your registered birthday",
                "**`/check_birthday`** - Look up someone else's birthday",
                "**`/upcoming_birthdays`** - See all upcoming birthdays",
                "**`/remove_birthday`** - Remove your registered birthday",
                "**`/birthday_help`** - Show this help message"
            ]
            
            embed.add_field(
                name="👥 User Commands",
                value="\n".join(user_commands),
                inline=False
            )
            
            # Admin Commands (only show if user has admin permissions)
            if interaction.user.guild_permissions.administrator:
                admin_commands = [
                    "**`/set_birthday_channel`** - Set the birthday announcement channel",
                    "**`/birthday_config`** - View current bot configuration"
                ]
                
                embed.add_field(
                    name="⚙️ Admin Commands",
                    value="\n".join(admin_commands),
                    inline=False
                )
            
            # Date formats
            embed.add_field(
                name="📅 Supported Date Formats",
                value="• **MM-DD** (e.g., `12-25` for December 25)\n• **MM/DD** (e.g., `12/25` for December 25)\n• **MM-DD-YYYY** (e.g., `12-25-1995`)\n• **MM/DD/YYYY** (e.g., `12/25/1995`)",
                inline=False
            )
            
            # How it works
            embed.add_field(
                name="🎉 How Birthday Announcements Work",
                value="• Register your birthday using `/register_birthday`\n• The bot checks daily at 9:00 AM for birthdays\n• Birthday messages are sent to the configured channel\n• Format: 'Hey Robo Nexus, it's @user's birthday today! 🎉'",
                inline=False
            )
            
            # Examples
            embed.add_field(
                name="💡 Examples",
                value="• `/register_birthday date:12-25` - Register December 25th\n• `/check_birthday user:@friend` - Check a friend's birthday\n• `/set_birthday_channel channel:#birthdays` - Set announcement channel (Admin)",
                inline=False
            )
            
            embed.set_footer(text="🤖 Robo Nexus Birthday Bot | Made for the Robo Nexus community")
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in birthday_help command: {e}")
            
            error_embed = discord.Embed(
                title="❌ Something went wrong",
                description="An unexpected error occurred. Please try again later.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed)
    
    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Handle slash command errors and provide helpful suggestions"""
        try:
            if isinstance(error, app_commands.CommandOnCooldown):
                embed = discord.Embed(
                    title="⏰ Command on Cooldown",
                    description=f"Please wait {error.retry_after:.1f} seconds before using this command again.",
                    color=discord.Color.orange()
                )
                
            elif isinstance(error, app_commands.MissingPermissions):
                embed = discord.Embed(
                    title="❌ Missing Permissions",
                    description="You don't have the required permissions to use this command.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="Need help?",
                    value="Use `/birthday_help` to see which commands you can use.",
                    inline=False
                )
                
            elif isinstance(error, app_commands.BotMissingPermissions):
                embed = discord.Embed(
                    title="❌ Bot Missing Permissions",
                    description="I don't have the required permissions to execute this command.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="Required Permissions",
                    value="Please ensure I have Administrator permissions or the specific permissions needed for this command.",
                    inline=False
                )
                
            else:
                # Generic error
                embed = discord.Embed(
                    title="❌ Command Error",
                    description="An error occurred while processing your command.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="Suggestions",
                    value="• Check your command syntax\n• Use `/birthday_help` for command examples\n• Try again in a few moments",
                    inline=False
                )
                
                logger.error(f"Unhandled app command error: {error}")
            
            # Try to send error message
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            except:
                # If we can't send the error message, log it
                logger.error(f"Failed to send error message for command error: {error}")
                
        except Exception as e:
            logger.error(f"Error in error handler: {e}")

async def setup(bot):
    """Add the HelpCommands cog to the bot"""
    await bot.add_cog(HelpCommands(bot))