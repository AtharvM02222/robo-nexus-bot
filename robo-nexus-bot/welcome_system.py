from supabase_api import get_supabase_api
"""
Welcome System for Robo Nexus Bot
Handles new member onboarding with name, class, email, and social links collection
NOW USING POSTGRESQL - NO MORE JSON FILES
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
import re
import asyncio
from typing import Optional, Dict
import json
# from supabase_api import get_supabase_api

logger = logging.getLogger(__name__)

class WelcomeSystem(commands.Cog):
    """Welcome system for new member onboarding with profile collection"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = get_supabase_api()
        self.pending_users = {}  # Store users waiting for verification (temporary, in memory)
        
        # Class roles mapping
        self.class_roles = {
            "6": "6", "7": "7", "8": "8", "9": "9", 
            "10": "10", "11": "11", "12": "12"
        }
        
        # Verification stages
        self.STAGE_NAME_CLASS = "name_class"
        self.STAGE_BIRTHDAY = "birthday"
        self.STAGE_EMAIL = "email"
        self.STAGE_PHONE = "phone"
        self.STAGE_LINKS = "links"
        self.STAGE_COMPLETE = "complete"
        
        logger.info("Welcome system initialized with PostgreSQL")
    
    def get_welcome_channel_id(self) -> Optional[int]:
        """Get welcome channel ID from PostgreSQL"""
        try:
            channel_id = self.db.get_setting('welcome_channel_id')
            return int(channel_id) if channel_id else None
        except Exception as e:
            logger.error(f"Error getting welcome channel ID: {e}")
            # Reconnect and retry
            # from supabase_api import get_supabase_api
            self.db = get_supabase_api()
            try:
                channel_id = self.db.get_setting('welcome_channel_id')
                return int(channel_id) if channel_id else None
            except:
                return None
    
    def set_welcome_channel_id(self, channel_id: int):
        """Set welcome channel ID in PostgreSQL"""
        try:
            self.db.set_setting('welcome_channel_id', str(channel_id))
        except Exception as e:
            logger.error(f"Error setting welcome channel ID: {e}")
            # Reconnect and retry
            # from supabase_api import get_supabase_api
            self.db = get_supabase_api()
            self.db.set_setting('welcome_channel_id', str(channel_id))
    
    def get_self_roles_channel_id(self) -> Optional[int]:
        """Get self-roles channel ID from PostgreSQL"""
        try:
            channel_id = self.db.get_setting('self_roles_channel_id')
            return int(channel_id) if channel_id else None
        except Exception as e:
            logger.error(f"Error getting self-roles channel ID: {e}")
            # Reconnect and retry
            # from supabase_api import get_supabase_api
            self.db = get_supabase_api()
            try:
                channel_id = self.db.get_setting('self_roles_channel_id')
                return int(channel_id) if channel_id else None
            except:
                return None
    
    def set_self_roles_channel_id(self, channel_id: int):
        """Set self-roles channel ID in PostgreSQL"""
        try:
            self.db.set_setting('self_roles_channel_id', str(channel_id))
        except Exception as e:
            logger.error(f"Error setting self-roles channel ID: {e}")
            # Reconnect and retry
            # from supabase_api import get_supabase_api
            self.db = get_supabase_api()
            self.db.set_setting('self_roles_channel_id', str(channel_id))
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile from PostgreSQL"""
        profile = self.db.get_user_profile(str(user_id))
        if profile and profile.get('social_links'):
            # Parse JSON field if it's a string
            if isinstance(profile['social_links'], str):
                profile['social_links'] = json.loads(profile['social_links'])
        return profile
    
    def save_user_profile(self, user_id: int, profile_data: Dict) -> bool:
        """Save user profile to PostgreSQL"""
        # Convert social_links dict to JSON string for storage
        if 'social_links' in profile_data and isinstance(profile_data['social_links'], dict):
            profile_data['social_links'] = json.dumps(profile_data['social_links'])
        
        profile_data['user_id'] = str(user_id)
        return self.db.create_user_profile(profile_data)
    
    def update_user_profile(self, user_id: int, updates: Dict) -> bool:
        """Update user profile in PostgreSQL"""
        # Convert social_links dict to JSON string for storage
        if 'social_links' in updates and isinstance(updates['social_links'], dict):
            updates['social_links'] = json.dumps(updates['social_links'])
        
        return self.db.update_user_profile(str(user_id), updates)
    
    def validate_email(self, email: str) -> bool:
        """Validate Gmail address"""
        if not email:
            return False
        
        # Allow skip keywords
        if email.lower().strip() in ['none', 'no', 'skip', 'n/a', 'na']:
            return True
        
        email = email.lower().strip()
        
        # Check if it's a Gmail address
        if not email.endswith('@gmail.com'):
            return False
        
        # Basic email format validation
        pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        return bool(re.match(pattern, email))
    
    def validate_phone(self, phone: str) -> Optional[str]:
        """
        Validate and format phone number
        Returns formatted number or None if invalid
        Accepts skip keywords
        """
        if not phone:
            return None
        
        phone = phone.strip()
        
        # Allow skip keywords
        if phone.lower() in ['none', 'no', 'skip', 'n/a', 'na']:
            return None
        
        # Remove common formatting characters
        cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
        
        # Check if it's all digits (after removing +)
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
        
        if not cleaned.isdigit():
            return None
        
        # Indian phone numbers: 10 digits or with country code (91)
        if len(cleaned) == 10:
            return f"+91{cleaned}"
        elif len(cleaned) == 12 and cleaned.startswith('91'):
            return f"+{cleaned}"
        elif len(cleaned) >= 10:
            # International or other format
            return f"+{cleaned}"
        
        return None
    
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
            
            # Remove common prefixes like "GitHub:", "LinkedIn:", "Website:", etc.
            line = re.sub(r'^(github|linkedin|youtube|spotify|website|portfolio):\s*', '', line, flags=re.IGNORECASE)
            
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
            
            # Portfolio/Website detection (improved with more domains)
            elif any(keyword in line.lower() for keyword in ['portfolio', 'website', 'site']) or \
                 any(domain in line.lower() for domain in ['.dev', '.com', '.org', '.net', '.io', '.me', '.co', '.github.io', '.netlify.app', '.vercel.app', '.herokuapp.com', '.firebase.app', '.pages.dev']) or \
                 line.startswith('http'):
                
                # This is likely a website/portfolio
                url = line if line.startswith('http') else f"https://{line}"
                
                # Use 'website' as the key for portfolio/personal websites
                website_key = 'website'
                counter = 1
                while website_key in links:
                    counter += 1
                    website_key = f'website{counter}'
                
                links[website_key] = url
        
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
                value="```\nJohn Smith, Class 10\n```\nor:\n```\nJohn Smith 10th grade\n```",
                inline=False
            )
            
            embed.add_field(
                name="🔄 What's Next?",
                value="After this, I'll ask for:\n• Your birthday\n• Your Gmail address\n• Social media links (including portfolio website)",
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
            self_roles_channel_id = self.get_self_roles_channel_id()
            # Add fallback for welcome channel
            if not self_roles_channel_id:
                # Fallback to hardcoded ID for SSL connection issues
                self_roles_channel_id = 1460556204383273148
                logger.info("Using fallback self-roles channel ID due to database connection issue")
            
            # Add fallback for welcome channel
            if not self_roles_channel_id:
                logger.warning("Self-roles channel not configured, cannot send welcome message")
                return
            
            channel = member.guild.get_channel(self_roles_channel_id)
            if not channel:
                logger.error(f"Self-roles channel {self_roles_channel_id} not found")
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
                title="📧 Step 2: Gmail Address (Optional)",
                description=f"Great! Welcome **{name}** from Class {class_num}!",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📮 Please provide your Gmail address",
                value="We use Gmail for:\n• Team communications\n• Project updates\n• Important announcements",
                inline=False
            )
            
            embed.add_field(
                name="💡 Example",
                value="`john.smith@gmail.com`",
                inline=False
            )
            
            embed.add_field(
                name="⏭️ Skip This Step",
                value="Type `skip` or `none` if you don't want to share your email.",
                inline=False
            )
            
            embed.set_footer(text="🔒 Your email is optional and kept private")
            
            await message.reply(embed=embed)
            
        except Exception as e:
            logger.error(f"Error sending email request: {e}")
    
    async def send_phone_request(self, message: discord.Message):
        """Send request for phone number - Stage 3"""
        try:
            embed = discord.Embed(
                title="📱 Step 3: Phone Number (Optional)",
                description="Almost there! Please share your phone number:",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📞 Why we need it",
                value="• Emergency contact\n• Team coordination\n• Event notifications",
                inline=False
            )
            
            embed.add_field(
                name="💡 Example",
                value="`9876543210` or `+91 98765 43210`",
                inline=False
            )
            
            embed.add_field(
                name="⏭️ Skip This Step",
                value="Type `skip` or `none` if you don't want to share your number.",
                inline=False
            )
            
            embed.set_footer(text="🔒 Your number is optional and kept private")
            
            await message.reply(embed=embed)
            
        except Exception as e:
            logger.error(f"Error sending phone request: {e}")
    
    async def send_links_request(self, message: discord.Message):
        """Send request for social media links - Stage 4 (Portfolio Website Emphasized)"""
        try:
            embed = discord.Embed(
                title="🔗 Step 4: Social Media Links & Portfolio",
                description="Last step! Please share your online presence:",
                color=discord.Color.purple()
            )
            
            embed.add_field(
                name="🌟 **PORTFOLIO WEBSITE (Highly Recommended)**",
                value="• **Personal Website** - Your portfolio/projects showcase\n• **GitHub Pages** - Your coding portfolio\n• **Portfolio Site** - Any personal website",
                inline=False
            )
            
            embed.add_field(
                name="🔗 Other Social Platforms",
                value="• **GitHub** - Your coding projects\n• **LinkedIn** - Professional profile\n• **YouTube** - Your channel\n• **Spotify** - Music profile",
                inline=False
            )
            
            embed.add_field(
                name="💡 Example Response",
                value="```\nPortfolio: johnsmith.dev\nGitHub: github.com/johnsmith\nLinkedIn: linkedin.com/in/johnsmith\n```\nOr simply: `None` if you don't have any links",
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Important Note",
                value="**Having a portfolio website may be required for certain features like creating auction listings.** Consider creating one to showcase your projects!",
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
            welcome_channel_id = self.get_welcome_channel_id()
            if welcome_channel_id:
                channel = member.guild.get_channel(welcome_channel_id)
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
            self_roles_channel_id = self.get_self_roles_channel_id()
            is_self_roles_channel = (
                self_roles_channel_id and 
                message.channel.id == self_roles_channel_id
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
                
            elif current_stage == self.STAGE_BIRTHDAY:
                await self.process_birthday_stage(message, user_input)
                
            elif current_stage == self.STAGE_EMAIL:
                await self.process_email_stage(message, user_input)
            
            elif current_stage == self.STAGE_PHONE:
                await self.process_phone_stage(message, user_input)
                
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
                    value="Please include your name and class like:\n• `John Smith, Class 10`\n• `Sarah, Grade 8`\n• `Mike 12th`",
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
            
            # Store name and class, move to birthday stage
            self.pending_users[member.id]["profile"]["name"] = name
            self.pending_users[member.id]["profile"]["class"] = class_number
            self.pending_users[member.id]["stage"] = self.STAGE_BIRTHDAY
            
            # Request birthday
            await self.send_birthday_request(message, name, class_number)
            
        except Exception as e:
            logger.error(f"Error processing name/class stage: {e}")
    
    async def send_birthday_request(self, message: discord.Message, name: str, class_number: str):
        """Send request for birthday - Stage 2"""
        try:
            embed = discord.Embed(
                title="🎂 Step 2: Your Birthday",
                description=f"Great! Nice to meet you, **{name}** from Class **{class_number}**!",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📅 Birthday Information",
                value="Please share your birthday so we can celebrate with you!",
                inline=False
            )
            
            embed.add_field(
                name="📝 Format",
                value="Please provide your birthday in **MM-DD** format:",
                inline=False
            )
            
            embed.add_field(
                name="💡 Examples",
                value="• `03-15` (March 15)\n• `12-25` (December 25)\n• `07/04` (July 4)\n• `11/22` (November 22)",
                inline=False
            )
            
            embed.add_field(
                name="🎉 What happens?",
                value="The Robo Nexus community will be notified on your birthday with a special celebration message!",
                inline=False
            )
            
            await message.reply(embed=embed)
            
        except Exception as e:
            logger.error(f"Error sending birthday request: {e}")
    
    async def process_birthday_stage(self, message: discord.Message, user_input: str):
        """Process Stage 2: Birthday"""
        try:
            member = message.author
            birthday_input = user_input.strip()
            
            from date_parser import DateParser
            
            # Parse the birthday
            birthday_date = DateParser.parse_birthday(birthday_input)
            
            if not birthday_date:
                embed = discord.Embed(
                    title="❌ Invalid Birthday Format",
                    description="I couldn't understand that birthday format.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="📅 Supported Formats",
                    value=DateParser.get_format_help_text(),
                    inline=False
                )
                embed.add_field(
                    name="💡 Examples",
                    value="• `03-15` (March 15)\n• `12/25` (December 25)\n• `07-04` (July 4)",
                    inline=False
                )
                
                await message.reply(embed=embed, delete_after=60)
                return
            
            # Store birthday and register it in the birthday system
            self.pending_users[member.id]["profile"]["birthday"] = birthday_date
            self.pending_users[member.id]["stage"] = self.STAGE_EMAIL
            
            # Register birthday in BOTH the birthday system AND user profile
            try:
                # Convert date object to MM-DD string format for database
                birthday_string = birthday_date.strftime('%m-%d')
                
                # Save to birthdays table
                from database import add_birthday
                birthday_success = add_birthday(member.id, birthday_string)
                
                # Also save to user_profiles table (update the pending profile)
                # This will be saved when the profile is completed
                self.pending_users[member.id]["profile"]["birthday"] = birthday_string
                formatted_date = DateParser.format_birthday(birthday_date)
                
                if birthday_success: 
                    logger.info(f"Birthday registered for {member.display_name} during verification: {formatted_date}")
                
                # Confirm birthday registration
                confirm_embed = discord.Embed(
                    title="🎉 Birthday Registered!",
                    description=f"Your birthday has been set to **{formatted_date}**\n\nThe Robo Nexus community will celebrate with you on your special day! 🎂",
                    color=discord.Color.green()
                )
                await message.reply(embed=confirm_embed, delete_after=30)
                
            except Exception as e:
                logger.error(f"Error registering birthday during verification: {e}")
            
            # Get user's name and class for the email request
            name = self.pending_users[member.id]["profile"]["name"]
            class_number = self.pending_users[member.id]["profile"]["class"]
            
            # Request email
            await self.send_email_request(message, name, class_number)
            
        except Exception as e:
            logger.error(f"Error processing birthday stage: {e}")

    async def process_email_stage(self, message: discord.Message, user_input: str):
        """Process Stage 2: Email"""
        try:
            member = message.author
            email = user_input.strip()
            
            # Check if user wants to skip
            if email.lower() in ['none', 'no', 'skip', 'n/a', 'na']:
                # Skip email, move to phone stage
                self.pending_users[member.id]["profile"]["email"] = None
                self.pending_users[member.id]["stage"] = self.STAGE_PHONE
                
                # Request phone number
                await self.send_phone_request(message)
                return
            
            if not self.validate_email(email):
                embed = discord.Embed(
                    title="❌ Invalid Gmail Address",
                    description="Please provide a valid Gmail address or type `skip` to skip this step.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="📧 Requirements",
                    value="• Must be a Gmail address (@gmail.com)\n• Example: `john.smith@gmail.com`\n• Or type: `skip`",
                    inline=False
                )
                
                await message.reply(embed=embed, delete_after=60)
                return
            
            # Store email, move to phone stage
            self.pending_users[member.id]["profile"]["email"] = email
            self.pending_users[member.id]["stage"] = self.STAGE_PHONE
            
            # Request phone number
            await self.send_phone_request(message)
            
        except Exception as e:
            logger.error(f"Error processing email stage: {e}")
    
    async def process_phone_stage(self, message: discord.Message, user_input: str):
        """Process Stage 3: Phone Number"""
        try:
            member = message.author
            phone_input = user_input.strip()
            
            # Check if user wants to skip
            if phone_input.lower() in ['none', 'no', 'skip', 'n/a', 'na']:
                # Skip phone, move to links stage
                self.pending_users[member.id]["profile"]["phone"] = None
                self.pending_users[member.id]["stage"] = self.STAGE_LINKS
                
                # Request social links
                await self.send_links_request(message)
                return
            
            # Validate phone number
            formatted_phone = self.validate_phone(phone_input)
            
            if not formatted_phone:
                embed = discord.Embed(
                    title="❌ Invalid Phone Number",
                    description="Please provide a valid phone number or type `skip` to skip this step.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="📱 Requirements",
                    value="• 10 digits for Indian numbers\n• Example: `9876543210` or `+91 98765 43210`\n• Or type: `skip`",
                    inline=False
                )
                
                await message.reply(embed=embed, delete_after=60)
                return
            
            # Store phone, move to links stage
            self.pending_users[member.id]["profile"]["phone"] = formatted_phone
            self.pending_users[member.id]["stage"] = self.STAGE_LINKS
            
            # Request social links
            await self.send_links_request(message)
            
        except Exception as e:
            logger.error(f"Error processing phone stage: {e}")
    
    async def process_links_stage(self, message: discord.Message, user_input: str):
        """Process Stage 4: Social Links"""
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
            email = profile.get("email")
            phone = profile.get("phone")
            social_links = profile.get("social_links", {})
            
            # Assign the class role
            success = await self.assign_class_role(member, class_number, name)
            
            if success:
                # Save complete profile to PostgreSQL
                profile_data = {
                    "user_id": str(member.id),
                    "username": str(member),
                    "display_name": name,
                    "email": email,
                    "phone": phone,
                    "class_year": class_number,
                    "birthday": profile.get("birthday"),  # This should already be a string from DateParser
                    "social_links": json.dumps(social_links) if social_links else None,
                    "verification_status": "verified",
                    "verification_stage": "complete"
                }
                
                # Ensure birthday is a string if it exists
                if profile_data["birthday"] and hasattr(profile_data["birthday"], 'strftime'):
                    profile_data["birthday"] = profile_data["birthday"].strftime('%m-%d')
                
                # Save profile with error handling
                profile_saved = self.save_user_profile(member.id, profile_data)
                
                if not profile_saved:
                    logger.error(f"CRITICAL: Failed to save user profile for {member.display_name} ({member.id})")
                    # Still complete verification but log the error
                    error_embed = discord.Embed(
                        title="⚠️ Verification Complete (with warning)",
                        description="Your verification is complete, but there was an issue saving your profile. Please contact an admin.",
                        color=discord.Color.orange()
                    )
                    await message.reply(embed=error_embed)
                else:
                    logger.info(f"✅ User profile saved successfully for {member.display_name}")
                
                # Remove from pending users
                del self.pending_users[member.id]
                
                # Send completion message
                embed = discord.Embed(
                    title="✅ Welcome Complete!",
                    description=f"Welcome to Robo Nexus, **{name}**!",
                    color=discord.Color.green()
                )
                
                profile_text = f"**Name:** {name}\n**Class:** {class_number}"
                if email:
                    profile_text += f"\n**Email:** {email}"
                if phone:
                    profile_text += f"\n**Phone:** {phone}"
                
                embed.add_field(
                    name="🎓 Profile Summary",
                    value=profile_text,
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
                    value="• Explore all server channels\n• Join your classmates\n• Participate in robotics discussions!",
                    inline=False
                )
                
                await message.reply(embed=embed)
                
                # Log successful verification
                logger.info(f"Successfully verified {member.display_name}: {name}, Class {class_number}, {email}")
                
                # Notify in welcome channel
                welcome_channel_id = self.get_welcome_channel_id()
                if welcome_channel_id:
                    channel = member.guild.get_channel(welcome_channel_id)
                    if channel:
                        welcome_embed = discord.Embed(
                            title="✅ Member Verified",
                            description=f"**{name}** (Class {class_number}) is now fully set up!",
                            color=discord.Color.green()
                        )
                        
                        contact_info = []
                        if email:
                            contact_info.append(f"📧 {email}")
                        if phone:
                            contact_info.append(f"📱 {phone}")
                        
                        if contact_info:
                            welcome_embed.add_field(
                                name="📞 Contact",
                                value="\n".join(contact_info),
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
            
            # Update nickname to the provided name
            try:
                # Always set nickname to the provided name (max 32 characters for Discord)
                if len(name) <= 32:
                    await member.edit(nick=name, reason="Set name from welcome verification")
                    logger.info(f"Set nickname to '{name}' for {member.display_name}")
                else:
                    logger.warning(f"Name '{name}' is too long ({len(name)} chars), max is 32")
            except discord.Forbidden:
                logger.warning(f"Could not set nickname for {member.display_name} - missing permissions or user has higher role")
            except Exception as e:
                logger.error(f"Error setting nickname: {e}")
            
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
        
        self.set_welcome_channel_id(channel.id)
        
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
        
        self.set_self_roles_channel_id(channel.id)
        
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
        welcome_channel_id = self.get_welcome_channel_id()
        if welcome_channel_id:
            channel = interaction.guild.get_channel(welcome_channel_id)
            welcome_status = f"✅ {channel.mention}" if channel else f"❌ Channel not found (ID: {welcome_channel_id})"
        else:
            welcome_status = "❌ Not configured"
        
        embed.add_field(
            name="📢 Welcome Channel",
            value=welcome_status,
            inline=False
        )
        
        # Self-roles channel
        self_roles_channel_id = self.get_self_roles_channel_id()
        if self_roles_channel_id:
            channel = interaction.guild.get_channel(self_roles_channel_id)
            self_roles_status = f"✅ {channel.mention}" if channel else f"❌ Channel not found (ID: {self_roles_channel_id})"
        else:
            self_roles_status = "❌ Not configured"
        
        embed.add_field(
            name="🎭 Self-Roles Channel",
            value=self_roles_status,
            inline=False
        )
        
        # Statistics
        profile_count = self.db.count_user_profiles()
        embed.add_field(
            name="📊 Statistics",
            value=f"• **{len(self.pending_users)}** users in verification\n• **{profile_count}** completed profiles",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="birthday_collect", description="Collect birthday data in self-roles channel")
    @app_commands.describe(date="Your birthday (MM-DD format, e.g., 03-15)")
    async def birthday_collect(self, interaction: discord.Interaction, date: str):
        """Collect birthday data from users in self-roles channel"""
        
        # Check if this is being used in the self-roles channel
        self_roles_channel_id = self.get_self_roles_channel_id()
        if not self_roles_channel_id or interaction.channel.id != self_roles_channel_id:
            await interaction.response.send_message(
                "❌ This command can only be used in the self-roles channel.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            from date_parser import DateParser
            
            # Parse the birthday
            birthday = DateParser.parse_birthday(date)
            
            if not birthday:
                embed = discord.Embed(
                    title="❌ Invalid Date Format",
                    description="I couldn't understand that date format.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="Supported Formats",
                    value=DateParser.get_format_help_text(),
                    inline=False
                )
                embed.add_field(
                    name="Examples",
                    value="• `03-15` (March 15)\n• `12/25` (December 25)\n• `07-04` (July 4)",
                    inline=False
                )
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Register the birthday
# #             db_manager = self.bot.db_manager
#             success = await db_manager.register_birthday(interaction.user.id, birthday)
            
            if success:
                formatted_date = DateParser.format_birthday(birthday)
                
                # Also update user profile if it exists
                user_id_str = str(interaction.user.id)
                profile = self.get_user_profile(interaction.user.id)
                if profile:
                    self.update_user_profile(interaction.user.id, {"birthday": birthday.isoformat()})
                
                success_embed = discord.Embed(
                    title="🎉 Birthday Registered!",
                    description=f"Your birthday has been set to **{formatted_date}**",
                    color=discord.Color.green()
                )
                success_embed.add_field(
                    name="What happens next?",
                    value="• The Robo Nexus community will be notified on your birthday\n• You can update your birthday anytime with this command\n• Birthday celebrations will be posted in the birthday channel",
                    inline=False
                )
                success_embed.set_footer(text="🎂 Happy early birthday from Robo Nexus!")
                
                await interaction.followup.send(embed=success_embed, ephemeral=True)
                logger.info(f"Birthday registered via self-roles for {interaction.user.display_name}: {formatted_date}")
                
            else:
                error_embed = discord.Embed(
                    title="❌ Registration Failed",
                    description="There was an error saving your birthday. Please try again.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error in birthday_collect command: {e}")
            await interaction.followup.send(
                "❌ An error occurred while registering your birthday. Please try again.",
                ephemeral=True
            )
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
        profile_count = self.db.count_user_profiles()
        embed.add_field(
            name="📊 Statistics",
            value=f"**{len(self.pending_users)}** pending verifications\n**{profile_count}** completed profiles",
            inline=True
        )
        
        embed.set_footer(text="🤖 Robo Nexus Welcome System")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="debug_data", description="[ADMIN] Check database data")
    @app_commands.default_permissions(administrator=True)
    async def debug_data(self, interaction: discord.Interaction):
        """Debug command to check database data"""
        
        await interaction.response.defer(ephemeral=True)
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("❌ Administrator permissions required.", ephemeral=True)
            return
        
        try:
            # Check auctions
            auctions = self.db.get_all_auctions('active')
            
            # Check user profiles
            profile = self.db.get_user_profile(str(interaction.user.id))
            
            # Check birthdays
            birthdays = self.db.get_all_birthdays()
            
            embed = discord.Embed(
                title="🔍 Database Debug Info",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📊 Data Counts",
                value=f"**Auctions:** {len(auctions)}\n**Birthdays:** {len(birthdays)}\n**Your Profile:** {'✅ Found' if profile else '❌ Not found'}",
                inline=False
            )
            
            if auctions:
                auction_names = [a.get('product_name', 'Unknown') for a in auctions[:3]]
                embed.add_field(
                    name="🏷️ Sample Auctions",
                    value="\n".join(auction_names),
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Debug error: {str(e)}", ephemeral=True)

    @app_commands.command(name="view_profile", description="[ADMIN] View a user's profile")
    @app_commands.describe(user="User whose profile to view")
    @app_commands.default_permissions(administrator=True)
    async def view_profile(self, interaction: discord.Interaction, user: discord.Member):
        """View a user's complete profile"""
        
        await interaction.response.defer(ephemeral=True)
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("❌ Administrator permissions required.", ephemeral=True)
            return
        
        user_id = str(user.id)
        
        # Get profile from Supabase
        profile = self.db.get_user_profile(user_id)
        if not profile:
            await interaction.followup.send(f"❌ No profile found for {user.display_name}.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"👤 Profile: {profile.get('display_name', user.display_name)}",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎓 Basic Info",
            value=f"**Class:** {profile.get('class_year', 'N/A')}\n**Email:** {profile.get('email') or 'Not provided'}\n**Phone:** {profile.get('phone') or 'Not provided'}\n**Discord:** {user.mention}",
            inline=False
        )
        
        # Check for birthday in profile
        birthday = profile.get('birthday')
        if birthday:
            try:
                from date_parser import DateParser
                formatted_birthday = DateParser.format_birthday(birthday)
                embed.add_field(
                    name="🎂 Birthday",
                    value=formatted_birthday,
                    inline=True
                )
            except:
                embed.add_field(
                    name="🎂 Birthday",
                    value=birthday,
                    inline=True
                )
        else:
            embed.add_field(
                name="🎂 Birthday",
                value="Not registered",
                inline=True
            )
        
        if profile.get('social_links'):
            # Parse social_links if it's a JSON string
            social_links = profile['social_links']
            if isinstance(social_links, str):
                social_links = json.loads(social_links)
            
            links_text = []
            for platform, url in social_links.items():
                links_text.append(f"**{platform.title()}:** [Link]({url})")
            
            embed.add_field(
                name="🔗 Social Links",
                value="\n".join(links_text) if links_text else "None provided",
                inline=False
            )
        
        embed.add_field(
            name="📅 Timestamps",
            value=f"**Created:** <t:{int(profile.get('created_at', discord.utils.utcnow()).timestamp())}:F>\n**Updated:** <t:{int(profile.get('updated_at', discord.utils.utcnow()).timestamp())}:F>",
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
    
    @app_commands.command(name="update_profile", description="[ADMIN] Update a user's profile")
    @app_commands.describe(
        user="User whose profile to update",
        name="New name (leave empty to keep current)",
        class_number="New class (leave empty to keep current)",
        email="New email (leave empty to keep current)",
        phone="New phone number (leave empty to keep current)",
        social_links="Social links to ADD (will merge with existing links)"
    )
    @app_commands.default_permissions(administrator=True)
    async def update_profile(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        name: str = None,
        class_number: int = None,
        email: str = None,
        phone: str = None,
        social_links: str = None
    ):
        """Update an existing user's profile"""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
            return
        
        user_id = str(user.id)
        
        # Check if user has a profile
        profile = self.get_user_profile(int(user_id))
        if not profile:
            await interaction.response.send_message(
                f"❌ No profile found for {user.display_name}. Use `/manual_verify` to create one first.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        changes = []
        
        # Update name
        if name:
            old_name = profile.get('display_name', 'Unknown')
            changes.append(f"**Name:** {old_name} → {name}")
            self.update_user_profile(int(user_id), {"display_name": name})
            
            # Update nickname
            try:
                if len(name) <= 32:
                    await user.edit(nick=name, reason="Profile name updated")
            except:
                pass
        
        # Update class
        if class_number:
            if class_number not in range(6, 13):
                await interaction.followup.send("❌ Class must be between 6 and 12.", ephemeral=True)
                return
            
            old_class = profile.get('class_year', 'Unknown')
            changes.append(f"**Class:** {old_class} → {class_number}")
            self.update_user_profile(int(user_id), {"class_year": str(class_number)})
            
            # Update class role
            # Remove old class role
            old_role = discord.utils.get(user.guild.roles, name=old_class)
            if old_role and old_role in user.roles:
                await user.remove_roles(old_role, reason="Class updated")
            
            # Add new class role
            new_role = await self.get_or_create_role(user.guild, str(class_number))
            if new_role:
                await user.add_roles(new_role, reason="Class updated")
        
        # Update email
        if email:
            if not self.validate_email(email):
                await interaction.followup.send("❌ Please provide a valid Gmail address or leave empty.", ephemeral=True)
                return
            
            old_email = profile.get('email', 'Not provided')
            changes.append(f"**Email:** {old_email} → {email}")
            self.update_user_profile(int(user_id), {"email": email})
        
        # Update phone
        if phone:
            formatted_phone = self.validate_phone(phone)
            if not formatted_phone:
                await interaction.followup.send("❌ Please provide a valid phone number.", ephemeral=True)
                return
            
            old_phone = profile.get('phone', 'Not provided')
            changes.append(f"**Phone:** {old_phone} → {formatted_phone}")
            self.update_user_profile(int(user_id), {"phone": formatted_phone})
        
        # Add/update social links
        if social_links:
            new_links = self.validate_social_links(social_links)
            
            if new_links:
                # Merge with existing links (new links override old ones with same key)
                existing_links = profile.get('social_links', {})
                if isinstance(existing_links, str):
                    existing_links = json.loads(existing_links)
                elif not existing_links:
                    existing_links = {}
                
                existing_links.update(new_links)
                
                added_links = []
                for platform, url in new_links.items():
                    added_links.append(f"**{platform.title()}:** {url}")
                
                changes.append(f"**Social Links Added/Updated:**\n" + "\n".join(added_links))
                self.update_user_profile(int(user_id), {"social_links": json.dumps(existing_links)})
        
        if not changes:
            await interaction.followup.send("❌ No changes specified. Provide at least one field to update.", ephemeral=True)
            return
        
        # Refresh profile from database
        profile = self.get_user_profile(int(user_id))
        
        # Send confirmation
        embed = discord.Embed(
            title="✅ Profile Updated",
            description=f"Updated profile for {user.mention}",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📝 Changes Made",
            value="\n\n".join(changes),
            inline=False
        )
        
        embed.add_field(
            name="👤 Current Profile",
            value=f"**Name:** {profile.get('display_name', 'Unknown')}\n**Class:** {profile.get('class_year', 'N/A')}\n**Email:** {profile.get('email') or 'Not provided'}\n**Phone:** {profile.get('phone') or 'Not provided'}",
            inline=False
        )
        
        if profile.get('social_links'):
            social_links_data = profile['social_links']
            if isinstance(social_links_data, str):
                social_links_data = json.loads(social_links_data)
            
            links_text = []
            for platform, url in social_links_data.items():
                links_text.append(f"**{platform.title()}:** {url}")
            
            embed.add_field(
                name="🔗 All Social Links",
                value="\n".join(links_text),
                inline=False
            )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Updated by {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed)
        logger.info(f"Profile updated for {user.display_name} by {interaction.user.display_name}: {len(changes)} changes")
    
    @app_commands.command(name="export_profiles", description="[ADMIN] Export all user profiles to CSV")
    @app_commands.default_permissions(administrator=True)
    async def export_profiles(self, interaction: discord.Interaction):
        """Export all user profiles to a CSV file"""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            import csv
            import io
            
            all_profiles = self.db.get_all_user_profiles()
            
            if not all_profiles:
                await interaction.followup.send("❌ No profiles to export.", ephemeral=True)
                return
            
            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Name', 'Class', 'Email', 'Phone', 'Birthday',
                'Discord Username', 'Discord ID', 'Joined At', 'Verified At',
                'GitHub', 'LinkedIn', 'YouTube', 'Spotify', 'Website'
            ])
            
            # Write data
            for profile in all_profiles:
                user_id = profile.get('user_id')
                
                # Get birthday if registered
                birthday_str = "Not registered"
                try:
# #                     birthday = await self.bot.db_manager.get_birthday(int(user_id))
                    if birthday:
                        birthday_str = birthday.strftime("%B %d")
                except:
                    pass
                
                # Get social links
                social_links_data = profile.get('social_links', {})
                if isinstance(social_links_data, str):
                    social_links_data = json.loads(social_links_data)
                elif not social_links_data:
                    social_links_data = {}
                
                github = social_links_data.get('github', '')
                linkedin = social_links_data.get('linkedin', '')
                youtube = social_links_data.get('youtube', '')
                spotify = social_links_data.get('spotify', '')
                website = social_links_data.get('website', '')
                
                writer.writerow([
                    profile.get('display_name', ''),
                    profile.get('class_year', ''),
                    profile.get('email', ''),
                    profile.get('phone', ''),
                    birthday_str,
                    profile.get('username', ''),
                    profile.get('user_id', ''),
                    profile.get('created_at', ''),
                    profile.get('updated_at', ''),
                    github,
                    linkedin,
                    youtube,
                    spotify,
                    website
                ])
            
            # Convert to bytes
            output.seek(0)
            file_content = output.getvalue().encode('utf-8')
            
            # Create Discord file
            from datetime import datetime
            filename = f"robo_nexus_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            file = discord.File(io.BytesIO(file_content), filename=filename)
            
            # Send file
            embed = discord.Embed(
                title="📊 Profiles Exported",
                description=f"Exported {len(all_profiles)} user profiles",
                color=discord.Color.green()
            )
            embed.add_field(
                name="📁 File",
                value=f"`{filename}`",
                inline=False
            )
            embed.set_footer(text="Open with Excel, Google Sheets, or any spreadsheet app")
            
            await interaction.followup.send(embed=embed, file=file)
            logger.info(f"Profiles exported by {interaction.user.display_name}: {len(all_profiles)} profiles")
            
        except Exception as e:
            logger.error(f"Error exporting profiles: {e}")
            await interaction.followup.send(f"❌ Error exporting profiles: {str(e)[:100]}", ephemeral=True)
    
    @app_commands.command(name="manual_verify", description="[ADMIN] Manually verify a user")
    @app_commands.describe(
        user="User to verify",
        name="User's name", 
        class_number="User's class (6-12)",
        email="User's Gmail address (optional)",
        phone="User's phone number (optional)",
        social_links="Optional: Social links (GitHub, LinkedIn, Website, etc.) separated by commas"
    )
    @app_commands.default_permissions(administrator=True)
    async def manual_verify(
        self, 
        interaction: discord.Interaction, 
        user: discord.Member,
        name: str,
        class_number: int,
        email: str = None,
        phone: str = None,
        social_links: str = None
    ):
        """Manually verify a user"""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
            return
        
        if class_number not in range(6, 13):
            await interaction.response.send_message("❌ Class must be between 6 and 12.", ephemeral=True)
            return
        
        # Validate email if provided
        if email and not self.validate_email(email):
            await interaction.response.send_message("❌ Please provide a valid Gmail address or leave empty.", ephemeral=True)
            return
        
        # Validate phone if provided
        formatted_phone = None
        if phone:
            formatted_phone = self.validate_phone(phone)
            if not formatted_phone:
                await interaction.response.send_message("❌ Please provide a valid phone number or leave empty.", ephemeral=True)
                return
        
        await interaction.response.defer()
        
        # Parse social links if provided
        parsed_links = {}
        if social_links:
            parsed_links = self.validate_social_links(social_links)
        
        success = await self.assign_class_role(user, str(class_number), name)
        
        if success:
            # Save complete profile to PostgreSQL
            # Get existing birthday if any
            from database import get_birthday
            existing_birthday = get_birthday(user.id)
            
            profile_data = {
                "user_id": str(user.id),
                "username": str(user),
                "display_name": name,
                "email": email,
                "phone": formatted_phone,
                "class_year": str(class_number),
                "birthday": existing_birthday,  # Use existing birthday instead of None
                "social_links": json.dumps(parsed_links) if parsed_links else None,
                "verification_status": "verified",
                "verification_stage": "complete"
            }
            
            self.save_user_profile(user.id, profile_data)
            
            # Remove from pending if exists
            if user.id in self.pending_users:
                del self.pending_users[user.id]
            
            embed = discord.Embed(
                title="✅ Manual Verification Complete",
                description=f"**{name}** has been verified and assigned Class {class_number} role.",
                color=discord.Color.green()
            )
            
            contact_info = []
            if email:
                contact_info.append(f"📧 {email}")
            if formatted_phone:
                contact_info.append(f"📱 {formatted_phone}")
            
            if contact_info:
                embed.add_field(
                    name="📞 Contact",
                    value="\n".join(contact_info),
                    inline=True
                )
            
            if parsed_links:
                links_text = []
                for platform, url in parsed_links.items():
                    links_text.append(f"**{platform.title()}:** {url}")
                
                embed.add_field(
                    name="🔗 Social Links",
                    value="\n".join(links_text),
                    inline=False
                )
            
            embed.set_thumbnail(url=user.display_avatar.url)
            
            await interaction.followup.send(embed=embed)
            logger.info(f"Manual verification: {user.display_name} -> {name}, Class {class_number}, {len(parsed_links)} links")
        else:
            await interaction.followup.send("❌ Failed to verify user. Check logs for details.", ephemeral=True)


async def setup(bot):
    """Setup function to add the cog to the bot"""
    await bot.add_cog(WelcomeSystem(bot))
    logger.info("Welcome system cog loaded")