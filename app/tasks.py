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
    yesterday = today - timedelta(days=1)
    changed = False

    for entry in data:
      guild = bot.get_guild(entry["guild_id"])
      if not guild:
        continue

      role_name = get_guild_config(guild.id).get("role_name", DEFAULT_ROLE_NAME)
      role = get_role(guild, role_name)
      member = await get_member(guild, entry["user_id"])
      username = entry.get("username", "Unbekannt")
      user_date_str = entry.get("date")
      notified = entry.get("notified")

      try:
        user_date_dt = datetime.strptime(user_date_str, "%d.%m.%Y")
      except Exception as e:
        logger.error(f"Bad date format for {username}: {user_date_str}")
        continue

      if not notified and user_date_dt.date() == today.date():
        user = bot.get_user(entry["user_id"])
        if user:
          await user.send(
            f"## ⏰ Rückkehrtag erreicht in **{guild.name}**\n"
            f"Deine Abwesenheit auf **{guild.name}** endet heute (am {user_date_str})!\n\n"
            f"Möchtest du sie verlängern?",
            view=ExtendAbsenceView(guild.id)
          )
          entry["notified"] = True
          changed = True
        continue

      if user_date_dt < yesterday and role and role in member.roles:
        if await modify_role(member, role, add=False):
          await member.send(
            f"## ✅ Abwesenheit beendet in **{guild.name}**\n"
            f"Deine Abwesenheit auf **{guild.name}** ist abgelaufen ({user_date_str}).\n"
            f"Rolle **{role.name}** wurde automatisch entfernt."
          )
          entry["remove"] = True
          changed = True
        continue

      if user_date_dt < yesterday and role and role not in member.roles:
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

    if changed:
      save_data([e for e in data if not e.get("remove")])
      logger.info("Absence data updated after role removals or notifications.")

  statuses = [
      "Zählt die Panzer, die du verloren hast…",
      "Matchmaking sabotieren…",
      "Glaubt immer noch an Teamwork",
      "Berechne nächstes Matchmaking-Desaster…",
      "87% der Spieler weinen im Stillen",
      "Folgt Minotaur LP für wahre Skills 🧠🔥",
      "Gajin hasst dich!",
      "Nur eine gefütterte schnecke ist eine gute schnecke…",
      "Sind die Gegner zu Stark, bist du zu schlecht…"
  ]

  @tasks.loop(seconds=86400)
  async def change_status():
    status = random.choice(statuses)
    await bot.change_presence(activity=discord.CustomActivity(name=status))
    logger.info(f"Changed status to: {status}")

  bot.check_dates_loop = check_dates
  bot.change_status_loop = change_status
