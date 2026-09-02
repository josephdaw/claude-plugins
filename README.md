# claude-plugins

Joseph Daw's Claude Code plugins. One marketplace, one plugin per concern.

| Plugin | What it does |
|--------|--------------|
| `ship` | Delegate a GitHub issue to a worker, review the PR with a higher tier model, and land it under the repo's merge policy. See `plugins/ship/README.md`. |

## Use in a repo

Commit this in the repo's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "josephdaw": { "source": { "source": "github", "repo": "josephdaw/claude-plugins" } }
  },
  "enabledPlugins": { "ship@josephdaw": true }
}
```

Or run `/ship:adopt` from a session that already has the plugin, which writes
that and the `## Harness` section the skills read.

Every session that opens the repo, local or cloud, then has the plugin.
Personal skills in `~/.claude` never reach a cloud session, which is why this
lives in a repo.

## Terms

Skill: one instruction file, run as a slash command or picked up by Claude.
Agent: a subagent definition with a model and a tool list.
Hook: a shell command Claude Code runs on an event.
Plugin: a bundle of the above that installs as a unit.
Marketplace: this repo, a catalogue of plugins.
Harness: everything around the model, including each repo's CLAUDE.md,
lint, git hooks, and CI. A plugin is one part of a harness.

## Style

Australian English. Plain ASCII. No emojis, no em dashes.
