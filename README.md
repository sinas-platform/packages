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
