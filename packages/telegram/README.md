# Telegram

Telegram Bot API integration for Sinas: the `telegram/notifier` agent sends formatted messages, edits them, and manages the bot — plus **fully declarative inbound chat** (requires Sinas ≥ 0.4.0): message the bot on Telegram and the agent replies, one conversation per chat, no handler function needed.

## What's inside

| Resource | Name | Purpose |
|---|---|---|
| Connector | `telegram/bot-api` | sendMessage/editMessageText/sendPhoto, chat info, getUpdates polling, webhook management (10 operations) |
| Skill | `telegram/bot-basics` | chat ids, HTML formatting (avoid MarkdownV2), rate limits, webhook vs polling |
| Agent | `telegram/notifier` | Notifications and formatted reports via the bot |

## Prerequisites

1. Create a bot with [@BotFather](https://t.me/BotFather) (`/newbot`) and copy the token.
2. Each recipient must **start a chat with the bot once** (Telegram forbids bots from initiating).

## Install

| Variable | Type | Value |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | text | The `123456:ABC-...` token from BotFather |

⚠️ **Token storage caveat**: Telegram authenticates via the URL path (`api.telegram.org/bot<token>/...`), so the token is substituted into the connector's `baseUrl` at install time and stored in plain connector config — not as an encrypted secret. Anyone with config-read access to the instance can see it. Rotate the token via BotFather if that assumption changes.

## Example prompts

- *"Send me a Telegram message when you're done: chat id 123456789"*
- *"Send the weekly summary to the team group (-1001234567890), nicely formatted"*

## Enabling inbound chat

1. At install, set `TELEGRAM_WEBHOOK_PATH` to something unguessable (e.g. `telegram/updates-x7k2m9pq`) — the path IS the auth, since Telegram's `secret_token` header can't be verified by the webhook runtime.
2. Ask the `notifier` agent to run `set-webhook` with `url: https://<your-sinas-domain>/webhooks/<that path>` — or curl the Bot API yourself.
3. Message the bot on Telegram. Updates dedup on `$.update_id`; each chat gets its own persistent conversation (`sessionKeyTemplate: tg-{{ message.chat.id }}`); bots never see their own messages, so there is no loop risk. `get-webhook-info` shows delivery status and last errors.

## Inbound option B: polling (no public URL needed)

For local/private instances that Telegram can't reach, the package ships a **polling pipeline** (`telegram/poll-inbox` + the `telegram-poll-inbox` schedule, every minute) — same result as the webhook: message the bot, the agent answers, per-chat memory. It polls `getUpdates` on a durable pipeline cursor (`offset`), so nothing is processed twice and nothing is missed (at-least-once with cursor commit only on success).

**Disabled by default** — enable *both* the pipeline and the schedule in the console to turn it on. Do not combine with a registered Telegram webhook: `getUpdates` returns 409 while one is set (`delete-webhook` first). Cost note: one cheap function run per minute; the LLM is only invoked when there are actual messages.

## Roadmap

- Webhook HMAC-equivalent (`secret_token` header verification) — pending platform header support.
