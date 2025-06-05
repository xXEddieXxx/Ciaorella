from logger import logger
from absence import AbwesenheitView
from config import get_guild_config


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

        import discord
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
        embed.set_thumbnail(url="https://i.imgur.com/7F7VlEg.png")

        for guild in bot.guilds:
            config = get_guild_config(guild.id)
            channel_id = config.get("channel_id") if config else None
            if channel_id:
                channel = guild.get_channel(channel_id)
                if channel:
                    try:
                        def is_bot(m):
                            return m.author == bot.user

                        deleted = await channel.purge(limit=100, check=is_bot)
                        logger.info(f"Deleted {len(deleted)} old bot messages in {channel.name}")
                        await channel.send(embed=embed, view=AbwesenheitView())
                        logger.info(f"Sent absence message to channel {channel.name} in {guild.name}")
                        continue
                    except Exception as e:
                        logger.error(f"Error sending/purging in channel #{channel.name}: {e}", exc_info=True)
            logger.info(f"No configured channel for {guild.name}, searching for first suitable channel...")
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages and channel.permissions_for(
                        guild.me).manage_messages:
                    try:
                        def is_bot(m):
                            return m.author == bot.user

                        deleted = await channel.purge(limit=100, check=is_bot)
                        logger.info(f"Deleted {len(deleted)} old bot messages in {channel.name}")
                        await channel.send(embed=embed, view=AbwesenheitView())
                        logger.info(f"Sent absence message to channel {channel.name} in {guild.name}")
                        break
                    except Exception as e:
                        logger.error(f"Error sending/purging in channel #{channel.name}: {e}", exc_info=True)
