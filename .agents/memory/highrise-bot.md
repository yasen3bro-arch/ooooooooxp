---
name: Highrise bot project
description: Imported Python Highrise bot in highrise-bot/, run as a plain workflow; known bug patterns and fixes.
---

## Setup
- Bot code lives in top-level `highrise-bot/` (not a registered artifact — Highrise bots don't fit the artifact system, so it's just a `configureWorkflow` running `python3.10 run.py`).
- Requires Python 3.10 exactly (`highrise-bot-sdk` pins `<3.11`).
- Secrets: `HIGHRISE_BOT_TOKEN` (required to connect), `GEMINI_API_KEY` (optional, only needed for the AI chat/assistant modules — bot runs fine without it, just logs a warning).
- Never hardcode the bot token/room id as a fallback in source — the original imported repo had a leaked token in `run.py`'s ImportError fallback branch; always read from env vars.

## Recurring bug pattern: caller/definition signature drift
This codebase has several spots where `main.py` (MyBot) calls a manager method with a name/signature that doesn't match the manager's actual definition — these fail silently into a caught exception and log an error, so features look "broken" with no user-visible symptom besides "it doesn't work":
- `on_user_join` called `responses_manager.get_welcome_response(user)` but the real method is `get_welcome_message(username, user_type, visit_info=None)`.
- `on_user_leave` called `get_farewell_message(user)` (1 arg) but the real signature is `get_farewell_message(username, user_type)`, and it never called `user_manager.remove_user_from_room(user)` at all (stale users never cleaned from `self.users`).
**Why:** these mismatches only surface in workflow logs (`❌ خطأ في معالجة دخول/مغادرة ...`), not in the room chat, so "welcome/farewell doesn't work" reports require checking logs around join/leave events, not just command logs.
**How to apply:** when a feature "doesn't work" with no error visible to the room, check workflow logs for a caught-and-swallowed exception around the relevant `on_*` handler in `main.py` before assuming game logic (permissions, command routing) is the cause.

## Recurring bug pattern: short exact-match Arabic commands
Commands matched via `message.lower() in [...]` exact equality (e.g. `"كف"`, `"وقّف"`) are fragile — Arabic mobile keyboards often inject invisible marks (ZWJ/ZWNJ/RLM/ALM: `\u200b\u200c\u200d\u200e\u200f\u061c\ufeff`) or stray whitespace that silently break exact equality while longer `.startswith()` commands are less affected.
**Why:** users report a specific short command "doesn't work" even though the code path is logically correct — isolated unit testing shows correct behavior, so the break is in the untrimmed/unnormalized raw message from the SDK.
**How to apply:** normalize incoming chat text (strip invisible unicode marks + whitespace) once at the top of the central command dispatcher (`CommandsHandler.handle_command`) rather than patching each exact-match list individually.
