"""
Robo Nexus Auction System
Marketplace for robotics equipment - buy, sell, and bid on items
"""
import discord
from discord import app_commands
from discord.ext import commands, tasks
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import asyncio

logger = logging.getLogger(__name__)

AUCTION_DATA_FILE = "auction_data.json"

class AuctionItem:
    """Represents an auction item"""
    def __init__(self, data: dict):
        self.id = data.get("id")
        self.title = data.get("title")
        self.description = data.get("description")
        self.image_url = data.get("image_url")
        self.starting_price = data.get("starting_price", 0)
        self.buy_now_price = data.get("buy_now_price")  # Optional instant buy
        self.current_bid = data.get("current_bid", 0)
        self.current_bidder_id = data.get("current_bidder_id")
        self.seller_id = data.get("seller_id")
        self.created_at = data.get("created_at")
        self.ends_at = data.get("ends_at")
        self.status = data.get("status", "active")  # active, sold, closed, expired
        self.bid_history = data.get("bid_history", [])
        self.category = data.get("category", "Other")
        self.condition = data.get("condition", "Used")
        self.message_id = data.get("message_id")
        self.channel_id = data.get("channel_id")
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "image_url": self.image_url,
            "starting_price": self.starting_price,
            "buy_now_price": self.buy_now_price,
            "current_bid": self.current_bid,
            "current_bidder_id": self.current_bidder_id,
            "seller_id": self.seller_id,
            "created_at": self.created_at,
            "ends_at": self.ends_at,
            "status": self.status,
            "bid_history": self.bid_history,
            "category": self.category,
            "condition": self.condition,
            "message_id": self.message_id,
            "channel_id": self.channel_id
        }


class AuctionSystem(commands.Cog):
    """Auction and marketplace system for Robo Nexus"""
    
    def __init__(self, bot):
        self.bot = bot
        self.auctions: Dict[int, AuctionItem] = {}
        self.next_id = 1
        self.auction_channel_id = None
        
        # Load existing auctions
        self.load_auctions()
        
        # Start auction monitoring
        self.check_expired_auctions.start()
        
        logger.info("Auction system initialized")
    
    def load_auctions(self):
        """Load auctions from file"""
        try:
            if os.path.exists(AUCTION_DATA_FILE):
                with open(AUCTION_DATA_FILE, 'r') as f:
                    data = json.load(f)
                    
                    self.next_id = data.get("next_id", 1)
                    self.auction_channel_id = data.get("auction_channel_id")
                    
                    for auction_data in data.get("auctions", []):
                        item = AuctionItem(auction_data)
                        self.auctions[item.id] = item
                    
                    logger.info(f"Loaded {len(self.auctions)} auctions")
        except Exception as e:
            logger.error(f"Error loading auctions: {e}")
    
    def save_auctions(self):
        """Save auctions to file"""
        try:
            data = {
                "next_id": self.next_id,
                "auction_channel_id": self.auction_channel_id,
                "auctions": [item.to_dict() for item in self.auctions.values()]
            }
            
            with open(AUCTION_DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving auctions: {e}")
    
    def is_admin(self, member: discord.Member) -> bool:
        """Check if user has admin permissions"""
        return member.guild_permissions.administrator or member.guild_permissions.manage_guild
    
    async def get_auction_channel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """Get the auction channel"""
        if self.auction_channel_id:
            channel = guild.get_channel(self.auction_channel_id)
            if channel:
                return channel
        
        # Try to find auction channel by name
        for channel in guild.text_channels:
            if "auction" in channel.name.lower():
                self.auction_channel_id = channel.id
                self.save_auctions()
                return channel
        
        return None
    
    @tasks.loop(minutes=5)
    async def check_expired_auctions(self):
        """Check for expired auctions and close them"""
        try:
            now = datetime.now()
            
            for auction in list(self.auctions.values()):
                if auction.status != "active":
                    continue
                
                if auction.ends_at:
                    end_time = datetime.fromisoformat(auction.ends_at)
                    if now >= end_time:
                        await self.close_auction(auction, "expired")
            
        except Exception as e:
            logger.error(f"Error checking expired auctions: {e}")
    
    @check_expired_auctions.before_loop
    async def before_check_expired(self):
        await self.bot.wait_until_ready()
    
    def cog_unload(self):
        self.check_expired_auctions.cancel()
        self.save_auctions()

    
    async def close_auction(self, auction: AuctionItem, reason: str = "manual"):
        """Close an auction and announce winner"""
        try:
            auction.status = "sold" if auction.current_bidder_id else "closed"
            self.save_auctions()
            
            # Find the auction channel
            for guild in self.bot.guilds:
                channel = await self.get_auction_channel(guild)
                if not channel:
                    continue
                
                # Create closing embed
                if auction.current_bidder_id:
                    winner = guild.get_member(auction.current_bidder_id)
                    winner_name = winner.display_name if winner else "Unknown"
                    
                    embed = discord.Embed(
                        title=f"🎉 SOLD: {auction.title}",
                        description=f"**Winner:** {winner.mention if winner else winner_name}\n**Final Price:** ₹{auction.current_bid:,.2f}",
                        color=discord.Color.gold()
                    )
                    
                    embed.add_field(
                        name="📊 Auction Stats",
                        value=f"**Total Bids:** {len(auction.bid_history)}\n**Starting Price:** ₹{auction.starting_price:,.2f}",
                        inline=True
                    )
                    
                    seller = guild.get_member(auction.seller_id)
                    if seller:
                        embed.add_field(
                            name="📞 Next Steps",
                            value=f"Contact {seller.mention} to arrange payment and pickup!",
                            inline=False
                        )
                else:
                    embed = discord.Embed(
                        title=f"❌ Auction Closed: {auction.title}",
                        description="No bids were placed on this item.",
                        color=discord.Color.red()
                    )
                
                embed.set_footer(text=f"Auction #{auction.id} • Closed: {reason}")
                
                if auction.image_url:
                    embed.set_thumbnail(url=auction.image_url)
                
                await channel.send(embed=embed)
                
                # Try to update original message
                if auction.message_id:
                    try:
                        original_msg = await channel.fetch_message(auction.message_id)
                        await original_msg.edit(embed=await self.create_auction_embed(auction, guild))
                    except:
                        pass
                
                logger.info(f"Auction #{auction.id} closed: {reason}")
                break
                
        except Exception as e:
            logger.error(f"Error closing auction: {e}")
    
    async def create_auction_embed(self, auction: AuctionItem, guild: discord.Guild) -> discord.Embed:
        """Create embed for auction listing"""
        
        # Status colors
        colors = {
            "active": discord.Color.green(),
            "sold": discord.Color.gold(),
            "closed": discord.Color.red(),
            "expired": discord.Color.dark_gray()
        }
        
        status_emoji = {
            "active": "🟢",
            "sold": "🎉",
            "closed": "❌",
            "expired": "⏰"
        }
        
        embed = discord.Embed(
            title=f"{status_emoji.get(auction.status, '📦')} {auction.title}",
            description=auction.description,
            color=colors.get(auction.status, discord.Color.blue())
        )
        
        # Price info
        if auction.status == "active":
            current_price = auction.current_bid if auction.current_bid > 0 else auction.starting_price
            embed.add_field(
                name="💰 Current Price",
                value=f"**₹{current_price:,.2f}**",
                inline=True
            )
            
            if auction.buy_now_price:
                embed.add_field(
                    name="⚡ Buy Now",
                    value=f"**₹{auction.buy_now_price:,.2f}**",
                    inline=True
                )
        else:
            embed.add_field(
                name="💰 Final Price",
                value=f"**₹{auction.current_bid:,.2f}**" if auction.current_bid > 0 else "No bids",
                inline=True
            )
        
        # Item details
        embed.add_field(
            name="📋 Details",
            value=f"**Category:** {auction.category}\n**Condition:** {auction.condition}",
            inline=True
        )
        
        # Bid info
        if auction.current_bidder_id and auction.status == "active":
            bidder = guild.get_member(auction.current_bidder_id)
            bidder_name = bidder.display_name if bidder else "Unknown"
            embed.add_field(
                name="🏆 Leading Bidder",
                value=f"**{bidder_name}**",
                inline=True
            )
        
        # Time remaining
        if auction.ends_at and auction.status == "active":
            end_time = datetime.fromisoformat(auction.ends_at)
            embed.add_field(
                name="⏰ Ends",
                value=f"<t:{int(end_time.timestamp())}:R>",
                inline=True
            )
        
        # Seller info
        seller = guild.get_member(auction.seller_id)
        if seller:
            embed.set_author(
                name=f"Listed by {seller.display_name}",
                icon_url=seller.avatar.url if seller.avatar else None
            )
        
        # Image
        if auction.image_url:
            embed.set_image(url=auction.image_url)
        
        # Footer
        embed.set_footer(text=f"Auction #{auction.id} • {len(auction.bid_history)} bid(s)")
        
        return embed

    
    # ==================== COMMANDS ====================
    
    @app_commands.command(name="auction_create", description="[ADMIN] Create a new auction listing")
    @app_commands.describe(
        title="Item title",
        description="Item description",
        starting_price="Starting bid price in ₹",
        category="Item category",
        condition="Item condition",
        duration_hours="Auction duration in hours (default: 72)",
        buy_now_price="Optional instant buy price",
        image_url="Optional image URL"
    )
    async def auction_create(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        starting_price: float,
        category: str = "Electronics",
        condition: str = "Used - Good",
        duration_hours: int = 72,
        buy_now_price: float = None,
        image_url: str = None
    ):
        """Create a new auction listing"""
        
        if not self.is_admin(interaction.user):
            await interaction.response.send_message(
                "❌ Only admins can create auction listings.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            # Create auction item
            auction = AuctionItem({
                "id": self.next_id,
                "title": title,
                "description": description,
                "image_url": image_url,
                "starting_price": starting_price,
                "buy_now_price": buy_now_price,
                "current_bid": 0,
                "current_bidder_id": None,
                "seller_id": interaction.user.id,
                "created_at": datetime.now().isoformat(),
                "ends_at": (datetime.now() + timedelta(hours=duration_hours)).isoformat(),
                "status": "active",
                "bid_history": [],
                "category": category,
                "condition": condition
            })
            
            self.next_id += 1
            
            # Get auction channel
            channel = await self.get_auction_channel(interaction.guild)
            if not channel:
                await interaction.followup.send(
                    "❌ No auction channel found. Create a channel with 'auction' in the name.",
                    ephemeral=True
                )
                return
            
            # Create and send embed
            embed = await self.create_auction_embed(auction, interaction.guild)
            
            # Add bidding instructions
            embed.add_field(
                name="📝 How to Bid",
                value=f"Use `/bid {auction.id} <amount>` to place a bid!\nMinimum bid: **₹{starting_price:,.2f}**",
                inline=False
            )
            
            if buy_now_price:
                embed.add_field(
                    name="⚡ Instant Buy",
                    value=f"Use `/buy_now {auction.id}` to buy instantly for **₹{buy_now_price:,.2f}**",
                    inline=False
                )
            
            # Send to auction channel
            msg = await channel.send(embed=embed)
            
            # Store message ID for updates
            auction.message_id = msg.id
            auction.channel_id = channel.id
            
            # Save auction
            self.auctions[auction.id] = auction
            self.save_auctions()
            
            # Confirm to admin
            confirm_embed = discord.Embed(
                title="✅ Auction Created!",
                description=f"**{title}** is now listed in {channel.mention}",
                color=discord.Color.green()
            )
            confirm_embed.add_field(name="Auction ID", value=f"#{auction.id}", inline=True)
            confirm_embed.add_field(name="Starting Price", value=f"₹{starting_price:,.2f}", inline=True)
            confirm_embed.add_field(name="Duration", value=f"{duration_hours} hours", inline=True)
            
            await interaction.followup.send(embed=confirm_embed)
            logger.info(f"Auction #{auction.id} created: {title}")
            
        except Exception as e:
            logger.error(f"Error creating auction: {e}")
            await interaction.followup.send(
                f"❌ Error creating auction: {str(e)[:100]}",
                ephemeral=True
            )
    
    @auction_create.autocomplete('category')
    async def category_autocomplete(self, interaction: discord.Interaction, current: str):
        categories = [
            "Electronics", "Motors", "Sensors", "Controllers", "Batteries",
            "Mechanical Parts", "3D Printed", "Tools", "Cables & Wires",
            "Displays", "Cameras", "Wheels & Chassis", "Other"
        ]
        return [
            app_commands.Choice(name=cat, value=cat)
            for cat in categories if current.lower() in cat.lower()
        ][:25]
    
    @auction_create.autocomplete('condition')
    async def condition_autocomplete(self, interaction: discord.Interaction, current: str):
        conditions = [
            "New - Sealed", "New - Open Box", "Used - Like New",
            "Used - Good", "Used - Fair", "For Parts/Repair"
        ]
        return [
            app_commands.Choice(name=cond, value=cond)
            for cond in conditions if current.lower() in cond.lower()
        ][:25]

    
    @app_commands.command(name="bid", description="Place a bid on an auction item")
    @app_commands.describe(
        auction_id="The auction ID number",
        amount="Your bid amount in ₹"
    )
    async def place_bid(
        self,
        interaction: discord.Interaction,
        auction_id: int,
        amount: float
    ):
        """Place a bid on an auction"""
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Find auction
            auction = self.auctions.get(auction_id)
            
            if not auction:
                await interaction.followup.send(
                    f"❌ Auction #{auction_id} not found.",
                    ephemeral=True
                )
                return
            
            if auction.status != "active":
                await interaction.followup.send(
                    f"❌ This auction is no longer active (Status: {auction.status}).",
                    ephemeral=True
                )
                return
            
            # Check if bidding on own item
            if auction.seller_id == interaction.user.id:
                await interaction.followup.send(
                    "❌ You can't bid on your own item!",
                    ephemeral=True
                )
                return
            
            # Calculate minimum bid
            min_bid = auction.current_bid + 10 if auction.current_bid > 0 else auction.starting_price
            
            if amount < min_bid:
                await interaction.followup.send(
                    f"❌ Bid too low! Minimum bid is **₹{min_bid:,.2f}**",
                    ephemeral=True
                )
                return
            
            # Record bid
            old_bidder_id = auction.current_bidder_id
            
            auction.current_bid = amount
            auction.current_bidder_id = interaction.user.id
            auction.bid_history.append({
                "user_id": interaction.user.id,
                "amount": amount,
                "time": datetime.now().isoformat()
            })
            
            self.save_auctions()
            
            # Update auction message
            channel = interaction.guild.get_channel(auction.channel_id)
            if channel and auction.message_id:
                try:
                    msg = await channel.fetch_message(auction.message_id)
                    embed = await self.create_auction_embed(auction, interaction.guild)
                    embed.add_field(
                        name="📝 How to Bid",
                        value=f"Use `/bid {auction.id} <amount>` to place a bid!\nMinimum bid: **₹{amount + 10:,.2f}**",
                        inline=False
                    )
                    await msg.edit(embed=embed)
                except:
                    pass
            
            # Notify in auction channel
            if channel:
                bid_embed = discord.Embed(
                    title="🔔 New Bid!",
                    description=f"**{interaction.user.display_name}** bid **₹{amount:,.2f}** on **{auction.title}**",
                    color=discord.Color.blue()
                )
                bid_embed.set_footer(text=f"Auction #{auction.id}")
                await channel.send(embed=bid_embed, delete_after=60)
            
            # Notify outbid user
            if old_bidder_id and old_bidder_id != interaction.user.id:
                old_bidder = interaction.guild.get_member(old_bidder_id)
                if old_bidder:
                    try:
                        outbid_embed = discord.Embed(
                            title="⚠️ You've Been Outbid!",
                            description=f"Someone bid **₹{amount:,.2f}** on **{auction.title}**",
                            color=discord.Color.orange()
                        )
                        outbid_embed.add_field(
                            name="🔄 Place a Higher Bid",
                            value=f"Use `/bid {auction.id} <amount>` to bid again!",
                            inline=False
                        )
                        await old_bidder.send(embed=outbid_embed)
                    except:
                        pass  # DMs might be disabled
            
            # Confirm to bidder
            await interaction.followup.send(
                f"✅ Bid placed! You're now the leading bidder on **{auction.title}** at **₹{amount:,.2f}**",
                ephemeral=True
            )
            
            logger.info(f"Bid placed on auction #{auction_id}: ₹{amount} by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error placing bid: {e}")
            await interaction.followup.send(
                f"❌ Error placing bid: {str(e)[:100]}",
                ephemeral=True
            )
    
    @app_commands.command(name="buy_now", description="Instantly buy an auction item")
    @app_commands.describe(auction_id="The auction ID number")
    async def buy_now(self, interaction: discord.Interaction, auction_id: int):
        """Instantly buy an item at the buy now price"""
        
        await interaction.response.defer()
        
        try:
            auction = self.auctions.get(auction_id)
            
            if not auction:
                await interaction.followup.send(f"❌ Auction #{auction_id} not found.", ephemeral=True)
                return
            
            if auction.status != "active":
                await interaction.followup.send(f"❌ This auction is no longer active.", ephemeral=True)
                return
            
            if not auction.buy_now_price:
                await interaction.followup.send("❌ This item doesn't have a Buy Now option.", ephemeral=True)
                return
            
            if auction.seller_id == interaction.user.id:
                await interaction.followup.send("❌ You can't buy your own item!", ephemeral=True)
                return
            
            # Process instant buy
            auction.current_bid = auction.buy_now_price
            auction.current_bidder_id = interaction.user.id
            auction.bid_history.append({
                "user_id": interaction.user.id,
                "amount": auction.buy_now_price,
                "time": datetime.now().isoformat(),
                "type": "buy_now"
            })
            
            await self.close_auction(auction, "buy_now")
            
            await interaction.followup.send(
                f"🎉 Congratulations! You bought **{auction.title}** for **₹{auction.buy_now_price:,.2f}**!"
            )
            
        except Exception as e:
            logger.error(f"Error in buy_now: {e}")
            await interaction.followup.send(f"❌ Error: {str(e)[:100]}", ephemeral=True)

    
    @app_commands.command(name="auction_list", description="View all active auctions")
    async def auction_list(self, interaction: discord.Interaction):
        """List all active auctions"""
        
        await interaction.response.defer()
        
        try:
            active_auctions = [a for a in self.auctions.values() if a.status == "active"]
            
            if not active_auctions:
                embed = discord.Embed(
                    title="📦 No Active Auctions",
                    description="There are no items currently up for auction.\nCheck back later or ask an admin to list something!",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"🏪 Active Auctions ({len(active_auctions)})",
                color=discord.Color.blue()
            )
            
            for auction in active_auctions[:10]:  # Limit to 10
                current_price = auction.current_bid if auction.current_bid > 0 else auction.starting_price
                
                # Time remaining
                end_time = datetime.fromisoformat(auction.ends_at)
                time_left = f"<t:{int(end_time.timestamp())}:R>"
                
                value = f"💰 **₹{current_price:,.2f}** • {len(auction.bid_history)} bids\n⏰ Ends {time_left}"
                
                if auction.buy_now_price:
                    value += f"\n⚡ Buy Now: **₹{auction.buy_now_price:,.2f}**"
                
                embed.add_field(
                    name=f"#{auction.id} {auction.title}",
                    value=value,
                    inline=False
                )
            
            embed.add_field(
                name="📝 Commands",
                value="`/bid <id> <amount>` - Place a bid\n`/buy_now <id>` - Instant purchase\n`/auction_view <id>` - View details",
                inline=False
            )
            
            if len(active_auctions) > 10:
                embed.set_footer(text=f"Showing 10 of {len(active_auctions)} auctions")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing auctions: {e}")
            await interaction.followup.send("❌ Error loading auctions.", ephemeral=True)
    
    @app_commands.command(name="auction_view", description="View details of a specific auction")
    @app_commands.describe(auction_id="The auction ID number")
    async def auction_view(self, interaction: discord.Interaction, auction_id: int):
        """View detailed auction information"""
        
        await interaction.response.defer()
        
        try:
            auction = self.auctions.get(auction_id)
            
            if not auction:
                await interaction.followup.send(f"❌ Auction #{auction_id} not found.", ephemeral=True)
                return
            
            embed = await self.create_auction_embed(auction, interaction.guild)
            
            # Add bid history
            if auction.bid_history:
                recent_bids = auction.bid_history[-5:]  # Last 5 bids
                bid_text = []
                for bid in reversed(recent_bids):
                    bidder = interaction.guild.get_member(bid["user_id"])
                    bidder_name = bidder.display_name if bidder else "Unknown"
                    bid_time = datetime.fromisoformat(bid["time"])
                    bid_text.append(f"**₹{bid['amount']:,.2f}** by {bidder_name}")
                
                embed.add_field(
                    name="📊 Recent Bids",
                    value="\n".join(bid_text) or "No bids yet",
                    inline=False
                )
            
            if auction.status == "active":
                min_bid = auction.current_bid + 10 if auction.current_bid > 0 else auction.starting_price
                embed.add_field(
                    name="📝 How to Bid",
                    value=f"Use `/bid {auction.id} <amount>`\nMinimum: **₹{min_bid:,.2f}**",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error viewing auction: {e}")
            await interaction.followup.send("❌ Error loading auction.", ephemeral=True)
    
    @app_commands.command(name="my_bids", description="View your active bids")
    async def my_bids(self, interaction: discord.Interaction):
        """View your current bids"""
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            user_bids = []
            
            for auction in self.auctions.values():
                if auction.status != "active":
                    continue
                
                # Check if user has bid on this auction
                user_bid = None
                for bid in reversed(auction.bid_history):
                    if bid["user_id"] == interaction.user.id:
                        user_bid = bid
                        break
                
                if user_bid:
                    is_winning = auction.current_bidder_id == interaction.user.id
                    user_bids.append((auction, user_bid, is_winning))
            
            if not user_bids:
                embed = discord.Embed(
                    title="📋 Your Bids",
                    description="You haven't placed any bids yet!\nUse `/auction_list` to see available items.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"📋 Your Bids ({len(user_bids)})",
                color=discord.Color.blue()
            )
            
            for auction, bid, is_winning in user_bids:
                status = "🏆 **WINNING**" if is_winning else "❌ Outbid"
                current_price = auction.current_bid if auction.current_bid > 0 else auction.starting_price
                
                embed.add_field(
                    name=f"#{auction.id} {auction.title}",
                    value=f"{status}\nYour bid: **₹{bid['amount']:,.2f}**\nCurrent: **₹{current_price:,.2f}**",
                    inline=True
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in my_bids: {e}")
            await interaction.followup.send("❌ Error loading your bids.", ephemeral=True)

    
    @app_commands.command(name="auction_close", description="[ADMIN] Close an auction early")
    @app_commands.describe(auction_id="The auction ID to close")
    async def auction_close(self, interaction: discord.Interaction, auction_id: int):
        """Close an auction early"""
        
        if not self.is_admin(interaction.user):
            await interaction.response.send_message("❌ Only admins can close auctions.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            auction = self.auctions.get(auction_id)
            
            if not auction:
                await interaction.followup.send(f"❌ Auction #{auction_id} not found.", ephemeral=True)
                return
            
            if auction.status != "active":
                await interaction.followup.send(f"❌ Auction is already {auction.status}.", ephemeral=True)
                return
            
            await self.close_auction(auction, "admin_closed")
            
            await interaction.followup.send(f"✅ Auction #{auction_id} has been closed.")
            
        except Exception as e:
            logger.error(f"Error closing auction: {e}")
            await interaction.followup.send("❌ Error closing auction.", ephemeral=True)
    
    @app_commands.command(name="auction_delete", description="[ADMIN] Delete an auction listing")
    @app_commands.describe(auction_id="The auction ID to delete")
    async def auction_delete(self, interaction: discord.Interaction, auction_id: int):
        """Delete an auction completely"""
        
        if not self.is_admin(interaction.user):
            await interaction.response.send_message("❌ Only admins can delete auctions.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            auction = self.auctions.get(auction_id)
            
            if not auction:
                await interaction.followup.send(f"❌ Auction #{auction_id} not found.", ephemeral=True)
                return
            
            # Delete the auction message if it exists
            if auction.message_id and auction.channel_id:
                try:
                    channel = interaction.guild.get_channel(auction.channel_id)
                    if channel:
                        msg = await channel.fetch_message(auction.message_id)
                        await msg.delete()
                except:
                    pass
            
            # Remove from auctions
            del self.auctions[auction_id]
            self.save_auctions()
            
            await interaction.followup.send(f"✅ Auction #{auction_id} ({auction.title}) has been deleted.")
            logger.info(f"Auction #{auction_id} deleted by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error deleting auction: {e}")
            await interaction.followup.send("❌ Error deleting auction.", ephemeral=True)
    
    @app_commands.command(name="set_auction_channel", description="[ADMIN] Set the auction channel")
    @app_commands.describe(channel="The channel for auction listings")
    async def set_auction_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set the auction channel"""
        
        if not self.is_admin(interaction.user):
            await interaction.response.send_message("❌ Only admins can set the auction channel.", ephemeral=True)
            return
        
        self.auction_channel_id = channel.id
        self.save_auctions()
        
        embed = discord.Embed(
            title="✅ Auction Channel Set",
            description=f"Auction listings will now be posted in {channel.mention}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"Auction channel set to {channel.name}")


async def setup(bot):
    """Setup function to add the cog to the bot"""
    await bot.add_cog(AuctionSystem(bot))
    logger.info("Auction system cog loaded")