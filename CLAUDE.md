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
| The ci gate | `scripts/ci.sh` |
| Version match check | `scripts/check-manifest-versions.py` |
| What each ship skill does | `plugins/ship/skills/<name>/SKILL.md` |
| Worker, reviewer, and spec-test agents | `plugins/ship/agents/<name>.md` |
| The coding rules every repo is held to | `plugins/ship/rules/coding.md` |
| How to adopt and use ship | `plugins/ship/README.md` |
| Why ship works the way it does | mnemosyne `ops/harness/ship-workflow.md` |

## Rules

- A change to ship bumps its version in both `plugin.json` and
  `marketplace.json`. The two must match, and the ci gate fails when they
  do not. Minor for `feat`, patch for `fix`. Installed copies only update
  when the version changes. History before 2026-09-12 does not hold to
  this: 0.3.0 and 0.4.0 shipped while marketplace.json still said 0.2.1.
- A rule lives in one skill. Other skills point to it, they do not
  restate it.
- Skill text is read by agents. Write rules as plain, checkable
  instructions.
- Australian English, plain ASCII, no emojis, no em dashes.
- Conventional commits with a `ship` scope, for example `feat(ship):`.

## How to run it

No build. Validate with:

```
./scripts/ci.sh
```

That validates the marketplace and every plugin manifest, then checks the
versions in the two manifests match.

To try a change before release, point a session at this checkout with
`claude --plugin-dir plugins/ship`.

## Harness

Read by the ship plugin (josephdaw/claude-plugins). Change a value here,
not in the plugin.

| Setting | Value |
|---------|-------|
| merge policy | auto |
| ci gate | ./scripts/ci.sh |
| default branch | main |

merge policy auto: the orchestrator merges after CI passes and the
reviewer approves. human: a person reviews and merges.
