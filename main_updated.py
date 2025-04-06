import discord
from discord.ext import commands
import requests
import random
from datetime import datetime, timezone, timedelta
import platform
import os
import sys
import asyncio
import signal
from dotenv import load_dotenv
import logging
import pytz
import json
import re
import atexit
import importlib
import time

# Impor modul yang telah direfaktor
from memory_db import MemoryDB
from utils import get_lang, get_prefix, get_text, log_command, get_command_stats, get_timestamp, format_time_id, create_embed
from constants import WAIFU_API_URL, WAIFU_CATEGORIES, EMBED_COLORS, BOT_INFO, COMMAND_DESCRIPTIONS

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    print("Error: DISCORD_TOKEN not found in .env file")
    print("Please add your Discord bot token to the .env file")
    sys.exit(1)

# Inisialisasi MemoryDB
db = MemoryDB()

# Configure logging to prevent Korean characters from being displayed in terminal
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Filter to prevent non-ASCII characters in logs
class ASCIIFilter(logging.Filter):
    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = re.sub(r'[^\x00-\x7F]+', '[non-ASCII]', record.msg)
        return True

# Apply filter to root logger
root_logger = logging.getLogger()
root_logger.addFilter(ASCIIFilter())

# Add signal handlers for graceful shutdown
def handle_exit(signum, frame):
    print(f"Received signal {signum}, shutting down gracefully...")
    # Perform cleanup if needed
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# Menentukan fungsi custom untuk mendapatkan prefix
async def get_prefix_wrapper(bot, message):
    return get_prefix(message.guild.id if message.guild else None)

# Inisialisasi bot dengan prefix kustom
bot = commands.Bot(command_prefix=get_prefix_wrapper, intents=discord.Intents.all(), help_command=None)

# Event handlers
@bot.event
async def on_ready():
    """Event yang dipanggil saat bot siap digunakan"""
    print(f"\n{'='*50}")
    print(f"Bot is ready! Logged in as {bot.user.name} (ID: {bot.user.id})")
    print(f"Connected to {len(bot.guilds)} guilds | Serving {len(set(bot.get_all_members()))} users")
    print(f"Python version: {platform.python_version()}")
    print(f"Discord.py version: {discord.__version__}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print(f"{'='*50}\n")
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name="!help | Menyala kembali!"
        )
    )
    
    # Log startup in a file
    with open("bot_log.txt", "a", encoding="utf-8") as f:
        startup_msg = f"[{datetime.now()}] Bot started: {bot.user.name} (ID: {bot.user.id})"
        f.write(f"{startup_msg}\n")
    
    print("Bot is fully operational!")

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
    prefix = get_prefix(ctx.guild.id if ctx.guild else None)
    
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
            f"⌛ Uptime: `{get_timestamp()}`\n"
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

@bot.command(name="prefix")
@commands.has_permissions(manage_guild=True)
async def prefix_command(ctx, new_prefix=None):
    """Mengubah prefix bot (Admin only)"""
    if new_prefix is None:
        # Show current prefix
        current_prefix = get_prefix(ctx.guild.id if ctx.guild else None)
        embed = discord.Embed(
            title="⚙️ Prefix Saat Ini",
            description=f"Prefix saat ini: `{current_prefix}`",
            color=EMBED_COLORS["primary"]
        )
        embed.add_field(
            name="📝 Cara Mengubah",
            value=f"Gunakan `{current_prefix}prefix <new_prefix>` untuk mengubah prefix",
            inline=False
        )
import discord
from discord.ext import commands
import requests
import random
from datetime import datetime, timezone, timedelta
import platform
import os
import sys
import asyncio
import signal
from dotenv import load_dotenv
try:
    from constants import WAIFU_API_URL, WAIFU_CATEGORIES, EMBED_COLORS, BOT_INFO, COMMAND_DESCRIPTIONS
    from language import LANGUAGES
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all required files are present in the directory")
    sys.exit(1)
import time
from typing import Optional
import pytz  # For imsakiyah feature
import json  # For saving JSON data
import re  # For anime search regex
import atexit
import importlib.util

# Configure logging to prevent Korean characters from being displayed in terminal
import logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Filter to prevent non-ASCII characters in logs
class ASCIIFilter(logging.Filter):
    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = re.sub(r'[^\x00-\x7F]+', '[non-ASCII]', record.msg)
        return True

# Apply filter to root logger
root_logger = logging.getLogger()
root_logger.addFilter(ASCIIFilter())

# In-memory storage sebagai pengganti database
GUILD_SETTINGS = {
    # guild_id: {'language': 'id', 'prefix': '!'}
}
COMMAND_LOGS = []
USER_DATA = {}

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    print("Error: DISCORD_TOKEN not found in .env file")
    print("Please add your Discord bot token to the .env file")
    sys.exit(1)

# Menghapus kode terkait MongoDB/database

# Add signal handlers for graceful shutdown
def handle_exit(signum, frame):
    print(f"Received signal {signum}, shutting down gracefully...")
    # Perform cleanup if needed
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# Fungsi-fungsi pengganti database
def get_guild_language(guild_id):
    """Get language setting for a guild"""
    if guild_id is None:
        return "id"  # Default language for DMs
    
    if guild_id in GUILD_SETTINGS and 'language' in GUILD_SETTINGS[guild_id]:
        return GUILD_SETTINGS[guild_id]['language']
    return "id"  # Default language

def set_guild_language(guild_id, language):
    """Set language preference for a guild"""
    if guild_id not in GUILD_SETTINGS:
        GUILD_SETTINGS[guild_id] = {}
    GUILD_SETTINGS[guild_id]['language'] = language
    return True

def get_guild_prefix(guild_id):
    """Get command prefix for a guild"""
    if guild_id is None:
        return "!"  # Default prefix for DMs
    
    if guild_id in GUILD_SETTINGS and 'prefix' in GUILD_SETTINGS[guild_id]:
        return GUILD_SETTINGS[guild_id]['prefix']
    return "!"  # Default prefix

def set_guild_prefix(guild_id, prefix):
    """Set command prefix for a guild"""
    if guild_id not in GUILD_SETTINGS:
        GUILD_SETTINGS[guild_id] = {}
    GUILD_SETTINGS[guild_id]['prefix'] = prefix
    return True

def log_command(user_id, guild_id, command_name):
    """Log command usage"""
    log_entry = {
        'user_id': user_id,
        'guild_id': guild_id,
        'command': command_name,
        'timestamp': datetime.now()
    }
    COMMAND_LOGS.append(log_entry)
    
    # Update user data
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {
            'commands_used': 0,
            'last_command': None,
            'last_command_time': None
        }
    
    USER_DATA[user_id]['commands_used'] = USER_DATA[user_id].get('commands_used', 0) + 1
    USER_DATA[user_id]['last_command'] = command_name
    USER_DATA[user_id]['last_command_time'] = datetime.now()
    
    return True

def get_command_stats():
    """Get command usage statistics"""
    stats = {}
    for log in COMMAND_LOGS:
        command = log['command']
        if command not in stats:
            stats[command] = 0
        stats[command] += 1
    return stats

# Function to get guild language
def get_lang(guild_id):
    if guild_id is None:
        return "id"  # Default language for DMs
    return get_guild_language(guild_id)

# Function to get guild prefix
def get_prefix(bot, message):
    if message.guild is None:
        return "!"  # Default prefix for DMs
    return get_guild_prefix(message.guild.id)

# Translations helper function
def get_text(guild_id: Optional[int], key: str, **kwargs) -> str:
    """Get translated text based on guild language preference"""
    lang = get_lang(guild_id)
    
    # Split the key by dots to handle nested keys
    keys = key.split('.')
    value = LANGUAGES[lang]["translations"]
    
    # Navigate through nested dictionary
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            # Fallback to English if key not found
            value = LANGUAGES["en"]["translations"]
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    # If still not found, check specific key patterns for common errors
                    if key == "error_title":
                        return LANGUAGES[lang]["translations"]["error"]["title"]
                    elif key == "error_occurred":
                        return LANGUAGES[lang]["translations"]["error"]["occurred"].format(error=kwargs.get("error", "Unknown error"))
                    elif key.startswith("error."):
                        error_key = key.split(".")[1]
                        if error_key in LANGUAGES[lang]["translations"]["error"]:
                            return LANGUAGES[lang]["translations"]["error"][error_key]
                    # Last resort: return the key itself
                    return key  # Return the key itself if not found
    
    # Format the string with provided kwargs
    if isinstance(value, str) and kwargs:
        try:
            return value.format(**kwargs)
        except KeyError:
            return value
    return value

# Bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

# Update bot specs
BOT_SPECS = {
    "python_version": platform.python_version(),
    "discord.py_version": discord.__version__,
    "server_count": 0,
    "uptime": datetime.now(timezone.utc)
}

# Add developer IDs list
DEVELOPER_IDS = [837954360818270230, 586802340607417]

# Add restart channel storage
RESTART_DATA = {
    "channel_id": None,
    "is_restarting": False
}

# Add get_text method to the bot
bot.get_text = get_text

class LanguageSelect(discord.ui.Select):
    def __init__(self):
        options = []
        for lang_code, lang_data in LANGUAGES.items():
            option = discord.SelectOption(
                label=lang_data['name'],
                description=f"Switch to {lang_data['name']} / Ganti ke {lang_data['name']}",
                value=lang_code,
                emoji=lang_data['flag']
            )
            options.append(option)
            
        super().__init__(
            placeholder="🌐 Select a language / Pilih bahasa",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("❌ This command can only be used in servers!", ephemeral=True)
            
        lang_code = self.values[0]
        guild_id = interaction.guild_id
        old_lang = get_lang(guild_id)
        
        # Update the language preference for this server
        set_guild_language(guild_id, lang_code)
        
        # Create confirmation embed
        embed = discord.Embed(
            title=f"{LANGUAGES[lang_code]['flag']} {get_text(guild_id, 'language.title')}",
            color=EMBED_COLORS["success"]
        )
        
        # Show language change confirmation
        embed.add_field(
            name="✨ Language Changed / 言語が変更されました / 언어가 변경됨 / Bahasa Diubah",
            value=f"{LANGUAGES[old_lang]['flag']} {LANGUAGES[old_lang]['name']} ➜ {LANGUAGES[lang_code]['flag']} {LANGUAGES[lang_code]['name']}",
            inline=False
        )
        
        # Show server-specific notice
        embed.add_field(
            name="📢 Notice / お知らせ / 알림 / Pemberitahuan",
            value="This language setting only affects this server\nこの言語設定はこのサーバーのみに適用されます\n이 언어 설정은 이 서버에만 적용됩니다\nPengaturan bahasa hanya berlaku untuk server ini",
            inline=False
        )
        
        # Add available commands field
        embed.add_field(
            name="🔍 Available Commands / Perintah Tersedia",
            value=get_text(guild_id, "help_command_guide"),
            inline=False
        )
        
        embed.set_footer(text=f"Server ID: {interaction.guild_id}")
        await interaction.response.edit_message(embed=embed, view=None)

class LanguageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(LanguageSelect())

class CategorySelect(discord.ui.Select):
    def __init__(self, guild_id):
        self.guild_id = guild_id
        options = []
        
        # Create select options for each category
        category_icons = {
            "general": "ℹ️",
            "utility": "🔧",
            "fun": "🎮",
            "anime": "🎬",  # Add anime category
            "reaction": "😄",
            "school": "🏫",
            "lastfm": "🎵"
        }
        
        # Define commands in each category
        categories = {
            "general": ["help", "info", "ping"],
            "reaction": ["hug", "kiss", "pat", "slap", "cuddle", "dance", "smile", "wave", "blush", "happy"],
            "lastfm": ["lastfm", "np", "recent", "album", "artist", "topalbums", "topartists", "countries"],
            "utility": ["help", "info", "ping", "prefix", "language", "sekolah", "imsakiyah", "anime", "update"],
            "anime": ["anime", "manga", "character", "season", "random", "top"],  # Add anime commands
            "fun": ["randomwaifu", "waifu", "neko", "shinobu", "megumin"]
        }
        
        # Add each category as an option
        for category, commands in categories.items():
            # Skip categories with no commands
            if not commands:
                continue
                
            # Get category emoji icon
            emoji = category_icons.get(category, "🔹")
            
            # Create select option for this category
            option = discord.SelectOption(
                label=category.capitalize(),
                description=f"{len(commands)} commands",
                value=category,
                emoji=emoji
            )
            options.append(option)
        
        super().__init__(
            placeholder="📚 Select a command category...",
            min_values=1,
            max_values=1,
            options=options
        )
        
    async def callback(self, interaction: discord.Interaction):
        """Handle category selection"""
        selected_category = self.values[0]
        guild_id = interaction.guild_id
        
        # Define commands in each category
        categories = {
            "general": ["help", "info", "ping"],
            "reaction": ["hug", "kiss", "pat", "slap", "cuddle", "dance", "smile", "wave", "blush", "happy"],
            "lastfm": ["lastfm", "np", "recent", "album", "artist", "topalbums", "topartists", "countries"],
            "utility": ["help", "info", "ping", "prefix", "language", "sekolah", "imsakiyah", "anime", "update"],
            "anime": ["anime", "manga", "character", "season", "random", "top"],  # Add anime commands
            "fun": ["randomwaifu", "waifu", "neko", "shinobu", "megumin"]
        }
        
        # Get commands in selected category
        commands_in_category = categories.get(selected_category, [])
        
        # Create embed for the category
        embed = discord.Embed(
            title=f"{selected_category.capitalize()} Commands",
            description=f"Here are the commands in the {selected_category} category:",
            color=EMBED_COLORS["primary"]
        )
        
        # Add each command to the embed
        command_text = ""
        for cmd_name in commands_in_category:
            # Try to get command description
            cmd = interaction.client.get_command(cmd_name)
            description = cmd.help if cmd and cmd.help else get_text(guild_id, f"command_descriptions.{cmd_name}")
            
            # Prefix with emoji based on category
            if selected_category == "reaction":
                emoji = f":{cmd_name}:" if cmd_name in ["smile", "wave", "blush", "happy"] else f":{cmd_name}_face:"
                command_text += f"• `!{cmd_name}` - {description}\n"
            elif selected_category == "anime":
                emoji_map = {
                    "anime": "🎬", "manga": "📚", "character": "👤", 
                    "season": "🗓️", "random": "🎲", "top": "🏆"
                }
                emoji = emoji_map.get(cmd_name, "🎬")
                command_text += f"{emoji} `!{cmd_name}` - {description}\n"
            else:
                command_text += f"• `!{cmd_name}` - {description}\n"
        
        # If we have a lot of commands, split into fields for better readability
        if len(command_text) > 1024:
            # Split commands into multiple fields (maximum 1024 characters per field)
            command_list = command_text.split('\n')
            field_text = ""
            field_count = 1
            
            for cmd in command_list:
                if len(field_text + cmd + '\n') > 1024:
                    embed.add_field(name=f"Commands (Part {field_count})", value=field_text, inline=False)
                    field_text = cmd + '\n'
                    field_count += 1
                else:
                    field_text += cmd + '\n'
            
            # Add the last field if there's any remaining text
            if field_text:
                embed.add_field(name=f"Commands (Part {field_count})", value=field_text, inline=False)
        else:
            # All commands fit in a single field
            embed.add_field(name="Commands", value=command_text, inline=False)
        
        # Add category-specific help for anime commands
        if selected_category == "anime":
            embed.add_field(
                name="🎬 About MyAnimeList Integration",
                value=(
                    "These commands allow you to interact with MyAnimeList data.\n"
                    "Examples:\n"
                    "• `!anime Naruto` - Search for an anime\n"
                    "• `!manga One Piece` - Search for a manga\n"
                    "• `!character Luffy` - Find character information\n"
                    "• `!random` - Get a random anime recommendation\n"
                    "• `!season winter 2023` - View anime from a specific season\n"
                    "• `!top anime bypopularity` - See top rated anime"
                ),
                inline=False
            )
            
            # Add a nice MAL image
            embed.set_thumbnail(url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png")
        
        # Add usage examples
        embed.add_field(
            name="✨ Usage Example",
            value=f"To use a command: `!{commands_in_category[0] if commands_in_category else 'help'}`",
            inline=False
        )
        
        # Add tip for detailed help
        embed.add_field(
            name="💡 Tip",
            value=f"For detailed help on a command, use `!help <command>`",
            inline=False
        )
        
        # Update the message with the category information
        await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self, guild_id, bot):
        super().__init__(timeout=60)
        self.bot = bot
        self.add_item(CategorySelect(guild_id))

# Load extension utility
async def load_extension(ext_name):
    """Load an extension (cog) by name"""
    try:
        # Check if the extension is a direct file
        if os.path.exists(f"{ext_name}.py"):
            spec = importlib.util.spec_from_file_location(ext_name, f"{ext_name}.py")
            extension = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(extension)
            
            # Check if setup function exists in module
            if hasattr(extension, "setup"):
                await extension.setup(bot)
                print(f"[INFO] Loaded extension: {ext_name}")
            else:
                print(f"[ERROR] Extension {ext_name} missing setup function")
        # Or check if it's in an extensions directory
        elif os.path.exists(os.path.join("extensions", f"{ext_name}.py")):
            spec = importlib.util.spec_from_file_location(
                f"extensions.{ext_name}", 
                os.path.join("extensions", f"{ext_name}.py")
            )
            extension = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(extension)
            
            # Check if setup function exists in module
            if hasattr(extension, "setup"):
                await extension.setup(bot)
                print(f"[INFO] Loaded extension: {ext_name} from extensions directory")
            else:
                print(f"[ERROR] Extension {ext_name} missing setup function")
        else:
            print(f"[WARNING] Extension {ext_name} not found")
    except Exception as e:
        print(f"[ERROR] Failed to load extension {ext_name}: {e}")
        import traceback
        traceback.print_exc()

async def load_cogs():
    """Load all available cogs"""
    # Before loading extensions, remove all existing commands with the same name
    # to prevent duplicate command errors
    for extension_name in bot.extensions.copy():
        await bot.unload_extension(extension_name)
        print(f"Unloaded existing extension: {extension_name}")
    
    # Add all extensions to load here
    extensions = [
        "slash_commands",
        "imsakiyah",
        "mal"  # Add the new MAL extension
    ]
    
    loaded_count = 0
    for ext in extensions:
        success = await load_extension(ext)
        if success:
            loaded_count += 1
    
    print(f"📚 Loaded {loaded_count}/{len(extensions)} extensions.")
    
    # Attempt to load MAL module specifically if it wasn't loaded above
    if "mal" not in bot.extensions:
        try:
            # Try loading from current directory
            if os.path.exists("mal.py"):
                spec = importlib.util.spec_from_file_location("mal", "mal.py")
                mal_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mal_module)
                
                if hasattr(mal_module, "setup"):
                    await mal_module.setup(bot)
                    print("✅ Successfully loaded MAL module directly")
                else:
                    print("❌ MAL module found but missing setup function")
            else:
                print("❌ mal.py file not found in current directory")
        except Exception as e:
            print(f"❌ Error loading MAL module: {e}")
            print("Make sure aiohttp is installed with: pip install aiohttp")

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord"""
    # Load cogs (extensions)
    await load_cogs()
    
    # Update server count
    BOT_SPECS["server_count"] = len(bot.guilds)
    
    # Print startup info
    print("\n" + "=" * 50)
    print(f"🤖 {BOT_INFO['name']} v{BOT_INFO['version']} is online!")
    print(f"👤 Logged in as: {bot.user.name}#{bot.user.discriminator}")
    print(f"🆔 Bot ID: {bot.user.id}")
    print(f"🌐 Connected to {len(bot.guilds)} server(s)")
    print(f"👥 Serving {sum(guild.member_count for guild in bot.guilds)} users")
    print(f"🐍 Python version: {platform.python_version()}")
    print(f"📚 discord.py version: {discord.__version__}")
    
    # Check for MAL integration
    mal_commands = [cmd.name for cmd in bot.commands if cmd.cog_name == "Anime"]
    if mal_commands:
        print(f"🎬 MyAnimeList integration loaded with commands: {', '.join(mal_commands)}")
    else:
        print("❌ MyAnimeList integration not loaded")
    
    print("=" * 50)
    
    # Send restart notification if bot was restarting
    if RESTART_DATA["is_restarting"] and RESTART_DATA["channel_id"]:
        try:
            channel = bot.get_channel(RESTART_DATA["channel_id"])
            if channel:
                success_embed = discord.Embed(
                    title="✅ Bot Berhasil Dimulai Ulang!",
                    description=(
                        "```diff\n"
                        "+ Sistem berhasil dimuat ulang\n"
                        "+ Cache telah dioptimalkan\n"
                        "+ Semua sistem berjalan normal\n"
                        "```\n"
                        "Ruri-chan sudah kembali dan siap membantu! ✨"
                    ),
                    color=discord.Color.from_rgb(147, 201, 255)  # Light blue
                )
                success_embed.add_field(
                    name="📢 Pesan Ruri",
                    value=(
                        "*\"Aku sudah kembali! Terima kasih sudah menunggu~ "
                        "Ayo kita bersenang-senang lagi! ✨\"*"
                    ),
                    inline=False
                )
                
                # Add MAL integration info if loaded
                if mal_commands:
                    success_embed.add_field(
                        name="🎬 MyAnimeList Integration",
                        value=(
                            f"MAL Integration is active with {len(mal_commands)} commands!\n"
                            f"Try `!anime`, `!manga`, or `!random` to explore anime content."
                        ),
                        inline=False
                    )
                
                success_embed.set_thumbnail(url="https://media.tenor.com/TY1HfJK5qQUAAAAC/ruri-dragon-smile.gif")
                success_embed.set_footer(text="📢 Ruri Dragon sudah siap melayani! ✨")
                await channel.send(embed=success_embed)
        except Exception as e:
            print(f"Failed to send restart notification: {e}")
        finally:
            # Reset restart data
            RESTART_DATA["channel_id"] = None
            RESTART_DATA["is_restarting"] = False

@bot.event
async def on_disconnect():
    print("Bot disconnected from Discord. Attempting to reconnect...")

@bot.event
async def on_resumed():
    print("Bot connection resumed with Discord.")

@bot.event
async def on_guild_join(guild):
    """Event yang dipanggil ketika bot bergabung dengan server baru"""
    try:
        # Update server count
        BOT_SPECS["server_count"] = len(bot.guilds)
        
        # Temukan channel yang sesuai untuk mengirim pesan sambutan
        channel = None
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                if any(word in ch.name.lower() for word in ['general', 'umum', 'chat', 'utama', 'welcome', 'sambutan']):
                    channel = ch
                    break
        
        # Jika tidak menemukan channel khusus, gunakan channel pertama yang dapat diakses
        if channel is None:
            for ch in guild.text_channels:
                if ch.permissions_for(guild.me).send_messages:
                    channel = ch
                    break
        
        # Jika masih tidak menemukan channel, keluar
        if channel is None:
            return
        
        # Kirim pesan sambutan
        embed = discord.Embed(
            title="👋 Hai! Ruri-chan di sini!",
            description=(
                "Terima kasih sudah mengundang Ruri-chan ke server ini! ✨\n\n"
                "Aku adalah bot multifungsi yang bisa:\n"
                "• Menampilkan gambar anime yang lucu dan menarik 🖼️\n"
                "• Menyediakan informasi anime dari berbagai database 🎬\n"
                "• Menampilkan jadwal imsakiyah saat Ramadhan 🕌\n"
                "• Mencari informasi sekolah di Indonesia 🏫\n"
                "• Dan masih banyak lagi!"
            ),
            color=discord.Color.from_rgb(147, 201, 255)  # Light blue
        )
        
        # Tambahkan panduan quickstart yang jelas 
        embed.add_field(
            name="🚀 Memulai",
            value=(
                f"• Gunakan `!help` untuk melihat daftar perintah\n"
                f"• Gunakan `!language` untuk mengubah bahasa bot\n"
                f"• Gunakan `!prefix` untuk mengubah prefix (admin saja)"
            ),
            inline=False
        )
        
        # Tambahkan bagian bantuan dan dukungan
        embed.add_field(
            name="📢 Butuh Bantuan?",
            value=(
                "• Gunakan `!info` untuk melihat informasi bot\n"
                "• Jika ada masalah, hubungi pembuat di Discord\n"
                f"• Developer: {BOT_INFO['creator']}"
            ),
            inline=False
        )
        
        # Tambahkan catatan tentang izin
        embed.add_field(
            name="⚠️ Catatan Penting",
            value=(
                "Ruri-chan membutuhkan izin untuk:\n"
                "• Membaca & Mengirim Pesan\n"
                "• Melihat Channel\n"
                "• Menambahkan Reaksi\n"
                "• Melihat Anggota Server\n"
                "• Mengirim Pesan Embeds\n"
                "Pastikan Ruri memiliki izin yang diperlukan, ya!"
            ),
            inline=False
        )
        
        embed.set_thumbnail(url="https://media.tenor.com/TY1HfJK5qQUAAAAC/ruri-dragon-smile.gif")
        embed.set_footer(text=f"{BOT_INFO['name']} v{BOT_INFO['version']} • Ketik !help untuk bantuan")
        
        await channel.send(embed=embed)
        
        # Log event
        print(f"✅ Bot has joined a new server: {guild.name} (ID: {guild.id}) - Members: {guild.member_count}")
    except Exception as e:
        print(f"❌ Error in on_guild_join: {e}")

@bot.event 
async def on_error(event, *args, **kwargs):
    """Global error handler for bot events"""
    error = sys.exc_info()
    error_text = f"Unhandled error in {event}: {error[1]}"
    print(error_text)
    try:
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {error_text}\n")
    except:
        pass  # If we can't write to file, just continue

@bot.command(name="language", aliases=["languange"])
async def language_command(ctx, lang_code: str = None):
    """Change bot language (EN/ID/JP/KR) / Ubah bahasa bot (EN/ID/JP/KR)"""
    guild_id = ctx.guild.id if ctx.guild else None
    
    # Check if running in DM
    if not ctx.guild:
        embed = discord.Embed(
            title="❌ Server Only Command",
            description="This command can only be used in servers!",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
    
    # If no language code provided, show language selector
    if not lang_code:
        embed = discord.Embed(
            title="🌐 Language Settings / Pengaturan Bahasa",
            description=(
                f"**Current language / Bahasa saat ini: {LANGUAGES[get_lang(guild_id)]['flag']} {LANGUAGES[get_lang(guild_id)]['name']}**\n\n"
                "Select your preferred language from the dropdown menu below.\n"
                "Pilih bahasa yang Anda inginkan dari menu dropdown di bawah ini."
            ),
            color=EMBED_COLORS["primary"]
        )
        
        # Add available languages
        languages_text = "\n".join([f"{lang_data['flag']} `{code.upper()}` - {lang_data['name']}" for code, lang_data in LANGUAGES.items()])
        embed.add_field(
            name="Available Languages / Bahasa yang Tersedia",
            value=languages_text,
            inline=False
        )
        
        # Add usage examples
        embed.add_field(
            name="Usage / Penggunaan",
            value=(
                f"`{get_guild_prefix(guild_id)}language en` - Switch to English\n"
                f"`{get_guild_prefix(guild_id)}language id` - Beralih ke Bahasa Indonesia\n"
                f"`{get_guild_prefix(guild_id)}language jp` - 日本語に切り替える\n"
                f"`{get_guild_prefix(guild_id)}language kr` - 한국어로 전환"
            ),
            inline=False
        )
        
        view = LanguageView()
        return await ctx.send(embed=embed, view=view)
    
    # Validate language code
    if lang_code not in LANGUAGES:
        embed = discord.Embed(
            title="❌ Invalid Language Code / Kode Bahasa Tidak Valid",
            description=(
                "Please use one of these codes / Gunakan salah satu kode berikut:\n"
                "🇬🇧 `EN` - English\n"
                "🇮🇩 `ID` - Bahasa Indonesia\n"
                "🇰🇷 `KR` - Korean\n"
                "🇯🇵 `JP` - Japanese"
            ),
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
    
    # Get old language for comparison
    old_lang = get_lang(guild_id)
    
    # Update the language preference for this server
    success = set_guild_language(guild_id, lang_code)
    
    if not success:
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to update language preference. Please try again later.",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
    
    # Create confirmation embed
    embed = discord.Embed(
        title=f"{LANGUAGES[lang_code]['flag']} {get_text(guild_id, 'language.title')}",
        color=EMBED_COLORS["success"]
    )
    
    # Show language change confirmation
    embed.add_field(
        name="✨ Language Changed / 言語が変更されました / 언어가 변경됨 / Bahasa Diubah",
        value=f"{LANGUAGES[old_lang]['flag']} {LANGUAGES[old_lang]['name']} ➜ {LANGUAGES[lang_code]['flag']} {LANGUAGES[lang_code]['name']}",
        inline=False
    )
    
    # Show example commands in new language
    example_commands = (
        f"**{get_text(guild_id, 'help_command_guide')}**\n"
        f"❓ `!help` - {get_text(guild_id, 'command_descriptions.help')}\n"
        f"🎲 `!randomwaifu` - {get_text(guild_id, 'command_descriptions.randomwaifu')}\n"
        f"ℹ️ `!info` - {get_text(guild_id, 'command_descriptions.info')}"
    )
    embed.add_field(
        name="🌐 Example Commands / コマンド例 / 명령어 예제 / Contoh Perintah",
        value=example_commands,
        inline=False
    )
    
    # Add server-specific notice
    embed.add_field(
        name="📢 Notice / お知らせ / 알림 / Pemberitahuan",
        value="This language setting only affects this server\nこの言語設定はこのサーバーのみに適用されます\n이 언어 설정은 이 서버에만 적용됩니다\nPengaturan bahasa hanya berlaku untuk server ini",
        inline=False
    )
    
    embed.set_footer(text=f"Server ID: {ctx.guild.id}")
    
    # Log command usage
    log_command(ctx.guild.id, ctx.author.id, "language", success=True)
    
    await ctx.send(embed=embed)

@bot.command(name="help")
async def help_command(ctx, *, command_name: str = None):
    """Display help command with categories and detailed information"""
    guild_id = ctx.guild.id if ctx.guild else None
    current_prefix = get_prefix(bot, ctx.message)
    
    if command_name:
        cmd = bot.get_command(command_name.lower())
        if not cmd:
            embed = discord.Embed(
                title=get_text(guild_id, "help.not_found"),
                description=get_text(guild_id, "help.use_help", prefix=current_prefix),
                color=EMBED_COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        # Command info embed
        embed = discord.Embed(
            title=get_text(guild_id, "help.command_info", prefix=current_prefix, command=cmd.name),
            description=get_text(guild_id, f"command_descriptions.{cmd.name}"),
            color=EMBED_COLORS["secondary"]
        )
        
        # Add usage field
        embed.add_field(
            name=get_text(guild_id, "help.usage"),
            value=f"`{current_prefix}{cmd.name}`",
            inline=False
        )
        
        embed.set_footer(text=get_text(guild_id, "help.return_to_menu", prefix=current_prefix))
        return await ctx.send(embed=embed)

    # Main help menu
    embed = discord.Embed(
        title=get_text(guild_id, "help.title", bot_name=BOT_INFO['name']),
        description=get_text(guild_id, "help.description", user=ctx.author.mention),
        color=EMBED_COLORS["primary"]
    )

    # Add command categories
    categories = {
        "image": "🖼️",
        "reaction": "💞",
        "fun": "🎭",
        "lastfm": "🎵",
        "utility": "⚙️"
    }

    for category, emoji in categories.items():
        category_name = get_text(guild_id, f"help.categories.{category}")
        category_desc = get_text(guild_id, f"help.category_descriptions.{category}")
        embed.add_field(
            name=f"{emoji} {category_name}",
            value=category_desc,
            inline=True
        )

    # Add quick tips
    embed.add_field(
        name=f"🌐 {get_text(guild_id, 'tips')}",
        value=get_text(guild_id, 'help_command_guide', prefix=current_prefix),
        inline=False
    )
    
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_footer(text=get_text(guild_id, "help.footer", creator=BOT_INFO['creator'], count=len(bot.commands)))
    
    view = HelpView(guild_id, bot)
    await ctx.send(embed=embed, view=view)

@bot.command(name="info")
async def bot_info(ctx):
    """Show detailed bot information"""
    guild_id = ctx.guild.id if ctx.guild else None
    uptime = datetime.now(timezone.utc) - BOT_SPECS["uptime"]
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    
    embed = discord.Embed(
        title=get_text(guild_id, "bot_info"),
        color=EMBED_COLORS["secondary"]
    )
    
    embed.add_field(
        name=get_text(guild_id, "bot_description"),
        value=BOT_INFO["description"],
        inline=False
    )
    
    embed.add_field(
        name=get_text(guild_id, "tech_specs"),
        value=(
            f"**Python Version:** {BOT_SPECS['python_version']}\n"
            f"**discord.py Version:** {BOT_SPECS['discord.py_version']}\n"
            f"**Server Count:** {BOT_SPECS['server_count']}\n"
            f"**Uptime:** {get_text(guild_id, 'uptime_format').format(days=days, hours=hours, minutes=minutes, seconds=seconds)}"
        ),
        inline=False
    )
    
    embed.set_footer(text=f"{get_text(guild_id, 'creator')}: {BOT_INFO['creator']} | v{BOT_INFO['version']}")
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    
    await ctx.send(embed=embed)

@bot.command(name="categories")
async def list_categories(ctx):
    """List all available waifu categories"""
    guild_id = ctx.guild.id if ctx.guild else None
    categories_chunk = [WAIFU_CATEGORIES[i:i+10] for i in range(0, len(WAIFU_CATEGORIES), 10)]
    
    for i, chunk in enumerate(categories_chunk, 1):
        embed = discord.Embed(
            title=get_text(guild_id, "categories_title", part=i),
            description="\n".join([f"🖼️{cat.capitalize()}" for cat in chunk]),
            color=EMBED_COLORS["primary"]
        )
        await ctx.send(embed=embed)

@bot.command(name="randomwaifu")
async def random_waifu(ctx):
    """Get a random waifu from any category"""
    category = random.choice(WAIFU_CATEGORIES)
    await get_waifu_image(ctx, category)

for category in WAIFU_CATEGORIES:
    # Periksa apakah command dengan nama ini sudah ada
    if not bot.get_command(category):
        @bot.command(name=category)
        async def waifu_command(ctx):
            """Get a waifu image from specific category"""
            command_name = ctx.invoked_with
            await get_waifu_image(ctx, command_name)

async def get_waifu_image(ctx, category):
    guild_id = ctx.guild.id if ctx.guild else None
    try:
        # Set a timeout for the request to prevent hanging
        response = requests.post(
            f"{WAIFU_API_URL}/many/sfw/{category}", 
            json={"exclude": []},
            timeout=10  # 10 seconds timeout
        )
        response.raise_for_status()
        data = response.json()
        
        if 'files' in data and data['files']:
            for url in data['files'][:1]:
                embed = discord.Embed(color=EMBED_COLORS["primary"])
                embed.set_image(url=url)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=get_text(guild_id, "error.title"),
                description=get_text(guild_id, "no_image"),
                color=EMBED_COLORS["error"]
            )
            await ctx.send(embed=embed)
            
    except requests.exceptions.Timeout:
        embed = discord.Embed(
            title=get_text(guild_id, "error.title"),
            description="API request timed out. Server mungkin sedang sibuk, silakan coba lagi nanti.",
            color=EMBED_COLORS["error"]
        )
        await ctx.send(embed=embed)
    except requests.exceptions.ConnectionError:
        embed = discord.Embed(
            title=get_text(guild_id, "error.title"),
            description="Koneksi ke API gagal. Periksa koneksi internet Anda atau coba lagi nanti.",
            color=EMBED_COLORS["error"]
        )
        await ctx.send(embed=embed)
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, 'response') else "unknown"
        embed = discord.Embed(
            title=get_text(guild_id, "error.title"),
            description=f"Error HTTP {status_code} saat mengakses API. Silakan coba lagi nanti.",
            color=EMBED_COLORS["error"]
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title=get_text(guild_id, "error.title"),
            description=get_text(guild_id, "error.occurred", error=str(e)),
            color=EMBED_COLORS["error"]
        )
        await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors and log them"""
    command_name = ctx.invoked_with
    guild_id = ctx.guild.id if ctx.guild else None
    user_id = ctx.author.id
    
    # Log the error to database with success=False
    try:
        log_command(guild_id, user_id, command_name, success=False)
    except Exception as e:
        print(f"Error logging command error: {e}")
    
    if isinstance(error, commands.CommandNotFound):
        command_used = ctx.message.content.split()[0]
        embed = discord.Embed(
            title="❌ Perintah Tidak Ditemukan...",
            description=(
                f"```css\n[Error: Perintah '{command_used}' tidak dikenali]\n```\n"
                "*Ruri-chan terlihat sedih dan menggembungkan pipinya...*"
            ),
            color=discord.Color.from_rgb(255, 182, 193)  # Pink pastel
        )
        
        # Tambahkan gambar Ruri yang sedih dengan berbagai pilihan GIF
        sad_gifs = [
            "https://media.tenor.com/V5QWkxFgsDgAAAAC/ruri-dragon-sad.gif",  # Sedih
            "https://media.tenor.com/7SqVQQZVticAAAAC/confused-anime.gif",  # Bingung
            "https://media.tenor.com/zLpNDWqF4TUAAAAC/anime-pout.gif",      # Cemberut
            "https://media.tenor.com/z2LTFz7yfsoAAAAC/anime-girl.gif"       # Menangis
        ]
        embed.set_thumbnail(url=random.choice(sad_gifs))
        
        # Pesan Ruri yang imut dan menyedihkan
        ruri_messages = [
            f"*\"Maaf {ctx.author.mention}-chan, aku tidak mengerti perintah itu... (｡•́︿•̀｡)\"*",
            f"*\"Huweee~ Aku tidak tahu perintah itu... Apakah {ctx.author.mention}-chan salah ketik? (｡>﹏<｡)\"*",
            f"*\"{ctx.author.mention}-chan... A-aku benar-benar tidak mengerti... (｡ŏ﹏ŏ)\"*",
            f"*\"Uuuu~ Aku sudah mencoba mencari perintah itu tapi tidak ketemu... (｡>_<｡)\"*"
        ]
        
        embed.add_field(
            name="📢 Pesan Ruri",
            value=random.choice(ruri_messages),
            inline=False
        )
        
        # Tambahkan saran perintah yang mungkin dimaksud
        all_commands = [cmd.name for cmd in bot.commands]
        similar_commands = [cmd for cmd in all_commands if command_used[1:] in cmd or any(c in command_used[1:] for c in cmd)]
        
        # Hanya tambahkan field jika ada similar commands yang ditemukan
        if similar_commands:
            similar_text = "\n".join([f"• `{get_prefix(bot, ctx.message)}{cmd}`" for cmd in similar_commands[:3]])
            embed.add_field(
                name="💡 Mungkin maksudmu...",
                value=similar_text,
                inline=False
            )
        
        # Tambahkan tip untuk melihat daftar perintah
        embed.add_field(
            name="📢 Tips",
            value=f"Gunakan `{get_prefix(bot, ctx.message)}help` untuk melihat semua perintah yang tersedia~",
            inline=False
        )
        
        # Tambahkan footer yang imut
        embed.set_footer(text="📢 Ruri akan selalu berusaha menjadi lebih baik!")
        
        # Kirim pesan dan tambahkan reaksi emoji sedih
        message = await ctx.send(embed=embed)
        sad_emojis = ["❌", "❌", "❌", "❌"]
        try:
            for emoji in sad_emojis[:2]:  # Batasi hanya 2 emoji untuk mengurangi rate limit
                await message.add_reaction(emoji)
        except:
            pass  # Abaikan error jika tidak bisa menambahkan reaksi
    else:
        embed = discord.Embed(
            title=get_text(guild_id, "error.title"),
            description=get_text(guild_id, "error.occurred", error=str(error)),
            color=EMBED_COLORS["error"]
        )
        await ctx.send(embed=embed)

async def setup_slash_commands():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

def has_developer_role():
    async def predicate(ctx):
        # Check if user ID is in developer list
        if ctx.author.id in DEVELOPER_IDS:
            return True
            
        # Check if user has a role named "Developer"
        if ctx.guild is None:
            return False
        return discord.utils.get(ctx.author.roles, name="Developer") is not None
    return commands.check(predicate)

@bot.command(name="restart")
@has_developer_role()
async def restart_bot(ctx):
    """Restart the bot (Developer only)"""
    guild_id = ctx.guild.id if ctx.guild else None
    
    # Store channel ID for restart notification
    RESTART_DATA["channel_id"] = ctx.channel.id
    RESTART_DATA["is_restarting"] = True
    
    # Create restart embed
    embed = discord.Embed(
        title="📢 Memulai Ulang Bot...",
        description=(
            "```diff\n"
            "+ Mempersiapkan sistem untuk restart...\n"
            "+ Menyimpan data sementara...\n"
            "+ Mengoptimalkan cache...\n"
            "```\n"
            "Tunggu sebentar ya~ Bot akan segera kembali! ✨"
        ),
        color=discord.Color.from_rgb(255, 182, 193)  # Pink pastel
    )
    
    # Add developer info with fancy formatting
    embed.add_field(
        name="📢 Developer Info",
        value=(
            "```yaml\n"
            f"Restart oleh: {ctx.author.name}\n"
            f"ID         : {ctx.author.id}\n"
            f"Timestamp  : {datetime.now().strftime('%H:%M:%S')}\n"
            "```"
        ),
        inline=False
    )
    
    # Add estimated time
    embed.add_field(
        name="⏳ Perkiraan Waktu",
        value="```Estimasi: ~10 detik```",
        inline=False
    )
    
    # Add cute message
    embed.add_field(
        name="📢 Pesan Ruri",
        value=(
            "*\"Aku akan kembali dengan kekuatan penuh! "
            "Tunggu aku ya~ ✨\"*"
        ),
        inline=False
    )
    
    # Set Ruri Dragon GIF
    embed.set_image(url="https://media.tenor.com/9CUBGKqR0KIAAAAd/ruri-dragon-cute.gif")
    embed.set_thumbnail(url="https://media.tenor.com/dqsvK2YWZJcAAAAC/ruri-dragon-anime.gif")
    
    # Set footer with cute message
    embed.set_footer(
        text="📢 Ruri Dragon akan kembali dalam sekejap! ✨",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )
    
    restart_msg = await ctx.send(embed=embed)
    
    try:
        # Add loading animation
        loading_emojis = ["❌", "❌", "❌", "❌", "✅"]
        for emoji in loading_emojis:
            await restart_msg.add_reaction(emoji)
            await asyncio.sleep(0.5)
        
        await asyncio.sleep(1)
        os.execv(sys.executable, ['python'] + sys.argv)
        
    except Exception as e:
        # Reset restart data on failure
        RESTART_DATA["channel_id"] = None
        RESTART_DATA["is_restarting"] = False
        
        error_embed = discord.Embed(
            title="❌ Gagal Memulai Ulang",
            description=(
                "```diff\n"
                f"- Error: {str(e)}\n"
                "```\n"
                "*Maaf, sepertinya ada masalah saat memulai ulang...*"
            ),
            color=discord.Color.red()
        )
        error_embed.set_thumbnail(url="https://media.tenor.com/V5QWkxFgsDgAAAAC/ruri-dragon-sad.gif")
        await ctx.send(embed=error_embed)

@bot.command(name="stop")
@has_developer_role()
async def stop_bot(ctx):
    """Stop the bot completely (Developer only)"""
    guild_id = ctx.guild.id if ctx.guild else None
    
    # Create shutdown embed
    embed = discord.Embed(
        title="🛑 Mematikan Bot...",
        description=(
            "```diff\n"
            "- Mempersiapkan sistem untuk shutdown...\n"
            "- Menyimpan data...\n"
            "- Menutup koneksi...\n"
            "```\n"
            "Bot akan dimatikan. Untuk menghidupkan kembali, restart bot secara manual dari server."
        ),
        color=discord.Color.red()
    )
    
    # Add developer info with fancy formatting
    embed.add_field(
        name="📢 Developer Info",
        value=(
            "```yaml\n"
            f"Shutdown oleh: {ctx.author.name}\n"
            f"ID          : {ctx.author.id}\n"
            f"Timestamp   : {datetime.now().strftime('%H:%M:%S %d-%m-%Y')}\n"
            "```"
        ),
        inline=False
    )
    
    # Add goodbye message
    embed.add_field(
        name="📢 Pesan Ruri",
        value=(
            "*\"Sampai jumpa semuanya! Aku akan istirahat sekarang. "
            "Sampai bertemu lagi di lain waktu~ 👋\"*"
        ),
        inline=False
    )
    
    # Set Ruri Dragon GIF
    embed.set_thumbnail(url="https://media.tenor.com/V5QWkxFgsDgAAAAC/ruri-dragon-sad.gif")
    
    # Set footer with cute message
    embed.set_footer(
        text="📢 Ruri Dragon akan tidur sekarang... 💤",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )
    
    shutdown_msg = await ctx.send(embed=embed)
    
    try:
        # Add shutdown animation
        shutdown_emojis = ["🔴", "🟠", "🟡", "⚫"]
        for emoji in shutdown_emojis:
            await shutdown_msg.add_reaction(emoji)
            await asyncio.sleep(0.5)
        
        # Log shutdown event
        print(f"Bot shutdown initiated by {ctx.author} (ID: {ctx.author.id})")
        
        # Final message
        final_embed = discord.Embed(
            title="💤 Bot Dimatikan",
            description="Bot telah dimatikan dengan aman. Terima kasih telah menggunakan Ruri-chan!",
            color=discord.Color.dark_gray()
        )
        await shutdown_msg.edit(embed=final_embed)
        
        # Wait a moment for the message to be seen
        await asyncio.sleep(2)
        
        # Close the bot
        await bot.close()
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Gagal Mematikan Bot",
            description=(
                "```diff\n"
                f"- Error: {str(e)}\n"
                "```\n"
                "*Maaf, sepertinya ada masalah saat mematikan bot...*"
            ),
            color=discord.Color.red()
        )
        error_embed.set_thumbnail(url="https://media.tenor.com/V5QWkxFgsDgAAAAC/ruri-dragon-sad.gif")
        await ctx.send(embed=error_embed)

@bot.command(name="update")
async def update_command(ctx):
    """Menampilkan pembaruan terbaru dari Ruri-chan"""
    guild_id = ctx.guild.id if ctx.guild else None
    
    # Step 1: Send initial loading animation
    loading_embed = discord.Embed(
        title="🔄 Memuat Pembaruan Terbaru...",
        description="Mengumpulkan informasi pembaruan terbaru dari Ruri-chan...",
        color=discord.Color.blue()
    )
    loading_embed.set_image(url="https://media.tenor.com/4RP0XOcQhYgAAAAC/ruri-dragon-wait.gif")
    message = await ctx.send(embed=loading_embed)
    
    # Add animated loading reactions
    loading_emojis = ["⏳", "🔄", "📡", "📊"]
    for emoji in loading_emojis:
        await message.add_reaction(emoji)
        await asyncio.sleep(0.5)
    
    # Get current date for update freshness
    current_date = datetime.now().strftime("%d %B %Y")
    
    # Step 2: Create main update embed with beautiful design
    embed = discord.Embed(
        title="✨ Pembaruan Terbaru Ruri-chan ✨",
        description=(
            f"📢 **Hai {ctx.author.mention}!** Berikut adalah pembaruan fitur terbaru pada Ruri-chan.\n\n"
            "```fix\n🌟 PEMBARUAN TERAKHIR: " + current_date + "```\n"
            "Swipe melalui reaksi untuk melihat seluruh update! 📝✨"
        ),
        color=discord.Color.from_rgb(147, 201, 255)  # Light blue color
    )
    
    # Step 3: Create multiple themed update sections
    
    # Latest update with fancy formatting
    embed.add_field(
        name="🎉 TERBARU: Peningkatan Visual & Sistem",
        value=(
            "```yaml\n📅 Tanggal: " + current_date + "\n```\n"
            "• 🖌️ Desain visual yang lebih menarik dan modern\n"
            "• 🛠️ Perbaikan pada komando `!language` dan `!update`\n"
            "• 🚀 Peningkatan kinerja dan respons yang lebih cepat\n"
            "• 🔧 Mengatasi berbagai bug dan masalah teknis\n"
            "• 🖼️ Tambahan animasi dan GIF yang lebih imut\n"
            "• 🌈 Pesan error dengan tampilan yang lebih informatif\n"
        ),
        inline=False
    )
    
    # Previous updates with different style
    embed.add_field(
        name="📱 Sistem & Perintah Baru",
        value=(
            "```diff\n+ Ditambahkan sistem pencarian Anime baru yang lebih lengkap\n"
            "+ Database anime terhubung ke MyAnimeList, AniList, dan lainnya\n"
            "+ Perintah !stop untuk developer\n"
            "+ Perintah status database baru\n```\n"
            "• 🎬 Coba `!anime <judul>` untuk mencari anime favoritmu!\n"
            "• 🔍 Gunakan `!anime id:<ID> source:<database>` untuk pencarian spesifik\n"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🌐 Fitur Bahasa & Internasional",
        value=(
            "```ini\n[Dukungan 4 bahasa sekarang tersedia!]\n```\n"
            "• 🇮🇩 Bahasa Indonesia (default)\n"
            "• 🇬🇧 English (Inggris)\n"
            "• 🇯🇵 日本語 (Jepang)\n"
            "• 🇰🇷 한국어 (Korea)\n\n"
            "Gunakan `!language` untuk mengubah bahasa bot!"
        ),
        inline=False
    )
    
    # Future roadmap in a special box
    embed.add_field(
        name="🔮 Roadmap Masa Depan",
        value=(
            "```css\n[Fitur yang sedang dikembangkan]\n```\n"
            "• 🎵 Integrasi Last.fm yang lebih baik\n"
            "• 🎮 Mini-games Discord baru\n"
            "• 📊 Dashboard web untuk pengaturan bot\n"
            "• 📱 Pemberitahuan rilis anime baru\n"
            "• 🌟 Sistem level dan XP untuk pengguna aktif\n"
        ),
        inline=False
    )
    
    # User feedback section with fancy style
    embed.add_field(
        name="💌 Berikan Pendapatmu!",
        value=(
            "```fix\nPunya ide untuk fitur baru? Atau menemukan bug?```\n"
            f"Kirimkan saranmu ke developer: **{BOT_INFO['creator']}**\n"
            "Setiap saran sangat berharga untuk pengembangan Ruri-chan! ✨"
        ),
        inline=False
    )
    
    # Set a cute animated thumbnail
    embed.set_thumbnail(url="https://media.tenor.com/TY1HfJK5qQUAAAAC/ruri-dragon-smile.gif")
    
    # Add beautiful banner image
    embed.set_image(url="https://i0.wp.com/www.comicbookrevolution.com/wp-content/uploads/2022/06/Ruri-Dragon-Chapter-1-Fire-Sneeze-Banner.jpg")  # Ruri banner - you can replace with appropriate URL
    
    # Custom footer with version info
    embed.set_footer(
        text=f"⭐ Ruri-chan v{BOT_INFO['version']} • Dibuat dengan ❤️ oleh {BOT_INFO['creator']} • Diperbarui: {current_date}",
        icon_url=ctx.bot.user.avatar.url if ctx.bot.user.avatar else None
    )
    
    # Step 4: Update the message and add interactive reactions
    await message.edit(embed=embed)
    
    # Clear the loading reactions
    await message.clear_reactions()
    
    # Add new interactive reactions for the update display
    reactions = ["⬅️", "🔄", "➡️", "💖", "📢", "🎮"]
    for reaction in reactions:
        try:
            await message.add_reaction(reaction)
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"Error adding reaction: {e}")
    
    # Step 5: Create reaction handler for interactive navigation
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in reactions and reaction.message.id == message.id
    
    # Start interactive session
    try:
        while True:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            emoji = str(reaction.emoji)
            
            # Handle different reactions
            if emoji == "⬅️":
                # Show older updates
                older_embed = discord.Embed(
                    title="📜 Pembaruan Sebelumnya",
                    description="Sejarah pembaruan Ruri-chan dari waktu ke waktu",
                    color=discord.Color.from_rgb(255, 183, 197)  # Pink color
                )
                
                older_embed.add_field(
                    name="📅 Maret 2025 - Fitur Imsakiyah & Visual Baru",
                    value=(
                        "• 🕌 Perintah `!imsakiyah` untuk jadwal sholat selama Ramadhan\n"
                        "• 🗺️ Dukungan untuk ratusan kota di seluruh Indonesia\n"
                        "• 🖼️ Tampilan visual baru yang lebih modern\n"
                        "• 📱 Responsivitas pesan yang lebih baik"
                    ),
                    inline=False
                )
                
                older_embed.add_field(
                    name="📅 Februari 2025 - Integrasi Sekolah",
                    value=(
                        "• 🏫 Perintah `!sekolah` untuk mencari informasi sekolah\n"
                        "• 🔍 Database lengkap sekolah di Indonesia\n"
                        "• 📊 Informasi NPSN, alamat, dan data penting lainnya"
                    ),
                    inline=False
                )
                
                older_embed.set_thumbnail(url="https://media.tenor.com/NcBVpmY9GVgAAAAC/ruri-dragon-girl.gif")
                older_embed.set_footer(text="Gunakan ➡️ untuk kembali ke update terbaru")
                
                await message.edit(embed=older_embed)
                
            elif emoji == "➡️":
                # Show main update embed again
                await message.edit(embed=embed)
                
            elif emoji == "🔄":
                # Show a special animation then restore main embed
                refresh_embed = discord.Embed(
                    title="🔄 Menyegarkan Informasi...",
                    description="Mengambil data terbaru...",
                    color=discord.Color.from_rgb(130, 255, 130)  # Light green
                )
                refresh_embed.set_image(url="https://media.tenor.com/1pMAGk2B5q4AAAAC/ruri-dragon-ruri.gif")
                
                await message.edit(embed=refresh_embed)
                await asyncio.sleep(2)
                await message.edit(embed=embed)
                
            elif emoji == "💖":
                # Show special thank you message
                thanks_embed = discord.Embed(
                    title="💖 Terima Kasih Sudah Menggunakan Ruri-chan!",
                    description=(
                        "*\"Hai~ Terima kasih sudah membaca update-ku dan menggunakan bot ini! "
                        "Aku akan terus berkembang untuk memberikan pengalaman terbaik! "
                        "Sampai jumpa di petualangan berikutnya~\"*"
                    ),
                    color=discord.Color.from_rgb(255, 105, 180)  # Hot pink
                )
                thanks_embed.set_image(url="https://media.tenor.com/9CUBGKqR0KIAAAAd/ruri-dragon-cute.gif")
                
                await message.edit(embed=thanks_embed)
                await asyncio.sleep(4)
                await message.edit(embed=embed)
                
            elif emoji == "📢":
                # Show tutorial on how to use new features
                tutorial_embed = discord.Embed(
                    title="📢 Cara Menggunakan Fitur Baru",
                    description="Panduan singkat untuk fitur-fitur terbaru Ruri-chan",
                    color=discord.Color.from_rgb(255, 165, 0)  # Orange
                )
                
                tutorial_embed.add_field(
                    name="🎬 Pencarian Anime",
                    value=(
                        "**Perintah: `!anime <judul>`**\n"
                        "Contoh: `!anime Naruto`\n\n"
                        "**Pencarian dengan ID:**\n"
                        "`!anime id:21 source:mal`\n\n"
                        "*source bisa berupa: mal, al, kt, adb, dll.*"
                    ),
                    inline=True
                )
                
                tutorial_embed.add_field(
                    name="🌐 Mengubah Bahasa",
                    value=(
                        "**Perintah: `!language <kode>`**\n"
                        "Kode bahasa yang tersedia:\n"
                        "• `en` - English\n"
                        "• `id` - Indonesia\n"
                        "• `jp` - 日本語\n"
                        "• `kr` - 한국어"
                    ),
                    inline=True
                )
                
                tutorial_embed.add_field(
                    name="🕌 Jadwal Imsakiyah",
                    value=(
                        "**Perintah: `!imsakiyah <kota>`**\n"
                        "Contoh: `!imsakiyah jakarta`\n\n"
                        "Gunakan navigasi tombol untuk melihat daftar kota"
                    ),
                    inline=False
                )
                
                tutorial_embed.set_thumbnail(url="https://media.tenor.com/aGtyI3Ah8ZEAAAAd/ruri-dragon-ruri.gif")
                tutorial_embed.set_footer(text="Gunakan ➡️ untuk kembali ke update terbaru")
                
                await message.edit(embed=tutorial_embed)
                
            elif emoji == "🎮":
                # Show easter egg
                easter_embed = discord.Embed(
                    title="🎮 Easter Egg Ditemukan!",
                    description=(
                        "```fix\nSelamat! Kamu menemukan easter egg tersembunyi!```\n\n"
                        "Ruri-chan memiliki beberapa easter egg tersembunyi. "
                        "Coba temukan easter egg lainnya dengan berbagai perintah! 👀"
                    ),
                    color=discord.Color.from_rgb(138, 43, 226)  # Purple
                )
                easter_embed.set_image(url="https://media.tenor.com/JBJGTdlOhMoAAAAd/ruri-dragon-ruri.gif")
                
                await message.edit(embed=easter_embed)
                await asyncio.sleep(3)
                await message.edit(embed=embed)
                
            # Remove user's reaction to keep the message clean
            try:
                await message.remove_reaction(emoji, user)
            except:
                pass  # Ignore if bot doesn't have permission
                
    except asyncio.TimeoutError:
        # After timeout, remove all reactions and update footer
        timeout_embed = embed.copy()
        timeout_embed.set_footer(text=f"⭐ Sesi interaktif telah berakhir • Ruri-chan v{BOT_INFO['version']}")
        
        try:
            await message.clear_reactions()
            await message.edit(embed=timeout_embed)
        except:
            pass
        
    # Log command usage
    try:
        log_command(guild_id, ctx.author.id, "update")
    except Exception as e:
        print(f"Error logging update command: {e}")

@bot.command(name="ping")
async def ping(ctx):
    """Check bot latency"""
    guild_id = ctx.guild.id if ctx.guild else None
    
    # Calculate API latency
    start_time = time.time()
    message = await ctx.send("Testing API latency...")
    end_time = time.time()
    api_latency = round((end_time - start_time) * 1000)
    
    # Get bot latency
    bot_latency = round(bot.latency * 1000)
    
    # Create embed
    embed = discord.Embed(
        title=get_text(guild_id, "ping.title"),
        description=get_text(guild_id, "ping.description", latency=bot_latency, api_latency=api_latency),
        color=EMBED_COLORS["primary"]
    )
    
    await message.edit(content=None, embed=embed)

@bot.command(name="prefix")
@commands.has_permissions(manage_guild=True)
async def change_prefix(ctx, new_prefix: str = None):
    """Change the bot's prefix for this server"""
    guild_id = ctx.guild.id if ctx.guild else None
    
    if not ctx.guild:
        embed = discord.Embed(
            title="❌ Server Only",
            description="This command can only be used in servers!",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
        
    if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(
            title="❌ No Permission",
            description="You don't have permission to change the prefix!",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
    
    current_prefix = get_guild_prefix(guild_id)
    
    # If no prefix provided, show current prefix
    if new_prefix is None:
        embed = discord.Embed(
            title="⚙️ Pengaturan Prefix",
            description=f"Prefix saat ini: `{current_prefix}`\n\nUntuk mengubah prefix, gunakan:\n`{current_prefix}prefix <prefix_baru>`",
            color=EMBED_COLORS["primary"]
        )
        return await ctx.send(embed=embed)
    
    # Validate prefix length
    if len(new_prefix) > 5:
        embed = discord.Embed(
            title="❌ Prefix Terlalu Panjang",
            description="Prefix tidak boleh lebih dari 5 karakter!",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
    
    # Validate prefix characters
    if not all(c.isprintable() for c in new_prefix):
        embed = discord.Embed(
            title="❌ Prefix Tidak Valid",
            description="Prefix mengandung karakter yang tidak valid!",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
    
    # Update the prefix
    old_prefix = current_prefix
    success = set_guild_prefix(guild_id, new_prefix)
    
    if not success:
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to update prefix. Please try again later.",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
    
    # Create confirmation embed
    embed = discord.Embed(
        title="✅ Prefix Berhasil Diubah",
        description=f"Prefix lama: `{old_prefix}`\nPrefix baru: `{new_prefix}`",
        color=EMBED_COLORS["success"]
    )
    
    embed.add_field(
        name="🌐 Contoh Penggunaan",
        value=f"`{new_prefix}help` - Menampilkan bantuan\n`{new_prefix}info` - Informasi bot",
        inline=False
    )
    
    embed.set_footer(text=f"Diubah oleh: {ctx.author.name}")
    
    # Log command usage
    log_command(ctx.guild.id, ctx.author.id, "prefix", success=True)
    
    await ctx.send(embed=embed)

# Imsakiyah functionality
API_BASE_URL = "https://raw.githubusercontent.com/lakuapik/jadwalsholatorg/master/adzan"
CACHE_DIR = "cache"

# Create cache directory if it doesn't exist
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

class Imsakiyah:
    """
    Class untuk mengelola fitur jadwal imsakiyah
    """
    def __init__(self, bot):
        self.bot = bot
        
    async def get_cities(self):
        """Get list of available cities"""
        try:
            response = requests.get("https://raw.githubusercontent.com/lakuapik/jadwalsholatorg/master/kota.json")
            response.raise_for_status()
            return {"data": response.json()}
        except Exception as e:
            print(f"Error fetching cities: {e}")
            return None
    
    async def get_imsakiyah_data(self, city_id, year=None, month=None):
        """Get imsakiyah data for a specific city and month"""
        # Use current year and month if not specified
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
            
        try:
            # Try to get data from the API
            response = requests.get(f"https://raw.githubusercontent.com/lakuapik/jadwalsholatorg/master/adzan/{city_id}/{year}/{month}.json")
            
            # If API returns error, use fallback data
            if response.status_code != 200:
                print(f"Error fetching imsakiyah data, using fallback: {response.status_code}")
                return self.generate_fallback_data(city_id, month, year)
                
            return {"data": response.json()}
        except Exception as e:
            print(f"Error fetching imsakiyah data: {e}")
            return self.generate_fallback_data(city_id, month, year)
    
    def generate_fallback_data(self, city_id, month, year):
        """Generate fallback data when API is unavailable"""
        # Generate 30 days of fallback data with slight variations
        fallback_data = []
        base_date = datetime(year, month, 1)
        
        for i in range(30):
            current_date = base_date + timedelta(days=i)
            
            # Skip if month changes
            if current_date.month != month:
                continue
                
            # Generate slight variations in time
            minute_offset = (i % 5) - 2  # Between -2 and 2
            
            fallback_data.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "hijri": "Ramadan 1445",
                "imsak": f"04:{(23 + minute_offset) % 60:02d}",
                "subuh": f"04:{(33 + minute_offset) % 60:02d}",
                "terbit": f"05:{(48 + minute_offset) % 60:02d}",
                "dhuha": f"06:{(15 + minute_offset) % 60:02d}",
                "dzuhur": f"12:{(0 + minute_offset) % 60:02d}",
                "ashar": f"15:{(16 + minute_offset) % 60:02d}",
                "maghrib": f"18:{(5 + minute_offset) % 60:02d}",
                "isya": f"19:{(15 + minute_offset) % 60:02d}"
            })
            
        return {"data": fallback_data}
    
    async def get_today_schedule(self, city_id):
        """Get today's schedule for a specific city"""
        tz = pytz.timezone('Asia/Jakarta')
        today = datetime.now(tz)
        
        data = await self.get_imsakiyah_data(city_id, today.year, today.month)
        if not data:
            return None
            
        today_str = today.strftime('%Y-%m-%d')
        
        # Find today's schedule
        for day_data in data['data']:
            if day_data['date'] == today_str:
                return day_data
        
        # If today's schedule not found, return the first day's schedule
        if len(data['data']) > 0:
            return data['data'][0]
            
        # Last resort fallback
        return {
            "date": today_str,
            "hijri": "Ramadan 1445",
            "imsak": "04:23",
            "subuh": "04:33",
            "terbit": "05:48",
            "dhuha": "06:15",
            "dzuhur": "12:00",
            "ashar": "15:16",
            "maghrib": "18:05",
            "isya": "19:15"
        }

# Anime API functionality
ANIME_API_BASE = "https://api.animeapi.my.id/v3"
ANIME_PROVIDERS = [
    "myanimelist", "anilist", "kitsu", "anidb", "animeplanet", "anisearch", 
    "livechart", "notify", "themoviedb", "shikimori", "simkl"
]

@bot.command(name="anime", aliases=["ani", "animecari"])
async def anime_command(ctx, *, query=None):
    """Search for anime information from various sources"""
    if query is None:
        # Show help if no query provided
        embed = discord.Embed(
            title="🎬 Anime Search",
            description="Cari informasi anime dari berbagai sumber.",
            color=EMBED_COLORS["primary"]
        )
        embed.add_field(
            name="ℹ️ Cara Penggunaan",
            value=(
                "`!anime <judul>` - Cari anime berdasarkan judul\n"
                "`!anime id:<id> source:<sumber>` - Cari berdasarkan ID\n\n"
                "**Sumber yang tersedia:**\n"
                "• `mal` - MyAnimeList\n"
                "• `al` - AniList\n"
                "• `kt` - Kitsu\n"
                "• `adb` - Anime DB\n"
            ),
            inline=False
        )
        embed.add_field(
            name="📢 Contoh",
            value=(
                "`!anime naruto`\n"
                "`!anime id:21 source:mal`\n"
                "`!anime id:1 source:al`"
            ),
            inline=False
        )
        
        # Add cute anime girl image
        embed.set_image(url="https://i.imgur.com/XmZPPbt.png")
        
        return await ctx.send(embed=embed)
    
    # Check if searching by ID
    id_match = re.search(r'id:(\d+)', query, re.IGNORECASE)
    source_match = re.search(r'source:(\w+)', query, re.IGNORECASE)
    
    if id_match and source_match:
        anime_id = id_match.group(1)
        source = source_match.group(1).lower()
        
        # Remove id and source from query
        clean_query = re.sub(r'id:\d+\s*', '', query, flags=re.IGNORECASE)
        clean_query = re.sub(r'source:\w+\s*', '', clean_query, flags=re.IGNORECASE).strip()
        
        # Valid sources
        valid_sources = ['mal', 'al', 'kt', 'adb']
        
        if source not in valid_sources:
            embed = discord.Embed(
                title="❌ Sumber Tidak Valid",
                description=f"Sumber `{source}` tidak valid. Gunakan salah satu dari: {', '.join(valid_sources)}",
                color=EMBED_COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        # Create loading message
        loading_embed = discord.Embed(
            title="🔍 Mencari Anime...",
            description=f"Mencari anime dengan ID {anime_id} dari {source.upper()}...",
            color=EMBED_COLORS["primary"]
        )
        loading_embed.set_footer(text="Mohon tunggu sebentar...")
        message = await ctx.send(embed=loading_embed)
        
        # Simulate API call delay
        await asyncio.sleep(2)
        
        # For demo purposes, return mock data
        # In a real implementation, this would call the appropriate API
        
        # Mock data based on source
        anime_data = {
            "mal": {
                "title": "Naruto",
                "title_japanese": "ナルト",
                "type": "TV",
                "episodes": 220,
                "status": "Finished Airing",
                "score": 8.1,
                "members": 2540000,
                "favorites": 95000,
                "synopsis": "Naruto Uzumaki, a mischievous adolescent ninja...",
                "year": 2002,
                "studios": ["Studio Pierrot"],
                "genres": ["Action", "Adventure", "Fantasy"],
                "image_url": "https://cdn.myanimelist.net/images/anime/13/17405l.jpg"
            },
            "al": {
                "title": {"english": "Naruto", "native": "ナルト"},
                "type": "TV",
                "episodes": 220,
                "status": "FINISHED",
                "averageScore": 81,
                "popularity": 250000,
                "description": "Naruto Uzumaki, a mischievous adolescent ninja...",
                "startDate": {"year": 2002, "month": 10, "day": 3},
                "studios": [{"name": "Studio Pierrot"}],
                "genres": ["Action", "Adventure", "Fantasy"],
                "coverImage": {"large": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20-YJvLbgJQPCoI.jpg"}
            }
        }
        
        # Default to MAL if source not found in mock data
        source_data = anime_data.get(source, anime_data["mal"])
        
        # Display anime info based on source
        await display_anime_info(ctx, source_data, message)
        
    else:
        # Searching by title
        # Create loading message
        loading_embed = discord.Embed(
            title="🔍 Mencari Anime...",
            description=f"Mencari anime dengan judul \"{query}\"...",
            color=EMBED_COLORS["primary"]
        )
        loading_embed.set_footer(text="Mohon tunggu sebentar...")
        message = await ctx.send(embed=loading_embed)
        
        # Simulate API call delay
        await asyncio.sleep(2)
        
        # Mock response for demo purposes
        mock_anime = {
            "title": "Naruto",
            "title_japanese": "ナルト",
            "type": "TV",
            "episodes": 220,
            "status": "Finished Airing",
            "score": 8.1,
            "members": 2540000, 
            "favorites": 95000,
            "synopsis": "Naruto Uzumaki, a mischievous adolescent ninja, struggles as he searches for recognition and dreams of becoming the Hokage, the village's leader and strongest ninja.",
            "year": 2002,
            "studios": ["Studio Pierrot"],
            "genres": ["Action", "Adventure", "Fantasy"],
            "image_url": "https://cdn.myanimelist.net/images/anime/13/17405l.jpg"
        }
        
        # Display anime info
        await display_anime_info(ctx, mock_anime, message)

async def display_anime_info(ctx, anime_data, message):
    """Display anime information in a formatted embed"""
    # Determine format based on data structure (MAL vs AniList)
    is_anilist = "averageScore" in anime_data
    
    # Create embed
    embed = discord.Embed(
        title=anime_data.get("title", {}).get("english", anime_data.get("title")) if is_anilist else anime_data.get("title"),
        color=EMBED_COLORS["primary"]
    )
    
    # Set description (synopsis)
    embed.description = anime_data.get("description") if is_anilist else anime_data.get("synopsis")
    
    # Set thumbnail
    embed.set_thumbnail(url=anime_data.get("coverImage", {}).get("large") if is_anilist else anime_data.get("image_url"))
    
    # Add Japanese title
    jp_title = anime_data.get("title", {}).get("native") if is_anilist else anime_data.get("title_japanese")
    if jp_title:
        embed.add_field(name="🇯🇵 Judul Jepang", value=jp_title, inline=True)
    
    # Add type and episodes
    embed.add_field(name="📺 Tipe", value=anime_data.get("type", "N/A"), inline=True)
    embed.add_field(name="📊 Episode", value=str(anime_data.get("episodes", "N/A")), inline=True)
    
    # Add status
    status = anime_data.get("status", "N/A")
    if is_anilist and status == "FINISHED":
        status = "Finished Airing"
    embed.add_field(name="📡 Status", value=status, inline=True)
    
    # Add score
    score = anime_data.get("averageScore") if is_anilist else anime_data.get("score")
    if score:
        score_str = f"{score/10:.1f}" if is_anilist else f"{score:.1f}"
        embed.add_field(name="⭐ Skor", value=score_str, inline=True)
    
    # Add popularity/members
    popularity = anime_data.get("popularity") if is_anilist else anime_data.get("members")
    if popularity:
        pop_str = f"{popularity:,}"
        embed.add_field(name="👥 Popularitas", value=pop_str, inline=True)
    
    # Add year
    year = anime_data.get("startDate", {}).get("year") if is_anilist else anime_data.get("year")
    if year:
        embed.add_field(name="📅 Tahun", value=str(year), inline=True)
    
    # Add studios
    studios = anime_data.get("studios", [])
    if studios:
        if is_anilist:
            studio_names = [studio.get("name", "N/A") for studio in studios]
        else:
            studio_names = studios
        embed.add_field(name="🎬 Studio", value=", ".join(studio_names), inline=True)
    
    # Add genres
    genres = anime_data.get("genres", [])
    if genres:
        embed.add_field(name="🏷️ Genre", value=", ".join(genres), inline=True)
    
    # Set footer with data source
    source = "AniList" if is_anilist else "MyAnimeList"
    embed.set_footer(text=f"Data dari {source} • Gunakan !anime untuk info lebih lanjut")
    
    # Update the loading message with anime info
    await message.edit(embed=embed)
    
    # Add reactions to navigate
    reactions = ["ℹ️", "📺", "⭐", "🎬"]
    for reaction in reactions:
        try:
            await message.add_reaction(reaction)
        except Exception as e:
            print(f"Error adding reaction: {e}")
    
    # Set up reaction handler
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in reactions and reaction.message.id == message.id
    
    try:
        # Wait for user reaction
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check)
        
        # Handle reaction based on emoji
        if str(reaction.emoji) == "ℹ️":
            # Show more info
            more_info_embed = discord.Embed(
                title=f"{anime_data.get('title')} - Detail Lengkap",
                description=anime_data.get("synopsis"),
                color=EMBED_COLORS["primary"]
            )
            more_info_embed.set_image(url=anime_data.get("image_url"))
            await message.edit(embed=more_info_embed)
        
        elif str(reaction.emoji) == "📺":
            # Show episodes info
            episodes_embed = discord.Embed(
                title=f"{anime_data.get('title')} - Informasi Episode",
                description=f"Total episode: {anime_data.get('episodes', 'N/A')}",
                color=EMBED_COLORS["primary"]
            )
            episodes_embed.set_thumbnail(url=anime_data.get("image_url"))
            await message.edit(embed=episodes_embed)
        
        elif str(reaction.emoji) == "⭐":
            # Show ratings info
            ratings_embed = discord.Embed(
                title=f"{anime_data.get('title')} - Ratings & Stats",
                description=(
                    f"⭐ Skor: {anime_data.get('score', 'N/A')}/10\n"
                    f"👥 Members: {anime_data.get('members', 'N/A'):,}\n"
                    f"❤️ Favorites: {anime_data.get('favorites', 'N/A'):,}"
                ),
                color=EMBED_COLORS["primary"]
            )
            ratings_embed.set_thumbnail(url=anime_data.get("image_url"))
            await message.edit(embed=ratings_embed)
        
        elif str(reaction.emoji) == "🎬":
            # Show studio info
            studio_embed = discord.Embed(
                title=f"{anime_data.get('title')} - Studio Information",
                description=f"Studio: {', '.join(anime_data.get('studios', ['N/A']))}",
                color=EMBED_COLORS["primary"]
            )
            studio_embed.set_thumbnail(url=anime_data.get("image_url"))
            await message.edit(embed=studio_embed)
    
    except asyncio.TimeoutError:
        # Remove reactions after timeout
        await message.clear_reactions()

    # Log command usage
    log_command(ctx.guild.id if ctx.guild else None, ctx.author.id, "anime")

# Run the bot
if __name__ == "__main__":
    try:
        print("Starting Ruri-chan Discord Bot...")
        print(f"Python Version: {platform.python_version()}")
        print(f"Discord.py Version: {discord.__version__}")
        print(f"System: {platform.system()} {platform.release()}")
        print("=========================================")
        print("Connecting to Discord...")
        
        # Create logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        # Create a log file with timestamp
        log_filename = f"logs/bot_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(log_filename, "w", encoding="utf-8") as f:
            f.write(f"Bot started at {datetime.now()}\n")
            f.write(f"Python Version: {platform.python_version()}\n")
            f.write(f"Discord.py Version: {discord.__version__}\n")
            f.write(f"System: {platform.system()} {platform.release()}\n")
            f.write("=========================================\n")
        
        # Run the bot
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("ERROR: Invalid Discord token. Please check your .env file.")
    except discord.PrivilegedIntentsRequired:
        print("ERROR: Privileged intents are not enabled for this bot.")
        print("Please go to the Discord Developer Portal and enable the intents in the Bot section.")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
    finally:
        print("Bot has shut down.")

@bot.command(name="stats")
@commands.has_permissions(administrator=True)
async def stats_command(ctx):
    """Tampilkan statistik penggunaan bot"""
    guild_id = ctx.guild.id if ctx.guild else None
    
    # Get command stats from database
    stats = get_command_stats()
    
    # Create stats embed
    embed = discord.Embed(
        title="📊 Statistik Bot",
        description=f"Statistik penggunaan {bot.user.name}",
        color=EMBED_COLORS["primary"]
    )
    
    # Add total commands field
    total_commands = stats.get("total", 0)
    embed.add_field(
        name="📝 Total Perintah",
        value=f"`{total_commands}` perintah dijalankan",
        inline=False
    )
    
    # Add command usage breakdown
    popular_commands = []
    for key, value in stats.items():
        if key != "total" and key != "_id":
            popular_commands.append((key, value))
    
    # Sort by usage count, descending
    popular_commands.sort(key=lambda x: x[1], reverse=True)
    
    # Get top 10 commands
    top_commands = popular_commands[:10]
    if top_commands:
        commands_list = "\n".join([f"`{cmd}`: **{count}** kali" for cmd, count in top_commands])
        embed.add_field(
            name="🔝 Perintah Populer",
            value=commands_list or "Belum ada data perintah",
            inline=False
        )
    
    # Add server info
    embed.add_field(
        name="🌐 Informasi Server",
        value=(
            f"**Servers**: {len(bot.guilds)}\n"
            f"**Users**: {sum(guild.member_count for guild in bot.guilds)}\n"
            f"**Channels**: {len(list(bot.get_all_channels()))}"
        ),
        inline=True
    )
    
    # Add bot uptime
    uptime = datetime.now(timezone.utc) - BOT_SPECS["uptime"]
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    
    embed.add_field(
        name="⏱️ Uptime",
        value=f"{days}d {hours}h {minutes}m {seconds}s",
        inline=True
    )
    
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    # Log command usage
    log_command(ctx.guild.id, ctx.author.id, "stats", success=True)
    
    await ctx.send(embed=embed)

@bot.command(name="dbstatus")
@commands.has_permissions(administrator=True)
async def db_status_command(ctx):
    """Tampilkan status koneksi database"""
    guild_id = ctx.guild.id if ctx.guild else None
    
    # First check if user is either admin or developer
    if not ctx.author.guild_permissions.administrator and ctx.author.id not in DEVELOPER_IDS:
        embed = discord.Embed(
            title="❌ Akses Ditolak",
            description="Anda memerlukan izin administrator untuk menggunakan perintah ini.",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
    
    # Send initial loading message
    loading_message = await ctx.send("🔄 Mengambil status database...")
    
    try:
        # Get connection info from database
        connection_info = db.get_connection_info()
        
        # Create embed with connection info
        embed = discord.Embed(
            title="🗄️ Status Database",
            description="Informasi koneksi database dan statistik",
            color=EMBED_COLORS["primary"] if connection_info.get("status") == "connected" else EMBED_COLORS["error"]
        )
        
        # Add connection status field
        status = connection_info.get("status", "unknown")
        message = connection_info.get("message", "Tidak ada info tambahan")
        embed.add_field(
            name="📊 Status Koneksi",
            value=f"Status: **{status}**\n{message}",
            inline=False
        )
        
        # Add details based on connection status
        if status == "connected":
            # Add server info
            server_info = connection_info.get("server_info", {})
            server_version = f"{server_info.get('version', 'Unknown')}"
            embed.add_field(
                name="🖥️ Informasi Server",
                value=f"MongoDB Version: {server_version}",
                inline=False
            )
            
            # Add collections info
            collections = connection_info.get("collections", [])
            embed.add_field(
                name="📚 Collections",
                value=", ".join(collections) if collections else "Tidak ada collections",
                inline=False
            )
            
            # Add document counts
            counts = connection_info.get("collection_counts", {})
            count_str = "\n".join([f"**{k}**: {v} dokumen" for k, v in counts.items()])
            embed.add_field(
                name="🔢 Jumlah Dokumen",
                value=count_str if count_str else "Tidak ada data",
                inline=False
            )
        elif status == "memory":
            # Add memory storage info
            counts = connection_info.get("collection_counts", {})
            count_str = "\n".join([f"**{k}**: {v} item" for k, v in counts.items()])
            embed.add_field(
                name="💾 Penyimpanan Memory",
                value=count_str if count_str else "Tidak ada data di memory",
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Peringatan",
                value="Data disimpan di memory dan akan hilang saat bot di-restart.\nGunakan MongoDB untuk penyimpanan permanen.",
                inline=False
            )
        
        # Add server info from Python
        embed.add_field(
            name="🤖 Informasi Sistem",
            value=f"Python: {platform.python_version()}\nDiscord.py: {discord.__version__}\nOS: {platform.system()} {platform.release()}",
            inline=False
        )
        
        embed.set_footer(text=f"Database command - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Log command usage
        log_command(ctx.guild.id if ctx.guild else None, ctx.author.id, "dbstatus", success=True)
        
        await loading_message.edit(content=None, embed=embed)
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Terjadi kesalahan saat mengambil status database: {str(e)}",
            color=EMBED_COLORS["error"]
        )
        await loading_message.edit(content=None, embed=error_embed)
        
        # Log error
        print(f"Error in dbstatus command: {e}")

@bot.command(name="dbrebuild")
async def db_rebuild_command(ctx):
    """Coba rebuild koneksi database jika terjadi masalah"""
    guild_id = ctx.guild.id if ctx.guild else None
    
    # First check if user is either admin or developer
    if not ctx.author.guild_permissions.administrator and ctx.author.id not in DEVELOPER_IDS:
        embed = discord.Embed(
            title="❌ Akses Ditolak",
            description="Anda memerlukan izin administrator untuk menggunakan perintah ini.",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
    
    # Send initial message
    message = await ctx.send("🔄 Mencoba rebuild koneksi database...")
    
    try:
        # Try to reconnect to the database
        if hasattr(db, '_connect_to_mongodb'):
            success = db._connect_to_mongodb()
        else:
            success = False
            print("Warning: Database module does not have _connect_to_mongodb method")
        
        if success:
            embed = discord.Embed(
                title="✅ Koneksi Database Berhasil",
                description="Koneksi ke database berhasil di-rebuild",
                color=EMBED_COLORS["success"]
            )
            embed.add_field(
                name="📊 Status",
                value="Terhubung ke MongoDB",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Rebuild Gagal",
                description="Tidak dapat terhubung ke database MongoDB",
                color=EMBED_COLORS["error"]
            )
            embed.add_field(
                name="📊 Status",
                value="Menggunakan penyimpanan memory (sementara)",
                inline=False
            )
            embed.add_field(
                name="⚠️ Peringatan",
                value="Data disimpan di memory dan akan hilang saat bot di-restart.\nPeriksa koneksi MongoDB Anda.",
                inline=False
            )
            
            # Add troubleshooting tips
            embed.add_field(
                name="🔍 Tips Troubleshooting",
                value=(
                    "1. Pastikan URI MongoDB di file .env benar\n"
                    "2. Pastikan server MongoDB dapat diakses\n"
                    "3. Periksa apakah username/password benar\n"
                    "4. Jika menggunakan MongoDB Atlas, pastikan IP Anda diizinkan\n"
                    "5. Coba gunakan `USE_MEMORY_SERVER=true` di .env untuk fallback storage"
                ),
                inline=False
            )
        
        embed.set_footer(text=f"Database rebuild - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Log command usage
        log_command(ctx.guild.id if ctx.guild else None, ctx.author.id, "dbrebuild", success=True)
        
        await message.edit(content=None, embed=embed)
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Terjadi kesalahan saat rebuild database: {str(e)}",
            color=EMBED_COLORS["error"]
        )
        await message.edit(content=None, embed=error_embed)
        
        # Log error
        print(f"Error in dbrebuild command: {e}")

@bot.event
async def on_command(ctx):
    """Log when a command is used"""
    command_name = ctx.command.name
    guild_id = ctx.guild.id if ctx.guild else None
    user_id = ctx.author.id
    
    # Check for duplicate command invocation to prevent double logging
    # Use ctx.message.id as a unique identifier for this command invocation
    message_id = ctx.message.id
    
    # Store in global or bot variable to track processed messages
    if not hasattr(bot, 'processed_commands'):
        bot.processed_commands = set()
        
    # Skip if this message was already processed
    if message_id in bot.processed_commands:
        return
        
    # Add to processed commands set
    bot.processed_commands.add(message_id)
    
    # Remove old message IDs to prevent memory leak (keep last 100)
    if len(bot.processed_commands) > 100:
        bot.processed_commands = set(list(bot.processed_commands)[-100:])
    
    # Filter out non-ASCII characters from the log message
    clean_author = re.sub(r'[^\x00-\x7F]+', '[non-ASCII]', str(ctx.author))
    clean_guild = re.sub(r'[^\x00-\x7F]+', '[non-ASCII]', str(ctx.guild)) if ctx.guild else "DM"
    
    # Log command usage to console
    print(f"Command used: {command_name} by {clean_author} in {clean_guild}")
    
    # Log command to database
    log_command(guild_id, user_id, command_name)
    
    # Update user data
    try:
        user_data = {
            "name": str(ctx.author),
            "updated_at": datetime.now(),
            "last_command": command_name,
            "last_command_time": datetime.now()
        }
# REMOVED MONGODB:         db.update_user(user_id, user_data)
    except Exception as e:
        print(f"Error updating user data: {e}")
