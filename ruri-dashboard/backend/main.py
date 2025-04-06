import subprocess
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import discord
from discord.ext import commands
import asyncio
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bot configuration
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Bot statistics
bot_stats = {
    "start_time": datetime.now(),
    "total_users": 0,
    "total_commands": 0,
    "total_messages": 0,
    "recent_commands": []
}

class Command(BaseModel):
    user: str
    user_avatar: str
    command: str
    timestamp: datetime
    status: str

@app.get("/api/stats")
async def get_stats():
    uptime = datetime.now() - bot_stats["start_time"]
    hours = int(uptime.total_seconds() // 3600)
    minutes = int((uptime.total_seconds() % 3600) // 60)
    
    return {
        "users": bot_stats["total_users"],
        "commands": bot_stats["total_commands"],
        "messages": bot_stats["total_messages"],
        "uptime": f"{hours}h {minutes}m"
    }

@app.get("/api/commands")
async def get_recent_commands():
    return bot_stats["recent_commands"][-10:]  # Return last 10 commands

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    bot_stats["total_users"] = len(bot.users)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    bot_stats["total_messages"] += 1
    await bot.process_commands(message)

@bot.event
async def on_command(ctx):
    bot_stats["total_commands"] += 1
    command = Command(
        user=str(ctx.author),
        user_avatar=str(ctx.author.avatar.url) if ctx.author.avatar else "",
        command=ctx.message.content,
        timestamp=datetime.now(),
        status="Success"
    )
    bot_stats["recent_commands"].append(command.dict())

def run_frontend():
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    npm_command = 'npm.cmd' if sys.platform == 'win32' else 'npm'
    
    try:
        subprocess.Popen(
            [npm_command, 'start'],
            cwd=frontend_dir,
            shell=True
        )
        print("Frontend server started at http://localhost:3000")
    except Exception as e:
        print(f"Error starting frontend server: {e}")

@app.on_event("startup")
async def startup_event():
    run_frontend()
    print("Backend server started at http://localhost:8000")
    
    # Start bot in background
    asyncio.create_task(bot.start(TOKEN))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 