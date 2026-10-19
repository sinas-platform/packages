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
| [slack](packages/slack/) | ⚠️ Experimental/parked. Slack Web API via bot token incl. inbound events — works, but relies on handler functions until webhook filters/handshake support land. |
| [telegram](packages/telegram/) | Telegram Bot API: notifications, formatted reports, and fully declarative inbound chat (message the bot → agent replies, per-chat memory). |
| [github](packages/github/) | GitHub REST API: issues, PRs with diffs, CI runs, code search, notifications, and a declarative issues/PRs/comments webhook. |
| [way-of-working](packages/way-of-working/) | A preloadable skill that makes an agent work like Claude Code (files in the workbench, verification by code, references instead of pasted content, questions only when blocked), plus an exemplar agent wired for the full loop. Needs the Sinas dev line after 0.4. |

## Package structure

Each package lives in its own directory under `packages/`:

```
packages/
  my-package/
    package.yaml     # The installable package (kind: SinasPackage); the
                     # folder name must equal package.name
    README.md        # Documentation
```

## The index

`index.json` lists every package in this repository: name, version, description, the path of its `package.yaml` and that file's SHA-256, `multiInstance: true` for packages that can be installed more than once, and `requires` for packages that need other packages. Sinas reads a package repository through this one file, so it works from any static host. Regenerate it whenever a package changes:

```bash
pip install pyyaml
python scripts/build_index.py
```

CI fails a change that leaves `index.json` out of date (`--check`).

A package that needs another one declares it in `package.requires`. Sinas installs a missing requirement first, from its active repositories, refuses to uninstall a package others require, and lets the package's resources refer to the required package's resources by `namespace/name`:

```yaml
package:
  name: support-mailbox-triage
  version: "1.0.0"
  requires:
    - name: gmail
      version: ">=0.1,<1"         # optional: a pyproject-style range
      repository: sinas-official  # optional: where to look first
      instance: gmail-support     # optional: which install of a multiInstance package
```

The index copies each requirement (`name`, and `version`, `repository` and `instance` when given) into the package's entry as `requires`, which the Sinas catalog shows. The field is left out for packages without requirements. Installs always read the requirements from the checksummed `package.yaml` itself.

## CI

Every pull request starts Sinas (`ghcr.io/sinas-platform/sinas/backend:dev`) and installs every package with `scripts/check_packages.py`: a preview with dummy values for required variables, an install, and a second install that must change nothing. Some packages get extra checks on what they installed. To run it against your own Sinas:

```bash
SINAS_URL=http://localhost:8000 SINAS_EMAIL=you@example.com SINAS_PASSWORD=... \
  python scripts/check_packages.py [package ...]
```

Run it against a throwaway instance: it installs packages for real.

## Guides

- [GOOGLE-SETUP.md](GOOGLE-SETUP.md) — one-time Google Cloud OAuth setup shared by the Calendar, Gmail and Drive & Docs packages: APIs, consent screen, redirect URI, per-user Connect, troubleshooting.
- [AUTHORING.md](AUTHORING.md) — writing your own packages: connector schema realities, webhook template guarding, pipeline cursor semantics, function runtime constraints, and the testing workflow.

## Contributing

Packages should follow the Sinas Package schema. Key constraints:

- Packages **cannot** create roles, users, LLM providers, or database connections (these are infrastructure-level)
- All resources created by a package are tagged with `managed_by: pkg:<name>` for clean uninstall
- Use `kind: SinasPackage` (not `SinasConfig`)

## License

AGPL-3.0
