---
name: notes-scan
description: Weekly scan of the NOTE items reviewers left on merged PRs. Looks for trends, turns a repeated one into a written repo rule, and proposes one small tidy-up PR at most. Run by Talos at the end of the week or as a scheduled routine, or by hand with /ship:notes-scan.
argument-hint: [--since YYYY-MM-DD] [--repo owner/name]
---

NOTE items are review findings that are not wrong: taste, naming, tighter
wording. Nothing happens to them at review time, on purpose. This skill is
the one place they are read, once a week, so a pattern gets a rule and a
one-off gets dropped.

## 1. Collect

Default window: the last seven days. `--since` overrides. Repo from the
Harness section of the current checkout, or `--repo`.

- `gh pr list --state merged --search "merged:>=<since>" --json number,title,mergedAt`
- For each PR, `gh pr view <n> --json comments` and pull every line that
  starts with `NOTE` from a comment headed `Review by ship:reviewer`.
- Also collect DEFER lines and confirm each has an issue number. One with
  none is a review that broke the rule; report it, do not file it here.

## 2. Sort

Group the NOTE lines by what they are about, not by PR: naming, comment
wording, ordering and layout, a pattern preference, other. A group with
three or more entries across different PRs is a trend.

## 3. Decide, per group

- Trend, and the repo has no written rule for it: draft the rule as one
  or two lines for the repo's CLAUDE.md or conventions doc, in the repo's
  voice. Open a PR with only that change. Next week the same finding is a
  FIX, not a NOTE.
- Trend, and a rule already exists: the reviewer is under-classifying.
  Say so in the report with the rule quoted. No PR.
- One-offs worth ten minutes together, all in files nobody has an open PR
  against: at most one tidy-up PR, `chore(tidy): <week>`, each change one
  commit, no behaviour change, ci gate green.
- Everything else: drop. Say how many were dropped.

Never more than two PRs from one scan. A scan that finds nothing and opens
nothing is a good outcome; say so in one line.

## 4. Report

```
Notes scan <repo> <since> to <today>
PRs read: <n>   NOTE lines: <n>   DEFER without issue: <n, list>
Trends:
- <group>: <count> across <PRs>. Rule PR #<n> | rule exists: "<quote>"
Tidy-up PR: #<n> | none
Dropped: <n>
```

Post the report as a comment on the repo's tracking issue if the Harness
section names one, otherwise return it to the caller.
