## v0.3.0.1 — Voice and YouTube download fixes

- Integrated voice system with TeamTalk audio capture, Groq Whisper transcription, and Edge TTS responses.
- Multilingual wake phrase activation with a 3-second inactivity session.
- `appear.wav` and `disappear.wav` are used for activation and deactivation.
- Files downloaded by `/dl` now use the video title as the MP3 filename, with Windows-invalid filename sanitization.

# Changelog — AI TeamTalk Bot

## v0.3.0.0 — Major update and version 3 consolidation

### New
- The **v0.2.x line has been discontinued and archived**. Active development now follows the **v0.3.x** line.
- Consolidated the bot's current systems into version 3.
- Expanded YouTube with pause, resume, forward, backward, next, previous, playlists, and playback queue support.
- Added the `/dl` command, which downloads only the video currently playing and accepts no URL or search argument.
- Audio download uses `yt-dlp.exe`, with MP3 conversion at 320 kbps / 48 kHz through `ffmpeg.exe`.
- The downloaded file is sent through TeamTalk, with channel and PM behavior handled as defined by the bot.
- Prepared the `tools/` directory for the external YouTube executables.
- Updated the manuals and documentation to match **v0.3.0.0**.

### Version note
v0.3.0.0 is a development-line transition, not merely another patch in the 0.2.x series. The 0.2.x versions remain in the historical changelog for reference and are no longer the active development line.
## v0.2.0.7 — Expanded YouTube

- Playback pause and resume controls.
- Forward and backward seeking by seconds.
- Playback queue with next/previous and automatic advancement.
- Playlist loading.
- 320 kbps/48 kHz MP3 download and channel upload through TeamTalk.
- YouTube uses external yt-dlp.exe and ffmpeg.exe from `tools/`.
- TeamTalk media API support prepared for pause and seek controls.

## v0.2.0.6 — Second auto-updater stage

### New
- Added safe installation preparation after downloading the Release package.
- The package is extracted outside the application directory before installation.
- Automatic installation runs through a separate helper process so the running application can finish before its files are replaced.
- The current application directory is kept as a backup during the swap.
- User data files (`config.ini`, `.env`, `site.db`, and log files) are preserved during the update.
- The installed executable name is kept stable regardless of the executable name inside the downloaded package.
- Installation can only be started by a PyInstaller-compiled application.
- Unsafe paths inside the ZIP are rejected during extraction.
### Limitation
- Automatic rollback after an unsuccessful startup will be implemented in the next stage.

## v0.2.0.5 — First auto-updater stage

### New
- Added automatic checks for new versions published through GitHub Releases.
- Versions are identified by Git tags using the `vX.Y.Z.W` format.
- The updater checks on connection and then every 15 minutes.
- When a new version is found, the bot plays `update_found.wav` and asks in the channel and by global broadcast whether it should be downloaded.
- Confirmation accepts `Y` or `N` and is restricted to configured administrators.
- The complete Release package is downloaded and its SHA-256 digest is validated when GitHub provides one.
- While downloading, `updating.wav` is repeated continuously in the channel until completion.
- The downloaded package is validated and extracted to prepare the next updater stage.

### Note
- Replacing files of the running application, restarting, and automatic rollback are reserved for the next updater stage.

## v0.2.0.4 — Waiting timer and sound reminder adjustment

### Fixes
- Fixed the inactivity timer so `message.wav` plays on every 20-minute cycle while the bot waits for activity.
- The waiting period now correctly counts 30 cycles of 20 minutes (10 hours).
- After the 30 cycles are completed, the bot remains in the sleeping state and plays `sleep.wav`.
- Kept the existing message/mention wake-up system and `wake_up.wav` behavior untouched.

## v0.2.0.3 — Mention system adjustment

### Fixes
- Fixed the mention system so it applies only to free-form AI conversations.
- Translator mode now processes ordinary channel messages without requiring the bot nickname to be mentioned.
- The configured nickname remains the trigger for free-form AI interactions.

## v0.2.0.2 — New interaction system

### New Features
- Changed the bot default nickname to `AI Bot`.
- The mention system now automatically uses the nickname configured for the bot, allowing custom names such as `AI Bot`, `Gerenciamento Bot`, or `Bot Manager`.
- Added the `ddev` command, displaying program information, the current version, and the developer.
- Added a mention system for AI interactions in ordinary channel messages.
- The bot now ignores ordinary channel messages when its nickname is not mentioned, reducing unwanted replies and spam.
- Messages directed to the bot can use `Hello <nickname>, <message>` or `<nickname> <message>`.
- The nickname used in the mention is removed from the text before AI processing.

## v0.2.0.1 — Stability Patch

### Fixes
- Fixed WebUI authentication session handling so the login is actually permanent.
- Increased the WebUI permanent session lifetime to 30 days, refreshed while the user remains active.
- Fixed the issue where configuration loading and saving stopped working after a few minutes and required a new login.

## v0.2.0.0 — Alpha

### New Features and Improvements
- Added new account registration through the WebUI.
- Added the **Register new account** button to the login screen.
- Added the `program_started.wav` startup sound.
- Improved bot start, stop, and restart control.
- Added automatic bot recovery after unexpected termination.
- Improved application configuration and controller organization.
- Prepared the architecture for future updates and the voice system.
- Separated the WebUI/controller from the TeamTalk bot process.

## v0.3.0.0 — Planned

### In Development
- Update system.
- Voice system.

> This file will be updated with every new project release.
