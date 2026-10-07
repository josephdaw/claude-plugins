---
name: commit-format
description: Release Please conventional commit and PR description format. Use when writing a git commit message, drafting a PR title or body, or asking which commit type or scope to use for a change.
---

# Commit Message Format (Release Please Specification)

Follow the Release Please format for automated changelog generation.

**Format:**
```
<type>(<scope>): <description>

<body>

<footer>
```

**Types:**
- feat: New feature for users
- fix: Bug fix for users
- docs: Documentation changes
- style: Code style changes (formatting, missing semicolons)
- refactor: Code refactoring without feature changes
- test: Adding or updating tests
- chore: Build process, dependency updates, tooling
- perf: Performance improvements

**Body guidelines:**
- Write body paragraphs as complete sentences ending with periods
- Multiple paragraphs are allowed
- Include relevant metadata like PiperOrigin-RevId or Source-Link when applicable
- For breaking changes, add BREAKING-CHANGE: in the footer

**Release Please best practices:**
- Do NOT use asterisk (*) prefixes in PR descriptions
- Release Please processes final merge commits on main branch
- Use standard conventional commit format for PR titles and descriptions
- Focus on clear, descriptive commit messages for the final merge commit

**Examples:**
```
feat: adds v4 UUID to crypto

This adds support for v4 UUIDs to the library.

fix(utils): unicode no longer throws exception
  PiperOrigin-RevId: 345559154
  BREAKING-CHANGE: encode method no longer throws.
  Source-Link: googleapis/googleapis@5e0dcb2

feat(utils): update encode to support unicode
  PiperOrigin-RevId: 345559182
  Source-Link: googleapis/googleapis@e5eef86
```

**PR description format**

This is also the squash commit body on merge (see `land` and `adopt`), so
it is the only account of the change that reaches main. Keep it under 250
words and keep it true for the life of the PR, including after fix
rounds.

Five headed sections, plain sentences, no bullets (the template uses
none):

```
## What changes
2 to 4 sentences on behaviour a user or caller sees. Not internals.

## Why
Closes #N. One line on the problem if the issue title does not say it.

## Evidence
Before: the failing test or observed behaviour.
After: the same test passing, or the output or screenshot.

## Risk
Door: one-way or two-way (migrations, data writes, and broker or payment
calls are one-way).
Blast radius: what breaks if this is wrong.
Not verified: what was not checked and how to check it by hand, or
"nothing" only when every acceptance line is proven by a test or a check
actually run.

## Where to look
2 to 5 files in reading order. Mark any moves-only commit.

Generated with Claude Code
```

Rules:

- Under 250 words.
- No test or line counts, no review-round history, no session links. The
  diff shows how the code works inside; a stale number or a paraphrase of
  the diff is a claim that can go false without anyone updating it.
- `Not verified:` is a line inside Risk, never its own heading.
- `Closes #N` (or `Refs #N` when the PR does not finish the issue). With
  no issue, Why holds the problem line alone and there is no Closes/Refs
  line.
- Plain ASCII. The last line is the plain-text attribution line,
  `Generated with Claude Code`, with no emoji and no session link. The
  Claude Code `attribution` project setting that `ship:adopt` writes
  produces this line. Where that setting is missing, this rule is the
  user instruction that outranks Claude Code's default footer.

**Example:**
```
feat: reject a login when the account is locked

## What changes
Login now returns 423 with a locked-account message instead of the
generic 401 when the account's lock flag is set. Callers see the same
response whether the lock came from repeated failed attempts or an
admin action.

## Why
Closes #142.

## Evidence
Before: logging in with a locked account returned 401, the same as a
wrong password.
After: the same request returns 423 with a locked-account message; ci
gate passing.

## Risk
Door: two-way, no migration.
Blast radius: a bug here would mask account locks as ordinary login
failures again.
Not verified: the admin-triggered lock path, since no test seeds an
admin-set lock. Check by hand: set a user's locked_at from the admin
console, then attempt that user's login and confirm 423.

## Where to look
src/auth/login.ts, src/auth/lockout.ts

Generated with Claude Code
```
