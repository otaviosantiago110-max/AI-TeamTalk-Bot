# Changelog — AI TeamTalk Bot

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
