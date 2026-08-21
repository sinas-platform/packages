# Sinas Packages

Official packages maintained by the Sinas team. Each package is a self-contained YAML file (`kind: SinasPackage`) that can be installed on any Sinas instance.

## Installation

### Via the console

Go to **Packages** > **Install** and paste or upload the package YAML.

### Via the API

```bash
curl -X POST https://your-instance/api/v1/packages/install \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg yaml "$(cat packages/sinas-package-author/package.yaml)" '{yaml: $yaml}')"
```

### Via an agent

If your agent has `packageManagement` in its `systemTools`, it can install packages directly:

```
Install the sinas/package-author package
```

## Available packages

| Package | Description |
|---|---|
| [sinas-package-author](packages/sinas-package-author/) | Skill + reference agent for authoring Sinas packages. Gives an agent the ability to draft, validate, preview, and install packages. |
| [ddf-powerpoint](packages/ddf-powerpoint/) | Create PowerPoint presentations from DDF YAML. Includes validator, compiler, and the full DDF specification as a skill. |
| [jira](packages/jira/) | Jira Cloud integration: Platform + Agile API connectors, JQL/ADF skills, a general assistant, and an hours-tracker agent for worklogs. |
| [google-calendar](packages/google-calendar/) | Google Calendar with per-user OAuth: Calendar v3 connector, event-format skill, and a scheduling agent. |
| [gmail](packages/gmail/) | Gmail with per-user OAuth: search/triage/labels/drafts connector, query + MIME skills, and an inbox assistant. |
| [google-drive-docs](packages/google-drive-docs/) | Drive & Docs with per-user OAuth: search and markdown export, template-based doc creation and editing, librarian agent. |
| [slack](packages/slack/) | Slack Web API via bot token: post/thread/summarize/DM, mrkdwn skill, assistant agent, and inbound events (mentions/DMs → threaded agent replies). |
| [telegram](packages/telegram/) | Telegram Bot API: notifications, formatted reports, and fully declarative inbound chat (message the bot → agent replies, per-chat memory). |

## Package structure

Each package lives in its own directory under `packages/`:

```
packages/
  my-package/
    package.yaml     # The installable package (kind: SinasPackage)
    README.md        # Documentation
```

## Contributing

Packages should follow the Sinas Package schema. Key constraints:

- Packages **cannot** create roles, users, LLM providers, or database connections (these are infrastructure-level)
- All resources created by a package are tagged with `managed_by: pkg:<name>` for clean uninstall
- Use `kind: SinasPackage` (not `SinasConfig`)

## License

AGPL-3.0
