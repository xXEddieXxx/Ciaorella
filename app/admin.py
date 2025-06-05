import discord
from discord import app_commands
from config import update_guild_config, get_guild_config, DEFAULT_ROLE_NAME

def register_admin_commands(bot):
    @bot.tree.command(
        name="set_channel",
        description="Setzt den Kanal für Abwesenheitsnachrichten."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
        update_guild_config(interaction.guild.id, channel_id=channel.id)
        await interaction.response.send_message(
            f"✅ **Kanal gesetzt!**\nAbwesenheitsnachrichten werden jetzt in {channel.mention} angezeigt.",
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