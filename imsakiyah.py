"""
Module imsakiyah - Menyediakan fungsionalitas jadwal imsakiyah untuk bot Discord.

Modul ini mengambil data jadwal dari API jadwalsholat.org dan menampilkannya
kepada pengguna dalam format yang mudah dibaca melalui Discord embeds dan
komponen UI interaktif.
"""

import json
import traceback
import re
from datetime import datetime, timedelta

import requests
import discord
import pytz
from discord.ext import commands

# Constants
API_BASE_URL = "https://raw.githubusercontent.com/lakuapik/jadwalsholatorg/master/kota.json"
ADZAN_API_BASE = "https://raw.githubusercontent.com/lakuapik/jadwalsholatorg/master/adzan"
EMBED_COLORS = {
    "primary": 0x3498db,  # Blue
    "success": 0x2ecc71,  # Green
    "warning": 0xf1c40f,  # Yellow
    "error": 0xe74c3c,    # Red
    "info": 0x9b59b6      # Purple
}

# UI Components for Imsakiyah
class RegionSelect(discord.ui.Select):
    """Component dropdown untuk memilih wilayah"""
    
    def __init__(self, regions, callback_func):
        self.callback_func = callback_func
        options = []
        
        for region_id, region_data in regions.items():
            options.append(
                discord.SelectOption(
                    label=region_data["name"],
                    description=f"{region_data['city_count']} kota",
                    emoji=region_data["emoji"],
                    value=region_id
                )
            )
        
        super().__init__(
            placeholder="📍 Pilih Wilayah...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="region_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Callback saat region dipilih"""
        await self.callback_func(interaction, self.values[0])

class CitySearchModal(discord.ui.Modal):
    """Modal untuk mencari kota dalam daftar"""
    
    def __init__(self, parent_view):
        super().__init__(title="🔍 Cari Kota")
        self.parent_view = parent_view
        
        # Add input field for search
        self.search_input = discord.ui.TextInput(
            label="Nama Kota",
            placeholder="Contoh: Jakarta, Bandung, dll",
            min_length=1,
            max_length=100,
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.search_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Menangani saat form pencarian dikirim"""
        # Get search query
        search_query = self.search_input.value.lower()
        
        # Find matching cities in the current region
        matching_cities = []
        for city in self.parent_view.cities:
            city_name = city.get('name', '').lower()
            if search_query in city_name:
                matching_cities.append(city)
        
        # If no matches, show message
        if not matching_cities:
            await interaction.response.send_message(
                f"❌ Tidak ada kota yang cocok dengan '{search_query}' di wilayah {self.parent_view.region_name}.",
                ephemeral=True
            )
            return
        
        # Create new view with filtered cities
        filtered_view = CitiesPageView(
            cities=matching_cities,
            region_name=f"{self.parent_view.region_name} (Filter: {search_query})",
            region_emoji=self.parent_view.region_emoji
        )
        
        # Update the message
        await interaction.response.edit_message(
            embed=filtered_view.create_cities_embed(),
            view=filtered_view
        )

class CitiesPageView(discord.ui.View):
    """View untuk menampilkan daftar kota per halaman dengan navigasi"""
    
    def __init__(self, cities, region_name, region_emoji, current_page=0):
        super().__init__(timeout=180)
        self.cities = cities
        self.region_name = region_name
        self.region_emoji = region_emoji
        self.current_page = current_page
        self.total_pages = (len(cities) + 9) // 10  # 10 cities per page
        self.page_size = 10  # Cities per page
        self.display_mode = "grid"  # "grid" or "side-by-side"
        
        # Add navigation buttons
        self.update_buttons()
    
    def update_buttons(self):
        """Update the navigation buttons based on current state"""
        # Clear existing items
        self.clear_items()
        
        # Left button (previous page)
        self.left_button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            emoji="⬅️",
            custom_id="left_btn",
            disabled=(self.current_page == 0)
        )
        self.left_button.callback = self.prev_page
        self.add_item(self.left_button)
        
        # Previous button
        self.prev_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            emoji="◀️",
            custom_id="prev_page",
            disabled=(self.current_page == 0)
        )
        self.prev_button.callback = self.prev_page
        self.add_item(self.prev_button)
        
        # Page indicator
        self.page_indicator = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label=f"Halaman {self.current_page + 1}/{self.total_pages}",
            custom_id="page_indicator",
            disabled=True
        )
        self.add_item(self.page_indicator)
        
        # Next button
        self.next_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            emoji="▶️",
            custom_id="next_page",
            disabled=(self.current_page >= self.total_pages - 1)
        )
        self.next_button.callback = self.next_page
        self.add_item(self.next_button)
        
        # Right button (next page)
        self.right_button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            emoji="➡️",
            custom_id="right_btn",
            disabled=(self.current_page >= self.total_pages - 1)
        )
        self.right_button.callback = self.next_page
        self.add_item(self.right_button)
        
        # Second row of buttons
        # Layout toggle button
        layout_emoji = "📊" if self.display_mode == "grid" else "📑"
        layout_label = "Tampilan Grid" if self.display_mode == "side-by-side" else "Tampilan Dua Kolom"
        self.layout_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            emoji=layout_emoji,
            label=layout_label,
            custom_id="layout_toggle",
            row=1
        )
        self.layout_button.callback = self.toggle_layout
        self.add_item(self.layout_button)
        
        # Search button
        self.search_button = discord.ui.Button(
            style=discord.ButtonStyle.success,
            emoji="🔍",
            label="Cari Kota",
            custom_id="search_button",
            row=1
        )
        self.search_button.callback = self.show_search_modal
        self.add_item(self.search_button)
        
        # Home button
        self.home_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            emoji="🏠",
            label="Kembali",
            custom_id="home_button",
            row=1
        )
        self.home_button.callback = self.go_home
        self.add_item(self.home_button)
    
    async def prev_page(self, interaction: discord.Interaction):
        """Navigasi ke halaman sebelumnya"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_cities_embed(), view=self)
    
    async def next_page(self, interaction: discord.Interaction):
        """Navigasi ke halaman berikutnya"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_cities_embed(), view=self)
    
    async def toggle_layout(self, interaction: discord.Interaction):
        """Mengubah tampilan antara grid dan side-by-side"""
        # Toggle between grid and side-by-side layout
        self.display_mode = "side-by-side" if self.display_mode == "grid" else "grid"
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_cities_embed(), view=self)
    
    async def show_search_modal(self, interaction: discord.Interaction):
        """Menampilkan modal pencarian kota"""
        # Create a modal for city search
        modal = CitySearchModal(self)
        await interaction.response.send_modal(modal)
    
    async def go_home(self, interaction: discord.Interaction):
        """Kembali ke menu utama"""
        # Create regions view and back to main menu
        regions, cities_by_region = await Imsakiyah(interaction.client).get_regions_data()
        view = ImsakiyahMainView(regions, cities_by_region)
        
        await interaction.response.edit_message(embed=view.create_main_menu_embed(), view=view)
    
    def create_cities_embed(self):
        """Membuat embed untuk halaman kota saat ini"""
        # Create embed for current page of cities
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.cities))
        
        cities_page = self.cities[start_idx:end_idx]
        
        embed = discord.Embed(
            title=f"{self.region_emoji} Kota di {self.region_name}",
            description=(
                f"Berikut adalah daftar kota di wilayah **{self.region_name}**.\n"
                f"Menampilkan {start_idx + 1}-{end_idx} dari {len(self.cities)} kota.\n\n"
                "Gunakan perintah berikut untuk melihat jadwal imsakiyah:\n"
                "```\n!imsakiyah <nama_kota>\n```\n"
                "Contoh: `!imsakiyah jakarta`\n\n"
                "Gunakan tombol 🔍 untuk mencari kota tertentu."
            ),
            color=0x91A3B0
        )
        
        # Add cities to the embed based on display mode
        if self.display_mode == "grid":
            # Add cities in a single column
            cities_text = ""
            for i, city in enumerate(cities_page, start=start_idx + 1):
                city_name = city.get('name', 'Unknown')
                cities_text += f"`{i}.` **{city_name}**\n"
            
            embed.add_field(name="📍 Daftar Kota", value=cities_text, inline=False)
        else:
            # Add cities in two columns
            # Calculate midpoint to split the list
            mid = len(cities_page) // 2 + len(cities_page) % 2  # Ceiling division
            
            # Create left column
            left_cities = cities_page[:mid]
            left_text = ""
            for i, city in enumerate(left_cities, start=start_idx + 1):
                city_name = city.get('name', 'Unknown')
                left_text += f"`{i}.` **{city_name}**\n"
            
            # Create right column
            right_cities = cities_page[mid:]
            right_text = ""
            right_start_idx = start_idx + mid
            for i, city in enumerate(right_cities, start=right_start_idx + 1):
                city_name = city.get('name', 'Unknown')
                right_text += f"`{i}.` **{city_name}**\n"
            
            # If left_text is empty, add placeholder
            if not left_text:
                left_text = "*Tidak ada kota*"
            
            # If right_text is empty, add placeholder
            if not right_text:
                right_text = "*Tidak ada kota*"
            
            embed.add_field(name="📍 Kota (1-" + str(mid + start_idx) + ")", value=left_text, inline=True)
            embed.add_field(name="📍 Kota (" + str(mid + start_idx + 1) + "-" + str(end_idx) + ")", value=right_text, inline=True)
        
        # Add instructions for buttons
        embed.add_field(
            name="💡 Navigasi",
            value=(
                "**⬅️ ◀️** : Halaman sebelumnya\n"
                "**▶️ ➡️** : Halaman berikutnya\n"
                "**📊/📑** : Ubah tampilan\n"
                "**🔍** : Cari kota\n"
                "**🏠** : Kembali ke menu utama"
            ),
            inline=False
        )
        
        embed.set_footer(text=f"Halaman {self.current_page + 1}/{self.total_pages} • Gunakan tombol untuk navigasi • Tampilan: {'Grid' if self.display_mode == 'grid' else 'Dua Kolom'}")
        embed.set_thumbnail(url="https://i.imgur.com/8eKS1xZ.png")
        
        return embed

class ImsakiyahMainView(discord.ui.View):
    """View utama untuk navigasi menu imsakiyah"""
    
    def __init__(self, regions, cities_by_region):
        super().__init__(timeout=180)
        self.regions = regions
        self.cities_by_region = cities_by_region
        
        # Add the region selector
        self.add_item(RegionSelect(regions, self.region_selected))
    
    async def region_selected(self, interaction, region_id):
        """Menangani saat region dipilih dari dropdown"""
        # Get region data
        region_data = self.regions.get(region_id, {"name": "Wilayah", "emoji": "📍"})
        region_cities = self.cities_by_region.get(region_id, [])
        
        # Create view for showing cities in this region
        view = CitiesPageView(
            cities=region_cities,
            region_name=region_data["name"],
            region_emoji=region_data["emoji"]
        )
        
        # Show cities embed
        await interaction.response.edit_message(
            embed=view.create_cities_embed(),
            view=view
        )
    
    def create_main_menu_embed(self):
        """Membuat embed untuk menu utama"""
        embed = discord.Embed(
            title="🕌 Jadwal Imsakiyah Ramadhan 1445H",
            description=(
                "**Assalamu'alaikum Warohmatullohi Wabarokatuh** 🌙✨\n\n"
                "Berikut adalah daftar kota di Indonesia untuk melihat jadwal imsakiyah.\n"
                "Silahkan pilih wilayah dengan menu dropdown di bawah.\n\n"
                "_Semoga ibadah puasa kita diterima Allah SWT_ 🤲"
            ),
            color=0x91A3B0
        )
        
        # Add region overviews
        for region_id, region_data in self.regions.items():
            region_cities = self.cities_by_region.get(region_id, [])
            if region_cities:
                # Show some sample cities
                sample_count = min(5, len(region_cities))
                sample_cities = [city['name'] for city in region_cities[:sample_count]]
                sample_text = "`, `".join(sample_cities)
                
                if len(region_cities) > sample_count:
                    sample_text += f"` dan {len(region_cities) - sample_count} kota lainnya"
                
                embed.add_field(
                    name=f"{region_data['emoji']} {region_data['name']} ({len(region_cities)} kota)",
                    value=f"`{sample_text}`",
                    inline=False
                )
        
        # Add command information
        embed.add_field(
            name="📋 Perintah Tersedia",
            value=(
                "```yaml\n"
                "!imsakiyah          - Menu utama daftar kota\n"
                "!imsakiyah <kota>   - Jadwal kota spesifik\n"
                "!imsakiyah cari <x> - Mencari kota\n"
                "!imsak <kota>       - Shortcut untuk jadwal\n"
                "```"
            ),
            inline=False
        )
        
        embed.set_thumbnail(url="https://i.imgur.com/8eKS1xZ.png")
        current_date = datetime.now().strftime('%d %B %Y')
        embed.set_footer(text=f"Jadwal Imsakiyah • {current_date} • Gunakan menu dropdown untuk memilih wilayah")
        
        return embed

class CitiesSearchView(discord.ui.View):
    """View untuk menampilkan hasil pencarian kota"""
    
    def __init__(self, matching_cities, search_term, current_page=0):
        super().__init__(timeout=180)
        self.matching_cities = matching_cities
        self.search_term = search_term
        self.current_page = current_page
        self.total_pages = (len(matching_cities) + 9) // 10  # 10 cities per page
        
        # Add navigation buttons
        self.update_buttons()
    
    def update_buttons(self):
        """Update tombol navigasi berdasarkan status saat ini"""
        # Clear existing items
        self.clear_items()
        
        # Previous button
        self.prev_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            emoji="⬅️",
            custom_id="prev_page",
            disabled=(self.current_page == 0)
        )
        self.prev_button.callback = self.prev_page
        self.add_item(self.prev_button)
        
        # Page indicator
        self.page_indicator = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label=f"Halaman {self.current_page + 1}/{self.total_pages}",
            custom_id="page_indicator",
            disabled=True
        )
        self.add_item(self.page_indicator)
        
        # Next button
        self.next_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            emoji="➡️",
            custom_id="next_page",
            disabled=(self.current_page >= self.total_pages - 1)
        )
        self.next_button.callback = self.next_page
        self.add_item(self.next_button)
        
        # Home button
        self.home_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            emoji="🏠",
            label="Menu Utama",
            custom_id="home_button"
        )
        self.home_button.callback = self.go_home
        self.add_item(self.home_button)
    
    async def prev_page(self, interaction: discord.Interaction):
        """Navigasi ke halaman sebelumnya"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_search_embed(), view=self)
    
    async def next_page(self, interaction: discord.Interaction):
        """Navigasi ke halaman berikutnya"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_search_embed(), view=self)
    
    async def go_home(self, interaction: discord.Interaction):
        """Kembali ke menu utama"""
        # Create regions view and back to main menu
        regions, cities_by_region = await Imsakiyah(interaction.client).get_regions_data()
        view = ImsakiyahMainView(regions, cities_by_region)
        
        await interaction.response.edit_message(embed=view.create_main_menu_embed(), view=view)
    
    def create_search_embed(self):
        """Membuat embed untuk hasil pencarian kota"""
        # Get current page cities
        page_size = 10
        start_idx = self.current_page * page_size
        end_idx = min(start_idx + page_size, len(self.matching_cities))
        
        cities_page = self.matching_cities[start_idx:end_idx]
        
        # Create embed
        embed = discord.Embed(
            title=f"🔍 Hasil Pencarian: '{self.search_term}'",
            description=(
                f"Ditemukan {len(self.matching_cities)} kota yang cocok dengan '{self.search_term}'.\n"
                f"Menampilkan {start_idx + 1}-{end_idx} dari {len(self.matching_cities)} hasil.\n\n"
                "Gunakan perintah berikut untuk melihat jadwal imsakiyah:\n"
                "```!imsakiyah <nama_kota>```\n"
                "Contoh: `!imsakiyah jakarta`"
            ),
            color=0x91A3B0
        )
        
        # Add cities to embed
        cities_text = ""
        for i, city in enumerate(cities_page, start=start_idx + 1):
            city_name = city.get('name', 'Unknown')
            # Add city to list
            cities_text += f"`{i}.` **{city_name}**\n"
        
        embed.add_field(name="📍 Daftar Kota", value=cities_text or "*Tidak ada kota*", inline=False)
        
        # Add info on how to use buttons
        embed.add_field(
            name="💡 Navigasi",
            value=(
                "**⬅️** : Halaman sebelumnya\n"
                "**➡️** : Halaman berikutnya\n"
                "**🏠** : Kembali ke menu utama"
            ),
            inline=False
        )
        
        embed.set_footer(text=f"Halaman {self.current_page + 1}/{self.total_pages} • Hasil Pencarian")
        return embed

class Imsakiyah:
    """
    Class untuk mengelola fitur jadwal imsakiyah
    """
    def __init__(self, bot):
        self.bot = bot
        
    async def get_regions_data(self):
        """Get regions data with cities organized by region"""
        # Get list of cities
        cities_data = await self.get_cities()
        
        if not cities_data or 'data' not in cities_data:
            # Create fallback cities if API fails
            fallback_cities = [
                {"id": "jakarta", "name": "Jakarta"},
                {"id": "bandung", "name": "Bandung"},
                {"id": "surabaya", "name": "Surabaya"},
                {"id": "medan", "name": "Medan"},
                {"id": "makassar", "name": "Makassar"},
                {"id": "semarang", "name": "Semarang"},
                {"id": "palembang", "name": "Palembang"},
                {"id": "denpasar", "name": "Denpasar"}
            ]
            all_cities = fallback_cities
        else:
            all_cities = cities_data['data']
            
        # Organize cities by region
        regions, cities_by_region = self._get_cities_by_region(all_cities)
        
        return regions, cities_by_region
        
    async def get_cities(self):
        """Get list of available cities"""
        try:
            response = requests.get(API_BASE_URL)
            response.raise_for_status()
            return {"data": response.json()}
        except Exception as e:
            print(f"Error fetching cities: {e}")
            return None
     
    async def get_imsakiyah_data(self, city_id, year=None, month=None):
        """Get imsakiyah data for a specific city and month"""
        # Use current year and month if not specified
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
            
        try:
            # Try to get data from the API
            response = requests.get(f"{ADZAN_API_BASE}/{city_id}/{year}/{month}.json")
            
            # If API returns error, use fallback data
            if response.status_code != 200:
                print(f"Error fetching imsakiyah data, using fallback: {response.status_code}")
                return self._generate_fallback_data(city_id, month, year)
                
            return {"data": response.json()}
        except Exception as e:
            print(f"Error fetching imsakiyah data: {e}")
            return self._generate_fallback_data(city_id, month, year)
     
    def _generate_fallback_data(self, city_id, month, year):
        """Generate fallback data when API is unavailable"""
        # Generate 30 days of fallback data with slight variations
        fallback_data = []
        base_date = datetime(year, month, 1)
        
        for i in range(30):
            current_date = base_date + timedelta(days=i)
            
            # Skip if month changes
            if current_date.month != month:
                continue
                
            # Generate slight variations in time
            minute_offset = (i % 5) - 2  # Between -2 and 2
            
            fallback_data.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "hijri": "Ramadan 1445",
                "imsak": f"04:{(23 + minute_offset) % 60:02d}",
                "subuh": f"04:{(33 + minute_offset) % 60:02d}",
                "terbit": f"05:{(48 + minute_offset) % 60:02d}",
                "dhuha": f"06:{(15 + minute_offset) % 60:02d}",
                "dzuhur": f"12:{(0 + minute_offset) % 60:02d}",
                "ashar": f"15:{(16 + minute_offset) % 60:02d}",
                "maghrib": f"18:{(5 + minute_offset) % 60:02d}",
                "isya": f"19:{(15 + minute_offset) % 60:02d}"
            })
            
        return {"data": fallback_data}
     
    async def get_today_schedule(self, city_id):
        """Get today's schedule for a specific city"""
        try:
            tz = pytz.timezone('Asia/Jakarta')
            today = datetime.now(tz)
            
            data = await self.get_imsakiyah_data(city_id, today.year, today.month)
            if not data:
                print(f"[DEBUG] No data returned for city_id: {city_id}")
                return None
                
            today_str = today.strftime('%Y-%m-%d')
            print(f"[DEBUG] Looking for schedule on {today_str}")
            
            # Ensure data has the expected structure
            if not isinstance(data, dict) or 'data' not in data:
                print(f"[DEBUG] Invalid data structure: {data}")
                return None
                
            # Find today's schedule
            for schedule in data['data']:
                if schedule.get('date') == today_str:
                    return schedule
                    
            print(f"[DEBUG] No schedule found for {today_str}")
            return None
        except Exception as e:
            print(f"Error getting today's schedule: {e}")
            traceback.print_exc()
            return None
     
    def _is_date_format(self, text):
        """Check if text is a valid date format YYYY-MM-DD"""
        try:
            if not isinstance(text, str):
                return False
            datetime.strptime(text, '%Y-%m-%d')
            return True
        except ValueError:
            return False
     
    def _is_json(self, text):
        """Check if text is valid JSON"""
        try:
            json.loads(text)
            return True
        except (ValueError, TypeError):
            return False
     
    def _normalize_schedule(self, day_data):
        """Normalize schedule to standard format"""
        try:
            # Handle case where day_data is a JSON string
            if isinstance(day_data, str) and self._is_json(day_data):
                try:
                    day_data = json.loads(day_data)
                except Exception as e:
                    print(f"[DEBUG] Could not parse string as JSON, using default schedule")
                    return self._create_safe_schedule()
            
            # Initialize with default values
            normalized = {
                "date": datetime.now().strftime('%Y-%m-%d'),
                "imsak": "04:30",
                "subuh": "04:40",
                "terbit": "06:00",
                "dhuha": "06:30",
                "dzuhur": "12:00",
                "ashar": "15:00",
                "maghrib": "18:00",
                "isya": "19:00"
            }
            
            # Field mappings (different APIs might use different field names)
            field_mappings = {
                # Date fields
                "date": ["date", "tanggal"],
                "hijri": ["hijri", "tanggal_hijriah", "hijriah"],
                
                # Prayer time fields
                "imsak": ["imsak", "imsa", "imask"],
                "subuh": ["subuh", "fajr", "shubuh", "fajar"],
                "terbit": ["terbit", "sunrise", "syuruq", "syuruk"],
                "dhuha": ["dhuha", "duha"],
                "dzuhur": ["dzuhur", "dhuhr", "zuhur", "dhuhur"],
                "ashar": ["ashar", "asr"],
                "maghrib": ["maghrib", "magrib"],
                "isya": ["isya", "isha"]
            }
            
            # Copy values based on field mappings
            for field, aliases in field_mappings.items():
                for alias in aliases:
                    if alias in day_data and day_data[alias]:
                        normalized[field] = day_data[alias]
                        break
            
            return normalized
        except Exception as e:
            print(f"[ERROR] Error normalizing schedule: {e}")
            traceback.print_exc()
            return self._create_safe_schedule()
     
    def _create_safe_schedule(self, date=None):
        """Create a safe default schedule for fallback"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
            
        return {
            "date": date,
            "hijri": "Ramadan 1445",
            "imsak": "04:23",
            "subuh": "04:33",
            "terbit": "05:48",
            "dhuha": "06:15",
            "dzuhur": "12:00",
            "ashar": "15:16",
            "maghrib": "18:05",
            "isya": "19:15"
        }
     
    def _get_cities_by_region(self, all_cities):
        """Organize cities by region"""
        # Define regions
        regions = {
            "jawa": {
                "name": "Jawa",
                "emoji": "🏙️",
                "city_count": 0
            },
            "sumatera": {
                "name": "Sumatera",
                "emoji": "🌋", 
                "city_count": 0
            },
            "kalimantan": {
                "name": "Kalimantan",
                "emoji": "🏝️",
                "city_count": 0
            },
            "sulawesi": {
                "name": "Sulawesi",
                "emoji": "🌊",
                "city_count": 0
            },
            "bali_ntt": {
                "name": "Bali & Nusa Tenggara",
                "emoji": "🏖️",
                "city_count": 0
            },
            "maluku_papua": {
                "name": "Maluku & Papua",
                "emoji": "🦜",
                "city_count": 0
            }
        }
        
        # Keywords to map cities to regions
        region_keywords = {
            "jawa": ["jakarta", "jawa", "bandung", "semarang", "yogyakarta", "yogya", "solo", "surabaya", "malang", "banten", "bogor", "bekasi", "tangerang", "depok", "cirebon", "sukabumi", "tasikmalaya", "cilegon", "serang", "cimahi", "tegal", "pekalongan", "salatiga", "magelang", "purwokerto", "kediri", "madiun", "mojokerto", "pasuruan", "batu", "blitar", "probolinggo"],
            
            "sumatera": ["sumatera", "sumatra", "aceh", "medan", "padang", "palembang", "pekanbaru", "jambi", "bengkulu", "bandar lampung", "lampung", "pangkal pinang", "tanjungpinang", "batam", "bintan", "tanjung balai", "dumai", "bukit tinggi", "payakumbuh", "pariaman", "solok", "padang panjang", "sawahlunto", "lubuk linggau", "prabumulih", "tebing tinggi", "pematang siantar", "binjai", "sibolga", "padang sidempuan", "gunungsitoli", "banda aceh", "langsa", "lhokseumawe", "subulussalam"],
            
            "kalimantan": ["kalimantan", "borneo", "pontianak", "palangkaraya", "banjarmasin", "samarinda", "tanjungpinang", "tanjung selor", "tarakan", "bontang", "balikpapan", "singkawang", "sampit", "palangka raya"],
            
            "sulawesi": ["sulawesi", "celebes", "makassar", "manado", "palu", "kendari", "gorontalo", "mamuju", "ambon", "ternate", "tidore", "bitung", "tomohon", "kotamobagu", "bau-bau"],
            
            "bali_ntt": ["bali", "denpasar", "mataram", "kupang", "nusa", "singaraja"],
            
            "maluku_papua": ["maluku", "papua", "jayapura", "manokwari", "sorong", "ternate", "ambon", "fakfak", "merauke", "timika"]
        }
        
        # Helper function to determine region of a city
        def determine_region(city_name):
            city_lower = city_name.lower()
            for region, keywords in region_keywords.items():
                for keyword in keywords:
                    if keyword in city_lower:
                        return region
            return "jawa"  # Default to Jawa if no match
        
        # Organize cities by region
        cities_by_region = {region: [] for region in regions}
        
        for city in all_cities:
            if isinstance(city, dict) and 'name' in city and 'id' in city:
                city_name = city['name']
                region = determine_region(city_name)
                cities_by_region[region].append(city)
                regions[region]["city_count"] += 1
            elif isinstance(city, str):
                # Handle string entries (from fallback)
                region = determine_region(city)
                idx = all_cities.index(city)
                cities_by_region[region].append({"id": str(idx), "name": city})
                regions[region]["city_count"] += 1
        
        # Sort cities alphabetically within each region
        for region in cities_by_region:
            cities_by_region[region] = sorted(cities_by_region[region], key=lambda x: x.get('name', ''))
        
        return regions, cities_by_region 

async def jadwal_imsakiyah(ctx, city=None):
    """Command to show imsakiyah schedule"""
    # Print debug info to identify duplicate command calls
    print(f"[DEBUG] jadwal_imsakiyah called by {ctx.author} - Message ID: {ctx.message.id}")
    
    imsakiyah = Imsakiyah(ctx.bot)
    
    # Send typing indicator
    async with ctx.typing():
        try:
            # If no city provided, show interactive menu with regions
            if not city:
                cities = await imsakiyah.get_cities()
                if not cities or not isinstance(cities, dict) or 'data' not in cities:
                    embed = discord.Embed(
                        title="❌ Gagal Memuat Data",
                        description="Tidak dapat memuat daftar kota. Silakan coba lagi nanti.",
                        color=EMBED_COLORS["error"]
                    )
                    return await ctx.send(embed=embed)
        
                # Verify cities['data'] is a list
                if not isinstance(cities['data'], list):
                    embed = discord.Embed(
                        title="❌ Format Data Tidak Valid",
                        description="Format data kota tidak sesuai. Silakan coba lagi nanti.",
                        color=EMBED_COLORS["error"]
                    )
                    return await ctx.send(embed=embed)
                
                # Organize cities by region
                regions, cities_by_region = await imsakiyah.get_regions_data()
                
                # Create the interactive view
                view = ImsakiyahMainView(regions, cities_by_region)
                
                # Create the initial embed
                embed = view.create_main_menu_embed()
                
                # Send the message with the view
                return await ctx.send(embed=embed, view=view)
            
            # Check if this is a search query
            if city.lower().startswith("cari "):
                search_term = city[5:].strip().lower()
                if not search_term:
                    embed = discord.Embed(
                        title="❌ Kata Kunci Kosong",
                        description="Silakan masukkan kata kunci pencarian. Contoh: `!imsakiyah cari jakarta`",
                        color=EMBED_COLORS["error"]
                    )
                    return await ctx.send(embed=embed)
                
                # Get cities and search
                cities = await imsakiyah.get_cities()
                if not cities or not isinstance(cities, dict) or 'data' not in cities:
                    embed = discord.Embed(
                        title="❌ Gagal Memuat Data",
                        description="Tidak dapat memuat daftar kota. Silakan coba lagi nanti.",
                        color=EMBED_COLORS["error"]
                    )
                    return await ctx.send(embed=embed)
                
                # Search for cities matching the term
                matching_cities = []
                for city_data in cities['data']:
                    try:
                        if isinstance(city_data, dict) and 'name' in city_data:
                            if search_term in city_data['name'].lower():
                                matching_cities.append(city_data)
                        elif isinstance(city_data, str) and search_term in city_data.lower():
                            # Convert string to dict format for consistency
                            idx = cities['data'].index(city_data)
                            matching_cities.append({"id": str(idx), "name": city_data})
                    except Exception as e:
                        print(f"[ERROR] Error during city search: {e}")
                        continue
                
                # Sort results alphabetically
                matching_cities = sorted(matching_cities, key=lambda x: x['name'])
                
                if not matching_cities:
                    embed = discord.Embed(
                        title="❌ Tidak Ditemukan",
                        description=f"Tidak ada kota yang cocok dengan '{search_term}'. Coba kata kunci lain.",
                        color=EMBED_COLORS["warning"]
                    )
                    return await ctx.send(embed=embed)
    
                # Create the search results view with pagination
                view = CitiesSearchView(matching_cities, search_term)
                
                # Send the search results
                return await ctx.send(embed=view.create_search_embed(), view=view)
            
            # Find the city ID based on name
            cities = await imsakiyah.get_cities()
            if not cities or not isinstance(cities, dict) or 'data' not in cities:
                embed = discord.Embed(
                    title="❌ Gagal Memuat Data",
                    description="Tidak dapat memuat daftar kota. Silakan coba lagi nanti.",
                    color=EMBED_COLORS["error"]
                )
                return await ctx.send(embed=embed)
            
            city_id = None
            city_name = "Kota"
            
            # Try to find exact match first
            for city_data in cities['data']:
                if isinstance(city_data, dict) and 'name' in city_data and 'id' in city_data:
                    if city_data['name'].lower() == city.lower():
                        city_id = city_data['id']
                        city_name = city_data['name']
                        break
                        
            # If no exact match, try partial match
            if not city_id:
                for city_data in cities['data']:
                    if isinstance(city_data, dict) and 'name' in city_data and 'id' in city_data:
                        if city.lower() in city_data['name'].lower():
                            city_id = city_data['id']
                            city_name = city_data['name']
                            break
            
            # If no city found, show error
            if not city_id:
                embed = discord.Embed(
                    title="❌ Kota Tidak Ditemukan",
                    description=(
                        f"Kota '{city}' tidak ditemukan dalam database. "
                        "Silakan periksa nama kota atau gunakan `!imsakiyah` untuk melihat daftar kota."
                    ),
                    color=EMBED_COLORS["error"]
                )
                return await ctx.send(embed=embed)
            
            # Get today's schedule
            schedule = await imsakiyah.get_today_schedule(city_id)
            
            # If no schedule found, show error
            if not schedule:
                embed = discord.Embed(
                    title="❌ Jadwal Tidak Tersedia",
                    description=f"Jadwal imsakiyah untuk kota {city_name} tidak tersedia untuk hari ini.",
                    color=EMBED_COLORS["warning"]
                )
                return await ctx.send(embed=embed)
    
            # Format date
            try:
                date_str = schedule.get('date', datetime.now().strftime('%Y-%m-%d'))
                if not isinstance(date_str, str):
                    date_str = datetime.now().strftime('%Y-%m-%d')
                    
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d %B %Y')
                
                # Get day name in Indonesian
                day_names_id = {
                    0: "Senin",
                    1: "Selasa",
                    2: "Rabu",
                    3: "Kamis",
                    4: "Jumat",
                    5: "Sabtu",
                    6: "Minggu"
                }
                day_name = day_names_id.get(date_obj.weekday(), "")
            except Exception as e:
                print(f"[ERROR] Error formatting date: {e}")
                formatted_date = "Hari ini"
                day_name = ""
            
            # Create embed for schedule
            embed = discord.Embed(
                title=f"📆 Jadwal Imsakiyah {city_name}",
                description=f"Jadwal untuk {day_name}, {formatted_date}",
                color=EMBED_COLORS["primary"]
            )
            
            # Prayer time fields to display
            prayer_times = {
                "imsak": "🌙 Imsak",
                "subuh": "🌅 Subuh",
                "terbit": "🌞 Terbit",
                "dhuha": "🌤️ Dhuha",
                "dzuhur": "☀️ Dzuhur",
                "ashar": "🌇 Ashar",
                "maghrib": "🌆 Maghrib",
                "isya": "🌃 Isya"
            }
            
            # Add prayer times to embed
            for code, label in prayer_times.items():
                time_value = schedule.get(code, "🕒 --:--")
                if time_value and isinstance(time_value, str) and ":" in time_value:
                    # Format the time if it's a valid string with colon
                    embed.add_field(name=label, value=f"🕒 {time_value}", inline=True)
                else:
                    # Use default value if missing or invalid
                    embed.add_field(name=label, value="🕒 --:--", inline=True)
            
            # Add footer with data source
            embed.set_footer(text="Data dari jadwalsholat.org | 👨‍💻 Rurawr Bot")
            
            # Send the embed
            return await ctx.send(embed=embed)
        
        except Exception as e:
            # Log the error
            print(f"[ERROR] Error in imsakiyah command: {e}")
            traceback.print_exc()
            
            # Send error message
            embed = discord.Embed(
                title="❌ Terjadi Kesalahan",
                description="Terjadi kesalahan saat memproses perintah. Silakan coba lagi nanti.",
                color=EMBED_COLORS["error"]
            )
            return await ctx.send(embed=embed)

async def setup(bot):
    """Setup function to register the command"""
    print("[DEBUG] Setting up imsakiyah extension...")
    
    # Make sure to remove any existing command to prevent duplicates
    for cmd_name in ["imsakiyah", "imsak", "jadwal"]:
        if bot.get_command(cmd_name):
            bot.remove_command(cmd_name)
            print(f"[DEBUG] Removed existing command: {cmd_name}")
    
    # Register the command
    @bot.command(name="imsakiyah", aliases=["imsak", "jadwal"])
    async def imsakiyah_command(ctx, *, city=None):
        """Display Ramadan schedule for a city in Indonesia"""
        await jadwal_imsakiyah(ctx, city)
    
    print("[DEBUG] Successfully registered imsakiyah command") 