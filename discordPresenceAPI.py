import discord
from discord.ext import commands
from flask import Flask, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv
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
    activity_logo_url = None

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
                        
                        # Fetch the application logo (large image) if available
                        if activity.assets and 'large_image' in activity.assets:
                            asset_id = activity.assets['large_image'].split(':')[-1]
                            activity_logo_url = f"https://cdn.discordapp.com/app-assets/{activity.application_id}/{asset_id}.png"

    if latest_activity:
        activity_info = {
            "activity_type": type(latest_activity).__name__,
            "activity_name": getattr(latest_activity, 'name', "N/A"),
            "details": getattr(latest_activity, 'details', 'N/A'),
            "state": getattr(latest_activity, 'state', 'N/A'),
            "activity_logo_url": activity_logo_url
        }
        
        # Calculate elapsed time
        current_time = int(time.time())
        start_time = getattr(latest_activity, 'start', None)
        elapsed_time = current_time - start_time.timestamp() if start_time else None
        activity_info["elapsed_time"] = format_elapsed_time(elapsed_time)
        
        # Additional Spotify-specific info
        if isinstance(latest_activity, discord.Spotify):
            activity_info.update({
                "song_title": latest_activity.title,
                "artist": latest_activity.artist,
                "album": latest_activity.album,
                "track_id": latest_activity.track_id,
                "song_elapsed": format_elapsed_time(current_time - latest_activity.start.timestamp()),
                "song_duration": format_elapsed_time(latest_activity.duration.total_seconds())
            })
        
        activities_html = f"""
        <div style="text-align: left;">
            <p>{activity_info['activity_name']}<br>
            {activity_info['details']}<br>
            {activity_info['state']}<br>
            {activity_info['elapsed_time']}<br>
            {', <strong>Song:</strong> ' + activity_info['song_title'] + ', <strong>Artist:</strong> ' + activity_info['artist'] + ', <strong>Album:</strong> ' + activity_info['album'] + ', <strong>Elapsed:</strong> ' + activity_info['song_elapsed'] + ', <strong>Duration:</strong> ' + activity_info['song_duration'] if activity_info['activity_type'] == 'Spotify' else ''}
            </p>
        </div>
        """

        if activity.assets and 'small_image' in activity.assets:
            small_asset_id = activity.assets['small_image'].split(':')[-1]
            small_icon_url = f"https://cdn.discordapp.com/app-assets/{activity.application_id}/{small_asset_id}.png"

        if activity_info['activity_logo_url']:
            main_activitylogo_url = activity_info["activity_logo_url"]
    else:
        activities_html = ''

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{user_name}'s Discord Presence</title>
        <style>
            body {{
                background-color: #2c2f33;
                color: #ffffff;
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 20px;
                margin: 0;
            }}
            .profile {{
                display: grid; 
                grid-template-columns: 1.6fr 1.4fr; 
                grid-template-rows: 1fr 1fr; 
                gap: 0px 0px; 
                grid-template-areas: 
                    "top top"
                    "bottom bottom"; 
                margin: 20px auto;
                padding: 20px;
                background-color: #23272a;
                border-radius: 10px;
                width: fit-content;
                align-items: center;
            }}
            .top {{ grid-area: top;display: flex; }}
            .bottom {{ grid-area: bottom; }}
            .username {{
                margin-top: 0px;
                align-items: center;
            }}
            .avatar {{
                text-align: center;
                margin-right: 20px;
                transform: scale(1.1);
                transform-origin: top left;
            }}
            .avatar img {{
                border-radius: 50%;
                margin-bottom: 10px;
            }}
            .banner-container {{
                display: flex;
                flex-direction: column;
                align-items: flex-start;
            }}
            .banner {{
            }}
            .banner img{{
                width:300px;
                heught=110px;
                border-radius: 10px;
            }}
            .activity-container {{
                display: flex;
                align-items: stretch;
            }}
            .activity {{
                margin-top: -10px;
            }}
            .activity-logo{{
                height: 128px;
                width: 128px;
                transform: scale(0.7);
                background-repeat: no-repeat; /* Prevent repeating the image */
                
                
                border-radius: 20px;
                
                transform-origin: left top;
                background-image: url('{main_activitylogo_url}');
            }}
        </style>
    </head>
    <body>
        <div class="profile">
            <div class="top">
            <div class="avatar">
                <img src="{user_avatar_url}" alt="Avatar" width="100" height="100">
                <p class="username">{user_name}</p>
            </div>
            
            <div class="banner-container">
                <div class="banner">
                    <img src="{banner_url}" alt="Banner">
                </div>
            </div>
        </div>
            <div class="bottom">
                <div class="activity-container">
                    <div class="activity-logo"></div>
                    <div class="activity">{activities_html}</div>
                </div>
            </div>
        </div>
        
    </body>
    </html>
    """
    
    return render_template_string(html_template)




def run_bot():
    bot.run(DISCORD_BOT_TOKEN)

if __name__ == '__main__':
    from threading import Thread

    bot_thread = Thread(target=run_bot)
    bot_thread.start()

    app.run(port=5000)
