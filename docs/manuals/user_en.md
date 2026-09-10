# User Manual — AI TeamTalk Bot

> Version: v0.3.0.1 — version 3 of the bot, with the current systems enabled.

This manual is for anyone using the bot on the TeamTalk server. You don't need to be an admin for anything listed here.

## Talking to the bot (no command needed)

You **don't need to type any command** to chat with the bot. Just send a normal message:

- **In PM:** any message you send privately becomes a question for the AI.
- **In the channel:** any message without a `/` in front also becomes a question for the AI — unless the bot is "asleep" (see the **Sleep mode** section below), in which case you need to mention its nickname.

The reply always comes back the same way you sent it (PM replies in PM, channel replies in the channel — never both at once).

## Sleep mode

If nobody interacts with the bot for **20 minutes**, it "falls asleep." While asleep:

- During free-form AI chat, it **ignores** messages that do not mention its nickname.
- Translator mode does not require a nickname mention to process ordinary messages.
- Mentioning its nickname wakes it up immediately, and that same message is processed normally.
- Every 20 minutes it goes without anyone interacting, it plays a reminder sound. After **30 reminders (10 hours)**, it gives up and stays "awake" on its own, but still requires a mention until someone actually interacts.

## Coexisting with other bots

If the server has other bots (e.g. a music bot), this bot **automatically ignores**:
- Known commands belonging to other bots (`/p`, `/pause`, `/resume`, `/stop`, `/next`, `/prev`, `/sf`, `/sb`, `/seek`, `/l`, `/v`, `/mute`, `/unmute`, `/r`, `/join`, `/leave`, `/playlist`, `/sunucu`, `/status`, `/adminhelp`)
- Any message sent by a user whose nickname ends in "bot" (assumed to be another bot, not a person)

## Available commands

**PM** commands work without a `/` in front. In the **channel**, all commands need the `/` in front (except where noted).

### Info & utilities
| Command | What it does |
|---|---|
| `h` | Shows the command list (this help). |
| `ping` | Checks if the bot is responding. |
| `info` | Shows bot and server status. |
| `whoami` | Shows your TeamTalk user info. |
| `rights` | Shows the bot's permissions on the server. |
| `cn <new nickname>` | Changes the bot's nickname. |
| `cs <new status>` | Changes the bot's status message. |

### Artificial Intelligence (Groq)
| Command | What it does |
|---|---|
| *(free message)* | Talks directly to the AI, no command needed. |
| `c <question>` | Asks the AI something via PM. |
| `/c <question>` | Asks the AI something in the channel. |
| `ch` / `/ch` | Starts a new AI chat (clears conversation history). |
| `cl` / `/cl` | Clears the current conversation history without "restarting" the chat. |
| `n` / `/n` | Ends the current chat. |

### YouTube
| Command | What it does |
|---|---|
| `yt <search or link>` / `/yt` | Searches YouTube (or uses a direct link) and plays the audio in the channel. |
| `ytstop` / `/ytstop` | Stops current playback. |

> YouTube only plays one audio at a time — requesting a new song automatically stops the current one.

| Command | What it does |
|---|---|

> You can also just ask for this in free chat, like "tell me a quote" or "what events are today?" — the AI understands and fetches this info on its own.

### Polls
| Command | What it does |
|---|---|
| `poll "Question" "Option A" "Option B" ...` | Creates a new poll. |
| `vote <id> <option number>` | Votes in an active poll. |
| `results <id>` | Shows a poll's results. |

## Language

The bot replies in **Brazilian Portuguese by default**. An admin can switch it to English with the `set_language` command. The web control panel follows the same configured language.

### Voice

The bot can listen to user audio, recognize wake phrases in supported languages, transcribe with Whisper through Groq, and answer using Edge TTS. The session ends after 3 seconds without new speech.
