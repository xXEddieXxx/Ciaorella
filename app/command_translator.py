from __future__ import annotations

import discord
from discord import app_commands
from discord.app_commands import locale_str

from localization import t


class TableTranslator(app_commands.Translator):
    async def translate(
        self,
        string: locale_str,
        locale: discord.Locale,
        context: app_commands.TranslationContext,
    ) -> str | None:
        key = string.message

        loc = str(locale)
        if loc.startswith("de"):
            lang = "de"
        elif loc.startswith("en"):
            lang = "en"
        else:
            lang = "de"

        return t(lang, key)
