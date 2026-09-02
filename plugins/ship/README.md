# ship

Delegate a GitHub issue to a worker, review the PR with a higher tier model,
and land it under the repo's merge policy.

## The loop

```
/ship:delegate 164 171        orchestrator: brief each issue, make a worktree,
                              launch a worker (local subagent, cloud, or paste)
    /ship:ship-issue 164      worker: brief to PR
/ship:land 167                orchestrator: CI, review, fix loop, then merge
                              or hand to a human, then clean up
```

Each piece also stands alone:

| Skill | Who runs it | What it does |
|-------|-------------|--------------|
| `brief` | orchestrator | Turn an issue into a worker brief, with a readiness check |
| `ship-issue` | worker | Brief to open PR: worktree, tests, code, docs, commit, push |
| `review-pr` | reviewer agent | Judge a PR against the spec and the repo's rules, post findings, return a verdict |
| `land` | orchestrator | Wait for CI, run review-pr, route fixes, merge or hand over, clean up |
| `delegate` | orchestrator | brief + worktree + launch, for one or many issues |
| `adopt` | anyone | Set a repo up: settings.json and the `## Harness` section |

| Agent | Model | Used by |
|-------|-------|---------|
| `worker` | sonnet | delegate, land (fix rounds) |
| `reviewer` | opus | land, or `/ship:review-pr` directly |

## What a repo must provide

A `## Harness` section in its CLAUDE.md. The skills read it and refuse to
guess when it is missing. `/ship:adopt` writes it.

```
## Harness

| Setting | Value |
|---------|-------|
| merge policy | auto |
| ci gate | pnpm lint && pnpm typecheck && pnpm test && pnpm build |
| worktree | scripts/new-worktree.sh <branch> |
| default branch | main |
```

merge policy is `auto` (the orchestrator merges after CI passes and the
reviewer approves) or `human` (the orchestrator posts its review and stops;
a person merges). Use `human` for anything in production.

ci gate is the one command a worker must pass before pushing.

worktree is optional. Without it, delegate uses `git worktree add` beside
the checkout.

## Worker model

Workers default to sonnet. Pass `--model haiku` to delegate for a mechanical
issue (rename, copy change, config). The reviewer stays on opus regardless,
because the review is the check on the cheaper model.

## Conventions the skills assume

Issues carry a `ready` label once they are specified. The most recent issue
comment titled "Decisions taken" or "Spec addendum" beats the body. PR
bodies carry `Closes #N` on its own line. Commit subjects follow Conventional
Commits, checked by the repo, not by this plugin.
