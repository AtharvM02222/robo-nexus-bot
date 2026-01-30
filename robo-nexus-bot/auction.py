"""
Robo Nexus Auction System - PostgreSQL ONLY
ALL DATA FROM REPLIT DATABASE
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
import requests
from datetime import datetime
from typing import Optional
from supabase_api import get_supabase_api

logger = logging.getLogger(__name__)

class AuctionSystem(commands.Cog):
    """Auction system - PostgreSQL only"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = get_supabase_api()
        logger.info("Auction system initialized with PostgreSQL")
    
    def is_admin(self, member: discord.Member) -> bool:
        """Check if user has admin permissions"""
        return member.guild_permissions.administrator or member.guild_permissions.manage_guild
    
    async def get_auction_channel(self):
        """Get the auction channel from database"""
        channel_id = self.db.get_setting('auction_channel_id')
        if channel_id:
            return self.bot.get_channel(int(channel_id))
        return None
    
    @app_commands.command(name="auction_create", description="Create a new auction listing")
    @app_commands.describe(
        product_name="Name of the product you're selling",
        starting_price="Starting bid price (₹)",
        description="Detailed description of the product",
        category="Product category",
        condition="Product condition",
        buy_now_price="Optional instant buy price (₹)",
        image_url="Optional image URL"
    )
    async def auction_create(
        self,
        interaction: discord.Interaction,
        product_name: str,
        starting_price: float,
        description: str = "",
        category: str = "Other",
        condition: str = "Used - Good",
        buy_now_price: Optional[float] = None,
        image_url: Optional[str] = None
    ):
        """Create a new auction"""
        try:
            if starting_price <= 0:
                await interaction.response.send_message("❌ Starting price must be greater than 0!", ephemeral=True)
                return
            
            if buy_now_price and buy_now_price <= starting_price:
                await interaction.response.send_message("❌ Buy now price must be higher than starting price!", ephemeral=True)
                return
            
            auction_data = {
                'seller_id': str(interaction.user.id),
                'seller_name': interaction.user.display_name,
                'product_name': product_name,
                'description': description,
                'starting_price': starting_price,
                'current_price': starting_price,
                'buy_now_price': buy_now_price,
                'category': category,
                'condition': condition,
                'image_url': image_url,
                'duration': 'forever',
                'end_time': None
            }
            
            auction_id = self.db.create_auction(auction_data)
            
            embed = discord.Embed(
                title="✅ Auction Created!",
                description=f"**{product_name}** is now listed",
                color=0x00ff00
            )
            embed.add_field(name="Auction ID", value=f"#{auction_id}", inline=True)
            embed.add_field(name="Starting Price", value=f"₹{starting_price:,.2f}", inline=True)
            
            await interaction.response.send_message(embed=embed)
            await self.post_auction_listing(auction_id)
            
            logger.info(f"Auction #{auction_id} created: {product_name}")
            
        except Exception as e:
            logger.error(f"Error creating auction: {e}")
            await interaction.response.send_message("❌ Failed to create auction.", ephemeral=True)
    
    async def post_auction_listing(self, auction_id: int):
        """Post auction in channel"""
        try:
            auction = self.db.get_auction(auction_id)
            if not auction:
                return
            
            channel = await self.get_auction_channel()
            if not channel:
                return
            
            embed = discord.Embed(
                title=f"🟢 {auction['product_name']}",
                description=auction['description'] or "No description",
                color=0x00ff00
            )
            
            embed.add_field(name="💰 Current Price", value=f"₹{auction['current_price']:,.2f}", inline=True)
            if auction['buy_now_price']:
                embed.add_field(name="⚡ Buy Now", value=f"₹{auction['buy_now_price']:,.2f}", inline=True)
            embed.add_field(name="📋 Details", value=f"**Category:** {auction['category']}\n**Condition:** {auction['condition']}", inline=True)
            
            embed.add_field(
                name="📝 How to Bid",
                value=f"Use `/bid {auction_id} <amount>` to place a bid!",
                inline=False
            )
            
            if auction['image_url']:
                embed.set_image(url=auction['image_url'])
            
            bids = self.db.get_auction_bids(auction_id)
            embed.set_footer(text=f"Listed by {auction['seller_name']} • Auction #{auction_id} • {len(bids)} bid(s)")
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error posting auction: {e}")
    
    @app_commands.command(name="auction_list", description="View all active auctions")
    async def auction_list(self, interaction: discord.Interaction):
        """List all active auctions from PostgreSQL"""
        try:
            await interaction.response.defer()
            
            # Get auctions from PostgreSQL database
            auctions = self.db.get_all_auctions('active')
            
            logger.info(f"Found {len(auctions)} active auctions in database")
            
            if not auctions:
                embed = discord.Embed(
                    title="📋 Active Auctions",
                    description="No active auctions found.",
                    color=0x808080
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="📋 Active Auctions",
                description=f"Found {len(auctions)} active auction(s)",
                color=0x0099ff
            )
            
            for auction in auctions[:10]:
                bids = self.db.get_auction_bids(auction['id'])
                
                embed.add_field(
                    name=f"#{auction['id']} - {auction['product_name']}",
                    value=f"💰 ₹{auction['current_price']:,.2f} • 🏷️ {auction['category']} • 📊 {len(bids)} bid(s)",
                    inline=False
                )
            
            if len(auctions) > 10:
                embed.set_footer(text=f"Showing first 10 of {len(auctions)} auctions")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing auctions: {e}", exc_info=True)
            try:
                await interaction.followup.send("❌ Failed to load auctions.", ephemeral=True)
            except:
                pass
    
    @app_commands.command(name="auction_view", description="View auction details")
    @app_commands.describe(auction_id="ID of the auction")
    async def auction_view(self, interaction: discord.Interaction, auction_id: int):
        """View detailed auction information"""
        try:
            auction = self.db.get_auction(auction_id)
            if not auction:
                await interaction.response.send_message("❌ Auction not found!", ephemeral=True)
                return
            
            bids = self.db.get_auction_bids(auction_id)
            
            embed = discord.Embed(
                title=f"🔍 Auction #{auction_id} - {auction['product_name']}",
                description=auction['description'] or "No description",
                color=0x0099ff
            )
            
            embed.add_field(name="💰 Current Price", value=f"₹{auction['current_price']:,.2f}", inline=True)
            if auction['buy_now_price']:
                embed.add_field(name="⚡ Buy Now", value=f"₹{auction['buy_now_price']:,.2f}", inline=True)
            embed.add_field(name="📊 Total Bids", value=str(len(bids)), inline=True)
            
            embed.add_field(name="🏷️ Category", value=auction['category'], inline=True)
            embed.add_field(name="🔧 Condition", value=auction['condition'], inline=True)
            embed.add_field(name="👤 Seller", value=auction['seller_name'], inline=True)
            
            if bids:
                recent_bids = bids[:5]
                bid_text = "\n".join([
                    f"₹{bid['amount']:,.2f} by {bid['bidder_name']}"
                    for bid in recent_bids
                ])
                embed.add_field(name="📈 Recent Bids", value=bid_text, inline=False)
            
            if auction['image_url']:
                embed.set_image(url=auction['image_url'])
            
            embed.set_footer(text=f"Created: {auction['created_at'].strftime('%Y-%m-%d %H:%M')}")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error viewing auction: {e}")
            await interaction.response.send_message("❌ Failed to load auction.", ephemeral=True)
    
    @app_commands.command(name="bid", description="Place a bid on an auction")
    @app_commands.describe(
        auction_id="ID of the auction",
        amount="Your bid amount (₹)"
    )
    async def bid(self, interaction: discord.Interaction, auction_id: int, amount: float):
        """Place a bid"""
        try:
            auction = self.db.get_auction(auction_id)
            if not auction:
                await interaction.response.send_message("❌ Auction not found!", ephemeral=True)
                return
            
            if auction['status'] != 'active':
                await interaction.response.send_message("❌ Auction is not active!", ephemeral=True)
                return
            
            if str(interaction.user.id) == auction['seller_id']:
                await interaction.response.send_message("❌ You cannot bid on your own auction!", ephemeral=True)
                return
            
            if amount <= auction['current_price']:
                await interaction.response.send_message(
                    f"❌ Bid must be higher than ₹{auction['current_price']:,.2f}!",
                    ephemeral=True
                )
                return
            
            success = self.db.place_bid(
                auction_id,
                str(interaction.user.id),
                interaction.user.display_name,
                amount
            )
            
            if success:
                embed = discord.Embed(
                    title="✅ Bid Placed!",
                    description=f"Your bid of ₹{amount:,.2f} on **{auction['product_name']}** has been placed!",
                    color=0x00ff00
                )
                embed.add_field(name="Auction ID", value=f"#{auction_id}", inline=True)
                embed.add_field(name="Your Bid", value=f"₹{amount:,.2f}", inline=True)
                
                await interaction.response.send_message(embed=embed)
                logger.info(f"Bid placed: ₹{amount} on auction #{auction_id}")
            else:
                await interaction.response.send_message("❌ Failed to place bid.", ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error placing bid: {e}")
            await interaction.response.send_message("❌ Failed to place bid.", ephemeral=True)
    
    @app_commands.command(name="buy_now", description="Instantly buy an auction item")
    @app_commands.describe(auction_id="The auction ID")
    async def buy_now(self, interaction: discord.Interaction, auction_id: int):
        """Instant purchase"""
        try:
            auction = self.db.get_auction(auction_id)
            if not auction:
                await interaction.response.send_message("❌ Auction not found!", ephemeral=True)
                return
            
            if auction['status'] != 'active':
                await interaction.response.send_message("❌ Auction is not active!", ephemeral=True)
                return
            
            if not auction['buy_now_price']:
                await interaction.response.send_message("❌ No Buy Now option available.", ephemeral=True)
                return
            
            if str(interaction.user.id) == auction['seller_id']:
                await interaction.response.send_message("❌ You can't buy your own item!", ephemeral=True)
                return
            
            success = self.db.place_bid(
                auction_id,
                str(interaction.user.id),
                interaction.user.display_name,
                auction['buy_now_price']
            )
            
            if success:
                # Update auction status to sold using Supabase API
                try:
                    # Get current auction data
                    auction = self.db.get_auction(auction_id)
                    if auction:
                        # Update status to sold
                        update_response = requests.patch(
                            f"{self.db.url}/rest/v1/auctions?id=eq.{auction_id}",
                            headers=self.db.headers,
                            json={"status": "sold"},
                            timeout=10
                        )
                        
                        if update_response.status_code == 200:
                            await interaction.response.send_message(
                                f"🎉 You bought **{auction['product_name']}** for ₹{auction['buy_now_price']:,.2f}!"
                            )
                            logger.info(f"Buy now: Auction #{auction_id} sold for ₹{auction['buy_now_price']}")
                        else:
                            logger.error(f"Failed to update auction status: {update_response.status_code}")
                            await interaction.response.send_message(
                                f"🎉 You bought **{auction['product_name']}** for ₹{auction['buy_now_price']:,.2f}! (Status update pending)"
                            )
                    else:
                        await interaction.response.send_message("❌ Auction not found after purchase.", ephemeral=True)
                except Exception as e:
                    logger.error(f"Error updating auction status: {e}")
                    await interaction.response.send_message(
                        f"🎉 Purchase successful, but there was an issue updating the auction status."
                    )
            else:
                await interaction.response.send_message("❌ Failed to complete purchase.", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error in buy_now: {e}")
            await interaction.response.send_message("❌ Error completing purchase.", ephemeral=True)
    
    @app_commands.command(name="my_auctions", description="View your active auctions")
    async def my_auctions(self, interaction: discord.Interaction):
        """View your auctions"""
        try:
            all_auctions = self.db.get_all_auctions('active')
            user_auctions = [a for a in all_auctions if a['seller_id'] == str(interaction.user.id)]
            
            if not user_auctions:
                embed = discord.Embed(
                    title="📋 Your Auctions",
                    description="You don't have any active auctions.",
                    color=0x808080
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"📋 Your Active Auctions ({len(user_auctions)})",
                color=0x0099ff
            )
            
            for auction in user_auctions:
                bids = self.db.get_auction_bids(auction['id'])
                embed.add_field(
                    name=f"#{auction['id']} - {auction['product_name']}",
                    value=f"💰 ₹{auction['current_price']:,.2f} • 📊 {len(bids)} bid(s)",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error getting user auctions: {e}")
            await interaction.response.send_message("❌ Failed to load your auctions.", ephemeral=True)
    
    @app_commands.command(name="my_bids", description="View your active bids")
    async def my_bids(self, interaction: discord.Interaction):
        """View your bids"""
        try:
            all_auctions = self.db.get_all_auctions('active')
            user_bids = []
            
            for auction in all_auctions:
                bids = self.db.get_auction_bids(auction['id'])
                user_bid = None
                for bid in bids:
                    if bid['bidder_id'] == str(interaction.user.id):
                        user_bid = bid
                
                if user_bid:
                    is_winning = bids[0]['bidder_id'] == str(interaction.user.id) if bids else False
                    user_bids.append((auction, user_bid, is_winning))
            
            if not user_bids:
                embed = discord.Embed(
                    title="📋 Your Bids",
                    description="You haven't placed any bids yet!",
                    color=0x808080
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"📋 Your Bids ({len(user_bids)})",
                color=0x0099ff
            )
            
            for auction, bid, is_winning in user_bids:
                status = "🏆 WINNING" if is_winning else "❌ Outbid"
                embed.add_field(
                    name=f"#{auction['id']} {auction['product_name']}",
                    value=f"{status}\nYour bid: ₹{bid['amount']:,.2f}\nCurrent: ₹{auction['current_price']:,.2f}",
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in my_bids: {e}")
            await interaction.response.send_message("❌ Error loading your bids.", ephemeral=True)
    
    @app_commands.command(name="set_auction_channel", description="[ADMIN] Set the auction channel")
    @app_commands.describe(channel="The channel for auctions")
    async def set_auction_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set auction channel"""
        if not self.is_admin(interaction.user):
            await interaction.response.send_message("❌ Admin only.", ephemeral=True)
            return
        
        self.db.set_setting('auction_channel_id', str(channel.id))
        
        embed = discord.Embed(
            title="✅ Auction Channel Set",
            description=f"Auctions will be posted in {channel.mention}",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed)
        logger.info(f"Auction channel set to {channel.name}")

async def setup(bot):
    """Setup function"""
    await bot.add_cog(AuctionSystem(bot))
    logger.info("Auction system cog loaded - PostgreSQL only")
