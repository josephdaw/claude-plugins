# Coding rules

The rules ship's workers and reviewers hold every repo to. A repo's own
CLAUDE.md wins where the two disagree: repo rules are more specific, and
ship-issue already puts CLAUDE.md first.

## Working rules

How Joe wants code work done. These were learned in earlier sessions and
are repeated here because memory does not carry across workspaces.

- Fix related problems now. Anything found during a task that relates to
  that task gets fixed in the same PR. Only out of scope work, or work
  that needs a planning session, becomes an issue. Never leave a
  should-fix with no owner.
- Deliver the outcome Joe pictured. Say the end state in his words and
  check the plan reaches it. If a simple manual step gets there today
  and the engineered path gets there next week, offer the simple one
  first.
- Ask before spending a metered budget. CI minutes and paid API calls
  are a design constraint, not an afterthought. Measure current spend
  first, give the estimated cost with the plan, and prefer the local
  gate because it is free.
- Check what is installed, not what the source repo says. Plugins run
  from a version-pinned cache, so an edit to a working copy does
  nothing until it is updated and the session restarts.
- Check upstream before building a workaround. A common tool failing at
  a common task is almost always a known bug or a config mistake, not
  something unique about this repo. Search the issue tracker and say
  what was checked.
- Give every subagent an explicit stop condition, and say what is not
  its job. A worker finishes at an open PR with a green local gate. CI
  belongs to the orchestrator. Never let an agent end a turn waiting.
- If an agreed plan has to change mid-task, say what changed and why,
  then let Joe choose. Never quietly swap the target, especially for
  settings, permissions, or anything with a wide blast radius.

## Code Style Preferences

### General Code Style
- Use concise, descriptive variable names
- Prefer explicit imports over wildcard imports
- Always include type hints in Python functions
- Use meaningful commit messages with conventional format
- Prefer functional programming patterns where appropriate

### Python Preferences
- Use Black for code formatting
- Prefer f-strings for string formatting
- Use dataclasses for simple data structures
- Always use virtual environments (.venv)
- Import order: standard library, third-party, local imports

### JavaScript/TypeScript Preferences
- Use const/let instead of var
- Prefer arrow functions for short functions
- Use async/await over Promises.then()
- Use JSDoc on API route handlers when the project uses swagger-jsdoc or similar. This is machine-readable input for documentation generation, not a comment.
- Do not use JSDoc on internal functions. TypeScript types already communicate the contract. Only add a plain comment when a constraint or behaviour cannot be expressed by the signature (for example, "must be called after init()" or a non-obvious return value distinction).

## DRY and Module Design

### No parallel logic
- Before adding a function, find its owner in the ownership map and search for an existing implementation.
- Extract shared logic into a utility or service module rather than copy-pasting.
- If the same behaviour exists in two places, that is a bug waiting to happen. Consolidate it.

### Structure
- File cap: 700 lines, not counting blank lines or comments (or Python
  docstrings). Generated files are excluded. Checked by a test.
- Function cap: 40 lines, from the signature to the end, counted the same
  way. It does not apply to test files, because test frameworks wrap
  whole suites in functions (`describe(() => ...)`). Checked by a test.
- A repo may set a stricter cap in its own CLAUDE.md. It may not set a
  looser one. Checked by a test, against whichever cap the repo declares.
- Ratchet: each repo keeps a baseline of the files and functions over a
  cap on the day the check is added, at their size that day. A baselined
  entry may shrink or be removed, never grow. A new breach fails. A PR
  that raises a baseline number is a FIX. Checked by a test where the
  repo's tool can measure growth, otherwise by review.
- Imports go one way. Each repo writes its layer order in its CLAUDE.md.
  Checked by a test or lint rule.
- The ownership map in each repo's CLAUDE.md lists every module and the
  concerns it owns. A large repo may map folders instead of files, and
  says which in its CLAUDE.md. A new module or folder adds its row in
  the same PR. That every one is listed is checked by a test. That the
  concerns are right is checked by review.
- One concern per module, named for that concern. A layer folder such as
  `utils/` is allowed, but each module in it is named for one concern
  (`utils/dates.ts`, not `utils/helpers.ts`). Checked by review.
- Logic takes data and returns data. Reading and writing (files, network,
  clock, environment) happens at the edges. Tests stub only those edges,
  so code can move without rewriting tests. Checked by review.
- A change that would push a file past its cap splits the file first, as
  its own PR. Checked at spec time.

Each repo enforces the test-checked rules with its own native tools. The
rules file says what is checked, not how.

### Constants and shared values
- Any literal that appears in two or more places, or that has non-obvious meaning, belongs in a dedicated constants or config file.
- Never hardcode the same string or number in multiple files. Import from the single source of truth so naming is mandated consistently.
- No magic numbers or strings inline in logic.

### Folder structure
- Treat `utils/`, `constants/`, `services/`, and `types/` as intentional layers with distinct purposes.
- Business logic belongs in services, not in route handlers, controllers, or UI components.
- Dependency direction flows one way: routes and controllers import from services, services import from utils and constants. Lower-level modules never import from higher-level ones.

## Error Handling

- Validate at system boundaries: user input, external API responses, file reads. These are the only places you cannot trust the data.
- Inside your own codebase, trust your own functions. Let errors propagate naturally rather than wrapping internal calls in defensive try/catch.
- If you catch an error, do one of two things: handle it meaningfully (retry, fallback, user-facing message), or re-throw it. Silent swallowing hides bugs and is almost always wrong.
- Log errors with context: what were you trying to do, and what input or state caused the failure.
- Detached execution contexts are boundaries. Any function that runs outside the call stack of its initiator, a thread, an async task, a scheduled callback, a message-queue handler, or a signal handler, is a top-level entry point. Errors raised there have no caller to propagate to. Wrap the body, log with context, and route the result back to whatever is waiting.
- Asynchronous work must always reach a terminal state. If a piece of state, a loading flag, a pending UI label, a held lock, or an unresolved promise, is set before the work begins, every path including failure must resolve it. Indefinite "in progress" is a bug, not a style choice.
- Install a runtime-level hook for unhandled errors in detached contexts. Most languages and runtimes expose one, an uncaught exception handler, an unhandled rejection event, a thread error hook, or similar. Install it once at startup as a safety net so anything the explicit handlers miss is logged rather than swallowed.

## Commit Message Format

Follow Release Please conventional commits. The full spec, types, and PR description format live in the `ship:commit-format` skill (ship plugin).

## PR scoping and work breakdown

Right-size the work: aim for the fewest pull requests that each ship a coherent, independently-testable slice. Not one giant PR, and not a swarm of tiny ones. Every split has real cost (a CI cycle, a review, a merge, and sequencing overhead per PR), so a split has to earn its place. When in doubt, prefer fewer, more cohesive PRs. Splitting for its own sake is a defect, not diligence.

The primary test is testability. If a change can only be tested once several PRs have all landed, it was one change and should have been one PR. A feature half-built across merges, where the surface dead-ends until the next PR arrives, is the over-splitting failure: nobody can verify the thing as the thing it is until the last fragment lands. Keep a coherent unit of behaviour in one PR so it can be driven end to end.

Split only on a real seam, not on a step boundary:
- Design vs implementation. "Let's rethink how X works" is a different shape from "fix the bug in Y". The design lands as an issue (and a short doc when warranted); the implementation lands as its own PR.
- Different test surfaces. A backend invariant vs the frontend that uses it, or a database migration vs the code on top of it, are genuinely separable because each is verified on its own.
- A true unblocker. A piece several later PRs all depend on, that is itself complete and testable, can ship first.
- One auth boundary, one queue, one migration. A cohesive seam; ship it as one.

Do not split when the pieces are the same surface done in sequence. Absorbing actions into a page, deleting the old page they replace, and relabelling that page are one coherent frontend change, not three PRs. Touching model and API and UI together for a single feature is normal and usually correct, because the feature is only testable as a whole.

Smells that a split is too granular: a PR that cannot be meaningfully tested without its siblings; PRs that must merge in a fixed order to make sense; a "delete the old thing" PR separated from the "build the replacement" PR; relabelling or copy split out from the change that introduced it; more than a couple of PRs all editing the same file.

Smells that a PR is too big: defining new vocabulary and consuming it in unrelated places in the same change; doing an audit and all the fixes it uncovers in one change; stapling an opportunistic "while we are here" cleanup onto something otherwise cohesive.

Process:
- Before agreeing on the work, lay out the proposed PRs as a numbered list, naming the seam each one sits on. Confirm the split before opening anything. If you cannot name the seam, it is one PR.
- Order any split so the smaller pieces unblock the larger one. Tight plumbing first, surface second.
- One PR per issue. When work needs more than one PR, write one issue per PR so nothing gets dropped between merges.
- Do not create parent "epic" issues. They clutter the issue list and do not reliably get closed when the work is done. Carry the overall context in the first issue of the sequence (or a companion doc when the scope warrants) and cross-link the sibling issues from each body.
- Every issue must be detailed enough that a worker agent can ship it from the issue body alone, with no follow-up prompt. Include file paths, line numbers, contract changes, test plan, and acceptance criteria. If background genuinely will not fit inline (a design doc, a long migration plan, a data audit), create a companion `.md` in the repo and link it. Do not create the companion file by default.


- Use TodoWrite for task management on complex tasks

## Documentation

### API documentation
- Use Swagger (via swagger-jsdoc and swagger-ui-express in Node, or similar) for all projects with HTTP endpoints.
- JSDoc on route handlers is the source of truth for the Swagger spec. Keep it accurate and up to date when routes change.
- Swagger UI should be mounted at /docs in development.
- For internal APIs (called only by your own apps or team), do not expose Swagger in production. There is no external consumer who needs it, and a public spec gives an attacker a detailed map of your API surface.
- For public APIs (where third-party developers are the intended consumers), exposing Swagger in production is expected and appropriate. Document the decision explicitly in the project CLAUDE.md.

### Project CLAUDE.md
Every new coding project should have a CLAUDE.md in the root. It is the first file a developer (or Claude) reads to understand the project. Include:

1. **Purpose** - one paragraph describing what the project does and who uses it.
2. **Tech stack** - languages, frameworks, and key libraries. Note any non-obvious choices.
3. **Ownership map** - what you are writing, and which module already owns it. Name the single owner for each write path and shared concern, and flag which rules are lint-enforced. Start the section with "find the existing owner; do not create a parallel implementation". Not a directory tree, `ls` covers that. On a brand new project with no owners yet, a short top-level tree is an acceptable placeholder until the map exists.
4. **How to run it** - setup steps, dev server command, build command, test command.
5. **Environment variables** - list every required variable, what it does, and where to get the value. No actual values in the file.
6. **API documentation** - where Swagger UI is mounted and how to regenerate the spec if applicable.
7. **Key architectural decisions** - anything a developer would get wrong without prior context (for example, why a particular pattern was chosen or what a non-obvious constraint is).
8. **Database** - schema overview or link to migration files. Note the migration tool and how to run migrations.

Keep the CLAUDE.md updated as the project evolves. Outdated documentation is worse than none.
