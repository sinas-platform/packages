# Jira

Jira Cloud integration for Sinas: two connectors (Platform REST v3 + Agile API), JQL and ADF skills, and two agents — a general assistant and a conversational hours tracker.

## What's inside

| Resource | Name | Purpose |
|---|---|---|
| Connector | `jira/platform-api` | Issues, JQL search, comments, transitions, worklogs, links, projects, users, field metadata (23 operations) |
| Connector | `jira/agile-api` | Boards, sprints, backlog, epics (7 operations) |
| Skill | `jira/jql-guide` | JQL syntax, functions, and recipes (incl. worklog queries) |
| Skill | `jira/adf-guide` | Atlassian Document Format for descriptions/comments |
| Agent | `jira/assistant` | General Jira work: search, create, update, transition, comment, sprint planning |
| Agent | `jira/hours-tracker` | Log and summarize time on issues conversationally |

The two agents demonstrate per-agent operation gating: `hours-tracker` only sees the search/read/worklog slice of the connector, while `assistant` gets the broad set (but no worklog mutations and no issue deletion — there is deliberately no delete-issue operation in the connector).

## Prerequisites

1. A Jira Cloud site, e.g. `https://your-site.atlassian.net`.
2. An API token: create one at [id.atlassian.com → Security → API tokens](https://id.atlassian.com/manage-profile/security/api-tokens).

## Install

Install the package and provide the variables when prompted:

| Variable | Type | Value |
|---|---|---|
| `JIRA_BASE_URL` | text | Your site URL, no trailing slash: `https://your-site.atlassian.net` |
| `JIRA_CREDENTIALS` | secret | `your-email@example.com:your-api-token` (basic auth, colon-separated) |

The secret is stored encrypted; the connector base64-encodes it per request as HTTP basic auth.

### OAuth alternative

Jira Cloud also supports OAuth 2.0 (3LO) via `auth.type: oauth2_authorization_code`. That requires an Atlassian Developer app and routes through `https://api.atlassian.com/ex/jira/{cloudId}` instead of your site URL. The API-token setup above is simpler and per-user tokens are rarely needed for Jira; if you need OAuth, adapt the connector `auth` block accordingly.

## Example prompts

- *"What's on my plate?"* — assistant runs `assignee = currentUser() AND statusCategory != Done`
- *"Create a bug in PROJ: checkout returns 500 when the cart is empty"*
- *"Move PROJ-12 to In Review and assign it to Sam"*
- *"What's left in the current sprint on the Platform board?"*
- *"Log 2.5 hours on PROJ-42 for this morning — API debugging"* (hours-tracker)
- *"How many hours did I log last week, per issue?"* (hours-tracker)

## Inbound events (Sinas ≥ 0.4.0)

The package ships a declarative agent-target webhook at `jira/events` (dedup on `X-Atlassian-Webhook-Identifier`, one conversation per issue key). To activate it, register the URL in Jira: **Settings → System → Webhooks → Create**, URL `https://<your-sinas-domain>/webhooks/jira/events`, select the events you want (issue created/updated, comment created) and optionally a JQL filter — Jira-side filtering is the intended way to scope what the agent sees. Adjust `messageTemplate` / `agentName` on the webhook to route to your own triage agent.

## Roadmap

- **Attachments**: upload/download needs multipart and binary handling — planned as functions in a later version.
- **Worklog bulk export** (`/worklog/updated` + `/worklog/list`): natural pipeline source for hour-report syncs to a database.
