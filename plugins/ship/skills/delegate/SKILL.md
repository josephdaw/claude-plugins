---
name: delegate
description: Delegate one or more GitHub issues to workers: brief each, make a worktree, and launch a local subagent, a cloud session, or a paste-ready prompt. The orchestrator's entry point. Use when asked to delegate, hand off, or farm out issues.
argument-hint: <issue ...> [--model sonnet|haiku] [--mode local|cloud|paste] [--yes]
allowed-tools: Bash(gh:*), Bash(git:*), Bash(scripts/new-worktree.sh:*), Bash(ls:*), Bash(test:*), Bash(realpath:*), Agent, Read, Grep, Glob, AskUserQuestion
---

Delegate each issue in `$ARGUMENTS` to its own worker. You coordinate. You
never enter a worktree and never write code.

Flags: `--model` forces the worker model for every issue. Without it,
delegate picks per issue (step 2a) and says so. `--mode` picks the launch
(default local). `--yes` skips the confirmation and treats a flagged issue
as skipped rather than asking.

## 1. Read the Harness section

From the repo's CLAUDE.md: default branch, worktree script, ci gate, merge
policy. Missing: stop and say to run `/ship:adopt`.

## 2. Brief every issue

Run `/ship:brief` for each. Collect the flags.

### 2a. Pick the worker model

Per issue, unless `--model` was given:

- `haiku` when the issue is labelled `docs`, `chore`, or `mechanical`, or
  its scope is a rename, a copy change, a config value, a dependency bump,
  or moving code without changing it, and the acceptance names no
  behaviour a test would have to prove.
- `sonnet` otherwise.

The reviewer is the check on the worker, so this is a cost dial. When in
doubt, sonnet. Show the pick in the Model column of the table and explain
any haiku pick in one clause, so a wrong rule gets corrected rather than
overridden each time.

Then show one table:

```
| Issue | Title | Branch | Model | Flags |
```

Ask once, batched, how to handle flagged rows (brief anyway, research only,
skip). Then confirm the whole list once. With `--yes`, skip flagged rows
and go.

## 3. One worktree per issue

`git pull` in the primary checkout first. Then, per issue, the Harness
worktree script with the branch name, or
`git worktree add <layout-root>/<type>-<slug> -b <type>/<slug> <default>`
followed by the repo's install step. If the path exists, refuse and
report; do not reuse. Put the resolved absolute path into the brief.

## 4. Launch

`local`: one `Agent` call per issue, in the same message so they run in
parallel. `subagent_type: ship:worker`, `model` from `--model`. The prompt
is the full brief text followed by:
"Follow /ship:ship-issue. Work only in the worktree above. Report the PR
URL in the shape ship-issue specifies."
Do not use the Agent tool's own worktree isolation; the worktree already
exists at the path in the brief.

`cloud`: print, per issue, the same prompt in a fenced block for the user
to start a cloud session with. The cloud session installs this plugin from
the repo's `.claude/settings.json`, so the prompt needs no extra setup. Note
the worktree section does not apply there: the cloud session has its own
checkout, so replace it with "Branch: <name> off <default>".

`paste`: print, per issue, the worktree path on its own line and the prompt
in a fenced block, for a terminal session the user opens in that path.

## 5. Report

```
### #<n> <title>
Worker: local <model> (running; why haiku, if haiku) | cloud prompt above | paste prompt above
Worktree: <path>
Branch: <name>
```

When local workers report back, run `/ship:land <pr>` for each PR. Do not
wait for all to finish before landing the first.

If the repo keeps a roadmap or planning file, you update it after merge.
Workers never touch it.
