import discord
from discord.ext import commands, tasks
import re
from datetime import datetime
import json
import os

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

DATA_FILE = "dates.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_to_json(entry):
    data = load_data()
    data.append(entry)
    save_data(data)

class DateModal(discord.ui.Modal, title="Enter a Date (German Format)"):
    date = discord.ui.TextInput(
        label="Date",
        placeholder="Enter a date (DD.MM.YYYY)",
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        date_pattern = (
            r"^(?:(?:31\.(?:0[13578]|1[02])\.\d{4})|"
            r"(?:29|30\.(?:0[1,3-9]|1[0-2])\.\d{4})|"
            r"(?:0[1-9]|1\d|2[0-8])\.(?:0[1-9]|1[0-2])\.\d{4}|"
            r"(?:29\.02\.(?:(?:[02468][048]00)|(?:[13579][26]00)|(?:\d{2}[048])|(?:\d{2}[13579][26]))))$"
        )

        if not re.match(date_pattern, self.date.value):
            await interaction.response.send_message(
                "❌ Ungültiges Datum! Bitte geben Sie ein gültiges Datum im Format `DD.MM.YYYY` ein.",
                ephemeral=True,
            )
            return

        try:
            valid_date = datetime.strptime(self.date.value, "%d.%m.%Y")
        except ValueError:
            await interaction.response.send_message(
                "❌ Ungültiges Datum. Bitte prüfen Sie Ihre Eingabe.",
                ephemeral=True,
            )
            return

        data_to_save = {
            "username": str(interaction.user),
            "user_id": interaction.user.id,  # store user ID to DM later
            "date": valid_date.strftime("%d.%m.%Y"),
            "notified": False  # flag for notification sent
        }
        save_to_json(data_to_save)

        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "⚠️ Fehler: Kein Serverkontext gefunden, Rolle konnte nicht zugewiesen werden.",
                ephemeral=True,
            )
            return

        role = discord.utils.get(guild.roles, name="Abwesend")
        if role is None:
            await interaction.response.send_message(
                "⚠️ Die Rolle 'Abwesend' existiert nicht. Bitte erstellen Sie sie zuerst.",
                ephemeral=True,
            )
            return

        member = guild.get_member(interaction.user.id)
        if member is None:
            await interaction.response.send_message(
                "⚠️ Fehler: Mitglied konnte nicht gefunden werden.",
                ephemeral=True,
            )
            return

        try:
            await member.add_roles(role, reason="Datum eingetragen - Abwesend Rolle zugewiesen")
        except discord.Forbidden:
            await interaction.response.send_message(
                "⚠️ Ich habe keine Berechtigung, die Rolle 'Abwesend' zu vergeben.",
                ephemeral=True,
            )
            return
        except Exception as e:
            await interaction.response.send_message(
                f"⚠️ Beim Zuweisen der Rolle ist ein Fehler aufgetreten: {e}",
                ephemeral=True,
            )
            return

        # Send confirmation message
        await interaction.response.send_message(
            f"✅ Vielen Dank {interaction.user.mention}! Du hast das Datum eingegeben: **{valid_date.strftime('%d.%m.%Y')}**.\n"
            f"Die Rolle 'Abwesend' wurde dir zugewiesen.",
            ephemeral=True,
        )

class ModalButton(discord.ui.View):
    @discord.ui.button(label="Datum eingeben", style=discord.ButtonStyle.primary)
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = DateModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Abwesenheit beenden", style=discord.ButtonStyle.danger)
    async def end_absence(self, interaction: discord.Interaction, button: discord.ui.Button):
            user_id = interaction.user.id
            data = load_data()
            # Filter out the entries of the current user
            new_data = [entry for entry in data if entry.get("user_id") != user_id]

            if len(new_data) == len(data):
                # User entry was not found
                await interaction.response.send_message(
                    "ℹ️ Du hast keine Abwesenheit eingetragen.",
                    ephemeral=True
                )
                return

            # Save updated data without the user entry
            save_data(new_data)

            guild = interaction.guild
            if guild is None:
                await interaction.response.send_message(
                    "⚠️ Fehler: Kein Serverkontext gefunden, Rolle konnte nicht entfernt werden.",
                    ephemeral=True,
                )
                return

            role = discord.utils.get(guild.roles, name="Abwesend")
            if role is None:
                await interaction.response.send_message(
                    "⚠️ Die Rolle 'Abwesend' existiert nicht.",
                    ephemeral=True,
                )
                return

            member = guild.get_member(user_id)
            if member is None:
                await interaction.response.send_message(
                    "⚠️ Fehler: Mitglied konnte nicht gefunden werden.",
                    ephemeral=True,
                )
                return

            try:
                await member.remove_roles(role, reason="Abwesenheit beendet - Rolle entfernt")
            except discord.Forbidden:
                await interaction.response.send_message(
                    "⚠️ Ich habe keine Berechtigung, die Rolle 'Abwesend' zu entfernen.",
                    ephemeral=True,
                )
                return
            except Exception as e:
                await interaction.response.send_message(
                    f"⚠️ Beim Entfernen der Rolle ist ein Fehler aufgetreten: {e}",
                    ephemeral=True,
                )
                return

            await interaction.response.send_message(
                "✅ Deine Abwesenheit wurde beendet und die Rolle 'Abwesend' entfernt.",
                ephemeral=True,
            )

@tasks.loop(minutes=1)  # check every hour, adjust as needed
async def check_dates():
    data = load_data()
    today_str = datetime.now().strftime("%d.%m.%Y")
    changed = False

    for entry in data:
        if not entry.get("notified") and entry.get("date") == today_str:
            user = bot.get_user(entry["user_id"])
            if user:
                try:
                    await user.send(f"📅 Hallo {entry['username']}, dein eingetragenes Datum **{entry['date']}** ist heute erreicht!")
                    entry["notified"] = True
                    changed = True
                except Exception as e:
                    print(f"Fehler beim Senden der Nachricht an {entry['username']}: {e}")

    if changed:
        save_data(data)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # Start the date checking task if not already running
    if not check_dates.is_running():
        check_dates.start()

    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(
                    "🤖 Willkommen! Klicke auf den Button um ein Datum einzugeben.",
                    view=ModalButton()
                )
                return

