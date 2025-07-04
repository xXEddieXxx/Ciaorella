import discord
from datetime import datetime
from discord import app_commands, Embed
from logger import logger
from config import update_guild_config, get_guild_config, DEFAULT_ROLE_NAME, load_data

def register_admin_commands(bot):
    @bot.tree.command(
        name="set_channel",
        description="Setzt den Kanal für Abwesenheitsnachrichten."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
        guild_id = interaction.guild.id
        config = get_guild_config(guild_id)
        old_channel_id = config.get("channel_id")

        if old_channel_id == channel.id:
            await interaction.response.send_message(
                f"⚠️ Der Kanal {channel.mention} ist bereits als Abwesenheitskanal gesetzt.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        if old_channel_id:
            old_channel = interaction.guild.get_channel(old_channel_id)
            if old_channel and old_channel != channel:
                await _delete_absence_embeds(old_channel, bot=interaction.client)

        update_guild_config(guild_id, channel_id=channel.id)

        from absence import AbwesenheitView
        embed = Embed(
            title="📅 Abwesenheitsmanager",
            description=(
                "### Verwalte deine Abwesenheit im Server\n\n"
                "▫️ Abwesenheit für 2 oder 4 Wochen eintragen\n"
                "▫️ Individuelle Rückkehrdaten festlegen\n"
                "▫️ Automatische Benachrichtigungen erhalten\n"
                "▫️ Deine Abwesenheit jederzeit beenden\n\n"
                "**Du erhältst die Abwesenheitsrolle, solange du als abwesend markiert bist.**"
            ),
            color=0x890024,
        )
        embed.set_footer(text="Verwende die Buttons unten um deine Abwesenheit zu verwalten")
        embed.set_thumbnail(url="https://pbs.twimg.com/media/DtFE2_BX4AECJ8a.jpg:large")

        try:
            await channel.send(embed=embed, view=AbwesenheitView())
        except Exception as e:
            logger.error(f"Fehler beim Senden in neuen Kanal #{channel.name}: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Fehler beim Senden der Nachricht in {channel.mention}. Bitte prüfe die Berechtigungen.",
                ephemeral=True
            )
            return

        await interaction.followup.send(
            f"✅ **Kanal aktualisiert!**\nDie Abwesenheitsnachricht wurde nach {channel.mention} verschoben.",
            ephemeral=True
        )

    @bot.tree.command(
        name="set_role",
        description="Setzt die Rolle für abwesende Mitglieder."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_role(interaction: discord.Interaction, role: discord.Role):
        update_guild_config(interaction.guild.id, role_name=role.name)
        await interaction.response.send_message(
            f"✅ **Rolle gesetzt!**\nAbwesenheitsrolle wurde auf `{role.name}` aktualisiert.",
            ephemeral=True
        )

    @bot.tree.command(
        name="set_logging_channel",
        description="Setzt den Kanal für Abwesenheits-Logs."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_logging_channel(interaction: discord.Interaction, channel: discord.TextChannel):
        update_guild_config(interaction.guild.id, logging_channel_id=channel.id)
        await interaction.response.send_message(
            f"✅ **Logging-Kanal gesetzt!**\nAlle Abwesenheitsereignisse werden jetzt in {channel.mention} geloggt.",
            ephemeral=True
        )

    @bot.tree.command(
        name="show_config",
        description="Zeigt die aktuelle Bot-Konfiguration für diesen Server."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def show_config(interaction: discord.Interaction):
        config = get_guild_config(interaction.guild.id)
        channel = interaction.guild.get_channel(config.get("channel_id"))
        log_channel = interaction.guild.get_channel(config.get("logging_channel_id")) if config.get(
            "logging_channel_id") else None
        role_name = config.get("role_name", DEFAULT_ROLE_NAME)
        embed = discord.Embed(
            title="⚙️ Bot-Konfiguration",
            color=0x3498db,
            description=f"**Aktuelle Einstellungen für diesen Server**"
        )
        embed.add_field(
            name="Kanal für Nachrichten",
            value=channel.mention if channel else "Nicht gesetzt",
            inline=False
        )
        embed.add_field(
            name="Abwesenheitsrolle",
            value=role_name,
            inline=False
        )
        embed.add_field(
            name="Logging-Kanal",
            value=log_channel.mention if log_channel else "Nicht gesetzt",
            inline=False
        )
        embed.set_footer(text="Verwende /set_channel, /set_role und /set_logging_channel zum Ändern.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(
        name="show_absent_users",
        description="Zeigt alle derzeit abwesenden Benutzer und deren geplantes Rückkehrdatum."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def show_absent_users(interaction: discord.Interaction):
      await interaction.response.defer(ephemeral=True)
      data = load_data()

      guild_data = [entry for entry in data if entry["guild_id"] == interaction.guild.id]

      if not guild_data:
        await interaction.followup.send("✅ Es sind derzeit keine Benutzer als abwesend markiert.", ephemeral=True)
        return

      embed = discord.Embed(
        title="📋 Aktuell Abwesende Mitglieder",
        description="Hier ist eine Liste der derzeit abwesenden Mitglieder und deren Rückkehrdatum.",
        color=0x3498db
      )

      for entry in guild_data:
        member = interaction.guild.get_member(entry["user_id"])
        if member:
          return_date_str = entry["date"]
          try:
            return_date = datetime.strptime(return_date_str, "%d.%m.%Y")
            time_remaining = discord.utils.format_dt(return_date, style='R')
            embed.add_field(
              name=member.display_name,
              value=f"Rückkehrdatum: **{return_date_str}**\n{time_remaining}",
              inline=False
            )
          except Exception:
            embed.add_field(
              name=member.display_name,
              value=f"Ungültiges Datum gespeichert: `{return_date_str}`",
              inline=False
            )

      if not embed.fields:
        await interaction.followup.send("✅ Es sind derzeit keine abwesenden Benutzer im Server.", ephemeral=True)
      else:
        await interaction.followup.send(embed=embed, ephemeral=True)


async def _delete_absence_embeds(channel: discord.TextChannel, bot: discord.Client):
    def is_absence_embed(message: discord.Message):
        return (
                message.author == bot.user
                and message.embeds
                and message.embeds[0].title == "📅 Abwesenheitsmanager"
        )

    try:
        async for msg in channel.history(limit=500):
            if is_absence_embed(msg):
                await msg.delete()
                logger.info(f"Gelöschtes Embed in #{channel.name} (Msg ID: {msg.id})")
    except discord.Forbidden:
        logger.warning(f"Keine Lösch‐Berechtigung in #{channel.name}, Abwesenheits‐Embed konnte nicht entfernt werden.")
    except discord.NotFound:
        logger.warning(f"Kanal #{channel.name} nicht gefunden beim Löschen des Embeds.")
