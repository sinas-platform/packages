# Google Calendar

Google Calendar integration for Sinas with per-user OAuth: each user connects their own Google account, and the `gcal/scheduler` agent reads their schedule, finds open slots, and manages events.

## What's inside

| Resource | Name | Purpose |
|---|---|---|
| Connector | `gcal/calendar-api` | Calendar v3: calendars, events CRUD, free/busy, recurring instances (11 operations) |
| Skill | `gcal/event-format` | date vs dateTime, timezones, RRULEs, attendees, free/busy interpretation |
| Agent | `gcal/scheduler` | Schedule review, slot finding, event create/update/move/cancel |

## Prerequisites (Google Cloud, one-time per instance)

1. Create (or reuse) a Google Cloud project and enable the **Google Calendar API**.
2. Configure the **OAuth consent screen** (external or internal; scope `https://www.googleapis.com/auth/calendar`).
3. Create **OAuth credentials** of type *Web application* and add the redirect URI:
   ```
   https://<your-sinas-domain>/auth/connectors/oauth/callback
   ```
   (The redirect host comes from the Sinas `DOMAIN` env var.)

## Install

| Variable | Type | Value |
|---|---|---|
| `GOOGLE_CLIENT_ID` | text | The OAuth client ID (`....apps.googleusercontent.com`) |
| `GOOGLE_CLIENT_SECRET` | secret | The OAuth client secret |

After installing, each user opens the connector in the console and clicks **Connect** — a Google consent popup completes the flow. Tokens are stored per user and refreshed automatically; the connector's `authorizeUrl` bakes in `access_type=offline&prompt=consent` so Google issues a refresh token.

## Example prompts

- *"What does my Thursday look like?"*
- *"Find 45 minutes for me and sam@company.com next week, mornings preferred"*
- *"Book the Friday 10:00 slot — title: Q3 planning, invite Sam"*
- *"Move my 1:1 to next Tuesday same time"*
- *"Set up a weekly standup Mon/Wed/Fri at 9:15"*

## Notes & roadmap

- **Same Google Cloud project, more packages**: the upcoming Gmail and Drive/Docs packages use the same credential setup — you can reuse the client ID/secret and just add their scopes to the consent screen.
- **Push notifications** (`events.watch` channels) are deliberately not included: channels expire and require renewal plumbing. For proactive briefings, add an agent schedule (`scheduleType: agent`) that asks `gcal/scheduler` for a morning summary.
- `sendUpdates` (suppressing invitation emails) is not exposed: it is a query parameter on write endpoints and the connector model maps non-path parameters of a write either all-to-body or all-to-query. Attendees therefore always receive Google's default notifications.
