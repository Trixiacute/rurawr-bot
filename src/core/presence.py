"""
presence.py - Module untuk manajemen Discord Rich Presence

Module ini menyediakan fungsi untuk mengatur Rich Presence
yang lebih dinamis dan informatif pada bot Discord.
"""

import discord
import asyncio
import platform
import logging
from datetime import datetime
from typing import Dict, Any, List

from src.core.bot import bot
from src.core.config import BOT_INFO

logger = logging.getLogger("presence")

class RichPresence:
    def __init__(self, bot):
        """
        Inisialisasi Rich Presence manager
        
        Args:
            bot: Bot instance Discord
        """
        self.bot = bot
        self.current_presence_index = 0
        self.presence_types = {
            "playing": discord.ActivityType.playing,
            "streaming": discord.ActivityType.streaming,
            "listening": discord.ActivityType.listening,
            "watching": discord.ActivityType.watching,
            "competing": discord.ActivityType.competing,
            "custom": discord.ActivityType.custom
        }
        
        # Daftar status yang akan dirotasi
        self.presence_list = [
            {"type": "watching", "name": "{guilds} server", "details": "Melayani {users} pengguna"},
            {"type": "listening", "name": "{prefix}help", "details": "untuk bantuan"},
            {"type": "playing", "name": "Anime & Jadwal Imsakiyah", "details": "Versi {version}"},
            {"type": "competing", "name": "layanan terbaik", "details": "Uptime: {uptime}"}
        ]
        
    async def update_presence(self, activity_data: Dict[str, Any]) -> None:
        """
        Memperbarui status rich presence bot
        
        Args:
            activity_data: Dictionary berisi informasi aktivitas
        """
        activity_type = self.presence_types.get(activity_data.get("type", "playing"), discord.ActivityType.playing)
        
        # Format placeholders in name
        name = activity_data.get("name", "Discord")
        name = self._format_presence_text(name)
        
        # Format details if present
        details = activity_data.get("details")
        if details:
            details = self._format_presence_text(details)
        
        # Create activity object
        if activity_type == discord.ActivityType.streaming:
            activity = discord.Streaming(name=name, url=activity_data.get("url", "https://www.twitch.tv/discord"))
        elif activity_type == discord.ActivityType.custom:
            activity = discord.CustomActivity(name=name)
        else:
            activity = discord.Activity(type=activity_type, name=name)
        
        # Set presence
        try:
            await self.bot.change_presence(activity=activity)
            logger.debug(f"Status berhasil diperbarui: {activity_type.name} {name}")
        except Exception as e:
            logger.error(f"Gagal memperbarui presence: {e}")
    
    def _format_presence_text(self, text: str) -> str:
        """
        Memformat teks presence dengan data dinamis
        
        Args:
            text: Teks dengan placeholder
            
        Returns:
            Teks terformat
        """
        uptime = self._get_uptime()
        version = self._get_version()
        
        try:
            # Replace placeholders
            formatted = text.format(
                guilds=len(self.bot.guilds),
                users=len(set(self.bot.get_all_members())),
                commands=len(self.bot.commands),
                prefix=self._get_default_prefix(),
                uptime=uptime,
                version=version,
                python=platform.python_version(),
                discord=discord.__version__
            )
        except KeyError as e:
            logger.warning(f"Format placeholder tidak valid dalam presence text: {e}")
            formatted = text
        except Exception as e:
            logger.error(f"Error saat memformat presence text: {e}")
            formatted = text
        
        return formatted
    
    def _get_uptime(self) -> str:
        """
        Mendapatkan uptime dalam format yang readable
        
        Returns:
            String uptime
        """
        if not hasattr(self.bot, 'start_time'):
            return "Unknown"
            
        now = datetime.now()
        delta = now - self.bot.start_time
        
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"
    
    def _get_default_prefix(self) -> str:
        """
        Mendapatkan default prefix bot
        
        Returns:
            String prefix
        """
        if callable(self.bot.command_prefix):
            return "!"
        return self.bot.command_prefix
    
    def _get_version(self) -> str:
        """
        Mendapatkan versi bot
        
        Returns:
            String versi
        """
        if hasattr(self.bot, 'version'):
            return self.bot.version
        
        return BOT_INFO.get('version', '1.0.0')
    
    async def start_presence_loop(self) -> None:
        """
        Memulai loop untuk mengubah status secara periodik
        """
        await self.bot.wait_until_ready()
        logger.info(f"Rich Presence loop dimulai dengan {len(self.presence_list)} status")
        
        while not self.bot.is_closed():
            try:
                # Get the presence data based on the current index
                presence = self.presence_list[self.current_presence_index]
                
                # Update the presence
                await self.update_presence(presence)
                
                # Increment the index for the next iteration
                self.current_presence_index = (self.current_presence_index + 1) % len(self.presence_list)
                
                # Wait before changing again (5 minutes)
                await asyncio.sleep(300)  # 5 minutes
            except Exception as e:
                logger.error(f"Error in presence loop: {e}")
                await asyncio.sleep(60)  # Wait a bit before retrying if there's an error

def setup(bot):
    """
    Setup function untuk fitur Rich Presence
    
    Args:
        bot: Bot instance Discord
    """
    # Initialize rich presence manager
    presence_manager = RichPresence(bot)
    
    # Store the presence manager on the bot for future use
    bot.presence_manager = presence_manager
    
    # Set bot start time if not already set
    if not hasattr(bot, 'start_time'):
        bot.start_time = datetime.now()
    
    # Start the presence loop
    bot.loop.create_task(presence_manager.start_presence_loop())
    
    logger.info("Rich Presence module loaded successfully") 