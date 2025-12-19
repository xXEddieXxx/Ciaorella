# app/localization.py
from __future__ import annotations

from typing import Any, Mapping
from config import get_guild_config

SUPPORTED_LANGUAGES: dict[str, str] = {
    "de": "Deutsch",
    "en": "English",
}

LOCALES: dict[str, dict[str, Any]] = {
    "de": {
        "common": {
            "not_set": "Nicht gesetzt",
            "assign_verb": "zuweisen",
            "remove_verb": "entfernen",
        },
        "cmd": {
            "set_channel": {"desc": "Setzt den Kanal für Abwesenheitsnachrichten."},
            "set_role": {"desc": "Setzt die Rolle für abwesende Mitglieder."},
            "set_logging_channel": {"desc": "Setzt den Kanal für Abwesenheits-Logs."},
            "show_config": {"desc": "Zeigt die aktuelle Bot-Konfiguration für diesen Server."},
            "show_absent_users": {"desc": "Zeigt alle derzeit abwesenden Benutzer und deren geplantes Rückkehrdatum."},
            "set_language": {"desc": "Setzt die Sprache des Bots für diesen Server."},
        },
        "errors": {
            "role_modify": "Fehler: Kann Rolle `{role}` nicht {action}.",
            "send_absence_manager_failed": "❌ Fehler beim Senden der Nachricht in {channel}. Bitte prüfe die Berechtigungen.",
        },
        "absence": {
            "set_ok": "✅ **Abwesenheit eingetragen!**\nBis **{date}**.",
            "end_ok": "✅ **Abwesenheit beendet!**",
            "invalid_date": "⚠️ **Ungültiges Datum!**\nBitte verwende das Format `TT.MM.JJJJ`.",
            "no_active": "Keine aktive Abwesenheit.",
            "no_active_hint": "ℹ️ **Keine aktive Abwesenheit**\nTrage zuerst ein Startdatum ein.",
            "extend_ok": "✅ **Abwesenheit verlängert!**\nNeues Rückkehrdatum: **{date}**.",
        },
        "ui": {
            "manager_title": "📅 Abwesenheitsmanager",
            "manager_desc": (
                "### Verwalte deine Abwesenheit im Server\n\n"
                "▫️ Abwesenheit für 2 oder 4 Wochen eintragen\n"
                "▫️ Individuelle Rückkehrdaten festlegen\n"
                "▫️ Automatische Benachrichtigungen erhalten\n"
                "▫️ Deine Abwesenheit jederzeit beenden\n\n"
                "**Du erhältst die Abwesenheitsrolle, solange du als abwesend markiert bist.**"
            ),
            "manager_footer": "Verwende die Buttons unten um deine Abwesenheit zu verwalten",
            "btn_2w": "2 Wochen",
            "btn_4w": "4 Wochen",
            "btn_custom_date": "Individuelles Datum",
            "btn_end": "Abwesenheit beenden",
            "btn_extend_2w": "+2 Wochen",
            "btn_extend_4w": "+4 Wochen",
            "btn_extend_custom": "Individuelles Datum",
            "modal_set_title": "Abwesenheit eintragen",
            "modal_extend_title": "Abwesenheit verlängern",
            "input_return_label": "Rückkehrdatum",
            "input_return_new_label": "Neues Rückkehrdatum",
            "input_date_placeholder": "TT.MM.JJJJ (z.B. 31.12.2024)",
        },
        "admin": {
            "language_set": "✅ **Sprache gesetzt!**\nBotsprache für diesen Server ist jetzt **{language}**.",
            "language_set_no_channel": "ℹ️ Hinweis: Es ist kein Abwesenheitskanal gesetzt, daher wurde kein Embed aktualisiert.",
            "channel_already_set": "⚠️ Der Kanal {channel} ist bereits als Abwesenheitskanal gesetzt.",
            "channel_updated": "✅ **Kanal aktualisiert!**\nDie Abwesenheitsnachricht wurde nach {channel} verschoben.",
            "role_set": "✅ **Rolle gesetzt!**\nAbwesenheitsrolle wurde auf `{role}` aktualisiert.",
            "logging_channel_set": "✅ **Logging-Kanal gesetzt!**\nAlle Abwesenheitsereignisse werden jetzt in {channel} geloggt.",
            "config_title": "⚙️ Bot-Konfiguration",
            "config_desc": "**Aktuelle Einstellungen für diesen Server**",
            "config_channel": "Kanal für Nachrichten",
            "config_role": "Abwesenheitsrolle",
            "config_logging": "Logging-Kanal",
            "config_footer": "Verwende /set_channel, /set_role, /set_logging_channel und /set_language zum Ändern.",
            "absent_users_none": "✅ Es sind derzeit keine Benutzer als abwesend markiert.",
            "absent_users_title": "📋 Aktuell Abwesende Mitglieder",
            "absent_users_desc": "Hier ist eine Liste der derzeit abwesenden Mitglieder und deren Rückkehrdatum.",
            "absent_users_entry": "Rückkehrdatum: **{date}**\n{relative}",
            "absent_users_invalid_date": "Ungültiges Datum gespeichert: `{date}`",
            "absent_users_none_in_server": "✅ Es sind derzeit keine abwesenden Benutzer im Server.",
        },
        "log": {
            "absence_set": "📋 {user} hat sich als abwesend eingetragen bis **{date}**.",
            "absence_ended": "✅ {user} hat die Abwesenheit beendet.",
            "absence_extended_until": "🕒 {user} hat seine Abwesenheit verlängert bis **{date}**.",
            "absence_extended_by_days": "🕒 {user} hat seine Abwesenheit um {days} Tage verlängert bis **{date}**.",
            "entry_deleted_role_removed": "🧹 In **{guild}**: {user} hat Rolle **{role}** verloren – Eintrag gelöscht.",
            "entry_deleted_role_missing": "🧹 In **{guild}**: {user} hat Rolle **{role}** nicht mehr – Eintrag gelöscht.",
            "entry_deleted_user_left": "🧹 In **{guild}**: User `{username}` (ID: {user_id}) ist nicht mehr im Server – Eintrag gelöscht.",
            "entry_deleted_role_not_found": "🧹 In **{guild}**: Abwesenheitsrolle `{role_name}` existiert nicht – Eintrag für {user} gelöscht.",
        },
        "dm": {
            "return_day_reached": (
                "## ⏰ Rückkehrtag erreicht in **{guild}**\n"
                "Deine Abwesenheit auf **{guild}** endet heute (am {date})!\n\n"
                "Möchtest du sie verlängern?"
            ),
            "absence_expired_role_removed": (
                "## ✅ Abwesenheit beendet in **{guild}**\n"
                "Deine Abwesenheit ist abgelaufen ({date}).\n"
                "Rolle **{role}** wurde automatisch entfernt."
            ),
            "absence_entry_deleted_role_removed": (
                "## ✅ Abwesenheit beendet in **{guild}**\n"
                "Deine Abwesenheitsrolle **{role}** wurde entfernt.\n"
                "Der Abwesenheits-Eintrag wurde daher automatisch gelöscht."
            ),
        },
    },
    "en": {
        "common": {
            "not_set": "Not set",
            "assign_verb": "assign",
            "remove_verb": "remove",
        },
        "cmd": {
            "set_channel": {"desc": "Sets the channel for absence messages."},
            "set_role": {"desc": "Sets the role for absent members."},
            "set_logging_channel": {"desc": "Sets the channel for absence logs."},
            "show_config": {"desc": "Shows the current bot configuration for this server."},
            "show_absent_users": {"desc": "Shows all currently absent users and their planned return date."},
            "set_language": {"desc": "Sets the bot language for this server."},
        },
        "errors": {
            "role_modify": "Error: Cannot {action} role `{role}`.",
            "send_absence_manager_failed": "❌ Failed to send the message in {channel}. Please check permissions.",
        },
        "absence": {
            "set_ok": "✅ **Absence recorded!**\nUntil **{date}**.",
            "end_ok": "✅ **Absence ended!**",
            "invalid_date": "⚠️ **Invalid date!**\nPlease use the format `DD.MM.YYYY`.",
            "no_active": "No active absence.",
            "no_active_hint": "ℹ️ **No active absence**\nPlease set an absence first.",
            "extend_ok": "✅ **Absence extended!**\nNew return date: **{date}**.",
        },
        "ui": {
            "manager_title": "📅 Absence Manager",
            "manager_desc": (
                "### Manage your absence on this server\n\n"
                "▫️ Set absence for 2 or 4 weeks\n"
                "▫️ Set a custom return date\n"
                "▫️ Receive automatic notifications\n"
                "▫️ End your absence anytime\n\n"
                "**You will keep the absence role while you are marked as absent.**"
            ),
            "manager_footer": "Use the buttons below to manage your absence",
            "btn_2w": "2 weeks",
            "btn_4w": "4 weeks",
            "btn_custom_date": "Custom date",
            "btn_end": "End absence",
            "btn_extend_2w": "+2 weeks",
            "btn_extend_4w": "+4 weeks",
            "btn_extend_custom": "Custom date",
            "modal_set_title": "Set absence",
            "modal_extend_title": "Extend absence",
            "input_return_label": "Return date",
            "input_return_new_label": "New return date",
            "input_date_placeholder": "DD.MM.YYYY (e.g. 31.12.2024)",
        },
        "admin": {
            "language_set": "✅ **Language set!**\nServer language is now **{language}**.",
            "language_set_no_channel": "ℹ️ Note: No absence channel is configured, so no embed was refreshed.",
            "channel_already_set": "⚠️ Channel {channel} is already configured as the absence channel.",
            "channel_updated": "✅ **Channel updated!**\nThe absence message was moved to {channel}.",
            "role_set": "✅ **Role set!**\nAbsence role updated to `{role}`.",
            "logging_channel_set": "✅ **Logging channel set!**\nAll absence events will now be logged in {channel}.",
            "config_title": "⚙️ Bot Configuration",
            "config_desc": "**Current settings for this server**",
            "config_channel": "Channel for messages",
            "config_role": "Absence role",
            "config_logging": "Logging channel",
            "config_footer": "Use /set_channel, /set_role, /set_logging_channel and /set_language to change settings.",
            "absent_users_none": "✅ There are currently no users marked as absent.",
            "absent_users_title": "📋 Currently Absent Members",
            "absent_users_desc": "Here is a list of members currently marked as absent and their return date.",
            "absent_users_entry": "Return date: **{date}**\n{relative}",
            "absent_users_invalid_date": "Invalid date stored: `{date}`",
            "absent_users_none_in_server": "✅ There are currently no absent users on this server.",
        },
        "log": {
            "absence_set": "📋 {user} recorded an absence until **{date}**.",
            "absence_ended": "✅ {user} ended their absence.",
            "absence_extended_until": "🕒 {user} extended their absence until **{date}**.",
            "absence_extended_by_days": "🕒 {user} extended their absence by {days} days until **{date}**.",
            "entry_deleted_role_removed": "🧹 In **{guild}**: {user} lost role **{role}** – entry deleted.",
            "entry_deleted_role_missing": "🧹 In **{guild}**: {user} no longer has role **{role}** – entry deleted.",
            "entry_deleted_user_left": "🧹 In **{guild}**: User `{username}` (ID: {user_id}) is no longer on the server – entry deleted.",
            "entry_deleted_role_not_found": "🧹 In **{guild}**: Absence role `{role_name}` does not exist – entry for {user} deleted.",
        },
        "dm": {
            "return_day_reached": (
                "## ⏰ Return day reached in **{guild}**\n"
                "Your absence on **{guild}** ends today ({date}).\n\n"
                "Would you like to extend it?"
            ),
            "absence_expired_role_removed": (
                "## ✅ Absence ended in **{guild}**\n"
                "Your absence expired ({date}).\n"
                "Role **{role}** was removed automatically."
            ),
            "absence_entry_deleted_role_removed": (
                "## ✅ Absence ended in **{guild}**\n"
                "Your absence role **{role}** was removed.\n"
                "The absence entry was deleted automatically."
            ),
        },
    },
}


def _deep_get(d: Mapping[str, Any], key: str) -> Any:
    cur: Any = d
    for part in key.split("."):
        if not isinstance(cur, Mapping) or part not in cur:
            return None
        cur = cur[part]
    return cur


def t(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in LOCALES else "de"
    text = _deep_get(LOCALES[lang], key)
    if not isinstance(text, str):
        text = _deep_get(LOCALES["de"], key)
    if not isinstance(text, str):
        return key
    try:
        return text.format(**kwargs)
    except Exception:
        return text


def tg(guild_id: int, key: str, **kwargs) -> str:
    lang = get_guild_config(guild_id).get("language", "de")
    return t(lang, key, **kwargs)
