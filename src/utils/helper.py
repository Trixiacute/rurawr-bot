"""
helper.py - Utility functions untuk bot Discord

Berisi berbagai fungsi pembantu yang digunakan di seluruh aplikasi.
"""

import discord
import time
from datetime import datetime
from typing import Optional, Dict, Any, List, Union, Tuple

from src.core.config import EMBED_COLORS, TIME_FORMAT
from src.core.database import db

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