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

**PR description format (no asterisk):**
```
feat: implement comprehensive testing coverage

Enable 77 additional passing tests through systematic infrastructure improvements.
Improve test coverage from 97 to 174 passing tests with behaviour-focused testing.
Add critical path validation for authentication, database operations and API endpoints.

Technical improvements include fixing authentication controller issues and resolving database connection handling.
```
