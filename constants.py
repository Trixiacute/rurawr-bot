"""
constants.py - Modul konstanta untuk bot Discord

Modul ini berisi konstanta-konstanta yang digunakan di berbagai
bagian aplikasi bot Discord.
"""

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

# URL API untuk Waifu
WAIFU_API_URL = "https://api.waifu.pics/"
WAIFU_CATEGORIES = {
    "sfw": ["waifu", "neko", "shinobu", "megumin", "bully", "cuddle", "hug", "kiss", "pat", "smug", "bonk", "smile", "wave"],
    "nsfw": [] # Dikosongkan untuk bot SFW
}

# Deskripsi command
COMMAND_DESCRIPTIONS = {
    "help": "Menampilkan daftar perintah yang tersedia atau informasi tentang perintah tertentu",
    "help_usage": "help [command]",
    
    "ping": "Memeriksa latensi bot dan waktu respons",
    
    "info": "Menampilkan informasi tentang bot",
    
    "stats": "Menampilkan statistik penggunaan bot (hanya admin)",
    
    "invite": "Mendapatkan link untuk mengundang bot ke server lain",
    
    "prefix": "Mengubah prefix command untuk server ini",
    "prefix_usage": "prefix <new_prefix>",
    
    "language": "Mengubah bahasa bot untuk server ini",
    "language_usage": "language <id|en>",
    
    "anime": "Mencari informasi anime",
    "anime_usage": "anime <judul>",
    
    "waifu": "Mendapatkan gambar waifu acak",
    "waifu_usage": "waifu [category]",
    
    "imsakiyah": "Menampilkan jadwal imsakiyah",
    "imsakiyah_usage": "imsakiyah <kota>",
    
    "imsak": "Alias untuk command imsakiyah",
    
    "jadwal": "Menampilkan jadwal imsakiyah (alias untuk imsakiyah)"
}

# Format waktu
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Teks bantuan
HELP_TEXT = {
    "id": """
**Perintah Dasar:**
`{prefix}help` - Menampilkan daftar perintah
`{prefix}ping` - Memeriksa latensi bot
`{prefix}info` - Informasi tentang bot

**Pengaturan:**
`{prefix}prefix <new_prefix>` - Mengubah prefix bot
`{prefix}language <id|en>` - Mengubah bahasa

**Fitur Anime:**
`{prefix}anime <judul>` - Mencari info anime
`{prefix}waifu [category]` - Gambar waifu acak

**Fitur Islami:**
`{prefix}imsakiyah <kota>` - Jadwal imsakiyah
""",
    
    "en": """
**Basic Commands:**
`{prefix}help` - Show command list
`{prefix}ping` - Check bot latency
`{prefix}info` - Bot information

**Settings:**
`{prefix}prefix <new_prefix>` - Change bot prefix
`{prefix}language <id|en>` - Change language

**Anime Features:**
`{prefix}anime <title>` - Search anime info
`{prefix}waifu [category]` - Random waifu image

**Islamic Features:**
`{prefix}imsakiyah <city>` - Imsakiyah schedule
"""
} 