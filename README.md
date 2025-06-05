# Abwesenheitsmanager Discord Bot

Ein moderner Discord-Bot zur **Abwesenheitsverwaltung** für Server – mit Rollenvergabe, Logging-Funktion und intuitiver Oberfläche.

![Banner](https://pbs.twimg.com/media/DtFE2_BX4AECJ8a.jpg:large)

---

## Features

- **Slash-Commands:** Einfache Verwaltung über `/set_channel`, `/set_role`, `/set_logging_channel`, `/show_config`.
- **Abwesenheits-Panel:** Ein-Klick Buttons für 2 oder 4 Wochen, individuelles Datum und Beenden.
- **Automatische Rollen:** Mitglieder erhalten/verlieren automatisch eine Abwesenheitsrolle.
- **Logging:** Ereignisse (z.B. "Benutzer ist abwesend") werden im festgelegten Log-Kanal dokumentiert.
- **Admin-Steuerung:** Nur Administratoren können Kanäle und Rollen setzen.
- **Persistente UI:** Das Panel bleibt nach Neustart aktiv und aktuell.

---

## Voraussetzungen

- Python 3.10+
- [discord.py 2.x](https://discordpy.readthedocs.io/en/stable/)
- Schreibrechte auf deinem Server für den Bot (inkl. `Manage Roles`, `Read Messages`, `Send Messages`, `Manage Messages`)

---

## Installation

1. **Repository klonen**  
   ```sh
   git clone <dein-repo-url>
   cd <dein-repo-ordner>


pip install -r requirements.txt


python bot.py