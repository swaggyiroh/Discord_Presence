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

def fetch_user_banner(user_id):
    headers = {
        'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
    }
    response = requests.get(f'https://discord.com/api/v10/users/{user_id}', headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        banner = user_data.get('banner', None)
        
        if banner:
            banner_url = f'https://cdn.discordapp.com/banners/{user_id}/{banner}'
            if banner.startswith('a_'):
                banner_url += '.gif'
            else:
                banner_url += '.png'
            return banner_url
        else:
            return None
    else:
        return None

@app.route('/get_presence/<int:user_id>', methods=['GET'])
def get_presence(user_id):
    user_name = None
    user_avatar_url = None
    banner_url = fetch_user_banner(user_id)
    
    # Check if banner_url is None or invalid
    if banner_url:
        banner_url = banner_url
    else:
        banner_url = 'https://via.placeholder.com/500x150?text=No+Banner'  # Placeholder image if no banner is available
    
    latest_activity = None
    latest_start_time = 0

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
        activity_info = {
            "activity_type": type(latest_activity).__name__,
            "activity_name": getattr(latest_activity, 'name', "N/A"),
            "details": getattr(latest_activity, 'details', 'N/A'),
            "state": getattr(latest_activity, 'state', 'N/A')
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
        <p><strong>Activity:</strong> {activity_info['activity_name']}<br>
           <strong>Details:</strong> {activity_info['details']}<br>
           <strong>State:</strong> {activity_info['state']}<br>
           <strong>Elapsed Time:</strong> {activity_info['elapsed_time']}<br>
           {', <strong>Song:</strong> ' + activity_info['song_title'] + ', <strong>Artist:</strong> ' + activity_info['artist'] + ', <strong>Album:</strong> ' + activity_info['album'] + ', <strong>Elapsed:</strong> ' + activity_info['song_elapsed'] + ', <strong>Duration:</strong> ' + activity_info['song_duration'] if activity_info['activity_type'] == 'Spotify' else ''}
        </p>
        """
    else:
        activities_html = '<p>No presence data available</p>'

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
                display: flex;
                flex-direction: row;
                align-items: flex-start;
                justify-content: center;
                margin: 20px auto;
                padding: 20px;
                background-color: #23272a;
                border-radius: 10px;
                box-sizing: border-box;
                max-width: 100vw;
            }}
            .avatar {{
                text-align: center;
                margin-right: 20px;
            }}
            .avatar img {{
                border-radius: 50%;
                width: 100px;
                height: 100px;
            }}
            .banner-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                width: 100%;
                max-width: 500px;
                overflow: hidden; /* Hide overflowed parts of the banner */
            }}
            .banner {{
                width: 100%; /* Ensure the banner takes full width */
                height: auto; /* Maintain aspect ratio */
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover; /* Cover the container while maintaining aspect ratio */
                background-image: url('{banner_url}');
                border-radius: 20px;
                margin-bottom: 20px;
            }}
            .activity {{
                text-align: left;
                width: 100%;
                max-width: 500px;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="profile">
            <div class="avatar">
                <img src="{user_avatar_url}" alt="Avatar">
                <p class="username"><strong>{user_name}</strong></p>
            </div>
            <div class="banner-container">
                <div class="banner"></div>
                <div class="activity">{activities_html}</div>
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
