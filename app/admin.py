import discord
from discord import app_commands
from config import update_guild_config, get_guild_config, DEFAULT_ROLE_NAME


def register_admin_commands(bot):
    @bot.tree.command(
        name="set_channel",
        description="Set the channel for absence messages."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
        # You could do further custom checks here, e.g. owner check
        update_guild_config(interaction.guild.id, channel_id=channel.id)
        await interaction.response.send_message(
            f"✅ **Kanal gesetzt!**\nAbwesenheitsnachrichten werden jetzt in {channel.mention} angezeigt.",
            ephemeral=True
        )

    @bot.tree.command(
        name="set_role",
        description="Set the absence role."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_role(interaction: discord.Interaction, role: discord.Role):
        update_guild_config(interaction.guild.id, role_name=role.name)
        await interaction.response.send_message(
            f"✅ **Rolle gesetzt!**\nAbwesenheitsrolle wurde auf `{role.name}` aktualisiert.",
            ephemeral=True
        )

    @bot.tree.command(
        name="show_config",
        description="Show the current bot config for this server."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def show_config(interaction: discord.Interaction):
        config = get_guild_config(interaction.guild.id)
        channel = interaction.guild.get_channel(config.get("channel_id"))
        role_name = config.get("role_name", DEFAULT_ROLE_NAME)
        embed = discord.Embed(
            title="⚙️ Bot-Konfiguration",
            color=0x3498db,
            description=f"**Aktuelle Einstellungen für diesen Server**"
        )
        embed.add_field(name="Kanal für Nachrichten", value=channel.mention if channel else "Nicht gesetzt",
                        inline=False)
        embed.add_field(name="Abwesenheitsrolle", value=role_name, inline=False)
        embed.set_footer(text="Verwende /set_channel und /set_role zum Ändern")
        await interaction.response.send_message(embed=embed, ephemeral=True)
