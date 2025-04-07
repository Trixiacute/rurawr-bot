"""
helper.py - Utility functions for the Discord bot

This module contains various helper functions used
throughout the Discord bot program.
"""

import discord
import time
from datetime import datetime
from typing import Optional, Dict, Any, List, Union, Tuple
import re
import logging
import pytz

from src.core.config import EMBED_COLORS, TIME_FORMAT
from src.core.database import db

# Configure logging to prevent non-ASCII characters from being displayed in terminal
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

def create_embed(
    title: Optional[str] = None, 
    description: Optional[str] = None, 
    color: Optional[int] = None,
    url: Optional[str] = None,
    thumbnail: Optional[str] = None,
    image: Optional[str] = None,
    author: Optional[Dict[str, str]] = None,
    fields: Optional[List[Dict[str, Union[str, bool]]]] = None,
    footer: Optional[Dict[str, str]] = None,
    timestamp: Optional[bool] = False
) -> discord.Embed:
    """
    Membuat embed Discord dengan parameter yang disediakan
    
    Args:
        title: Judul embed
        description: Deskripsi embed
        color: Warna embed (integer)
        url: URL untuk judul embed
        thumbnail: URL untuk thumbnail embed
        image: URL untuk gambar besar embed
        author: Dict dengan 'name', 'url' (opsional), dan 'icon_url' (opsional)
        fields: List dari Dict dengan 'name', 'value', dan 'inline' (opsional)
        footer: Dict dengan 'text' dan 'icon_url' (opsional)
        timestamp: Apakah menambahkan timestamp saat ini
        
    Returns:
        discord.Embed yang sudah diatur
    """
    # Set default color if not provided
    if color is None:
        color = EMBED_COLORS.get("primary", 0x3498db)
    
    # Create embed
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        url=url
    )
    
    # Add thumbnail if provided
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    # Add image if provided
    if image:
        embed.set_image(url=image)
    
    # Add author if provided
    if author:
        embed.set_author(
            name=author.get("name", ""),
            url=author.get("url"),
            icon_url=author.get("icon_url")
        )
    
    # Add fields if provided
    if fields:
        for field in fields:
            embed.add_field(
                name=field.get("name", ""),
                value=field.get("value", ""),
                inline=field.get("inline", False)
            )
    
    # Add footer if provided
    if footer:
        embed.set_footer(
            text=footer.get("text", ""),
            icon_url=footer.get("icon_url")
        )
    
    # Add timestamp if requested
    if timestamp:
        embed.timestamp = datetime.utcnow()
    
    return embed

def format_timestamp(timestamp: float, format_str: Optional[str] = None) -> str:
    """
    Memformat timestamp Unix ke string yang readable
    
    Args:
        timestamp: Timestamp Unix (detik sejak epoch)
        format_str: Format string untuk strftime (opsional)
        
    Returns:
        String timestamp yang terformat
    """
    if format_str is None:
        format_str = TIME_FORMAT
    
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime(format_str)

def get_user_avatar_url(user: discord.User) -> str:
    """
    Mendapatkan URL avatar pengguna Discord
    
    Args:
        user: Objek User atau Member Discord
        
    Returns:
        String URL avatar
    """
    if user.avatar:
        return user.avatar.url
    
    # Default avatar if none is set
    return user.default_avatar.url

def log_command(user_id: int, guild_id: Optional[int], command_name: str) -> None:
    """
    Mencatat penggunaan command
    
    Args:
        user_id: ID pengguna Discord
        guild_id: ID server Discord (None jika di DM)
        command_name: Nama command yang digunakan
    """
    db.log_command(user_id, guild_id, command_name)

def get_uptime(bot) -> Tuple[int, int, int, int]:
    """
    Menghitung uptime bot dalam hari, jam, menit, detik
    
    Args:
        bot: Instance bot Discord
        
    Returns:
        Tuple (hari, jam, menit, detik)
    """
    if not hasattr(bot, 'start_time'):
        return (0, 0, 0, 0)
    
    now = datetime.now()
    delta = now - bot.start_time
    
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return (days, hours, minutes, seconds)

def get_uptime_string(bot) -> str:
    """
    Mendapatkan string uptime yang readable
    
    Args:
        bot: Instance bot Discord
        
    Returns:
        String uptime yang diformat
    """
    days, hours, minutes, seconds = get_uptime(bot)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

# Function to get guild language
def get_lang(guild_id):
    """
    Get language setting from guild
    
    Args:
        guild_id: Discord guild ID
        
    Returns:
        Language code string (id, en, etc.)
    """
    from src.core.database import MemoryDB
    db = MemoryDB()
    return db.get_guild_language(guild_id)

# Function to get guild prefix
def get_prefix(bot, message):
    """
    Get command prefix for a guild
    
    Args:
        bot: Bot instance
        message: Discord message
        
    Returns:
        Command prefix string
    """
    if message.guild is None:
        return "!"  # Default prefix for DMs
    from src.core.database import MemoryDB
    db = MemoryDB()
    return db.get_guild_prefix(message.guild.id)

# Translations helper function
def get_text(guild_id: Optional[int], key: str, **kwargs) -> str:
    """
    Get translated text based on guild language
    
    Args:
        guild_id: Discord guild ID
        key: Translation key (e.g. 'commands.help.title')
        **kwargs: Parameters to insert into the string
        
    Returns:
        Translated string
    """
    from src.core import LANGUAGES
    lang = get_lang(guild_id)
    
    # Split the key by dots to handle nested keys
    keys = key.split('.')
    value = LANGUAGES[lang]["translations"]
    
    # Navigate through nested dictionary
    for k in keys:
        if k in value:
            value = value[k]
        else:
            # If key not found, use the default language (id)
            if lang != "id":
                return get_text(guild_id, key, lang="id", **kwargs)
            # If still not found, return the key itself
            return key
    
    # If we have a string, format it with kwargs
    if isinstance(value, str):
        try:
            value = value.format(**kwargs)
        except KeyError:
            # If there's a missing key in kwargs, use key as fallback
            pass
    
    return value

def get_command_stats():
    """
    Get command usage statistics
    
    Returns:
        Dictionary with command statistics
    """
    from src.core.database import MemoryDB
    db = MemoryDB()
    return db.get_command_stats()

def get_timestamp():
    """
    Get current timestamp with Indonesia time
    
    Returns:
        Timestamp string
    """
    # Get current time in Asia/Jakarta timezone
    tz = pytz.timezone('Asia/Jakarta')
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M:%S %z")

def format_time_id(dt):
    """
    Format time to Indonesian format
    
    Args:
        dt: Datetime object
        
    Returns:
        Formatted time string
    """
    days_id = {
        0: "Senin",
        1: "Selasa",
        2: "Rabu",
        3: "Kamis", 
        4: "Jumat",
        5: "Sabtu",
        6: "Minggu"
    }
    
    months_id = {
        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember"
    }
    
    day_name = days_id.get(dt.weekday(), "")
    month_name = months_id.get(dt.month, "")
    
    return f"{day_name}, {dt.day} {month_name} {dt.year}, {dt.strftime('%H:%M:%S')}" 