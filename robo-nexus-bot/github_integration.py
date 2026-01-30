"""
GitHub Integration for Robo Nexus Birthday Bot
Handles commit notifications, issue creation, and auto-deploy tracking
"""
import discord
from discord import app_commands
from discord.ext import commands, tasks
import logging
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class GitHubIntegration(commands.Cog):
    """GitHub integration for commit tracking and issue management"""
    
    def __init__(self, bot):
        self.bot = bot
        self.github_token = os.getenv('GITHUB_TOKEN')  # Optional GitHub token
        self.repo_owner = "AtharvM02222"  # Your GitHub username
        
        # Multiple repositories to monitor
        self.repositories = [
            "robo-nexus-bot",           # Bot code repository
            "Robo-Nexus-Website-Dev"    # Website repository
        ]
        
        self.last_commit_check = datetime.now()
        
        # Start commit monitoring
        if self.github_token:
            self.check_commits.start()
        
        logger.info(f"GitHub integration initialized for {len(self.repositories)} repositories")
    
    def is_dev(self, user_id: int) -> bool:
        """Check if user is a developer"""
        DEV_IDS = [1147221423815938179]  # Your Discord ID
        return user_id in DEV_IDS
    
    async def get_dev_channel(self):
        """Get the dev channel for notifications"""
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                name = channel.name.lower()
                if any(keyword in name for keyword in ['dev', 'bot', 'admin', 'website']):
                    return channel
        return None
    
    @tasks.loop(minutes=5)  # Check for new commits every 5 minutes
    async def check_commits(self):
        """Check for new commits across all repositories and send notifications"""
        try:
            if not self.github_token:
                return
            
            channel = await self.get_dev_channel()
            if not channel:
                return
            
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            params = {
                'since': self.last_commit_check.isoformat(),
                'per_page': 5
            }
            
            # Check each repository
            for repo_name in self.repositories:
                try:
                    url = f"https://api.github.com/repos/{self.repo_owner}/{repo_name}/commits"
                    response = requests.get(url, headers=headers, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        commits = response.json()
                        
                        if commits:
                            for commit in reversed(commits):  # Show oldest first
                                await self.send_commit_notification(channel, commit, repo_name)
                    
                    elif response.status_code == 404:
                        logger.warning(f"Repository {repo_name} not found or no access")
                    
                except Exception as e:
                    logger.error(f"Error checking commits for {repo_name}: {e}")
            
            self.last_commit_check = datetime.now()
            
        except Exception as e:
            logger.error(f"Error in commit checking task: {e}")
    
    async def send_commit_notification(self, channel, commit_data, repo_name):
        """Send commit notification to dev channel"""
        try:
            commit = commit_data['commit']
            author = commit_data['author']
            
            # Determine emoji based on repository
            repo_emoji = "🤖" if "bot" in repo_name.lower() else "🌐"
            
            # Create embed
            embed = discord.Embed(
                title=f"{repo_emoji} New Commit to {repo_name}",
                description=f"**{commit['message'][:100]}{'...' if len(commit['message']) > 100 else ''}**",
                color=discord.Color.green() if "bot" in repo_name.lower() else discord.Color.blue(),
                url=commit_data['html_url']
            )
            
            # Author info
            if author:
                embed.set_author(
                    name=f"{author['login']} committed",
                    icon_url=author['avatar_url'],
                    url=author['html_url']
                )
            
            # Commit details
            embed.add_field(
                name="📊 Changes",
                value=f"**+{commit_data.get('stats', {}).get('additions', '?')}** / **-{commit_data.get('stats', {}).get('deletions', '?')}** lines",
                inline=True
            )
            
            # Commit hash
            embed.add_field(
                name="🔗 Commit",
                value=f"`{commit_data['sha'][:7]}`",
                inline=True
            )
            
            # Timestamp
            commit_time = datetime.fromisoformat(commit['author']['date'].replace('Z', '+00:00'))
            embed.add_field(
                name="⏰ Time",
                value=f"<t:{int(commit_time.timestamp())}:R>",
                inline=True
            )
            
            # Repository-specific actions
            if "bot" in repo_name.lower():
                embed.add_field(
                    name="🚀 Auto-Deploy",
                    value="Use `/pull` to update the bot with these changes!",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🌐 Website Update",
                    value="Website changes detected - check your hosting platform!",
                    inline=False
                )
            
            embed.set_footer(text=f"Repository: {self.repo_owner}/{repo_name}")
            
            await channel.send(embed=embed)
            logger.info(f"Sent commit notification for {repo_name}:{commit_data['sha'][:7]}")
            
        except Exception as e:
            logger.error(f"Error sending commit notification: {e}")
    
    @check_commits.before_loop
    async def before_check_commits(self):
        """Wait for bot to be ready"""
        await self.bot.wait_until_ready()
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        if hasattr(self, 'check_commits'):
            self.check_commits.cancel()
    
    @app_commands.command(name="repo_list", description="[DEV] List monitored repositories")
    async def repo_list(self, interaction: discord.Interaction):
        """List all monitored repositories"""
        
        if not self.is_dev(interaction.user.id):
            await interaction.response.send_message(
                "❌ This command is only available to developers.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="📋 Monitored Repositories",
            color=discord.Color.blue()
        )
        
        if not self.repositories:
            embed.description = "No repositories are being monitored."
        else:
            repo_list = []
            for i, repo in enumerate(self.repositories, 1):
                emoji = "🤖" if "bot" in repo.lower() else "🌐"
                repo_list.append(f"{emoji} **{repo}**")
            
            embed.description = "\n".join(repo_list)
        
        embed.add_field(
            name="🔧 Configuration",
            value=f"**Owner:** {self.repo_owner}\n**Token:** {'✅ Configured' if self.github_token else '❌ Not set'}",
            inline=False
        )
        
        if self.github_token:
            embed.add_field(
                name="📡 Monitoring",
                value="✅ **Active** - Checking for commits every 5 minutes",
                inline=False
            )
        else:
            embed.add_field(
                name="📡 Monitoring",
                value="❌ **Inactive** - Add GITHUB_TOKEN to Replit Secrets to enable",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="create_issue", description="[DEV] Create a GitHub issue")
    async def create_issue(
        self, 
        interaction: discord.Interaction, 
        repository: str,
        title: str, 
        description: str,
        priority: str = "normal"
    ):
        """Create a GitHub issue from Discord"""
        
        if not self.is_dev(interaction.user.id):
            await interaction.response.send_message(
                "❌ This command is only available to developers.",
                ephemeral=True
            )
            return
        
        if not self.github_token:
            await interaction.response.send_message(
                "❌ GitHub token not configured. Set GITHUB_TOKEN environment variable.",
                ephemeral=True
            )
            return
        
        # Validate repository
        if repository not in self.repositories:
            available_repos = ", ".join(self.repositories)
            await interaction.response.send_message(
                f"❌ Repository '{repository}' not monitored. Available: {available_repos}",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            # Prepare issue data
            labels = []
            if priority == "high":
                labels.append("priority: high")
            elif priority == "low":
                labels.append("priority: low")
            
            labels.append("created-from-discord")
            
            issue_body = f"{description}\n\n---\n*Created from Discord by {interaction.user.mention}*"
            
            # Create issue via GitHub API
            url = f"https://api.github.com/repos/{self.repo_owner}/{repository}/issues"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            data = {
                'title': title,
                'body': issue_body,
                'labels': labels
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 201:
                issue = response.json()
                
                repo_emoji = "🤖" if "bot" in repository.lower() else "🌐"
                
                embed = discord.Embed(
                    title=f"✅ GitHub Issue Created in {repository}",
                    description=f"**{title}**",
                    color=discord.Color.green(),
                    url=issue['html_url']
                )
                
                embed.add_field(
                    name="📋 Issue Details",
                    value=f"{repo_emoji} **Repository:** {repository}\n🔢 **Number:** #{issue['number']}\n🏷️ **Priority:** {priority.title()}",
                    inline=False
                )
                
                embed.add_field(
                    name="🔗 Quick Actions",
                    value=f"[View Issue]({issue['html_url']}) • [Repository](https://github.com/{self.repo_owner}/{repository})",
                    inline=False
                )
                
                embed.set_footer(text=f"Created by {interaction.user.display_name}")
                
                await interaction.followup.send(embed=embed)
                logger.info(f"Created GitHub issue #{issue['number']} in {repository} from Discord")
                
            else:
                await interaction.followup.send(
                    f"❌ Failed to create issue. GitHub API returned: {response.status_code}",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Error creating GitHub issue: {e}")
            await interaction.followup.send(
                f"❌ Error creating issue: {str(e)[:100]}",
                ephemeral=True
            )
    
    @create_issue.autocomplete('repository')
    async def repository_autocomplete(self, interaction: discord.Interaction, current: str):
        """Autocomplete for repository parameter"""
        return [
            app_commands.Choice(name=repo, value=repo)
            for repo in self.repositories
            if current.lower() in repo.lower()
        ][:25]
    
    @app_commands.command(name="recent_commits", description="Show recent commits")
    @app_commands.describe(repository="Repository to check", count="Number of commits to show")
    async def recent_commits(self, interaction: discord.Interaction, repository: str = None, count: int = 5):
        """Show recent commits from the repository"""
        
        await interaction.response.defer()
        
        # Default to first repository if not specified
        repo_name = repository or self.repositories[0]
        
        try:
            # Get recent commits (public API, no token needed)
            url = f"https://api.github.com/repos/{self.repo_owner}/{repo_name}/commits"
            params = {'per_page': min(count, 10)}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                commits = response.json()
                
                embed = discord.Embed(
                    title=f"📝 Recent Commits - {repo_name} ({len(commits)})",
                    color=discord.Color.blue()
                )
                
                for i, commit in enumerate(commits[:5], 1):
                    commit_msg = commit['commit']['message']
                    author = commit['commit']['author']['name']
                    sha = commit['sha'][:7]
                    
                    # Format commit time
                    commit_time = datetime.fromisoformat(
                        commit['commit']['author']['date'].replace('Z', '+00:00')
                    )
                    
                    embed.add_field(
                        name=f"#{i} `{sha}` by {author}",
                        value=f"**{commit_msg[:60]}{'...' if len(commit_msg) > 60 else ''}**\n<t:{int(commit_time.timestamp())}:R>",
                        inline=False
                    )
                
                embed.add_field(
                    name="🚀 Deploy Latest",
                    value="Use `/pull` to update the bot with latest changes!",
                    inline=False
                )
                
                embed.set_footer(text=f"Repository: {self.repo_owner}/{repo_name}")
                
                await interaction.followup.send(embed=embed)
                
            else:
                await interaction.followup.send(
                    "❌ Failed to fetch commits. Repository might be private or not found.",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Error fetching recent commits: {e}")
            await interaction.followup.send(
                f"❌ Error fetching commits: {str(e)[:100]}",
                ephemeral=True
            )
    
    @recent_commits.autocomplete('repository')
    async def recent_commits_repo_autocomplete(self, interaction: discord.Interaction, current: str):
        """Autocomplete for repository parameter"""
        return [
            app_commands.Choice(name=repo, value=repo)
            for repo in self.repositories
            if current.lower() in repo.lower()
        ][:25]
    
    @app_commands.command(name="repo_stats", description="Show repository statistics")
    @app_commands.describe(repository="Repository to check stats for")
    async def repo_stats(self, interaction: discord.Interaction, repository: str = None):
        """Show GitHub repository statistics"""
        
        await interaction.response.defer()
        
        # Default to first repository if not specified
        repo_name = repository or self.repositories[0]
        
        try:
            # Get repo info (public API)
            url = f"https://api.github.com/repos/{self.repo_owner}/{repo_name}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                repo = response.json()
                
                embed = discord.Embed(
                    title=f"📊 Repository Statistics",
                    description=f"**{repo['full_name']}**",
                    color=discord.Color.purple(),
                    url=repo['html_url']
                )
                
                # Basic stats
                embed.add_field(
                    name="⭐ Stars",
                    value=f"{repo['stargazers_count']}",
                    inline=True
                )
                
                embed.add_field(
                    name="🍴 Forks",
                    value=f"{repo['forks_count']}",
                    inline=True
                )
                
                embed.add_field(
                    name="👀 Watchers",
                    value=f"{repo['watchers_count']}",
                    inline=True
                )
                
                embed.add_field(
                    name="📝 Language",
                    value=repo['language'] or "Mixed",
                    inline=True
                )
                
                embed.add_field(
                    name="📦 Size",
                    value=f"{repo['size']} KB",
                    inline=True
                )
                
                # Last update
                updated = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
                embed.add_field(
                    name="🔄 Last Updated",
                    value=f"<t:{int(updated.timestamp())}:R>",
                    inline=True
                )
                
                # Description
                if repo['description']:
                    embed.add_field(
                        name="📋 Description",
                        value=repo['description'][:100],
                        inline=False
                    )
                
                embed.set_footer(text=f"Created: {repo['created_at'][:10]}")
                
                await interaction.followup.send(embed=embed)
                
            else:
                await interaction.followup.send(
                    "❌ Failed to fetch repository stats.",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Error fetching repo stats: {e}")
            await interaction.followup.send(
                f"❌ Error fetching stats: {str(e)[:100]}",
                ephemeral=True
            )
    
    @repo_stats.autocomplete('repository')
    async def repo_stats_autocomplete(self, interaction: discord.Interaction, current: str):
        """Autocomplete for repository parameter"""
        return [
            app_commands.Choice(name=repo, value=repo)
            for repo in self.repositories
            if current.lower() in repo.lower()
        ][:25]


async def setup(bot):
    """Setup function to add the cog to the bot"""
    await bot.add_cog(GitHubIntegration(bot))
    logger.info("GitHub integration cog loaded")