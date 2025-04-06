"""
database.py - Modul database untuk bot Discord

Berisi implementasi kelas untuk mengelola data dalam memori
atau file JSON sederhana.
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List, Union

from src.core.config import DATA_DIR

logger = logging.getLogger("database")

class Database:
    """
    Kelas Database untuk menyimpan dan mengelola data bot
    """
    def __init__(self, filename: str = "database.json"):
        """
        Inisialisasi database
        
        Args:
            filename: Nama file untuk menyimpan data
        """
        self.filename = os.path.join(DATA_DIR, filename)
        self.data = self._load_data()
        
        # Setup default structure
        if "settings" not in self.data:
            self.data["settings"] = {
                "guilds": {},
                "users": {}
            }
        
        if "stats" not in self.data:
            self.data["stats"] = {
                "commands": {},
                "total_commands": 0,
                "start_time": time.time()
            }
        
        if "cache" not in self.data:
            self.data["cache"] = {}
        
        # Simpan struktur default
        self._save_data()
        
    def _load_data(self) -> Dict[str, Any]:
        """
        Memuat data dari file
        
        Returns:
            Dictionary berisi data
        """
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Gagal memuat database: {e}")
                # Buat backup file yang rusak
                if os.path.exists(self.filename):
                    backup_file = f"{self.filename}.bak"
                    os.rename(self.filename, backup_file)
                    logger.info(f"File database yang rusak dipindahkan ke {backup_file}")
        
        return {}
    
    def _save_data(self) -> None:
        """Menyimpan data ke file"""
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Gagal menyimpan database: {e}")
    
    # -- Server Settings --
    
    def get_guild_setting(self, guild_id: int, key: str, default: Any = None) -> Any:
        """
        Mendapatkan pengaturan server
        
        Args:
            guild_id: ID server Discord
            key: Kunci pengaturan
            default: Nilai default jika tidak ditemukan
            
        Returns:
            Nilai pengaturan atau default
        """
        guild_id = str(guild_id)  # Convert to string for JSON
        if guild_id not in self.data["settings"]["guilds"]:
            return default
        
        return self.data["settings"]["guilds"][guild_id].get(key, default)
    
    def set_guild_setting(self, guild_id: int, key: str, value: Any) -> None:
        """
        Mengatur pengaturan server
        
        Args:
            guild_id: ID server Discord
            key: Kunci pengaturan
            value: Nilai yang akan disimpan
        """
        guild_id = str(guild_id)  # Convert to string for JSON
        if guild_id not in self.data["settings"]["guilds"]:
            self.data["settings"]["guilds"][guild_id] = {}
        
        self.data["settings"]["guilds"][guild_id][key] = value
        self._save_data()
    
    def get_prefix(self, guild_id: Optional[int], default_prefix: str = "!") -> str:
        """
        Mendapatkan prefix untuk server
        
        Args:
            guild_id: ID server Discord atau None untuk DM
            default_prefix: Prefix default jika tidak diatur
            
        Returns:
            String prefix
        """
        if guild_id is None:  # DMs
            return default_prefix
        
        return self.get_guild_setting(guild_id, "prefix", default_prefix)
    
    def set_prefix(self, guild_id: int, prefix: str) -> None:
        """
        Mengatur prefix untuk server
        
        Args:
            guild_id: ID server Discord
            prefix: Prefix baru
        """
        self.set_guild_setting(guild_id, "prefix", prefix)
    
    def get_language(self, guild_id: Optional[int], default_lang: str = "id") -> str:
        """
        Mendapatkan bahasa untuk server
        
        Args:
            guild_id: ID server Discord atau None untuk DM
            default_lang: Bahasa default jika tidak diatur
            
        Returns:
            String kode bahasa
        """
        if guild_id is None:  # DMs
            return default_lang
        
        return self.get_guild_setting(guild_id, "language", default_lang)
    
    def set_language(self, guild_id: int, language: str) -> None:
        """
        Mengatur bahasa untuk server
        
        Args:
            guild_id: ID server Discord
            language: Kode bahasa baru
        """
        self.set_guild_setting(guild_id, "language", language)
    
    # -- Command Stats --
    
    def log_command(self, user_id: int, guild_id: Optional[int], command: str) -> None:
        """
        Mencatat penggunaan command
        
        Args:
            user_id: ID pengguna Discord
            guild_id: ID server Discord atau None untuk DM
            command: Nama command
        """
        # Update command stats
        if command not in self.data["stats"]["commands"]:
            self.data["stats"]["commands"][command] = 0
        
        self.data["stats"]["commands"][command] += 1
        self.data["stats"]["total_commands"] += 1
        
        # Save changes
        self._save_data()
    
    def get_command_stats(self) -> Dict[str, int]:
        """
        Mendapatkan statistik penggunaan command
        
        Returns:
            Dictionary dengan nama command dan jumlah penggunaan
        """
        return self.data["stats"]["commands"]
    
    def get_total_commands(self) -> int:
        """
        Mendapatkan total command yang digunakan
        
        Returns:
            Integer jumlah total
        """
        return self.data["stats"]["total_commands"]
    
    # -- Cache --
    
    def set_cache(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        """
        Menyimpan data ke cache
        
        Args:
            key: Kunci cache
            value: Nilai yang akan disimpan
            expire: Waktu kedaluwarsa dalam detik, None untuk tidak kedaluwarsa
        """
        cache_entry = {
            "value": value,
            "created_at": time.time()
        }
        
        if expire is not None:
            cache_entry["expire_at"] = time.time() + expire
        
        self.data["cache"][key] = cache_entry
        self._save_data()
    
    def get_cache(self, key: str, default: Any = None) -> Any:
        """
        Mendapatkan data dari cache
        
        Args:
            key: Kunci cache
            default: Nilai default jika tidak ditemukan atau kedaluwarsa
            
        Returns:
            Nilai cache atau default
        """
        if key not in self.data["cache"]:
            return default
        
        cache_entry = self.data["cache"][key]
        
        # Check expiration
        if "expire_at" in cache_entry and time.time() > cache_entry["expire_at"]:
            del self.data["cache"][key]
            self._save_data()
            return default
        
        return cache_entry["value"]
    
    def clear_cache(self, key: Optional[str] = None) -> None:
        """
        Menghapus data dari cache
        
        Args:
            key: Kunci cache atau None untuk menghapus semua
        """
        if key is None:
            self.data["cache"] = {}
        elif key in self.data["cache"]:
            del self.data["cache"][key]
        
        self._save_data()
    
    def clean_expired_cache(self) -> int:
        """
        Membersihkan cache yang kedaluwarsa
        
        Returns:
            Jumlah entri yang dihapus
        """
        count = 0
        now = time.time()
        
        keys_to_delete = []
        for key, entry in self.data["cache"].items():
            if "expire_at" in entry and now > entry["expire_at"]:
                keys_to_delete.append(key)
                count += 1
        
        for key in keys_to_delete:
            del self.data["cache"][key]
        
        if count > 0:
            self._save_data()
        
        return count

# Initialize database
db = Database() 