from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv
from fastapi.responses import Response
import fastapi
import pydantic

# Load environment variables from .env file
load_dotenv()

# Perubahan: Import router dari modul routers.auth
from routers.auth import router as auth_router

app = FastAPI(
    title="Ruri Dragon API",
    description="API for Ruri Dragon Discord Bot Dashboard",
    version="1.0.0"
)

# Konfigurasi CORS
origins = [
    "http://localhost:3000",  # Development frontend
    os.getenv("FRONTEND_URL", "http://localhost:3000")  # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth_router)

# Sample data models
class BotStats(BaseModel):
    total_commands: int
    active_servers: int
    messages_today: int
    school_searches: int
    lifetime_commands: int
    lifetime_messages: int
    lifetime_school_searches: int
    average_commands_per_day: int
    bot_uptime_days: int
    users_reached: int
    response_time_ms: int

class TopCommands(BaseModel):
    command_name: str
    usage_count: int
    percentage: float

class TimeSeriesData(BaseModel):
    timestamp: str
    commands: int
    active_users: int
    messages: int
    school_searches: int

# Base stats that will be modified on each API call to simulate realtime changes
base_stats = {
    "total_commands": 12345,
    "active_servers": 89,
    "messages_today": 5678,
    "school_searches": 1234,
    "lifetime_commands": 567890,
    "lifetime_messages": 892345,
    "lifetime_school_searches": 78941,
    "average_commands_per_day": 457,
    "bot_uptime_days": 138,
    "users_reached": 12450,
    "response_time_ms": 45
}

# Top commands data
top_commands = [
    {"command_name": "!sekolah", "usage_count": 28945, "percentage": 38.5},
    {"command_name": "!help", "usage_count": 15780, "percentage": 21.0},
    {"command_name": "!info", "usage_count": 9876, "percentage": 13.1},
    {"command_name": "!prefix", "usage_count": 6543, "percentage": 8.7},
    {"command_name": "!waifu", "usage_count": 5432, "percentage": 7.2}
]

# Language usage data
language_usage = {
    "id": 72.5,
    "en": 23.8,
    "jp": 3.7
}

# Function to generate dynamic stats that change on every API call
def get_dynamic_stats():
    # Create a copy of base stats
    dynamic_stats = base_stats.copy()
    
    # Increment values randomly to simulate realtime updates
    dynamic_stats["total_commands"] += random.randint(1, 10)
    dynamic_stats["active_servers"] += random.randint(-2, 3)  # Can go up or down
    dynamic_stats["messages_today"] += random.randint(5, 20)
    dynamic_stats["school_searches"] += random.randint(0, 5)
    dynamic_stats["users_reached"] += random.randint(3, 15)
    dynamic_stats["response_time_ms"] = max(20, dynamic_stats["response_time_ms"] + random.randint(-5, 5))
    
    # Update lifetime stats accordingly
    dynamic_stats["lifetime_commands"] += dynamic_stats["total_commands"] - base_stats["total_commands"]
    dynamic_stats["lifetime_messages"] += dynamic_stats["messages_today"] - base_stats["messages_today"]
    dynamic_stats["lifetime_school_searches"] += dynamic_stats["school_searches"] - base_stats["school_searches"]
    
    # Ensure active_servers doesn't go below a minimum value
    dynamic_stats["active_servers"] = max(dynamic_stats["active_servers"], 70)
    
    return dynamic_stats

# Generate updated top commands
def get_top_commands():
    updated_commands = []
    for cmd in top_commands:
        cmd_copy = cmd.copy()
        cmd_copy["usage_count"] += random.randint(0, 5)
        updated_commands.append(cmd_copy)
    return updated_commands

# Get updated language usage
def get_language_usage():
    lang_usage = language_usage.copy()
    total = 0
    for lang in lang_usage:
        change = random.uniform(-0.3, 0.3)
        lang_usage[lang] = max(0.1, lang_usage[lang] + change)
        total += lang_usage[lang]
    
    # Normalize to 100%
    for lang in lang_usage:
        lang_usage[lang] = round((lang_usage[lang] / total) * 100, 1)
    
    return lang_usage

# Generate sample time series data
def generate_time_series():
    data = []
    now = datetime.now()
    for i in range(7):
        date = now - timedelta(days=6-i)
        data.append({
            "timestamp": date.strftime("%Y-%m-%d"),
            "commands": random.randint(50, 100),
            "active_users": random.randint(20, 90),
            "messages": random.randint(100, 500),
            "school_searches": random.randint(10, 30)
        })
    return data

@app.get("/")
async def read_root():
    return {"message": "Welcome to Ruri Dragon API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/stats")
async def get_stats():
    stats = get_dynamic_stats()
    return stats

@app.get("/api/activity")
async def get_activity():
    return generate_time_series()

@app.get("/api/lifetime-stats")
async def get_lifetime_stats():
    stats = get_dynamic_stats()
    lifetime_stats = {
        "lifetime_commands": stats["lifetime_commands"],
        "lifetime_messages": stats["lifetime_messages"],
        "lifetime_school_searches": stats["lifetime_school_searches"],
        "average_commands_per_day": stats["average_commands_per_day"],
        "bot_uptime_days": stats["bot_uptime_days"],
        "users_reached": stats["users_reached"],
        "response_time_ms": stats["response_time_ms"]
    }
    return lifetime_stats

@app.get("/api/top-commands")
async def get_command_stats():
    return get_top_commands()

@app.get("/api/language-stats")
async def get_language_stats():
    return {"language_usage": get_language_usage()}

@app.get("/api/bot-performance")
async def get_bot_performance():
    return {
        "response_time_ms": get_dynamic_stats()["response_time_ms"],
        "uptime_percentage": 99.8,
        "cpu_usage": random.uniform(10, 30),
        "memory_usage": random.uniform(150, 300),
        "api_calls_per_minute": random.randint(50, 200)
    }

@app.get("/api/servers")
async def get_servers():
    # Sample server data
    servers = [
        {
            "id": "123456789",
            "name": "Ruri Fan Club",
            "member_count": 150,
            "commands_used": 1234,
            "most_used_command": "!sekolah",
            "language": "id",
            "region": "Indonesia"
        },
        {
            "id": "987654321",
            "name": "Anime Discussion",
            "member_count": 347,
            "commands_used": 876,
            "most_used_command": "!waifu",
            "language": "en",
            "region": "Global"
        },
        {
            "id": "456789123",
            "name": "School Network",
            "member_count": 523,
            "commands_used": 1567,
            "most_used_command": "!sekolah",
            "language": "id",
            "region": "Indonesia"
        }
    ]
    return servers

@app.get("/system/info")
async def system_info():
    """
    Endpoint untuk menampilkan informasi sistem dan konfigurasi
    """
    return {
        "environment": {
            "frontend_url": os.getenv("FRONTEND_URL", "http://localhost:3000"),
            "debug_mode": os.getenv("DEBUG_MODE", "False"),
            "discord": {
                "client_id": os.getenv("DISCORD_CLIENT_ID", "NOT_SET"),
                "redirect_uri": os.getenv("DISCORD_REDIRECT_URI", "NOT_SET"),
                "allowed_guild_ids": os.getenv("ALLOWED_GUILD_IDS", "").split(","),
            }
        },
        "routers": [route.path for route in app.routes],
        "version": {
            "fastapi": fastapi.__version__,
            "pydantic": pydantic.__version__,
        }
    }

# Middleware to handle CORS preflight requests
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    
    # Add CORS headers to every response
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    response.headers["Access-Control-Allow-Origin"] = frontend_url
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Cookie"
    
    # Handle OPTIONS requests
    if request.method == "OPTIONS":
        return Response(
            status_code=200,
            headers=response.headers
        )
        
    return response

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 