---
name: land
description: Take an open PR to merged (or to a human's queue): wait for CI, run the reviewer, route fixes back to a worker, then merge or hand over under the repo's merge policy, and clean up the worktree. Use after a worker reports a PR.
argument-hint: <pr-number> [pr-number ...] [--rounds N] [--review self|fork]
allowed-tools: Bash(gh:*), Bash(git:*), Agent, SendMessage, Read, Grep, Glob
---

Land each PR in `$ARGUMENTS`. Run independent PRs in parallel. `--rounds`
caps fix rounds; default 2. `--review` forces where the review runs; by
default land decides per PR (step 2).

Read the repo's CLAUDE.md `## Harness` section first for merge policy,
default branch, and ci gate. Missing: stop and say to run `/ship:adopt`.

## Per PR

1. CI. `gh pr checks <n> --watch`. If CI fails, skip to the fix round
   with the failing job's output as the finding. Do not run the reviewer
   on a red PR; it wastes an opus call on something the worker can see.

2. Review. One checklist, `/ship:review-pr`, two places to run it:
   - `self`: you follow the checklist here, in your own context. Cheap
     when the diff is small and your context is already warm.
   - `fork`: launch the `ship:reviewer` agent (Agent tool, subagent_type
     `ship:reviewer`) with "Follow /ship:review-pr for PR <n>". Fresh
     context on opus, so it does not share the blind spots of the session
     that briefed the work.
   Default `fork`. Choose `self` only when all of these hold: under about
   150 changed lines (`gh pr diff <n> --stat`), no file under an auth,
   permission, proxy, schema, migration, payment, or payroll path, and no
   new route or external call. Say which you chose and why in the report.
   `--review` overrides. Either way the result is a VERDICT line.

3. Fix round, when the verdict is CHANGES or CI is red, while rounds
   remain:
   - If the worker that opened the PR is still reachable (a subagent from
     this session), `SendMessage` it: "Review posted on PR <n>. Address
     every blocking finding, rerun the ci gate, push, and report."
   - Otherwise launch a fresh `ship:worker` (Agent tool, subagent_type
     `ship:worker`) with: the worktree path and branch from the PR, the
     review comment text, and the same instruction. It works in the
     existing worktree, never a new one.
   - When it reports, go back to step 1. Count the round.
   - Rounds exhausted with CHANGES still standing: stop, report the last
     review, and leave the PR open. Do not merge.

4. Land, when the verdict is APPROVE and CI is green:
   - merge policy `auto`: `gh pr merge <n> --squash --delete-branch`. The
     squash subject must be the PR title; confirm it is in Conventional
     Commits form before merging, since the release tooling reads it.
     Then from the primary checkout `git pull`, remove the worktree
     (`git worktree remove <path>`, then `git branch -d` if it survives),
     and confirm the linked issue closed (`gh issue view N --json state`).
     If it did not, close it with a comment naming the PR.
   - merge policy `human`: post a comment "Ready for human review. CI green,
     ship:reviewer approved, see review above." Do not merge. Leave the
     worktree. Report the URL for the person to pick up.

## Report

One block per PR:

```
PR <n>: merged | awaiting human | blocked after <k> rounds
Issue: #N closed | still open (why)
Review: APPROVE | CHANGES, <blocking count> blocking, by self | fork (why)
Worktree: removed | kept at <path>
```

Then one line naming anything the reviewer marked "should fix" that was
left, so it can become an issue rather than be forgotten.

Never merge on a red CI, a CHANGES verdict, or a `human` policy. Never
force-push. Never delete a worktree with uncommitted changes; report it
instead.
