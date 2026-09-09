---
name: brief
description: Turn a GitHub issue (or a freeform task) into a self-contained worker brief, after checking the issue is actually ready to delegate. Use when delegating, or when asked whether an issue is ready.
argument-hint: <issue-number | "task description">
allowed-tools: Bash(gh issue view:*), Bash(gh pr view:*), Bash(git log:*), Read, Grep, Glob
---

Produce one worker brief for `$ARGUMENTS`. The brief must let a worker who
has never seen this chat ship the work from the brief and the repo alone.

## 1. Gather

For an issue number:

- `gh issue view <n> --json number,title,body,labels,url`
- `gh issue view <n> --comments`. A comment titled "Decisions taken",
  "Spec addendum", or "Note" is authoritative over the body where they
  differ. Capture those verbatim, in posting order.
- Follow `Refs #X`, `Closes #Y`, `Blocked by #Z`, `Depends on #Z` far enough
  to know whether a blocker is still open. An open blocker fails readiness.

For a freeform task: if it is under about ten words or has no acceptance,
stop and ask for one paragraph of context plus acceptance criteria.

Read the repo's CLAUDE.md `## Harness` section. If it is missing, stop and
say to run `/ship:adopt` first.

## 2. Readiness check

Flag the task if any of these hold. Surface every flag; do not silently
proceed and do not silently block.

1. No `ready` label (issues only).
2. No acceptance: no heading like Acceptance, Definition of done, Success
   criteria, or a "done when" list.
3. Unresolved questions: a heading like Open questions, or inline TBD,
   TODO:, decide:, not sure, figure out.
4. Unresolved options: Option A / Option B, Approach 1 / 2, with no
   Decision, Decided, Going with, or Settled marker after them.
5. Design issue: title starts with Design:, Proposal:, RFC:, Spike:, or
   Investigate:, with no Decisions or Conclusion section.
6. Too thin: under about 30 words of substance once headers and template
   scaffolding are removed.
7. An open blocker from step 1.
8. Suggested tests, or a prescribed test list. An issue says what the
   behaviour must achieve and what done means. It does not say how to
   test it, and it does not spell out the cases.

   This one is a warning rather than a block, but say it every time. A
   suggested list anchors: the spec-test pass works down the list instead
   of enumerating, and the cases the issue forgot stay forgotten, which is
   the whole thing the pass exists to catch. Prescribed wording does the
   same to a worker. Issue #1392 in utm-platform suggested exact user copy
   that was wrong for every short position; it was implemented faithfully
   and nobody questioned it until review.

   Domain knowledge the agent cannot derive is different and belongs in the
   issue: a real incident, a regression that must never recur, a broker
   quirk learned the hard way. Frame it as history and as what must not
   break, never as a test to write.

If any flag tripped, report them as one line each (`#657: no Acceptance
section`) and ask whether to brief anyway, brief as a research task, or
skip. When running non-interactively (inside delegate with `--yes`), a
flagged task is skipped and reported, never briefed.

## 3. Write the brief

Return it as a fenced markdown block. Do not write a file; the caller embeds
the brief in the worker's prompt so it works in a local subagent, a cloud
session, and a pasted prompt alike.

```
# Worker brief: <title>

Issue: <url>   (omit for freeform)

## Worktree

<absolute path>   (or "TO BE SET BY DELEGATE" when called standalone)
Branch: <type>/<slug> off <default branch>
Dependencies are installed and .env is in place.

## Why this exists

<the why, background, or bug section, with file:line references kept>

## Scope

<the scope as written, structure preserved>

## Spec addenda (authoritative over Scope where they differ)

<the captured comments, verbatim, in order; omit the section if none>

## Acceptance

<bullets>

## Out of scope

<as written; omit if none>

## Repo rules

Read <worktree>/CLAUDE.md before starting. Its Harness section names the ci
gate: `<ci gate>`. It must pass before you push.
<one or two conventions from CLAUDE.md that bear on this issue>

## When done

Follow /ship:ship-issue from "Verify" onward: rebase on <default branch>,
run the ci gate, commit in Conventional Commits form, push, open the PR with
`Closes #<n>` on its own line, and report the PR URL.

Do not touch any roadmap, sprint, or planning file. The orchestrator owns
those and updates them after merge.
```

Branch type: `fix/` for a `bug` label, `chore/` for `chore` or `refactor`,
`docs/` for `documentation`, else `feat/`. Slug: kebab-case from the title,
prefixed with the issue number, for example `feat/issue-164-review-table`.
