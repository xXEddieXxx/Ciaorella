import discord
from datetime import datetime, timedelta
from config import (
    get_guild_config, get_role, get_member, modify_role,
    validate_date, add_or_update_entry, remove_entry, DEFAULT_ROLE_NAME
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
        action = "zuweisen" if add else "entfernen"
        logger.error(f"Failed to {action} role '{role_name}' for {interaction.user} in guild {guild.id}")
        await interaction.response.send_message(
            f"Fehler: Kann Rolle `{role_name}` nicht {action}.", ephemeral=True)
        return False
    logger.info(f"User {interaction.user} {'assigned' if add else 'removed'} role '{role_name}' in guild {guild.id}")
    return True

async def respond_absence_set(interaction, until_date):
    await interaction.response.send_message(
        f"✅ **Abwesenheit eingetragen!**\nBis **{until_date}**.", ephemeral=True)

async def respond_absence_end(interaction):
    await interaction.response.send_message(
        f"✅ **Abwesenheit beendet!**", ephemeral=True)

async def respond_invalid_date(interaction):
    await interaction.response.send_message(
        "⚠️ **Ungültiges Datum!**\nBitte verwende das Format `TT.MM.JJJJ`.", ephemeral=True)


class DateModalExtend(discord.ui.Modal, title="Abwesenheit verlängern"):
  def __init__(self, guild_id):
    super().__init__()
    self.guild_id = guild_id

  date = discord.ui.TextInput(
    label="Neues Rückkehrdatum",
    placeholder="TT.MM.JJJJ (z.B. 31.12.2024)",
    required=True)

  async def on_submit(self, interaction: discord.Interaction):
        valid_date = validate_date(self.date.value)
        logger.info(f"User {interaction.user} attempts to extend absence to {self.date.value}")
        if not valid_date:
            await respond_invalid_date(interaction)
            return
        from config import load_data, save_data
        data = load_data()
        user_id = interaction.user.id
        for entry in data:
            if entry.get("user_id") == user_id:
                entry["date"] = valid_date.strftime("%d.%m.%Y")
                entry["notified"] = False
                save_data(data)
                logger.info(f"User {interaction.user} successfully extended absence to {valid_date.strftime('%d.%m.%Y')}")
                await interaction.response.send_message(
                    f"✅ **Abwesenheit verlängert!**\nNeues Rückkehrdatum: **{valid_date.strftime('%d.%m.%Y')}**.", ephemeral=True)
                guild_id = entry.get("guild_id") or interaction.guild.id
                await log_absence_event_by_guild(
                    interaction.client,
                    guild_id,
                    f"🕒 {interaction.user.mention} hat seine Abwesenheit verlängert bis **{valid_date.strftime('%d.%m.%Y')}**."
                )
                return
        logger.warning(f"User {interaction.user} tried to extend non-existing absence.")
        await interaction.response.send_message(
            "ℹ️ **Keine aktive Abwesenheit**\nTrage zuerst ein Startdatum ein.", ephemeral=True)

async def _extend_absence(interaction: discord.Interaction, weeks: int, guild_id):
    from config import load_data, save_data
    data = load_data()
    user_id = interaction.user.id
    for entry in data:
      if entry.get("user_id") == user_id and entry.get("guild_id") == guild_id:
            current_date = validate_date(entry["date"])
            if not current_date:
                logger.warning(f"User {interaction.user} has invalid current absence date.")
                await respond_invalid_date(interaction)
                return
            extended_date = current_date + timedelta(weeks=weeks)
            entry["date"] = extended_date.strftime("%d.%m.%Y")
            entry["notified"] = False
            save_data(data)
            logger.info(f"User {interaction.user} extended absence by {weeks} weeks to {extended_date.strftime('%d.%m.%Y')}")
            await interaction.response.send_message(
                f"✅ **Abwesenheit verlängert!**\nNeues Rückkehrdatum: **{extended_date.strftime('%d.%m.%Y')}**.", ephemeral=True)
            guild_id = entry.get("guild_id") or interaction.guild.id
            await log_absence_event_by_guild(
                interaction.client,
                guild_id,
                f"🕒 {interaction.user.mention} hat seine Abwesenheit um {weeks*7} Tage verlängert bis **{extended_date.strftime('%d.%m.%Y')}**."
            )
            return
    logger.warning(f"User {interaction.user} tried to extend non-existing absence.")
    await interaction.response.send_message(
        "ℹ️ **Keine aktive Abwesenheit**\nTrage zuerst ein Startdatum ein.", ephemeral=True)

class ExtendAbsenceView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(label="+2 Wochen", style=discord.ButtonStyle.primary, emoji="⏱️", custom_id="extend_2w")
    async def set_2weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _extend_absence(interaction, weeks=2, guild_id=self.guild_id)

    @discord.ui.button(label="+4 Wochen", style=discord.ButtonStyle.primary, emoji="⏳", custom_id="extend_4w")
    async def set_4weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _extend_absence(interaction, weeks=4, guild_id=self.guild_id)

    @discord.ui.button(label="Individuelles Datum", style=discord.ButtonStyle.secondary, emoji="🗓️", custom_id="extend_custom")
    async def extend_absence(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DateModalExtend(guild_id=self.guild_id))

class DateModal(discord.ui.Modal, title="Abwesenheit eintragen"):
    date = discord.ui.TextInput(
        label="Rückkehrdatum",
        placeholder="TT.MM.JJJJ (z.B. 31.12.2024)",
        required=True
    )
    async def on_submit(self, interaction: discord.Interaction):
        valid_date = validate_date(self.date.value)
        logger.info(f"User {interaction.user} sets absence date to {self.date.value}")
        if not valid_date:
            logger.warning(f"User {interaction.user} entered invalid date: {self.date.value}")
            await respond_invalid_date(interaction)
            return
        date_str = valid_date.strftime("%d.%m.%Y")
        add_or_update_entry(interaction.user.id, str(interaction.user), date_str, interaction.guild.id)
        if not await assign_absence_role(interaction, add=True):
            return
        await respond_absence_set(interaction, date_str)
        await log_absence_event_by_guild(
            interaction.client,
            interaction.guild.id,
            f"📋 {interaction.user.mention} hat sich als abwesend eingetragen bis **{date_str}**."
        )

async def _set_absence(interaction: discord.Interaction, days: int):
    target_date = (datetime.now() + timedelta(days=days)).strftime("%d.%m.%Y")
    logger.info(f"User {interaction.user} sets absence for {days} days (until {target_date})")
    add_or_update_entry(interaction.user.id, str(interaction.user), target_date, interaction.guild.id)
    if not await assign_absence_role(interaction, add=True):
        return
    await respond_absence_set(interaction, target_date)
    await log_absence_event_by_guild(
        interaction.client,
        interaction.guild.id,
        f"📋 {interaction.user.mention} hat sich als abwesend eingetragen bis **{target_date}**."
    )

class AbwesenheitView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent

    @discord.ui.button(label="2 Wochen", style=discord.ButtonStyle.primary, emoji="⏱️", row=0, custom_id="absence_2w")
    async def set_2weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _set_absence(interaction, days=14)

    @discord.ui.button(label="4 Wochen", style=discord.ButtonStyle.primary, emoji="⏳", row=0, custom_id="absence_4w")
    async def set_4weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _set_absence(interaction, days=28)

    @discord.ui.button(label="Individuelles Datum", style=discord.ButtonStyle.secondary, emoji="🗓️", row=1, custom_id="absence_custom")
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DateModal())

    @discord.ui.button(label="Abwesenheit beenden", style=discord.ButtonStyle.danger, emoji="✅", row=1,
                       custom_id="absence_end")
    async def end_absence(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not remove_entry(interaction.user.id, interaction.guild.id):
            logger.warning(f"User {interaction.user} tried to end non-existing absence.")
            await interaction.response.send_message(
                "Keine aktive Abwesenheit.", ephemeral=True)
            return
        if not await assign_absence_role(interaction, add=False):
            return
        logger.info(f"User {interaction.user} ended absence and role was removed.")
        await respond_absence_end(interaction)
        await log_absence_event_by_guild(
            interaction.client,
            interaction.guild.id,
            f"✅ {interaction.user.mention} hat die Abwesenheit beendet."
        )
