"""
config.py - File konfigurasi utama bot

Berisi konstanta-konstanta dan konfigurasi utama yang digunakan 
di seluruh aplikasi bot Discord.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot token (required)
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("DISCORD_TOKEN tidak ditemukan di file .env. Silakan tambahkan token bot Discord Anda.")

# Default prefix if not set for a server
DEFAULT_PREFIX = "!"

# Default language if not set for a server
DEFAULT_LANGUAGE = "id"

# Warna untuk embed Discord
EMBED_COLORS = {
    "primary": 0x3498db,    # Biru
    "success": 0x2ecc71,    # Hijau
    "warning": 0xf1c40f,    # Kuning
    "error": 0xe74c3c,      # Merah
    "info": 0x9b59b6,       # Ungu
    "neutral": 0x95a5a6     # Abu-abu
}

# Informasi bot
BOT_INFO = {
    "name": "Rurawr Bot",
    "version": "1.2.0",
    "description": "Bot multifungsi dengan fitur anime dan jadwal imsakiyah",
    "author": "Bot ini dibuat oleh **Kezia**",
    "github": "https://github.com/username/rurawr-bot",
    "support_server": "https://discord.gg/support"
}

# Format waktu
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# URL API untuk Waifu
WAIFU_API_URL = "https://api.waifu.pics/"
WAIFU_CATEGORIES = {
    "sfw": ["waifu", "neko", "shinobu", "megumin", "bully", "cuddle", "hug", "kiss", "pat", "smug", "bonk", "smile", "wave"],
    "nsfw": [] # Dikosongkan untuk bot SFW
}

# Logger configuration
LOGGING_CONFIG = {
    "format": "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
    "level": "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
}

# Path-path penting
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "src", "data")

# Pastikan direktori data ada
os.makedirs(DATA_DIR, exist_ok=True)

# Command cooldowns (seconds)
COOLDOWNS = {
    "general": 3,
    "anime": 5,
    "waifu": 3,
    "imsakiyah": 5
} 