import json, os, re
from datetime import datetime
from logger import logger

DATA_FILE = "config/dates.json"
CONFIG_FILE = "config/guild_config.json"
DEFAULT_ROLE_NAME = "Abwesend"
ABSENCE_MANAGER_THUMB_URL = "https://pbs.twimg.com/media/DtFE2_BX4AECJ8a.jpg:large"

DATE_PATTERN = re.compile(
    r"^(?:31\.(?:0[13578]|1[02])\.\d{4}|"
    r"(?:29|30\.(?:0[1,3-9]|1[0-2])\.\d{4})|"
    r"(?:0[1-9]|1\d|2[0-8])\.(?:0[1-9]|1[0-2])\.\d{4}|"
    r"29\.02\.(?:[02468][048]00|[13579][26]00|\d{2}[048]|\d{2}[13579][26]))$"
)

def load_config():
    logger.info("Loading config file...")
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                logger.debug("Config file loaded.")
                return json.load(f)
        except json.JSONDecodeError:
            logger.error("Config JSON decode error.")
            return {}
    logger.warning("Config file not found, using defaults.")
    return {}

def save_config(config):
    logger.info("Saving config file.")
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def get_guild_config(guild_id):
    config = load_config()
    return config.get(str(guild_id), {
        "channel_id": None,
        "role_name": DEFAULT_ROLE_NAME,
        "logging_channel_id": None,
        "language": "de"
    })
def update_guild_config(guild_id, **kwargs):
    config = load_config()
    guild_id = str(guild_id)
    if guild_id not in config:
        config[guild_id] = {
            "channel_id": None,
            "role_name": DEFAULT_ROLE_NAME,
            "logging_channel_id": None,
            "language": "de",
        }
    for key, value in kwargs.items():
        if value is not None:
            config[guild_id][key] = value
    save_config(config)
    logger.info(f"Updated guild config for {guild_id}: {config[guild_id]}")
    return config[guild_id]

def load_data():
    logger.info("Loading absence data...")
    if os.path.isfile(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error("Absence data JSON decode error.")
    return []

def save_data(data):
    logger.info("Saving absence data.")
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_or_update_entry(user_id, username, date_str, guild_id):
    logger.info(f"Adding/updating absence entry for {username} ({user_id}) to {date_str} (guild: {guild_id})")
    data = load_data()
    for entry in data:
        if entry.get("user_id") == user_id and entry.get("guild_id") == guild_id:
            entry["date"] = date_str
            entry["notified"] = False
            break
    else:
        data.append({
            "user_id": user_id,
            "username": username,
            "date": date_str,
            "notified": False,
            "guild_id": guild_id
        })
    save_data(data)

def remove_entry(user_id, guild_id):
    logger.info(f"Removing absence entry for user {user_id} in guild {guild_id}")
    data = load_data()
    new_data = [e for e in data if not (e.get("user_id") == user_id and e.get("guild_id") == guild_id)]
    if len(new_data) == len(data):
        logger.warning(f"No entry found for user {user_id} in guild {guild_id} to remove.")
        return False
    save_data(new_data)
    return True

def validate_date(date_str):
    if not DATE_PATTERN.match(date_str):
        logger.warning(f"Date validation failed for input: {date_str}")
        return None
    try:
        parsed_date = datetime.strptime(date_str, "%d.%m.%Y")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if parsed_date < today:
            logger.warning(f"Rejected past date: {date_str}")
            return None
        return parsed_date
    except ValueError:
        logger.error(f"ValueError in date validation: {date_str}")
        return None

def get_role(guild, role_name):
    import discord
    role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        logger.warning(f"Role '{role_name}' not found in guild {guild.name}.")
    return role

async def get_member(guild, user_id):
    member = guild.get_member(user_id)
    if member is None:
        try:
            member = await guild.fetch_member(user_id)
        except Exception as e:
            logger.error(f"Failed to fetch member {user_id} in guild {guild.id}: {e}")
            return None
    return member

async def modify_role(member, role, add=True):
    try:
        if add:
            await member.add_roles(role, reason="Abwesenheit eingetragen")
            logger.info(f"Added role '{role.name}' to {member.display_name}")
        else:
            await member.remove_roles(role, reason="Abwesenheit beendet")
            logger.info(f"Removed role '{role.name}' from {member.display_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to modify role for {member.display_name}: {e}", exc_info=True)
        return False

def is_admin_or_owner(ctx):
    return ctx.author == ctx.guild.owner or ctx.author.guild_permissions.administrator

async def ensure_single_embed(channel, bot, embed, view):
  def is_absence_embed(message):
    if message.author != bot.user or not message.embeds:
        return False
    emb = message.embeds[0]
    thumb_url = emb.thumbnail.url if emb.thumbnail else None
    return thumb_url == ABSENCE_MANAGER_THUMB_URL

  messages = [m async for m in channel.history(limit=50)]
  bot_embeds = [m for m in messages if is_absence_embed(m)]

  if len(bot_embeds) == 1:
    return
  elif len(bot_embeds) == 0:
    await channel.send(embed=embed, view=view)
  else:
    for msg in bot_embeds:
      await msg.delete()
    await channel.send(embed=embed, view=view)
