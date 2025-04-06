import discord
from discord.ext import commands
import requests
import json
import os
from dotenv import load_dotenv
from typing import Optional
import time
from datetime import datetime
import asyncio
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for non-interactive environments
from matplotlib.colors import ListedColormap
import numpy as np
import pycountry

# Load environment variables
load_dotenv()

# Last.fm API Configuration
LASTFM_API_KEY = "3bdd30d3799864596b04361db75aec6f"
LASTFM_API_SECRET = "03dd48c292c3fae60de990b9741b9ed0"
LASTFM_API_URL = "http://ws.audioscrobbler.com/2.0/"

# In-memory user storage
LASTFM_USERS = {}  # {discord_id: lastfm_username}

# Embed colors
EMBED_COLORS = {
    "primary": 0xd51007,  # Last.fm red
    "success": 0x2ecc71,  # Green
    "warning": 0xf1c40f,  # Yellow
    "error": 0xe74c3c,    # Red
    "info": 0x3498db      # Blue
}

# Helper function to make API requests to Last.fm
async def lastfm_request(method, **params):
    """Make a request to the Last.fm API"""
    query_params = {
        "method": method,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        **params
    }
    
    try:
        response = requests.get(LASTFM_API_URL, params=query_params)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Last.fm API Request Error: {e}")
        return None

# Clean user input for album/artist names
def clean_query(query):
    """Clean query for Last.fm API search"""
    return query.strip()

# Generate album covers
def get_album_cover(album_info, size="large"):
    """Get album cover image from album info"""
    if not album_info or "album" not in album_info:
        return None
    
    size_map = {
        "small": 0,
        "medium": 1,
        "large": 2,
        "extralarge": 3,
        "mega": 4
    }
    
    images = album_info["album"].get("image", [])
    if not images or len(images) <= size_map.get(size, 2):
        return None
    
    return images[size_map.get(size, 2)]["#text"]

# Format Last.fm timestamp 
def format_timestamp(unix_timestamp):
    """Format Last.fm timestamp to a readable date"""
    try:
        dt = datetime.fromtimestamp(int(unix_timestamp))
        return dt.strftime("%d %b %Y, %H:%M")
    except (ValueError, TypeError):
        return "Unknown date"

# Track info formatter
def format_track_info(track, include_album=True):
    """Format track information"""
    artist = track.get("artist", {}).get("#text", "Unknown Artist")
    name = track.get("name", "Unknown Track")
    formatted = f"**{name}** by **{artist}**"
    
    if include_album and track.get("album") and track["album"].get("#text"):
        formatted += f" from *{track['album']['#text']}*"
    
    return formatted

class LastFM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # Helper method to get text based on guild language
    def get_text(self, guild_id, key, **kwargs):
        """Get translated text based on guild language"""
        if hasattr(self.bot, 'get_text'):
            return self.bot.get_text(guild_id, key, **kwargs)
        
        # Fallback if bot doesn't have get_text
        translations = {
            "lastfm.not_set": "Kamu belum mengatur username Last.fm! Gunakan `!lastfm set <username>` untuk mengaturnya.",
            "lastfm.set_success": "Username Last.fm kamu telah diatur menjadi `{username}`!",
            "lastfm.user_not_found": "Pengguna Last.fm `{username}` tidak ditemukan!",
            "lastfm.no_recent": "Tidak ada riwayat lagu terbaru untuk `{username}`!",
            "lastfm.api_error": "Terjadi kesalahan saat mengambil data dari API Last.fm!",
            "lastfm.album_not_found": "Album tidak ditemukan untuk `{query}`!",
            "lastfm.artist_not_found": "Artis tidak ditemukan untuk `{query}`!",
            "lastfm.track_not_found": "Lagu tidak ditemukan untuk `{query}`!",
            "lastfm.no_album_plays": "Kamu belum mendengarkan album `{album}` oleh `{artist}` sama sekali!",
            "lastfm.no_artist_plays": "Kamu belum mendengarkan `{artist}` sama sekali!",
            "lastfm.specify_album": "Harap tentukan nama album! Penggunaan: `!album <nama album> | <nama artis>`",
            "lastfm.specify_artist": "Harap tentukan nama artis! Penggunaan: `!artist <nama artis>`",
            "lastfm.specify_track": "Harap tentukan nama lagu! Penggunaan: `!track <nama lagu> | <nama artis>`",
        }
        
        return translations.get(key, key).format(**kwargs)
    
    @commands.group(name="lastfm", aliases=["lf", "fm"], invoke_without_command=True)
    async def lastfm(self, ctx):
        """Last.fm command group"""
        # Check if user has set a Last.fm username
        user_id = str(ctx.author.id)
        if user_id not in LASTFM_USERS:
            await ctx.send(self.get_text(ctx.guild.id if ctx.guild else None, "lastfm.not_set"))
            return
        
        # Show Now Playing or recently played tracks
        await self.now_playing(ctx)
    
    @lastfm.command(name="set")
    async def set_lastfm(self, ctx, username: str = None):
        """Set your Last.fm username"""
        if not username:
            await ctx.send("Please provide your Last.fm username! Usage: `!lastfm set <username>`")
            return
        
        # Verify that the username exists on Last.fm
        user_info = await lastfm_request("user.getInfo", user=username)
        if user_info and "user" in user_info:
            # Store the username in our database
            LASTFM_USERS[str(ctx.author.id)] = username
            
            # Send confirmation message
            await ctx.send(self.get_text(
                ctx.guild.id if ctx.guild else None, 
                "lastfm.set_success", 
                username=username
            ))
        else:
            await ctx.send(self.get_text(
                ctx.guild.id if ctx.guild else None, 
                "lastfm.user_not_found", 
                username=username
            ))
    
    @commands.command(name="np", aliases=["nowplaying"])
    async def now_playing(self, ctx):
        """Show what you're currently listening to on Last.fm"""
        user_id = str(ctx.author.id)
        if user_id not in LASTFM_USERS:
            await ctx.send(self.get_text(ctx.guild.id if ctx.guild else None, "lastfm.not_set"))
            return
        
        username = LASTFM_USERS[user_id]
        
        # Send typing indicator while fetching data
        async with ctx.typing():
            # Get recent tracks for the user
            recent_tracks = await lastfm_request("user.getRecentTracks", user=username, limit=1)
            
            if not recent_tracks or "recenttracks" not in recent_tracks or not recent_tracks["recenttracks"]["track"]:
                await ctx.send(self.get_text(
                    ctx.guild.id if ctx.guild else None, 
                    "lastfm.no_recent", 
                    username=username
                ))
                return
            
            # Get the most recent track
            track = recent_tracks["recenttracks"]["track"][0]
            
            # Check if the user is currently listening to the track
            now_playing = "@attr" in track and "nowplaying" in track["@attr"] and track["@attr"]["nowplaying"] == "true"
            
            # Get album info for the track
            artist_name = track["artist"]["#text"]
            track_name = track["name"]
            album_name = track["album"]["#text"] if "album" in track and "#text" in track["album"] else "Unknown Album"
            
            # Create embed
            embed = discord.Embed(
                title="Now Playing" if now_playing else "Last Played",
                description=format_track_info(track),
                color=EMBED_COLORS["primary"]
            )
            
            # Add album and profile fields
            if album_name != "Unknown Album":
                album_info = await lastfm_request("album.getInfo", artist=artist_name, album=album_name, username=username)
                album_cover = get_album_cover(album_info)
                if album_cover:
                    embed.set_thumbnail(url=album_cover)
            
            # Add timestamp
            if not now_playing and "date" in track and "#text" in track["date"]:
                scrobble_time = int(track["date"]["uts"])
                embed.add_field(
                    name="Scrobbled",
                    value=format_timestamp(scrobble_time),
                    inline=True
                )
            
            # Add user profile link
            embed.add_field(
                name="Profile",
                value=f"[{username}](https://www.last.fm/user/{username})",
                inline=True
            )
            
            # Add bot footer
            embed.set_footer(
                text=f"Last.fm | {ctx.author.display_name}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            
            await ctx.send(embed=embed)
    
    @commands.command(name="recent", aliases=["recents"])
    async def recent_tracks(self, ctx, username: str = None):
        """Show your recent tracks on Last.fm"""
        user_id = str(ctx.author.id)
        
        # If username not provided, use the saved one
        if not username:
            if user_id not in LASTFM_USERS:
                await ctx.send(self.get_text(ctx.guild.id if ctx.guild else None, "lastfm.not_set"))
                return
            username = LASTFM_USERS[user_id]
        
        # Send typing indicator while fetching data
        async with ctx.typing():
            # Get recent tracks for the user
            recent_tracks = await lastfm_request("user.getRecentTracks", user=username, limit=10)
            
            if not recent_tracks or "recenttracks" not in recent_tracks or not recent_tracks["recenttracks"]["track"]:
                await ctx.send(self.get_text(
                    ctx.guild.id if ctx.guild else None, 
                    "lastfm.no_recent", 
                    username=username
                ))
                return
            
            tracks = recent_tracks["recenttracks"]["track"]
            
            # Create embed
            embed = discord.Embed(
                title=f"Recent Tracks for {username}",
                description=f"The 10 most recent tracks scrobbled by {username}",
                color=EMBED_COLORS["primary"]
            )
            
            # Add tracks to the embed
            for i, track in enumerate(tracks[:10], 1):
                now_playing = "@attr" in track and "nowplaying" in track["@attr"] and track["@attr"]["nowplaying"] == "true"
                
                # Format the track info
                track_info = format_track_info(track, include_album=False)
                if "album" in track and "#text" in track["album"]:
                    track_info += f"\n*{track['album']['#text']}*"
                
                # Add timestamp if not now playing
                if not now_playing and "date" in track and "#text" in track["date"]:
                    scrobble_time = format_timestamp(int(track["date"]["uts"]))
                    track_info += f"\n`{scrobble_time}`"
                
                embed.add_field(
                    name=f"{'🎵 Now Playing' if now_playing else f'{i}.'}", 
                    value=track_info,
                    inline=False
                )
            
            # Set thumbnail from the first track's album if possible
            if tracks and tracks[0].get("image"):
                for image in tracks[0]["image"]:
                    if image["size"] == "large" and image["#text"]:
                        embed.set_thumbnail(url=image["#text"])
                        break
            
            # Add user profile link footer
            embed.set_footer(
                text=f"Last.fm | {ctx.author.display_name}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            
            await ctx.send(embed=embed)
    
    @commands.command(name="album")
    async def album_info(self, ctx, *, query: str = None):
        """Show how many times you've listened to an album"""
        user_id = str(ctx.author.id)
        if user_id not in LASTFM_USERS:
            await ctx.send(self.get_text(ctx.guild.id if ctx.guild else None, "lastfm.not_set"))
            return
        
        if not query:
            await ctx.send(self.get_text(ctx.guild.id if ctx.guild else None, "lastfm.specify_album"))
            return
        
        username = LASTFM_USERS[user_id]
        
        # Parse album and artist from query
        if "|" in query:
            album_name, artist_name = map(clean_query, query.split("|", 1))
        else:
            # If only album name is provided, need to find artist
            album_name = clean_query(query)
            # Get user's now playing or recent track to infer artist
            recent_tracks = await lastfm_request("user.getRecentTracks", user=username, limit=1)
            
            if recent_tracks and "recenttracks" in recent_tracks and recent_tracks["recenttracks"]["track"]:
                recent_artist = recent_tracks["recenttracks"]["track"][0]["artist"]["#text"]
                # Get album info using the album name and recent artist
                album_search = await lastfm_request("album.search", album=album_name, limit=1)
                if album_search and "results" in album_search and "albummatches" in album_search["results"] and "album" in album_search["results"]["albummatches"] and album_search["results"]["albummatches"]["album"]:
                    artist_name = album_search["results"]["albummatches"]["album"][0]["artist"]
                else:
                    artist_name = recent_artist
            else:
                # If we can't get a recent track, inform the user to provide artist name
                await ctx.send("Please specify the artist name as well: `!album <album name> | <artist name>`")
                return
        
        # Send typing indicator while fetching data
        async with ctx.typing():
            # Get album info
            album_info = await lastfm_request("album.getInfo", artist=artist_name, album=album_name, username=username)
            
            if not album_info or "album" not in album_info:
                await ctx.send(self.get_text(
                    ctx.guild.id if ctx.guild else None, 
                    "lastfm.album_not_found", 
                    query=query
                ))
                return
            
            album = album_info["album"]
            user_playcount = album.get("userplaycount", "0")
            
            if user_playcount == "0":
                await ctx.send(self.get_text(
                    ctx.guild.id if ctx.guild else None, 
                    "lastfm.no_album_plays", 
                    album=album["name"],
                    artist=album["artist"]
                ))
                return
            
            # Create embed
            embed = discord.Embed(
                title=album["name"],
                description=f"by **{album['artist']}**",
                color=EMBED_COLORS["primary"],
                url=album["url"]
            )
            
            # Add album cover
            album_cover = get_album_cover(album_info, "extralarge")
            if album_cover:
                embed.set_thumbnail(url=album_cover)
            
            # Add playcount
            embed.add_field(
                name="Scrobbles",
                value=f"**{user_playcount}** plays",
                inline=True
            )
            
            # Add tags
            if "tags" in album and "tag" in album["tags"]:
                tags = album["tags"]["tag"]
                tag_names = [f"`{tag['name']}`" for tag in tags[:5]]
                if tag_names:
                    embed.add_field(
                        name="Tags",
                        value=" ".join(tag_names),
                        inline=True
                    )
            
            # Add tracks
            if "tracks" in album and "track" in album["tracks"]:
                tracks = album["tracks"]["track"]
                if isinstance(tracks, list):
                    track_count = len(tracks)
                    tracks_str = f"{track_count} tracks"
                else:
                    tracks_str = "1 track"
                
                embed.add_field(
                    name="Tracks",
                    value=tracks_str,
                    inline=True
                )
            
            # Add user profile link footer
            embed.set_footer(
                text=f"Last.fm | {ctx.author.display_name}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            
            await ctx.send(embed=embed)
    
    @commands.command(name="artist")
    async def artist_info(self, ctx, *, artist_name: str = None):
        """Show how many times you've listened to an artist"""
        user_id = str(ctx.author.id)
        if user_id not in LASTFM_USERS:
            await ctx.send(self.get_text(ctx.guild.id if ctx.guild else None, "lastfm.not_set"))
            return
        
        if not artist_name:
            await ctx.send(self.get_text(ctx.guild.id if ctx.guild else None, "lastfm.specify_artist"))
            return
        
        username = LASTFM_USERS[user_id]
        artist_name = clean_query(artist_name)
        
        # Send typing indicator while fetching data
        async with ctx.typing():
            # Get artist info
            artist_info = await lastfm_request("artist.getInfo", artist=artist_name, username=username)
            
            if not artist_info or "artist" not in artist_info:
                await ctx.send(self.get_text(
                    ctx.guild.id if ctx.guild else None, 
                    "lastfm.artist_not_found", 
                    query=artist_name
                ))
                return
            
            artist = artist_info["artist"]
            user_playcount = artist.get("stats", {}).get("userplaycount", "0")
            
            if user_playcount == "0":
                await ctx.send(self.get_text(
                    ctx.guild.id if ctx.guild else None, 
                    "lastfm.no_artist_plays", 
                    artist=artist["name"]
                ))
                return
            
            # Create embed
            embed = discord.Embed(
                title=artist["name"],
                color=EMBED_COLORS["primary"],
                url=artist["url"]
            )
            
            # Add artist image if available
            if "image" in artist:
                for image in artist["image"]:
                    if image["size"] == "extralarge" and image["#text"]:
                        embed.set_thumbnail(url=image["#text"])
                        break
            
            # Add playcount
            embed.add_field(
                name="Scrobbles",
                value=f"**{user_playcount}** plays",
                inline=True
            )
            
            # Add global listeners and scrobbles if available
            if "stats" in artist:
                stats = artist["stats"]
                if "listeners" in stats:
                    embed.add_field(
                        name="Listeners",
                        value=f"{stats['listeners']} listeners",
                        inline=True
                    )
                if "playcount" in stats:
                    embed.add_field(
                        name="Global Scrobbles",
                        value=f"{stats['playcount']} plays",
                        inline=True
                    )
            
            # Add tags
            if "tags" in artist and "tag" in artist["tags"]:
                tags = artist["tags"]["tag"]
                tag_names = [f"`{tag['name']}`" for tag in tags[:5]]
                if tag_names:
                    embed.add_field(
                        name="Tags",
                        value=" ".join(tag_names),
                        inline=False
                    )
            
            # Add summary
            if "bio" in artist and "summary" in artist["bio"]:
                summary = artist["bio"]["summary"]
                # Remove "Read more on Last.fm" link
                summary = summary.split("<a href=")[0].strip()
                if summary:
                    embed.add_field(
                        name="About",
                        value=f"{summary[:250]}..." if len(summary) > 250 else summary,
                        inline=False
                    )
            
            # Add user profile link footer
            embed.set_footer(
                text=f"Last.fm | {ctx.author.display_name}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            
            await ctx.send(embed=embed)
    
    @commands.command(name="topalbums", aliases=["talb"])
    async def top_albums(self, ctx, period: str = "overall"):
        """Show your top albums on Last.fm"""
        user_id = str(ctx.author.id)
        if user_id not in LASTFM_USERS:
            await ctx.send(self.get_text(ctx.guild.id if ctx.guild else None, "lastfm.not_set"))
            return
        
        username = LASTFM_USERS[user_id]
        
        # Map period to Last.fm API periods
        period_map = {
            "week": "7day",
            "month": "1month",
            "3month": "3month",
            "6month": "6month",
            "year": "12month",
            "overall": "overall"
        }
        
        period_value = period_map.get(period.lower(), "overall")
        period_display = {
            "7day": "Last 7 Days",
            "1month": "Last Month",
            "3month": "Last 3 Months",
            "6month": "Last 6 Months",
            "12month": "Last Year",
            "overall": "All Time"
        }[period_value]
        
        # Send typing indicator while fetching data
        async with ctx.typing():
            # Get top albums
            top_albums = await lastfm_request("user.getTopAlbums", user=username, period=period_value, limit=10)
            
            if not top_albums or "topalbums" not in top_albums or not top_albums["topalbums"]["album"]:
                await ctx.send(f"No top albums found for {username} in {period_display}!")
                return
            
            albums = top_albums["topalbums"]["album"]
            
            # Create embed
            embed = discord.Embed(
                title=f"Top Albums for {username}",
                description=f"Your top 10 albums ({period_display})",
                color=EMBED_COLORS["primary"]
            )
            
            # Add albums to the embed
            for i, album in enumerate(albums[:10], 1):
                artist_name = album["artist"]["name"]
                album_name = album["name"]
                playcount = album["playcount"]
                
                embed.add_field(
                    name=f"{i}. {album_name}",
                    value=f"**Artist:** {artist_name}\n**Plays:** {playcount}",
                    inline=(i % 2 != 0)  # Alternate inline fields
                )
            
            # Set thumbnail from the first album
            if albums and albums[0].get("image"):
                for image in albums[0]["image"]:
                    if image["size"] == "large" and image["#text"]:
                        embed.set_thumbnail(url=image["#text"])
                        break
            
            # Add user profile link footer
            embed.set_footer(
                text=f"Last.fm | {ctx.author.display_name}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            
            await ctx.send(embed=embed)

    @commands.command(name="topartists", aliases=["tart"])
    async def top_artists(self, ctx, period: str = "overall"):
        """Show your top artists on Last.fm"""
        user_id = str(ctx.author.id)
        if user_id not in LASTFM_USERS:
            await ctx.send(self.get_text(ctx.guild.id if ctx.guild else None, "lastfm.not_set"))
            return
        
        username = LASTFM_USERS[user_id]
        
        # Map period to Last.fm API periods
        period_map = {
            "week": "7day",
            "month": "1month",
            "3month": "3month",
            "6month": "6month",
            "year": "12month",
            "overall": "overall"
        }
        
        period_value = period_map.get(period.lower(), "overall")
        period_display = {
            "7day": "Last 7 Days",
            "1month": "Last Month",
            "3month": "Last 3 Months",
            "6month": "Last 6 Months",
            "12month": "Last Year",
            "overall": "All Time"
        }[period_value]
        
        # Send typing indicator while fetching data
        async with ctx.typing():
            # Get top artists
            top_artists = await lastfm_request("user.getTopArtists", user=username, period=period_value, limit=10)
            
            if not top_artists or "topartists" not in top_artists or not top_artists["topartists"]["artist"]:
                await ctx.send(f"No top artists found for {username} in {period_display}!")
                return
            
            artists = top_artists["topartists"]["artist"]
            
            # Create embed
            embed = discord.Embed(
                title=f"Top Artists for {username}",
                description=f"Your top 10 artists ({period_display})",
                color=EMBED_COLORS["primary"]
            )
            
            # Add artists to the embed
            for i, artist in enumerate(artists[:10], 1):
                artist_name = artist["name"]
                playcount = artist["playcount"]
                
                embed.add_field(
                    name=f"{i}. {artist_name}",
                    value=f"**Plays:** {playcount}",
                    inline=True
                )
            
            # Add user profile link footer
            embed.set_footer(
                text=f"Last.fm | {ctx.author.display_name}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            
            await ctx.send(embed=embed)

    @commands.command(name="countries", aliases=["country", "map"])
    async def countries(self, ctx, period: str = "overall"):
        """Show a map representation of your scrobbled artists by country"""
        user_id = str(ctx.author.id)
        if user_id not in LASTFM_USERS:
            await ctx.send(self.get_text(ctx.guild.id if ctx.guild else None, "lastfm.not_set"))
            return
        
        username = LASTFM_USERS[user_id]
        
        # Map period to Last.fm API periods
        period_map = {
            "week": "7day",
            "month": "1month",
            "3month": "3month",
            "6month": "6month",
            "year": "12month",
            "overall": "overall"
        }
        
        period_value = period_map.get(period.lower(), "overall")
        period_display = {
            "7day": "Last 7 Days",
            "1month": "Last Month",
            "3month": "Last 3 Months",
            "6month": "Last 6 Months",
            "12month": "Last Year",
            "overall": "All Time"
        }[period_value]
        
        # Send typing indicator while fetching data
        async with ctx.typing():
            # Get top artists
            top_artists = await lastfm_request("user.getTopArtists", user=username, period=period_value, limit=100)
            
            if not top_artists or "topartists" not in top_artists or not top_artists["topartists"]["artist"]:
                await ctx.send(f"No top artists found for {username} in {period_display}!")
                return
            
            artists = top_artists["topartists"]["artist"]
            
            # Create a temporary embed while generating the map
            temp_embed = discord.Embed(
                title=f"Generating country map for {username}",
                description=f"Processing {len(artists)} artists from {period_display}...",
                color=EMBED_COLORS["primary"]
            )
            temp_message = await ctx.send(embed=temp_embed)
            
            # Process artist countries
            country_data = await self.get_artist_countries(artists)
            
            if not country_data:
                await temp_message.edit(embed=discord.Embed(
                    title="Error generating map",
                    description="Could not find country data for any artists.",
                    color=EMBED_COLORS["error"]
                ))
                return
            
            # Generate map image
            map_image = await self.generate_world_map(country_data)
            
            # Create final embed with map
            embed = discord.Embed(
                title=f"Country Map for {username}",
                description=f"Artist distribution by country ({period_display})",
                color=EMBED_COLORS["primary"]
            )
            
            # Add top 5 countries
            sorted_countries = sorted(country_data.items(), key=lambda x: x[1], reverse=True)
            top_countries = sorted_countries[:5]
            total_scrobbles = sum(country_data.values())
            
            country_list = []
            for country_code, count in top_countries:
                try:
                    country_name = pycountry.countries.get(alpha_2=country_code).name
                    percentage = (count / total_scrobbles) * 100
                    country_list.append(f"**{country_name}**: {count} artists ({percentage:.1f}%)")
                except (AttributeError, KeyError):
                    continue
            
            if country_list:
                embed.add_field(
                    name="Top Countries",
                    value="\n".join(country_list),
                    inline=False
                )
            
            # Add total stats
            embed.add_field(
                name="Stats",
                value=f"Total Artists: {len(artists)}\nMapped Countries: {len(country_data)}",
                inline=False
            )
            
            # Add note about data source
            embed.set_footer(
                text=f"Last.fm | {ctx.author.display_name} | Data based on artist origin countries",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            
            # Attach the map image
            file = discord.File(fp=map_image, filename="country_map.png")
            embed.set_image(url="attachment://country_map.png")
            
            # Send the final embed with map image
            await temp_message.delete()
            await ctx.send(file=file, embed=embed)
    
    async def get_artist_countries(self, artists):
        """Get country codes for each artist"""
        country_count = {}
        
        # Mapping of some major artist countries (as a fallback)
        artist_country_map = {
            "BTS": "KR",
            "BLACKPINK": "KR",
            "Taylor Swift": "US",
            "The Beatles": "GB",
            "Queen": "GB",
            "Drake": "CA",
            "Daft Punk": "FR",
            "Rammstein": "DE",
            "ABBA": "SE",
            "Coldplay": "GB",
            "Ed Sheeran": "GB",
            "Adele": "GB",
            "Lady Gaga": "US",
            "Eminem": "US",
            "Justin Bieber": "CA",
            "Ariana Grande": "US",
            "The Weeknd": "CA",
            "Beyoncé": "US",
            "Dua Lipa": "GB",
            "Billie Eilish": "US"
        }
        
        for artist in artists:
            artist_name = artist["name"]
            
            # Try to get artist info with bio which might contain country info
            artist_info = await lastfm_request("artist.getInfo", artist=artist_name)
            
            country_code = None
            
            if artist_info and "artist" in artist_info:
                # Try to extract country from tags
                if "tags" in artist_info["artist"] and "tag" in artist_info["artist"]["tags"]:
                    tags = artist_info["artist"]["tags"]["tag"]
                    for tag in tags:
                        tag_name = tag["name"].lower()
                        # Look for country tags
                        if tag_name in ["american", "usa", "us"]:
                            country_code = "US"
                            break
                        elif tag_name in ["british", "uk"]:
                            country_code = "GB"
                            break
                        elif tag_name == "canadian":
                            country_code = "CA"
                            break
                        elif tag_name == "australian":
                            country_code = "AU"
                            break
                        elif tag_name == "german":
                            country_code = "DE"
                            break
                        elif tag_name == "french":
                            country_code = "FR"
                            break
                        elif tag_name == "japanese":
                            country_code = "JP"
                            break
                        elif tag_name == "korean" or tag_name == "k-pop":
                            country_code = "KR"
                            break
                        elif tag_name == "swedish":
                            country_code = "SE"
                            break
                        # Add more countries as needed
            
            # If no country found from tags, try the fallback map
            if not country_code and artist_name in artist_country_map:
                country_code = artist_country_map[artist_name]
            
            if country_code:
                if country_code in country_count:
                    country_count[country_code] += 1
                else:
                    country_count[country_code] = 1
        
        return country_count
    
    async def generate_world_map(self, country_data):
        """Generate a world map visualization of artist countries"""
        try:
            # Import necessary packages here to avoid loading them if not needed
            import geopandas
            
            # Get world map data
            world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
            
            # Create a figure and axis
            fig, ax = plt.subplots(1, 1, figsize=(12, 8))
            
            # Create the color map
            max_value = max(country_data.values()) if country_data else 1
            world['artist_count'] = 0
            
            # Assign artist counts to countries
            for country_code, count in country_data.items():
                # Handle special cases for country codes
                if country_code == 'GB':
                    # Great Britain might be listed as United Kingdom
                    world.loc[world['iso_a3'] == 'GBR', 'artist_count'] = count
                elif country_code == 'US':
                    world.loc[world['iso_a3'] == 'USA', 'artist_count'] = count
                else:
                    # Try to find by ISO A2 (convert to A3 if needed)
                    try:
                        if len(country_code) == 2:
                            country = pycountry.countries.get(alpha_2=country_code)
                            if country:
                                world.loc[world['iso_a3'] == country.alpha_3, 'artist_count'] = count
                    except Exception:
                        pass
            
            # Normalize the data
            world['normalized'] = world['artist_count'] / max_value
            
            # Create a custom colormap
            colors = plt.cm.YlOrRd(np.linspace(0.2, 0.8, 256))
            custom_cmap = ListedColormap(colors)
            
            # Plot the world map
            world.plot(column='normalized', cmap=custom_cmap, linewidth=0.5, 
                      edgecolor='0.5', ax=ax, legend=True, 
                      legend_kwds={'label': "Artist Count", 'orientation': "horizontal"})
            
            # Add title and remove axis
            ax.set_title('Artist Distribution by Country', fontsize=16)
            ax.set_axis_off()
            
            # Save the figure to a BytesIO object
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            
            # Close the figure to free memory
            plt.close(fig)
            
            return buf
        except ImportError:
            # If necessary packages are not available, create a simple text-based visualization
            fig, ax = plt.subplots(figsize=(10, 6))
            
            countries = list(country_data.keys())
            counts = list(country_data.values())
            
            # Sort by count
            sorted_indices = np.argsort(counts)[::-1][:10]  # Top 10 countries
            sorted_countries = [countries[i] for i in sorted_indices]
            sorted_counts = [counts[i] for i in sorted_indices]
            
            # Try to convert country codes to country names
            country_names = []
            for code in sorted_countries:
                try:
                    country = pycountry.countries.get(alpha_2=code)
                    country_names.append(country.name)
                except:
                    country_names.append(code)  # Use code if conversion fails
            
            # Create bar chart
            ax.bar(country_names, sorted_counts, color='#d51007')
            
            # Add labels and title
            ax.set_xlabel('Country')
            ax.set_ylabel('Number of Artists')
            ax.set_title('Top Countries by Artist Count')
            
            # Rotate x-labels for better readability
            plt.xticks(rotation=45, ha='right')
            
            # Adjust layout
            plt.tight_layout()
            
            # Save to BytesIO
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            
            # Close figure
            plt.close(fig)
            
            return buf

async def setup(bot):
    """Setup function to register the cog"""
    print("[DEBUG] Setting up Last.fm extension...")
    await bot.add_cog(LastFM(bot))
    print("[DEBUG] Successfully added Last.fm cog to the bot")
