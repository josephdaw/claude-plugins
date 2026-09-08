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
| `worktree` | anyone | Create a worktree in any repo, handling env files; delegate's fallback when there is no worktree script |

| Agent | Model | Used by |
|-------|-------|---------|
| `worker` | sonnet | delegate, land (fix rounds) |
| `reviewer` | opus | land in `fork` mode; a fresh-context wrapper around `review-pr` |

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

## Which model does what

Workers: delegate picks per issue. Haiku for a mechanical change (rename,
copy, config, dependency bump, a `docs` or `chore` label), sonnet for
anything with behaviour to prove. `--model` forces it. The pick is printed
so a wrong rule gets fixed here rather than overridden each time.

Review: `review-pr` is one checklist. land runs it in one of two places.
`fork` launches the `reviewer` agent on opus in a fresh context, the
default. `self` runs it inline in the orchestrator, chosen only for a small
diff that touches nothing risky, because an inline review shares the
blind spots of the session that briefed the work. `--review` forces either.

## Conventions the skills assume

Issues carry a `ready` label once they are specified. The most recent issue
comment titled "Decisions taken" or "Spec addendum" beats the body. PR
bodies carry `Closes #N` on its own line. Commit subjects follow Conventional
Commits, checked by the repo, not by this plugin.
