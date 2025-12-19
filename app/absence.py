from __future__ import annotations
import discord
from datetime import datetime, timedelta
from app.localization import tg
from config import (
    get_guild_config, get_role, get_member, modify_role,
    validate_date, add_or_update_entry, remove_entry, DEFAULT_ROLE_NAME, ABSENCE_MANAGER_THUMB_URL
)
from logger import logger

async def log_absence_event_by_guild(client: discord.Client, guild_id: int, message: str):
    guild = client.get_guild(guild_id)
    if not guild:
        return

    config = get_guild_config(guild_id)
    log_channel_id = config.get("logging_channel_id")
    if not log_channel_id:
        return

    log_channel = guild.get_channel(log_channel_id)
    if not log_channel:
        return
    await log_channel.send(message)

async def assign_absence_role(interaction, add=True):
    guild = interaction.guild
    config = get_guild_config(guild.id)
    role_name = config.get("role_name", DEFAULT_ROLE_NAME)
    role = get_role(guild, role_name)
    member = await get_member(guild, interaction.user.id)
    if not role or not member or not await modify_role(member, role, add=add):
        action = tg(guild.id, "common.assign_verb") if add else tg(guild.id, "common.remove_verb")
        logger.error(f"Failed to {action} role '{role_name}' for {interaction.user} in guild {guild.id}")
        await interaction.response.send_message(
            tg(guild.id, "errors.role_modify", role=role_name, action=action),
            ephemeral=True
        )
        return False
    logger.info(f"User {interaction.user} {'assigned' if add else 'removed'} role '{role_name}' in guild {guild.id}")
    return True

async def respond_absence_set(interaction, until_date):
    await interaction.response.send_message(
        tg(interaction.guild.id, "absence.set_ok", date=until_date),
        ephemeral=True
    )

async def respond_absence_end(interaction):
    await interaction.response.send_message(
        tg(interaction.guild.id, "absence.end_ok"),
        ephemeral=True
    )

async def respond_invalid_date(interaction):
    await interaction.response.send_message(
        tg(interaction.guild.id, "absence.invalid_date"),
        ephemeral=True
    )

class DateModalExtend(discord.ui.Modal):
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        super().__init__(title=tg(guild_id, "ui.modal_extend_title"))

        self.date_input = discord.ui.TextInput(
            label=tg(guild_id, "ui.input_return_new_label"),
            placeholder=tg(guild_id, "ui.input_date_placeholder"),
            required=True
        )
        self.add_item(self.date_input)

    async def on_submit(self, interaction: discord.Interaction):
        valid_date = validate_date(self.date_input.value)
        logger.info(f"User {interaction.user} attempts to extend absence to {self.date_input.value}")
        if not valid_date:
            await respond_invalid_date(interaction)
            return

        from config import load_data, save_data
        data = load_data()
        user_id = interaction.user.id

        for entry in data:
            if entry.get("user_id") == user_id and entry.get("guild_id") == self.guild_id:
                entry["date"] = valid_date.strftime("%d.%m.%Y")
                entry["notified"] = False
                save_data(data)

                await interaction.response.send_message(
                    tg(interaction.guild.id, "absence.extend_ok", date=valid_date.strftime("%d.%m.%Y")),
                    ephemeral=True
                )

                await log_absence_event_by_guild(
                    interaction.client,
                    self.guild_id,
                    tg(self.guild_id, "log.absence_extended_until", user=interaction.user.mention,
                       date=valid_date.strftime("%d.%m.%Y"))
                )
                return

        await interaction.response.send_message(
            tg(interaction.guild.id, "absence.no_active_hint"),
            ephemeral=True
        )

async def _extend_absence(interaction: discord.Interaction, weeks: int, guild_id: int):
    from config import load_data, save_data
    data = load_data()
    user_id = interaction.user.id

    for entry in data:
        if entry.get("user_id") == user_id and entry.get("guild_id") == guild_id:
            current_date = validate_date(entry["date"])
            if not current_date:
                await respond_invalid_date(interaction)
                return

            extended_date = current_date + timedelta(weeks=weeks)
            extended_str = extended_date.strftime("%d.%m.%Y")
            entry["date"] = extended_str
            entry["notified"] = False
            save_data(data)

            await interaction.response.send_message(
                tg(interaction.guild.id, "absence.extend_ok", date=extended_str),
                ephemeral=True
            )

            await log_absence_event_by_guild(
                interaction.client,
                guild_id,
                tg(guild_id, "log.absence_extended_by_days", user=interaction.user.mention, days=weeks * 7, date=extended_str)
            )
            return

    await interaction.response.send_message(
        tg(interaction.guild.id, "absence.no_active_hint"),
        ephemeral=True
    )

class ExtendAbsenceView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id

        self.set_2weeks.label = tg(guild_id, "ui.btn_extend_2w")
        self.set_4weeks.label = tg(guild_id, "ui.btn_extend_4w")
        self.extend_absence.label = tg(guild_id, "ui.btn_extend_custom")

    @discord.ui.button(label="+2 Wochen", style=discord.ButtonStyle.primary, emoji="⏱️", custom_id="extend_2w")
    async def set_2weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _extend_absence(interaction, weeks=2, guild_id=self.guild_id)

    @discord.ui.button(label="+4 Wochen", style=discord.ButtonStyle.primary, emoji="⏳", custom_id="extend_4w")
    async def set_4weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _extend_absence(interaction, weeks=4, guild_id=self.guild_id)

    @discord.ui.button(label="Individuelles Datum", style=discord.ButtonStyle.secondary, emoji="🗓️", custom_id="extend_custom")
    async def extend_absence(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DateModalExtend(guild_id=self.guild_id))


class DateModal(discord.ui.Modal):
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        super().__init__(title=tg(guild_id, "ui.modal_set_title"))

        self.date_input = discord.ui.TextInput(
            label=tg(guild_id, "ui.input_return_label"),
            placeholder=tg(guild_id, "ui.input_date_placeholder"),
            required=True
        )
        self.add_item(self.date_input)

    async def on_submit(self, interaction: discord.Interaction):
        valid_date = validate_date(self.date_input.value)
        logger.info(f"User {interaction.user} sets absence date to {self.date_input.value}")
        if not valid_date:
            await respond_invalid_date(interaction)
            return

        date_str = valid_date.strftime("%d.%m.%Y")
        add_or_update_entry(interaction.user.id, str(interaction.user), date_str, interaction.guild.id)

        if not await assign_absence_role(interaction, add=True):
            remove_entry(interaction.user.id, interaction.guild.id)
            return

        await respond_absence_set(interaction, date_str)
        await log_absence_event_by_guild(
            interaction.client,
            interaction.guild.id,
            tg(interaction.guild.id, "log.absence_set", user=interaction.user.mention, date=date_str)
        )

async def _set_absence(interaction: discord.Interaction, days: int):
    target_date = (datetime.now() + timedelta(days=days)).strftime("%d.%m.%Y")
    logger.info(f"User {interaction.user} sets absence for {days} days (until {target_date})")
    add_or_update_entry(interaction.user.id, str(interaction.user), target_date, interaction.guild.id)
    if not await assign_absence_role(interaction, add=True):
        remove_entry(interaction.user.id, interaction.guild.id)
        return
    await respond_absence_set(interaction, target_date)
    await log_absence_event_by_guild(
        interaction.client,
        interaction.guild.id,
        tg(interaction.guild.id, "log.absence_set", user=interaction.user.mention, date=target_date)
    )

class AbwesenheitView(discord.ui.View):
    def __init__(self, guild_id: int | None = None):
        super().__init__(timeout=None)
        self.guild_id = guild_id

        if guild_id is not None:
            self.set_2weeks.label = tg(guild_id, "ui.btn_2w")
            self.set_4weeks.label = tg(guild_id, "ui.btn_4w")
            self.open_modal.label = tg(guild_id, "ui.btn_custom_date")
            self.end_absence.label = tg(guild_id, "ui.btn_end")

    @discord.ui.button(label="2 Wochen", style=discord.ButtonStyle.primary, emoji="⏱️", row=0, custom_id="absence_2w")
    async def set_2weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _set_absence(interaction, days=14)

    @discord.ui.button(label="4 Wochen", style=discord.ButtonStyle.primary, emoji="⏳", row=0, custom_id="absence_4w")
    async def set_4weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _set_absence(interaction, days=28)

    @discord.ui.button(label="Individuelles Datum", style=discord.ButtonStyle.secondary, emoji="🗓️", row=1, custom_id="absence_custom")
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        gid = self.guild_id or interaction.guild.id
        await interaction.response.send_modal(DateModal(guild_id=gid))

    @discord.ui.button(label="Abwesenheit beenden", style=discord.ButtonStyle.danger, emoji="✅", row=1, custom_id="absence_end")
    async def end_absence(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not remove_entry(interaction.user.id, interaction.guild.id):
            await interaction.response.send_message(tg(interaction.guild.id, "absence.no_active"), ephemeral=True)
            return

        if not await assign_absence_role(interaction, add=False):
            return

        await respond_absence_end(interaction)
        await log_absence_event_by_guild(
            interaction.client,
            interaction.guild.id,
            tg(interaction.guild.id, "log.absence_ended", user=interaction.user.mention)
        )

def build_manager_embed(guild_id: int) -> discord.Embed:
    embed = discord.Embed(
        title=tg(guild_id, "ui.manager_title"),
        description=tg(guild_id, "ui.manager_desc"),
        color=0x890024,
    )
    embed.set_footer(text=tg(guild_id, "ui.manager_footer"))
    embed.set_thumbnail(url=ABSENCE_MANAGER_THUMB_URL)
    return embed