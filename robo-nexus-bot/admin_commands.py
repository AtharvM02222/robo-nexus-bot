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
        from supabase_api import get_supabase_api
        self.db = get_supabase_api()
    
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
            success = self.db.set_setting(f'birthday_channel_{interaction.guild.id}', str(channel.id))
            
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
            channel_id = self.db.get_setting(f'birthday_channel_{interaction.guild.id}')
            if channel_id:
                channel_id = int(channel_id)
            
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
            all_birthdays = self.db.get_all_birthdays()
            guild_birthdays = []
            
            for birthday in all_birthdays:
                user_id = int(birthday['user_id'])
                birthday_date = birthday['birthday']
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
                value=f"• Status: **Online** ✅\n• Database: **PostgreSQL** ✅\n• Permissions: **Administrator** ✅",
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
    
    @app_commands.command(name="verification_stats", description="[ADMIN] View verification statistics")
    @app_commands.default_permissions(administrator=True)
    async def verification_stats(self, interaction: discord.Interaction):
        """Show verification statistics for the server"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Check if user has administrator permissions
            if not interaction.user.guild_permissions.administrator:
                embed = discord.Embed(
                    title="❌ Permission Denied",
                    description="You need Administrator permissions to view verification statistics.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Get verification data from database
            from supabase_api import get_supabase_api
            db = get_supabase_api()
            
            # Get all user profiles (verified users)
            try:
                profiles = db.get_all_user_profiles()
            except Exception as e:
                logger.error(f"Error getting user profiles: {e}")
                profiles = []
            
            # Count verification statuses
            verified_count = 0
            pending_count = 0
            self_role_count = 0
            manual_verify_count = 0
            
            verified_users = []
            pending_users = []
            
            for profile in profiles:
                user_id = profile.get('user_id')
                username = profile.get('username')
                status = profile.get('verification_status', 'verified')  # Default to verified
                stage = profile.get('verification_stage', 'complete')    # Default to complete
                
                # Try to get member from guild
                try:
                    member = interaction.guild.get_member(int(user_id))
                    if not member:
                        continue  # Skip users not in this guild
                    
                    if status == 'verified':
                        verified_count += 1
                        verified_users.append(f"• {member.display_name} ({username})")
                        
                        # Check if they have self-roles (assuming verified role exists)
                        has_verified_role = any(role.name.lower() in ['verified', 'member'] for role in member.roles)
                        if has_verified_role:
                            self_role_count += 1
                        else:
                            manual_verify_count += 1
                            
                    elif status == 'pending':
                        pending_count += 1
                        pending_users.append(f"• {member.display_name} ({username}) - Stage: {stage}")
                        
                except Exception as e:
                    logger.warning(f"Error processing user {user_id}: {e}")
                    continue
            
            # Get total server members
            total_members = interaction.guild.member_count
            unverified_count = total_members - verified_count - pending_count
            
            # Create embed
            embed = discord.Embed(
                title="📊 Verification Statistics",
                description=f"Server: **{interaction.guild.name}**",
                color=discord.Color.blue()
            )
            
            # Overview stats
            embed.add_field(
                name="📈 Overview",
                value=f"**Total Members:** {total_members}\n"
                      f"**✅ Verified:** {verified_count}\n"
                      f"**⏳ Pending:** {pending_count}\n"
                      f"**❌ Unverified:** {unverified_count}",
                inline=True
            )
            
            # Verification breakdown
            embed.add_field(
                name="🔍 Verification Breakdown",
                value=f"**🤖 Self-Role Verified:** {self_role_count}\n"
                      f"**👤 Manual Verified:** {manual_verify_count}\n"
                      f"**📝 In Progress:** {pending_count}",
                inline=True
            )
            
            # Percentages
            verified_percent = (verified_count / total_members * 100) if total_members > 0 else 0
            pending_percent = (pending_count / total_members * 100) if total_members > 0 else 0
            
            embed.add_field(
                name="📊 Percentages",
                value=f"**Verified:** {verified_percent:.1f}%\n"
                      f"**Pending:** {pending_percent:.1f}%\n"
                      f"**Unverified:** {100 - verified_percent - pending_percent:.1f}%",
                inline=True
            )
            
            # Recent verified users (last 10)
            if verified_users:
                recent_verified = "\n".join(verified_users[:10])
                if len(verified_users) > 10:
                    recent_verified += f"\n... and {len(verified_users) - 10} more"
                embed.add_field(
                    name="✅ Recently Verified Users",
                    value=recent_verified[:1024],  # Discord field limit
                    inline=False
                )
            
            # Pending users
            if pending_users:
                pending_list = "\n".join(pending_users[:10])
                if len(pending_users) > 10:
                    pending_list += f"\n... and {len(pending_users) - 10} more"
                embed.add_field(
                    name="⏳ Pending Verification",
                    value=pending_list[:1024],  # Discord field limit
                    inline=False
                )
            
            embed.set_footer(text="🔐 Robo Nexus Verification System")
            embed.timestamp = discord.utils.utcnow()
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in verification_stats command: {e}")
            
            error_embed = discord.Embed(
                title="❌ Something went wrong",
                description="An unexpected error occurred while fetching verification statistics.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed)
    
    @app_commands.command(name="reset_birthdays", description="[ADMIN] Delete ALL birthdays from database")
    @app_commands.default_permissions(administrator=True)
    async def reset_birthdays(self, interaction: discord.Interaction):
        """Delete all birthdays from the database"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Check if user has administrator permissions
            if not interaction.user.guild_permissions.administrator:
                embed = discord.Embed(
                    title="❌ Permission Denied",
                    description="You need Administrator permissions to reset birthdays.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Get count before deletion
            all_birthdays = self.db.get_all_birthdays()
            count = len(all_birthdays)
            
            if count == 0:
                embed = discord.Embed(
                    title="📋 No Birthdays",
                    description="There are no birthdays to delete.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Delete all birthdays
            success = self.db.delete_all_birthdays()
            
            if success:
                embed = discord.Embed(
                    title="✅ Birthdays Reset",
                    description=f"Successfully deleted all birthdays from the database.",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="⚠️ Warning",
                    value="This action cannot be undone. Users will need to re-register their birthdays.",
                    inline=False
                )
                
                await interaction.followup.send(embed=embed)
                logger.info(f"All birthdays reset by {interaction.user}")
            else:
                embed = discord.Embed(
                    title="❌ Reset Failed",
                    description="There was an error deleting birthdays from the database.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in reset_birthdays: {e}")
            
            error_embed = discord.Embed(
                title="❌ Something went wrong",
                description="An unexpected error occurred while resetting birthdays.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed)
    
    @app_commands.command(name="reset_auctions", description="[ADMIN] Delete ALL auctions from database")
    @app_commands.default_permissions(administrator=True)
    async def reset_auctions(self, interaction: discord.Interaction):
        """Delete all auctions from the database"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Check if user has administrator permissions
            if not interaction.user.guild_permissions.administrator:
                embed = discord.Embed(
                    title="❌ Permission Denied",
                    description="You need Administrator permissions to reset auctions.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Get count before deletion
            all_auctions = self.db.get_all_auctions('active')
            count = len(all_auctions)
            
            # Delete all auctions and bids
            success = self.db.delete_all_auctions()
            
            if success:
                embed = discord.Embed(
                    title="✅ Auctions Reset",
                    description=f"Successfully deleted all auctions and bids from the database.",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="⚠️ Warning",
                    value="This action cannot be undone. All auction data has been permanently deleted.",
                    inline=False
                )
                
                await interaction.followup.send(embed=embed)
                logger.info(f"All auctions reset by {interaction.user}")
            else:
                embed = discord.Embed(
                    title="❌ Reset Failed",
                    description="There was an error deleting auctions from the database.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in reset_auctions: {e}")
            
            error_embed = discord.Embed(
                title="❌ Something went wrong",
                description="An unexpected error occurred while resetting auctions.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed)
    
    @app_commands.command(name="purge", description="[ADMIN] Delete multiple messages")
    @app_commands.describe(
        count="Number of messages to delete (1-100)",
        channel="Channel to purge messages from (optional, defaults to current channel)"
    )
    @app_commands.default_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, count: int, channel: discord.TextChannel = None):
        """Delete multiple messages from a specific channel"""
        try:
            # Check if user has manage messages permission
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message(
                    "❌ You need Manage Messages permission to use this command.",
                    ephemeral=True
                )
                return
            
            # Validate count
            if count < 1 or count > 100:
                await interaction.response.send_message(
                    "❌ Count must be between 1 and 100.",
                    ephemeral=True
                )
                return
            
            # Use specified channel or current channel
            target_channel = channel if channel else interaction.channel
            
            await interaction.response.defer(ephemeral=True)
            
            # Delete messages
            deleted = await target_channel.purge(limit=count)
            
            embed = discord.Embed(
                title="✅ Messages Deleted",
                description=f"Successfully deleted **{len(deleted)}** message(s) from {target_channel.mention}.",
                color=discord.Color.green()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"{interaction.user} purged {len(deleted)} messages in {target_channel.name}")
            
        except discord.Forbidden:
            await interaction.followup.send(
                f"❌ I don't have permission to delete messages in {target_channel.mention}.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in purge command: {e}")
            await interaction.followup.send(
                "❌ An error occurred while deleting messages.",
                ephemeral=True
            )
    
    @app_commands.command(name="reset_all_except_auctions", description="[ADMIN] Reset ALL data EXCEPT auctions")
    @app_commands.default_permissions(administrator=True)
    async def reset_all_except_auctions(self, interaction: discord.Interaction):
        """Delete all birthdays, user profiles, and welcome data but keep auctions"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Check if user has administrator permissions
            if not interaction.user.guild_permissions.administrator:
                embed = discord.Embed(
                    title="❌ Permission Denied",
                    description="You need Administrator permissions to reset data.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Get counts before deletion
            all_birthdays = self.db.get_all_birthdays()
            birthday_count = len(all_birthdays)
            
            all_profiles = self.db.get_all_user_profiles()
            profile_count = len(all_profiles)
            
            all_auctions = self.db.get_all_auctions('active')
            auction_count = len(all_auctions)
            
            bids_count = 0
            for auction in all_auctions:
                bids = self.db.get_auction_bids(auction['id'])
                bids_count += len(bids)
            
            # Create confirmation embed
            confirm_embed = discord.Embed(
                title="⚠️ CONFIRM DATA RESET",
                description="This will delete ALL data EXCEPT auctions!",
                color=discord.Color.orange()
            )
            confirm_embed.add_field(
                name="❌ Will DELETE:",
                value=f"• **{birthday_count}** birthdays\n• **{profile_count}** user profiles",
                inline=False
            )
            confirm_embed.add_field(
                name="✅ Will KEEP:",
                value=f"• **{auction_count}** auctions\n• **{bids_count}** bids",
                inline=False
            )
            confirm_embed.add_field(
                name="⚠️ Warning",
                value="This action **CANNOT BE UNDONE**. All deleted data will be permanently lost.",
                inline=False
            )
            confirm_embed.set_footer(text="Type 'CONFIRM' in the next 30 seconds to proceed")
            
            await interaction.followup.send(embed=confirm_embed)
            
            # Wait for confirmation
            def check(m):
                return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id and m.content.upper() == 'CONFIRM'
            
            try:
                msg = await self.bot.wait_for('message', timeout=30.0, check=check)
                
                # Delete the confirmation message
                try:
                    await msg.delete()
                except:
                    pass
                
                # Perform deletion
                birthday_success = self.db.delete_all_birthdays()
                profile_success = self.db.delete_all_user_profiles()
                
                if birthday_success and profile_success:
                    # Send success message
                    success_embed = discord.Embed(
                        title="✅ Data Reset Complete",
                        description="All data has been reset except auctions!",
                        color=discord.Color.green()
                    )
                    success_embed.add_field(
                        name="❌ Deleted:",
                        value=f"• **{birthday_count}** birthdays\n• **{profile_count}** user profiles",
                        inline=False
                    )
                    success_embed.add_field(
                        name="✅ Kept:",
                        value=f"• **{auction_count}** auctions\n• **{bids_count}** bids",
                        inline=False
                    )
                    success_embed.add_field(
                        name="🚀 Next Steps:",
                        value="1. Remove members from server\n2. Add them back one at a time\n3. Each member will go through verification\n4. Bot will collect all their info",
                        inline=False
                    )
                    
                    await interaction.followup.send(embed=success_embed)
                    logger.info(f"Data reset by {interaction.user} - kept {auction_count} auctions, deleted {birthday_count} birthdays, {profile_count} profiles")
                else:
                    error_embed = discord.Embed(
                        title="❌ Reset Failed",
                        description="There was an error deleting some data. Please check the logs.",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=error_embed)
                
            except TimeoutError:
                timeout_embed = discord.Embed(
                    title="❌ Reset Cancelled",
                    description="Confirmation not received within 30 seconds. No data was deleted.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=timeout_embed)
            
        except Exception as e:
            logger.error(f"Error in reset_all_except_auctions: {e}")
            
            error_embed = discord.Embed(
                title="❌ Something went wrong",
                description="An unexpected error occurred while resetting data.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed)

    @app_commands.command(name="test_birthday", description="[ADMIN] Manually trigger birthday check for today")
    @app_commands.default_permissions(administrator=True)
    async def test_birthday(self, interaction: discord.Interaction):
        """Manually trigger birthday announcements for today"""
        try:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ You need Administrator permissions to use this command.",
                    ephemeral=True
                )
                return
            
            await interaction.response.defer()
            
            # Get today's birthdays
            from database import get_all_birthdays
            from datetime import datetime
            
            today = datetime.now().strftime("%m-%d")
            all_birthdays = get_all_birthdays()
            todays_birthdays = [(b['user_id'], b['birthday']) for b in all_birthdays if b['birthday'] == today]
            
            if not todays_birthdays:
                embed = discord.Embed(
                    title="🎂 No Birthdays Today",
                    description="There are no registered birthdays for today.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Get birthday channel
            channel_id = self.db.get_setting(f'birthday_channel_{interaction.guild.id}')
            if channel_id:
                channel_id = int(channel_id)
            
            if not channel_id:
                await interaction.followup.send(
                    "❌ Birthday channel not configured. Use `/set_birthday_channel` first.",
                    ephemeral=True
                )
                return
            
            channel = interaction.guild.get_channel(channel_id)
            if not channel:
                await interaction.followup.send(
                    "❌ Birthday channel not found. Please reconfigure with `/set_birthday_channel`.",
                    ephemeral=True
                )
                return
            
            # Send birthday messages
            sent_count = 0
            for user_id, birthday_date in todays_birthdays:
                try:
                    member = await interaction.guild.fetch_member(int(user_id))
                    if member:
                        # Send to birthday channel with @everyone
                        message = f"@everyone\n\n🎉🎂 **HAPPY BIRTHDAY {member.mention}!** 🎂🎉\n\nEveryone wish them a fantastic day! 🎈🎁🥳"
                        await channel.send(message)
                        sent_count += 1
                        
                        # Try to send to announcements channel too
                        for ann_channel in interaction.guild.text_channels:
                            if 'announcement' in ann_channel.name.lower() and ann_channel.id != channel.id:
                                try:
                                    ann_msg = f"@everyone\n\n🎂 **Birthday Alert!** 🎂\n\nToday is **{member.display_name}**'s birthday! Head over to {channel.mention} to wish them! 🎉"
                                    await ann_channel.send(ann_msg)
                                except:
                                    pass
                                break
                except discord.NotFound:
                    continue
                except Exception as e:
                    logger.error(f"Error sending birthday message for {user_id}: {e}")
            
            embed = discord.Embed(
                title="✅ Birthday Check Complete",
                description=f"Sent **{sent_count}** birthday announcement(s) to {channel.mention}",
                color=discord.Color.green()
            )
            embed.add_field(
                name="🎂 Today's Birthdays",
                value=f"Found **{len(todays_birthdays)}** birthday(s)",
                inline=True
            )
            
            await interaction.followup.send(embed=embed)
            logger.info(f"Manual birthday check triggered by {interaction.user}, sent {sent_count} messages")
            
        except Exception as e:
            logger.error(f"Error in test_birthday: {e}")
            await interaction.followup.send(
                f"❌ Error running birthday check: {str(e)[:100]}",
                ephemeral=True
            )

async def setup(bot):
    """Add the AdminCommands cog to the bot"""
    await bot.add_cog(AdminCommands(bot))