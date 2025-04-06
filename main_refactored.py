"""
main_refactored.py - Entry point utama bot Discord

File ini merupakan entry point utama untuk bot Discord yang telah direfaktorisasi.
Menggunakan struktur modular dan best practices.
"""

import discord
from discord.ext import commands
import platform
import os
import sys
import asyncio
import signal
from dotenv import load_dotenv
import logging
import time
from datetime import datetime
import re

# Impor modul yang telah direfaktor
from memory_db import db
from utils import get_prefix, log_command, create_embed
from constants import EMBED_COLORS, BOT_INFO, COMMAND_DESCRIPTIONS

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    print("Error: DISCORD_TOKEN not found in .env file")
    print("Please add your Discord bot token to the .env file")
    sys.exit(1)

# Add signal handlers for graceful shutdown
def handle_exit(signum, frame):
    print(f"Received signal {signum}, shutting down gracefully...")
    # Perform cleanup if needed
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# Menentukan fungsi custom untuk mendapatkan prefix
def get_prefix_wrapper(bot, message):
    """Fungsi pembungkus untuk mendapatkan prefix command guild"""
    return get_prefix(bot, message)

# Inisialisasi bot dengan prefix kustom
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix_wrapper, intents=intents, help_command=None)

# Simpan waktu mulai bot untuk perhitungan uptime
bot.start_time = datetime.now()
bot.version = BOT_INFO.get('version', '1.0.0')

@bot.event
async def on_message(message):
    """Event yang dipanggil saat ada pesan baru"""
    # Ignore messages from any bot
    if message.author.bot:
        return
    
    # Process commands
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    """Event yang dipanggil saat ada error pada command"""
    if isinstance(error, commands.CommandNotFound):
        return
    
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Error",
            description=f"Argumen yang diperlukan tidak diberikan: `{error.param.name}`",
            color=EMBED_COLORS["error"]
        )
        await ctx.send(embed=embed)
        return
    
    if isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="❌ Error",
            description=f"Argumen tidak valid: {str(error)}",
            color=EMBED_COLORS["error"]
        )
        await ctx.send(embed=embed)
        return
    
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title="❌ Akses Ditolak",
            description="Anda tidak memiliki izin untuk menjalankan perintah ini.",
            color=EMBED_COLORS["error"]
        )
        await ctx.send(embed=embed)
        return
    
    # Log other errors
    print(f"Command error in {ctx.command}: {error}")
    embed = discord.Embed(
        title="❌ Error",
        description=f"Terjadi kesalahan saat menjalankan perintah: {str(error)}",
        color=EMBED_COLORS["error"]
    )
    await ctx.send(embed=embed)

# Perintah dasar
@bot.command(name="ping")
async def ping_command(ctx):
    """Menampilkan latensi bot"""
    start_time = time.time()
    message = await ctx.send("Pinging...")
    end_time = time.time()
    
    # Calculate round trip latency
    round_trip = (end_time - start_time) * 1000
    websocket_latency = bot.latency * 1000
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latensi Bot: `{websocket_latency:.2f}ms`\nRound Trip: `{round_trip:.2f}ms`",
        color=EMBED_COLORS["primary"]
    )
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    await message.edit(content=None, embed=embed)
    
    # Log command usage
    log_command(ctx.author.id, ctx.guild.id if ctx.guild else None, "ping")

@bot.command(name="help", aliases=["bantuan", "h", "menu"])
async def help_command(ctx, command_name=None):
    """Menampilkan daftar perintah yang tersedia"""
    prefix = get_prefix(bot, ctx.message)
    
    if command_name:
        # Show help for specific command
        command = bot.get_command(command_name)
        if not command:
            embed = discord.Embed(
                title="❌ Perintah Tidak Ditemukan",
                description=f"Perintah `{command_name}` tidak ditemukan",
                color=EMBED_COLORS["error"]
            )
            await ctx.send(embed=embed)
            return
        
        # Get command description
        if command.name in COMMAND_DESCRIPTIONS:
            desc = COMMAND_DESCRIPTIONS[command.name]
        else:
            desc = command.help or "Tidak ada deskripsi"
        
        # Create embed for command help
        embed = discord.Embed(
            title=f"Bantuan: {prefix}{command.name}",
            description=desc,
            color=EMBED_COLORS["primary"]
        )
        
        # Add usage if available
        usage = COMMAND_DESCRIPTIONS.get(f"{command.name}_usage")
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
            "Islami": ["imsakiyah", "imsak", "jadwal"]
        }
        
        # Add fields for each category
        for category, cmds in categories.items():
            # Filter commands that exist
            valid_cmds = []
            for cmd_name in cmds:
                cmd = bot.get_command(cmd_name)
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

@bot.command(name="info", aliases=["about", "tentang"])
async def info_command(ctx):
    """Menampilkan informasi tentang bot"""
    embed = discord.Embed(
        title=f"ℹ️ Tentang {bot.user.name}",
        description=BOT_INFO["description"],
        color=EMBED_COLORS["primary"]
    )
    
    # Add bot statistics
    embed.add_field(
        name="📊 Statistik",
        value=(
            f"🏘️ Server: `{len(bot.guilds)}`\n"
            f"👥 Pengguna: `{len(set(bot.get_all_members()))}`\n"
            f"⌛ Uptime: `{get_uptime_str()}`\n"
            f"🌐 Ping: `{bot.latency*1000:.2f}ms`"
        ),
        inline=True
    )
    
    # Add technical info
    embed.add_field(
        name="💻 Teknis",
        value=(
            f"🐍 Python: `{platform.python_version()}`\n"
            f"🤖 Discord.py: `{discord.__version__}`\n"
            f"💾 OS: `{platform.system()} {platform.release()}`\n"
            f"🔧 Versi: `{BOT_INFO['version']}`"
        ),
        inline=True
    )
    
    # Add author info
    embed.add_field(
        name="👨‍💻 Pembuat",
        value=BOT_INFO["author"],
        inline=False
    )
    
    # Set bot avatar as thumbnail
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    
    # Add footer
    embed.set_footer(
        text=f"Requested by {ctx.author.name}", 
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )
    
    await ctx.send(embed=embed)
    
    # Log command usage
    log_command(ctx.author.id, ctx.guild.id if ctx.guild else None, "info")

@bot.command(name="stats")
@commands.has_permissions(administrator=True)
async def stats_command(ctx):
    """Menampilkan statistik penggunaan bot (Admin only)"""
    from utils import get_command_stats
    
    # Get command usage statistics
    command_stats = get_command_stats()
    
    # Sort commands by usage (most used first)
    sorted_commands = sorted(command_stats.items(), key=lambda x: x[1], reverse=True)
    
    # Create embed
    embed = discord.Embed(
        title="📊 Statistik Penggunaan Bot",
        description="Berikut adalah statistik penggunaan perintah bot:",
        color=EMBED_COLORS["primary"]
    )
    
    # Add top commands
    if sorted_commands:
        command_list = "\n".join([f"`{cmd}`: {count} kali" for cmd, count in sorted_commands[:10]])
        embed.add_field(
            name="🔝 Perintah Terpopuler",
            value=command_list,
            inline=False
        )
    else:
        embed.add_field(
            name="🔝 Perintah Terpopuler",
            value="Belum ada data penggunaan perintah",
            inline=False
        )
    
    # Add general stats
    total_commands = sum(command_stats.values()) if command_stats else 0
    embed.add_field(
        name="🔢 Statistik Umum",
        value=(
            f"Total perintah digunakan: `{total_commands}`\n"
            f"Jumlah jenis perintah: `{len(command_stats)}`\n"
            f"Server aktif: `{len(bot.guilds)}`\n"
            f"Pengguna terjangkau: `{len(set(bot.get_all_members()))}`"
        ),
        inline=False
    )
    
    # Add footer
    embed.set_footer(
        text=f"Requested by {ctx.author.name}", 
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )
    
    await ctx.send(embed=embed)
    
    # Log command usage
    log_command(ctx.author.id, ctx.guild.id if ctx.guild else None, "stats")

@bot.command(name="invite")
async def invite_command(ctx):
    """Mendapatkan link invite bot ke server lain"""
    # Create an invite URL with the necessary permissions
    permissions = discord.Permissions(
        send_messages=True,
        embed_links=True,
        attach_files=True,
        read_messages=True,
        read_message_history=True,
        add_reactions=True,
        use_external_emojis=True,
        manage_messages=True  # For deleting reactions
    )
    
    invite_url = discord.utils.oauth_url(bot.user.id, permissions=permissions)
    
    embed = discord.Embed(
        title="🔗 Invite Bot",
        description=f"Gunakan link berikut untuk mengundang bot ke server Anda:",
        color=EMBED_COLORS["primary"]
    )
    
    embed.add_field(
        name="📨 Link Invite",
        value=f"[Klik di sini untuk invite]({invite_url})",
        inline=False
    )
    
    embed.set_footer(
        text=f"Requested by {ctx.author.name}",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )
    
    await ctx.send(embed=embed)
    
    # Log command usage
    log_command(ctx.author.id, ctx.guild.id if ctx.guild else None, "invite")

def get_uptime_str():
    """Mendapatkan string uptime yang readable"""
    now = datetime.now()
    delta = now - bot.start_time
    
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    else:
        return f"{minutes}m {seconds}s"

# Load external modules
def load_modules():
    """Load semua modul eksternal"""
    modules = [
        "rich_presence",  # Load Rich Presence module first
        "mal",            # Anime module
        "imsakiyah"       # Imsakiyah module
    ]
    
    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
            module.setup(bot)
            print(f"[INFO] {module_name} module loaded successfully")
        except Exception as e:
            print(f"[ERROR] Failed to load module {module_name}: {e}")

# Run the bot
if __name__ == "__main__":
    try:
        print(f"Starting bot: {BOT_INFO['name']} v{BOT_INFO['version']}...")
        
        # Load all modules
        load_modules()
        
        # Run the bot
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        print("Error: Invalid Discord token")
        sys.exit(1)
    except discord.errors.PrivilegedIntentsRequired:
        print("Error: Privileged intents are required but not enabled")
        print("Please enable the required intents in the Discord Developer Portal")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 