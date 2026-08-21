# GitHub

GitHub integration for Sinas: issues, pull requests, CI runs, code/file access, notifications — plus a fully declarative inbound webhook (issues/PRs/comments → agent, one conversation per issue).

## What's inside

| Resource | Name | Purpose |
|---|---|---|
| Connector | `github/rest-api` | Issues, PRs (incl. per-file diffs), search, file contents, Actions runs/jobs, notifications (16 operations) |
| Skill | `github/search-guide` | Search qualifiers + API conventions (issue/PR duality, pagination, rate limits) |
| Agent | `github/assistant` | Triage, PR summaries, CI failure diagnosis, comments, issue management |
| Webhook | `github/events` | Declarative agent target: `issues`, `issue_comment`, `pull_request` events, dedup on `X-GitHub-Delivery` |

## Install

| Variable | Type | Value |
|---|---|---|
| `GITHUB_TOKEN` | secret | Fine-grained PAT (recommended — scope it to the repos and permissions you need) or classic PAT with `repo` scope |

> Note (Sinas 0.4.0-rc): until the package secret-variable fix lands, pre-create the secret first: `POST /api/v1/secrets {"name": "GITHUB_TOKEN", "value": "...", "visibility": "shared"}` — then install.

## Enabling inbound events

Repo (or org) **Settings → Webhooks → Add webhook**: Payload URL `https://<your-sinas-domain>/webhooks/github/events`, content type **application/json**, select events (issues, issue comments, pull requests). GitHub's initial ping succeeds automatically (no handshake needed); redeliveries are absorbed by dedup on the delivery id. Webhook secret/HMAC is not verified (platform limitation) — treat the URL as private.

## Example prompts

- *"What's waiting on my review?"*
- *"Summarize PR acme/api#482 — what changed and what's risky?"*
- *"Why is CI red on main?"*
- *"File an issue on acme/api: rate limiter returns 500 instead of 429, label it bug"*
- *"Anything in my GitHub notifications since yesterday?"*

## Deliberately not included (v0.1)

- **Merging PRs** — too consequential for an agent default; add `PUT /repos/{o}/{r}/pulls/{n}/merge` to the connector yourself if you want it.
- Branch/commit/release management, PR review submission — candidates for a later version.
- Webhook HMAC verification — pending platform header support.
