import discord
from discord import app_commands, Embed
from logger import logger
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
