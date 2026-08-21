# Google Drive & Docs

Google Drive and Docs integration for Sinas with per-user OAuth. The `gdrive/librarian` agent finds and reads documents, creates docs from templates, edits them safely via `replaceAllText`, organizes folders, and manages sharing.

## What's inside

| Resource | Name | Purpose |
|---|---|---|
| Connector | `gdrive/drive-api` | Drive v3: search, metadata, Docs→markdown export, copy, folders, rename/trash, permissions, revisions, comments (10 operations) |
| Connector | `gdrive/docs-api` | Docs v1: structured read, create, batchUpdate editing (3 operations) |
| Skill | `gdrive/search-syntax` | The Drive `q` query language + recipes |
| Skill | `gdrive/docs-editing` | batchUpdate patterns: template-fill, append, index pitfalls |
| Agent | `gdrive/librarian` | Find/read/summarize, template-based doc creation, edits, sharing |

## Prerequisites

Same Google Cloud setup as the other Google packages: enable the **Google Drive API** and **Google Docs API**, add scope `https://www.googleapis.com/auth/drive` to the consent screen, reuse the Web-application OAuth credentials (redirect URI `https://<your-sinas-domain>/auth/connectors/oauth/callback`).

| Variable | Type | Value |
|---|---|---|
| `GDRIVE_CLIENT_ID` | text | OAuth client ID (same as the other Google packages is fine) |
| `GDRIVE_CLIENT_SECRET` | secret | OAuth client secret (package-scoped name, same value is fine) |

Each user clicks **Connect** on either connector in the console (both share the credentials; each needs its own connect — one consent covers the shared scope).

## Design choices worth knowing

- **Read docs as markdown.** `export-file` with `mimeType=text/markdown` (`responseMapping: text`) is the reading path — the Docs structured body is 10-50× larger and only needed for index-based edits.
- **Template-first editing.** The agent's default write path is copy-a-template + `replaceAllText` — robust against the Docs API's index-shifting footgun. The `docs-editing` skill encodes the highest-index-first rule for when index edits are unavoidable.
- **Sharing is guarded** in the agent prompt (explicit confirmation; `type: anyone` only on verbatim request) since `share-file` sends notification emails.
- **No binary upload/PDF export** yet: multipart upload doesn't fit the connector model and binary responses need more than text mapping — both queued behind the platform's connector-execute-for-functions API.

## Example prompts

- *"Find the latest partnership agreement draft and summarize the termination clause"*
- *"Create a new client folder for Acme and an onboarding doc from our template, filling in their details"*
- *"Who has access to the Q3 budget sheet?"*
- *"Append today's meeting notes to the running 1:1 doc"*
