# sinas-package-author

Skill + reference agent for authoring Sinas packages. Gives an agent the ability to draft, validate, preview, and install packages on behalf of the user.

## What's included

| Resource | Type | Description |
|---|---|---|
| `sinas/package-author` | Skill | Knowledge doc covering the SinasPackage schema, authoring workflow, conventions, and pitfalls |
| `sinas/package-author` | Agent | Reference agent with `packageManagement` + `configIntrospection` enabled and the skill preloaded |

## Requirements

The agent needs a user with these permissions:
- `sinas.config.validate:all` — for validating package YAML
- `sinas.packages.install:all` — for previewing and installing packages
- `sinas.packages.read:own` — for listing and exporting packages

## Usage

After installing, chat with the `sinas/package-author` agent:

```
Create a package that adds a search query over my products table
```

The agent will:
1. Ask clarifying questions if needed
2. Draft the YAML
3. Validate it (fix errors automatically)
4. Show you a preview of what would be created
5. Ask for confirmation before installing

## Customization

The skill and agent are independent — you can:
- Add the skill to your own agent via `enabledSkills: [{skill: sinas/package-author, preload: true}]`
- Modify the reference agent's system prompt, model, or tool wiring after installation
- Add a readwrite collection (e.g. `sinas/packages`) for file-backed drafting
