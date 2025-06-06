# Absence Manager Discord Bot

Installation: https://discord.com/oauth2/authorize?client_id=1379890220547178587

A modern Discord bot for **absence management** – featuring role automation, logging, and intuitive button/Slash-Command controls.

![Banner](https://pbs.twimg.com/media/DtFE2_BX4AECJ8a.jpg:large)

---

## Features

- **Absence Panel:**  
  One-click buttons to register for 2 weeks, 4 weeks, custom dates, or end absence.
- **Automatic Role Management:**  
  Members automatically receive/loose the absence role.
- **Logging:**  
  All absence events (registration, extension, cancellation) are logged in a dedicated channel.
- **Automatic Reminders:**  
  Users receive DM notifications when their return date arrives.
- **Slash Commands:**  
  `/set_channel`, `/set_role`, `/set_logging_channel`, `/show_config` for easy configuration.
- **Persistent UI:**  
  The panel remains functional after bot restarts/crashes.
- **Admin-Exclusive Configuration:**  
  Only administrators can modify settings.

---

## Requirements

- Python 3.10+
- [discord.py 2.x](https://discordpy.readthedocs.io/en/stable/)
- Bot must have these permissions:
  - Read Messages & Send Messages
  - Manage Messages (to clean old bot messages)
  - Manage Roles
  - Write access in configured channels

---

## Installation

1. **Clone Repository**
   ```sh
   git clone https://github.com/xXEddieXxx/Ciaorella.git
   cd Ciaorella
      ```
2. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure Bot**
   - Create an application on [Discord Developer Portal](https://discord.com/developers/applications) and invite it to your server.
   - Create an **absence** role (e.g., `Away`).
   - Start the bot once to generate config files (`config/guild_config.json` and `config/dates.json`).

4. **Launch Bot**
   ```sh
   python bot.py
   ```

5. **Set Up in Discord**
   - Set main panel channel:
     ```
     /set_channel <#channel>
     ```
   - Set absence role name:
     ```
     /set_role Abwesend
     ```
   - Set logging channel:
     ```
     /set_logging_channel <#log-channel>
     ```
   - **Done!** The panel will appear automatically in the designated channel.

---

## User Guide

- **Click "2 Weeks", "4 Weeks", or "Custom Date" in the panel**  
  → Your absence will be registered, you'll receive the role, and get auto-notified on return day.
- **Click "End Absence" when returning** 
  → Role removed and status reset.
- **Extend Absence:**  
  When your return date arrives, you'll receive a DM with extension buttons!

---

## Admin Commands

- `/set_channel <#channel>` – Sets the panel's display channel
- `/set_role <Rollenname>` – Sets the absence role name (role must exist)
- `/set_logging_channel <#log-channel>` – Sets logging channel 
- `/show_config` – Shows current server configuration

*Configuration changes require administrator permissions.*

---

## Notes & Tips

- Configurations (`guild_config.json`) are server-specific.
- Absence data (`dates.json`) is stored per server/user.
- **Each server uses unique roles/channels!**
- Bot automatically checks for expired absences and removes roles.
- All logs are sent to your designated logging channel.
- Panels persist through bot restarts.

---

## Troubleshooting

- **Can't assign roles?**  
  Ensure the bot's role position is higher than the absence role with "Manage Roles" permission.
- **Panel not appearing?**  
  Use `/set_channel` and verify channel permissions.
- **No logging?**  
  Set `/set_logging_channel` and confirm bot has write access.

=======================================


# Abwesenheitsmanager Discord Bot

Installation: https://discord.com/oauth2/authorize?client_id=1379890220547178587

Ein moderner Discord-Bot zur **Abwesenheitsverwaltung** für Server – mit Rollenvergabe, Logging, und einfacher Bedienung über Buttons und Slash-Commands.

![Banner](https://pbs.twimg.com/media/DtFE2_BX4AECJ8a.jpg:large)

---

## Features

- **Abwesenheits-Panel:**  
  Ein-Klick-Buttons zum Eintragen für 2 oder 4 Wochen, beliebiges Datum oder „Abwesenheit beenden“.
- **Automatische Rollenverwaltung:**  
  Mitglieder bekommen oder verlieren automatisch die Abwesenheitsrolle.
- **Logging:**  
  Alle Abwesenheits-Ereignisse (Eintragung, Verlängerung, Beendigung) werden im konfigurierten Log-Channel dokumentiert.
- **Automatische Benachrichtigungen:**  
  Nutzer werden per DM erinnert, wenn ihr Rückkehrdatum erreicht ist.
- **Slash-Commands:**  
  `/set_channel`, `/set_role`, `/set_logging_channel`, `/show_config` für einfache Konfiguration.
- **Persistente UI:**  
  Das Panel bleibt auch nach einem Neustart oder Ausfall des Bots aktiv.
- **Nur Admins können Konfigurationen ändern.**

---

## Voraussetzungen

- Python 3.10+
- [discord.py 2.x](https://discordpy.readthedocs.io/en/stable/)
- Bot benötigt folgende Rechte:
  - Nachrichten lesen & senden
  - Nachrichten verwalten (zum Aufräumen alter Bot-Nachrichten)
  - Rollen verwalten
  - In den eingestellten Kanälen schreiben

---

## Installation

1. **Repository klonen**
   ```sh
   git clone https://github.com/xXEddieXxx/Ciaorella.git
   cd Ciaorella
   ```

2. **Abhängigkeiten installieren**
   ```sh
   pip install -r requirements.txt
   ```

3. **Bot konfigurieren**
   - Erstelle auf [Discord Developer Portal](https://discord.com/developers/applications) deine Bot-Anwendung und lade ihn auf deinen Server ein.
   - Lege eine **Abwesenheitsrolle** an (z.B. `Abwesend`).  
   - Starte den Bot einmal, dann werden die Konfig-Dateien angelegt (`config/guild_config.json` und `config/dates.json`).

4. **Starte den Bot**
   ```sh
   python bot.py
   ```

5. **Richte den Bot im Discord ein**
   - Setze den Haupt-Channel fürs Panel:
     ```
     /set_channel <#channel>
     ```
   - Setze den Namen der Abwesenheitsrolle:
     ```
     /set_role Abwesend
     ```
   - Setze den Log-Channel (wo alle Aktionen dokumentiert werden):
     ```
     /set_logging_channel <#log-channel>
     ```
   - **Fertig!** Das Panel wird automatisch im gewünschten Channel angezeigt.

---

## Bedienung für Nutzer

- **Klicke im Panel auf „2 Wochen“, „4 Wochen“ oder „Individuelles Datum“**  
  → Deine Abwesenheit wird bis zum gewählten Tag gespeichert, du bekommst die Rolle und wirst am Rückkehrtag automatisch benachrichtigt.
- **Klicke auf „Abwesenheit beenden“**, wenn du zurück bist  
  → Deine Rolle wird entfernt und dein Status zurückgesetzt.
- **Abwesenheit verlängern:**  
  Wenn dein Rückkehrtag erreicht ist, bekommst du eine private Nachricht mit Buttons zum Verlängern!

---

## Admin-Befehle

- `/set_channel <#channel>` – Setzt den Channel, in dem das Abwesenheits-Panel erscheint  
- `/set_role <Rollenname>` – Setzt den Namen der Abwesenheitsrolle (Rolle muss existieren)  
- `/set_logging_channel <#log-channel>` – Setzt den Channel für Log-Nachrichten  
- `/show_config` – Zeigt die aktuelle Konfiguration für deinen Server an

*Nur Administratoren dürfen die Konfiguration ändern.*

---

## Hinweise & Tipps

- Die Konfiguration (`guild_config.json`) wird pro Server gespeichert.
- Die Abwesenheits-Daten (`dates.json`) werden ebenfalls pro Server und User gespeichert.
- **Jeder Server kann eigene Rollen/Channels setzen!**
- Der Bot prüft regelmäßig, ob Abwesenheitszeiträume abgelaufen sind, und entfernt Rollen automatisch.
- Alle Logs landen im von dir festgelegten Log-Channel.
- Das Panel bleibt auch nach Bot-Restarts sichtbar.

---

## Fehlerbehebung

- **Der Bot kann keine Rolle zuweisen?**  
  Prüfe, ob der Bot die Rolle über seiner eigenen Position in der Rollenliste hat und die Rechte „Rollen verwalten“ besitzt.
- **Das Panel erscheint nicht?**  
  Nutze `/set_channel` und prüfe die Channel-Rechte.
- **Kein Logging?**  
  Setze `/set_logging_channel` und stelle sicher, dass der Bot dort schreiben kann.
