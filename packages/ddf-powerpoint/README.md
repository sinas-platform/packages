# ddf-powerpoint

Create PowerPoint presentations from DDF (Declarative Document Format) YAML using the [declarativedocs](https://github.com/declarativedocs/compiler-py) compiler.

## What's included

| Resource | Type | Description |
|---|---|---|
| `ddf/presentations` | Collection | Storage for DDF YAML source files and compiled .pptx output |
| `ddf/validate_ddf` | Function | Validates DDF YAML against the official schema (v0.1.0) with bounds checking |
| `ddf/compile_pptx` | Function | Compiles DDF YAML to a PowerPoint file |
| `ddf/presentation-author` | Skill | Full DDF specification — teaches an agent how to write valid DDF YAML |

## Dependencies

- `sinas` >= 0.1.8 (Python SDK with `update_existing` support)
- `declarativedocs` 0.1.1 (DDF compiler)
- `jsonschema` (schema validation)

## Usage

This package provides capabilities, not an agent. Add the skill and functions to any agent:

```yaml
enabledSkills:
  - skill: ddf/presentation-author
    preload: true
enabledFunctions:
  - ddf/validate_ddf
  - ddf/compile_pptx
enabledCollections:
  - collection: ddf/presentations
    access: readwrite
```

Then ask the agent to create a presentation:

```
Create a 5-slide pitch deck for our Series A fundraise
```

The agent will:
1. Draft DDF YAML using the specification from the skill
2. Write it to the `ddf/presentations` collection
3. Validate against the schema (with bounds checking)
4. Compile to .pptx
5. The compiled file is available in the collection for download

## Workflow

1. **Write** — Agent creates DDF YAML, saves to `ddf/presentations`
2. **Validate** — `validate_ddf(filename)` checks schema + element bounds
3. **Iterate** — Agent uses `edit_file` for surgical fixes based on validation errors
4. **Compile** — `compile_pptx(filename)` produces the .pptx in the same collection
5. **Download** — User downloads from the collection browser or via file URL

## DDF Format

DDF is a YAML-based format where every slide is a list of positioned elements:

```yaml
presentation:
  layout: "16x9"
  theme:
    colors:
      primary: "1E2761"
      accent: "FF6B35"
    fonts:
      heading: "Arial Black"
      body: "Calibri"
  slides:
    - elements:
        - type: text
          x: 0.5
          y: 0.3
          w: 9
          h: 1.2
          text: "Title Here"
          font: $heading
          size: 36
          color: $primary
          bold: true
```

Supported element types: `text`, `shape`, `image`, `chart`, `table`, `group`, `icon`.
