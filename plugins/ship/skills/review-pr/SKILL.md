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
- Walk every sentence of the PR description against the code at the
  reviewed head. Check each one for two things: is it true, and does it
  hold to the four-part shape `ship:commit-format` defines (what changed,
  how it was tested, a "Not verified" line, `Closes`/`Refs #N`). Do this
  on every review, including a re-review after a fix round: walk the whole
  description again, not only the sentences that changed.

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

   When the PR has a spec-test commit, two checks are mechanical, so do
   them rather than judge them:

   - The test files have not changed since that commit:
     `git diff <test-sha> HEAD -- <test paths>`. Any change is a FIX
     unless the PR body records that the orchestrator approved it and why.
     An implementer that edits the tests to pass has removed the guarantee,
     and a green suite then means nothing.
   - Tests the worker added after the implementation get more suspicion than
     the spec tests, not less. They were written with the code in front of
     them, so the revert test is the only thing that separates a regression
     test from a mirror of the implementation. Check at least one properly.
   - The tests were genuinely red first: check out the test commit, run
     them, confirm they fail for the absence of the behaviour rather than a
     missing import. This turns "would it fail if reverted" from a guess
     into evidence, so do not skip it because the tests are green now.
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

TLDR
Verified by running: <the claims you executed, one line>
Verified by reading: <the claims you traced but did not execute>
Not verified: <what nobody has checked, and what would check it>
Merge risk if wrong: <one sentence on what breaks in production>

Spec: <n of m criteria met; name any partly met or missing>

Findings. Each is FIX, DEFER, or NOTE. Any FIX means CHANGES:
1. FIX <file:line> <what is wrong> <the acceptance line, repo rule, or
   trace it fails> <what to do>
2. DEFER #<issue> <one line on why it is not this PR's to fix>
3. NOTE <one line, no file:line needed>

Checked and fine: <one line naming the risky parts you traced and found
sound, so the human knows what was covered>
```

The TLDR is written for someone who will not read the rest and will merge
on it. Keep it to those four lines. "Not verified" is the most valuable of
them: say plainly what no one has checked, because a reader who is not
reading the code themselves has no other way to know. Never leave it empty
to look thorough. If everything really was verified, say so and name how.

## FIX, DEFER, or NOTE

Three labels, one owner each. There is no "should fix, not blocking".
Deferring work that belongs to this PR grows the backlog, so the default
is FIX, and the worker and reviewer get as much as they can into the one
PR.

- FIX. Wrong, and this PR's to fix. Any size. Every FIX names what it is
  wrong against: an acceptance line, a rule the repo has written down, a
  correctness trace, or a test gap. A FIX that cannot name one is a NOTE.
  Any FIX means the verdict is CHANGES and the fix round clears it.
- DEFER. Real, but out of scope for this issue or in need of a decision
  the issue did not make. You create the issue before you post the review:
  `gh issue create` with a title, a body written from the finding, and a
  link to the PR. The review carries the issue number. A DEFER without an
  issue number is an incomplete review.
- NOTE. Not wrong. Taste, a nicer name, tighter wording, ordering. One
  short list at the end. Nothing happens to it now; a weekly scan over
  merged PRs looks for trends.

The test: would a reader of the merged code be misled, or would a user or
operator see a wrong result? Yes is FIX. No, but the codebase is worse off
in a way another issue should own: DEFER. Neither: NOTE.

FIX includes things that used to slide as "not blocking":

- A false claim in a comment or PR body (a version number that is not the
  installed one, an issue number that credits the wrong PR, a test count,
  or a described behaviour the code does not have). False documentation
  misleads the next reader, so it is a defect. A PR description sentence
  that is true but does not hold to the `ship:commit-format` shape (for
  example it counts tests, or it is a bullet point) is a NOTE, not a FIX:
  it misleads nobody, so it does not cost the worker a round.
- A log line that misleads an operator.
- Output that drops data under a shape the spec covers.
- A written repo rule broken: prose style, dependency direction, file
  size the PR made worse.
- A test that does not test the thing: it would pass with the change
  reverted, or it calls the unit directly instead of driving the path the
  spec names.
- A missing test for a behaviour the acceptance names.
- An acceptance criterion not met, red CI, a safety finding, scope the
  issue did not ask for, and anything that defeats the issue's purpose
  even if the code is not defective. Name the issue's purpose in one
  sentence before you classify anything, and judge against it.

DEFER, for example: a defect the PR exposed but did not cause, in code it
did not touch; a design question the issue left open; anything that would
widen the PR past one coherent change.

NOTE, for example: a name that could be better; wording that is correct
but could be tighter; a pattern you prefer where the repo has no stated
rule.

You never apply a FIX yourself. The worker does, and you review the new
head. Reviewing your own fix is not a review.
