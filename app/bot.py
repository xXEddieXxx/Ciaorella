from discord.ext import commands

from admin import register_admin_commands
from absence import *
from tasks import register_tasks
from events import register_events
from logger import logger

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

register_admin_commands(bot)
register_tasks(bot)
register_events(bot)

if __name__ == "__main__":
    with open("token.txt", "r") as f:
        token = f.read().strip()
    logger.info("Starting bot...")
    bot.run(token)
