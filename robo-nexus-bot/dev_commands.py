"""
Robo Nexus Birthday Bot - Developer Commands
Fully automated deployment management and monitoring from Discord
"""
import discord
from discord import app_commands
from discord.ext import commands, tasks
import logging
import subprocess
import os
import json
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

DEPLOY_INFO_FILE = "deploy_info.json"

class DevCommands(commands.Cog):
    """Fully automated developer commands for bot management"""
    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now()
        self.deploy_info = self.load_deploy_info()
        self.dev_channel_id = None
        
        # Start auto-monitoring
        self.auto_monitor.start()
    
    def load_deploy_info(self) -> dict:
        """Load deployment info with auto-detection"""
        try:
            if os.path.exists(DEPLOY_INFO_FILE):
                with open(DEPLOY_INFO_FILE, 'r') as f:
                    data = json.load(f)
                    # Auto-update publish date if needed
                    auto_date = self.auto_detect_publish_date()
                    if auto_date > data.get("last_publish", "2020-01-01"):
                        data["last_publish"] = auto_date
                    return data
        except Exception as e:
            logger.error(f"Error loading deploy info: {e}")
        
        return {
            "last_publish": self.auto_detect_publish_date(),
            "last_pull": None,
            "version": "1.1.0",
            "pull_history": [],
            "notifications_sent": []
        }
    
    def auto_detect_publish_date(self) -> str:
        """Auto-detect when the app was published by checking file timestamps"""
        try:
            # Check Replit-specific files
            replit_files = ['.replit', 'replit.nix', '.replit.nix', 'main.py']
            
            latest_time = None
            for file in replit_files:
                if os.path.exists(file):
                    mtime = os.path.getmtime(file)
                    file_time = datetime.fromtimestamp(mtime)
                    if latest_time is None or file_time > latest_time:
                        latest_time = file_time
            
            return (latest_time or datetime.now()).isoformat()
            
        except Exception as e:
            logger.error(f"Error auto-detecting publish date: {e}")
            return datetime.now().isoformat()
    
    def save_deploy_info(self):
        """Save deployment info to file"""
        try:
            with open(DEPLOY_INFO_FILE, 'w') as f:
                json.dump(self.deploy_info, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving deploy info: {e}")
    
    def is_dev(self, user_id: int) -> bool:
        """Check if user is a developer"""
        DEV_IDS = [1147221423815938179]  # Your Discord ID
        return user_id in DEV_IDS
    
    async def get_dev_channel(self):
        """Auto-find dev channel"""
        if self.dev_channel_id:
            return self.bot.get_channel(self.dev_channel_id)
        
        # Look for dev-related channels
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                name = channel.name.lower()
                if any(keyword in name for keyword in ['dev', 'bot', 'admin', 'website']):
                    self.dev_channel_id = channel.id
                    return channel
        
        # Fallback to first channel
        for guild in self.bot.guilds:
            if guild.text_channels:
                self.dev_channel_id = guild.text_channels[0].id
                return guild.text_channels[0]
        
        return None
    
    @tasks.loop(hours=6)  # Check every 6 hours
    async def auto_monitor(self):
        """Automatically monitor and send republish notifications"""
        try:
            # Auto-update publish date
            auto_date = self.auto_detect_publish_date()
            current_date = self.deploy_info.get("last_publish")
            
            if auto_date > current_date:
                self.deploy_info["last_publish"] = auto_date
                self.deploy_info["notifications_sent"] = []  # Reset notifications
                self.save_deploy_info()
            
            last_publish = datetime.fromisoformat(self.deploy_info["last_publish"])
            expire_date = last_publish + timedelta(days=30)
            days_left = (expire_date - datetime.now()).days
            
            channel = await self.get_dev_channel()
            if not channel:
                return
            
            notifications_sent = self.deploy_info.get("notifications_sent", [])
            
            # Send notifications at key intervals
            if days_left == 7 and "7_days" not in notifications_sent:
                await self.send_republish_reminder(channel, days_left, "🟡")
                notifications_sent.append("7_days")
                
            elif days_left == 3 and "3_days" not in notifications_sent:
                await self.send_republish_reminder(channel, days_left, "🟠")
                notifications_sent.append("3_days")
                
            elif days_left == 1 and "1_day" not in notifications_sent:
                await self.send_republish_reminder(channel, days_left, "🔴")
                notifications_sent.append("1_day")
                
            elif days_left <= 0 and "expired" not in notifications_sent:
                await self.send_expired_notification(channel)
                notifications_sent.append("expired")
            
            self.deploy_info["notifications_sent"] = notifications_sent
            self.save_deploy_info()
            
        except Exception as e:
            logger.error(f"Error in auto_monitor: {e}")
    
    async def send_republish_reminder(self, channel, days_left, emoji):
        """Send automatic republish reminder"""
        embed = discord.Embed(
            title=f"{emoji} Auto-Republish Reminder",
            description=f"Your Replit app expires in **{days_left} day{'s' if days_left != 1 else ''}**!",
            color=discord.Color.orange() if days_left > 1 else discord.Color.red()
        )
        
        embed.add_field(
            name="🔗 Quick Action",
            value="[Republish on Replit](https://replit.com/@atharvam682/robo-nexus-bot)",
            inline=False
        )
        
        embed.set_footer(text="🤖 Automatic monitoring • No manual tracking needed!")
        
        await channel.send(embed=embed)
        logger.info(f"Auto-sent {days_left}-day republish reminder")
    
    async def send_expired_notification(self, channel):
        """Send automatic expired notification"""
        embed = discord.Embed(
            title="🚨 AUTO-ALERT: App Expired!",
            description="Your Replit app has expired and may stop working!",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="⚡ Immediate Action",
            value="[Republish NOW on Replit](https://replit.com/@atharvam682/robo-nexus-bot)",
            inline=False
        )
        
        await channel.send(embed=embed)
        logger.warning("Auto-sent app expired notification")
    
    @auto_monitor.before_loop
    async def before_auto_monitor(self):
        """Wait for bot to be ready"""
        await self.bot.wait_until_ready()
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.auto_monitor.cancel()
    
    @app_commands.command(name="republish_status", description="Check auto-detected republish status")
    async def republish_status(self, interaction: discord.Interaction):
        """Show automatically detected republish status"""
        
        try:
            # Auto-update publish date
            auto_date = self.auto_detect_publish_date()
            current_date = self.deploy_info.get("last_publish")
            
            if auto_date > current_date:
                self.deploy_info["last_publish"] = auto_date
                self.save_deploy_info()
            
            last_publish = datetime.fromisoformat(self.deploy_info["last_publish"])
            expire_date = last_publish + timedelta(days=30)
            time_left = expire_date - datetime.now()
            days_left = time_left.days
            hours_left = int(time_left.total_seconds() // 3600) % 24
            
            # Status determination
            if days_left > 14:
                color = discord.Color.green()
                status_emoji = "🟢"
                status_text = "Healthy"
            elif days_left > 7:
                color = discord.Color.yellow()
                status_emoji = "🟡"
                status_text = "Republish Soon"
            elif days_left > 0:
                color = discord.Color.orange()
                status_emoji = "🟠"
                status_text = "Action Required Soon!"
            else:
                color = discord.Color.red()
                status_emoji = "🔴"
                status_text = "EXPIRED - Republish Now!"
            
            embed = discord.Embed(
                title="🤖 Auto-Republish Status",
                description=f"{status_emoji} **{status_text}**",
                color=color
            )
            
            embed.add_field(
                name="⏰ Time Remaining",
                value=f"**{max(0, days_left)}** days, **{max(0, hours_left)}** hours",
                inline=True
            )
            
            embed.add_field(
                name="📆 Auto-Detected Publish",
                value=last_publish.strftime("%B %d, %Y"),
                inline=True
            )
            
            embed.add_field(
                name="💀 Expires On",
                value=expire_date.strftime("%B %d, %Y"),
                inline=True
            )
            
            # Progress bar
            progress = max(0, min(30, 30 - days_left))
            bar_filled = int(progress / 30 * 10)
            bar_empty = 10 - bar_filled
            progress_bar = "█" * bar_filled + "░" * bar_empty
            
            embed.add_field(
                name="📊 Expiry Progress",
                value=f"`[{progress_bar}]` {progress}/30 days used",
                inline=False
            )
            
            embed.add_field(
                name="🤖 Automation Status",
                value="✅ **Fully Automatic** - Reminders at 7, 3, and 1 day(s) left",
                inline=False
            )
            
            if days_left <= 7:
                embed.add_field(
                    name="🔗 Quick Action",
                    value="[Republish on Replit](https://replit.com/@atharvam682/robo-nexus-bot)",
                    inline=False
                )
            
            embed.set_footer(text="🔄 Fully automated • No manual tracking required!")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in republish_status: {e}")
            await interaction.response.send_message(
                "❌ Error checking republish status.",
                ephemeral=True
            )
    
    @app_commands.command(name="pull", description="[DEV] Pull latest code from GitHub")
    async def pull_code(self, interaction: discord.Interaction):
        """Pull latest code from GitHub repository"""
        
        if not self.is_dev(interaction.user.id):
            await interaction.response.send_message(
                "❌ This command is only available to developers.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="🔄 Pulling from GitHub...",
                description="Fetching latest changes from repository",
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed)
            
            # Run git pull
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout.strip() or "Already up to date."
                
                # Update deploy info
                self.deploy_info["last_pull"] = datetime.now().isoformat()
                self.deploy_info["pull_history"].append({
                    "time": datetime.now().isoformat(),
                    "user": str(interaction.user),
                    "result": "success"
                })
                self.deploy_info["pull_history"] = self.deploy_info["pull_history"][-10:]
                self.save_deploy_info()
                
                embed = discord.Embed(
                    title="✅ Git Pull Successful!",
                    description=f"```\n{output[:500]}\n```",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="⚠️ Note",
                    value="Use `/restart` to apply changes.",
                    inline=False
                )
                embed.set_footer(text=f"Pulled by {interaction.user.display_name}")
                
            else:
                error = result.stderr.strip() or "Unknown error"
                embed = discord.Embed(
                    title="❌ Git Pull Failed",
                    description=f"```\n{error[:500]}\n```",
                    color=discord.Color.red()
                )
            
            await interaction.edit_original_response(embed=embed)
            logger.info(f"Git pull executed by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error during git pull: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)[:200]}",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed)
    
    @app_commands.command(name="status", description="Check comprehensive bot status")
    async def status(self, interaction: discord.Interaction):
        """Show detailed bot status with auto-monitoring info"""
        
        # Calculate uptime
        uptime = datetime.now() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        embed = discord.Embed(
            title="🤖 Robo Nexus Birthday Bot Status",
            color=discord.Color.purple()
        )
        
        embed.add_field(name="📊 Status", value="🟢 **Online**", inline=True)
        embed.add_field(name="📦 Version", value=f"`{self.deploy_info.get('version', '1.1.0')}`", inline=True)
        embed.add_field(name="⏱️ Uptime", value=f"{days}d {hours}h {minutes}m", inline=True)
        
        embed.add_field(name="🌐 Servers", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="📡 Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        # Last pull
        last_pull = self.deploy_info.get("last_pull")
        pull_text = "Never"
        if last_pull:
            last_pull_dt = datetime.fromisoformat(last_pull)
            pull_text = last_pull_dt.strftime("%b %d, %H:%M")
        embed.add_field(name="🔄 Last Pull", value=pull_text, inline=True)
        
        # Auto-monitoring
        embed.add_field(name="🤖 Auto-Monitor", value="✅ **Active**", inline=True)
        
        # Scheduler
        scheduler_status = "✅ Running" if self.bot.scheduler_started else "❌ Not Started"
        embed.add_field(name="⏰ Birthday Scheduler", value=scheduler_status, inline=True)
        
        # Republish countdown
        try:
            last_publish = datetime.fromisoformat(self.deploy_info.get("last_publish"))
            days_left = (last_publish + timedelta(days=30) - datetime.now()).days
            embed.add_field(name="📅 Republish In", value=f"{max(0, days_left)} days", inline=True)
        except:
            pass
        
        embed.set_footer(text=f"🔄 Fully automated • Started: {self.start_time.strftime('%b %d, %H:%M')}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="restart", description="[DEV] Restart the bot")
    async def restart_bot(self, interaction: discord.Interaction):
        """Restart the bot"""
        
        if not self.is_dev(interaction.user.id):
            await interaction.response.send_message(
                "❌ This command is only available to developers.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="🔄 Restarting Bot...",
            description="Bot will restart automatically. Back online in ~10 seconds.",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Restart by {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"Bot restart initiated by {interaction.user}")
        
        # Exit - Replit auto-restarts
        import sys
        sys.exit(0)


async def setup(bot):
    """Setup function to add the cog to the bot"""
    await bot.add_cog(DevCommands(bot))
    logger.info("DevCommands cog loaded - Fully automated monitoring active!")