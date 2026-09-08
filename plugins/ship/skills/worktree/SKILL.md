---
allowed-tools: Bash(git worktree:*), Bash(git rev-parse:*), Bash(git symbolic-ref:*), Bash(git show-ref:*), Bash(git branch:*), Bash(git check-ignore:*), Bash(ls:*), Bash(test:*), Bash(ln:*), Bash(cp:*), Bash(realpath:*), Bash(cd:*)
name: worktree
description: Create a git worktree for feature work in any repo, adopted by ship or not. Inspects the layout, resolves branch, base, and path, and handles gitignored env files by copy, symlink, or skip. Use when asked for a new worktree, or by delegate when a repo has no worktree script.
---

# Create Git Worktree

Create a new git worktree, after inspecting the project layout and asking the user how to handle a few setup decisions. Goal: produce a worktree the user can `cd` into and start working in immediately, without baking in conventions from any specific project.

Use AskUserQuestion for each decision below. Do not batch unrelated questions.

## Step 1: Inspect

Before suggesting anything, gather facts:

- `git rev-parse --show-toplevel` to get the current checkout root.
- `git rev-parse --git-common-dir` to detect whether you are already inside a linked worktree. If the common dir is not `<toplevel>/.git`, you are in a worktree. In that case, the primary checkout is the parent directory of the common dir. Use the primary as the reference point for the rest of these steps.
- `git worktree list` to see existing worktrees and their branches.
- `git rev-parse --abbrev-ref HEAD` for the current branch.
- Detect the default branch: try `git symbolic-ref refs/remotes/origin/HEAD` first. If it fails, check `git show-ref --verify --quiet refs/heads/main`, then `refs/heads/master`. If neither exists, note this and ask the user which branch should be the base.
- `ls` the directory containing the primary checkout. If the primary's directory name is `main`, `primary`, or `trunk`, treat its parent as a wrapper directory (the layout root). Otherwise, the primary's parent is the layout root.
- List `.env*` files at the primary checkout root, then run `git check-ignore` on each. The gitignored ones are what a fresh worktree will be missing.

## Step 2: Resolve the branch name

Start from `$ARGUMENTS`.

- If empty, ask the user for a branch name. Do not proceed without one.
- If the value already contains a `/`, take it as-is (it already carries a prefix).
- Otherwise, ask which prefix to apply. Options: `feat/`, `fix/`, `chore/`, or none. Recommend `feat/` as the default.
- Sanitise the result: lowercase any uppercase letters, replace spaces with hyphens, and reject characters git itself rejects (`~`, `^`, `:`, `?`, `*`, `[`, `\`, control chars, leading or trailing dot, double dots).
- Check whether the branch already exists: `git show-ref --verify --quiet refs/heads/<name>`. If it does, ask whether to attach to the existing branch or pick a different name. If attaching, skip Step 3.

## Step 3: Resolve the base branch

- If the user is currently on the default branch (Step 1), use it as the base without asking.
- If the user is on something else, ask: "Branch from `<default>` (recommended) or from current branch `<current>`?" Recommend the default.

## Step 4: Resolve the worktree path

- The directory name is the branch name with the prefix stripped (so `feat/payments` becomes `payments`).
- Default location: a sibling of the primary checkout, inside the layout root from Step 1. So `<layout-root>/<dir-name>`.
- Show the resolved absolute path with `realpath` and offer the user a chance to override.
- If the path already exists, refuse and ask for a new one.

## Step 5: Resolve env-file handling

For each gitignored `.env*` file found in Step 1, ask the user how to handle it:

- **Copy** (`cp`): the worktree gets its own copy. Edit it freely without touching the primary. Required if you plan to run dev servers in both worktrees at the same time, since each needs its own ports and resources.
- **Symlink** (`ln -s`): the worktree shares the file with the primary. Changes stay in sync. Best when both worktrees should use identical config and you will not run them concurrently.
- **Skip**: the worktree starts without the file. The user populates it before running anything that needs those values.

Recommend copy as the default. Port collisions are the most common foot-gun, and the cost of copying when you could have symlinked is small drift, whereas symlinking when you needed a copy means dev-server conflicts.

If you also notice obvious local-only files at the toplevel (for example `.claude/settings.local.json`, IDE config files), flag them and ask whether to symlink any. Do not act unless the user opts in.

## Step 6: Create

Run the chosen commands.

Attach to an existing branch:
```bash
git worktree add <chosen-path> <existing-branch>
```

Create a new branch from a chosen base:
```bash
git worktree add <chosen-path> -b <chosen-branch> <chosen-base>
```

Then for each env file the user opted into:
```bash
ln -s "<source-abs-path>" "<chosen-path>/<filename>"   # if symlink
cp "<source-abs-path>" "<chosen-path>/<filename>"      # if copy
```

After creation, run `cd <chosen-path>` as your next Bash call so subsequent shell commands operate in the new worktree.

Report back:

- Final absolute path and branch
- Base branch used (or "attached to existing branch")
- Which files were copied, symlinked, or skipped
- Any skipped files the user will need to populate before running anything

## Notes on layout

Sibling worktrees, alongside the primary checkout or in a shared wrapper directory, are generally preferred over nested ones (under `.claude/worktrees/` or similar):

- Tools that walk up from cwd (linters, IDEs, ripgrep) treat each worktree as its own root, with no double-indexing.
- `git status` in the primary checkout stays clean.
- `rm -rf` of a sibling worktree cannot accidentally touch the primary.

Nested worktrees can make sense if the user explicitly wants one rolled-up project root. Ask if unsure.
