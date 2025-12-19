import discord

from app.absence import AbwesenheitView, build_manager_embed
from app.command_translator import TableTranslator
from app.localization import tg
from config import ensure_single_embed, get_guild_config, get_role, DEFAULT_ROLE_NAME, remove_entry
from logger import logger


def register_events(bot):
    @bot.event
    async def on_ready():
        if not hasattr(bot, "_translator_set"):
            await bot.tree.set_translator(TableTranslator())
            bot._translator_set = True
            logger.info("Registered app_commands translator.")

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

        for guild in bot.guilds:
            cfg = get_guild_config(guild.id)
            channel_id = cfg.get("channel_id") if cfg else None

            target_channel = guild.get_channel(channel_id) if channel_id else None
            if target_channel is None:
                for ch in guild.text_channels:
                    perms = ch.permissions_for(guild.me)
                    if perms.send_messages and perms.manage_messages:
                        target_channel = ch
                        break

            if target_channel:
                try:
                    embed = build_manager_embed(guild.id)
                    view = AbwesenheitView(guild_id=guild.id)
                    await ensure_single_embed(target_channel, bot, embed, view)
                    logger.info(f"Checked/managed absence embed in {target_channel.name} ({guild.name})")
                except Exception as e:
                    logger.error(f"Error managing embed in channel #{target_channel.name}: {e}", exc_info=True)
            else:
                logger.info(f"No suitable channel found in {guild.name} for Abwesenheitsmanager.")

    @bot.event
    async def on_member_update(before: discord.Member, after: discord.Member):
        if before.guild is None:
            return

        cfg = get_guild_config(after.guild.id)
        role_name = cfg.get("role_name", DEFAULT_ROLE_NAME)
        role = get_role(after.guild, role_name)
        if role is None:
            return

        had_role = role in before.roles
        has_role = role in after.roles

        if had_role and not has_role:
            if remove_entry(after.id, after.guild.id):
                log_channel_id = cfg.get("logging_channel_id")
                log_ch = after.guild.get_channel(log_channel_id) if log_channel_id else None
                if log_ch:
                    await log_ch.send(
                        tg(
                            after.guild.id,
                            "log.entry_deleted_role_removed",
                            guild=after.guild.name,
                            user=after.mention,
                            role=role.name,
                        )
                    )
                logger.info(f"Removed absence entry because role was removed: {after} in guild {after.guild.id}")
