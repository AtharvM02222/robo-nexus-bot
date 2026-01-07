"""
Admin Commands for Robo Nexus Birthday Bot
Administrative slash commands for server configuration
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class AdminCommands(commands.Cog):
    """Cog containing administrative commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db_manager
    
    @app_commands.command(name="set_birthday_channel", description="[ADMIN] Set the channel for birthday announcements")
    @app_commands.describe(channel="The channel where birthday messages will be sent")
    @app_commands.default_permissions(administrator=True)
    async def set_birthday_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set the birthday announcement channel (Admin only)"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Check if user has administrator permissions
            if not interaction.user.guild_permissions.administrator:
                embed = discord.Embed(
                    title="❌ Permission Denied",
                    description="You need Administrator permissions to configure the birthday channel.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Check if bot can send messages to the channel
            if not channel.permissions_for(interaction.guild.me).send_messages:
                embed = discord.Embed(
                    title="❌ Invalid Channel",
                    description=f"I don't have permission to send messages in {channel.mention}.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="Required Permissions",
                    value="• Send Messages\n• View Channel",
                    inline=False
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Save the channel configuration
            success = await self.db.set_birthday_channel(interaction.guild.id, channel.id)
            
            if success:
                embed = discord.Embed(
                    title="✅ Birthday Channel Set",
                    description=f"Birthday announcements will now be sent to {channel.mention}",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="What happens next?",
                    value="• Daily birthday checks will post messages here\n• Messages will use the format: 'Hey Robo Nexus, it's @user's birthday today! 🎉'\n• The bot checks for birthdays every day at 9:00 AM",
                    inline=False
                )
                embed.set_footer(text="🎂 Robo Nexus Birthday Bot is ready!")
                
                logger.info(f"Birthday channel set to {channel.name} in {interaction.guild.name}")
                
            else:
                embed = discord.Embed(
                    title="❌ Configuration Failed",
                    description="There was an error saving the channel configuration. Please try again.",
                    color=discord.Color.red()
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in set_birthday_channel command: {e}")
            
            error_embed = discord.Embed(
                title="❌ Something went wrong",
                description="An unexpected error occurred. Please try again later.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed)
    
    @app_commands.command(name="birthday_config", description="[ADMIN] View current birthday bot configuration")
    @app_commands.default_permissions(administrator=True)
    async def birthday_config(self, interaction: discord.Interaction):
        """Show current birthday bot configuration (Admin only)"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Check if user has administrator permissions
            if not interaction.user.guild_permissions.administrator:
                embed = discord.Embed(
                    title="❌ Permission Denied",
                    description="You need Administrator permissions to view the birthday configuration.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Get current configuration
            channel_id = await self.db.get_birthday_channel(interaction.guild.id)
            
            embed = discord.Embed(
                title="⚙️ Robo Nexus Birthday Bot Configuration",
                color=discord.Color.blue()
            )
            
            # Birthday channel status
            if channel_id:
                channel = interaction.guild.get_channel(channel_id)
                if channel:
                    embed.add_field(
                        name="🎂 Birthday Channel",
                        value=f"✅ {channel.mention}",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="🎂 Birthday Channel",
                        value=f"❌ Channel not found (ID: {channel_id})\nPlease reconfigure with `/set_birthday_channel`",
                        inline=False
                    )
            else:
                embed.add_field(
                    name="🎂 Birthday Channel",
                    value="❌ Not configured\nUse `/set_birthday_channel` to set up birthday announcements",
                    inline=False
                )
            
            # Get birthday statistics
            all_birthdays = await self.db.get_all_birthdays()
            guild_birthdays = []
            
            for user_id, birthday_date in all_birthdays:
                try:
                    # Try to fetch member from Discord API (more reliable than get_member)
                    member = await interaction.guild.fetch_member(user_id)
                    if member:
                        guild_birthdays.append((member, birthday_date))
                except discord.NotFound:
                    # User not in this guild, skip
                    continue
                except Exception as e:
                    # Log other errors but continue
                    logger.warning(f"Error fetching member {user_id}: {e}")
                    continue
            
            embed.add_field(
                name="📊 Statistics",
                value=f"• **{len(guild_birthdays)}** registered birthdays in this server\n• **{len(all_birthdays)}** total registered birthdays\n• Daily check time: **9:00 AM**",
                inline=False
            )
            
            # Bot status
            embed.add_field(
                name="🤖 Bot Status",
                value=f"• Status: **Online** ✅\n• Scheduler: **{'Running' if self.bot.scheduler_started else 'Not Started'}**\n• Permissions: **Administrator** ✅",
                inline=False
            )
            
            embed.set_footer(text="🎉 Robo Nexus Birthday Bot")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in birthday_config command: {e}")
            
            error_embed = discord.Embed(
                title="❌ Something went wrong",
                description="An unexpected error occurred. Please try again later.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed)

async def setup(bot):
    """Add the AdminCommands cog to the bot"""
    await bot.add_cog(AdminCommands(bot))