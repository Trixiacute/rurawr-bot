"""
bot.py - Inisialisasi utama bot Discord

Modul ini menangani inisialisasi dan konfigurasi bot Discord.
"""

import os
import sys
import signal
import logging
import importlib
from datetime import datetime
from typing import List, Optional, Callable, Dict, Any

import discord
from discord.ext import commands

from src.core.config import TOKEN, DEFAULT_PREFIX, LOGGING_CONFIG, BOT_INFO
from src.core.database import db

# Setup logging
logging.basicConfig(
    format=LOGGING_CONFIG["format"],
    datefmt=LOGGING_CONFIG["datefmt"],
    level=getattr(logging, LOGGING_CONFIG["level"])
)
logger = logging.getLogger("bot")

# Custom prefix getter
def get_prefix(bot, message):
    """
    Mendapatkan prefix untuk pesan yang diterima
    
    Args:
        bot: Instance bot
        message: Pesan yang diterima
        
    Returns:
        String prefix
    """
    if message.guild:
        return db.get_prefix(message.guild.id, DEFAULT_PREFIX)
    return DEFAULT_PREFIX

# Initialize bot with intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

# Handle shutdowns gracefully
def handle_exit(signum, frame):
    """
    Menangani signal untuk keluar dari program dengan baik
    
    Args:
        signum: Nomor signal
        frame: Current stack frame
    """
    logger.info(f"Menerima signal {signum}, mematikan bot dengan baik...")
    
    # Cleanup if needed
    # db._save_data()  # Make sure all data is saved
    
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# Set start time for uptime calculation
bot.start_time = datetime.now()
bot.version = BOT_INFO.get('version', '1.0.0')

@bot.event
async def on_ready():
    """Event yang dipanggil saat bot siap"""
    logger.info(f"Bot siap! Masuk sebagai {bot.user.name} (ID: {bot.user.id})")
    logger.info(f"Terhubung ke {len(bot.guilds)} server | Melayani {len(set(bot.get_all_members()))} pengguna")

@bot.event
async def on_message(message):
    """
    Event yang dipanggil saat ada pesan baru
    
    Args:
        message: Pesan Discord yang diterima
    """
    # Ignore messages from bots
    if message.author.bot:
        return
    
    # Process commands
    await bot.process_commands(message)

def load_extensions(extension_list: List[str]) -> Dict[str, bool]:
    """
    Memuat ekstensi bot
    
    Args:
        extension_list: Daftar nama ekstensi untuk dimuat
        
    Returns:
        Dictionary dengan nama ekstensi dan status pemuatan
    """
    results = {}
    for extension in extension_list:
        try:
            bot.load_extension(extension)
            logger.info(f"Ekstensi dimuat: {extension}")
            results[extension] = True
        except Exception as e:
            logger.error(f"Gagal memuat ekstensi {extension}: {e}")
            results[extension] = False
    
    return results

def run_bot():
    """Menjalankan bot Discord"""
    # List of extensions to load
    extensions = [
        "src.core.presence",
        "src.commands.general.help",
        "src.commands.general.info",
        "src.commands.general.ping",
        "src.commands.general.stats",
        "src.commands.general.invite",
        "src.commands.settings.prefix",
        "src.commands.settings.language",
        "src.commands.anime.anime",
        "src.commands.anime.waifu",
        "src.commands.islamic.imsakiyah"
    ]
    
    # Load all extensions
    load_results = load_extensions(extensions)
    
    # Log any failed extensions
    failed = [ext for ext, success in load_results.items() if not success]
    if failed:
        logger.warning(f"Gagal memuat {len(failed)} ekstensi: {', '.join(failed)}")
    
    # Run the bot
    try:
        logger.info(f"Memulai bot: {BOT_INFO['name']} v{BOT_INFO['version']}...")
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        logger.critical("Token Discord tidak valid. Cek file .env Anda.")
        sys.exit(1)
    except discord.errors.PrivilegedIntentsRequired:
        logger.critical("Intents yang diperlukan tidak diaktifkan. Aktifkan intents di Discord Developer Portal.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Error saat menjalankan bot: {e}")
        sys.exit(1) 