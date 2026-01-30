"""
Slash Commands for Robo Nexus Birthday Bot
All Discord slash command implementations
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional

from date_parser import DateParser

logger = logging.getLogger(__name__)

class BirthdayCommands(commands.Cog):
    """Cog containing all birthday-related slash commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db_manager
    
    @app_commands.command(name="register_birthday", description="Register your birthday with the Robo Nexus bot")
    @app_commands.describe(date="Your birthday (formats: MM-DD, MM/DD, MM-DD-YYYY, MM/DD/YYYY)")
    async def register_birthday(self, interaction: discord.Interaction, date: str):
        """Register a user's birthday"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Parse the birthday
            birthday = DateParser.parse_birthday(date)
            
            if not birthday:
                # Invalid date format
                error_embed = discord.Embed(
                    title="❌ Invalid Date Format",
                    description="I couldn't understand that date format.",
                    color=discord.Color.red()
                )
                error_embed.add_field(
                    name="Supported Formats",
                    value=DateParser.get_format_help_text(),
                    inline=False
                )
                error_embed.add_field(
                    name="Examples",
                    value="• `12-25` (December 25)\n• `03/15` (March 15)\n• `12-25-1995` (December 25, 1995)",
                    inline=False
                )
                
                await interaction.followup.send(embed=error_embed)
                return
            
            # Convert date object to MM-DD string format for database
            birthday_string = birthday.strftime('%m-%d')
            
            # Register the birthday in birthdays table
            success = self.db.add_birthday(interaction.user.id, birthday_string)
            
            # Also update user profile if it exists
            try:
                from supabase_api import get_supabase_api
                supabase = get_supabase_api()
                profile = supabase.get_user_profile(str(interaction.user.id))
                if profile:
                    # Update the birthday in user profile too (use string format)
                    supabase.update_user_profile(str(interaction.user.id), {"birthday": birthday_string})
                    logger.info(f"Updated birthday in user profile for {interaction.user.display_name}")
            except Exception as e:
                logger.error(f"Error updating user profile birthday: {e}")
                # Don't fail the command if profile update fails
            
            if success:
                # Success message
                formatted_date = DateParser.format_birthday(birthday)
                success_embed = discord.Embed(
                    title="🎉 Birthday Registered!",
                    description=f"Your birthday has been set to **{formatted_date}**",
                    color=discord.Color.green()
                )
                success_embed.add_field(
                    name="What happens next?",
                    value="• The Robo Nexus community will be notified on your birthday\n• You can update or remove your birthday anytime\n• Use `/my_birthday` to check your registered date",
                    inline=False
                )
                success_embed.set_footer(text="🎂 Happy early birthday from Robo Nexus!")
                
                await interaction.followup.send(embed=success_embed)
                logger.info(f"Birthday registered for {interaction.user.display_name}: {formatted_date}")
                
            else:
                # Database error
                error_embed = discord.Embed(
                    title="❌ Registration Failed",
                    description="There was an error saving your birthday. Please try again.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=error_embed)
                
        except Exception as e:
            logger.error(f"Error in register_birthday command: {e}")
            
            error_embed = discord.Embed(
                title="❌ Something went wrong",
                description="An unexpected error occurred. Please try again later.",
                color=discord.Color.red()
            )
            
            try:
                await interaction.followup.send(embed=error_embed)
            except:
                # If followup fails, try response
                try:
                    await interaction.response.send_message(embed=error_embed, ephemeral=True)
                except:
                    pass  # Give up gracefully
    
    @app_commands.command(name="my_birthday", description="Check your registered birthday")
    async def my_birthday(self, interaction: discord.Interaction):
        """Show the user's registered birthday"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Get user's birthday
            birthday = self.db.get_birthday(interaction.user.id)
            
            if birthday:
                formatted_date = DateParser.format_birthday(birthday)
                
                embed = discord.Embed(
                    title="🎂 Your Birthday",
                    description=f"Your birthday is registered as **{formatted_date}**",
                    color=discord.Color.blue()
                )
                embed.add_field(
                    name="Need to change it?",
                    value="Use `/register_birthday` to update your birthday\nUse `/remove_birthday` to remove it",
                    inline=False
                )
                embed.set_footer(text="🎉 The Robo Nexus community will celebrate with you!")
                
            else:
                embed = discord.Embed(
                    title="📅 No Birthday Registered",
                    description="You haven't registered your birthday yet.",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="Want to register?",
                    value="Use `/register_birthday` to let the Robo Nexus community know when your birthday is!",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in my_birthday command: {e}")
            
            error_embed = discord.Embed(
                title="❌ Something went wrong",
                description="An unexpected error occurred. Please try again later.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed)
    
    @app_commands.command(name="check_birthday", description="Look up someone's birthday")
    @app_commands.describe(user="The user whose birthday you want to check")
    async def check_birthday(self, interaction: discord.Interaction, user: discord.Member):
        """Look up another user's birthday"""
        try:
            await interaction.response.defer()
            
            # Get the user's birthday
            birthday = self.db.get_birthday(user.id)
            
            if birthday:
                formatted_date = DateParser.format_birthday(birthday)
                
                embed = discord.Embed(
                    title=f"🎂 {user.display_name}'s Birthday",
                    description=f"{user.mention}'s birthday is **{formatted_date}**",
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=user.display_avatar.url)
                embed.set_footer(text="🎉 Don't forget to wish them happy birthday!")
                
            else:
                embed = discord.Embed(
                    title="📅 Birthday Not Found",
                    description=f"{user.display_name} hasn't registered their birthday yet.",
                    color=discord.Color.orange()
                )
                embed.set_thumbnail(url=user.display_avatar.url)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in check_birthday command: {e}")
            
            error_embed = discord.Embed(
                title="❌ Something went wrong",
                description="An unexpected error occurred. Please try again later.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed)
    
    @app_commands.command(name="remove_birthday", description="Remove your registered birthday")
    async def remove_birthday(self, interaction: discord.Interaction):
        """Remove the user's birthday registration"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Check if user has a birthday registered
            existing_birthday = self.db.get_birthday(interaction.user.id)
            
            if not existing_birthday:
                embed = discord.Embed(
                    title="📅 No Birthday Registered",
                    description="You don't have a birthday registered to remove.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Remove the birthday
            success = self.db.remove_birthday(interaction.user.id)
            
            if success:
                embed = discord.Embed(
                    title="✅ Birthday Removed",
                    description="Your birthday has been removed from the Robo Nexus system.",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="Want to register again?",
                    value="You can use `/register_birthday` anytime to register your birthday again.",
                    inline=False
                )
                
                logger.info(f"Birthday removed for {interaction.user.display_name}")
                
            else:
                embed = discord.Embed(
                    title="❌ Removal Failed",
                    description="There was an error removing your birthday. Please try again.",
                    color=discord.Color.red()
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in remove_birthday command: {e}")
            
            error_embed = discord.Embed(
                title="❌ Something went wrong",
                description="An unexpected error occurred. Please try again later.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed)
    
    @app_commands.command(name="upcoming_birthdays", description="See all upcoming birthdays in Robo Nexus")
    async def upcoming_birthdays(self, interaction: discord.Interaction):
        """Show all upcoming birthdays"""
        try:
            await interaction.response.defer()
            
            # Get all birthdays
            all_birthdays = self.db.get_all_birthdays()
            
            if not all_birthdays:
                embed = discord.Embed(
                    title="📅 No Birthdays Registered",
                    description="No one has registered their birthday yet in Robo Nexus!",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="Be the first!",
                    value="Use `/register_birthday` to register your birthday and start the celebration list!",
                    inline=False
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create birthday list
            birthday_list = []
            for birthday_record in all_birthdays[:10]:  # Limit to 10 for display
                try:
                    # Extract user_id and birthday from the record
                    if isinstance(birthday_record, dict):
                        user_id = int(birthday_record['user_id'])
                        birthday_date = birthday_record['birthday']
                    else:
                        # Handle tuple format (legacy)
                        user_id, birthday_date = birthday_record
                    
                    # Try to fetch member from Discord API (more reliable than get_member)
                    user = await interaction.guild.fetch_member(user_id)
                    if user:
                        formatted_date = DateParser.format_birthday(birthday_date)
                        birthday_list.append(f"🎂 **{user.display_name}** - {formatted_date}")
                except discord.NotFound:
                    # User not in this guild, skip
                    continue
                except Exception as e:
                    # Log other errors but continue
                    logger.warning(f"Error processing birthday record {birthday_record}: {e}")
                    continue
            
            if not birthday_list:
                embed = discord.Embed(
                    title="📅 No Birthdays in This Server",
                    description="No registered birthdays found for members of this server.",
                    color=discord.Color.orange()
                )
            else:
                embed = discord.Embed(
                    title="🎉 Upcoming Birthdays in Robo Nexus",
                    description="\n".join(birthday_list),
                    color=discord.Color.purple()
                )
                
                if len(all_birthdays) > 10:
                    embed.set_footer(text=f"Showing first 10 of {len(all_birthdays)} registered birthdays")
                else:
                    embed.set_footer(text=f"{len(birthday_list)} registered birthdays")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in upcoming_birthdays command: {e}")
            
            error_embed = discord.Embed(
                title="❌ Something went wrong",
                description="An unexpected error occurred. Please try again later.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed)

async def setup(bot):
    """Add the BirthdayCommands cog to the bot"""
    await bot.add_cog(BirthdayCommands(bot))