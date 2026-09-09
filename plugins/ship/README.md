# ship

Delegate a GitHub issue to a worker, review the PR with a higher tier model,
and land it under the repo's merge policy.

## The loop

```
/ship:raise-issue             author: write the issue, spec and evidence,
                              no test list, no unmade choice
/ship:ready-issue 164         reviewer: check the issue against the code,
                              then apply the ready label
/ship:delegate 164 171        orchestrator: brief each issue, make a worktree,
                              spec tests first, then launch a worker
    /ship:spec-tests 164      opus: failing behaviour tests, committed alone
    /ship:ship-issue 164      worker: make them pass, add its own coverage
/ship:land 167                orchestrator: CI, review, fix loop, re-review,
                              then merge or hand to a human, then clean up
```

The two ends of that loop are the ones people skip and the ones that cost
most. A wrong spec is measured against by every stage after it, so they all
pass and the result is still wrong. A fix round that is not re-reviewed
means the commit that merges is not the commit anyone read.

Each piece also stands alone:

| Skill | Who runs it | What it does |
|-------|-------------|--------------|
| `raise-issue` | author | Write an issue a spec-test pass and a worker can act on: problem, evidence, behaviour, acceptance, known regressions |
| `ready-issue` | reviewer | Check an issue against the codebase, flag what is wrong, apply the `ready` label |
| `brief` | orchestrator | Turn an issue into a worker brief, with a prose-only readiness backstop |
| `ship-issue` | worker | Brief to open PR: worktree, tests, code, docs, commit, push |
| `review-pr` | reviewer agent | Judge a PR against the spec and the repo's rules, post findings, return a verdict |
| `land` | orchestrator | Wait for CI, run review-pr, route fixes, merge or hand over, clean up |
| `delegate` | orchestrator | brief + worktree + launch, for one or many issues |
| `adopt` | anyone | Set a repo up: settings.json and the `## Harness` section |
| `commit-format` | anyone | Release Please conventional commit and PR description format |
| `worktree` | anyone | Create a worktree in any repo, handling env files; delegate's fallback when there is no worktree script |

| Agent | Model | Used by |
|-------|-------|---------|
| `spec-tests` | opus | delegate, ahead of the worker; `--test-model fable` to decorrelate from the reviewer |
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

## Setting a repo up

`/ship:adopt` does all of this. The checklist, for reading or for doing by
hand:

1. `.claude/settings.json` declares the marketplace and enables the plugin
   (the JSON block above the Harness table in adopt). Committed, not local.
2. `.claude/hooks/session-start.sh`, cloud only, installs the plugin. Cloud
   sessions read project settings but do not install an external-source
   plugin on their own, so without this the ship skills are missing on the
   web. The same script is the place for anything else a cloud container
   needs: a Node version, a dependency install, a database for the tests.
   Skip with `--no-cloud-hook` if a repo does not want hooks.
3. A `## Harness` section in CLAUDE.md with the merge policy, ci gate,
   default branch, and optional worktree script.
4. Issues carry a `ready` label when specified, and a `talos` label to
   hand-pick them for an unattended night.

If ship skills are missing in a cloud session, check 2 first: the hook
must be committed on the branch the session cloned.

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

Issues carry a `ready` label once `/ship:ready-issue` has checked them
against the code. The label is a gate the rest of the pipeline trusts, so
it is earned by a pass that greps for every symbol the issue names, not by
someone reading the prose and agreeing with it. The most recent issue
comment titled "Decisions taken" or "Spec addendum" beats the body. PR
bodies carry `Closes #N` on its own line. Commit subjects follow Conventional
Commits, checked by the repo, not by this plugin.
