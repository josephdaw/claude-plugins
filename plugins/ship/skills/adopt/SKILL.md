---
name: adopt
description: Set a repo up for the ship plugin: write the marketplace and plugin entries into .claude/settings.json and add the Harness section to CLAUDE.md. Use when a repo has no Harness section or when delegate, brief, or land say to run it.
argument-hint: [--merge-policy auto|human]
allowed-tools: Bash(git:*), Bash(ls:*), Bash(cat:*), Bash(test:*), Read, Write, Edit, Grep, Glob, AskUserQuestion
---

Set the current repo up for `ship`.

## 1. Settings

Merge into `.claude/settings.json` (create it if absent, keep every key
already there):

```json
{
  "extraKnownMarketplaces": {
    "josephdaw": { "source": { "source": "github", "repo": "josephdaw/claude-plugins" } }
  },
  "enabledPlugins": { "ship@josephdaw": true }
}
```

If `.gitignore` ignores `.claude/` wholesale, narrow it to
`.claude/settings.local.json` and `.claude/worktrees/` so the shared file
is committed.

## 2. Detect

- default branch: `git symbolic-ref refs/remotes/origin/HEAD`, else main.
- worktree script: `scripts/new-worktree.sh` if present, else none.
- ci gate: from package.json scripts (lint, typecheck, test, build joined
  with `&&`), a Makefile `check` target, `pyproject` (ruff, mypy, pytest),
  or whatever CLAUDE.md already names. Show what you found.
- merge policy: from `--merge-policy`, else ask one question: is this repo
  in production or relied on by anyone? Yes means `human`, no means `auto`.
  Recommend `human` when unsure.

## 3. Write the Harness section

Append to CLAUDE.md, or replace an existing `## Harness` section:

```
## Harness

Read by the ship plugin (josephdaw/claude-plugins). Change a value here,
not in the plugin.

| Setting | Value |
|---------|-------|
| merge policy | auto |
| ci gate | pnpm lint && pnpm typecheck && pnpm test && pnpm build |
| worktree | scripts/new-worktree.sh <branch> |
| default branch | main |

merge policy auto: the orchestrator merges after CI passes and the
reviewer approves. human: a person reviews and merges.
```

Omit the worktree row when there is no script.

## 4. Report

Show the diff of both files. Do not commit; the user commits.
