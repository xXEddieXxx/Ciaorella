import discord

from absence import AbwesenheitView
from config import ensure_single_embed, get_guild_config
from logger import logger


def register_events(bot):
  @bot.event
  async def on_ready():
    try:
      synced = await bot.tree.sync()
      logger.info(f"Synced {len(synced)} slash commands with Discord.")
    except Exception as e:
      logger.error(f"Error syncing slash commands: {e}", exc_info=True)

    logger.info(f"Bot gestartet als {bot.user} (ID: {bot.user.id})")

    if not hasattr(bot, "_abwesenheit_view_added"):
      bot.add_view(AbwesenheitView())
      bot._abwesenheit_view_added = True
      logger.info("Registered persistent AbwesenheitView.")

    if hasattr(bot, "check_dates_loop") and not bot.check_dates_loop.is_running():
      bot.check_dates_loop.start()
      logger.info("Started absence check background task.")

    if hasattr(bot, "change_status_loop") and not bot.change_status_loop.is_running():
      bot.change_status_loop.start()
      logger.info("Started status rotation task.")

    embed = discord.Embed(
      title="📅 Abwesenheitsmanager",
      description=(
        "### Verwalte deine Abwesenheit im Server\n\n"
        "Mit diesem System kannst du:\n"
        "▫️ Abwesenheit für 2 oder 4 Wochen eintragen\n"
        "▫️ Individuelle Rückkehrdaten festlegen\n"
        "▫️ Automatische Benachrichtigungen erhalten\n"
        "▫️ Deine Abwesenheit jederzeit beenden\n\n"
        f"**Du erhältst die Abwesenheitsrolle, solange du als abwesend markiert bist.**"
      ),
      color=0x890024,
    )
    embed.set_footer(text="Verwende die Buttons unten um deine Abwesenheit zu verwalten")
    embed.set_thumbnail(url="https://pbs.twimg.com/media/DtFE2_BX4AECJ8a.jpg:large")

    for guild in bot.guilds:
      config = get_guild_config(guild.id)
      channel_id = config.get("channel_id") if config else None
      target_channel = None
      if channel_id:
        channel = guild.get_channel(channel_id)
        if channel:
          target_channel = channel
      if not target_channel:
        for channel in guild.text_channels:
          perms = channel.permissions_for(guild.me)
          if perms.send_messages and perms.manage_messages:
            target_channel = channel
            break

      if target_channel:
        try:
          await ensure_single_embed(
            target_channel,
            bot,
            embed,
            AbwesenheitView()
          )
          logger.info(f"Checked/managed absence embed in {target_channel.name} ({guild.name})")
        except Exception as e:
          logger.error(f"Error managing embed in channel #{target_channel.name}: {e}", exc_info=True)
      else:
        logger.info(f"No suitable channel found in {guild.name} for Abwesenheitsmanager.")
