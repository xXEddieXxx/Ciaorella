
# Abwesenheitsmanager Discord Bot

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
