---
name: adopt
description: Set a repo up for the ship plugin: write the marketplace and plugin entries into .claude/settings.json, add a cloud SessionStart hook that installs the plugin, and add the Harness section to CLAUDE.md. Use when a repo has no Harness section, when ship skills are missing in a cloud session, or when delegate, brief, or land say to run it.
argument-hint: [--merge-policy auto|human] [--no-cloud-hook]
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

## 2. Cloud SessionStart hook

Skip this step with `--no-cloud-hook`.

Cloud sessions (claude.ai/code) read the project settings above but do
not install a plugin from an external marketplace source, so the ship
skills are missing there until something installs them. A SessionStart
hook that only runs in cloud does it.

If `.claude/hooks/session-start.sh` does not exist, create it, executable:

```bash
#!/bin/bash
#
# SessionStart hook for Claude Code on the web. Exits at once elsewhere.
# Cloud sessions read .claude/settings.json but do not install a plugin
# from an external marketplace source, so install ship here.
# See: https://code.claude.com/docs/en/discover-plugins.md
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

if command -v claude >/dev/null 2>&1; then
  claude plugin marketplace add josephdaw/claude-plugins --scope user >/dev/null 2>&1 \
    && echo "session-start: josephdaw marketplace ready" \
    || echo "session-start: marketplace add failed or already present, continuing" >&2
  claude plugin install ship@josephdaw --scope user -y >/dev/null 2>&1 \
    && echo "session-start: ship plugin ready" \
    || echo "session-start: ship plugin install failed or already present, continuing" >&2
else
  echo "session-start: claude CLI not on PATH, skipping ship plugin install" >&2
fi
```

If the script already exists, add the plugin block after its cloud guard
and leave the rest alone. Then merge a SessionStart entry into
`.claude/settings.json`, keeping any hooks already there:

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh" } ] }
    ]
  }
}
```

Repo-specific setup belongs in the same script after the plugin block:
a Node version the container lacks, a dependency install, services the
tests need. Look at the repo's CLAUDE.md for what the ci gate needs and
add only that. Check `.gitignore` does not exclude `.claude/hooks/`.

## 3. Detect

- default branch: `git symbolic-ref refs/remotes/origin/HEAD`, else main.
- worktree script: `scripts/new-worktree.sh` if present, else none.
- ci gate: from package.json scripts (lint, typecheck, test, build joined
  with `&&`), a Makefile `check` target, `pyproject` (ruff, mypy, pytest),
  or whatever CLAUDE.md already names. Show what you found.
- merge policy: from `--merge-policy`, else ask one question: is this repo
  in production or relied on by anyone? Yes means `human`, no means `auto`.
  Recommend `human` when unsure.

## 4. Write the Harness section

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

## 5. Report

Show the diff of every file touched. Do not commit; the user commits.
