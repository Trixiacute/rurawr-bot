"""
utils.py - Fungsi-fungsi utilitas untuk bot Discord

Module ini berisi berbagai fungsi pembantu yang digunakan
di berbagai bagian program bot Discord.
"""

import discord
from typing import Optional, Dict, Any
from memory_db import db
import re
import logging
import pytz
from datetime import datetime

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

# Function to get guild language
def get_lang(guild_id):
    """
    Mendapatkan setting bahasa dari guild
    
    Args:
        guild_id: ID dari guild Discord
        
    Returns:
        String kode bahasa (id, en, dll)
    """
    return db.get_guild_language(guild_id)

# Function to get guild prefix
def get_prefix(bot, message):
    """
    Mendapatkan prefix command dari guild
    
    Args:
        bot: Bot instance
        message: Pesan Discord
        
    Returns:
        String prefix command
    """
    if message.guild is None:
        return "!"  # Default prefix for DMs
    return db.get_guild_prefix(message.guild.id)

# Translations helper function
def get_text(guild_id: Optional[int], key: str, **kwargs) -> str:
    """
    Mendapatkan teks terjemahan berdasarkan bahasa guild
    
    Args:
        guild_id: ID dari guild Discord
        key: Kunci terjemahan (e.g. 'commands.help.title')
        **kwargs: Parameter untuk dimasukkan ke dalam string
        
    Returns:
        String terjemahan
    """
    from language import LANGUAGES
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

def log_command(user_id, guild_id, command_name):
    """
    Mencatat penggunaan command
    
    Args:
        user_id: ID pengguna Discord
        guild_id: ID guild Discord
        command_name: Nama command yang digunakan
    
    Returns:
        Boolean sukses/gagal
    """
    return db.log_command(user_id, guild_id, command_name)

def get_command_stats():
    """
    Mendapatkan statistik penggunaan command
    
    Returns:
        Dictionary dengan statistik command
    """
    return db.get_command_stats()

def get_timestamp():
    """
    Mendapatkan timestamp saat ini dengan waktu Indonesia
    
    Returns:
        String timestamp
    """
    # Get current time in Asia/Jakarta timezone
    tz = pytz.timezone('Asia/Jakarta')
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M:%S %z")

def format_time_id(dt):
    """
    Memformat waktu ke format Indonesia
    
    Args:
        dt: Datetime object
        
    Returns:
        String waktu terformat
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

def create_embed(title, description=None, color=0x3498db, footer=None, thumbnail=None, image=None, author=None, fields=None):
    """
    Membuat embed Discord dengan lebih mudah
    
    Args:
        title: Judul embed
        description: Deskripsi embed
        color: Warna embed
        footer: Teks footer
        thumbnail: URL thumbnail
        image: URL gambar
        author: Dictionary dengan info author
        fields: List fields
        
    Returns:
        Discord.Embed object
    """
    embed = discord.Embed(title=title, description=description, color=color)
    
    if footer:
        embed.set_footer(text=footer)
    
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    if image:
        embed.set_image(url=image)
    
    if author and isinstance(author, dict):
        name = author.get('name', '')
        url = author.get('url', None)
        icon_url = author.get('icon_url', None)
        embed.set_author(name=name, url=url, icon_url=icon_url)
    
    if fields and isinstance(fields, list):
        for field in fields:
            if isinstance(field, dict) and 'name' in field and 'value' in field:
                inline = field.get('inline', False)
                embed.add_field(name=field['name'], value=field['value'], inline=inline)
    
    return embed 