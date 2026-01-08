"""
Analytics and Performance Monitoring for Robo Nexus Birthday Bot
Tracks usage, performance metrics, and error reporting
"""
import discord
from discord import app_commands
from discord.ext import commands, tasks
import logging
import json
import os
import psutil
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class Analytics(commands.Cog):
    """Analytics and performance monitoring system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now()
        
        # Analytics data
        self.command_usage = defaultdict(int)
        self.user_activity = defaultdict(int)
        self.error_log = deque(maxlen=100)  # Keep last 100 errors
        self.performance_metrics = deque(maxlen=1000)  # Keep last 1000 command executions
        self.daily_stats = defaultdict(lambda: defaultdict(int))
        
        # Load existing analytics
        self.load_analytics()
        
        # Start monitoring tasks
        self.save_analytics_task.start()
        self.performance_monitor.start()
        
        logger.info("Analytics system initialized")
    
    def load_analytics(self):
        """Load analytics data from file"""
        try:
            if os.path.exists("analytics.json"):
                with open("analytics.json", 'r') as f:
                    data = json.load(f)
                    
                    # Load command usage
                    self.command_usage.update(data.get("command_usage", {}))
                    
                    # Load user activity
                    self.user_activity.update(data.get("user_activity", {}))
                    
                    # Load daily stats
                    for date, stats in data.get("daily_stats", {}).items():
                        self.daily_stats[date].update(stats)
                    
                    logger.info("Analytics data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading analytics: {e}")
    
    def save_analytics(self):
        """Save analytics data to file"""
        try:
            data = {
                "command_usage": dict(self.command_usage),
                "user_activity": dict(self.user_activity),
                "daily_stats": dict(self.daily_stats),
                "last_updated": datetime.now().isoformat()
            }
            
            with open("analytics.json", 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")
    
    @tasks.loop(minutes=10)  # Save analytics every 10 minutes
    async def save_analytics_task(self):
        """Periodically save analytics data"""
        self.save_analytics()
    
    @tasks.loop(seconds=30)  # Monitor performance every 30 seconds
    async def performance_monitor(self):
        """Monitor bot performance metrics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            # Bot-specific metrics
            latency = round(self.bot.latency * 1000, 2)
            guild_count = len(self.bot.guilds)
            
            # Store metrics
            metric = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": round(memory.used / 1024 / 1024, 2),
                "latency_ms": latency,
                "guild_count": guild_count
            }
            
            self.performance_metrics.append(metric)
            
        except Exception as e:
            logger.error(f"Error in performance monitor: {e}")
    
    @save_analytics_task.before_loop
    @performance_monitor.before_loop
    async def before_tasks(self):
        """Wait for bot to be ready"""
        await self.bot.wait_until_ready()
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.save_analytics_task.cancel()
        self.performance_monitor.cancel()
        self.save_analytics()
    
    def track_command_usage(self, command_name: str, user_id: int):
        """Track command usage"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Update counters
        self.command_usage[command_name] += 1
        self.user_activity[str(user_id)] += 1
        self.daily_stats[today]["commands"] += 1
        self.daily_stats[today][f"cmd_{command_name}"] += 1
    
    def track_error(self, error: Exception, context: str = ""):
        """Track errors for reporting"""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error)[:200],
            "context": context[:100]
        }
        
        self.error_log.append(error_data)
        
        # Log to file as well
        logger.error(f"Tracked error: {error_data}")
    
    def track_performance(self, command_name: str, execution_time: float):
        """Track command performance"""
        perf_data = {
            "timestamp": datetime.now().isoformat(),
            "command": command_name,
            "execution_time_ms": round(execution_time * 1000, 2)
        }
        
        self.performance_metrics.append(perf_data)
    
    def is_dev(self, user_id: int) -> bool:
        """Check if user is a developer"""
        DEV_IDS = [1147221423815938179]  # Your Discord ID
        return user_id in DEV_IDS
    
    async def get_dev_channel(self):
        """Get the dev channel for error reporting"""
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                name = channel.name.lower()
                if any(keyword in name for keyword in ['dev', 'bot', 'admin', 'website']):
                    return channel
        return None
    
    async def report_error_to_dev(self, error: Exception, context: str = ""):
        """Auto-report errors to dev channel"""
        try:
            channel = await self.get_dev_channel()
            if not channel:
                return
            
            embed = discord.Embed(
                title="🚨 Bot Error Detected",
                description=f"**{type(error).__name__}**",
                color=discord.Color.red()
            )
            
            embed.add_field(
                name="📝 Error Message",
                value=f"```\n{str(error)[:500]}\n```",
                inline=False
            )
            
            if context:
                embed.add_field(
                    name="🔍 Context",
                    value=f"`{context[:100]}`",
                    inline=False
                )
            
            embed.add_field(
                name="⏰ Time",
                value=f"<t:{int(datetime.now().timestamp())}:F>",
                inline=True
            )
            
            embed.set_footer(text="🤖 Automatic error reporting")
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to report error to dev channel: {e}")
    
    @app_commands.command(name="analytics", description="[DEV] View bot usage analytics")
    async def view_analytics(self, interaction: discord.Interaction):
        """Show comprehensive bot analytics"""
        
        if not self.is_dev(interaction.user.id):
            await interaction.response.send_message(
                "❌ This command is only available to developers.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            # Calculate uptime
            uptime = datetime.now() - self.start_time
            
            embed = discord.Embed(
                title="📊 Bot Analytics Dashboard",
                color=discord.Color.blue()
            )
            
            # Basic stats
            total_commands = sum(self.command_usage.values())
            unique_users = len(self.user_activity)
            
            embed.add_field(
                name="📈 Usage Stats",
                value=f"**{total_commands}** total commands\n**{unique_users}** unique users\n**{uptime.days}** days uptime",
                inline=True
            )
            
            # Top commands
            top_commands = sorted(self.command_usage.items(), key=lambda x: x[1], reverse=True)[:5]
            if top_commands:
                cmd_text = "\n".join([f"`{cmd}`: {count}" for cmd, count in top_commands])
                embed.add_field(
                    name="🏆 Top Commands",
                    value=cmd_text,
                    inline=True
                )
            
            # Recent performance
            if self.performance_metrics:
                recent_metrics = list(self.performance_metrics)[-10:]
                avg_latency = sum(m.get('latency_ms', 0) for m in recent_metrics) / len(recent_metrics)
                avg_cpu = sum(m.get('cpu_percent', 0) for m in recent_metrics) / len(recent_metrics)
                avg_memory = sum(m.get('memory_percent', 0) for m in recent_metrics) / len(recent_metrics)
                
                embed.add_field(
                    name="⚡ Performance",
                    value=f"**{avg_latency:.1f}ms** avg latency\n**{avg_cpu:.1f}%** avg CPU\n**{avg_memory:.1f}%** avg memory",
                    inline=True
                )
            
            # Daily activity (last 7 days)
            daily_activity = []
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                commands_today = self.daily_stats.get(date, {}).get("commands", 0)
                daily_activity.append(commands_today)
            
            if any(daily_activity):
                activity_text = " ".join([f"{count}" for count in reversed(daily_activity)])
                embed.add_field(
                    name="📅 Daily Commands (7 days)",
                    value=f"`{activity_text}`",
                    inline=False
                )
            
            # Error summary
            recent_errors = len([e for e in self.error_log if 
                               datetime.fromisoformat(e['timestamp']) > datetime.now() - timedelta(hours=24)])
            
            embed.add_field(
                name="🚨 Error Summary",
                value=f"**{recent_errors}** errors in last 24h\n**{len(self.error_log)}** total tracked errors",
                inline=True
            )
            
            embed.set_footer(text=f"Analytics since {self.start_time.strftime('%B %d, %Y')}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in analytics command: {e}")
            await interaction.followup.send(
                "❌ Error generating analytics report.",
                ephemeral=True
            )
    
    @app_commands.command(name="performance", description="[DEV] View performance metrics")
    async def view_performance(self, interaction: discord.Interaction):
        """Show detailed performance metrics"""
        
        if not self.is_dev(interaction.user.id):
            await interaction.response.send_message(
                "❌ This command is only available to developers.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            if not self.performance_metrics:
                await interaction.followup.send(
                    "📊 No performance data available yet. Check back in a few minutes!",
                    ephemeral=True
                )
                return
            
            # Get recent metrics
            recent_metrics = list(self.performance_metrics)[-20:]
            
            # Calculate averages
            avg_latency = sum(m.get('latency_ms', 0) for m in recent_metrics) / len(recent_metrics)
            avg_cpu = sum(m.get('cpu_percent', 0) for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.get('memory_percent', 0) for m in recent_metrics) / len(recent_metrics)
            avg_memory_mb = sum(m.get('memory_used_mb', 0) for m in recent_metrics) / len(recent_metrics)
            
            # Get current metrics
            current_cpu = psutil.cpu_percent()
            current_memory = psutil.virtual_memory()
            current_latency = round(self.bot.latency * 1000, 2)
            
            embed = discord.Embed(
                title="⚡ Performance Metrics",
                color=discord.Color.green()
            )
            
            # Current metrics
            embed.add_field(
                name="📊 Current Status",
                value=f"**{current_latency}ms** latency\n**{current_cpu}%** CPU usage\n**{current_memory.percent}%** memory usage",
                inline=True
            )
            
            # Average metrics (last 20 readings)
            embed.add_field(
                name="📈 Recent Average",
                value=f"**{avg_latency:.1f}ms** avg latency\n**{avg_cpu:.1f}%** avg CPU\n**{avg_memory:.1f}%** avg memory",
                inline=True
            )
            
            # Memory details
            embed.add_field(
                name="💾 Memory Details",
                value=f"**{avg_memory_mb:.1f}MB** used\n**{current_memory.available / 1024 / 1024:.1f}MB** available\n**{current_memory.total / 1024 / 1024:.1f}MB** total",
                inline=True
            )
            
            # Performance status
            status_emoji = "🟢"
            status_text = "Excellent"
            
            if avg_latency > 500 or avg_cpu > 80 or avg_memory > 80:
                status_emoji = "🔴"
                status_text = "Poor"
            elif avg_latency > 200 or avg_cpu > 50 or avg_memory > 60:
                status_emoji = "🟡"
                status_text = "Fair"
            
            embed.add_field(
                name="🎯 Overall Status",
                value=f"{status_emoji} **{status_text}**",
                inline=True
            )
            
            # Uptime
            uptime = datetime.now() - self.start_time
            embed.add_field(
                name="⏱️ Uptime",
                value=f"**{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m**",
                inline=True
            )
            
            # Guild count
            embed.add_field(
                name="🌐 Servers",
                value=f"**{len(self.bot.guilds)}** connected",
                inline=True
            )
            
            embed.set_footer(text=f"Based on last {len(recent_metrics)} readings")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in performance command: {e}")
            await interaction.followup.send(
                "❌ Error generating performance report.",
                ephemeral=True
            )
    
    @app_commands.command(name="error_log", description="[DEV] View recent errors")
    async def view_error_log(self, interaction: discord.Interaction):
        """Show recent error log"""
        
        if not self.is_dev(interaction.user.id):
            await interaction.response.send_message(
                "❌ This command is only available to developers.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            if not self.error_log:
                embed = discord.Embed(
                    title="✅ No Errors Logged",
                    description="No errors have been tracked recently. Great job!",
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="🚨 Recent Error Log",
                color=discord.Color.red()
            )
            
            # Show last 5 errors
            recent_errors = list(self.error_log)[-5:]
            
            for i, error in enumerate(reversed(recent_errors), 1):
                timestamp = datetime.fromisoformat(error['timestamp'])
                time_str = f"<t:{int(timestamp.timestamp())}:R>"
                
                embed.add_field(
                    name=f"#{len(self.error_log) - i + 1} {error['error_type']}",
                    value=f"**Message:** `{error['error_message'][:50]}...`\n**Context:** `{error.get('context', 'N/A')[:30]}`\n**Time:** {time_str}",
                    inline=False
                )
            
            # Error summary
            error_types = {}
            for error in self.error_log:
                error_type = error['error_type']
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            if error_types:
                top_errors = sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:3]
                summary_text = "\n".join([f"`{error_type}`: {count}" for error_type, count in top_errors])
                
                embed.add_field(
                    name="📊 Error Summary",
                    value=summary_text,
                    inline=True
                )
            
            embed.set_footer(text=f"Showing last 5 of {len(self.error_log)} total errors")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in error_log command: {e}")
            await interaction.followup.send(
                "❌ Error generating error log (how ironic!).",
                ephemeral=True
            )


# Command tracking decorator
def track_command(func):
    """Decorator to track command usage and performance"""
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
        start_time = time.time()
        command_name = func.__name__
        
        try:
            # Track command usage
            analytics_cog = self.bot.get_cog('Analytics')
            if analytics_cog:
                analytics_cog.track_command_usage(command_name, interaction.user.id)
            
            # Execute command
            result = await func(self, interaction, *args, **kwargs)
            
            # Track performance
            execution_time = time.time() - start_time
            if analytics_cog:
                analytics_cog.track_performance(command_name, execution_time)
            
            return result
            
        except Exception as e:
            # Track error
            if analytics_cog:
                analytics_cog.track_error(e, f"Command: {command_name}")
                await analytics_cog.report_error_to_dev(e, f"Command: {command_name}")
            
            # Re-raise the error
            raise e
    
    return wrapper


async def setup(bot):
    """Setup function to add the cog to the bot"""
    await bot.add_cog(Analytics(bot))
    logger.info("Analytics cog loaded")