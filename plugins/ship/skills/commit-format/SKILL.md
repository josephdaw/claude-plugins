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
it is the only account of the change that reaches main. Keep it short and
keep it true for the life of the PR, including after fix rounds.

Four parts, plain sentences, no asterisk bullets:

1. What changed, as behaviour a user or caller sees.
2. How it was tested: the command run, for example the ci gate. No counts.
3. A line starting `Not verified:` naming each acceptance line or
   behaviour that no test or executed check proves, and how to check it by
   hand. Write `Not verified: nothing` only when every acceptance line is
   proven by a test or a check actually run.
4. `Closes #N` (or `Refs #N` when the PR does not finish the issue) on its
   own line.

It never holds test counts or other numbers that change as tests or code
change, and never an account of how the code works inside. The diff shows
that; a stale number or a paraphrase of the diff is a claim that can go
false without anyone updating it.

**Example:**
```
feat: reject a login when the account is locked

Login now returns 423 with a locked-account message instead of the
generic 401 when the account's lock flag is set. Callers see the same
response whether the lock came from repeated failed attempts or an
admin action.

Tested by running the ci gate.

Not verified: the admin-triggered lock path, since no test seeds an
admin-set lock. Check by hand: set a user's locked_at from the admin
console, then attempt that user's login and confirm 423.

Closes #142
```
