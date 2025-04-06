import discord
from discord.ext import commands
from discord import app_commands
from typing import Dict, Any, Optional, List

class CommandCategory(discord.ui.Select):
    def __init__(self, bot, language_data: Dict[str, Any], guild_id: Optional[int], embed_color):
        self.bot = bot
        self.language_data = language_data
        self.guild_id = guild_id
        self.embed_color = embed_color
        
        # Get category translations
        categories = language_data.get('help', {}).get('categories', {})
        
        options = [
            discord.SelectOption(
                label=categories.get('image', '🖼️ Image Commands'), 
                description=language_data.get('help', {}).get('category_descriptions', {}).get('image', 'Commands for getting anime images'),
                emoji='🖼️',
                value='image'
            ),
            discord.SelectOption(
                label=categories.get('reaction', '💞 Reaction Commands'),
                description=language_data.get('help', {}).get('category_descriptions', {}).get('reaction', 'Commands for reactions and emotions'),
                emoji='💞',
                value='reaction'
            ),
            discord.SelectOption(
                label=categories.get('fun', '🎭 Fun Commands'), 
                description=language_data.get('help', {}).get('category_descriptions', {}).get('fun', 'Additional fun commands'),
                emoji='🎭',
                value='fun'
            ),
            discord.SelectOption(
                label=categories.get('lastfm', '🎵 Last.fm'), 
                description=language_data.get('help', {}).get('category_descriptions', {}).get('lastfm', 'Commands for displaying your Last.fm data'),
                emoji='🎵',
                value='lastfm'
            ),
            discord.SelectOption(
                label=categories.get('utility', '⚙️ Utility Commands'), 
                description=language_data.get('help', {}).get('category_descriptions', {}).get('utility', 'Utility and information commands'),
                emoji='⚙️',
                value='utility'
            )
        ]
        
        super().__init__(placeholder=language_data.get('select_category', '📚 Select a command category...'), min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        embed = await self.create_category_embed(category)
        await interaction.response.edit_message(embed=embed)

    async def create_category_embed(self, category: str) -> discord.Embed:
        # Create an embed based on the selected category
        language_data = self.language_data
        
        # Get the category name
        categories = language_data.get('help', {}).get('categories', {})
        category_name = categories.get(category, category.capitalize())
        
        # Create embed
        embed = discord.Embed(
            title=f"{category_name}",
            color=self.embed_color
        )
        
        # Categorize commands
        command_categories = {
            'image': ['waifu', 'neko', 'shinobu', 'megumin', 'randomwaifu'],
            'reaction': ['hug', 'kiss', 'pat', 'slap', 'cuddle', 'dance', 'smile', 'wave', 'blush', 'happy'],
            'fun': ['anime', 'sekolah'],
            'lastfm': ['lastfm', 'np', 'recent', 'album', 'artist', 'topalbums', 'topartists', 'countries'],
            'utility': ['help', 'ping', 'info', 'prefix', 'language', 'imsakiyah', 'update']
        }
        
        commands_list = command_categories.get(category, [])
        
        # Get command descriptions
        command_descriptions = language_data.get('command_descriptions', {})
        
        # Get the bot's prefix
        default_prefix = '!'
        prefix = default_prefix
        if hasattr(self.bot, 'get_prefix_cache'):
            prefix = self.bot.get_prefix_cache(self.guild_id) or default_prefix
        
        # Add commands to embed
        for cmd in commands_list:
            # Try to get translated command name
            cmd_name = language_data.get('commands', {}).get(cmd, cmd)
            description = command_descriptions.get(cmd, "No description available.")
            embed.add_field(name=f"`{prefix}{cmd_name}`", value=description, inline=False)
        
        # If no commands in category
        if len(commands_list) == 0:
            embed.add_field(name="No Commands", value="No commands available in this category.")
        
        # Add footer
        embed.set_footer(text=language_data.get('help', {}).get('dropdown_guide', 'Use the dropdown menu to view commands by category'))
        
        return embed 