import discord
from discord.ext import commands
import requests
import os
from utils.helpers import format_elapsed_time
import time

intents = discord.Intents.default()
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def get_user_info(user_id):
    user_name = None
    user_avatar_url = None
    
    headers = {
        'Authorization': f'Bot {os.getenv("DISCORD_BOT_TOKEN")}',
    }
    response = requests.get(f'https://discord.com/api/v10/users/{user_id}', headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        banner = user_data.get('banner', None)
        
        if banner:
            file_format = "gif" if banner.startswith("a_") else "png"
            banner_url = f"https://cdn.discordapp.com/banners/{user_id}/{banner}.{file_format}?size=4096"
        else:
            banner_url = 'https://via.placeholder.com/500x150?text=No+Banner'
    else:
        banner_url = 'https://via.placeholder.com/500x150?text=No+Banner'
    
    latest_activity = None
    latest_start_time = 0
    activity_info = {}

    for guild in bot.guilds:
        member = guild.get_member(user_id)
        if member:
            user_name = member.global_name
            user_avatar_url = member.avatar.url if member.avatar else None
            
            for activity in member.activities:
                start_time = getattr(activity, 'start', None)
                if start_time:
                    start_timestamp = start_time.timestamp()
                    if start_timestamp > latest_start_time:
                        latest_activity = activity
                        latest_start_time = start_timestamp

    if latest_activity:
    
        if isinstance(latest_activity, discord.Spotify):
            activity_info = {
                "song_title": latest_activity.title,
                "artist": latest_activity.artist,
                "album": latest_activity.album,
                "track_id": latest_activity.track_id,
                "song_elapsed": format_elapsed_time(int(time.time()) - latest_activity.start.timestamp()),
                "song_duration": format_elapsed_time(latest_activity.duration.total_seconds()),
                "activity_logo_url": latest_activity.album_cover_url,
                "track_url":latest_activity.track_url,
            }
        else:
            activity_info = {
            "type": type(latest_activity).__name__,
            "start_time": latest_activity.start,
            "activity_name": getattr(latest_activity, 'name', "N/A"),
            "details": getattr(latest_activity, 'details', 'N/A'),
            "state": getattr(latest_activity, 'state', 'N/A'),
            "activity_logo_url": latest_activity.large_image_url if latest_activity.large_image_url else "https://via.placeholder.com/500x150?text=No+Image"
        }
    return {
        "user_name": user_name,
        "user_avatar_url": user_avatar_url,
        "banner_url": banner_url,
        "latest_activity": latest_activity,
        "activity_info": activity_info,
    }
