---
name: raise-issue
description: Write one GitHub issue that a spec-test pass and a worker can act on without guessing. Captures the problem, the evidence, the behaviour wanted, what done means, and the regressions that must not recur. Use when raising an issue, writing up a bug, or turning a rough note into something delegable.
argument-hint: <rough description, or a paste of notes>
allowed-tools: Bash(gh:*), Bash(git:*), Read, Grep, Glob, AskUserQuestion
---

Write the issue for `$ARGUMENTS`. You are writing for two readers who are
not you: a spec-test pass that will enumerate the behaviour, and a worker
who will implement it. Neither can ask you a question later.

## What the issue must carry

Only the first five are always required.

1. The problem, in the terms of what a person cannot do or what goes wrong.
   Not the fix. "The card renders nothing when there is no suggestion, so
   the user cannot tell why" beats "add a reason field".
2. When the issue adds behaviour, the module that owns it, taken from the
   repo's CLAUDE.md ownership map. If no module owns it yet, say a new
   module is needed and what it will own.
3. Evidence. What was observed: real output, a log line, counts, a date, an
   account, a screenshot's content. This is the part nobody can reconstruct
   later and the part that survives longest. "114 credential failures at
   3/3 attempts, empty DLQ, zero audit rows, 24 to 29 June" is worth more
   than three paragraphs of description.
4. The behaviour wanted, stated so it can be checked. What the system does
   afterwards, in which situations.
5. Acceptance. What done means, as a list a reviewer can walk. Each line
   must be decidable: someone reads it, looks at the PR, and says met or
   not met, with no interpretation.
6. Known regressions, when there are any. A thing that broke before and
   must not break again, with its history. This is domain knowledge the
   codebase does not contain and no agent can derive.
7. Out of scope, when the issue sits next to work it must not absorb.
8. Related issues and PRs, including anything it must land after.

## What the issue must NOT carry

- A test list, or "add a test for X". The spec-test pass enumerates the
  cases, and its whole value is finding the ones you did not think of. A
  list makes it work down your list instead, so the cases you forgot stay
  forgotten. Describe the behaviour and let it find the axes.
- An implementation, unless the choice is genuinely yours to make and you
  have made it. Then mark it as decided and say why, so it reads as a
  constraint rather than a suggestion.
- An unmade choice. "Option A or B, first is recommended" is not ready, it
  is a decision wearing an issue's clothes. Decide, or raise it as a
  question issue and let this one wait.

## Prescribed wording, and the trap in it

You may prescribe user-facing copy, and sometimes you should, because voice
is the author's call. But copy in an issue gets implemented verbatim and
treated as settled, so it must be checked before it is written down.

Before prescribing any string, walk it against the axes the thing varies on.
utm-platform#1392 suggested copy saying the broker's order history
"includes sells". The entry side of a short is a sell, so the sentence was
wrong for every short position. It was implemented faithfully, and nobody
questioned it until review.

If you prescribe copy, say which cases you checked it against. If you have
not checked, state the meaning you want and let the implementation find the
words.

## Before you write

Read enough of the codebase to be accurate about what exists now. An issue
that names a function that does not exist, or describes current behaviour
wrongly, sends everyone downstream to the wrong place, and it is a stated
fact rather than an obvious gap, so it is trusted.

Also read `<base>/../../rules/coding.md`, the plugin's shared coding
rules, alongside the repo's CLAUDE.md ownership map, so the module you
name in the issue is the real owner. Where the repo's CLAUDE.md and the
rules file disagree, the repo's CLAUDE.md wins.

Do not write acceptance you cannot check yourself. If you cannot tell
whether it would be met, neither can the reviewer.

## Output

Draft the body, show it, and confirm before creating. Then
`gh issue create` with a conventional-commit-style title naming the surface
(`fix(api):`, `feat(web):`, `docs:`), and labels for type and priority.

Do NOT apply the `ready` label. `/ship:ready-issue` earns that by checking
the issue against the codebase. An issue you wrote and labelled ready
yourself has had one pair of eyes on it.

Australian English, plain ASCII, no emojis, no em dashes.
