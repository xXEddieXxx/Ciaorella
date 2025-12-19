import os
from discord.ext import commands

from admin import register_admin_commands
from absence import *
from tasks import register_tasks
from events import register_events
from logger import logger

PRODUCTION = False

intents = discord.Intents.default()
intents.guilds          = True
intents.members         = True
intents.message_content = True
intents.messages        = True

bot = commands.Bot(command_prefix="!", intents=intents)

register_admin_commands(bot)
register_tasks(bot)
register_events(bot)

if __name__ == "__main__":
    if PRODUCTION:
        token = os.environ.get("DISCORD_TOKEN")
        if not token:
            raise RuntimeError("No DISCORD_TOKEN set in environment variables.")
    else:
        with open("token.txt", "r") as f:
            token = f.read().strip()
    logger.info("Starting bot...")
    bot.run(token)
