"""
help.py - Command help untuk bot Discord

Modul ini berisi command help untuk menampilkan bantuan dan daftar perintah.
"""

import discord
from discord.ext import commands

from src.core.config import EMBED_COLORS, BOT_INFO
from src.core.database import db
from src.utils import log_command

class HelpCommand(commands.Cog):
    """Command help untuk menampilkan bantuan"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Dictionary definisi command
        self.command_desc = {
            "help": "Menampilkan daftar perintah yang tersedia atau informasi tentang perintah tertentu",
            "ping": "Memeriksa latensi bot dan waktu respons",
            "info": "Menampilkan informasi tentang bot",
            "stats": "Menampilkan statistik penggunaan bot (hanya admin)",
            "invite": "Mendapatkan link untuk mengundang bot ke server lain",
            "prefix": "Mengubah prefix command untuk server ini",
            "language": "Mengubah bahasa bot untuk server ini",
            "anime": "Mencari informasi anime",
            "waifu": "Mendapatkan gambar waifu acak",
            "imsakiyah": "Menampilkan jadwal imsakiyah"
        }
        
        # Dictionary penggunaan command
        self.command_usage = {
            "help": "help [command]",
            "prefix": "prefix <new_prefix>",
            "language": "language <id|en>",
            "anime": "anime <judul>",
            "waifu": "waifu [category]",
            "imsakiyah": "imsakiyah <kota>"
        }
    
    @commands.command(name="help", aliases=["bantuan", "h", "menu"])
    async def help(self, ctx, command_name=None):
        """Menampilkan daftar perintah yang tersedia"""
        prefix = db.get_prefix(ctx.guild.id if ctx.guild else None)
        
        if command_name:
            # Show help for specific command
            command = self.bot.get_command(command_name)
            if not command:
                embed = discord.Embed(
                    title="❌ Perintah Tidak Ditemukan",
                    description=f"Perintah `{command_name}` tidak ditemukan",
                    color=EMBED_COLORS["error"]
                )
                await ctx.send(embed=embed)
                return
            
            # Get command description
            if command.name in self.command_desc:
                desc = self.command_desc[command.name]
            else:
                desc = command.help or "Tidak ada deskripsi"
            
            # Create embed for command help
            embed = discord.Embed(
                title=f"Bantuan: {prefix}{command.name}",
                description=desc,
                color=EMBED_COLORS["primary"]
            )
            
            # Add usage if available
            usage = self.command_usage.get(command.name)
            if usage:
                embed.add_field(name="Penggunaan", value=f"`{prefix}{usage}`", inline=False)
            
            # Add aliases if available
            if command.aliases:
                aliases = ", ".join([f"`{prefix}{alias}`" for alias in command.aliases])
                embed.add_field(name="Alias", value=aliases, inline=False)
            
            await ctx.send(embed=embed)
        else:
            # Show general help menu
            embed = discord.Embed(
                title="📚 Menu Bantuan", 
                description=f"Berikut adalah daftar perintah yang tersedia. Gunakan `{prefix}help <perintah>` untuk info lebih lanjut.", 
                color=EMBED_COLORS["primary"]
            )
            
            # Get all command categories
            categories = {
                "Umum": ["help", "ping", "info", "stats", "invite"],
                "Setelan": ["prefix", "language"],
                "Anime": ["anime", "waifu"],
                "Islami": ["imsakiyah"]
            }
            
            # Add fields for each category
            for category, cmds in categories.items():
                # Filter commands that exist
                valid_cmds = []
                for cmd_name in cmds:
                    cmd = self.bot.get_command(cmd_name)
                    if cmd:
                        valid_cmds.append(f"`{prefix}{cmd_name}`")
                
                if valid_cmds:
                    embed.add_field(
                        name=f"⚙️ {category}",
                        value=" • ".join(valid_cmds),
                        inline=False
                    )
            
            # Add footer with bot info
            embed.set_footer(
                text=f"Requested by {ctx.author.name} • {BOT_INFO['name']} v{BOT_INFO['version']}", 
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None
            )
            
            await ctx.send(embed=embed)
        
        # Log command usage
        log_command(ctx.author.id, ctx.guild.id if ctx.guild else None, "help")

def setup(bot):
    """Adds the HelpCommand cog to the bot."""
    bot.add_cog(HelpCommand(bot)) 