---
name: review-pr
description: The review checklist. Review one pull request against its issue spec and the repo's rules, post findings on the PR, and return APPROVE or CHANGES. Runs in whatever context calls it: inline in the orchestrator for a small diff, or inside the ship:reviewer agent (opus, fresh context) for anything larger or riskier. Use when asked to review a PR or as the review step of land.
argument-hint: <pr-number>
allowed-tools: Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr checks:*), Bash(gh pr comment:*), Bash(gh issue view:*), Bash(gh issue list:*), Bash(git:*), Bash(pnpm:*), Bash(npm:*), Read, Grep, Glob
---

Review PR #$ARGUMENTS. A cheaper model wrote it. Find what is wrong before a
merge does.

If you are the orchestrator reviewing inline, you share context with the
brief you wrote. Read the diff as a stranger would: start from the issue's
acceptance criteria, not from what you expected the worker to do.

One review round per PR. This skill reviews the whole PR once. A second
pass happens only after a worker fix round that changed code, and that
pass reads only the fix diff, in the shorter re-review shape at the end of
section 3. A text-only finding (the PR description, a code comment, a
docstring, or docs) never earns a re-review: `/ship:land` applies the
wording itself and moves straight to merge.

## 1. Load the spec and the rules

- `gh pr view $ARGUMENTS --json title,body,baseRefName,headRefName,url,files`
- The `Closes #N` or `Refs #N` line names the issue. `gh issue view N` and
  `gh issue view N --comments`. The latest "Decisions taken" or "Spec
  addendum" comment is the spec where it differs from the body.
- The repo's CLAUDE.md, and whatever it names as the rulebook
  (`docs/conventions.md`, ADRs).
- `<base>/../../rules/coding.md`, the plugin's shared coding rules. This
  file counts as written down: it applies to every repo whether or not
  that repo's own CLAUDE.md mentions structure, DRY, or any of it. Where
  the repo's CLAUDE.md and the rules file disagree, the repo's CLAUDE.md
  wins.
- These two sources are the rules you review against. Do not import a
  rule beyond what they, together, have written down.
- `gh pr checks $ARGUMENTS`. If CI is still running, wait for it. A red CI
  is a CHANGES verdict on its own, but keep reviewing so one round fixes
  everything.
- `gh pr diff $ARGUMENTS`. Read the whole diff, then open each changed file
  in full. A diff hides the function around the change.
- Walk every sentence of the PR description against the code at the
  reviewed head. Check each one for two things: is it true, and does it
  hold to the template `ship:commit-format` defines (the five headed
  sections, under 250 words, `Not verified:` inside Risk,
  `Closes`/`Refs #N` in Why). This full walk happens once, on this round;
  a re-review after a fix round does not repeat it.
- `gh issue list --state open --search "<keywords>"` when you are about to
  write a Follow-up, so you append to an existing issue instead of a new
  one.

Prefer running something over reasoning about it. If a claim can be checked
by executing it, execute it: read the installed dependency's source rather
than recalling its semantics, run the schema against the input the spec
names, reproduce the failing job locally. State which findings you verified
by running and which you reasoned about, because the second kind is where
reviews are wrong.

## 2. Judge, in this order

1. Spec. Walk the acceptance criteria one by one. Each is met, partly met,
   or missing. A related fold-in is welcome and expected, not scope creep:
   a small related fix in a file the PR already touches is the fold-in
   rule working (rules/coding.md, "Fix related problems now"). An
   unrelated change, one that needed a decision the issue did not make or
   that touches a file or area the issue does not reach, is a [spec] Must
   fix.
2. Correctness. Trace the main path and the edge each criterion implies.
   Empty input, a missing row, a second call, a permission denied.
3. Tests. Does each behaviour have a test named for the behaviour? Would the
   test fail if the change were reverted? Pick one and check by reading,
   or by reverting locally if a worktree is available. A test that mirrors
   the code is not a test.

   When the PR has a spec-test commit, two checks are mechanical, so do
   them rather than judge them:

   - The test files have not changed since that commit:
     `git diff <test-sha> HEAD -- <test paths>`. Any change is a Must fix
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
   - When the PR has a spec-test commit and you raise a Must fix for a
     behaviour those tests did not cover, also add a NOTE starting
     `spec-tests missed:` naming the behaviour, in the Notes block
     (delegate step 3b reads it from there for its count).
4. Rules. The repo's stated ones, plus the Structure rules in the coding
   rules file: dependency direction, file size, where authorisation
   lives, no logging of personal data, config in the database, and
   whatever else the repo's CLAUDE.md says. On Structure, a duplicated
   owner, a module missing from the ownership map, an import going the
   wrong way, a cap breach, or a raised ratchet baseline is a Must fix.
5. Safety. Secrets in the diff, a migration that drops human-made data,
   a new route left open, participant or staff data reaching a log.
6. Docs. The repo's maps and conventions updated where the change moved
   something.

Skip style unless the repo names the rule.

## 3. Post and return

Post one PR comment with `gh pr comment $ARGUMENTS --body-file -`, in this
shape. Under 400 words, not counting the Notes block. At most two
sentences per finding. No legend, no "Verified by" lines, no "checked and
fine" list, no TLDR block:

```
Review: APPROVE | CHANGES (<who>, <model>) at <short head sha>
Spec: <n> of <m> criteria met. <Name any partly met or missing.>

Must fix (blocks merge)
1. [defect|test|spec] <file:line>. <What is wrong.> <What to do.>

Lander fixes (no re-review)
- <file:line, or "PR body, <section>">: <the exact replacement text>

Follow-up
- Append to #<N>: <one line>
- Suggest: <title>. <one line on why it waits>

Not verified
- <one line each: what nobody checked, and how to check it by hand>

<details><summary>Notes</summary>

- <one NOTE per line>

</details>
```

`<who>` is `ship:reviewer` when the agent runs it, `inline` when the
orchestrator reviews in its own context. `<model>` is the model that
reviewed (opus, fable, sonnet). The first line always starts `Review: `.
`land` and `notes-scan` find reviews by that first line, so never alter
its shape.

Verdict: CHANGES when Must fix has any item. Lander fixes alone do not
block: the verdict is APPROVE, and `/ship:land` applies them before
merge.

Omit an empty Must fix, Lander fixes, or Follow-up section. The Notes
block appears only when there are notes.

Not verified is still the most valuable line for a reader who will not
read the rest and will merge on it: say plainly what nobody checked and
how to check it by hand. Write "nothing" only when every acceptance line
was proven by a test or a check actually run. Never leave the section out.

### A re-review (after a worker fix round)

Reads only the fix diff, under 100 words:

```
Review: APPROVE | CHANGES (<who>, <model>) at <short head sha>, fix diff <old sha>..<new sha>
- Must fix 1: fixed. | still wrong: <one sentence>.
- <any new Must fix the fix diff introduced, same shape as above>
```

## Must fix, Lander fixes, or Follow-up

Three outcomes, one owner each. There is no "should fix, not blocking".
A related fold-in is a Must fix, not a Follow-up, so the worker and
reviewer get as much as they can into the one PR. In a risk-area PR the
one-change rule wins: the same finding becomes a Follow-up instead,
because the worker reports the related fix rather than making it.

- Must fix. Wrong, and this PR's to fix. Any size. Tag it `defect` (wrong
  behaviour, or a reader of the merged code would be misled into a wrong
  result; red CI; a safety finding), `test` (a behaviour the PR adds or
  changes that no test proves, or a test that would still pass with the
  change reverted), or `spec` (an acceptance line not met, or a change
  unrelated to the issue that is not a fold-in). Each finding names what
  it is wrong against: an acceptance line, a written repo rule, a
  correctness trace, or a test gap. One that cannot name one is a NOTE,
  not a Must fix. Any Must fix means CHANGES and a fix round clears it.
  A small related fix in a file the PR already touches is a Must fix (or
  a Lander fix if it is text), never a Follow-up, unless this is a
  risk-area PR.
- Lander fixes. Text only: the PR description, a code comment, a
  docstring, or docs. Give the exact replacement text; if you cannot give
  the exact text, it is not a Lander fix, put it under Must fix instead.
  A broken "never" rule in text (for example test counts in the PR body)
  is a Lander fix, not a NOTE. `/ship:land` edits these itself with no
  worker round and no re-review.
- Follow-up. Only work that needs a decision the issue did not make, or
  that sits in another area (a file or module the PR does not touch,
  another owner). Before writing one, check open issues
  (`gh issue list --state open --search "<keywords>"`). Write
  "Append to #N" when one fits, "Suggest: <title>" with one line on why
  it waits when none does. You never run `gh issue create`, `edit`, or
  `comment`; `/ship:land` is the only step that writes to an issue.

The test: would a reader of the merged code be misled, or would a user or
operator see a wrong result? Yes is Must fix (or a Lander fix if the fix
is an exact piece of text). No, but the codebase is worse off in a way
another decision or area should own: Follow-up. Neither: NOTE.

Must fix includes things that used to slide as "not blocking": a log line
that misleads an operator, output that drops data under a shape the spec
covers, a written repo rule broken (dependency direction, a file size the
PR made worse), a test that does not test the thing (it would pass with
the change reverted, or it calls the unit directly instead of driving the
path the spec names), a missing test for a behaviour the acceptance
names, red CI, a safety finding, and an unrelated change that is not a
fold-in.

NOTE, for example: a name that could be better; wording that is correct
but could be tighter; a pattern you prefer where the repo has no stated
rule. One short line each, in the Notes block. Nothing happens to a NOTE
now; a weekly scan over merged PRs looks for trends.

You never apply a finding yourself, of any kind. The worker applies a
Must fix and you re-review the fix diff; `/ship:land` applies a Lander
fix without a re-review. Reviewing your own fix is not a review.
