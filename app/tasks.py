# tasks.py
import random
from datetime import datetime
import discord
from discord import Forbidden, HTTPException
from discord.ext import tasks

from app.localization import tg
from config import (
    load_data, save_data, get_guild_config,
    get_member, get_role, modify_role, DEFAULT_ROLE_NAME
)
from logger import logger
from app.absence import ExtendAbsenceView


def register_tasks(bot):
    @tasks.loop(minutes=1)
    async def check_dates():
        logger.info("Running absence check task...")
        data = load_data()
        today = datetime.now()
        changed = False

        for entry in data:
            guild = bot.get_guild(entry["guild_id"])
            if not guild:
                entry["remove"] = True
                changed = True
                continue

            cfg = get_guild_config(guild.id)
            role_name = cfg.get("role_name", DEFAULT_ROLE_NAME)
            role = get_role(guild, role_name)
            member = await get_member(guild, entry["user_id"])

            log_channel_id = cfg.get("logging_channel_id")
            log_ch = guild.get_channel(log_channel_id) if log_channel_id else None

            if member is None:
                if log_ch:
                    await log_ch.send(
                        tg(
                            guild.id,
                            "log.entry_deleted_user_left",
                            guild=guild.name,
                            username=entry.get("username", "Unknown"),
                            user_id=entry["user_id"],
                        )
                    )
                entry["remove"] = True
                changed = True
                continue

            if role is None:
                if log_ch:
                    await log_ch.send(
                        tg(
                            guild.id,
                            "log.entry_deleted_role_not_found",
                            guild=guild.name,
                            role_name=role_name,
                            user=member.mention,
                        )
                    )
                entry["remove"] = True
                changed = True
                continue

            if role not in member.roles:
                if log_ch:
                    await log_ch.send(
                        tg(
                            guild.id,
                            "log.entry_deleted_role_missing",
                            guild=guild.name,
                            user=member.mention,
                            role=role.name,
                        )
                    )
                try:
                    await member.send(
                        tg(
                            guild.id,
                            "dm.absence_entry_deleted_role_removed",
                            guild=guild.name,
                            role=role.name,
                        )
                    )
                except (Forbidden, HTTPException):
                    pass

                entry["remove"] = True
                changed = True
                continue

            username = entry.get("username", "Unknown")
            user_date_str = entry.get("date")
            notified = entry.get("notified", False)

            try:
                user_date_dt = datetime.strptime(user_date_str, "%d.%m.%Y")
            except Exception:
                logger.error(f"Bad date format for {username}: {user_date_str}")
                continue

            if not notified and user_date_dt.date() == today.date():
                user = bot.get_user(entry["user_id"])
                if user:
                    try:
                        await user.send(
                            tg(
                                guild.id,
                                "dm.return_day_reached",
                                guild=guild.name,
                                date=user_date_str,
                            ),
                            view=ExtendAbsenceView(guild.id)
                        )
                        entry["notified"] = True
                        changed = True
                    except (Forbidden, HTTPException):
                        pass
                continue

            if user_date_dt.date() < today.date() and role in member.roles:
                if await modify_role(member, role, add=False):
                    try:
                        await member.send(
                            tg(
                                guild.id,
                                "dm.absence_expired_role_removed",
                                guild=guild.name,
                                date=user_date_str,
                                role=role.name,
                            )
                        )
                    except (Forbidden, HTTPException):
                        pass
                    entry["remove"] = True
                    changed = True
                continue

        if changed:
            save_data([e for e in data if not e.get("remove")])
            logger.info("Absence data updated after reconciliation/notifications.")

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
