import discord
from discord.ext import commands
from flask import Flask, render_template_string
from flask_cors import CORS

import os

intents = discord.Intents.default()
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

app = Flask(__name__)
CORS(app) 

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

@app.route('/get_presence/<int:user_id>', methods=['GET'])
def get_presence(user_id):
    presence_data_list = []
    user_name = None

    for guild in bot.guilds:
        member = guild.get_member(user_id)
        if member:
            user_name = member.name
            for activity in member.activities:
                activity_info = {
                    "activity_type": type(activity).__name__,
                    "activity_name": getattr(activity, 'name', "N/A"),
                    "details": getattr(activity, 'details', 'N/A'),
                    "state": getattr(activity, 'state', 'N/A')
                }
                if isinstance(activity, discord.Spotify):
                    activity_info.update({
                        "song_title": activity.title,
                        "artist": activity.artist,
                        "album": activity.album,
                        "track_id": activity.track_id,
                        "start": activity.start.timestamp() if activity.start else "N/A",
                        "end": activity.end.timestamp() if activity.end else "N/A"
                    })
                if activity_info not in presence_data_list:
                    presence_data_list.append(activity_info)

    if not presence_data_list:
        html_content = '<p>No presence data available</p>'
    else:
        activities_html = ''.join([
            f"<p>Activity: {activity['activity_name']}, "
            f"Details: {activity['details']}, State: {activity['state']}"
            + (f", Song: {activity['song_title']}, Artist: {activity['artist']}, Album: {activity['album']}, "
               f"Start: {activity['start']}, End: {activity['end']}" if activity['activity_type'] == 'Spotify' else "")
            + "</p>"
            for activity in presence_data_list
        ])
        html_content = f"<p>Name: {user_name}</p>{activities_html}"

    return render_template_string(html_content)

def run_bot():
    bot.run(os.environ['DISCORD_BOT_TOKEN'])

if __name__ == '__main__':
    from threading import Thread

    bot_thread = Thread(target=run_bot)
    bot_thread.start()

    app.run(port=5000)
