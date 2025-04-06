"""
rich_presence.py - Module untuk manajemen Discord Rich Presence

Module ini menyediakan fungsi untuk mengatur Rich Presence
yang lebih dinamis dan informatif pada bot Discord.
"""

import discord
import asyncio
import random
from datetime import datetime
import platform
from typing import List, Dict, Any, Optional

class RichPresence:
    def __init__(self, bot):
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
        except Exception as e:
            print(f"[ERROR] Failed to update presence: {e}")
    
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
        
        return formatted
    
    def _get_uptime(self) -> str:
        """
        Mendapatkan uptime dalam format yang readable
        
        Returns:
            String uptime
        """
        # This requires bot.start_time to be set when bot starts
        # If you don't have it, you can add:
        # bot.start_time = datetime.now() in on_ready event
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
            return "!"  # Default if prefix is a callable
        return self.bot.command_prefix
    
    def _get_version(self) -> str:
        """
        Mendapatkan versi bot
        
        Returns:
            String versi
        """
        # Check if BOT_INFO is available
        if hasattr(self.bot, 'version'):
            return self.bot.version
        
        # Try to import from a constants file
        try:
            from constants import BOT_INFO
            return BOT_INFO.get('version', '1.0.0')
        except (ImportError, AttributeError):
            return "1.0.0"
    
    async def start_presence_loop(self) -> None:
        """
        Memulai loop untuk mengubah status secara periodik
        """
        while True:
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
                print(f"[ERROR] Error in presence loop: {e}")
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
    
    # Register events
    @bot.event
    async def on_ready():
        # Start the presence loop
        bot.loop.create_task(presence_manager.start_presence_loop())
        
        # Log startup info
        print(f"\n{'='*50}")
        print(f"Bot is ready! Logged in as {bot.user.name} (ID: {bot.user.id})")
        print(f"Connected to {len(bot.guilds)} guilds | Serving {len(set(bot.get_all_members()))} users")
        print(f"Python version: {platform.python_version()}")
        print(f"Discord.py version: {discord.__version__}")
        print(f"Running on: {platform.system()} {platform.release()}")
        print(f"Rich Presence enabled: Rotating between {len(presence_manager.presence_list)} statuses")
        print(f"{'='*50}\n")
        
        print("Bot is fully operational!")
    
    print("[INFO] Rich Presence module loaded successfully") 