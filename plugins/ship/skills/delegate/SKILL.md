---
name: delegate
description: Delegate one or more GitHub issues to workers: brief each, make a worktree, and launch a local subagent, a cloud session, or a paste-ready prompt. The orchestrator's entry point. Use when asked to delegate, hand off, or farm out issues.
argument-hint: <issue ...> [--model sonnet|haiku] [--test-model opus|fable] [--mode local|cloud|paste] [--yes]
allowed-tools: Bash(gh:*), Bash(git:*), Bash(scripts/new-worktree.sh:*), Bash(ls:*), Bash(test:*), Bash(realpath:*), Agent, Read, Grep, Glob, AskUserQuestion
---

Delegate each issue in `$ARGUMENTS` to its own worker. You coordinate. You
never enter a worktree and never write code.

Flags: `--model` forces the worker model for every issue. Without it,
delegate picks per issue (step 2a) and says so. `--test-model` picks the
model for the spec-test pass (step 3b), default opus. `--mode` picks the launch
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
worktree script with the branch name, or follow `/ship:worktree` with
the branch name and `--yes` defaults (sibling path, copy env files)
followed by the repo's install step. If the path exists, refuse and
report; do not reuse. Put the resolved absolute path into the brief.

## 3b. Spec tests first, on the full tier

Docs-only and runtime-free `chore` issues skip this. Everything else gets a
spec-test pass before any implementation.

Launch the `ship:spec-tests` agent (Agent tool, `subagent_type:
ship:spec-tests`) in the issue's worktree, with `model` from `--test-model`
if given.

On the model: the default is opus, and fable is worth running as a measured
experiment rather than a preference. The argument for it is not that one
writes better tests, it is that opus reviews the PR, so an opus test pass
shares its blind spots. A behaviour neither considers passes the whole
pipeline unchallenged and looks like agreement rather than a gap. A
different model at the two judgement points decorrelates them.

That is a testable claim, so test it: run `--test-model fable` on a run of
full-tier issues and record whether the reviewer finds behaviour the tests
missed, against the same count for opus. Promote or drop it on the number,
not on the reasoning above. It writes the failing tests that
encode the issue's behaviour, proves they fail for the right reason, and
commits them alone.

Two of its outcomes are not "carry on":

- Spec gaps found. It stopped because the issue is wrong or has an unmade
  choice. Do not launch a worker. Fix the issue, or bring the choice to the
  human. An issue that specifies the wrong behaviour will otherwise be
  implemented correctly and reviewed as correct, and the error survives all
  the way to production.
- No red proof. If it could not make the tests fail for the right reason,
  the tests do not test the thing. Send it back before spending a worker.

Pass the test commit SHA and the test file paths into the worker's brief.
The worker may not change those files, and the reviewer checks that.

## 4. Launch

`local`: one `Agent` call per issue, in the same message so they run in
parallel. `subagent_type: ship:worker`, `model` from `--model`. The prompt
is the full brief text followed by:
"Follow /ship:ship-issue. Work only in the worktree above. Report the PR
URL in the shape ship-issue specifies."
Do not use the Agent tool's own worktree isolation; the worktree already
exists at the path in the brief.

Workers run in the background. Never end your turn while one is still
running: a headless session (Talos, `claude -p`) exits the moment you
send a message with no tool call, and every running worker is killed with
its uncommitted work lost. After launching, block on each worker with
TaskOutput (or wait for its completion notification) and keep the turn
open until all have reported. Land PRs as they arrive, between waits.

`cloud`: print, per issue, the same prompt in a fenced block for the user
to start a cloud session with. Cloud reads the repo's `.claude/settings.json`
but does not auto-install an external-source plugin, so the repo's
SessionStart hook must run `claude plugin install ship@josephdaw` (see
utm-platform's `.claude/hooks/session-start.sh`). The prompt itself needs
no extra setup. Note
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
wait for all to finish before landing the first. Do not finish the
turn while any worker is still running.

If the repo keeps a roadmap or planning file, you update it after merge.
Workers never touch it.
