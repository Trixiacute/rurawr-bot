import discord
from discord import app_commands
from discord.ext import commands
import requests
import random
from constants import WAIFU_API_URL, WAIFU_CATEGORIES, EMBED_COLORS, BOT_INFO, COMMAND_DESCRIPTIONS

class HelpPaginator(discord.ui.View):
    def __init__(self, embeds: list[discord.Embed]):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.current_page = 0

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

class SlashCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="help", description="Tampilkan bantuan dan daftar perintah")
    async def help(self, interaction: discord.Interaction):
        # Create multiple pages for different command categories
        embeds = []
        
        # Page 1: Main Help
        main_embed = discord.Embed(
            title="🌸 Selamat Datang di Waifu Bot! 🌸",
            description=(
                f"Halo {interaction.user.mention}! Aku adalah bot anime yang bisa mengirimkan berbagai gambar bertema anime.\n\n"
                f"**Tentang Saya:**\n"
                f"• Nama: {BOT_INFO['name']}\n"
                f"• Versi: {BOT_INFO['version']}\n"
                f"• Pembuat: {BOT_INFO['creator']}\n"
                f"• Server: {len(self.bot.guilds)}\n\n"
                f"**Panduan Cepat:**\n"
                f"• Gunakan `/help` untuk melihat daftar perintah\n"
                f"• Coba `/randomwaifu` untuk mendapatkan gambar acak!\n\n"
                f"**Bantuan:**\n"
                f"Jika kamu butuh bantuan atau ingin melaporkan masalah, hubungi {BOT_INFO['creator']}"
            ),
            color=EMBED_COLORS["primary"]
        )
        main_embed.set_thumbnail(url="https://i.imgur.com/JX7f5x1.png")
        main_embed.set_footer(text=f"Halaman 1/4 • Diminta oleh {interaction.user.display_name}")
        embeds.append(main_embed)

        # Page 2: Image Commands
        image_cmds = ["waifu", "neko", "shinobu", "megumin"]
        image_embed = discord.Embed(
            title="🖼️ Perintah Gambar",
            description="Dapatkan gambar karakter anime lucu!",
            color=EMBED_COLORS["primary"]
        )
        for cmd in image_cmds:
            image_embed.add_field(
                name=f"/{cmd}",
                value=COMMAND_DESCRIPTIONS[cmd],
                inline=True
            )
        image_embed.set_footer(text=f"Halaman 2/4 • Diminta oleh {interaction.user.display_name}")
        embeds.append(image_embed)

        # Page 3: Reaction Commands
        reaction_cmds = ["hug", "kiss", "pat", "slap", "cuddle", "cry", "bully", "smile", "wave", "highfive", "handhold"]
        reaction_embed = discord.Embed(
            title="💞 Perintah Reaksi",
            description="Ekspresikan dirimu dengan reaksi anime!",
            color=EMBED_COLORS["primary"]
        )
        for cmd in reaction_cmds:
            reaction_embed.add_field(
                name=f"/{cmd}",
                value=COMMAND_DESCRIPTIONS[cmd],
                inline=True
            )
        reaction_embed.set_footer(text=f"Halaman 3/4 • Diminta oleh {interaction.user.display_name}")
        embeds.append(reaction_embed)

        # Page 4: Fun Commands
        fun_cmds = ["bite", "glomp", "kill", "happy", "wink", "poke", "dance", "cringe", "blush", "smug", "bonk"]
        fun_embed = discord.Embed(
            title="🎭 Perintah Seru",
            description="Perintah seru lainnya untuk digunakan!",
            color=EMBED_COLORS["primary"]
        )
        for cmd in fun_cmds:
            fun_embed.add_field(
                name=f"/{cmd}",
                value=COMMAND_DESCRIPTIONS[cmd],
                inline=True
            )
        fun_embed.set_footer(text=f"Halaman 4/4 • Diminta oleh {interaction.user.display_name}")
        embeds.append(fun_embed)

        # Create and send paginator
        paginator = HelpPaginator(embeds)
        await interaction.response.send_message(embed=embeds[0], view=paginator)

    @app_commands.command(name="info", description="Tampilkan informasi tentang bot")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 Informasi Waifu Bot",
            color=EMBED_COLORS["secondary"]
        )
        
        embed.add_field(
            name="📝 Deskripsi",
            value=BOT_INFO["description"],
            inline=False
        )
        
        embed.add_field(
            name="🛠️ Spesifikasi Teknis",
            value=f"**Jumlah Server:** {len(self.bot.guilds)}",
            inline=False
        )
        
        embed.set_footer(text=f"Dibuat oleh {BOT_INFO['creator']} | v{BOT_INFO['version']}")
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="categories", description="Tampilkan semua kategori yang tersedia")
    async def categories(self, interaction: discord.Interaction):
        categories_chunk = [WAIFU_CATEGORIES[i:i+10] for i in range(0, len(WAIFU_CATEGORIES), 10)]
        
        embeds = []
        for i, chunk in enumerate(categories_chunk, 1):
            embed = discord.Embed(
                title=f"Kategori Waifu (Bagian {i})",
                description="\n".join([f"• {cat.capitalize()}" for cat in chunk]),
                color=EMBED_COLORS["primary"]
            )
            embeds.append(embed)
        
        await interaction.response.send_message(embed=embeds[0])
        for embed in embeds[1:]:
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="randomwaifu", description="Get a random waifu from any category")
    async def randomwaifu(self, interaction: discord.Interaction):
        category = random.choice(WAIFU_CATEGORIES)
        await self.get_waifu_image(interaction, category)

    async def get_waifu_image(self, interaction: discord.Interaction, category: str):
        try:
            response = requests.post(f"{WAIFU_API_URL}/many/sfw/{category}", json={"exclude": []})
            response.raise_for_status()
            data = response.json()
            
            if 'files' in data:
                for url in data['files'][:1]:
                    embed = discord.Embed(color=EMBED_COLORS["primary"])
                    embed.set_image(url=url)
                    await interaction.response.send_message(embed=embed)
            else:
                embed = discord.Embed(
                    title="Error",
                    description="Couldn't fetch waifu image. Please try again later.",
                    color=EMBED_COLORS["error"]
                )
                await interaction.response.send_message(embed=embed)
                
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {str(e)}",
                color=EMBED_COLORS["error"]
            )
            await interaction.response.send_message(embed=embed)

    # Dynamic creation of commands for each category
    @app_commands.command(name="waifu", description="Get a waifu image")
    async def waifu(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "waifu")

    @app_commands.command(name="neko", description="Get a neko image")
    async def neko(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "neko")

    @app_commands.command(name="pat", description="Get a patting image")
    async def pat(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "pat")

    @app_commands.command(name="hug", description="Get a hugging image")
    async def hug(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "hug")

    @app_commands.command(name="kiss", description="Get a kissing image")
    async def kiss(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "kiss")

    @app_commands.command(name="shinobu", description="Get a Shinobu image")
    async def shinobu(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "shinobu")

    @app_commands.command(name="megumin", description="Get a Megumin image")
    async def megumin(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "megumin")

    @app_commands.command(name="bully", description="Get a bullying image")
    async def bully(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "bully")

    @app_commands.command(name="cuddle", description="Get a cuddling image")
    async def cuddle(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "cuddle")

    @app_commands.command(name="cry", description="Get a crying image")
    async def cry(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "cry")

    @app_commands.command(name="awoo", description="Get an awoo image")
    async def awoo(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "awoo")

    @app_commands.command(name="lick", description="Get a licking image")
    async def lick(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "lick")

    @app_commands.command(name="smug", description="Get a smug image")
    async def smug(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "smug")

    @app_commands.command(name="bonk", description="Get a bonking image")
    async def bonk(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "bonk")

    @app_commands.command(name="yeet", description="Get a yeeting image")
    async def yeet(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "yeet")

    @app_commands.command(name="blush", description="Get a blushing image")
    async def blush(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "blush")

    @app_commands.command(name="smile", description="Get a smiling image")
    async def smile(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "smile")

    @app_commands.command(name="wave", description="Get a waving image")
    async def wave(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "wave")

    @app_commands.command(name="highfive", description="Get a high-five image")
    async def highfive(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "highfive")

    @app_commands.command(name="handhold", description="Get a handholding image")
    async def handhold(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "handhold")

    @app_commands.command(name="bite", description="Get a biting image")
    async def bite(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "bite")

    @app_commands.command(name="glomp", description="Get a glomping image")
    async def glomp(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "glomp")

    @app_commands.command(name="kill", description="Get a killing image")
    async def kill(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "kill")

    @app_commands.command(name="happy", description="Get a happy image")
    async def happy(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "happy")

    @app_commands.command(name="wink", description="Get a winking image")
    async def wink(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "wink")

    @app_commands.command(name="poke", description="Get a poking image")
    async def poke(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "poke")

    @app_commands.command(name="dance", description="Get a dancing image")
    async def dance(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "dance")

    @app_commands.command(name="cringe", description="Get a cringing image")
    async def cringe(self, interaction: discord.Interaction):
        await self.get_waifu_image(interaction, "cringe")

async def setup(bot):
    await bot.add_cog(SlashCommands(bot)) 