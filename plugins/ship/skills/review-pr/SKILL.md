---
name: review-pr
description: The review checklist. Review one pull request against its issue spec and the repo's rules, post findings on the PR, and return APPROVE or CHANGES. Runs in whatever context calls it: inline in the orchestrator for a small diff, or inside the ship:reviewer agent (opus, fresh context) for anything larger or riskier. Use when asked to review a PR or as the review step of land.
argument-hint: <pr-number>
allowed-tools: Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr checks:*), Bash(gh pr review:*), Bash(gh pr comment:*), Bash(gh issue view:*), Bash(git:*), Bash(pnpm:*), Bash(npm:*), Read, Grep, Glob
---

Review PR #$ARGUMENTS. A cheaper model wrote it. Find what is wrong before a
merge does.

If you are the orchestrator reviewing inline, you share context with the
brief you wrote. Read the diff as a stranger would: start from the issue's
acceptance criteria, not from what you expected the worker to do.

## 1. Load the spec and the rules

- `gh pr view $ARGUMENTS --json title,body,baseRefName,headRefName,url,files`
- The `Closes #N` or `Refs #N` line names the issue. `gh issue view N` and
  `gh issue view N --comments`. The latest "Decisions taken" or "Spec
  addendum" comment is the spec where it differs from the body.
- The repo's CLAUDE.md, and whatever it names as the rulebook
  (`docs/conventions.md`, ADRs). These are the rules you review against.
  Do not import rules the repo has not written down.
- `gh pr checks $ARGUMENTS`. If CI is still running, wait for it. A red CI
  is a CHANGES verdict on its own, but keep reviewing so one round fixes
  everything.
- `gh pr diff $ARGUMENTS`. Read the whole diff, then open each changed file
  in full. A diff hides the function around the change.

Prefer running something over reasoning about it. If a claim can be checked
by executing it, execute it: read the installed dependency's source rather
than recalling its semantics, run the schema against the input the spec
names, reproduce the failing job locally. State which findings you verified
by running and which you reasoned about, because the second kind is where
reviews are wrong.

## 2. Judge, in this order

1. Spec. Walk the acceptance criteria one by one. Each is met, partly met,
   or missing. Scope creep counts against: a change the issue did not ask
   for is a finding.
2. Correctness. Trace the main path and the edge each criterion implies.
   Empty input, a missing row, a second call, a permission denied.
3. Tests. Does each behaviour have a test named for the behaviour? Would the
   test fail if the change were reverted? Pick one and check by reading,
   or by reverting locally if a worktree is available. A test that mirrors
   the code is not a test.
4. Rules. The repo's stated ones only: dependency direction, file size,
   where authorisation lives, no logging of personal data, config in the
   database, and whatever else its CLAUDE.md says.
5. Safety. Secrets in the diff, a migration that drops human-made data,
   a new route left open, participant or staff data reaching a log.
6. Docs. The repo's maps and conventions updated where the change moved
   something.

Skip style unless the repo names the rule.

## 3. Post and return

Post one PR comment with `gh pr comment $ARGUMENTS --body-file -`, in this
shape, plain sentences, no asterisk bullets:

```
Review by ship:reviewer

Verdict: APPROVE | CHANGES

Spec: <n of m criteria met; name any partly met or missing>

Findings (blocking):
1. <file:line> <what is wrong, what the spec or rule says, what to do>

Findings (should fix, not blocking). Each carries FIX NOW or FILE:
1. FIX NOW <file:line> <what is wrong, what to do>
2. FILE <proposed issue title> <one paragraph of body>

Checked and fine: <one line naming the risky parts you traced and found
sound, so the human knows what was covered>
```

## What blocking means

Blocking means the verdict is CHANGES.

A finding is blocking if it defeats what the issue set out to achieve, not
only if the code is defective. Name the issue's purpose in one sentence
before you classify anything, and judge against that sentence.

The two tests are different and the second one is the one that gets missed.
A DLQ escalation fix whose logs claim a retry is coming on the terminal
attempt is not defective, the audit row still lands, but the issue existed
because failures were invisible, so it fails its own purpose and blocks.
Copy that is wrong for short positions is not a crash, but the issue existed
to explain something to a user, so it blocks.

Also blocking: an acceptance criterion not met, red CI, a test that would
pass with the change reverted, a safety finding, and scope the issue did not
ask for.

Not blocking: anything the repo has not written down as a rule, a
preference, or work that is genuinely a separate issue rather than this one
done badly.

If you are unsure, ask whether a reader of the issue would say this PR did
what they asked. If they would hesitate, it blocks.

## Should-fix findings are fixed or filed, never dropped

Every "should fix" leaves this review in one of two states, and you say
which for each one:

- FIX NOW, when it is small, in the same files, and does not need a decision
  the issue did not make. Default to this. The worker is already in context
  and it is cheaper now than as a future issue nobody prioritises.
- FILE, when it needs a decision, widens scope, or belongs to another
  surface. Give the issue title and one paragraph of body so it can be
  filed without rediscovering the problem.

A should-fix with neither label is an incomplete review. Merging with an
unfiled should-fix is how a known problem becomes an unknown one.

Then return to the caller exactly:

```
VERDICT: APPROVE | CHANGES
PR: <url>
BLOCKING: <count>
SUMMARY: <one sentence>
```

Never edit code. Never merge. Never approve a PR whose CI is red.
