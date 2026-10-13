# Way of working

A preloadable skill that makes a Sinas agent work like Claude Code, plus an exemplar agent wired for the whole loop.

**Installs:**

- **Skill `way-of-working/workbench-loop`.** How to work in the chat's workbench:
  - deliverables are workbench files;
  - facts are verified with code;
  - content moves by reference (`$workbench` paths), not pasted;
  - collections are checked out and promoted back;
  - questions go to the user only when blocked;
  - long runs go to the background, and the agent waits to be woken.
- **Agent `way-of-working/assistant`.** It has the skill preloaded and the workbench, code execution, `ask_user`, artifacts and background tools switched on. Reads and edits inside the chat's workbench run unattended; promoting to a collection, deleting, and writing or editing collection files ask for approval first.

**Requires** a Sinas with the workbench, tool approvals and background tools: the dev line after 0.4 (`ghcr.io/sinas-platform/sinas/backend:dev`). On an older Sinas the install preview reports what is missing.

**Variables:** none.

## Use it

Install it from the console (**Packages** → **Install**) or the API, then chat with `way-of-working/assistant`. To give your own agent the same way of working, copy two things from `package.yaml`: the `enabledSkills` entry with `preload: true`, and the `toolApprovals` block.

The skill teaches the agent the deliveries that wake it: `[background job …]`, `[wakeup …]`, `[watch …]` and `[mcp task …]` are events to act on, not the user speaking.
