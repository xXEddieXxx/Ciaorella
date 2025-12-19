# Absence Manager Discord Bot

Installation (Invite Link): https://discord.com/oauth2/authorize?client_id=1379890220547178587

Discord bot for **absence management** – featuring role automation, logging, and intuitive button/Slash-Command controls.

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
- `/set_language` – changes the language of the bot (de, en currently supported)

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


<a href="https://www.buymeacoffee.com/xEddie" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
