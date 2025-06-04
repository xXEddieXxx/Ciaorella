import discord
from discord.ext import commands, tasks
import re
from datetime import datetime, timedelta
import json
import os

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

DATA_FILE = "dates.json"
ROLE_NAME = "Abwesend"

DATE_PATTERN = re.compile(
    r"^(?:(?:31\.(?:0[13578]|1[02])\.\d{4})|"
    r"(?:29|30\.(?:0[1,3-9]|1[0-2])\.\d{4})|"
    r"(?:0[1-9]|1\d|2[0-8])\.(?:0[1-9]|1[0-2])\.\d{4}|"
    r"(?:29\.02\.(?:(?:[02468][048]00)|(?:[13579][26]00)|(?:\d{2}[048])|(?:\d{2}[13579][26]))))$"
)

def load_data() -> list[dict]:
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_data(data: list[dict]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_or_update_entry(user_id: int, username: str, date_str: str) -> None:
    data = load_data()
    for entry in data:
        if entry.get("user_id") == user_id:
            entry["date"] = date_str
            entry["notified"] = False
            break
    else:
        data.append({
            "user_id": user_id,
            "username": username,
            "date": date_str,
            "notified": False
        })
    save_data(data)

def remove_entry(user_id: int) -> bool:
    data = load_data()
    new_data = [e for e in data if e.get("user_id") != user_id]
    if len(new_data) == len(data):
        return False
    save_data(new_data)
    return True

def validate_date(date_str: str) -> datetime | None:
    if not DATE_PATTERN.match(date_str):
        return None
    try:
        return datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        return None

async def get_role(guild: discord.Guild) -> discord.Role | None:
    return discord.utils.get(guild.roles, name=ROLE_NAME)

async def assign_role(member: discord.Member, role: discord.Role) -> bool:
    try:
        await member.add_roles(role, reason="Datum eingetragen - Abwesend Rolle zugewiesen")
        return True
    except discord.Forbidden:
        return False
    except Exception:
        return False

async def remove_role(member: discord.Member, role: discord.Role) -> bool:
    try:
        await member.remove_roles(role, reason="Abwesenheit beendet - Rolle entfernt")
        return True
    except discord.Forbidden:
        return False
    except Exception:
        return False

class DateModalExtend(discord.ui.Modal, title="Abwesenheit verlängern (Datum eingeben)"):
    date = discord.ui.TextInput(
        label="Neues Datum",
        placeholder="Gib das neue Datum ein (DD.MM.YYYY)",
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        valid_date = validate_date(self.date.value)
        if not valid_date:
            await interaction.response.send_message(
                "❌ Ungültiges Datum! Bitte geben Sie ein gültiges Datum im Format `DD.MM.YYYY` ein.",
                ephemeral=True,
            )
            return

        data = load_data()
        user_id = interaction.user.id
        for entry in data:
            if entry.get("user_id") == user_id:
                entry["date"] = valid_date.strftime("%d.%m.%Y")
                entry["notified"] = False
                save_data(data)
                await interaction.response.send_message(
                    f"✅ Deine Abwesenheit wurde auf den **{valid_date.strftime('%d.%m.%Y')}** verlängert.",
                    ephemeral=True,
                )
                return

        await interaction.response.send_message(
            "ℹ️ Du hast keine bestehende Abwesenheit. Bitte trage zuerst ein Datum ein.",
            ephemeral=True,
        )

class ExtendAbsenceView(discord.ui.View):
    @discord.ui.button(label="2 Wochen verlängern", style=discord.ButtonStyle.primary)
    async def set_2weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
      await self._set_absence(interaction, days=14)

    @discord.ui.button(label="4 Wochen verlängern", style=discord.ButtonStyle.primary)
    async def set_4weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
      await self._set_absence(interaction, days=28)

    @discord.ui.button(label="Abwesenheit verlängern", style=discord.ButtonStyle.secondary)
    async def extend_absence(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DateModalExtend())

class DateModal(discord.ui.Modal, title="Datum eingeben (DD.MM.YYYY)"):
    date = discord.ui.TextInput(
        label="Datum",
        placeholder="Gib ein Datum im Format DD.MM.YYYY ein",
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        valid_date = validate_date(self.date.value)
        if not valid_date:
            await interaction.response.send_message(
                "❌ Ungültiges Datum! Bitte geben Sie ein gültiges Datum im Format `DD.MM.YYYY` ein.",
                ephemeral=True,
            )
            return

        date_str = valid_date.strftime("%d.%m.%Y")
        add_or_update_entry(interaction.user.id, str(interaction.user), date_str)

        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(
                "⚠️ Fehler: Kein Serverkontext gefunden, Rolle konnte nicht zugewiesen werden.",
                ephemeral=True,
            )
            return

        role = await get_role(guild)
        if not role:
            await interaction.response.send_message(
                f"⚠️ Die Rolle '{ROLE_NAME}' existiert nicht. Bitte erstellen Sie sie zuerst.",
                ephemeral=True,
            )
            return

        member = guild.get_member(interaction.user.id)
        if not member:
            await interaction.response.send_message(
                "⚠️ Fehler: Mitglied konnte nicht gefunden werden.",
                ephemeral=True,
            )
            return

        if not await assign_role(member, role):
            await interaction.response.send_message(
                f"⚠️ Ich habe keine Berechtigung, die Rolle '{ROLE_NAME}' zu vergeben.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"✅ Vielen Dank {interaction.user.mention}! Du hast das Datum eingegeben: **{date_str}**.\n"
            f"Die Rolle '{ROLE_NAME}' wurde dir zugewiesen.",
            ephemeral=True,
        )

class ModalButton(discord.ui.View):
    @discord.ui.button(label="2 Wochen", style=discord.ButtonStyle.primary)
    async def set_2weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._set_absence(interaction, days=14)

    @discord.ui.button(label="4 Wochen", style=discord.ButtonStyle.primary)
    async def set_4weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._set_absence(interaction, days=28)

    @discord.ui.button(label="Individuelle Abwesenheit", style=discord.ButtonStyle.primary)
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DateModal())

    @discord.ui.button(label="Abwesenheit beenden", style=discord.ButtonStyle.danger)
    async def end_absence(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not remove_entry(interaction.user.id):
            await interaction.response.send_message("ℹ️ Du hast keine Abwesenheit eingetragen.", ephemeral=True)
            return

        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(
                "⚠️ Fehler: Kein Serverkontext gefunden, Rolle konnte nicht entfernt werden.",
                ephemeral=True,
            )
            return

        role = await get_role(guild)
        if not role:
            await interaction.response.send_message(
                f"⚠️ Die Rolle '{ROLE_NAME}' existiert nicht.",
                ephemeral=True,
            )
            return

        member = guild.get_member(interaction.user.id)
        if not member:
            await interaction.response.send_message(
                "⚠️ Fehler: Mitglied konnte nicht gefunden werden.",
                ephemeral=True,
            )
            return

        if not await remove_role(member, role):
            await interaction.response.send_message(
                f"⚠️ Ich habe keine Berechtigung, die Rolle '{ROLE_NAME}' zu entfernen.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"✅ Deine Abwesenheit wurde beendet und die Rolle '{ROLE_NAME}' entfernt.",
            ephemeral=True,
        )

    async def _set_absence(self, interaction: discord.Interaction, days: int):
      target_date = (datetime.now() + timedelta(days=days)).strftime("%d.%m.%Y")
      user_id = interaction.user.id
      username = str(interaction.user)

      add_or_update_entry(user_id, username, target_date)

      guild = interaction.guild
      if not guild:
        await interaction.response.send_message(
          "⚠️ Fehler: Kein Serverkontext gefunden, Rolle konnte nicht zugewiesen werden.",
          ephemeral=True,
        )
        return

      role = await get_role(guild)
      if not role:
        await interaction.response.send_message(
          f"⚠️ Die Rolle '{ROLE_NAME}' existiert nicht. Bitte erstellen Sie sie zuerst.",
          ephemeral=True,
        )
        return

      member = guild.get_member(user_id)
      if not member:
        await interaction.response.send_message(
          "⚠️ Fehler: Mitglied konnte nicht gefunden werden.",
          ephemeral=True,
        )
        return

      if not await assign_role(member, role):
        await interaction.response.send_message(
          f"⚠️ Ich habe keine Berechtigung, die Rolle '{ROLE_NAME}' zu vergeben.",
          ephemeral=True,
        )
        return

      await interaction.response.send_message(
        f"✅ Deine Abwesenheit wurde für **{days} Tage** gesetzt bis zum **{target_date}**.\n"
        f"Die Rolle '{ROLE_NAME}' wurde dir zugewiesen.",
        ephemeral=True,
      )

@tasks.loop(minutes=1)
async def check_dates():
    data = load_data()
    today_str = datetime.now().strftime("%d.%m.%Y")
    changed = False

    for entry in data:
        if not entry.get("notified") and entry.get("date") == today_str:
            user = bot.get_user(entry["user_id"])
            if user:
                try:
                    await user.send(
                        f"📅 Hallo {entry['username']}, dein eingetragenes Datum **{entry['date']}** ist heute erreicht!",
                        view=ExtendAbsenceView()
                    )
                    entry["notified"] = True
                    changed = True
                except Exception as e:
                    print(f"Fehler beim Senden der Nachricht an {entry['username']}: {e}")

    if changed:
        save_data(data)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    if not check_dates.is_running():
        check_dates.start()

    embed = discord.Embed(
        title="🤖 Willkommen!",
        description="Klicke auf den Button unten, um ein Datum einzugeben.",
        color=0x890024
    )
    embed.set_footer(text="Bot bereitgestellt von Eddie")

    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(embed=embed, view=ModalButton())
                return

