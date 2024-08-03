from flask import request, render_template, current_app as app
from bot.discord_bot import bot, get_user_info
from utils.helpers import format_elapsed_time
import time
import discord

@app.route('/get_presence/<int:user_id>', methods=['GET'])
def get_presence(user_id):
    user_data = get_user_info(user_id)
    user_name = user_data['user_name']
    user_avatar_url = user_data['user_avatar_url']
    banner_url = user_data['banner_url']

    latest_activity = user_data['latest_activity']
    activity_info = user_data['activity_info']

    activities_html = "<p>currently not doing anything!</p>"

    if latest_activity:
        current_time = int(time.time())
        formatted_elapsed_time = format_elapsed_time(current_time - latest_activity.start.timestamp())

        if isinstance(latest_activity, discord.Spotify):
            activity_info['elapsed_time'] = formatted_elapsed_time
            activities_html = f"""
            <div style="text-align: left;">
                <p><u><strong >{activity_info['song_title']}</strong></u><br>
                by <u>{activity_info['artist']}</u><br>
                on <u>{activity_info['album']}</u><br>
                </p>
            </div>
            """
        else:
            activity_info['elapsed_time'] = formatted_elapsed_time
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
                           main_activitylogo_url=activity_info.get("activity_logo_url", "https://i.pinimg.com/originals/63/f5/6f/63f56f97a2fb9648cb8b07a78953b70b.gif"),
                           activities_html=activities_html)
