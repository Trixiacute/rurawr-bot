"""
mal.py - Module untuk mencari dan menampilkan informasi anime

Module ini menggunakan API MyAnimeList, AniList, dan sumber lainnya
untuk mencari dan menampilkan informasi anime.
"""

import discord
from discord.ext import commands
import aiohttp
import asyncio
import random
from datetime import datetime
import re
from typing import Optional, Dict, Any, List, Union
from utils import create_embed, log_command
from constants import EMBED_COLORS

class Anime(commands.Cog):
    """Commands for anime information using Jikan API (MyAnimeList)"""
    
    def __init__(self, bot):
        self.bot = bot
        self.base_url = "https://api.jikan.moe/v4"
        self.session = aiohttp.ClientSession()
    
    def cog_unload(self):
        asyncio.create_task(self.session.close())
    
    async def fetch_data(self, endpoint, params=None):
        """Helper function to fetch data from Jikan API"""
        try:
            async with self.session.get(f"{self.base_url}/{endpoint}", params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    # Rate limited, wait and try again
                    await asyncio.sleep(2)
                    return await self.fetch_data(endpoint, params)
                else:
                    return {"error": f"API returned status code {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    @commands.command(name="anime")
    async def anime_search(self, ctx, *, query):
        """Search for an anime by title"""
        data = await self.fetch_data("anime", {"q": query, "limit": 5})
        
        if "error" in data:
            return await ctx.send(f"Error: {data['error']}")
        
        if not data.get("data"):
            return await ctx.send("No results found.")
        
        anime = data["data"][0]
        
        embed = discord.Embed(
            title=anime["title"],
            url=anime["url"],
            description=anime.get("synopsis", "No description available."),
            color=discord.Color.blue()
        )
        
        if anime.get("images", {}).get("jpg", {}).get("image_url"):
            embed.set_thumbnail(url=anime["images"]["jpg"]["image_url"])
        
        embed.add_field(name="Type", value=anime.get("type", "N/A"), inline=True)
        embed.add_field(name="Episodes", value=anime.get("episodes", "N/A"), inline=True)
        embed.add_field(name="Status", value=anime.get("status", "N/A"), inline=True)
        embed.add_field(name="Score", value=anime.get("score", "N/A"), inline=True)
        embed.add_field(name="Aired", value=anime.get("aired", {}).get("string", "N/A"), inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="manga")
    async def manga_search(self, ctx, *, query):
        """Search for a manga by title"""
        data = await self.fetch_data("manga", {"q": query, "limit": 5})
        
        if "error" in data:
            return await ctx.send(f"Error: {data['error']}")
        
        if not data.get("data"):
            return await ctx.send("No results found.")
        
        manga = data["data"][0]
        
        embed = discord.Embed(
            title=manga["title"],
            url=manga["url"],
            description=manga.get("synopsis", "No description available."),
            color=discord.Color.dark_green()
        )
        
        if manga.get("images", {}).get("jpg", {}).get("image_url"):
            embed.set_thumbnail(url=manga["images"]["jpg"]["image_url"])
        
        embed.add_field(name="Type", value=manga.get("type", "N/A"), inline=True)
        embed.add_field(name="Chapters", value=manga.get("chapters", "N/A"), inline=True)
        embed.add_field(name="Status", value=manga.get("status", "N/A"), inline=True)
        embed.add_field(name="Score", value=manga.get("score", "N/A"), inline=True)
        embed.add_field(name="Published", value=manga.get("published", {}).get("string", "N/A"), inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="character")
    async def character_search(self, ctx, *, query):
        """Search for an anime/manga character"""
        data = await self.fetch_data("characters", {"q": query, "limit": 5})
        
        if "error" in data:
            return await ctx.send(f"Error: {data['error']}")
        
        if not data.get("data"):
            return await ctx.send("No results found.")
        
        character = data["data"][0]
        
        embed = discord.Embed(
            title=character["name"],
            url=character["url"],
            description=character.get("about", "No information available."),
            color=discord.Color.purple()
        )
        
        if character.get("images", {}).get("jpg", {}).get("image_url"):
            embed.set_thumbnail(url=character["images"]["jpg"]["image_url"])
        
        nicknames = ", ".join(character.get("nicknames", [])) or "None"
        embed.add_field(name="Nicknames", value=nicknames, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="season")
    async def anime_season(self, ctx, season=None, year=None):
        """Get anime from a specific season (winter, spring, summer, fall)"""
        current_year = datetime.now().year
        seasons = ["winter", "spring", "summer", "fall"]
        
        if not season:
            # Determine current season
            month = datetime.now().month
            if month in [12, 1, 2]:
                season = "winter"
            elif month in [3, 4, 5]:
                season = "spring"
            elif month in [6, 7, 8]:
                season = "summer"
            else:
                season = "fall"
        else:
            season = season.lower()
            if season not in seasons:
                return await ctx.send(f"Invalid season. Choose from: {', '.join(seasons)}")
        
        if not year:
            year = current_year
        
        try:
            year = int(year)
            if year < 1950 or year > current_year + 1:
                return await ctx.send(f"Year must be between 1950 and {current_year + 1}")
        except ValueError:
            return await ctx.send("Year must be a number")
        
        data = await self.fetch_data(f"seasons/{year}/{season}")
        
        if "error" in data:
            return await ctx.send(f"Error: {data['error']}")
        
        if not data.get("data"):
            return await ctx.send("No results found.")
        
        # Get 5 random anime from the season
        anime_list = random.sample(data["data"], min(5, len(data["data"])))
        
        embed = discord.Embed(
            title=f"{season.capitalize()} {year} Anime",
            description=f"Here are some anime from {season} {year}:",
            color=discord.Color.gold()
        )
        
        for anime in anime_list:
            embed.add_field(
                name=anime["title"],
                value=f"Type: {anime.get('type', 'N/A')} | Score: {anime.get('score', 'N/A')} | [MAL]({anime['url']})",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="random")
    async def random_anime(self, ctx):
        """Get a random anime recommendation"""
        data = await self.fetch_data("random/anime")
        
        if "error" in data:
            return await ctx.send(f"Error: {data['error']}")
        
        if not data.get("data"):
            return await ctx.send("No results found.")
        
        anime = data["data"]
        
        embed = discord.Embed(
            title=anime["title"],
            url=anime["url"],
            description=anime.get("synopsis", "No description available."),
            color=discord.Color.random()
        )
        
        if anime.get("images", {}).get("jpg", {}).get("image_url"):
            embed.set_thumbnail(url=anime["images"]["jpg"]["image_url"])
        
        embed.add_field(name="Type", value=anime.get("type", "N/A"), inline=True)
        embed.add_field(name="Episodes", value=anime.get("episodes", "N/A"), inline=True)
        embed.add_field(name="Status", value=anime.get("status", "N/A"), inline=True)
        embed.add_field(name="Score", value=anime.get("score", "N/A"), inline=True)
        embed.add_field(name="Aired", value=anime.get("aired", {}).get("string", "N/A"), inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="top")
    async def top_anime(self, ctx, category="anime", subtype=None):
        """Get top anime or manga (anime, manga)"""
        if category.lower() not in ["anime", "manga"]:
            return await ctx.send("Category must be either 'anime' or 'manga'")
        
        params = {}
        if subtype:
            valid_subtypes = {
                "anime": ["airing", "upcoming", "tv", "movie", "ova", "special", "bypopularity", "favorite"],
                "manga": ["manga", "novels", "oneshots", "doujin", "manhwa", "manhua", "bypopularity", "favorite"]
            }
            
            if subtype.lower() not in valid_subtypes[category.lower()]:
                return await ctx.send(f"Invalid subtype. Valid subtypes for {category} are: {', '.join(valid_subtypes[category.lower()])}")
            
            params["type"] = subtype.lower()
        
        data = await self.fetch_data(f"top/{category.lower()}", params)
        
        if "error" in data:
            return await ctx.send(f"Error: {data['error']}")
        
        if not data.get("data"):
            return await ctx.send("No results found.")
        
        # Get top 10 items
        items = data["data"][:10]
        
        embed = discord.Embed(
            title=f"Top {subtype.capitalize() if subtype else ''} {category.capitalize()}",
            description=f"Here are the top {len(items)} {category}:",
            color=discord.Color.red()
        )
        
        for i, item in enumerate(items, 1):
            embed.add_field(
                name=f"{i}. {item['title']}",
                value=f"Score: {item.get('score', 'N/A')} | [MAL]({item['url']})",
                inline=False
            )
        
        await ctx.send(embed=embed)

async def display_anime_info(ctx, anime_data, message):
    """
    Menampilkan informasi anime dalam format embed yang rapi
    
    Args:
        ctx: Context Discord
        anime_data: Data anime dari API
        message: Pesan loading yang akan diupdate
    """
    # Determine format based on data structure (MAL vs AniList)
    is_anilist = "averageScore" in anime_data
    
    # Create embed
    embed = discord.Embed(
        title=anime_data.get("title", {}).get("english", anime_data.get("title")) if is_anilist else anime_data.get("title"),
        color=EMBED_COLORS["primary"]
    )
    
    # Set description (synopsis)
    embed.description = anime_data.get("description") if is_anilist else anime_data.get("synopsis")
    
    # Set thumbnail
    embed.set_thumbnail(url=anime_data.get("coverImage", {}).get("large") if is_anilist else anime_data.get("image_url"))
    
    # Add Japanese title
    jp_title = anime_data.get("title", {}).get("native") if is_anilist else anime_data.get("title_japanese")
    if jp_title:
        embed.add_field(name="🇯🇵 Judul Jepang", value=jp_title, inline=True)
    
    # Add type and episodes
    embed.add_field(name="📺 Tipe", value=anime_data.get("type", "N/A"), inline=True)
    embed.add_field(name="📊 Episode", value=str(anime_data.get("episodes", "N/A")), inline=True)
    
    # Add status
    status = anime_data.get("status", "N/A")
    if is_anilist and status == "FINISHED":
        status = "Finished Airing"
    embed.add_field(name="📡 Status", value=status, inline=True)
    
    # Add score
    score = anime_data.get("averageScore") if is_anilist else anime_data.get("score")
    if score:
        score_str = f"{score/10:.1f}" if is_anilist else f"{score:.1f}"
        embed.add_field(name="⭐ Skor", value=score_str, inline=True)
    
    # Add popularity/members
    popularity = anime_data.get("popularity") if is_anilist else anime_data.get("members")
    if popularity:
        pop_str = f"{popularity:,}"
        embed.add_field(name="👥 Popularitas", value=pop_str, inline=True)
    
    # Add year
    year = anime_data.get("startDate", {}).get("year") if is_anilist else anime_data.get("year")
    if year:
        embed.add_field(name="📅 Tahun", value=str(year), inline=True)
    
    # Add studios
    studios = anime_data.get("studios", [])
    if studios:
        if is_anilist:
            studio_names = [studio.get("name", "N/A") for studio in studios]
        else:
            studio_names = studios
        embed.add_field(name="🎬 Studio", value=", ".join(studio_names), inline=True)
    
    # Add genres
    genres = anime_data.get("genres", [])
    if genres:
        embed.add_field(name="🏷️ Genre", value=", ".join(genres), inline=True)
    
    # Set footer with data source
    source = "AniList" if is_anilist else "MyAnimeList"
    embed.set_footer(text=f"Data dari {source} • Gunakan !anime untuk info lebih lanjut")
    
    # Update the loading message with anime info
    await message.edit(embed=embed)
    
    # Add reactions to navigate
    reactions = ["ℹ️", "📺", "⭐", "🎬"]
    for reaction in reactions:
        try:
            await message.add_reaction(reaction)
        except Exception as e:
            print(f"Error adding reaction: {e}")
    
    # Set up reaction handler
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in reactions and reaction.message.id == message.id
    
    try:
        # Wait for user reaction
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check)
        
        # Handle reaction based on emoji
        if str(reaction.emoji) == "ℹ️":
            # Show more info
            more_info_embed = discord.Embed(
                title=f"{anime_data.get('title')} - Detail Lengkap",
                description=anime_data.get("synopsis"),
                color=EMBED_COLORS["primary"]
            )
            more_info_embed.set_image(url=anime_data.get("image_url"))
            await message.edit(embed=more_info_embed)
        
        elif str(reaction.emoji) == "📺":
            # Show episodes info
            episodes_embed = discord.Embed(
                title=f"{anime_data.get('title')} - Informasi Episode",
                description=f"Total episode: {anime_data.get('episodes', 'N/A')}",
                color=EMBED_COLORS["primary"]
            )
            episodes_embed.set_thumbnail(url=anime_data.get("image_url"))
            await message.edit(embed=episodes_embed)
        
        elif str(reaction.emoji) == "⭐":
            # Show ratings info
            ratings_embed = discord.Embed(
                title=f"{anime_data.get('title')} - Ratings & Stats",
                description=(
                    f"⭐ Skor: {anime_data.get('score', 'N/A')}/10\n"
                    f"👥 Members: {anime_data.get('members', 'N/A'):,}\n"
                    f"❤️ Favorites: {anime_data.get('favorites', 'N/A'):,}"
                ),
                color=EMBED_COLORS["primary"]
            )
            ratings_embed.set_thumbnail(url=anime_data.get("image_url"))
            await message.edit(embed=ratings_embed)
        
        elif str(reaction.emoji) == "🎬":
            # Show studio info
            studio_embed = discord.Embed(
                title=f"{anime_data.get('title')} - Studio Information",
                description=f"Studio: {', '.join(anime_data.get('studios', ['N/A']))}",
                color=EMBED_COLORS["primary"]
            )
            studio_embed.set_thumbnail(url=anime_data.get("image_url"))
            await message.edit(embed=studio_embed)
    
    except asyncio.TimeoutError:
        # Remove reactions after timeout
        await message.clear_reactions()
    
    # Log command usage
    log_command(ctx.author.id, ctx.guild.id if ctx.guild else None, "anime")

async def anime_command(ctx, *, query=None):
    """
    Command untuk mencari informasi anime
    
    Args:
        ctx: Context Discord
        query: Query pencarian
    """
    if query is None:
        # Show help if no query provided
        embed = discord.Embed(
            title="🎬 Anime Search",
            description="Cari informasi anime dari berbagai sumber.",
            color=EMBED_COLORS["primary"]
        )
        embed.add_field(
            name="ℹ️ Cara Penggunaan",
            value=(
                "`!anime <judul>` - Cari anime berdasarkan judul\n"
                "`!anime id:<id> source:<sumber>` - Cari berdasarkan ID\n\n"
                "**Sumber yang tersedia:**\n"
                "• `mal` - MyAnimeList\n"
                "• `al` - AniList\n"
                "• `kt` - Kitsu\n"
                "• `adb` - Anime DB\n"
            ),
            inline=False
        )
        embed.add_field(
            name="📢 Contoh",
            value=(
                "`!anime naruto`\n"
                "`!anime id:21 source:mal`\n"
                "`!anime id:1 source:al`"
            ),
            inline=False
        )
        
        # Add cute anime girl image
        embed.set_image(url="https://i.imgur.com/XmZPPbt.png")
        
        return await ctx.send(embed=embed)
    
    # Check if searching by ID
    id_match = re.search(r'id:(\d+)', query, re.IGNORECASE)
    source_match = re.search(r'source:(\w+)', query, re.IGNORECASE)
    
    if id_match and source_match:
        anime_id = id_match.group(1)
        source = source_match.group(1).lower()
        
        # Remove id and source from query
        clean_query = re.sub(r'id:\d+\s*', '', query, flags=re.IGNORECASE)
        clean_query = re.sub(r'source:\w+\s*', '', clean_query, flags=re.IGNORECASE).strip()
        
        # Valid sources
        valid_sources = ['mal', 'al', 'kt', 'adb']
        
        if source not in valid_sources:
            embed = discord.Embed(
                title="❌ Sumber Tidak Valid",
                description=f"Sumber `{source}` tidak valid. Gunakan salah satu dari: {', '.join(valid_sources)}",
                color=EMBED_COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        # Create loading message
        loading_embed = discord.Embed(
            title="🔍 Mencari Anime...",
            description=f"Mencari anime dengan ID {anime_id} dari {source.upper()}...",
            color=EMBED_COLORS["primary"]
        )
        loading_embed.set_footer(text="Mohon tunggu sebentar...")
        message = await ctx.send(embed=loading_embed)
        
        # Simulate API call delay
        await asyncio.sleep(2)
        
        # For demo purposes, return mock data
        # In a real implementation, this would call the appropriate API
        
        # Mock data based on source
        anime_data = {
            "mal": {
                "title": "Naruto",
                "title_japanese": "ナルト",
                "type": "TV",
                "episodes": 220,
                "status": "Finished Airing",
                "score": 8.1,
                "members": 2540000,
                "favorites": 95000,
                "synopsis": "Naruto Uzumaki, a mischievous adolescent ninja...",
                "year": 2002,
                "studios": ["Studio Pierrot"],
                "genres": ["Action", "Adventure", "Fantasy"],
                "image_url": "https://cdn.myanimelist.net/images/anime/13/17405l.jpg"
            },
            "al": {
                "title": {"english": "Naruto", "native": "ナルト"},
                "type": "TV",
                "episodes": 220,
                "status": "FINISHED",
                "averageScore": 81,
                "popularity": 250000,
                "description": "Naruto Uzumaki, a mischievous adolescent ninja...",
                "startDate": {"year": 2002, "month": 10, "day": 3},
                "studios": [{"name": "Studio Pierrot"}],
                "genres": ["Action", "Adventure", "Fantasy"],
                "coverImage": {"large": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20-YJvLbgJQPCoI.jpg"}
            }
        }
        
        # Default to MAL if source not found in mock data
        source_data = anime_data.get(source, anime_data["mal"])
        
        # Display anime info based on source
        await display_anime_info(ctx, source_data, message)
        
    else:
        # Searching by title
        # Create loading message
        loading_embed = discord.Embed(
            title="🔍 Mencari Anime...",
            description=f"Mencari anime dengan judul \"{query}\"...",
            color=EMBED_COLORS["primary"]
        )
        loading_embed.set_footer(text="Mohon tunggu sebentar...")
        message = await ctx.send(embed=loading_embed)
        
        # Simulate API call delay
        await asyncio.sleep(2)
        
        # Mock response for demo purposes
        mock_anime = {
            "title": "Naruto",
            "title_japanese": "ナルト",
            "type": "TV",
            "episodes": 220,
            "status": "Finished Airing",
            "score": 8.1,
            "members": 2540000, 
            "favorites": 95000,
            "synopsis": "Naruto Uzumaki, a mischievous adolescent ninja, struggles as he searches for recognition and dreams of becoming the Hokage, the village's leader and strongest ninja.",
            "year": 2002,
            "studios": ["Studio Pierrot"],
            "genres": ["Action", "Adventure", "Fantasy"],
            "image_url": "https://cdn.myanimelist.net/images/anime/13/17405l.jpg"
        }
        
        # Display anime info
        await display_anime_info(ctx, mock_anime, message)

def setup(bot):
    """
    Setup function untuk mendaftarkan command anime
    
    Args:
        bot: Bot instance Discord
    """
    @bot.command(name="anime", aliases=["ani", "animecari"])
    async def _anime_command(ctx, *, query=None):
        """Mencari informasi anime dari berbagai sumber"""
        await anime_command(ctx, query=query)
    
    print("[INFO] MAL module loaded successfully")
