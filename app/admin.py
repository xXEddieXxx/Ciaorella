import discord
from datetime import datetime
from discord import app_commands
from discord.app_commands import locale_str

from absence import AbwesenheitView, build_manager_embed
from localization import SUPPORTED_LANGUAGES, tg
from config import update_guild_config, get_guild_config, DEFAULT_ROLE_NAME, load_data, ABSENCE_MANAGER_THUMB_URL


async def _delete_absence_embeds(channel: discord.TextChannel, bot: discord.Client):
    def is_absence_embed(message: discord.Message):
        if message.author != bot.user or not message.embeds:
            return False
        emb = message.embeds[0]
        thumb_url = emb.thumbnail.url if emb.thumbnail else None
        return thumb_url == ABSENCE_MANAGER_THUMB_URL

    async for msg in channel.history(limit=500):
        if is_absence_embed(msg):
            await msg.delete()


async def _refresh_manager_message(guild: discord.Guild, bot: discord.Client) -> bool:
    cfg = get_guild_config(guild.id)
    channel_id = cfg.get("channel_id")
    if not channel_id:
        return False

    channel = guild.get_channel(channel_id)
    if not isinstance(channel, discord.TextChannel):
        return False

    try:
        await _delete_absence_embeds(channel, bot)
        await channel.send(embed=build_manager_embed(guild.id), view=AbwesenheitView(guild_id=guild.id))
        return True
    except discord.Forbidden:
        return False


def register_admin_commands(bot):
    @bot.tree.command(name="set_channel", description=locale_str("cmd.set_channel.desc"))
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
        guild_id = interaction.guild.id
        cfg = get_guild_config(guild_id)
        old_channel_id = cfg.get("channel_id")

        if old_channel_id == channel.id:
            await interaction.response.send_message(
                tg(guild_id, "admin.channel_already_set", channel=channel.mention),
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        if old_channel_id:
            old_channel = interaction.guild.get_channel(old_channel_id)
            if isinstance(old_channel, discord.TextChannel) and old_channel != channel:
                try:
                    await _delete_absence_embeds(old_channel, interaction.client)
                except discord.Forbidden:
                    pass

        update_guild_config(guild_id, channel_id=channel.id)

        try:
            await channel.send(embed=build_manager_embed(guild_id), view=AbwesenheitView(guild_id=guild_id))
        except Exception:
            await interaction.followup.send(
                tg(guild_id, "errors.send_absence_manager_failed", channel=channel.mention),
                ephemeral=True
            )
            return

        await interaction.followup.send(
            tg(guild_id, "admin.channel_updated", channel=channel.mention),
            ephemeral=True
        )

    @bot.tree.command(name="set_role", description=locale_str("cmd.set_role.desc"))
    @app_commands.checks.has_permissions(administrator=True)
    async def set_role(interaction: discord.Interaction, role: discord.Role):
        update_guild_config(interaction.guild.id, role_name=role.name)
        await interaction.response.send_message(
            tg(interaction.guild.id, "admin.role_set", role=role.name),
            ephemeral=True
        )

    @bot.tree.command(name="set_logging_channel", description=locale_str("cmd.set_logging_channel.desc"))
    @app_commands.checks.has_permissions(administrator=True)
    async def set_logging_channel(interaction: discord.Interaction, channel: discord.TextChannel):
        update_guild_config(interaction.guild.id, logging_channel_id=channel.id)
        await interaction.response.send_message(
            tg(interaction.guild.id, "admin.logging_channel_set", channel=channel.mention),
            ephemeral=True
        )

    @bot.tree.command(name="show_config", description=locale_str("cmd.show_config.desc"))
    @app_commands.checks.has_permissions(administrator=True)
    async def show_config(interaction: discord.Interaction):
        cfg = get_guild_config(interaction.guild.id)
        channel = interaction.guild.get_channel(cfg.get("channel_id"))
        log_channel = interaction.guild.get_channel(cfg.get("logging_channel_id")) if cfg.get("logging_channel_id") else None
        role_name = cfg.get("role_name", DEFAULT_ROLE_NAME)

        embed = discord.Embed(
            title=tg(interaction.guild.id, "admin.config_title"),
            description=tg(interaction.guild.id, "admin.config_desc"),
            color=0x3498db,
        )
        embed.add_field(
            name=tg(interaction.guild.id, "admin.config_channel"),
            value=channel.mention if channel else tg(interaction.guild.id, "common.not_set"),
            inline=False
        )
        embed.add_field(
            name=tg(interaction.guild.id, "admin.config_role"),
            value=role_name,
            inline=False
        )
        embed.add_field(
            name=tg(interaction.guild.id, "admin.config_logging"),
            value=log_channel.mention if log_channel else tg(interaction.guild.id, "common.not_set"),
            inline=False
        )
        embed.set_footer(text=tg(interaction.guild.id, "admin.config_footer"))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="show_absent_users", description=locale_str("cmd.show_absent_users.desc"))
    @app_commands.checks.has_permissions(administrator=True)
    async def show_absent_users(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        data = load_data()
        guild_data = [entry for entry in data if entry.get("guild_id") == interaction.guild.id]

        if not guild_data:
            await interaction.followup.send(tg(interaction.guild.id, "admin.absent_users_none"), ephemeral=True)
            return

        embed = discord.Embed(
            title=tg(interaction.guild.id, "admin.absent_users_title"),
            description=tg(interaction.guild.id, "admin.absent_users_desc"),
            color=0x3498db
        )

        for entry in guild_data:
            member = interaction.guild.get_member(entry["user_id"])
            if not member:
                continue

            return_date_str = entry.get("date", "")
            try:
                return_date = datetime.strptime(return_date_str, "%d.%m.%Y")
                relative = discord.utils.format_dt(return_date, style='R')
                embed.add_field(
                    name=member.display_name,
                    value=tg(interaction.guild.id, "admin.absent_users_entry", date=return_date_str, relative=relative),
                    inline=False
                )
            except Exception:
                embed.add_field(
                    name=member.display_name,
                    value=tg(interaction.guild.id, "admin.absent_users_invalid_date", date=return_date_str),
                    inline=False
                )

        if not embed.fields:
            await interaction.followup.send(tg(interaction.guild.id, "admin.absent_users_none_in_server"), ephemeral=True)
        else:
            await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(name="set_language", description=locale_str("cmd.set_language.desc"))
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.choices(language=[
        app_commands.Choice(name="Deutsch", value="de"),
        app_commands.Choice(name="English", value="en"),
    ])
    async def set_language(interaction: discord.Interaction, language: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        update_guild_config(interaction.guild.id, language=language.value)

        refreshed = await _refresh_manager_message(interaction.guild, interaction.client)

        msg = tg(
            interaction.guild.id,
            "admin.language_set",
            language=SUPPORTED_LANGUAGES.get(language.value, language.value),
        )
        if not refreshed:
            msg += "\n" + tg(interaction.guild.id, "admin.language_set_no_channel")

        await interaction.followup.send(msg, ephemeral=True)
