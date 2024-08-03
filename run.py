from app import create_app
from bot import run_bot
import os
from dotenv import load_dotenv
from threading import Thread

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

if __name__ == '__main__':
    app = create_app()
    
    bot_thread = Thread(target=run_bot, args=(DISCORD_BOT_TOKEN,))
    bot_thread.start()

    app.run(port=5000)
