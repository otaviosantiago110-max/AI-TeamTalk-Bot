# Admin Manual — Ai Bot (TeamTalk)

> Bot version: **Public Alpha v0.2.0** — still in development, may be unstable.

This manual covers commands exclusive to **admins** (configured via `admin_usernames` in `config.ini`, or registered as Super Admin/Admin in the Web UI). For regular user commands, see `MANUAL_USUARIO_en.md`.

All commands below are used **via PM only** — none of them work in-channel with `/`.

> ⚠️ **Found while writing this manual:** `setwelcomeinstruction` (AI welcome message instructions) is registered in the code as a regular command, not admin-gated. This is likely an oversight — let me know if you'd like it fixed.

## Bot control

| Command | What it does |
|---|---|
| `lock` | Locks the bot: ignores all non-admin commands until unlocked (run `lock` again). |
| `block <command>` | Blocks a specific command for everyone. |
| `unblock <command>` | Unblocks a blocked command. |
| `rs` | Restarts the bot. |
| `q` | Shuts down the bot. |

## Language and AI

| Command | What it does |
|---|---|
| `set_language <pt_BR\|en>` | Sets the language for **all** bot replies (chat and commands). |
| `gapi <key>` | Sets the Groq API key. |
| `list_groq_models` / `lgm` | Lists available Groq models. |
| `set_groq_model <model>` / `sgm <model>` | Sets the active Groq model (default: `openai/gpt-oss-120b`). |
| `instruct <text>` | Sets the permanent AI system instructions (personality, tone, rules). |
| `setwelcomeinstruction <text>` | Sets the instructions for the AI-generated welcome message. |
| `set_context_retention <minutes>` | Sets how long conversation history is kept. |

## Toggles (enable/disable features)

| Command | What it does |
|---|---|
| `jcl` | Toggle join/leave announcements in the channel. |
| `tg_chanmsg` | Toggle the bot's ability to send channel messages. |
| `tg_broadcast` | Toggle the bot's ability to send broadcast messages. |
| `tg_groq_pm` | Toggle AI in PM. |
| `tg_groq_chan` | Toggle AI in channel. |
| `tgmmode` | Toggle between a fixed welcome message template and an AI-generated one. |
| `tfilter` | Toggle the word filter. |
| `tg_context_history` | Toggle conversation context memory. |
| `tg_debug_logging` | Toggle debug logging (more verbose). |

## Moderation and users

| Command | What it does |
|---|---|
| `addword <word>` | Adds a word to the filter. |
| `delword <word>` | Removes a word from the filter. |
| `listusers [channel_path]` | Lists users in a channel (or the current one, if unspecified). |
| `listchannels` | Lists all channels on the server. |
| `admins` | Lists configured admins and who's currently online. |
| `kick <nickname>` | Kicks a user from the bot's current channel. |
| `ban <nickname>` | Bans a user from the server. |
| `unban <username>` | Removes a user's ban. |
| `move <nickname> <channel_path>` | Moves a user to another channel. |

> The word filter also auto-kicks (if the bot has permission) after **3 warnings** for the same user.

## Channel

| Command | What it does |
|---|---|
| `jc <channel_path>[\|password]` | Makes the bot join another channel. |
| `ct <message>` | Sends a message to the bot's current channel. |
| `bm <message>` | Sends a broadcast message to the whole server. |

## Task scheduler

Schedules **daily recurring** tasks. Tasks are **in-memory only** — they don't survive a bot restart (re-add them after restarting).

| Command | What it does |
|---|---|
| `addtask <maintenance\|restart\|shutdown\|disconnect> <HH:MM>` | Schedules a daily task, 24h time format. |
| `deltask <id>` | Removes a scheduled task. |
| `listtasks` | Lists scheduled tasks. |

Notification sounds: `maintenance`→`notify1.wav`, `restart`→`notify2.wav`, `shutdown`→`notify3.wav`, `disconnect`→`notify4.wav`.

## Translator mode

When enabled, **any plain message** (no command) gets translated instead of chatted with by the AI.

| Command | What it does |
|---|---|
| `tg_translator` | Toggles translator mode (plays `toggle.wav`). |
| `set_translate_lang <language>` | Sets the translation target language (default: English). |

## Sound system (quick reference)

| File | When it plays |
|---|---|
| `critical.wav` | Locally, at startup: Python < 3.12 or a missing dependency. |
| `sleep.wav` | Bot enters sleep mode (20 min of no activity). |
| `message.wav` | Every 20 min while asleep, up to 29 times (reminder). |
| `wake_up.wav` | Bot wakes up (by name mention, or after giving up on reminders). |
| `appear.wav` / `disappear.wav` | Reserved for the future voice system (activation/deactivation). |
| `toggle.wav` | Mode switch (e.g. translator). |
| `notify1-4.wav` | Task scheduler notifications. |
| `update_found.wav` / `updating.wav` | Reserved for the future auto-updater. |
| `startup.wav` | Plays in the browser when opening the web control panel. |

See `docs/SOUNDS.md` for the full design.

## Web UI configuration

In `config.ini`, `[WebUI]` section:
- `host` — address the web panel listens on (default `0.0.0.0`, i.e. all interfaces).
- `port` — web panel port (default `5000`).

> Changing these requires **restarting the `web_ui.py` process** to take effect.

## Known pending work (future versions)

- **Auto-updater**: automatically check/download new versions from GitHub. *(Postponed — still unstable.)*
- **Voice recognition**: spoken wake-word activation, voice commands. *(To be implemented later — the most technically complex piece.)*

---
*Manual generated for Ai Bot — Public Alpha v0.2.0.0
