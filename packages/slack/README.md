# Slack

> ⚠️ **Experimental / parked.** Functional and live-tested, but unlike the other integrations it needs two handler functions (Slack's URL-verification handshake and bot-echo filtering). It is parked until the platform grows declarative webhook filters + handshake support, at which point the functions disappear. Use at your own discretion meanwhile.

Slack integration for Sinas via a bot token: post messages and thread replies, read and summarize channels, DM users, react — plus **inbound events** (requires Sinas ≥ 0.4.0): @mention the bot or DM it, and `slack/assistant` answers in-thread with per-thread conversation memory.

## What's inside

| Resource | Name | Purpose |
|---|---|---|
| Connector | `slack/web-api` | chat.postMessage/update, conversations list/history/replies/join/open, users, reactions, permalinks (11 operations) |
| Skill | `slack/formatting` | mrkdwn (≠ markdown), mentions, threading semantics, `ok:false` error handling |
| Agent | `slack/assistant` | Post, thread-reply, summarize channels/threads, DM; answers inbound mentions/DMs |
| Function | `slack/events_handler` | Fast Events API receiver: challenge echo, bot/loop filtering, enqueue (raw-mode webhook at `slack/events`) |
| Function | `slack/process_event` | Async processor: invokes the assistant per channel+thread, posts the reply back |

## Prerequisites (Slack app, one-time)

1. Create an app at [api.slack.com/apps](https://api.slack.com/apps) (from scratch).
2. **OAuth & Permissions → Bot Token Scopes**: `chat:write`, `channels:read`, `channels:history`, `channels:join`, `groups:read`, `groups:history`, `im:write`, `im:read`, `im:history`, `users:read`, `reactions:write`.
3. **Install to Workspace** and copy the Bot User OAuth Token (`xoxb-...`).
4. Invite the bot to private channels it should read (`/invite @yourbot`); it can join public channels itself.

## Install

| Variable | Type | Value |
|---|---|---|
| `SLACK_BOT_TOKEN` | secret | The `xoxb-...` bot token |

## Example prompts

- *"Summarize what happened in #incidents today"*
- *"Post the release notes to #engineering as a thread under the pinned message"*
- *"DM Sam that the deploy is done"*
- *"React ✅ to the last message in #standup"*

## Enabling inbound events (Slack app config)

1. Install the package (needs Sinas ≥ 0.4.0 for raw-mode webhooks), which creates the webhook at `https://<your-sinas-domain>/webhooks/slack/events`.
2. In the Slack app: **Event Subscriptions → Enable**, set that URL as the Request URL — the handler echoes the `url_verification` challenge and Slack will show *Verified*.
3. Subscribe to bot events: `app_mention`, `message.im`. Reinstall the app if Slack asks.

The handler enqueues processing and returns within Slack's 3-second deadline; `$.event_id` dedup absorbs Slack's retries; bot messages and subtypes are filtered to prevent reply loops. Only @mentions and DMs reach the agent — plain channel chatter does not.

## Known limitations

- **No request-signature verification**: the webhook runtime doesn't expose headers, so `X-Slack-Signature` can't be checked. The endpoint's obscurity plus event filtering is the current mitigation; treat the webhook URL as a secret.
- **No message search**: `search.messages` requires a user token, not a bot token.
- Message deletion is deliberately not exposed.
