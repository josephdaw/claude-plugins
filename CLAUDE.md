# claude-plugins

Joe's Claude Code plugin marketplace. It holds one plugin today, `ship`,
which delegates GitHub issues to workers, reviews the PRs, and lands them.
Every repo the factory runs on loads `ship` from here, so a change to a
skill or agent changes how every repo's workers and reviewers behave.

## Tech stack

Markdown skills and agents, plus JSON manifests. No build step and no
dependencies. The `claude` CLI validates the manifests.

## Ownership map

Find the existing owner; do not create a parallel implementation.

| Concern | Owner |
|---------|-------|
| Marketplace listing and plugin versions | `.claude-plugin/marketplace.json` |
| ship manifest and version | `plugins/ship/.claude-plugin/plugin.json` |
| What each ship skill does | `plugins/ship/skills/<name>/SKILL.md` |
| Worker, reviewer, and spec-test agents | `plugins/ship/agents/<name>.md` |
| How to adopt and use ship | `plugins/ship/README.md` |
| Why ship works the way it does | mnemosyne `ops/harness/ship-workflow.md` |

## Rules

- A change to ship bumps its version in both `plugin.json` and
  `marketplace.json`, and the two must match. Minor for `feat`, patch for
  `fix`. Installed copies only update when the version changes.
- A rule lives in one skill. Other skills point to it, they do not
  restate it.
- Skill text is read by agents. Write rules as plain, checkable
  instructions.
- Australian English, plain ASCII, no emojis, no em dashes.
- Conventional commits with a `ship` scope, for example `feat(ship):`.

## How to run it

No build. Validate with:

```
claude plugin validate . && claude plugin validate plugins/ship
```

To try a change before release, point a session at this checkout with
`claude --plugin-dir plugins/ship`.

## Harness

Read by the ship plugin (josephdaw/claude-plugins). Change a value here,
not in the plugin.

| Setting | Value |
|---------|-------|
| merge policy | human |
| ci gate | claude plugin validate . && claude plugin validate plugins/ship |
| default branch | main |

merge policy auto: the orchestrator merges after CI passes and the
reviewer approves. human: a person reviews and merges.
