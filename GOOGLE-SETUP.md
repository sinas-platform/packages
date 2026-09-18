# Google OAuth Setup

One-time setup to enable the Google integration packages — [google-calendar](packages/google-calendar/), [gmail](packages/gmail/), and [google-drive-docs](packages/google-drive-docs/) — on a Sinas deployment served from a domain.

All three use **per-user OAuth**: an administrator registers one Google Cloud OAuth client on the instance, then each user connects their own Google account and the agents act as that user. Tokens are stored encrypted per user and refreshed automatically.

**One Google Cloud project and one OAuth client can serve all three packages.** Enable the APIs and add the scopes for whichever packages you install.

## Per-package reference

| Package | Google APIs to enable | Scope | Connectors to connect |
|---|---|---|---|
| google-calendar | Google Calendar API | `https://www.googleapis.com/auth/calendar` | `gcal/calendar-api` |
| gmail | Gmail API | `https://www.googleapis.com/auth/gmail.modify` | `gmail/gmail-api` |
| google-drive-docs | Google Drive API + Google Docs API | `https://www.googleapis.com/auth/drive` | `gdrive/drive-api`, `gdrive/docs-api` |

| Package | Install variables |
|---|---|
| google-calendar | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| gmail | `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET` |
| google-drive-docs | `GDRIVE_CLIENT_ID`, `GDRIVE_CLIENT_SECRET` |

Variable names are package-scoped on purpose, so uninstalling one package cannot revoke another's credentials. When one OAuth client serves several packages, paste the **same** client ID and secret into each package's variables.

## Before you start: your redirect URI

Sinas derives the OAuth callback from the `DOMAIN` environment variable:

```
https://<DOMAIN>/auth/connectors/oauth/callback
```

Always HTTPS, no port, no trailing slash — Google matches it character for character. Take `<DOMAIN>` from the deployment's `DOMAIN` variable, not from what you typed in the browser. (With `DOMAIN` unset or set to `localhost`, Sinas falls back to `http://localhost:<backend_port>/auth/connectors/oauth/callback`, which Google accepts for local development.)

In the default deployment the API is served at `https://<DOMAIN>` and the console at `https://<DOMAIN>:51245`. The callback belongs to the API origin — the console port never appears in the redirect URI.

## Step 1 — Create or select a Google Cloud project

At [console.cloud.google.com](https://console.cloud.google.com), use the project dropdown to create a project (or pick an existing one). If your organization uses Google Workspace, create it inside that organization so you can use the **Internal** user type in step 3.

## Step 2 — Enable the APIs

APIs & Services → **Library**. Search for each API your packages need (see the table above) and click **Enable**. Drive and Docs are separate APIs; enabling only one produces 403s from the other.

## Step 3 — Configure the OAuth consent screen

APIs & Services → **OAuth consent screen** (newer consoles: *Google Auth Platform → Branding / Audience*).

**Choose a user type:**

| | Internal | External |
|---|---|---|
| Who can connect | Only users in your Workspace organization | Any Google account you list as a test user (or anyone, once published) |
| Verification | Not required | Required before publishing, for the scopes these packages use |
| Refresh tokens | Do not expire | **Expire after 7 days while in Testing** |
| Requires | Google Workspace | Nothing |

**Internal is strongly preferred for a company deployment** — it avoids Google's verification process and the 7-day token expiry entirely.

Fill in app name, user support email and developer contact. Under **Scopes**, add the scope(s) for your packages (use "Add or Remove Scopes" and paste the scope string). If you chose External, add every person who will connect under **Test users** while the app is in Testing.

## Step 4 — Create the OAuth client

APIs & Services → **Credentials** → Create credentials → **OAuth client ID**.

- **Application type: Web application.** (Not Desktop — the Connect flow is a browser redirect.)
- **Authorized redirect URIs** → Add URI → paste your redirect URI from above. Add one entry per environment that shares this client (staging, production, and `http://localhost:8000/auth/connectors/oauth/callback` for local development).
- Authorized JavaScript origins can stay empty.

Create it, then copy the **Client ID** (`…apps.googleusercontent.com`) and **Client secret** (`GOCSPX-…`). The secret is shown once; treat it like any other production credential.

## Step 5 — Install the package in Sinas

In the console: **Packages → Install**, then paste the package YAML (or install via `POST /api/v1/packages/install` with `{"source": "<yaml>", "variables": {...}}`). Supply the client ID and secret for that package's variables (see the table above). The client secret is stored as an encrypted Sinas secret; the client ID lives in the connector's auth config.

Re-running the install with corrected values updates the connectors in place.

## Step 6 — Each user connects their Google account

In the console: **Connectors → `<connector>` → Connect**. A Google consent popup opens; the user picks their account and grants access, and the panel switches to Connected.

Every user who will use these agents does this once for themselves — tokens are stored per user and per connector. **google-drive-docs has two connectors**, so it needs two clicks (the second consent is usually one click, since the scope is already granted).

Sinas requests offline access with forced consent, so Google returns a refresh token and the platform refreshes access tokens on its own from then on. Users can Disconnect or Reconnect from the same panel.

## Step 7 — Verify

Test a read-only operation from the connector page — for example `list-calendars`, `list-labels`, or `search-files` with `q` = `trashed = false` — or ask the package's agent something harmless:

- *"What's on my calendar tomorrow?"* (`gcal/scheduler`)
- *"Anything unread in my inbox from today?"* (`gmail/assistant`)
- *"Find my most recently modified Google Doc and summarize it."* (`gdrive/librarian`)

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `redirect_uri_mismatch` | The registered URI differs from `https://<DOMAIN>/auth/connectors/oauth/callback` — check for a trailing slash, `http` instead of `https`, a port, `www.`, or a `DOMAIN` value that differs from the URL you browse to. |
| `access_denied` immediately after choosing an account | External + Testing, and that account is not in the Test users list. Add it, or switch to Internal. |
| `invalid_client` | Client ID or secret mismatched — most often the secret was pasted with whitespace, or a client from a different project was used. Reinstall the package with corrected values. |
| Connector works, then fails ~a week later | External + Testing refresh-token expiry. Users click **Reconnect**; switch to Internal (or publish) to stop it recurring. |
| 403 `…API has not been used in project…` | That specific API was never enabled (commonly Docs, when only Drive was enabled). Enable it in step 2. |
| 403 `insufficient authentication scopes` after a package upgrade | The scope list changed; existing tokens predate it. Users must Disconnect and Connect again. |
| Consent popup completes but the connector stays disconnected | Usually a mismatch between the browser origin and `DOMAIN`, so the callback cannot hand the result back to the console. Make sure the console and API are served from the same HTTPS host and that `DOMAIN` matches it. `OAUTH_BIND_BROWSER_SESSION` should stay at its default on HTTPS deployments; it is a local-development workaround only. |
| Drive search returns nothing for files you can see | Shared-drive items need `includeItemsFromAllDrives` and `supportsAllDrives` set to true on the search operation. |

## Publishing and verification (External only)

Sinas requests `drive`, `gmail.modify` and `calendar` — Google classifies the first two as **restricted** scopes. An External app stays limited to its test users until it is verified, which for restricted scopes means a security assessment on top of the usual brand review, and can take weeks. Options, in order of preference:

1. **Internal user type** (Google Workspace) — no verification, no 7-day expiry.
2. **External, Testing** — fine for pilots and small teams; each user reconnects weekly.
3. **External, Published + verified** — only worth it for a product serving accounts outside your organization. You will also need a privacy policy, terms of service, a verified domain, and a demo video of the OAuth flow.

## Narrowing scopes

The packages request broad scopes so every shipped operation works. To tighten them, edit the connector's `auth.scopes` in the package YAML before installing, then drop the operations that need more access:

- `drive.readonly` or `drive.file` instead of `drive` — loses copy/create/update/share operations.
- `gmail.readonly` instead of `gmail.modify` — loses labeling, archiving, trashing and drafts.
- `calendar.readonly` instead of `calendar` — read-only scheduling.

Changing scopes on an installed connector requires every user to Disconnect and Connect again.
