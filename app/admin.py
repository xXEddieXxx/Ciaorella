import discord
from discord import app_commands, Embed
from app.logger import logger
from config import update_guild_config, get_guild_config, DEFAULT_ROLE_NAME

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

        old_channel = interaction.guild.get_channel(old_channel_id) if old_channel_id else None

        if old_channel and old_channel != channel:
            try:
                def is_our_bot_message(m):
                    return m.author == interaction.client.user

                deleted = await old_channel.purge(limit=100, check=is_our_bot_message)
                logger.info(f"Deleted {len(deleted)} old messages in #{old_channel.name}")
            except Exception as e:
                logger.warning(f"Konnte alte Nachrichten in #{old_channel.name} nicht löschen: {e}")

        update_guild_config(guild_id, channel_id=channel.id)

        from absence import AbwesenheitView
        embed = discord.Embed(
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

      #not Implemented YET
"""
    @bot.tree.command(
        name="set_language",
        description="Erlaubt das Ändern der Sprache, die der Bot verwendet."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_language(interaction: discord.Interaction, language: str):
        if language not in ["de", "en"]:
            await interaction.response.send_message(
                "⚠️ Ungültige Sprache! Bitte wähle entweder `de` oder `en`.",
                ephemeral=True
            )
            return

        update_guild_config(interaction.guild.id, language=language)
        readable = "Deutsch" if language == "de" else "Englisch"
        await interaction.response.send_message(
            f"🌐 **Sprache gesetzt!**\nDer Bot verwendet jetzt **{readable}**.",
            ephemeral=True
        )
"""
