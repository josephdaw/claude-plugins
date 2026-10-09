# claude-plugins

Joe's Claude Code plugin marketplace. It holds one plugin today, `ship`,
which delegates GitHub issues to workers, reviews the PRs, and lands them.
Every repo the factory runs on loads `ship` from here, so a change to a
skill or agent changes how every repo's workers and reviewers behave.

## Tech stack

Markdown skills and agents, plus JSON manifests. No build step and no
dependencies. The `claude` CLI validates the manifests.

## Ownership map

Find the existing owner; do not create a parallel implementation.

| Concern | Owner |
|---------|-------|
| Marketplace listing | `.claude-plugin/marketplace.json` |
| ship manifest and version (bumped by Release Please) | `plugins/ship/.claude-plugin/plugin.json` |
| The ci gate | `scripts/ci.sh` |
| Version convention check | `scripts/check-manifest-versions.py` |
| Release config and current versions | `release-please-config.json`, `.release-please-manifest.json` |
| The release workflow | `.github/workflows/release-please.yml` |
| Generated changelog per plugin | `plugins/<name>/CHANGELOG.md` |
| What each ship skill does | `plugins/ship/skills/<name>/SKILL.md` |
| Worker, reviewer, and spec-test agents | `plugins/ship/agents/<name>.md` |
| The coding rules every repo is held to | `plugins/ship/rules/coding.md` |
| How to adopt and use ship | `plugins/ship/README.md` |
| Why ship works the way it does | mnemosyne `ops/harness/ship-workflow.md` |

## Rules

- Versions are never bumped by hand. Release Please reads the
  Conventional Commit types on main (feat = minor; fix, perf, and revert =
  patch; chore, docs, ci, refactor, test, style, and build do not
  release), opens a release PR that bumps `plugin.json` and writes the
  plugin's CHANGELOG.md, and Joe merges it. A `!` after the type, or the
  text `BREAKING CHANGE:` or `BREAKING-CHANGE:` anywhere in a squash
  body, bumps the major, so 0.x becomes 1.0.0. Never write that text in
  a PR body unless you mean it.
  CHANGELOG.md is generated, never edited by hand. A commit releases a
  plugin only when it touches files under that plugin's directory.
  marketplace.json carries no version; the ci gate fails if one is added.
  History before 2026-09-12 does not hold to this: 0.3.0 and 0.4.0 shipped
  while marketplace.json still said 0.2.1, which is the reason for this
  rule.
- After a release PR merges, installed copies update on the next
  auto-update, or by running
  `claude plugin update ship@josephdaw --scope project` in each repo.
- A rule lives in one skill. Other skills point to it, they do not
  restate it.
- Skill text is read by agents. Write rules as plain, checkable
  instructions.
- Australian English, plain ASCII, no emojis, no em dashes.
- Conventional commits with a `ship` scope, for example `feat(ship):`.

## How to run it

No build. Validate with:

```
./scripts/ci.sh
```

That validates the marketplace and every plugin manifest, then checks that
marketplace.json carries no version and that every listed plugin's
plugin.json has one.

To try a change before release, point a session at this checkout with
`claude --plugin-dir plugins/ship`.

### Adding a plugin later

Add a `packages` entry in `release-please-config.json` with its own
`component` and `extra-files` pointing at its plugin.json, and a matching
entry in `.release-please-manifest.json` with its current version.
Without a manifest entry, its first release is 1.0.0.

## Harness

Read by the ship plugin (josephdaw/claude-plugins). Change a value here,
not in the plugin.

| Setting | Value |
|---------|-------|
| merge policy | auto |
| ci gate | ./scripts/ci.sh |
| default branch | main |

merge policy auto: the orchestrator merges after CI passes and the
reviewer approves. human: a person reviews and merges.
