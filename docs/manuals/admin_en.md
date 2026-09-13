# Admin Manual — AI TeamTalk Bot

> Version: v0.3.2 — version 3 of the bot, with the current systems enabled.

This manual covers admin-only commands. Admins can also use every command from the [user manual](user_en.md). Only users configured as admins (via `admin_usernames` in `config.ini`, or the admin list) can use the commands below — anyone else who tries gets an "unauthorized" notice.

## Bot control
| Command | What it does |
|---|---|
| `lock` | Locks the bot — it starts ignoring all non-admin commands. |
| `block <command>` | Blocks a specific command for everyone. |
| `unblock <command>` | Unblocks a blocked command. |
| `rs` | Restarts the bot. |
| `q` | Shuts the bot down completely. |

## AI configuration
| Command | What it does |
|---|---|
| `gapi <key>` | Sets the Groq API key. |
| `list_groq_models` / `lgm` | Lists available Groq models. |
| `set_groq_model <model>` / `sgm <model>` | Sets the active model (e.g. `openai/gpt-oss-120b`). |
| `instruct <instructions>` | Sets the AI's permanent behavior instructions. |
| `setwelcomeinstruction <instructions>` | Sets the instructions for the AI-generated welcome message. |
| `tg_groq_pm` | Toggles AI in PMs. |
| `tg_groq_chan` | Toggles AI in the channel. |
| `tgmmode` | Toggles welcome message mode (fixed template vs. AI-generated). |
| `tg_context_history` | Toggles conversation context memory. |
| `set_context_retention <minutes>` | Sets how long context history is kept. |

## Language system
| Command | What it does |
|---|---|
| `set_language <pt_BR\|en>` | Sets the language the bot replies in (affects chat and the web panel). Accepts variants like "pt", "português", "en-US", "english". |

## Translator
| Command | What it does |
|---|---|
| `tg_translator` | Toggles translator mode. When on, **any plain message** (no command) gets translated instead of chatted with. |
| `set_translate_lang <language>` | Sets the translation target language (e.g. "english", "spanish"). |

## Task scheduler
| Command | What it does |
|---|---|
| `addtask <maintenance\|restart\|shutdown\|disconnect> <HH:MM>` | Schedules a recurring daily task at the given time (24h). |
| `deltask <id>` | Removes a scheduled task by ID. |
| `listtasks` | Lists all scheduled tasks. |

> Scheduled tasks are saved to `config.ini` automatically and survive bot restarts. Each task type has its own notify sound: `maintenance`→`notify1.wav`, `restart`→`notify2.wav`, `shutdown`→`notify3.wav`, `disconnect`→`notify4.wav`.

## Moderation & word filter
| Command | What it does |
|---|---|
| `addword <word>` | Adds a word to the filter. |
| `delword <word>` | Removes a word from the filter. |
| `tfilter` | Toggles the word filter. |
| `kick <nickname>` | Kicks a user from the bot's current channel. |
| `ban <nickname>` | Bans a user from the server. |
| `unban <username>` | Unbans a user. |

> The filter warns a user for each detected bad word; after **3 warnings**, the bot tries to auto-kick them (if it has permission).

## User & channel management
| Command | What it does |
|---|---|
| `listusers [channel path]` | Lists users in a channel (or the current one, if unspecified). |
| `listchannels` | Lists all channels on the server. |
| `move <nickname> <channel path>` | Moves a user to another channel. |
| `admins` | Lists configured admins and who's online. |
| `jc <channel path>[\|password]` | Makes the bot join another channel. |

## Communication
| Command | What it does |
|---|---|
| `ct <message>` | Sends a message to the bot's current channel. |
| `bm <message>` | Sends a broadcast message to the whole server. |
| `jcl` | Toggles join/leave announcements. |
| `tg_chanmsg` | Toggles the bot's ability to send channel messages. |
| `tg_broadcast` | Toggles the bot's ability to send broadcasts. |

## Debugging
| Command | What it does |
|---|---|
| `tg_debug_logging` | Toggles debug logging (writes more detail to `bot.log`). |

## Sound system

See [`docs/SOUNDS.md`](../SOUNDS.md) for the full table of every sound and when it plays (sleep/wake, scheduler, translator, web panel).

## Web Panel & "Server Manager"

The web panel (`web_ui.py`) has its own configurable host/port, under the `[WebUI]` section of `config.ini` (`host` and `port`). This can be set from the initial setup screen. **Changing host/port requires restarting the `web_ui.py` process** to take effect — the server doesn't rebind on its own while running.

## What's still missing (roadmap)

- **Auto-updater** (checking GitHub for new versions) — intentionally postponed until the bot is more stable.
