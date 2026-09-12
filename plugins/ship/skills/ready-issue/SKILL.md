---
name: ready-issue
description: Review one GitHub issue against the codebase before it is delegated, flag what is wrong or missing, and apply the ready label when it holds up. The gate that makes the ready label mean something. Use when asked whether an issue is ready, to review an issue, or to label one ready.
argument-hint: <issue number>
allowed-tools: Bash(gh:*), Bash(git:*), Bash(pnpm:*), Bash(npm:*), Read, Grep, Glob
---

Review issue #$ARGUMENTS against the code it describes. Someone wrote it
from memory or from a session that has ended. Your job is to find where it
is wrong before a spec-test pass encodes it and a worker builds on it.

An issue that specifies the wrong behaviour is the most expensive failure
in this pipeline, because everything downstream measures against it. The
tests encode it, the implementation satisfies the tests, and the review
confirms the implementation matches the spec. Every stage passes and the
result is wrong. You are the only stage that checks the spec itself.

## 1. Read

`gh issue view $ARGUMENTS` and its comments. The latest decision comment
wins over the body. Then the repo's CLAUDE.md and whatever it names as the
rulebook, plus its decisions log if it has one. Also read
`<base>/../../rules/coding.md`, the plugin's shared coding rules. Where
the repo's CLAUDE.md and the rules file disagree, the repo's CLAUDE.md
wins.

## 2. Check it against the code, do not reason from the issue alone

Every one of these is a command, not a judgement. Run them.

- Every file, function, symbol, table, column, route, and flag the issue
  names still exists, and is spelled as written. Grep for each.
- The current behaviour the issue describes is the behaviour in the code.
  Read the path it names and confirm. An issue's account of "what happens
  today" is the claim most often out of date, because the writer was
  working from a session that has since shipped.
- The cause the issue asserts is the cause. If it says a thing happens
  because of X, read X. A plausible cause written confidently is worse
  than no cause, because it stops anyone looking further.
- Any version, dependency, or upstream behaviour it relies on. Read the
  installed source or the lockfile rather than recalling the semantics.
- Prescribed user-facing copy, checked against the axes the thing varies
  on. Long and short, empty and full, first and last, one and many. Copy
  that is only true for one case is a spec bug, and it will otherwise ship.
- Where the issue names an owning module, the repo's CLAUDE.md ownership
  map actually lists that module against that concern. Where the issue
  says a new module is needed, it says what the new module will own.
- For each file the issue names, the current line count, against the
  file cap the coding rules file and the repo's CLAUDE.md set. Flag any
  file already at 85 percent of the cap or more. If the issue's change
  will grow a flagged file, the split is raised first as its own issue,
  and this issue waits on it.

## 3. Check it is one deliverable

- One PR's worth. If it needs two, say where it splits and why.
- It does not depend on unlanded work, or it names that work and says it
  must land first.
- It does not contradict a decision in the repo's decisions log or ADRs.
  If it does, that is a reversal and needs to be argued, not slipped in.
- Nothing here is already done. Check the current code before assuming.

## 4. Check it can be acted on

- Acceptance exists and every line is decidable. "Works correctly" is not.
- No unmade choice. Options with no decision means not ready.
- No prescribed test list. Warn if present and say to remove it: it anchors
  the spec-test pass onto the cases the author already thought of, which
  are not the ones that matter.
- Evidence is present for a bug. Without it nobody can tell later whether
  the fix worked.
- Out of scope is stated where the issue sits next to work it could absorb.

## 5. Report, then label

Post one comment on the issue with what you found, in plain sentences:

```
Readiness review

Verdict: READY | NOT READY

Checked against the code: <what you actually ran or read, one line>

Blocking:
1. <what is wrong, the evidence, and what the issue should say instead>

Worth fixing:
1. ...

Confirmed accurate: <the claims you verified and found correct, so the next
reader knows what was covered and does not redo it>
```

On READY, apply the label: `gh issue edit $ARGUMENTS --add-label ready`.

On NOT READY, do not label, and do not fix the issue yourself unless the
correction is a fact you verified, such as a renamed symbol or a wrong line
number. Behaviour and scope are the author's to decide.

Never label ready an issue you have not checked against the code. The label
is the gate the whole pipeline trusts, and a label applied on a reading of
the prose alone is worth nothing to the stages that come after it.

Australian English, plain ASCII, no emojis, no em dashes.
