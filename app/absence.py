import discord
from datetime import datetime, timedelta
from config import (
    get_guild_config, get_role, get_member, modify_role,
    validate_date, add_or_update_entry, remove_entry, DEFAULT_ROLE_NAME
)
from logger import logger

class DateModalExtend(discord.ui.Modal, title="Abwesenheit verlängern"):
    date = discord.ui.TextInput(
        label="Neues Rückkehrdatum",
        placeholder="TT.MM.JJJJ (z.B. 31.12.2024)",
        required=True
    )
    async def on_submit(self, interaction: discord.Interaction):
        valid_date = validate_date(self.date.value)
        logger.info(f"User {interaction.user} attempts to extend absence to {self.date.value}")
        if not valid_date:
            await interaction.response.send_message(
                "⚠️ **Ungültiges Datum!**\nBitte verwende das Format `TT.MM.JJJJ`.", ephemeral=True)
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
                return
        logger.warning(f"User {interaction.user} tried to extend non-existing absence.")
        await interaction.response.send_message(
            "ℹ️ **Keine aktive Abwesenheit**\nTrage zuerst ein Startdatum ein.", ephemeral=True)

class ExtendAbsenceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="+2 Wochen", style=discord.ButtonStyle.primary, emoji="⏱️", custom_id="extend_2w")
    async def set_2weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._extend_absence(interaction, weeks=2)

    @discord.ui.button(label="+4 Wochen", style=discord.ButtonStyle.primary, emoji="⏳", custom_id="extend_4w")
    async def set_4weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._extend_absence(interaction, weeks=4)

    @discord.ui.button(label="Individuelles Datum", style=discord.ButtonStyle.secondary, emoji="📅", custom_id="extend_custom")
    async def extend_absence(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DateModalExtend())

    async def _extend_absence(self, interaction: discord.Interaction, weeks: int):
        from config import load_data, save_data
        data = load_data()
        user_id = interaction.user.id
        for entry in data:
            if entry.get("user_id") == user_id:
                current_date = validate_date(entry["date"])
                if not current_date:
                    logger.warning(f"User {interaction.user} has invalid current absence date.")
                    await interaction.response.send_message(
                        "⚠️ **Ungültiges Datum**\nBitte trage ein gültiges Rückkehrdatum ein.", ephemeral=True)
                    return
                extended_date = current_date + timedelta(weeks=weeks)
                entry["date"] = extended_date.strftime("%d.%m.%Y")
                entry["notified"] = False
                save_data(data)
                logger.info(f"User {interaction.user} extended absence by {weeks} weeks to {extended_date.strftime('%d.%m.%Y')}")
                await interaction.response.send_message(
                    f"✅ **Abwesenheit verlängert!**\nNeues Rückkehrdatum: **{extended_date.strftime('%d.%m.%Y')}**.", ephemeral=True)
                return
        logger.warning(f"User {interaction.user} tried to extend non-existing absence.")
        await interaction.response.send_message(
            "ℹ️ **Keine aktive Abwesenheit**\nTrage zuerst ein Startdatum ein.", ephemeral=True)

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
            await interaction.response.send_message(
                "⚠️ **Ungültiges Datum!**\nBitte verwende das Format `TT.MM.JJJJ`.", ephemeral=True)
            return
        date_str = valid_date.strftime("%d.%m.%Y")
        add_or_update_entry(interaction.user.id, str(interaction.user), date_str)
        guild = interaction.guild
        config = get_guild_config(guild.id)
        role_name = config.get("role_name", DEFAULT_ROLE_NAME)
        role = get_role(guild, role_name)
        member = await get_member(guild, interaction.user.id)
        if not role or not member or not await modify_role(member, role, add=True):
            logger.error(f"Failed to assign role '{role_name}' to {interaction.user} in guild {guild.id}")
            await interaction.response.send_message(
                f"⚠️ Fehler: Kann Rolle `{role_name}` nicht zuweisen.", ephemeral=True)
            return
        logger.info(f"User {interaction.user} assigned role '{role_name}' in guild {guild.id}")
        await interaction.response.send_message(
            f"✅ **Abwesenheit eingetragen!**\nBis **{date_str}**.", ephemeral=True)

class AbwesenheitView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent

    @discord.ui.button(label="2 Wochen", style=discord.ButtonStyle.primary, emoji="⏱️", row=0, custom_id="absence_2w")
    async def set_2weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._set_absence(interaction, days=14)

    @discord.ui.button(label="4 Wochen", style=discord.ButtonStyle.primary, emoji="⏳", row=0, custom_id="absence_4w")
    async def set_4weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._set_absence(interaction, days=28)

    @discord.ui.button(label="Individuelles Datum", style=discord.ButtonStyle.secondary, emoji="📅", row=1, custom_id="absence_custom")
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DateModal())

    @discord.ui.button(label="Abwesenheit beenden", style=discord.ButtonStyle.danger, emoji="✅", row=1,
                       custom_id="absence_end")
    async def end_absence(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not remove_entry(interaction.user.id):
            logger.warning(f"User {interaction.user} tried to end non-existing absence.")
            await interaction.response.send_message(
                "Keine aktive Abwesenheit.", ephemeral=True)
            return
        guild = interaction.guild
        config = get_guild_config(guild.id)
        role_name = config.get("role_name", DEFAULT_ROLE_NAME)
        role = get_role(guild, role_name)
        member = await get_member(guild, interaction.user.id)
        if not role or not member or not await modify_role(member, role, add=False):
            logger.error(f"Failed to remove role '{role_name}' from {interaction.user} in guild {guild.id}")
            await interaction.response.send_message(
                f"Fehler: Kann Rolle `{role_name}` nicht entfernen.", ephemeral=True)
            return
        logger.info(f"User {interaction.user} ended absence and role '{role_name}' was removed.")
        await interaction.response.send_message(
            f"✅ **Abwesenheit beendet!**", ephemeral=True)
    async def _set_absence(self, interaction: discord.Interaction, days: int):
        target_date = (datetime.now() + timedelta(days=days)).strftime("%d.%m.%Y")
        logger.info(f"User {interaction.user} sets absence for {days} days (until {target_date})")
        add_or_update_entry(interaction.user.id, str(interaction.user), target_date)
        guild = interaction.guild
        config = get_guild_config(guild.id)
        role_name = config.get("role_name", DEFAULT_ROLE_NAME)
        role = get_role(guild, role_name)
        member = await get_member(guild, interaction.user.id)
        if not role or not member or not await modify_role(member, role, add=True):
            logger.error(f"Failed to assign role '{role_name}' to {interaction.user} in guild {guild.id}")
            await interaction.response.send_message(
                f"Fehler: Kann Rolle `{role_name}` nicht zuweisen.", ephemeral=True)
            return
        logger.info(f"User {interaction.user} assigned absence role '{role_name}' until {target_date}")
        await interaction.response.send_message(
            f"✅ **Abwesenheit eingetragen!**\nBis **{target_date}**.", ephemeral=True)
