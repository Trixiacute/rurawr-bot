"""
Paket core untuk bot Discord

Berisi modul-modul inti yang dibutuhkan untuk menjalankan bot.
"""

from src.core.config import *
from src.core.bot import RurawrBot
from src.core.database import MemoryDB

# Language configurations and translations
LANGUAGES = {
    "id": {
        "name": "Bahasa Indonesia",
        "native_name": "Bahasa Indonesia",
        "translations": {
            "general": {
                "yes": "Ya",
                "no": "Tidak",
                "success": "Berhasil",
                "error": "Error",
                "wait": "Mohon tunggu...",
                "loading": "Sedang memuat...",
                "not_found": "Tidak ditemukan"
            },
            "commands": {
                "help": {
                    "title": "Menu Bantuan",
                    "description": "Berikut adalah daftar perintah yang tersedia. Gunakan `{prefix}help <perintah>` untuk info lebih lanjut.",
                    "not_found": "Perintah `{command}` tidak ditemukan",
                    "usage": "Penggunaan",
                    "aliases": "Alias"
                },
                "ping": {
                    "title": "🏓 Pong!",
                    "description": "Latensi Bot: `{latency}ms`\nRound Trip: `{roundtrip}ms`"
                },
                "info": {
                    "title": "ℹ️ Tentang {bot_name}",
                    "stats": "📊 Statistik",
                    "technical": "💻 Teknis",
                    "creator": "👨‍💻 Pembuat"
                },
                "prefix": {
                    "current": "Prefix saat ini: `{prefix}`",
                    "changed": "Prefix telah diubah menjadi: `{prefix}`",
                    "error": "Tidak dapat mengubah prefix"
                },
                "language": {
                    "current": "Bahasa saat ini: `{language}`",
                    "changed": "Bahasa telah diubah menjadi: `{language}`",
                    "not_supported": "Bahasa `{language}` tidak didukung",
                    "available": "Bahasa yang tersedia: {languages}"
                },
                "anime": {
                    "loading": "🔍 Mencari anime...",
                    "not_found": "Anime tidak ditemukan",
                    "type": "📺 Tipe",
                    "episodes": "📊 Episode",
                    "status": "📡 Status",
                    "score": "⭐ Skor",
                    "popularity": "👥 Popularitas",
                    "year": "📅 Tahun",
                    "studio": "🎬 Studio",
                    "genres": "🏷️ Genre"
                },
                "waifu": {
                    "loading": "🖼️ Mengambil gambar waifu...",
                    "not_found": "Tidak dapat menemukan gambar waifu",
                    "category_not_found": "Kategori `{category}` tidak ditemukan",
                    "available_categories": "Kategori yang tersedia: {categories}"
                },
                "imsakiyah": {
                    "loading": "🔍 Mencari jadwal imsakiyah...",
                    "not_found": "Jadwal imsakiyah untuk kota `{city}` tidak ditemukan",
                    "city_not_specified": "Silakan tentukan nama kota",
                    "date": "📅 Tanggal",
                    "imsak": "🌙 Imsak",
                    "subuh": "🧎 Subuh",
                    "terbit": "🌅 Terbit",
                    "dzuhur": "☀️ Dzuhur",
                    "ashar": "🌤️ Ashar",
                    "maghrib": "🌆 Maghrib",
                    "isya": "🌃 Isya",
                    "title": "Jadwal Imsakiyah {city}"
                },
                "stats": {
                    "title": "📊 Statistik Penggunaan Bot",
                    "description": "Berikut adalah statistik penggunaan perintah bot:",
                    "top_commands": "🔝 Perintah Terpopuler",
                    "general_stats": "🔢 Statistik Umum",
                    "no_data": "Belum ada data penggunaan perintah"
                },
                "invite": {
                    "title": "🔗 Invite Bot",
                    "description": "Gunakan link berikut untuk mengundang bot ke server Anda:",
                    "link": "📨 Link Invite"
                }
            },
            "errors": {
                "generic": "Terjadi kesalahan: {error}",
                "command_not_found": "Perintah tidak ditemukan",
                "missing_permissions": "Anda tidak memiliki izin untuk melakukan ini",
                "missing_arguments": "Argumen yang diperlukan tidak diberikan: {argument}",
                "bot_missing_permissions": "Bot tidak memiliki izin yang cukup untuk melakukan ini"
            }
        }
    },
    "en": {
        "name": "English",
        "native_name": "English",
        "translations": {
            "general": {
                "yes": "Yes",
                "no": "No",
                "success": "Success",
                "error": "Error",
                "wait": "Please wait...",
                "loading": "Loading...",
                "not_found": "Not found"
            },
            "commands": {
                "help": {
                    "title": "Help Menu",
                    "description": "Here is a list of available commands. Use `{prefix}help <command>` for more info.",
                    "not_found": "Command `{command}` not found",
                    "usage": "Usage",
                    "aliases": "Aliases"
                },
                "ping": {
                    "title": "🏓 Pong!",
                    "description": "Bot Latency: `{latency}ms`\nRound Trip: `{roundtrip}ms`"
                },
                "info": {
                    "title": "ℹ️ About {bot_name}",
                    "stats": "📊 Statistics",
                    "technical": "💻 Technical",
                    "creator": "👨‍💻 Creator"
                },
                "prefix": {
                    "current": "Current prefix: `{prefix}`",
                    "changed": "Prefix has been changed to: `{prefix}`",
                    "error": "Could not change prefix"
                },
                "language": {
                    "current": "Current language: `{language}`",
                    "changed": "Language has been changed to: `{language}`",
                    "not_supported": "Language `{language}` is not supported",
                    "available": "Available languages: {languages}"
                },
                "anime": {
                    "loading": "🔍 Searching for anime...",
                    "not_found": "Anime not found",
                    "type": "📺 Type",
                    "episodes": "📊 Episodes",
                    "status": "📡 Status",
                    "score": "⭐ Score",
                    "popularity": "👥 Popularity",
                    "year": "📅 Year",
                    "studio": "🎬 Studio",
                    "genres": "🏷️ Genres"
                },
                "waifu": {
                    "loading": "🖼️ Fetching waifu image...",
                    "not_found": "Could not find waifu image",
                    "category_not_found": "Category `{category}` not found",
                    "available_categories": "Available categories: {categories}"
                },
                "imsakiyah": {
                    "loading": "🔍 Searching for imsakiyah schedule...",
                    "not_found": "Imsakiyah schedule for city `{city}` not found",
                    "city_not_specified": "Please specify a city name",
                    "date": "📅 Date",
                    "imsak": "🌙 Imsak",
                    "subuh": "🧎 Fajr",
                    "terbit": "🌅 Sunrise",
                    "dzuhur": "☀️ Dhuhr",
                    "ashar": "🌤️ Asr",
                    "maghrib": "🌆 Maghrib",
                    "isya": "🌃 Isha",
                    "title": "Imsakiyah Schedule for {city}"
                },
                "stats": {
                    "title": "📊 Bot Usage Statistics",
                    "description": "Here are the bot command usage statistics:",
                    "top_commands": "🔝 Top Commands",
                    "general_stats": "🔢 General Stats",
                    "no_data": "No command usage data yet"
                },
                "invite": {
                    "title": "🔗 Invite Bot",
                    "description": "Use the following link to invite the bot to your server:",
                    "link": "📨 Invite Link"
                }
            },
            "errors": {
                "generic": "An error occurred: {error}",
                "command_not_found": "Command not found",
                "missing_permissions": "You don't have permission to do this",
                "missing_arguments": "Required argument not provided: {argument}",
                "bot_missing_permissions": "Bot doesn't have enough permissions to do this"
            }
        }
    }
}

def get_available_languages():
    """
    Get list of available languages
    
    Returns:
        List of language codes
    """
    return list(LANGUAGES.keys())

def get_language_name(language_code):
    """
    Get the name of a language
    
    Args:
        language_code: The language code
        
    Returns:
        Language name or None if not found
    """
    if language_code in LANGUAGES:
        return LANGUAGES[language_code]["name"]
    return None

def get_native_language_name(language_code):
    """
    Get the native name of a language
    
    Args:
        language_code: The language code
        
    Returns:
        Native language name or None if not found
    """
    if language_code in LANGUAGES:
        return LANGUAGES[language_code]["native_name"]
    return None 