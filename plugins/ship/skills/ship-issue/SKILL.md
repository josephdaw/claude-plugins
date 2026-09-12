---
name: ship-issue
description: Ship one GitHub issue end to end as a single PR, from brief or issue number to an open pull request. The worker's playbook. Use when asked to implement, ship, or fix an issue.
argument-hint: <issue-number>
---

You are shipping issue #$ARGUMENTS in this repo as one PR. Shipped means the
PR exists. Invoking this skill is standing authorisation for every step,
including opening the PR. Stop only for a genuine blocker: an unresolved
design choice, a spec bigger than one PR, or a failing gate you cannot fix.
Never stop short of the PR out of caution.

## Setup

1. Read the repo's CLAUDE.md front to back. It wins over this file. Find
   its `## Harness` section and note the ci gate, the default branch, and
   the worktree script. If CLAUDE.md or the Harness section is missing,
   stop and report: the repo has not been set up for delegation.
2. Reply first with a block titled `Rulebook read` listing: the ci gate
   command, the commit format, any do-not-touch paths, and one convention
   from CLAUDE.md that will shape this issue. This proves the read.
3. If you were given a brief, it is the spec. Otherwise `gh issue view $ARGUMENTS`
   and `gh issue view $ARGUMENTS --comments`. The latest comment titled
   "Decisions taken" or "Spec addendum" beats the body.
4. Confirm the issue carries the `ready` label. If not, stop and report.
5. Follow `Refs`, `Closes`, `Blocked by`, `Depends on` links for context.
6. If you are not already in the worktree the brief names: from the primary
   checkout, `git pull`, then run the Harness worktree script, or
   `git worktree add ../<type>-<slug> -b <type>/<slug> <default branch>`
   and install dependencies there. Never check out a branch in the primary
   checkout. Every later command uses the worktree's absolute path.

## Decide before coding

7. The spec offers options or leaves a call open: stop and report. Do not
   pick.
8. The spec is bigger than one PR (model plus API plus UI plus migration in
   a non-trivial way, or unrelated concerns bundled): stop and reply with a
   numbered split, one seam per line. Wait.
9. Something in the spec cannot be proven by code: say so in the PR body
   under "Not verified" and list exactly what needs a hand check. Never
   claim a manual check you did not do.

## Implement

10. Match existing patterns. `rg` for similar code first. Read the most
    recent merged PRs touching the same files:
    `git log --merges --oneline -10 -- <path>` then `gh pr view <n>`. They
    are the current convention, including ones CLAUDE.md has not caught up
    with.
11. Test first. Write the failing test that names the behaviour, run it,
    watch it fail, then write the least code that passes. Name tests after
    behaviour a person can observe, not after a function. If you are
    changing untested code, write the characterisation test first.
12. Docs are part of the change: CLAUDE.md maps, conventions, ADRs, or
    whatever surface the repo names.
13. Keep to the issue. A "while I am here" cleanup goes in a note in the PR
    body, not in the diff.

## Verify

14. `git fetch origin <default>` and `git rebase origin/<default>`. Resolve
    conflicts. Do this before the first push.
15. Run the ci gate from the Harness section. It must pass. Paste the tail
    of a failure rather than describing it.

## Ship

16. Commit in Conventional Commits form, `<type>(<scope>): <description>`.
    Match the trailer style of `git log -5`.
17. Push with `-u`. Open the PR with `gh pr create`. Title in Conventional
    Commits form. Write the body in the PR description format `ship:commit-format`
    defines: it is also the squash commit body, so keep to that shape.
18. Report in this shape:

```
PR: <url>
Branch: <name>
Worktree: <path>
Gate: <command> passed | failed (output below)
Not verified: <list or "nothing">
```

Leave the worktree in place. The orchestrator removes it after merge.

When in doubt: CLAUDE.md, then the latest spec comment, then the issue
body, then recent merged PRs. If those disagree, stop and ask.
