import random
from datetime import datetime, timedelta
import discord
from discord.ext import tasks

from config import (
    load_data, save_data, get_guild_config,
    get_member, get_role, modify_role, DEFAULT_ROLE_NAME
)
from logger import logger
from absence import ExtendAbsenceView

def register_tasks(bot):
    @tasks.loop(minutes=1)
    async def check_dates():
        logger.info("Running absence check task...")
        data = load_data()
        today = datetime.now()
        today_str = today.strftime("%d.%m.%Y")
        yesterday_str = (today - timedelta(days=1)).strftime("%d.%m.%Y")
        changed = False

        for entry in data:
            user_id = entry.get("user_id")
            username = entry.get("username", "Unbekannt")
            user_date = entry.get("date")
            notified = entry.get("notified")
            guild_id = entry.get("guild_id")

            guild = bot.get_guild(guild_id)
            if not guild:
                continue

            config = get_guild_config(guild.id)
            role_name = config.get("role_name", DEFAULT_ROLE_NAME)
            role = get_role(guild, role_name)
            member = await get_member(guild, user_id)

            if not member:
                continue

            if role and role not in member.roles:
                logger.info(f"Benutzer {username} hat Rolle '{role_name}' nicht mehr – Eintrag wird entfernt.")
                try:
                    await member.send(
                        f"## ✅ Abwesenheit beendet\n"
                        f"Die Rolle **{role.name}** wurde manuell entfernt.\n"
                        f"Dein Abwesenheitsstatus wurde daher automatisch beendet."
                    )
                except Exception as e:
                    logger.warning(f"Fehler beim Senden der automatischen Abmeldung an {username}: {e}")
                log_channel_id = config.get("logging_channel_id")
                if log_channel_id:
                    log_channel = guild.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(
                            f"✅ {member.mention} hat die Abwesenheitsrolle nicht mehr. "
                            f"Eintrag wurde von einem Admin entfernt."
                        )
                entry["remove"] = True
                changed = True
                continue

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
                        logger.info(f"Notified user {user_id} of return date {user_date}.")
                    except Exception as e:
                        logger.error(f"Error notifying user {username}: {e}", exc_info=True)

            if user_date < yesterday_str:
                if role and role in member.roles and await modify_role(member, role, add=False):
                    logger.info(f"Rolle '{role_name}' entfernt für {username}.")
                    try:
                        await member.send(
                            f"## ✅ Abwesenheit beendet\n"
                            f"Deine Abwesenheitsperiode ist abgelaufen.\n"
                            f"Die Rolle '{role_name}' wurde automatisch entfernt."
                        )
                    except Exception as e:
                        logger.error(f"Fehler bei Benachrichtigung: {username}: {e}", exc_info=True)
                    entry["remove"] = True
                    changed = True

        new_data = [entry for entry in data if not entry.get("remove")]
        if changed:
            save_data(new_data)
            logger.info("Absence data updated after role removals or corrections.")

    bot.check_dates_loop = check_dates

    statuses = [
        "Zählt die Panzer, die du verloren hast…",
        "Verteidigt den Punkt mit Sarkasmus",
        "Matchmaking sabotieren seit 2012",
        "Campen in Spawn seit der Steinzeit",
        "Glaubt immer noch an Teamwork",
        "Berechne nächstes Matchmaking-Desaster…",
        "Analyziere: 87% der Spieler weinen im Stillen",
        "Folgt Minotaur LP für wahre Skills 🧠🔥",
        "Gajin hasst dich!"
    ]

    @tasks.loop(seconds=86400)
    async def change_status():
        status = random.choice(statuses)
        await bot.change_presence(activity=discord.CustomActivity(name=status))
        logger.info(f"Changed status to: {status}")

    bot.change_status_loop = change_status
