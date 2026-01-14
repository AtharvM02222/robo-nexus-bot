"""
Welcome System for Robo Nexus Birthday Bot
Handles new member onboarding with name, class, email, and social links collection
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
import re
import asyncio
from typing import Optional, Dict
import json
import os

logger = logging.getLogger(__name__)

WELCOME_DATA_FILE = "welcome_data.json"
PROFILES_DATA_FILE = "user_profiles.json"

class WelcomeSystem(commands.Cog):
    """Welcome system for new member onboarding with profile collection"""
    
    def __init__(self, bot):
        self.bot = bot
        self.pending_users = {}  # Store users waiting for verification
        self.user_profiles = {}  # Store complete user profiles
        self.welcome_channel_id = None
        self.self_roles_channel_id = None
        
        # Class roles mapping
        self.class_roles = {
            "6": "6", "7": "7", "8": "8", "9": "9", 
            "10": "10", "11": "11", "12": "12"
        }
        
        # Verification stages
        self.STAGE_NAME_CLASS = "name_class"
        self.STAGE_EMAIL = "email"
        self.STAGE_LINKS = "links"
        self.STAGE_COMPLETE = "complete"
        
        # Load welcome configuration
        self.load_welcome_data()
        
        logger.info("Welcome system initialized")
    
    def load_welcome_data(self):
        """Load welcome system configuration"""
        try:
            if os.path.exists(WELCOME_DATA_FILE):
                with open(WELCOME_DATA_FILE, 'r') as f:
                    data = json.load(f)
                    self.welcome_channel_id = data.get("welcome_channel_id")
                    self.self_roles_channel_id = data.get("self_roles_channel_id")
                    logger.info("Welcome data loaded successfully")
            
            # Load user profiles
            if os.path.exists(PROFILES_DATA_FILE):
                with open(PROFILES_DATA_FILE, 'r') as f:
                    self.user_profiles = json.load(f)
                    logger.info(f"Loaded {len(self.user_profiles)} user profiles")
                    
        except Exception as e:
            logger.error(f"Error loading welcome data: {e}")
    
    def save_welcome_data(self):
        """Save welcome system configuration"""
        try:
            data = {
                "welcome_channel_id": self.welcome_channel_id,
                "self_roles_channel_id": self.self_roles_channel_id
            }
            with open(WELCOME_DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2)
                
            # Save user profiles
            with open(PROFILES_DATA_FILE, 'w') as f:
                json.dump(self.user_profiles, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving welcome data: {e}")
    
    def validate_email(self, email: str) -> bool:
        """Validate Gmail address"""
        if not email:
            return False
        
        email = email.lower().strip()
        
        # Check if it's a Gmail address
        if not email.endswith('@gmail.com'):
            return False
        
        # Basic email format validation
        pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        return bool(re.match(pattern, email))
    
    def validate_social_links(self, links_text: str) -> Dict[str, str]:
        """
        Extract and validate social media links
        Returns dict with platform names as keys and URLs as values
        """
        links = {}
        
        if not links_text or links_text.lower().strip() in ['none', 'no', 'skip', 'n/a', 'na']:
            return links
        
        # Split by lines or commas
        lines = re.split(r'[,\n]', links_text)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove common prefixes like "GitHub:", "LinkedIn:", etc.
            line = re.sub(r'^(github|linkedin|youtube|spotify):\s*', '', line, flags=re.IGNORECASE)
            
            # GitHub
            if 'github.com' in line.lower():
                links['github'] = line if line.startswith('http') else f"https://{line}"
            
            # LinkedIn
            elif 'linkedin.com' in line.lower():
                links['linkedin'] = line if line.startswith('http') else f"https://{line}"
            
            # YouTube
            elif 'youtube.com' in line.lower() or 'youtu.be' in line.lower():
                links['youtube'] = line if line.startswith('http') else f"https://{line}"
            
            # Spotify
            elif 'spotify.com' in line.lower() or 'open.spotify.com' in line.lower():
                links['spotify'] = line if line.startswith('http') else f"https://{line}"
            
            # Generic URL detection
            elif 'http' in line.lower():
                # Try to identify platform from URL
                if 'github' in line.lower():
                    links['github'] = line
                elif 'linkedin' in line.lower():
                    links['linkedin'] = line
                elif 'youtube' in line.lower() or 'youtu.be' in line.lower():
                    links['youtube'] = line
                elif 'spotify' in line.lower():
                    links['spotify'] = line
        
        return links
    
    def extract_class_from_text(self, text: str) -> Optional[str]:
        """
        Extract class number from user input
        Supports: "6", "class 6", "grade 6", "6th", "sixth", etc.
        """
        if not text:
            return None
        
        text = text.lower().strip()
        
        # Direct number match
        if text in self.class_roles:
            return text
        
        # Number with ordinal (6th, 7th, etc.)
        ordinal_match = re.search(r'(\d+)(?:st|nd|rd|th)', text)
        if ordinal_match:
            class_num = ordinal_match.group(1)
            if class_num in self.class_roles:
                return class_num
        
        # Word forms (sixth, seventh, etc.)
        word_to_number = {
            "sixth": "6", "six": "6",
            "seventh": "7", "seven": "7", 
            "eighth": "8", "eight": "8",
            "ninth": "9", "nine": "9",
            "tenth": "10", "ten": "10",
            "eleventh": "11", "eleven": "11",
            "twelfth": "12", "twelve": "12"
        }
        
        for word, number in word_to_number.items():
            if word in text:
                return number
        
        # Extract any number from text (class 6, grade 7, etc.)
        number_match = re.search(r'\b(\d+)\b', text)
        if number_match:
            class_num = number_match.group(1)
            if class_num in self.class_roles:
                return class_num
        
        return None
    
    async def get_or_create_role(self, guild: discord.Guild, role_name: str) -> Optional[discord.Role]:
        """Get existing role or create new one"""
        try:
            # Try to find existing role
            role = discord.utils.get(guild.roles, name=role_name)
            
            if not role:
                # Create new role
                role = await guild.create_role(
                    name=role_name,
                    color=discord.Color.blue(),
                    mentionable=True,
                    reason="Auto-created class role by Robo Nexus Bot"
                )
                logger.info(f"Created new role: {role_name}")
            
            return role
            
        except Exception as e:
            logger.error(f"Error getting/creating role {role_name}: {e}")
            return None
    
    async def send_welcome_dm(self, member: discord.Member):
        """Send welcome DM to new member - Stage 1: Name and Class"""
        try:
            embed = discord.Embed(
                title="🎉 Welcome to Robo Nexus!",
                description=f"Hi {member.mention}! Welcome to our robotics community!",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📝 Step 1: Basic Info",
                value="To get started, please provide:\n\n**1. Your Name**\n**2. Your Class/Grade** (6, 7, 8, 9, 10, 11, or 12)",
                inline=False
            )
            
            embed.add_field(
                name="💡 Example Response",
                value="```\nJohn Smith, Class 10\n```\nor simply:\n```\nJohn Smith 10th grade\n```",
                inline=False
            )
            
            embed.add_field(
                name="🔄 What's Next?",
                value="After this, I'll ask for:\n• Your Gmail address\n• Social media links (optional)",
                inline=False
            )
            
            embed.set_footer(text="🔒 Currently you only have access to #self-roles channel")
            embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else None)
            
            await member.send(embed=embed)
            logger.info(f"Sent welcome DM to {member.display_name}")
            
        except discord.Forbidden:
            logger.warning(f"Could not send DM to {member.display_name} - DMs disabled")
            # Try to send in self-roles channel instead
            await self.send_welcome_in_channel(member)
    
    async def send_welcome_in_channel(self, member: discord.Member):
        """Send welcome message in self-roles channel"""
        try:
            if not self.self_roles_channel_id:
                logger.warning("Self-roles channel not configured, cannot send welcome message")
                return
            
            channel = member.guild.get_channel(self.self_roles_channel_id)
            if not channel:
                logger.error(f"Self-roles channel {self.self_roles_channel_id} not found")
                return
            
            embed = discord.Embed(
                title="🎉 Welcome to Robo Nexus!",
                description=f"Hi {member.mention}! Welcome to our robotics community!",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📝 Step 1: Basic Info",
                value="To get started, please reply in this channel with:\n\n**1. Your Name**\n**2. Your Class/Grade** (6, 7, 8, 9, 10, 11, or 12)",
                inline=False
            )
            
            embed.add_field(
                name="💡 Example Response",
                value="```\nJohn Smith, Class 10\n```\nor simply:\n```\nJohn Smith 10th grade\n```",
                inline=False
            )
            
            embed.add_field(
                name="🔄 What's Next?",
                value="After this, I'll ask for:\n• Your Gmail address\n• Social media links (optional)",
                inline=False
            )
            
            embed.set_footer(text="🔒 Reply in this channel to complete verification!")
            embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else None)
            
            await channel.send(embed=embed)
            logger.info(f"Sent welcome message in #self-roles for {member.display_name}")
            
        except Exception as e:
            logger.error(f"Error sending welcome in channel: {e}")
    
    async def send_email_request(self, message: discord.Message, name: str, class_num: str):
        """Send request for Gmail address - Stage 2"""
        try:
            embed = discord.Embed(
                title="📧 Step 2: Gmail Address",
                description=f"Great! Welcome **{name}** from Class {class_num}!",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📮 Please provide your Gmail address",
                value="We need your Gmail for:\n• Team communications\n• Project updates\n• Important announcements",
                inline=False
            )
            
            embed.add_field(
                name="💡 Example",
                value="`john.smith@gmail.com`",
                inline=False
            )
            
            embed.add_field(
                name="🔒 Privacy",
                value="Your email will only be used for Robo Nexus activities and won't be shared externally.",
                inline=False
            )
            
            await message.reply(embed=embed)
            
        except Exception as e:
            logger.error(f"Error sending email request: {e}")
    
    async def send_links_request(self, message: discord.Message, email: str):
        """Send request for social media links - Stage 3"""
        try:
            embed = discord.Embed(
                title="🔗 Step 3: Social Media Links (Optional)",
                description="Almost done! Please share your social media profiles:",
                color=discord.Color.purple()
            )
            
            embed.add_field(
                name="🌐 Supported Platforms",
                value="• **GitHub** - Your coding projects\n• **LinkedIn** - Professional profile\n• **YouTube** - Your channel\n• **Spotify** - Music profile",
                inline=False
            )
            
            embed.add_field(
                name="💡 Example Response",
                value="```\nGitHub: github.com/johnsmith\nLinkedIn: linkedin.com/in/johnsmith\nYouTube: youtube.com/@johnsmith\n```\nOr simply: `None` if you don't want to share",
                inline=False
            )
            
            embed.add_field(
                name="⚡ Quick Option",
                value="Type `skip` or `none` if you don't have any links to share right now.",
                inline=False
            )
            
            await message.reply(embed=embed)
            
        except Exception as e:
            logger.error(f"Error sending links request: {e}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Handle new member joining"""
        try:
            logger.info(f"New member joined: {member.display_name} ({member.id})")
            
            # Send welcome message in self-roles channel
            await self.send_welcome_in_channel(member)
            
            # Store user as pending
            self.pending_users[member.id] = {
                "member": member,
                "stage": self.STAGE_NAME_CLASS,
                "joined_at": member.joined_at.isoformat() if member.joined_at else None,
                "profile": {}
            }
            
            # Send notification to welcome channel if configured
            if self.welcome_channel_id:
                channel = member.guild.get_channel(self.welcome_channel_id)
                if channel:
                    embed = discord.Embed(
                        title="👋 New Member Joined",
                        description=f"{member.mention} joined the server!",
                        color=discord.Color.blue()
                    )
                    embed.add_field(
                        name="📊 Member Count", 
                        value=f"{member.guild.member_count} members",
                        inline=True
                    )
                    embed.add_field(
                        name="🔄 Status",
                        value="Starting verification process...",
                        inline=True
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_footer(text=f"User ID: {member.id}")
                    
                    await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error handling member join: {e}")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle messages for multi-stage verification"""
        try:
            # Ignore bot messages
            if message.author.bot:
                return
            
            # Check if user is pending verification
            if message.author.id not in self.pending_users:
                return
            
            # Check if message is in self-roles channel or DM
            is_self_roles_channel = (
                self.self_roles_channel_id and 
                message.channel.id == self.self_roles_channel_id
            )
            is_dm = isinstance(message.channel, discord.DMChannel)
            
            if not (is_self_roles_channel or is_dm):
                return
            
            # Process based on current stage
            await self.process_verification_stage(message)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def process_verification_stage(self, message: discord.Message):
        """Process user's response based on their current verification stage"""
        try:
            user_id = message.author.id
            user_data = self.pending_users[user_id]
            current_stage = user_data["stage"]
            user_input = message.content.strip()
            
            if current_stage == self.STAGE_NAME_CLASS:
                await self.process_name_class_stage(message, user_input)
                
            elif current_stage == self.STAGE_EMAIL:
                await self.process_email_stage(message, user_input)
                
            elif current_stage == self.STAGE_LINKS:
                await self.process_links_stage(message, user_input)
            
        except Exception as e:
            logger.error(f"Error processing verification stage: {e}")
    
    async def process_name_class_stage(self, message: discord.Message, user_input: str):
        """Process Stage 1: Name and Class"""
        try:
            member = message.author
            
            # Extract class from the message
            class_number = self.extract_class_from_text(user_input)
            
            if not class_number:
                # Ask for clarification
                embed = discord.Embed(
                    title="❓ Class Not Found",
                    description="I couldn't find your class in your message.",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="📚 Valid Classes",
                    value="6, 7, 8, 9, 10, 11, 12",
                    inline=False
                )
                embed.add_field(
                    name="💡 Try Again",
                    value="Please include your class like:\n• `John Smith, Class 10`\n• `Sarah, Grade 8`\n• `Mike 12th`",
                    inline=False
                )
                
                await message.reply(embed=embed, delete_after=60)
                return
            
            # Extract name (remove class-related words)
            name_text = user_input
            # Remove class-related patterns
            patterns_to_remove = [
                rf'\b(?:class|grade|std)\s*{class_number}\b',
                rf'\b{class_number}(?:st|nd|rd|th)?\b',
                r'\bclass\b', r'\bgrade\b', r'\bstd\b'
            ]
            
            for pattern in patterns_to_remove:
                name_text = re.sub(pattern, '', name_text, flags=re.IGNORECASE)
            
            # Clean up the name
            name = re.sub(r'[,\-\s]+', ' ', name_text).strip()
            
            if len(name) < 2:
                embed = discord.Embed(
                    title="❓ Name Too Short",
                    description="Please provide your full name along with your class.",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="💡 Example",
                    value="`John Smith, Class 10`",
                    inline=False
                )
                await message.reply(embed=embed, delete_after=60)
                return
            
            # Store name and class, move to email stage
            self.pending_users[member.id]["profile"]["name"] = name
            self.pending_users[member.id]["profile"]["class"] = class_number
            self.pending_users[member.id]["stage"] = self.STAGE_EMAIL
            
            # Request email
            await self.send_email_request(message, name, class_number)
            
        except Exception as e:
            logger.error(f"Error processing name/class stage: {e}")
    
    async def process_email_stage(self, message: discord.Message, user_input: str):
        """Process Stage 2: Email"""
        try:
            member = message.author
            email = user_input.strip()
            
            if not self.validate_email(email):
                embed = discord.Embed(
                    title="❌ Invalid Gmail Address",
                    description="Please provide a valid Gmail address.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="📧 Requirements",
                    value="• Must be a Gmail address (@gmail.com)\n• Example: `john.smith@gmail.com`",
                    inline=False
                )
                embed.add_field(
                    name="💡 Why Gmail?",
                    value="We use Gmail for team communications and Google Workspace integration.",
                    inline=False
                )
                
                await message.reply(embed=embed, delete_after=60)
                return
            
            # Store email, move to links stage
            self.pending_users[member.id]["profile"]["email"] = email
            self.pending_users[member.id]["stage"] = self.STAGE_LINKS
            
            # Request social links
            await self.send_links_request(message, email)
            
        except Exception as e:
            logger.error(f"Error processing email stage: {e}")
    
    async def process_links_stage(self, message: discord.Message, user_input: str):
        """Process Stage 3: Social Links"""
        try:
            member = message.author
            
            # Extract social links
            social_links = self.validate_social_links(user_input)
            
            # Store links and complete verification
            self.pending_users[member.id]["profile"]["social_links"] = social_links
            self.pending_users[member.id]["stage"] = self.STAGE_COMPLETE
            
            # Complete the verification process
            await self.complete_verification(message)
            
        except Exception as e:
            logger.error(f"Error processing links stage: {e}")
    
    async def complete_verification(self, message: discord.Message):
        """Complete the verification process and assign role"""
        try:
            member = message.author
            user_data = self.pending_users[member.id]
            profile = user_data["profile"]
            
            name = profile["name"]
            class_number = profile["class"]
            email = profile["email"]
            social_links = profile.get("social_links", {})
            
            # Assign the class role
            success = await self.assign_class_role(member, class_number, name)
            
            if success:
                # Save complete profile
                self.user_profiles[str(member.id)] = {
                    "name": name,
                    "class": class_number,
                    "email": email,
                    "social_links": social_links,
                    "discord_id": member.id,
                    "discord_username": str(member),
                    "joined_at": user_data.get("joined_at"),
                    "verified_at": discord.utils.utcnow().isoformat()
                }
                
                # Remove from pending users
                del self.pending_users[member.id]
                
                # Save data
                self.save_welcome_data()
                
                # Send completion message
                embed = discord.Embed(
                    title="✅ Welcome Complete!",
                    description=f"Welcome to Robo Nexus, **{name}**!",
                    color=discord.Color.green()
                )
                
                embed.add_field(
                    name="🎓 Profile Summary",
                    value=f"**Name:** {name}\n**Class:** {class_number}\n**Email:** {email}",
                    inline=False
                )
                
                if social_links:
                    links_text = []
                    for platform, url in social_links.items():
                        links_text.append(f"**{platform.title()}:** {url}")
                    
                    embed.add_field(
                        name="🔗 Social Links",
                        value="\n".join(links_text),
                        inline=False
                    )
                
                embed.add_field(
                    name="🚀 What's Next?",
                    value="• Explore all server channels\n• Join your classmates\n• Participate in robotics discussions!\n• Register your birthday with `/register_birthday`",
                    inline=False
                )
                
                await message.reply(embed=embed)
                
                # Log successful verification
                logger.info(f"Successfully verified {member.display_name}: {name}, Class {class_number}, {email}")
                
                # Notify in welcome channel
                if self.welcome_channel_id:
                    channel = member.guild.get_channel(self.welcome_channel_id)
                    if channel:
                        welcome_embed = discord.Embed(
                            title="✅ Member Verified",
                            description=f"**{name}** (Class {class_number}) is now fully set up!",
                            color=discord.Color.green()
                        )
                        welcome_embed.add_field(
                            name="📧 Contact",
                            value=email,
                            inline=True
                        )
                        if social_links:
                            welcome_embed.add_field(
                                name="🔗 Links",
                                value=f"{len(social_links)} social links provided",
                                inline=True
                            )
                        welcome_embed.set_thumbnail(url=member.display_avatar.url)
                        await channel.send(embed=welcome_embed)
            
        except Exception as e:
            logger.error(f"Error completing verification: {e}")
            await message.reply("❌ An error occurred while completing verification. Please contact an admin.")
    
    async def assign_class_role(self, member: discord.Member, class_number: str, name: str) -> bool:
        """Assign class role to member"""
        try:
            guild = member.guild
            
            # Get or create the class role
            role_name = class_number
            role = await self.get_or_create_role(guild, role_name)
            
            if not role:
                logger.error(f"Could not create role for class {class_number}")
                return False
            
            # Assign the role
            await member.add_roles(role, reason=f"Auto-assigned class role: {name}")
            
            # Update nickname to include name if different
            try:
                if member.display_name != name and len(name) <= 32:
                    await member.edit(nick=name, reason="Set name from welcome process")
            except discord.Forbidden:
                logger.warning(f"Could not set nickname for {member.display_name}")
            
            logger.info(f"Assigned role '{role_name}' to {member.display_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error assigning role: {e}")
            return False
    
    # ==================== ADMIN COMMANDS ====================
    
    @app_commands.command(name="set_welcome_channel", description="[ADMIN] Set the welcome notifications channel")
    @app_commands.describe(channel="Channel for welcome notifications")
    @app_commands.default_permissions(administrator=True)
    async def set_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set welcome notifications channel"""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
            return
        
        self.welcome_channel_id = channel.id
        self.save_welcome_data()
        
        embed = discord.Embed(
            title="✅ Welcome Channel Set",
            description=f"Welcome notifications will be sent to {channel.mention}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"Welcome channel set to {channel.name}")
    
    @app_commands.command(name="set_self_roles_channel", description="[ADMIN] Set the self-roles channel")
    @app_commands.describe(channel="Channel where users can only access initially")
    @app_commands.default_permissions(administrator=True)
    async def set_self_roles_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set self-roles channel"""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
            return
        
        self.self_roles_channel_id = channel.id
        self.save_welcome_data()
        
        embed = discord.Embed(
            title="✅ Self-Roles Channel Set",
            description=f"New members will be directed to {channel.mention} for verification",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"Self-roles channel set to {channel.name}")
    
    @app_commands.command(name="welcome_config", description="[ADMIN] View welcome system configuration")
    @app_commands.default_permissions(administrator=True)
    async def welcome_config(self, interaction: discord.Interaction):
        """Show welcome system configuration"""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="⚙️ Welcome System Configuration",
            color=discord.Color.blue()
        )
        
        # Welcome channel
        if self.welcome_channel_id:
            channel = interaction.guild.get_channel(self.welcome_channel_id)
            welcome_status = f"✅ {channel.mention}" if channel else f"❌ Channel not found (ID: {self.welcome_channel_id})"
        else:
            welcome_status = "❌ Not configured"
        
        embed.add_field(
            name="📢 Welcome Channel",
            value=welcome_status,
            inline=False
        )
        
        # Self-roles channel
        if self.self_roles_channel_id:
            channel = interaction.guild.get_channel(self.self_roles_channel_id)
            self_roles_status = f"✅ {channel.mention}" if channel else f"❌ Channel not found (ID: {self.self_roles_channel_id})"
        else:
            self_roles_status = "❌ Not configured"
        
        embed.add_field(
            name="🔐 Self-Roles Channel",
            value=self_roles_status,
            inline=False
        )
        
        # Class roles
        existing_roles = []
        for class_num in self.class_roles.keys():
            role = discord.utils.get(interaction.guild.roles, name=class_num)
            if role:
                existing_roles.append(f"✅ {class_num}")
            else:
                existing_roles.append(f"❌ {class_num}")
        
        embed.add_field(
            name="🎓 Class Roles",
            value=" | ".join(existing_roles),
            inline=False
        )
        
        # Statistics
        embed.add_field(
            name="📊 Statistics",
            value=f"**{len(self.pending_users)}** pending verifications\n**{len(self.user_profiles)}** completed profiles",
            inline=True
        )
        
        embed.set_footer(text="🤖 Robo Nexus Welcome System")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="view_profile", description="[ADMIN] View a user's profile")
    @app_commands.describe(user="User whose profile to view")
    @app_commands.default_permissions(administrator=True)
    async def view_profile(self, interaction: discord.Interaction, user: discord.Member):
        """View a user's complete profile"""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
            return
        
        user_id = str(user.id)
        
        if user_id not in self.user_profiles:
            await interaction.response.send_message(f"❌ No profile found for {user.display_name}.", ephemeral=True)
            return
        
        profile = self.user_profiles[user_id]
        
        embed = discord.Embed(
            title=f"👤 Profile: {profile['name']}",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎓 Basic Info",
            value=f"**Class:** {profile['class']}\n**Email:** {profile['email']}\n**Discord:** {user.mention}",
            inline=False
        )
        
        if profile.get('social_links'):
            links_text = []
            for platform, url in profile['social_links'].items():
                links_text.append(f"**{platform.title()}:** [Link]({url})")
            
            embed.add_field(
                name="🔗 Social Links",
                value="\n".join(links_text) if links_text else "None provided",
                inline=False
            )
        
        embed.add_field(
            name="📅 Timestamps",
            value=f"**Joined:** <t:{int(discord.utils.parse_time(profile.get('joined_at', '2024-01-01T00:00:00')).timestamp())}:F>\n**Verified:** <t:{int(discord.utils.parse_time(profile.get('verified_at', '2024-01-01T00:00:00')).timestamp())}:F>",
            inline=False
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"User ID: {user.id}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="check_intents", description="[ADMIN] Check if member intents are enabled")
    @app_commands.default_permissions(administrator=True)
    async def check_intents(self, interaction: discord.Interaction):
        """Check if member intents are properly enabled"""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔍 Bot Intents Status",
            color=discord.Color.blue()
        )
        
        # Check intents
        intents = self.bot.intents
        
        embed.add_field(
            name="👥 Members Intent",
            value="✅ Enabled" if intents.members else "❌ DISABLED",
            inline=True
        )
        
        embed.add_field(
            name="💬 Message Content",
            value="✅ Enabled" if intents.message_content else "❌ DISABLED",
            inline=True
        )
        
        embed.add_field(
            name="🏰 Guilds",
            value="✅ Enabled" if intents.guilds else "❌ DISABLED",
            inline=True
        )
        
        embed.add_field(
            name="📊 Guild Members",
            value=f"Can see {interaction.guild.member_count} members",
            inline=False
        )
        
        # Check if on_member_join is registered
        listeners = [listener.__name__ for listener in self.bot.extra_events.get('on_member_join', [])]
        
        embed.add_field(
            name="🎧 on_member_join Listeners",
            value=f"✅ {len(listeners)} registered: {', '.join(listeners) if listeners else 'None'}" if listeners else "❌ No listeners registered",
            inline=False
        )
        
        embed.set_footer(text="If Members Intent is disabled, the bot won't detect new members!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="manual_verify", description="[ADMIN] Manually verify a user")
    @app_commands.describe(
        user="User to verify",
        name="User's name", 
        class_number="User's class (6-12)",
        email="User's Gmail address"
    )
    @app_commands.default_permissions(administrator=True)
    async def manual_verify(
        self, 
        interaction: discord.Interaction, 
        user: discord.Member,
        name: str,
        class_number: int,
        email: str
    ):
        """Manually verify a user"""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
            return
        
        if class_number not in range(6, 13):
            await interaction.response.send_message("❌ Class must be between 6 and 12.", ephemeral=True)
            return
        
        if not self.validate_email(email):
            await interaction.response.send_message("❌ Please provide a valid Gmail address.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        success = await self.assign_class_role(user, str(class_number), name)
        
        if success:
            # Save complete profile
            self.user_profiles[str(user.id)] = {
                "name": name,
                "class": str(class_number),
                "email": email,
                "social_links": {},
                "discord_id": user.id,
                "discord_username": str(user),
                "joined_at": user.joined_at.isoformat() if user.joined_at else None,
                "verified_at": discord.utils.utcnow().isoformat(),
                "manual_verification": True,
                "verified_by": interaction.user.id
            }
            
            # Remove from pending if exists
            if user.id in self.pending_users:
                del self.pending_users[user.id]
            
            self.save_welcome_data()
            
            embed = discord.Embed(
                title="✅ Manual Verification Complete",
                description=f"**{name}** has been verified and assigned Class {class_number} role.",
                color=discord.Color.green()
            )
            embed.add_field(
                name="📧 Email",
                value=email,
                inline=True
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            
            await interaction.followup.send(embed=embed)
            logger.info(f"Manual verification: {user.display_name} -> {name}, Class {class_number}, {email}")
        else:
            await interaction.followup.send("❌ Failed to verify user. Check logs for details.", ephemeral=True)


async def setup(bot):
    """Setup function to add the cog to the bot"""
    await bot.add_cog(WelcomeSystem(bot))
    logger.info("Welcome system cog loaded")