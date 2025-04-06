import discord
from discord.ext import commands
import aiohttp
import asyncio
from typing import Optional, Dict, Any
import json
import random

SCHOOL_API_URL = "https://api-sekolah-indonesia.vercel.app"
SCHOOL_TYPES = {
    "sd": {
        "name": "Sekolah Dasar",
        "emoji": "🎓",
        "description": "Pendidikan dasar untuk usia 7-12 tahun",
        "color": 0x4CAF50  # Hijau
    },
    "smp": {
        "name": "Sekolah Menengah Pertama",
        "emoji": "📚",
        "description": "Pendidikan menengah pertama untuk usia 13-15 tahun",
        "color": 0x2196F3  # Biru
    },
    "sma": {
        "name": "Sekolah Menengah Atas",
        "emoji": "🏛️",
        "description": "Pendidikan menengah atas untuk usia 16-18 tahun",
        "color": 0x9C27B0  # Ungu
    },
    "smk": {
        "name": "Sekolah Menengah Kejuruan",
        "emoji": "⚙️",
        "description": "Pendidikan kejuruan untuk persiapan kerja",
        "color": 0xFF9800  # Oranye
    }
}

class SchoolNavigationView(discord.ui.View):
    def __init__(self, schools: list, page: int = 1, items_per_page: int = 5, school_type: str = None):
        super().__init__(timeout=60)
        self.schools = schools
        self.page = page
        self.items_per_page = items_per_page
        self.total_pages = (len(schools) + items_per_page - 1) // items_per_page
        self.school_type = school_type
        self.update_buttons()
    
    def update_buttons(self):
        self.previous_page.disabled = self.page <= 1
        self.next_page.disabled = self.page >= self.total_pages
    
    def get_page_schools(self):
        start_idx = (self.page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        return self.schools[start_idx:end_idx]
    
    def create_embed(self, title: str) -> discord.Embed:
        school_type_info = SCHOOL_TYPES.get(self.school_type.lower()) if self.school_type else None
        embed_color = school_type_info["color"] if school_type_info else 0x3498db
        
        embed = discord.Embed(
            title=f"{school_type_info['emoji'] if school_type_info else '🏫'} {title}",
            description=f"✨ Ditemukan {len(self.schools)} sekolah",
            color=embed_color
        )
        
        for school in self.get_page_schools():
            status_emoji = "🏛️" if school.get('status') == "N" else "🏢"
            status_text = "Negeri" if school.get('status') == "N" else "Swasta"
            
            # Create a more aesthetic field layout
            school_name = school.get('sekolah', 'Nama tidak tersedia')
            field_value = (
                f"```yaml\n"
                f"Status    : {status_emoji} {status_text}\n"
                f"NPSN      : {school.get('npsn', '-')}\n"
                f"Alamat    : {school.get('alamat_jalan', '-')}\n"
                f"Kecamatan : {school.get('kecamatan', '-')}\n"
                f"Kota      : {school.get('kabupaten_kota', '-')}\n"
                f"Provinsi  : {school.get('provinsi', '-')}\n"
                "```"
            )
            
            embed.add_field(
                name=f"📍 {school_name}",
                value=field_value,
                inline=False
            )
        
        # Add aesthetic footer with page info and tips
        tips = [
            "💡 Gunakan tombol navigasi untuk melihat hasil lainnya",
            "🔍 Coba cari dengan NPSN untuk hasil lebih spesifik",
            "📱 Informasi kontak tersedia di detail sekolah"
        ]
        
        embed.set_footer(
            text=f"📖 Halaman {self.page} dari {self.total_pages} • {random.choice(tips)}"
        )
        
        if school_type_info:
            embed.set_author(
                name=f"{school_type_info['name']} ({self.school_type.upper()})",
                icon_url="https://cdn-icons-png.flaticon.com/512/8074/8074800.png"
            )
        
        return embed
    
    @discord.ui.button(
        label="◀️", 
        style=discord.ButtonStyle.secondary,
        custom_id="previous"
    )
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(
            embed=self.create_embed("Hasil Pencarian Sekolah"),
            view=self
        )
    
    @discord.ui.button(
        label="▶️",
        style=discord.ButtonStyle.secondary,
        custom_id="next"
    )
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(
            embed=self.create_embed("Hasil Pencarian Sekolah"),
            view=self
        )

class SchoolView(discord.ui.View):
    def __init__(self, guild_id, get_text_func):
        super().__init__(timeout=60)
        self.add_item(SchoolTypeSelect(guild_id, get_text_func))

class SchoolTypeSelect(discord.ui.Select):
    def __init__(self, guild_id, get_text_func):
        self.get_text = get_text_func
        self.guild_id = guild_id
        options = []
        
        for school_type, info in SCHOOL_TYPES.items():
            option = discord.SelectOption(
                label=info["name"],
                description=info["description"],
                value=school_type,
                emoji=info["emoji"]
            )
            options.append(option)
            
        super().__init__(
            placeholder="🎓 Pilih Jenis Sekolah...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="school_type_select"
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            school_type = self.values[0].lower()
            
            # Create loading embed
            loading_embed = discord.Embed(
                title=f"{SCHOOL_TYPES[school_type]['emoji']} Mencari Sekolah...",
                description="```yaml\nStatus: Mengambil data dari server...\nMohon tunggu sebentar...```",
                color=SCHOOL_TYPES[school_type]['color']
            )
            loading_embed.set_footer(text="🔄 Memproses permintaan...")
            
            await interaction.followup.send(embed=loading_embed, ephemeral=False)
            
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"{SCHOOL_API_URL}/sekolah/{school_type.upper()}"
                    print(f"[DEBUG] Fetching schools with URL: {url}")
                    
                    async with session.get(url, params={"page": 1, "perPage": 25}) as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"[DEBUG] API response type: {type(data)}")
                            
                            if isinstance(data, dict) and "dataSekolah" in data:
                                schools = data["dataSekolah"]
                            else:
                                schools = data if isinstance(data, list) else []
                            
                            print(f"[DEBUG] Found {len(schools)} schools")
                            
                            if not schools or len(schools) == 0:
                                error_embed = discord.Embed(
                                    title="❌ Tidak Ditemukan",
                                    description=f"```diff\n- Tidak ada {SCHOOL_TYPES[school_type]['name']} yang ditemukan\n```",
                                    color=0xFF5252
                                )
                                await interaction.followup.send(embed=error_embed, ephemeral=False)
                                return
                            
                            view = SchoolNavigationView(schools, school_type=school_type)
                            embed = view.create_embed(f"Hasil Pencarian {SCHOOL_TYPES[school_type]['name']}")
                            await interaction.followup.send(embed=embed, view=view)
                            
                        else:
                            error_embed = discord.Embed(
                                title="❌ Error",
                                description=f"```diff\n- API mengembalikan kode {response.status}\n```",
                                color=0xFF5252
                            )
                            await interaction.followup.send(embed=error_embed, ephemeral=False)
                
            except Exception as e:
                print(f"[ERROR] Error in SchoolTypeSelect callback (API request): {e}")
                import traceback
                traceback.print_exc()
                
                error_embed = discord.Embed(
                    title="❌ Error",
                    description=f"```diff\n- Gagal mengambil data: {str(e)}\n```",
                    color=0xFF5252
                )
                await interaction.followup.send(embed=error_embed, ephemeral=False)
                
        except Exception as e:
            print(f"[ERROR] Error in SchoolTypeSelect callback: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                error_embed = discord.Embed(
                    title="❌ Error",
                    description=f"Terjadi kesalahan: {str(e)}",
                    color=0xFF5252
                )
                await interaction.followup.send(embed=error_embed, ephemeral=False)
            except:
                # If we can't send a followup, try to edit the original response
                try:
                    await interaction.edit_original_response(
                        content="Terjadi kesalahan saat menjalankan perintah. Silakan coba lagi."
                    )
                except:
                    pass

class SchoolCommands(commands.Cog):
    """🔍 Utility commands for searching schools in Indonesia"""
    
    def __init__(self, bot, get_text_func):
        self.bot = bot
        self.get_text = get_text_func
        print("[DEBUG] SchoolCommands cog initialized")

    # Create a group command for school-related commands
    @commands.group(name="sekolah", invoke_without_command=True)
    async def sekolah(self, ctx):
        """🏫 Search for schools in Indonesia"""
        try:
            guild_id = ctx.guild.id if ctx.guild else None
            
            embed = discord.Embed(
                title="🏫 Info Sekolah Indonesia",
                description="Cari dan temukan informasi sekolah di seluruh Indonesia!",
                color=0x3498db
            )
            
            embed.add_field(
                name="🔍 Cari berdasarkan Jenis Sekolah",
                value="Klik tombol di bawah untuk mencari berdasarkan jenis sekolah",
                inline=False
            )
            
            embed.add_field(
                name="🔢 Cari berdasarkan NPSN",
                value=f"Gunakan command `!sekolah npsn <nomor_npsn>`\nContoh: `!sekolah npsn 20539960`",
                inline=False
            )
            
            embed.add_field(
                name="🔤 Cari berdasarkan Nama",
                value=f"Gunakan command `!sekolah nama <nama_sekolah>`\nContoh: `!sekolah nama smk negeri 1`",
                inline=False
            )
            
            view = discord.ui.View()
            view.add_item(SchoolTypeSelect(guild_id, self.get_text))
            
            await ctx.send(embed=embed, view=view)
        except Exception as e:
            print(f"[ERROR] Error in sekolah command: {e}")
            import traceback
            traceback.print_exc()
            
            guild_id = ctx.guild.id if ctx.guild else None
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"Terjadi kesalahan saat menjalankan perintah sekolah: {str(e)}",
                color=0xFF5252
            )
            await ctx.send(embed=error_embed)

    @sekolah.command(name="nama")
    async def search_by_name(self, ctx, *, name: str):
        """🔤 Search for a school by name"""
        try:
            guild_id = ctx.guild.id if ctx.guild else None
            
            loading_msg = await ctx.send("🔍 Mencari sekolah... Mohon tunggu sebentar.")
            
            async with aiohttp.ClientSession() as session:
                search_term = name.strip()
                url = f"{SCHOOL_API_URL}/sekolah/s?sekolah={search_term}"
                
                print(f"[DEBUG] Searching for school with URL: {url}")
                
                async with session.get(url) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            
                            print(f"[DEBUG] API response type: {type(data)}")
                            
                            if isinstance(data, dict) and "dataSekolah" in data:
                                schools = data["dataSekolah"]
                            else:
                                schools = data if isinstance(data, list) else []
                            
                            print(f"[DEBUG] Found {len(schools)} schools")
                            
                            if not schools or len(schools) == 0:
                                await loading_msg.edit(content="❌ Tidak ada sekolah yang ditemukan dengan nama tersebut.")
                                return
                            
                            view = SchoolNavigationView(schools)
                            embed = view.create_embed("🔍 Hasil Pencarian Sekolah")
                            await loading_msg.edit(content=None, embed=embed, view=view)
                            
                        except Exception as e:
                            print(f"[ERROR] Error in search_by_name command (data processing): {e}")
                            import traceback
                            traceback.print_exc()
                            await loading_msg.edit(content=f"❌ Error: Format data tidak valid - {str(e)}")
                    else:
                        print(f"[ERROR] API returned status code: {response.status}")
                        await loading_msg.edit(content=f"❌ Error: API returned status code {response.status}")
        except Exception as e:
            print(f"[ERROR] Error in search_by_name command: {e}")
            import traceback
            traceback.print_exc()
            await ctx.send(f"❌ Terjadi kesalahan: {str(e)}")
    
    @sekolah.command(name="npsn")
    async def search_by_npsn(self, ctx, npsn: str):
        """🔢 Search for a school by NPSN number"""
        guild_id = ctx.guild.id if ctx.guild else None
        loading_msg = await ctx.send(self.get_text(guild_id, "school.loading"))
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{SCHOOL_API_URL}/sekolah/s?npsn={npsn}"
                async with session.get(url) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            
                            if isinstance(data, dict) and "dataSekolah" in data:
                                schools = data["dataSekolah"]
                            else:
                                schools = data if isinstance(data, list) else []
                            
                            if not schools or len(schools) == 0:
                                await loading_msg.edit(content=self.get_text(guild_id, "school.not_found"))
                                return
                            
                            school = schools[0]
                            status_emoji = "🏛️" if school.get('status') == "N" else "🏢"
                            status_text = "Negeri" if school.get('status') == "N" else "Swasta"
                            
                            embed = discord.Embed(
                                title=f"🏫 {self.get_text(guild_id, 'school.school_info')}",
                                color=0x3498db
                            )
                            
                            embed.add_field(
                                name="📝 Nama Sekolah",
                                value=f"🏫 {school.get('sekolah', 'Nama tidak tersedia')}",
                                inline=False
                            )
                            
                            embed.add_field(
                                name="ℹ️ Informasi Dasar",
                                value=(
                                    f"**{status_emoji} Status:** {status_text}\n"
                                    f"**🏛️ Jenis:** {school.get('bentuk', '-')}\n"
                                    f"**🔢 NPSN:** {school.get('npsn', '-')}"
                                ),
                                inline=False
                            )
                            
                            embed.add_field(
                                name="📍 Lokasi",
                                value=(
                                    f"**🏙️ Kota:** {school.get('kabupaten_kota', '-')}\n"
                                    f"**🗺️ Kecamatan:** {school.get('kecamatan', '-')}\n"
                                    f"**📮 Alamat:** {school.get('alamat_jalan', '-')}"
                                ),
                                inline=False
                            )
                            
                            await loading_msg.edit(content=None, embed=embed)
                        except Exception as e:
                            await loading_msg.edit(content=f"{self.get_text(guild_id, 'school.error')}: Invalid data format")
                    else:
                        await loading_msg.edit(content=self.get_text(guild_id, "school.error"))
        except Exception as e:
            await loading_msg.edit(content=f"{self.get_text(guild_id, 'school.error')}: {str(e)}")

async def setup(bot):
    """Add SchoolCommands cog to the bot"""
    try:
        # Initialize the cog with the bot and get_text function
        cog = SchoolCommands(bot, bot.get_text)
        await bot.add_cog(cog)
        print("[DEBUG] Successfully added SchoolCommands cog to the bot")
    except Exception as e:
        print(f"[ERROR] Error in setting up SchoolCommands cog: {e}")
        import traceback
        traceback.print_exc() 