from flask import Flask, render_template, request
from flask_cors import CORS
from dotenv import load_dotenv
import discord
from discord.ext import commands
import os
import time
import requests

# Load environment variables from .env file
load_dotenv()

# Get the bot token from environment variable
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

app = Flask(__name__)
CORS(app)  # Enable CORS

def format_elapsed_time(seconds):
    if seconds is None:
        return "N/A"
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}:{int(minutes):02}:{int(seconds):02}"

@app.route('/get_presence/<int:user_id>', methods=['GET'])
def get_presence(user_id):
    user_name = None
    user_avatar_url = None
    
    headers = {
        'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
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
    activities_html = "<p>No activity found.</p>"

    for guild in bot.guilds:
        member = guild.get_member(user_id)
        if member:
            user_name = member.name
            user_avatar_url = member.avatar.url if member.avatar else None
            
            for activity in member.activities:
                start_time = getattr(activity, 'start', None)
                if start_time:
                    start_timestamp = start_time.timestamp()
                    if start_timestamp > latest_start_time:
                        latest_activity = activity
                        latest_start_time = start_timestamp
    
    if latest_activity:
        current_time = int(time.time())
        start_time = getattr(latest_activity, 'start', None)
        elapsed_time = current_time - start_time.timestamp() if start_time else None
        formatted_elapsed_time = format_elapsed_time(elapsed_time)

        if isinstance(latest_activity, discord.Spotify):
            activity_info = {
                "activity_type": "Spotify",
                "song_title": latest_activity.title,
                "artist": latest_activity.artist,
                "album": latest_activity.album,
                "track_id": latest_activity.track_id,
                "song_elapsed": format_elapsed_time(current_time - latest_activity.start.timestamp()),
                "song_duration": format_elapsed_time(latest_activity.duration.total_seconds()),
                "activity_logo_url": latest_activity.album_cover_url,
                "elapsed_time": formatted_elapsed_time,
            }

            activities_html = f"""
            <div style="text-align: left;">
                <p><strong>{activity_info['song_title']}</strong><br>
                by {activity_info['artist']}<br>
                on  {activity_info['album']}<br>
                </p>
            </div>
            """
        else:
            activity_info = {
                "activity_type": type(latest_activity).__name__,
                "activity_name": getattr(latest_activity, 'name', "N/A"),
                "details": getattr(latest_activity, 'details', 'N/A'),
                "state": getattr(latest_activity, 'state', 'N/A'),
                "activity_logo_url": latest_activity.large_image_url,
                "elapsed_time": formatted_elapsed_time,
            }

            
            
            activities_html = f"""
            <div style="text-align: left;">
                <p>{activity_info['activity_name']}<br>
                {activity_info['details'] + '<br>' if activity_info['details'] else ''}
                {activity_info['state'] + '<br>' if activity_info['state'] else ''}
                {activity_info['elapsed_time']}
                </p>
            </div>
        """

    return render_template('user_presence.html',
                           user_name=user_name,
                           user_avatar_url=user_avatar_url,
                           banner_url=banner_url,
                           main_activitylogo_url=activity_info.get("activity_logo_url", 'https://via.placeholder.com/100x100?text=No+Activity'),
                           activities_html=activities_html)


def run_bot():
    bot.run(DISCORD_BOT_TOKEN)

if __name__ == '__main__':
    from threading import Thread

    bot_thread = Thread(target=run_bot)
    bot_thread.start()

    app.run(port=5000)
