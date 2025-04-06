import discord
from discord.ext import commands
import requests
import random
from datetime import datetime, timezone
import platform
import os
import sys
import asyncio
from dotenv import load_dotenv
from constants import WAIFU_API_URL, WAIFU_CATEGORIES, EMBED_COLORS, BOT_INFO, COMMAND_DESCRIPTIONS
from languange import LANGUAGES
import time
from typing import Optional
import aiohttp  # Untuk API requests daerah

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Store server language preferences
SERVER_LANGUAGES = {}

# Store server prefix preferences
SERVER_PREFIXES = {}
DEFAULT_PREFIX = "!"

# Function to get guild prefix
def get_prefix(bot, message):
    if message.guild is None:
        return DEFAULT_PREFIX
    return SERVER_PREFIXES.get(message.guild.id, DEFAULT_PREFIX)

# Bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

# Update bot specs
BOT_SPECS = {
    "python_version": platform.python_version(),
    "discord.py_version": discord.__version__,
    "server_count": 0,
    "uptime": datetime.now(timezone.utc)
}

# Add developer IDs list
DEVELOPER_IDS = [837954360818270230, 586802340607164417]

# Add restart channel storage
RESTART_DATA = {
    "channel_id": None,
    "is_restarting": False
}

def get_lang(guild_id):
    return SERVER_LANGUAGES.get(guild_id, "id")

def get_text(guild_id: Optional[int], key: str, **kwargs) -> str:
    """Get translated text based on guild language preference"""
    lang = get_lang(guild_id)
    
    # Split the key by dots to handle nested keys
    keys = key.split('.')
    value = LANGUAGES[lang]["translations"]
    
    # Navigate through nested dictionary
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            # Fallback to English if key not found
            value = LANGUAGES["en"]["translations"]
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return key  # Return the key itself if not found
    
    # Format the string with provided kwargs
    if isinstance(value, str) and kwargs:
        try:
            return value.format(**kwargs)
        except KeyError:
            return value
    return value

# Add get_text method to the bot
bot.get_text = get_text

class LanguangeSelect(discord.ui.Select):
    def __init__(self):
        options = []
        for lang_code, lang_data in LANGUAGES.items():
            option = discord.SelectOption(
                label=lang_data['name'],
                description=f"Switch to {lang_data['name']} / Ganti ke {lang_data['name']}",
                value=lang_code,
                emoji=lang_data['flag']
            )
            options.append(option)
            
        super().__init__(
            placeholder="?�� Select a language / Pilih bahasa",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("??This command can only be used in servers!", ephemeral=True)
            
        lang_code = self.values[0]
        guild_id = interaction.guild_id
        old_lang = get_lang(guild_id)
        
        # Update the language preference for this server
        SERVER_LANGUAGES[guild_id] = lang_code
        
        # Create confirmation embed
        embed = discord.Embed(
            title=f"{LANGUAGES[lang_code]['flag']} {get_text(guild_id, 'languange.title')}",
            color=EMBED_COLORS["success"]
        )
        
        # Show language change confirmation
        embed.add_field(
            name="??Language Changed / Bahasa Diubah",
            value=f"{LANGUAGES[old_lang]['flag']} {LANGUAGES[old_lang]['name']} ??{LANGUAGES[lang_code]['flag']} {LANGUAGES[lang_code]['name']}",
            inline=False
        )
        
        # Show server-specific notice
        embed.add_field(
            name="?�� Notice / Pemberitahuan",
            value=get_text(guild_id, "languange.notice"),
            inline=False
        )
        
        # Add available commands field
        embed.add_field(
            name="?�� Available Commands / Perintah Tersedia",
            value=get_text(guild_id, "help_command_guide"),
            inline=False
        )
        
        embed.set_footer(text=f"Server ID: {interaction.guild_id}")
        await interaction.response.edit_message(embed=embed, view=None)

class LanguangeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(LanguangeSelect())

class CategorySelect(discord.ui.Select):
    def __init__(self, guild_id):
        self.guild_id = guild_id
        options = [
            discord.SelectOption(
                label=get_text(guild_id, "help.categories.image"),
                description=get_text(guild_id, "help.category_descriptions.image"),
                value="image",
                emoji="?���?
            ),
            discord.SelectOption(
                label=get_text(guild_id, "help.categories.reaction"),
                description=get_text(guild_id, "help.category_descriptions.reaction"),
                value="reaction",
                emoji="?��"
            ),
            discord.SelectOption(
                label=get_text(guild_id, "help.categories.fun"),
                description=get_text(guild_id, "help.category_descriptions.fun"),
                value="fun",
                emoji="?��"
            ),
            discord.SelectOption(
                label=get_text(guild_id, "help.categories.utility"),
                description=get_text(guild_id, "help.category_descriptions.utility"),
                value="utility",
                emoji="?�️"
            )
        ]
        super().__init__(
            placeholder=get_text(guild_id, "select_category"),
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        current_prefix = get_prefix(self.view.bot, interaction.message)
        
        # Define commands for each category with emojis
        command_emojis = {
            "help": "??,
            "info": "?�️",
            "ping": "?��",
            "prefix": "?�️",
            "languange": "?��",
            "sekolah": "?��",
            "waifu": "?��",
            "neko": "?��",
            "shinobu": "?�️",
            "megumin": "?��",
            "hug": "?��",
            "kiss": "?��",
            "pat": "?��",
            "slap": "?��",
            "cuddle": "?��",
            "dance": "?��",
            "smile": "?��",
            "wave": "?��",
            "blush": "?��",
            "happy": "?��",
            "randomwaifu": "?��",
            "daerah": "?��?��"  # Tambahkan emoji untuk perintah daerah
        }

        categories = {
            "image": ["waifu", "neko", "shinobu", "megumin"],
            "reaction": ["hug", "kiss", "pat", "slap", "cuddle"],
            "fun": ["dance", "smile", "wave", "blush", "happy"],
            "utility": ["help", "info", "ping", "prefix", "languange", "sekolah", "daerah"]  # Tambahkan daerah ke kategori utility
        }

        selected = self.values[0]
        commands = categories[selected]
        
        embed = discord.Embed(
            title=get_text(self.guild_id, f"help.categories.{selected}"),
            description=get_text(self.guild_id, f"help.category_descriptions.{selected}"),
            color=EMBED_COLORS["primary"]
        )

        # Add commands in a clean format with emojis
        command_list = []
        for cmd in commands:
            desc = get_text(self.guild_id, f"command_descriptions.{cmd}")
            emoji = command_emojis.get(cmd, "?��")  # Default emoji if none specified
            command_list.append(f"`{current_prefix}{cmd}` ??{emoji} {desc}")

        embed.add_field(
            name=get_text(self.guild_id, "command_list"),
            value="\n".join(command_list),
            inline=False
        )

        embed.set_footer(text=get_text(self.guild_id, "help.return_to_menu", prefix=current_prefix))
        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=60)
        self.bot = bot
        self.add_item(CategorySelect(guild_id))

@bot.event
async def on_ready():
    BOT_SPECS["server_count"] = len(bot.guilds)
    print(f"Logged in as {bot.user.name}")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.guilds)} servers | !help"
        )
    )
    await load_cogs()
    await setup_slash_commands()
    
    # Send restart notification if bot was restarting
    if RESTART_DATA["is_restarting"] and RESTART_DATA["channel_id"]:
        try:
            channel = bot.get_channel(RESTART_DATA["channel_id"])
            if channel:
                success_embed = discord.Embed(
                    title="??Bot Berhasil Dimulai Ulang!",
                    description=(
                        "```diff\n"
                        "+ Sistem berhasil dimuat ulang\n"
                        "+ Cache telah dioptimalkan\n"
                        "+ Semua sistem berjalan normal\n"
                        "```\n"
                        "Ruri-chan sudah kembali dan siap membantu! ?��"
                    ),
                    color=discord.Color.from_rgb(147, 201, 255)  # Light blue
                )
                success_embed.add_field(
                    name="?�� Pesan Ruri",
                    value=(
                        "*\"Aku sudah kembali! Terima kasih sudah menunggu~ "
                        "Ayo kita bersenang-senang lagi! ?�️\"*"
                    ),
                    inline=False
                )
                success_embed.set_thumbnail(url="https://media.tenor.com/TY1HfJK5qQUAAAAC/ruri-dragon-smile.gif")
                success_embed.set_footer(text="?�� Ruri Dragon sudah siap melayani! ?��")
                await channel.send(embed=success_embed)
        except Exception as e:
            print(f"Failed to send restart notification: {e}")
        finally:
            # Reset restart data
            RESTART_DATA["channel_id"] = None
            RESTART_DATA["is_restarting"] = False

@bot.command(name="languange")
async def languange_command(ctx, lang_code: str = None):
    """Change bot language (EN/ID/JP/KR) / Ubah bahasa bot (EN/ID/JP/KR)"""
    if not ctx.guild:
        return await ctx.send("??This command can only be used in servers!")
        
    guild_id = ctx.guild.id
    
    # If no language code provided, show current language and available options
    if not lang_code:
        current_lang = get_lang(guild_id)
        embed = discord.Embed(
            title=f"?�� {get_text(guild_id, 'languange.title')}",
            color=EMBED_COLORS["primary"]
        )
        
        # Add current language field
        embed.add_field(
            name="?�� Current Language / Bahasa Saat Ini",
            value=f"{LANGUAGES[current_lang]['flag']} {LANGUAGES[current_lang]['name']}",
            inline=False
        )
        
        # Add usage instructions
        usage = (
            "**Usage / Cara Penggunaan:**\n"
            "`!languange EN` - Change to English\n"
            "`!languange ID` - Ganti ke Bahasa Indonesia"
        )
        embed.add_field(name="?�️ Instructions / Petunjuk", value=usage, inline=False)
        
        # Add available languages field
        available_langs = "\n".join([
            f"{lang_data['flag']} **{lang_data['name']}** (`{code.upper()}`)"
            for code, lang_data in LANGUAGES.items()
        ])
        embed.add_field(
            name="?���?Available Languages / Bahasa Tersedia",
            value=available_langs,
            inline=False
        )
        
        # Add server-specific notice
        embed.add_field(
            name="?�� Notice / Pemberitahuan",
            value=get_text(guild_id, "languange.notice"),
            inline=False
        )
        
        embed.set_footer(text=f"Server ID: {ctx.guild.id}")
        return await ctx.send(embed=embed)
    
    # Convert language code to lowercase for comparison
    lang_code = lang_code.lower()
    
    # Validate language code
    if lang_code not in LANGUAGES:
        embed = discord.Embed(
            title="??Invalid Language Code / ?�効?��?語コ?�ド / ?�못???�어 코드 / Kode Bahasa Tidak Valid",
            description=(
                "Please use one of these codes / 以下??��?�ド??��?�れ?�を使用?�て?�だ?�い / ?�음 코드 �??�나�??�용?�세??/ Gunakan salah satu kode berikut:\n"
                "?��?�� `EN` - English\n"
                "?��?�� `ID` - Bahasa Indonesia\n"
                "?��?�� `KR` - ?�국??n"
                "?��?�� `JP` - ?�本�?
            ),
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
    
    # Get old language for comparison
    old_lang = get_lang(guild_id)
    
    # Update the language preference for this server
    SERVER_LANGUAGES[guild_id] = lang_code
    
    # Create confirmation embed
    embed = discord.Embed(
        title=f"{LANGUAGES[lang_code]['flag']} {get_text(guild_id, 'languange.title')}",
        color=EMBED_COLORS["success"]
    )
    
    # Show language change confirmation
    embed.add_field(
        name="??Language Changed / 言語が変更?�れ?�し??/ ?�어가 변경됨 / Bahasa Diubah",
        value=f"{LANGUAGES[old_lang]['flag']} {LANGUAGES[old_lang]['name']} ??{LANGUAGES[lang_code]['flag']} {LANGUAGES[lang_code]['name']}",
        inline=False
    )
    
    # Show example commands in new language
    example_commands = (
        f"**{get_text(guild_id, 'help_command_guide')}**\n"
        f"??`!help` - {get_text(guild_id, 'command_descriptions.help')}\n"
        f"??`!randomwaifu` - {get_text(guild_id, 'command_descriptions.randomwaifu')}\n"
        f"??`!info` - {get_text(guild_id, 'command_descriptions.info')}"
    )
    embed.add_field(
        name="?�� Example Commands / ?�マ?�ド�?/ ?�제 명령??/ Contoh Perintah",
        value=example_commands,
        inline=False
    )
    
    # Add server-specific notice
    embed.add_field(
        name="?�� Notice / ?�知?�せ / ?�림 / Pemberitahuan",
        value="This language setting only affects this server\n?�の言語設定は?�の?�ー?�ー?�の?�適?�さ?�ま??n???�어 ?�정?� ???�버?�만 ?�용?�니??nPengaturan bahasa hanya berlaku untuk server ini",
        inline=False
    )
    
    embed.set_footer(text=f"Server ID: {ctx.guild.id}")
    await ctx.send(embed=embed)

@bot.command(name="help")
async def help_command(ctx, *, command_name: str = None):
    """Display help command with categories and detailed information"""
    guild_id = ctx.guild.id if ctx.guild else None
    current_prefix = get_prefix(bot, ctx.message)
    
    if command_name:
        cmd = bot.get_command(command_name.lower())
        if not cmd:
            embed = discord.Embed(
                title=get_text(guild_id, "help.not_found"),
                description=get_text(guild_id, "help.use_help", prefix=current_prefix),
                color=EMBED_COLORS["error"]
            )
            return await ctx.send(embed=embed)
        
        # Command info embed
        embed = discord.Embed(
            title=get_text(guild_id, "help.command_info", prefix=current_prefix, command=cmd.name),
            description=get_text(guild_id, f"command_descriptions.{cmd.name}"),
            color=EMBED_COLORS["secondary"]
        )
        
        # Add usage field
        embed.add_field(
            name=get_text(guild_id, "help.usage"),
            value=f"`{current_prefix}{cmd.name}`",
            inline=False
        )
        
        embed.set_footer(text=get_text(guild_id, "help.return_to_menu", prefix=current_prefix))
        return await ctx.send(embed=embed)

    # Main help menu
    embed = discord.Embed(
        title=get_text(guild_id, "help.title", bot_name=BOT_INFO['name']),
        description=get_text(guild_id, "help.description", user=ctx.author.mention),
        color=EMBED_COLORS["primary"]
    )

    # Add command categories
    categories = {
        "image": "?���?,
        "reaction": "?��",
        "fun": "?��",
        "utility": "?�️"
    }

    for category, emoji in categories.items():
        category_name = get_text(guild_id, f"help.categories.{category}")
        category_desc = get_text(guild_id, f"help.category_descriptions.{category}")
        embed.add_field(
            name=f"{emoji} {category_name}",
            value=category_desc,
            inline=True
        )

    # Add quick tips
    embed.add_field(
        name=f"?�� {get_text(guild_id, 'tips')}",
        value=get_text(guild_id, 'help_command_guide', prefix=current_prefix),
        inline=False
    )
    
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_footer(text=get_text(guild_id, "help.footer", creator=BOT_INFO['creator'], count=len(bot.commands)))
    
    view = HelpView(guild_id)
    await ctx.send(embed=embed, view=view)

@bot.command(name="info")
async def bot_info(ctx):
    """Show detailed bot information"""
    guild_id = ctx.guild.id if ctx.guild else None
    uptime = datetime.now(timezone.utc) - BOT_SPECS["uptime"]
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    
    embed = discord.Embed(
        title=get_text(guild_id, "bot_info"),
        color=EMBED_COLORS["secondary"]
    )
    
    embed.add_field(
        name=get_text(guild_id, "bot_description"),
        value=BOT_INFO["description"],
        inline=False
    )
    
    embed.add_field(
        name=get_text(guild_id, "tech_specs"),
        value=(
            f"**Python Version:** {BOT_SPECS['python_version']}\n"
            f"**discord.py Version:** {BOT_SPECS['discord.py_version']}\n"
            f"**Server Count:** {BOT_SPECS['server_count']}\n"
            f"**Uptime:** {get_text(guild_id, 'uptime_format').format(days=days, hours=hours, minutes=minutes, seconds=seconds)}"
        ),
        inline=False
    )
    
    embed.set_footer(text=f"{get_text(guild_id, 'creator')}: {BOT_INFO['creator']} | v{BOT_INFO['version']}")
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    
    await ctx.send(embed=embed)

@bot.command(name="categories")
async def list_categories(ctx):
    """List all available waifu categories"""
    guild_id = ctx.guild.id if ctx.guild else None
    categories_chunk = [WAIFU_CATEGORIES[i:i+10] for i in range(0, len(WAIFU_CATEGORIES), 10)]
    
    for i, chunk in enumerate(categories_chunk, 1):
        embed = discord.Embed(
            title=get_text(guild_id, "categories_title", part=i),
            description="\n".join([f"??{cat.capitalize()}" for cat in chunk]),
            color=EMBED_COLORS["primary"]
        )
        await ctx.send(embed=embed)

@bot.command(name="randomwaifu")
async def random_waifu(ctx):
    """Get a random waifu from any category"""
    category = random.choice(WAIFU_CATEGORIES)
    await get_waifu_image(ctx, category)

for category in WAIFU_CATEGORIES:
    @bot.command(name=category)
    async def waifu_command(ctx):
        """Get a waifu image from specific category"""
        command_name = ctx.invoked_with
        await get_waifu_image(ctx, command_name)

async def get_waifu_image(ctx, category):
    guild_id = ctx.guild.id if ctx.guild else None
    try:
        response = requests.post(f"{WAIFU_API_URL}/many/sfw/{category}", json={"exclude": []})
        response.raise_for_status()
        data = response.json()
        
        if 'files' in data:
            for url in data['files'][:1]:
                embed = discord.Embed(color=EMBED_COLORS["primary"])
                embed.set_image(url=url)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=get_text(guild_id, "error_title"),
                description=get_text(guild_id, "no_image"),
                color=EMBED_COLORS["error"]
            )
            await ctx.send(embed=embed)
            
    except Exception as e:
        embed = discord.Embed(
            title=get_text(guild_id, "error_title"),
            description=get_text(guild_id, "error_occurred", error=str(e)),
            color=EMBED_COLORS["error"]
        )
        await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    guild_id = ctx.guild.id if ctx.guild else None
    if isinstance(error, commands.CommandNotFound):
        command_used = ctx.message.content.split()[0]
        embed = discord.Embed(
            title="??Perintah Tidak Ditemukan...",
            description=(
                f"```css\n[Error: Perintah '{command_used}' tidak dikenali]\n```\n"
                "*Ruri-chan terlihat sedih dan menggembungkan pipinya...*"
            ),
            color=discord.Color.from_rgb(255, 182, 193)  # Pink pastel
        )
        
        # Tambahkan gambar Ruri yang sedih dengan berbagai pilihan GIF
        sad_gifs = [
            "https://media.tenor.com/V5QWkxFgsDgAAAAC/ruri-dragon-sad.gif",  # Sedih
            "https://media.tenor.com/7SqVQQZVticAAAAC/confused-anime.gif",  # Bingung
            "https://media.tenor.com/zLpNDWqF4TUAAAAC/anime-pout.gif",      # Cemberut
            "https://media.tenor.com/z2LTFz7yfsoAAAAC/anime-girl.gif"       # Menangis
        ]
        embed.set_thumbnail(url=random.choice(sad_gifs))
        
        # Pesan Ruri yang imut dan menyedihkan
        ruri_messages = [
            f"*\"Maaf {ctx.author.mention}-chan, aku tidak mengerti perintah itu... (｡•́︿?�̀�?\"*",
            f"*\"Huweee~ Aku tidak tahu perintah itu... Apakah {ctx.author.mention}-chan salah ketik? (?�﹏??\"*",
            f"*\"{ctx.author.mention}-chan... A-aku benar-benar tidak mengerti... (｡ŏ﹏ŏ)\"*",
            f"*\"Uuuu~ Aku sudah mencoba mencari perintah itu tapi tidak ketemu... (?�?･�?\"*"
        ]
        
        embed.add_field(
            name="?�� Pesan Ruri",
            value=random.choice(ruri_messages),
            inline=False
        )
        
        # Tambahkan saran perintah yang mungkin dimaksud
        all_commands = [cmd.name for cmd in bot.commands]
        similar_commands = [cmd for cmd in all_commands if command_used[1:] in cmd or any(c in command_used[1:] for c in cmd)]
        
        if similar_commands:
            similar_text = "\n".join([f"??`{get_prefix(bot, ctx.message)}{cmd}`" for cmd in similar_commands[:3]])
            embed.add_field(
                name="??Mungkin maksudmu...",
                value=similar_text,
                inline=False
            )
        
        # Tambahkan tip untuk melihat daftar perintah
        embed.add_field(
            name="?�� Tips",
            value=f"Gunakan `{get_prefix(bot, ctx.message)}help` untuk melihat semua perintah yang tersedia~",
            inline=False
        )
        
        # Tambahkan footer yang imut
        embed.set_footer(text="?�� Ruri akan selalu berusaha menjadi lebih baik!")
        
        # Kirim pesan dan tambahkan reaksi emoji sedih
        message = await ctx.send(embed=embed)
        sad_emojis = ["?��", "?��", "?��", "??"]
        try:
            for emoji in sad_emojis[:2]:  # Batasi hanya 2 emoji untuk mengurangi rate limit
                await message.add_reaction(emoji)
        except:
            pass  # Abaikan error jika tidak bisa menambahkan reaksi
    else:
        embed = discord.Embed(
            title=get_text(guild_id, "error_title"),
            description=get_text(guild_id, "error_occurred", error=str(error)),
            color=EMBED_COLORS["error"]
        )
        await ctx.send(embed=embed)

async def setup_slash_commands():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

async def load_cogs():
    try:
        await bot.load_extension("slash_commands")
        await bot.load_extension("apisekolah")
        print("??Loaded all extensions successfully")
    except Exception as e:
        print(f"??Failed to load extensions: {e}")

def has_developer_role():
    async def predicate(ctx):
        # Check if user ID is in developer list
        if ctx.author.id in DEVELOPER_IDS:
            return True
            
        # Check if user has a role named "Developer"
        if ctx.guild is None:
            return False
        return discord.utils.get(ctx.author.roles, name="Developer") is not None
    return commands.check(predicate)

@bot.command(name="restart")
@has_developer_role()
async def restart_bot(ctx):
    """Restart the bot (Developer only)"""
    guild_id = ctx.guild.id if ctx.guild else None
    
    # Store channel ID for restart notification
    RESTART_DATA["channel_id"] = ctx.channel.id
    RESTART_DATA["is_restarting"] = True
    
    # Create restart embed
    embed = discord.Embed(
        title="?�� Memulai Ulang Bot...",
        description=(
            "```diff\n"
            "+ Mempersiapkan sistem untuk restart...\n"
            "+ Menyimpan data sementara...\n"
            "+ Mengoptimalkan cache...\n"
            "```\n"
            "Tunggu sebentar ya~ Bot akan segera kembali! ??n"
            "*Ruri-chan sedang beristirahat sejenak...*"
        ),
        color=discord.Color.from_rgb(255, 182, 193)  # Pink pastel
    )
    
    # Add developer info with fancy formatting
    embed.add_field(
        name="?�� Developer Info",
        value=(
            "```yaml\n"
            f"Restart oleh: {ctx.author.name}\n"
            f"ID         : {ctx.author.id}\n"
            f"Timestamp  : {datetime.now().strftime('%H:%M:%S')}\n"
            "```"
        ),
        inline=False
    )
    
    # Add estimated time
    embed.add_field(
        name="?�️ Perkiraan Waktu",
        value="```Estimasi: ~10 detik```",
        inline=False
    )
    
    # Add cute message
    embed.add_field(
        name="?�� Pesan Ruri",
        value=(
            "*\"Aku akan kembali dengan kekuatan penuh! "
            "Tunggu aku ya~ ?�️\"*"
        ),
        inline=False
    )
    
    # Set Ruri Dragon GIF
    embed.set_image(url="https://media.tenor.com/9CUBGKqR0KIAAAAd/ruri-dragon-cute.gif")
    embed.set_thumbnail(url="https://media.tenor.com/dqsvK2YWZJcAAAAC/ruri-dragon-anime.gif")
    
    # Set footer with cute message
    embed.set_footer(
        text="?�� Ruri Dragon akan kembali dalam sekejap! ?��",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )
    
    restart_msg = await ctx.send(embed=embed)
    
    try:
        # Add loading animation
        loading_emojis = ["?��", "??, "?��", "�?, "?��"]
        for emoji in loading_emojis:
            await restart_msg.add_reaction(emoji)
            await asyncio.sleep(0.5)
        
        await asyncio.sleep(1)
        os.execv(sys.executable, ['python'] + sys.argv)
        
    except Exception as e:
        # Reset restart data on failure
        RESTART_DATA["channel_id"] = None
        RESTART_DATA["is_restarting"] = False
        
        error_embed = discord.Embed(
            title="??Gagal Memulai Ulang",
            description=(
                "```diff\n"
                f"- Error: {str(e)}\n"
                "```\n"
                "*Maaf, sepertinya ada masalah saat memulai ulang...*"
            ),
            color=discord.Color.red()
        )
        error_embed.set_thumbnail(url="https://media.tenor.com/V5QWkxFgsDgAAAAC/ruri-dragon-sad.gif")
        await ctx.send(embed=error_embed)

@bot.command(name="ping")
async def ping(ctx):
    """Check bot latency"""
    guild_id = ctx.guild.id if ctx.guild else None
    
    # Calculate API latency
    start_time = time.time()
    message = await ctx.send("Testing API latency...")
    end_time = time.time()
    api_latency = round((end_time - start_time) * 1000)
    
    # Get bot latency
    bot_latency = round(bot.latency * 1000)
    
    # Create embed
    embed = discord.Embed(
        title=get_text(guild_id, "ping.title"),
        description=get_text(guild_id, "ping.description", latency=bot_latency, api_latency=api_latency),
        color=EMBED_COLORS["primary"]
    )
    
    await message.edit(content=None, embed=embed)

@bot.command(name="prefix")
@commands.has_permissions(manage_guild=True)
async def change_prefix(ctx, new_prefix: str = None):
    """Change the bot's prefix for this server"""
    guild_id = ctx.guild.id if ctx.guild else None
    
    if not ctx.guild:
        embed = discord.Embed(
            title="??Server Only",
            description="This command can only be used in servers!",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
        
    if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(
            title="??No Permission",
            description="You don't have permission to change the prefix!",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
    
    current_prefix = SERVER_PREFIXES.get(guild_id, DEFAULT_PREFIX)
    
    # If no prefix provided, show current prefix
    if new_prefix is None:
        embed = discord.Embed(
            title="?�️ Pengaturan Prefix",
            description=f"Prefix saat ini: `{current_prefix}`\n\nUntuk mengubah prefix, gunakan:\n`{current_prefix}prefix <prefix_baru>`",
            color=EMBED_COLORS["primary"]
        )
        return await ctx.send(embed=embed)
    
    # Validate prefix length
    if len(new_prefix) > 5:
        embed = discord.Embed(
            title="??Prefix Terlalu Panjang",
            description="Prefix tidak boleh lebih dari 5 karakter!",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
    
    # Validate prefix characters
    if not all(c.isprintable() for c in new_prefix):
        embed = discord.Embed(
            title="??Prefix Tidak Valid",
            description="Prefix mengandung karakter yang tidak valid!",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
    
    # Update the prefix
    old_prefix = current_prefix
    SERVER_PREFIXES[guild_id] = new_prefix
    
    # Create confirmation embed
    embed = discord.Embed(
        title="??Prefix Berhasil Diubah",
        description=f"Prefix lama: `{old_prefix}`\nPrefix baru: `{new_prefix}`",
        color=EMBED_COLORS["success"]
    )
    
    embed.add_field(
        name="?�� Contoh Penggunaan",
        value=f"`{new_prefix}help` - Menampilkan bantuan\n`{new_prefix}info` - Informasi bot",
        inline=False
    )
    
    embed.set_footer(text=f"Diubah oleh: {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name="daerah", aliases=["bahasadaerah", "lokalbahasa"])
async def daerah_command(ctx, *, query: str = None):
    """
    Menampilkan informasi tentang bahasa daerah di Indonesia
    """
    guild_id = ctx.guild.id if ctx.guild else None
    
    # URL API
    api_url = "https://indonesia-public-static-api.vercel.app/api/languages"
    
    # Mengirim pesan "sedang mengetik"
    async with ctx.typing():
        # Kirim animasi loading terlebih dahulu
        loading_embed = discord.Embed(
            title="?�� Mencari Informasi Bahasa Daerah...",
            description=(
                "```\nSedang mengumpulkan informasi... Mohon tunggu sebentar.\n```\n"
                "*Ruri-chan sedang mencari data untuk kamu~*"
            ),
            color=discord.Color.from_rgb(155, 89, 182)  # Ungu
        )
        loading_embed.set_thumbnail(url="https://media.tenor.com/FawYo00tBekAAAAC/loading-thinking.gif")
        loading_msg = await ctx.send(embed=loading_embed)
        
        try:
            # Fetch data from API
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status != 200:
                        embed = discord.Embed(
                            title="??Error",
                            description=f"Tidak dapat mengakses API: {response.status} {response.reason}",
                            color=discord.Color.red()
                        )
                        await loading_msg.edit(embed=embed)
                        return
                    
                    data = await response.json()
            
            # Gambar-gambar untuk representasi bahasa daerah Indonesia
            indonesia_images = [
                "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_Indonesia.svg/1200px-Flag_of_Indonesia.svg.png",
                "https://www.indonesia.travel/content/dam/indtravelrevamp/en/destinations/bali-nusa-tenggara/west-nusa-tenggara/lombok/lombok.jpg",
                "https://media.istockphoto.com/id/675172642/photo/pura-ulun-danu-bratan-temple-in-bali.jpg?s=612x612&w=0&k=20&c=_MPdmDviIyhldqhf7t6s59LiNeKyzH_Jzl7v71uZAkA=",
                "https://media.istockphoto.com/id/535169503/photo/indonesia-sumatra-traditional-batak-house.jpg?s=612x612&w=0&k=20&c=4w2ST8aM5vK3S_P3UEfYiDnvoQn3p6-PjxzQZQ3cOqM=",
                "https://media.istockphoto.com/id/508857283/photo/borobudur-temple-at-sunrise-yogyakarta-java-indonesia.jpg?s=612x612&w=0&k=20&c=pxgzWm1pVNzYbKYu7GUxLYcf0z_CBZd6w5Q_DztHaQU="
            ]
            
            # Filter data jika ada query
            if query:
                filtered_data = [lang for lang in data if query.lower() in lang.get("language", "").lower()]
                
                if not filtered_data:
                    embed = discord.Embed(
                        title="??Bahasa Daerah Tidak Ditemukan",
                        description=f"Tidak dapat menemukan bahasa daerah dengan kata kunci: `{query}`\n\n*Ruri-chan terlihat sedih karena tidak menemukan bahasa yang kamu cari...*",
                        color=discord.Color.red()
                    )
                    embed.set_thumbnail(url="https://media.tenor.com/V5QWkxFgsDgAAAAC/ruri-dragon-sad.gif")
                    await loading_msg.edit(embed=embed)
                    return
                
                # Jika hanya 1 hasil, tampilkan detail
                if len(filtered_data) == 1:
                    lang = filtered_data[0]
                    embed = discord.Embed(
                        title=f"?��?�� Bahasa Daerah: {lang['language']}",
                        description=f"Salah satu warisan budaya Indonesia yang berharga\n\n*\"Aku menemukan bahasa {lang['language']} untuk {ctx.author.mention}-chan! Ini sangat menarik~\"*",
                        color=discord.Color.from_rgb(255, 0, 0)  # Merah
                    )
                    
                    embed.add_field(name="?�� Jumlah Penutur", value=lang.get("speakers", "Tidak diketahui"), inline=True)
                    embed.add_field(name="?�� Provinsi", value=lang.get("province", "Tidak diketahui"), inline=True)
                    
                    if "iso_639-3" in lang:
                        embed.add_field(name="?���?Kode ISO 639-3", value=lang["iso_639-3"], inline=True)
                    
                    if "writing_system" in lang:
                        embed.add_field(name="?�️ Sistem Penulisan", value=lang["writing_system"], inline=True)
                    
                    # Tambahkan Tahukah Kamu
                    fun_facts = [
                        "Indonesia memiliki lebih dari 700 bahasa daerah, menjadikannya negara dengan keragaman bahasa terbesar kedua di dunia setelah Papua Nugini.",
                        "Bahasa Jawa adalah bahasa daerah dengan jumlah penutur terbanyak di Indonesia, diikuti oleh Bahasa Sunda.",
                        "Bahasa Indonesia berasal dari bahasa Melayu yang dipilih sebagai bahasa persatuan dalam Sumpah Pemuda tahun 1928.",
                        "Beberapa bahasa daerah seperti Jawa dan Bali memiliki sistem penulisan aksara mereka sendiri.",
                        "Bahasa Batak sebenarnya terdiri dari beberapa varian bahasa yang berbeda, seperti Toba, Karo, Simalungun, dan lainnya.",
                        "Bahasa Minangkabau adalah salah satu bahasa daerah di Indonesia yang memiliki jumlah penutur hingga 5,5 juta orang."
                    ]
                    
                    embed.add_field(
                        name="?�� Tahukah Kamu?",
                        value=random.choice(fun_facts),
                        inline=False
                    )
                    
                    embed.set_footer(text="Data bahasa daerah Indonesia | Sumber: github.com/Mahes2/bahasa-daerah-indonesia")
                    embed.set_thumbnail(url=random.choice(indonesia_images))
                    
                    # Tambahkan cara penggunaan
                    embed.add_field(
                        name="?�� Cara Penggunaan",
                        value=(
                            f"??`{get_prefix(bot, ctx.message)}daerah` - Menampilkan bahasa daerah acak\n"
                            f"??`{get_prefix(bot, ctx.message)}daerah <query>` - Menampilkan informasi tentang bahasa daerah"
                        ),
                        inline=False
                    )
        
        except Exception as e:
            embed = discord.Embed(
                title="??Error",
                description=f"Terjadi kesalahan saat mencari informasi bahasa daerah: {str(e)}",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

@bot.command(name="prefix")
@commands.has_permissions(manage_guild=True)
async def change_prefix(ctx, new_prefix: str = None):
    """Change the bot's prefix for this server"""
    guild_id = ctx.guild.id if ctx.guild else None
    
    if not ctx.guild:
        embed = discord.Embed(
            title="??Server Only",
            description="This command can only be used in servers!",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
        
    if not ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(
            title="??No Permission",
            description="You don't have permission to change the prefix!",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
    
    current_prefix = SERVER_PREFIXES.get(guild_id, DEFAULT_PREFIX)
    
    # If no prefix provided, show current prefix
    if new_prefix is None:
        embed = discord.Embed(
            title="?�️ Pengaturan Prefix",
            description=f"Prefix saat ini: `{current_prefix}`\n\nUntuk mengubah prefix, gunakan:\n`{current_prefix}prefix <prefix_baru>`",
            color=EMBED_COLORS["primary"]
        )
        return await ctx.send(embed=embed)
    
    # Validate prefix length
    if len(new_prefix) > 5:
        embed = discord.Embed(
            title="??Prefix Terlalu Panjang",
            description="Prefix tidak boleh lebih dari 5 karakter!",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
    
    # Validate prefix characters
    if not all(c.isprintable() for c in new_prefix):
        embed = discord.Embed(
            title="??Prefix Tidak Valid",
            description="Prefix mengandung karakter yang tidak valid!",
            color=EMBED_COLORS["error"]
        )
        return await ctx.send(embed=embed)
    
    # Update the prefix
    old_prefix = current_prefix
    SERVER_PREFIXES[guild_id] = new_prefix
    
    # Create confirmation embed
    embed = discord.Embed(
        title="??Prefix Berhasil Diubah",
        description=f"Prefix lama: `{old_prefix}`\nPrefix baru: `{new_prefix}`",
        color=EMBED_COLORS["success"]
    )
    
    embed.add_field(
        name="?�� Contoh Penggunaan",
        value=f"`{new_prefix}help` - Menampilkan bantuan\n`{new_prefix}info` - Informasi bot",
        inline=False
    )
    
    embed.set_footer(text=f"Diubah oleh: {ctx.author.name}")
    await ctx.send(embed=embed)
