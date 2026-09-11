# User Manual — Ai Bot (TeamTalk)

> Bot version: **v0.3.2** — version 3 of the bot, with the current systems enabled.

This manual covers every command available to **any user** on the server. For admin-only commands, see `MANUAL_ADMIN_en.md`.

## How commands work

- **Via PM (private message)**: type the command **without a slash**. Ex: `c hi, how are you?`
- **In channel**: type the command **with a `/` in front**. Ex: `/c hi, how are you?`
- Not every PM command is available in channel — the ones that are get a 🔊 mark below.

## Free-form AI chat (no command needed)

You don't need to type `c` every time. Just send a plain message (no `/` in front, in channel) and the bot will reply using AI — like a normal conversation.

> ⚠️ If the bot is **asleep** (see below), it ignores everything until someone mentions its nickname in the message.

## Sleep system

If nobody interacts with the bot for **20 minutes**, it "falls asleep" (plays a sound to indicate it) and starts **ignoring every message**, unless you mention its nickname anywhere in the text — that wakes it up and it replies normally again. If it goes 10 hours with nobody talking to it, it gives up trying to get attention and just stays "awake and quiet" until someone interacts.

## Basic commands

| Command | What it does |
|---|---|
| `h` 🔊 | Shows the command list (this help). |
| `ping` | Checks if the bot is responding. |
| `info` | Shows bot status and server info. |
| `whoami` | Shows your user info. |
| `rights` | Shows the bot's permissions on the server. |
| `cn <new_nick>` | Changes the bot's nickname. |
| `cs <new_status>` | Changes the bot's status message. |

## Artificial Intelligence (Groq)

| Command | What it does |
|---|---|
| `c <question>` 🔊 | Asks the AI something. In channel, it replies only in channel; in PM, only in PM (never both). |
| `ch` 🔊 | Starts a new chat, **clearing** the previous conversation history. |
| `cl` 🔊 | Clears the current chat history without leaving the conversation. |
| `n` 🔊 | Ends the current chat. |

## YouTube

| Comando | O que faz |
|---|---|
| `yt <busca ou link>` / `/yt <busca ou link>` | Pesquisa ou abre um vídeo e inicia a reprodução. |
| `ytstop` / `/ytstop` | Para a reprodução e limpa a fila. |
| `ytpause` / `/ytpause` | Pausa. |
| `ytresume` / `/ytresume` | Continua. |
| `ytforward [segundos]` / `/ytforward [segundos]` | Avança o tempo; padrão 10 segundos. |
| `ytback [segundos]` / `/ytback [segundos]` | Retrocede o tempo; padrão 10 segundos. |
| `ytnext` / `/ytnext` | Próximo vídeo. |
| `ytprev` / `/ytprev` | Vídeo anterior. |
| `ytplaylist <link>` / `/ytplaylist <link>` | Carrega uma playlist na fila. |
| `ytclear` / `/ytclear` | Limpa a fila. |
| `dl` / `/dl` | Baixa **o vídeo que está tocando atualmente**; não recebe URL ou busca. |

O `/dl` baixa o áudio com `yt-dlp.exe`, converte para MP3 **320 kbps / 48 kHz** com `ffmpeg.exe` e envia o arquivo pelo TeamTalk.

## Polls

| Command | What it does |
|---|---|
| `poll "Question" "Option A" "Option B" ...` 🔊 | Creates a new poll. |
| `vote <poll_id> <option_number>` 🔊 | Votes in an active poll. |
| `results <poll_id>` 🔊 | Shows a poll's results. |

## Language

The bot's reply language (including this manual) matches whatever the admin configured. Check with `info` if you're not sure which one is set.

---
*Manual generated for Ai Bot — v0.3.2.0

## Voice

The voice system was removed in this version to keep the core lighter and more stable.
