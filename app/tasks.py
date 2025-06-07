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
      guild = bot.get_guild(entry["guild_id"])
      if not guild:
        continue

      role_name = get_guild_config(guild.id).get("role_name", DEFAULT_ROLE_NAME)
      role = get_role(guild, role_name)
      member = await get_member(guild, entry["user_id"])
      username = entry.get("username", "Unbekannt")
      user_date = entry.get("date")
      notified = entry.get("notified")

      if role and role not in member.roles:
        await member.send(
          f"## ✅ Abwesenheit beendet in **{guild.name}**\n"
          f"Die Rolle **{role.name}** wurde manuell entfernt.\n"
          f"Dein Abwesenheitsstatus auf **{guild.name}** wurde daher beendet."
        )
        log_ch = guild.get_channel(get_guild_config(guild.id)["logging_channel_id"])
        if log_ch:
          await log_ch.send(
            f"✅ In **{guild.name}**: {member.mention} hatte Rolle **{role.name}** manuell entfernt – Eintrag gelöscht."
          )
        entry["remove"] = True
        changed = True
        continue

      if not notified and user_date == today_str:
        user = bot.get_user(entry["user_id"])
        if user:
          await user.send(
            f"## ⏰ Rückkehrtag erreicht in **{guild.name}**\n"
            f"Deine Abwesenheit auf **{guild.name}** endet heute (am {user_date})!\n\n"
            f"Möchtest du sie verlängern?",
            view=ExtendAbsenceView()
          )
          entry["notified"] = True
          changed = True

      if user_date < yesterday_str and role in member.roles:
        if await modify_role(member, role, add=False):
          await member.send(
            f"## ✅ Abwesenheit beendet in **{guild.name}**\n"
            f"Deine Abwesenheit auf **{guild.name}** ist abgelaufen ({user_date}).\n"
            f"Rolle **{role.name}** wurde automatisch entfernt."
          )
          entry["remove"] = True
          changed = True

    if changed:
      save_data([e for e in data if not e.get("remove")])
      logger.info("Absence data updated after role removals or notifications.")
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
