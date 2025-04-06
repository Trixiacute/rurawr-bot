# Rurawr Discord Bot

A multifunctional Discord bot with anime features and Islamic prayer time schedule capabilities.

## File Structure

The file structure in this project has been organized to facilitate development and maintenance:

```
rurawr-bot/
├── main.py                # Main entry point
├── .env                   # Environment variables configuration file
├── README.md              # Project documentation
└── src/                   # Source code
    ├── commands/          # Bot commands
    │   ├── general/       # General commands
    │   │   ├── help.py    # Help command
    │   │   ├── info.py    # Info command
    │   │   ├── invite.py  # Invite command
    │   │   ├── ping.py    # Ping command
    │   │   └── stats.py   # Stats command
    │   ├── anime/         # Anime-related commands
    │   │   ├── anime.py   # Anime command
    │   │   └── waifu.py   # Waifu command
    │   ├── islamic/       # Islamic-related commands
    │   │   └── imsakiyah.py # Prayer time command
    │   └── settings/      # Configuration commands
    │       ├── language.py # Language command
    │       └── prefix.py  # Prefix command
    ├── core/              # Core bot components
    │   ├── bot.py         # Main bot initialization
    │   ├── config.py      # Bot configuration
    │   ├── database.py    # Database management
    │   └── presence.py    # Discord Rich Presence feature
    ├── utils/             # Utility functions
    │   └── helper.py      # Helper functions
    └── data/              # Data stored by the bot
        └── database.json  # Database file
```

## Features

- **Anime Features**
  - Anime information search
  - Random waifu image generator
  
- **Islamic Features**
  - Prayer time schedule (Imsakiyah)
  
- **Server Settings**
  - Customizable command prefix
  - Bot language settings
  
- **Other Features**
  - Dynamic Discord Rich Presence
  - Informative help menu
  - Bot usage statistics

## How to Use

1. Clone this repository
2. Create a `.env` file with the following content:
```
DISCORD_TOKEN=your_bot_token_here
```
3. Install dependencies:
```
pip install -r requirements.txt
```
4. Run the bot:
```
python main.py
```

## Rich Presence

This bot features dynamic Discord Rich Presence. The bot's status will automatically change every 5 minutes, displaying:

- Number of servers being served
- Number of users using the bot
- Bot uptime
- Bot version

## Commands

Use `!help` to see the list of available commands.

## Requirements

- Python 3.8+
- discord.py 2.0+
- requests
- python-dotenv 