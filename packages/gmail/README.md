# Gmail

Gmail integration for Sinas with per-user OAuth. The `gmail/assistant` agent searches and summarizes mail, triages and labels, and prepares reply drafts — which the user reviews and sends in Gmail.

## What's inside

| Resource | Name | Purpose |
|---|---|---|
| Connector | `gmail/gmail-api` | Gmail v1: search, messages/threads, labels, archive/trash, drafts, send, history (13 operations) |
| Skill | `gmail/search-operators` | Gmail query syntax + triage recipes |
| Skill | `gmail/message-format` | MIME payload decoding and RFC 2822 raw-message building |
| Agent | `gmail/assistant` | Inbox triage, summaries, labeling, reply drafts |

## Prerequisites

Same Google Cloud setup as [google-calendar](../google-calendar/): enable the **Gmail API**, add scope `https://www.googleapis.com/auth/gmail.modify` to the consent screen, and reuse the same Web-application OAuth credentials (redirect URI `https://<your-sinas-domain>/auth/connectors/oauth/callback`).

| Variable | Type | Value |
|---|---|---|
| `GMAIL_CLIENT_ID` | text | OAuth client ID (may be identical to the calendar package's) |
| `GMAIL_CLIENT_SECRET` | secret | OAuth client secret (same value is fine; the name is package-scoped so each package manages its own secret lifecycle) |

After install, each user clicks **Connect** on the connector in the console.

## Design choices worth knowing

- **Drafts, not sends.** The assistant is wired to `create-draft` but deliberately *not* to `send-message`. Drafts appear in the user's Gmail ready to send — a human-review step by construction. The `send-message` operation exists on the connector; an admin can create an agent (or extend this one) with it enabled if unattended sending is truly wanted.
- **MIME via code execution.** Gmail's draft/send API takes a base64url-encoded RFC 2822 message. The agent builds it with the `codeExecution` system tool (guided by the `gmail/message-format` skill) — no helper function needed. Once the platform's connector-execute API for functions lands, a `gmail/send_email` convenience function becomes possible.
- **Metadata-first triage.** The agent fetches `format=metadata` + snippet for summaries and only pulls full bodies when needed — keeps token usage sane on busy inboxes.
- **Attachments** are reported by filename/size but not downloaded (base64 payloads would flood the context).

## Example prompts

- *"Anything important in my inbox since yesterday?"*
- *"Summarize the thread with Acme about the renewal"*
- *"Label everything from recruiting@ as Hiring and archive it"*
- *"Draft a polite decline to the sponsorship request"*

## Roadmap

- **Inbound triggers**: real Gmail push needs a GCP Pub/Sub topic (not portable in a package). Planned instead: a polling schedule using `get-profile` + `list-history` with a stored `historyId` cursor, invoking a configurable agent per new message — a natural early consumer of the upcoming syncs/transforms platform work.
