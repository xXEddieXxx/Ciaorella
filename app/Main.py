import discord
from discord.ext import commands, tasks
import re
from datetime import datetime, timedelta
import json
import os

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

DATA_FILE = "config/dates.json"
ROLE_NAME = "Abwesend"

DATE_PATTERN = re.compile(
    r"^(?:31\.(?:0[13578]|1[02])\.\d{4}|"
    r"(?:29|30\.(?:0[1,3-9]|1[0-2])\.\d{4})|"
    r"(?:0[1-9]|1\d|2[0-8])\.(?:0[1-9]|1[0-2])\.\d{4}|"
    r"29\.02\.(?:[02468][048]00|[13579][26]00|\d{2}[048]|\d{2}[13579][26]))$"
)


def load_data() -> list[dict]:
    if os.path.isfile(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return []


def save_data(data: list[dict]) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
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
        data.append({"user_id": user_id, "username": username, "date": date_str, "notified": False})
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


def get_role(guild: discord.Guild) -> discord.Role | None:
    return discord.utils.get(guild.roles, name=ROLE_NAME)


async def get_member(guild: discord.Guild, user_id: int) -> discord.Member | None:
    member = guild.get_member(user_id)
    if member is None:
        try:
            member = await guild.fetch_member(user_id)
        except discord.NotFound:
            return None
    return member


async def modify_role(member: discord.Member, role: discord.Role, add: bool = True) -> bool:
    try:
        if add:
            await member.add_roles(role, reason="Abwesenheit eingetragen")
        else:
            await member.remove_roles(role, reason="Abwesenheit beendet")
        return True
    except discord.Forbidden:
        return False
    except Exception as e:
        print(f"Fehler bei Rollenänderung für {member}: {e}")
        return False


class DateModalExtend(discord.ui.Modal, title="Abwesenheit verlängern"):
    date = discord.ui.TextInput(
        label="Neues Rückkehrdatum",
        placeholder="TT.MM.JJJJ (z.B. 31.12.2024)",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        valid_date = validate_date(self.date.value)
        if not valid_date:
            await interaction.response.send_message(
                "⚠️ **Ungültiges Datum!**\nBitte verwende das Format `TT.MM.JJJJ` (z.B. 15.07.2024).",
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
                    f"✅ **Abwesenheit verlängert!**\n"
                    f"Dein neues Rückkehrdatum ist der **{valid_date.strftime('%d.%m.%Y')}**.",
                    ephemeral=True,
                )
                return

        await interaction.response.send_message(
            "ℹ️ **Keine aktive Abwesenheit**\n"
            "Du hast noch keine Abwesenheit eingetragen. Bitte trage zuerst ein Startdatum ein.",
            ephemeral=True,
        )


class ExtendAbsenceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="+2 Wochen", style=discord.ButtonStyle.primary, emoji="⏱️")
    async def set_2weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._extend_absence(interaction, weeks=2)

    @discord.ui.button(label="+4 Wochen", style=discord.ButtonStyle.primary, emoji="⏳")
    async def set_4weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._extend_absence(interaction, weeks=4)

    @discord.ui.button(label="Individuelles Datum", style=discord.ButtonStyle.secondary, emoji="📅")
    async def extend_absence(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DateModalExtend())

    async def _extend_absence(self, interaction: discord.Interaction, weeks: int):
        data = load_data()
        user_id = interaction.user.id

        for entry in data:
            if entry.get("user_id") == user_id:
                current_date = validate_date(entry["date"])
                if not current_date:
                    await interaction.response.send_message(
                        "⚠️ **Ungültiges Datum**\nBitte trage ein gültiges Rückkehrdatum ein.",
                        ephemeral=True,
                    )
                    return

                extended_date = current_date + timedelta(weeks=weeks)
                entry["date"] = extended_date.strftime("%d.%m.%Y")
                entry["notified"] = False
                save_data(data)

                await interaction.response.send_message(
                    f"✅ **Abwesenheit verlängert!**\n"
                    f"Deine Abwesenheit wurde um **{weeks} Wochen** verlängert.\n"
                    f"Neues Rückkehrdatum: **{extended_date.strftime('%d.%m.%Y')}**.",
                    ephemeral=True,
                )
                return

        await interaction.response.send_message(
            "ℹ️ **Keine aktive Abwesenheit**\n"
            "Du hast noch keine Abwesenheit eingetragen. Bitte trage zuerst ein Startdatum ein.",
            ephemeral=True,
        )


class DateModal(discord.ui.Modal, title="Abwesenheit eintragen"):
    date = discord.ui.TextInput(
        label="Rückkehrdatum",
        placeholder="TT.MM.JJJJ (z.B. 31.12.2024)",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        valid_date = validate_date(self.date.value)
        if not valid_date:
            await interaction.response.send_message(
                "⚠️ **Ungültiges Datum!**\nBitte verwende das Format `TT.MM.JJJJ` (z.B. 15.07.2024).",
                ephemeral=True,
            )
            return

        date_str = valid_date.strftime("%d.%m.%Y")
        add_or_update_entry(interaction.user.id, str(interaction.user), date_str)

        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(
                "⚠️ **Serverfehler**\nDie Abwesenheit konnte nicht eingetragen werden.",
                ephemeral=True,
            )
            return

        role = get_role(guild)
        if not role:
            await interaction.response.send_message(
                f"⚠️ **Rolle fehlt**\nDie Rolle '{ROLE_NAME}' existiert nicht.",
                ephemeral=True,
            )
            return

        member = await get_member(guild, interaction.user.id)
        if not member:
            await interaction.response.send_message(
                "⚠️ **Benutzer nicht gefunden**\nDein Profil konnte nicht identifiziert werden.",
                ephemeral=True,
            )
            return

        if not await modify_role(member, role, add=True):
            await interaction.response.send_message(
                f"⚠️ **Berechtigungsfehler**\nIch kann dir die Rolle '{ROLE_NAME}' nicht zuweisen.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"✅ **Abwesenheit eingetragen!**\n"
            f"Deine Rückkehr ist für den **{date_str}** geplant.\n"
            f"Du hast jetzt die Rolle '{ROLE_NAME}' erhalten.",
            ephemeral=True,
        )


class AbwesenheitView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="2 Wochen", style=discord.ButtonStyle.primary, emoji="⏱️", row=0)
    async def set_2weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._set_absence(interaction, days=14)

    @discord.ui.button(label="4 Wochen", style=discord.ButtonStyle.primary, emoji="⏳", row=0)
    async def set_4weeks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._set_absence(interaction, days=28)

    @discord.ui.button(label="Individuelles Datum", style=discord.ButtonStyle.secondary, emoji="📅", row=1)
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DateModal())

    @discord.ui.button(label="Abwesenheit beenden", style=discord.ButtonStyle.danger, emoji="✅", row=1)
    async def end_absence(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not remove_entry(interaction.user.id):
            await interaction.response.send_message(
                "ℹ️ **Keine aktive Abwesenheit**\nDu hast aktuell keine eingetragene Abwesenheit.",
                ephemeral=True,
            )
            return

        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(
                "⚠️ **Serverfehler**\nDie Abwesenheit konnte nicht beendet werden.",
                ephemeral=True,
            )
            return

        role = get_role(guild)
        if not role:
            await interaction.response.send_message(
                f"⚠️ **Rolle fehlt**\nDie Rolle '{ROLE_NAME}' existiert nicht.",
                ephemeral=True,
            )
            return

        member = await get_member(guild, interaction.user.id)
        if not member:
            await interaction.response.send_message(
                "⚠️ **Benutzer nicht gefunden**\nDein Profil konnte nicht identifiziert werden.",
                ephemeral=True,
            )
            return

        if not await modify_role(member, role, add=False):
            await interaction.response.send_message(
                f"⚠️ **Berechtigungsfehler**\nIch kann dir die Rolle '{ROLE_NAME}' nicht entfernen.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"✅ **Abwesenheit beendet!**\n"
            f"Deine Abwesenheit wurde erfolgreich beendet und die Rolle '{ROLE_NAME}' entfernt.",
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
                "⚠️ **Serverfehler**\nDie Abwesenheit konnte nicht eingetragen werden.",
                ephemeral=True,
            )
            return

        role = get_role(guild)
        if not role:
            await interaction.response.send_message(
                f"⚠️ **Rolle fehlt**\nDie Rolle '{ROLE_NAME}' existiert nicht.",
                ephemeral=True,
            )
            return

        member = await get_member(guild, user_id)
        if not member:
            await interaction.response.send_message(
                "⚠️ **Benutzer nicht gefunden**\nDein Profil konnte nicht identifiziert werden.",
                ephemeral=True,
            )
            return

        if not await modify_role(member, role, add=True):
            await interaction.response.send_message(
                f"⚠️ **Berechtigungsfehler**\nIch kann dir die Rolle '{ROLE_NAME}' nicht zuweisen.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"✅ **Abwesenheit eingetragen!**\n"
            f"Du bist für **{days} Tage** abwesend (bis zum **{target_date}**).\n"
            f"Du hast jetzt die Rolle '{ROLE_NAME}' erhalten.",
            ephemeral=True,
        )


@tasks.loop(minutes=1)
async def check_dates():
    data = load_data()
    today = datetime.now()
    today_str = today.strftime("%d.%m.%Y")
    yesterday = (today - timedelta(days=1)).strftime("%d.%m.%Y")
    changed = False

    for entry in data:
        user_id = entry.get("user_id")
        user_date = entry.get("date")
        notified = entry.get("notified")

        # Benachrichtigung am Rückkehrtag
        if not notified and user_date == today_str:
            user = bot.get_user(user_id)
            if user:
                try:
                    await user.send(
                        f"## ⏰ Rückkehrtag erreicht\n"
                        f"Deine eingetragene Abwesenheit endet heute am **{user_date}**!\n\n"
                        f"Möchtest du deine Abwesenheit verlängern?",
                        view=ExtendAbsenceView()
                    )
                    entry["notified"] = True
                    changed = True
                except Exception as e:
                    print(f"Fehler beim Senden der Nachricht an {entry['username']}: {e}")

        # Rolle entfernen nach Ablauf
        elif user_date <= yesterday:
            guilds = bot.guilds
            for guild in guilds:
                member = await get_member(guild, user_id)
                if member:
                    role = get_role(guild)
                    if role and await modify_role(member, role, add=False):
                        print(f"Rolle '{ROLE_NAME}' entfernt für {entry['username']}.")
                        try:
                            await member.send(
                                f"## ✅ Abwesenheit beendet\n"
                                f"Deine Abwesenheitsperiode ist abgelaufen.\n"
                                f"Die Rolle '{ROLE_NAME}' wurde automatisch entfernt."
                            )
                        except Exception as e:
                            print(f"Fehler bei Benachrichtigung: {entry['username']}: {e}")

            entry["remove"] = True

    new_data = [entry for entry in data if not entry.get("remove")]
    if len(new_data) != len(data):
        changed = True

    if changed:
        save_data(new_data)


@bot.event
async def on_ready():
    print(f"Bot gestartet als {bot.user} (ID: {bot.user.id})")
    if not check_dates.is_running():
        check_dates.start()

    embed = discord.Embed(
        title="📅 Abwesenheitsmanager",
        description=(
            "### Verwalte deine Abwesenheit im Server\n\n"
            "Mit diesem System kannst du:\n"
            "▫️ Abwesenheit für 2 oder 4 Wochen eintragen\n"
            "▫️ Individuelle Rückkehrdaten festlegen\n"
            "▫️ Automatische Benachrichtigungen erhalten\n"
            "▫️ Deine Abwesenheit jederzeit beenden\n\n"
            "**Du erhältst die Rolle 'Abwesend', solange du als abwesend markiert bist.**"
        ),
        color=0x890024,
    )
    embed.set_footer(text="Bot Service bereitgestellt von Eddie")
    embed.set_thumbnail(url="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse4.mm.bing.net%2Fth%3Fid%3DOIP.x_6qM1AmmYi6eRt5wSDTmgHaEP%26pid%3DApi&f=1&ipt=c7cad40f0364ecfb964a6a14ad31df561274ec59ceb976aeade7a7e5b9b5d142&ipo=images")

    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages and channel.permissions_for(guild.me).manage_messages:
                try:
                    def is_bot(m):
                        return m.author == bot.user

                    deleted = await channel.purge(limit=100, check=is_bot)
                    print(f"{len(deleted)} Bot-Nachrichten in #{channel.name} gelöscht")
                except Exception as e:
                    print(f"Löschfehler in #{channel.name}: {e}")

                await channel.send(embed=embed, view=AbwesenheitView())
                return

