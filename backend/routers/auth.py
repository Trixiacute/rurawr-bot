from fastapi import APIRouter, HTTPException, Request, Response, Cookie
from fastapi.responses import JSONResponse
import requests
import httpx
import os
from typing import Dict, Optional
import json

# Buat router untuk endpoint auth
router = APIRouter(prefix="/auth", tags=["auth"])

# Discord OAuth2 config
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "1231886560606158859")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "m9oLKeqdeLih6BzV7RVV3TI5yOhpKXH4")
# Gunakan FRONTEND_URL sebagai basis untuk redirect_uri
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
DISCORD_REDIRECT_URI = f"{FRONTEND_URL}/auth/callback"
# Default to at least one guild ID to prevent empty list errors
ALLOWED_GUILD_IDS = os.getenv("ALLOWED_GUILD_IDS", "123456789").split(",")  

# Discord API endpoints
DISCORD_API_URL = "https://discord.com/api/v10"
DISCORD_TOKEN_URL = f"{DISCORD_API_URL}/oauth2/token"
DISCORD_USER_URL = f"{DISCORD_API_URL}/users/@me"
DISCORD_GUILDS_URL = f"{DISCORD_API_URL}/users/@me/guilds"

@router.post("/logout")
@router.get("/logout")
async def logout(response: Response, request: Request):
    """
    Logout user dari Discord OAuth session dan hapus cookies
    """
    print("=== Logout endpoint called ===")
    print(f"Request method: {request.method}")
    print(f"Request headers: {dict(request.headers)}")
    
    try:
        # Cetak cookies yang ada sebelum dihapus
        cookies = request.cookies
        print(f"Cookies before deletion: {cookies}")
        
        # Hapus cookies saja tanpa mencoba revoke token
        response.delete_cookie(key="discord_token")
        response.delete_cookie(key="refresh_token")
        print("Cookies marked for deletion")
        
        # Tambahkan HTTP header untuk CORS
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        response.headers["Access-Control-Allow-Origin"] = frontend_url
        response.headers["Access-Control-Allow-Credentials"] = "true"
        print(f"Added CORS headers, allowing origin: {frontend_url}")
        
        return {"message": "Logout successful"}
    except Exception as e:
        print(f"Error during logout: {str(e)}")
        return {"message": f"Error during logout: {str(e)}"}

@router.post("/token")
async def exchange_code(request: Request):
    """
    Exchange authorization code for access token and user data
    """
    try:
        body = await request.body()
        data = {}
        
        try:
            data = json.loads(body)
        except:
            # If JSON parsing fails, try to get form data
            form_data = await request.form()
            data = dict(form_data)
        
        code = data.get("code")
        redirect_uri = data.get("redirect_uri", DISCORD_REDIRECT_URI)
        
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code missing")
        
        # Exchange code for token
        token_data = {
            "client_id": DISCORD_CLIENT_ID,
            "client_secret": DISCORD_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "scope": "identify guilds"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Log the request for debugging
        print(f"Requesting token with data: {token_data}")
        
        token_response = requests.post(DISCORD_TOKEN_URL, data=token_data, headers=headers)
        
        if token_response.status_code != 200:
            print(f"Discord token error: {token_response.text}")
            raise HTTPException(status_code=400, detail=f"Failed to get token: {token_response.text}")
        
        token_json = token_response.json()
        access_token = token_json.get("access_token")
        token_type = token_json.get("token_type")
        
        # Get user data
        user_response = requests.get(
            DISCORD_USER_URL,
            headers={"Authorization": f"{token_type} {access_token}"}
        )
        
        if user_response.status_code != 200:
            print(f"Discord user error: {user_response.text}")
            raise HTTPException(status_code=400, detail="Failed to get user data")
        
        user_data = user_response.json()
        
        # Get guilds (servers) that the user is in
        guilds_response = requests.get(
            DISCORD_GUILDS_URL,
            headers={"Authorization": f"{token_type} {access_token}"}
        )
        
        if guilds_response.status_code != 200:
            print(f"Discord guilds error: {guilds_response.text}")
            raise HTTPException(status_code=400, detail="Failed to get guilds data")
        
        guilds_data = guilds_response.json()
        user_guild_ids = [guild["id"] for guild in guilds_data]
        
        # For development: allow access even if user is not in any allowed guild
        debug_mode = os.getenv("DEBUG_MODE", "False").lower() == "true"
        has_access = any(guild_id in ALLOWED_GUILD_IDS for guild_id in user_guild_ids) or debug_mode
        
        return {
            "access_token": access_token,
            "token_type": token_type,
            "user": user_data,
            "guilds": guilds_data,
            "has_access": has_access
        }
        
    except Exception as e:
        print(f"Auth error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/simple-logout")
async def simple_logout(request: Request):
    """
    Endpoint sangat sederhana untuk logout tanpa manipulasi cookie
    """
    print("=== Simple logout endpoint called ===")
    print(f"Request method: {request.method}")
    print(f"Request headers: {dict(request.headers)}")
    return {"message": "Simple logout successful"}

@router.get("/debug")
async def debug_info(request: Request):
    """
    Endpoint untuk debugging - menampilkan info cookies dan headers
    """
    try:
        return {
            "cookies": dict(request.cookies),
            "headers": dict(request.headers),
            "client_host": request.client.host if request.client else None,
            "discord_config": {
                "client_id": DISCORD_CLIENT_ID,
                "redirect_uri": DISCORD_REDIRECT_URI,
                "allowed_guilds": ALLOWED_GUILD_IDS,
                "debug_mode": os.getenv("DEBUG_MODE", "False")
            }
        }
    except Exception as e:
        return {"error": str(e)} 