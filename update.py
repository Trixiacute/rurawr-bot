import discord
from discord.ext import commands
import asyncio
from datetime import datetime
from constants import EMBED_COLORS, BOT_INFO

class UpdateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="update")
    async def update_command(self, ctx):
        """Menampilkan pembaruan terbaru dari Ruri-chan"""
        guild_id = ctx.guild.id if ctx.guild else None
        
        # Create embed to show recent updates
        embed = discord.Embed(
            title="🆕 Pembaruan Terbaru Ruri-chan",
            description=(
                f"Hai {ctx.author.mention}! Berikut adalah pembaruan fitur terbaru yang telah "
                f"ditambahkan ke Ruri-chan. Reaksi akan ditambahkan otomatis jika kamu telah membaca update ini~"
            ),
            color=EMBED_COLORS["primary"]
        )
        
        # Add update history with dates (newest first)
        embed.add_field(
            name="📅 07 April 2025 - Perbaikan Bug & Peningkatan Sistem",
            value=(
                "• 🛠️ Mengatasi masalah perintah yang dijalankan 2 kali\n"
                "• 🗄️ Perbaikan sistem database dan optimasi memory\n"
                "• 📊 Penambahan perintah `!dbstatus` dan `!dbrebuild`\n"
                "• 🕌 Peningkatan tampilan jadwal imsakiyah\n"
                "• 🆕 Penambahan perintah `!update` untuk menampilkan pembaruan terbaru"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📅 01 April 2025 - Penambahan Fitur Anime",
            value=(
                "• 🎬 Perintah `!anime` untuk mencari info anime dari berbagai database\n"
                "• 🔍 Dukungan pencarian berdasarkan judul atau ID\n"
                "• 📚 Integrasi dengan Kitsu, MyAnimeList, AniList, dan lainnya\n"
                "• 🖼️ Tampilan baru untuk hasil pencarian anime"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📅 25 Maret 2025 - Fitur Bahasa Baru",
            value=(
                "• 🌐 Dukungan untuk 4 bahasa (Indonesia, Inggris, Jepang, Korea)\n"
                "• 🎭 Penambahan kategori reaksi anime baru\n"
                "• 👋 Pesan sambutan server yang lebih menarik\n"
                "• 🖌️ Tampilan pesan yang lebih cantik dan colorful"
            ),
            inline=False
        )
        
        # Add planned future updates
        embed.add_field(
            name="🔮 Fitur yang Akan Datang",
            value=(
                "• 🎵 Integrasi fitur musik untuk server\n"
                "• 🎮 Game sederhana yang bisa dimainkan di Discord\n"
                "• 📱 Notifikasi anime terbaru\n"
                "• 🌱 Sistem level dan XP untuk pengguna aktif\n"
                "• 🏆 Sistem ranking dan leaderboard server"
            ),
            inline=False
        )
        
        # Add user feedback request
        embed.add_field(
            name="💌 Ingin Fitur Baru?",
            value=(
                "Punya ide untuk fitur baru? Atau menemukan bug?\n"
                f"Silakan hubungi {BOT_INFO['creator']} untuk memberikan saran dan masukan!"
            ),
            inline=False
        )
        
        # Add bot info and contact
        embed.set_footer(
            text=f"Ruri-chan v{BOT_INFO['version']} • Dibuat oleh {BOT_INFO['creator']}",
            icon_url=ctx.bot.user.avatar.url if ctx.bot.user.avatar else None
        )
        
        # Set a cute thumbnail
        embed.set_thumbnail(url="https://media.tenor.com/NcBVpmY9GVgAAAAC/ruri-dragon-girl.gif")
        
        # Send the message and add reactions
        message = await ctx.send(embed=embed)
        
        # Add reactions to indicate the user has read the update
        reactions = ["🆕", "👍", "❤️", "🎉"]
        for reaction in reactions:
            try:
                await message.add_reaction(reaction)
                await asyncio.sleep(0.5)  # Add small delay to avoid rate limiting
            except:
                pass  # Ignore errors if reaction can't be added
        
        # Log command usage
        try:
            from database import log_command
            log_command(ctx.guild.id, ctx.author.id, "update", success=True)
        except Exception as e:
            print(f"Error logging update command: {e}")

async def setup(bot):
    await bot.add_cog(UpdateCommand(bot))
