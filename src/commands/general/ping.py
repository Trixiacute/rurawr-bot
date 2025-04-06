"""
ping.py - Command ping untuk bot Discord

Modul ini berisi command ping untuk mengecek latensi bot.
"""

import time
import discord
from discord.ext import commands

from src.core.config import EMBED_COLORS
from src.utils import log_command

class Ping(commands.Cog):
    """Command ping untuk cek latensi bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="ping", aliases=["pong", "latency"])
    async def ping(self, ctx):
        """Menampilkan latensi bot"""
        start_time = time.time()
        message = await ctx.send("Pinging...")
        end_time = time.time()
        
        # Calculate round trip latency
        round_trip = (end_time - start_time) * 1000
        websocket_latency = self.bot.latency * 1000
        
        # Create embed response
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latensi Bot: `{websocket_latency:.2f}ms`\nRound Trip: `{round_trip:.2f}ms`",
            color=EMBED_COLORS["primary"]
        )
        
        # Add footer
        embed.set_footer(
            text=f"Requested by {ctx.author.name}", 
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        
        await message.edit(content=None, embed=embed)
        
        # Log command usage
        log_command(ctx.author.id, ctx.guild.id if ctx.guild else None, "ping")

def setup(bot):
    """Adds the Ping cog to the bot."""
    bot.add_cog(Ping(bot)) 