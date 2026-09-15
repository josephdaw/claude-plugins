---
name: land
description: Take an open PR to merged (or to a human's queue): wait for CI, run the reviewer, route fixes back to a worker, then merge or hand over under the repo's merge policy, and clean up the worktree. Use after a worker reports a PR.
argument-hint: <pr-number> [pr-number ...] [--rounds N] [--review self|fork]
allowed-tools: Bash(gh:*), Bash(git:*), Agent, SendMessage, Read, Write, Grep, Glob
---

Land each PR in `$ARGUMENTS`. Run independent PRs in parallel. `--rounds`
caps fix rounds; default 2. `--review` forces where the review runs; by
default land decides per PR (step 3).

Read the repo's CLAUDE.md `## Harness` section first for merge policy,
default branch, and ci gate. Missing: stop and say to run `/ship:adopt`.

## Per PR

1. CI. `gh pr checks <n> --watch`. If CI fails, skip to the fix round
   with the failing job's output as the finding. Do not run the reviewer
   on a red PR; it wastes an opus call on something the worker can see.

2. Spec drift. The brief was a snapshot. Compare the issue's `updatedAt`
   and its latest comment time (`gh issue view N --json updatedAt,comments`)
   with the PR's `createdAt`. If the issue changed after the PR was opened,
   or after the worker was briefed if you know that time, tell the reviewer
   in its prompt: "Issue N was edited after the brief. The live body is the
   spec. Walk every What to build, Test plan, and Acceptance item and name
   each one the PR misses." A missed item is a FIX.

3. Review. How deep depends on what the PR touches.

   Light: the PR changes only documentation, or is a `chore` that touches
   no runtime code. Review inline, one pass.

   Full: everything else, with no exceptions carved out for a small diff.
   Size is not risk. A one-line change to order placement outranks a
   thousand lines of docs.

   Start coarse and only split the full tier further if it proves too slow
   in practice, which is a measurement, not a guess.

   One checklist, `/ship:review-pr`, two places to run it:
   - `self`: you follow the checklist here, in your own context. Cheap
     when the diff is small and your context is already warm.
   - `fork`: launch the `ship:reviewer` agent (Agent tool, subagent_type
     `ship:reviewer`) with "Follow /ship:review-pr for PR <n>". Fresh
     context on opus, so it does not share the blind spots of the session
     that briefed the work.
   Default `fork`. Choose `self` only when all of these hold: under about
   150 changed lines (`gh pr diff <n> --stat`), no file under an auth,
   permission, proxy, schema, migration, payment, or payroll path, and no
   new route or external call. Say which you chose and why in the report.
   `--review` overrides. Either way the result is a VERDICT line.

4. Fix round, when the verdict is CHANGES or CI is red. First sort the
   FIX items:

   - Text finding: the PR description, or a comment or docstring, where
     the reviewer's own finding states the correct wording and the fix
     needs no other code change. A text finding whose correct wording
     the reviewer did not give is not a text finding: treat it as code.
   - Code finding: any FIX that is not a text finding, including a red
     CI.

   When every FIX in the verdict is a text finding, land applies the
   wording itself instead of spending a round:
   - A PR description finding: read the current body with
     `gh pr view <n> --json body -q .body`, `Write` it to a scratch file,
     replace only the sentence the finding names with the reviewer's
     wording, then `gh pr edit <n> --body-file <that scratch file>`.
     Never pass a whole new body: `--body` replaces the description
     outright, and the reviewer's wording is for the named sentence, not
     the rest of it. This scratch file is the only thing land writes; it
     is not a file in the repo the PR touches.
   - A comment or docstring finding: that file lives in the repo, and
     land's own allowed-tools have no `Edit` and no way to run an
     arbitrary repo's ci gate, so land does not touch a repo file itself.
     Instead it sends the reviewer's exact wording to a worker (the one
     that opened the PR if reachable, else a fresh `ship:worker` in the
     existing worktree at the PR's branch and path, never a new one)
     with: "Make only this edit: <the finding and the reviewer's
     wording>. Run the ci gate, commit with a one-line message naming
     the finding, and push. Do not touch anything else." This does not
     spend a fix round: the worker is applying wording land and the
     reviewer already settled, not designing a fix.
   - Either way, land never picks the wording; it only applies, or has
     applied, the wording the reviewer already gave. Land still made the
     change, so it cannot approve it: the fork re-review below is
     mandatory, and step 5 still checks the head and the description
     against what was actually approved before any merge.
   - Go back to step 1 (CI on the pushed commit, when there was one).
     Then run the re-review as `fork` always, never `self`, regardless of
     what step 3 chose for the earlier review: land wrote or dispatched
     this edit, so it cannot also be the one who approves it. Launch the
     `ship:reviewer` agent with "Re-review PR <n>. Since your CHANGES
     review, only <the description edit | commit <sha>> changed. Walk
     the whole description again."
   - Track text passes and worker rounds as two separate tallies. A text
     pass never counts toward the round cap. Two text passes in a row
     still coming back CHANGES stops the PR on that verdict, the same as
     running out of rounds, but it does not spend or block a worker
     round: if a later CHANGES verdict on this same PR has a code
     finding, it still goes to a worker while rounds remain, unaffected
     by how many text passes came before it.

   Any other FIX (a code finding, or a text finding mixed with a code
   finding) goes to a worker while rounds remain:
   - If the worker that opened the PR is still reachable (a subagent from
     this session), `SendMessage` it: "Review posted on PR <n>. Address
     every FIX, rerun the ci gate, push, and report."
   - Otherwise launch a fresh `ship:worker` (Agent tool, subagent_type
     `ship:worker`) with: the worktree path and branch from the PR, the
     review comment text, and the same instruction. It works in the
     existing worktree, never a new one.
   - When it reports, go back to step 1. Count the round.
   - Rounds exhausted with CHANGES still standing: stop, report the last
     review, and leave the PR open. Do not merge.

   The re-review is not optional and it is not a skim, on either path. A
   fix changes what merges, whether a worker wrote it or land applied the
   reviewer's own wording, so the previous verdict describes a commit or a
   description that no longer exists. Review the new head, or the edited
   description, as its own diff, including any commit the orchestrator
   wrote itself. Reviewing your own fix is not a review.

5. Land, when the verdict is APPROVE and CI is green:

   Before merging, check the commit you are about to merge is the one that
   was reviewed:

   ```
   gh pr view <n> --json headRefOid -q .headRefOid
   ```

   It must equal the head the APPROVE was given on. If it moved, for any
   reason, go back to step 3. Never merge a commit no reviewer has seen.

   Then check the description itself has not moved since the approving
   review. The reviewer posts a plain PR comment (an IssueComment), not a
   GitHub review (a PullRequestReview), so compare the PR's
   `lastEditedAt` against that comment's `createdAt`:

   ```
   gh api graphql -f query='
     query($owner:String!,$repo:String!,$n:Int!) {
       repository(owner:$owner,name:$repo) {
         pullRequest(number:$n) {
           lastEditedAt
           comments(last: 20) { nodes { author { login } body createdAt } }
         }
       }
     }' -F owner=<owner> -F repo=<repo> -F n=<n>
   ```

   Find the latest comment whose body starts "Review by ship:reviewer" and
   read its `createdAt`. If the PR's `lastEditedAt` is later, the approved
   text is not the text about to be merged: go back to step 3 and
   re-review the current description.

   - merge policy `auto`: read the current description with
     `gh pr view <n> --json body -q .body` into a file, then
     `gh pr merge <n> --squash --delete-branch --subject "<PR title> (#<n>)" --body-file <that file>`.
     The subject is the PR title plus ` (#<n>)`; confirm the title is in
     Conventional Commits form before merging, since the release tooling
     reads it. The body is the PR description read at merge time, verbatim
     (no trailers such as Co-Authored-By carried over from branch commits;
     the description is the record). Then from the primary checkout
     `git pull`, remove the worktree (`git worktree remove <path>`, then
     `git branch -d` if it survives), and confirm the linked issue closed
     (`gh issue view N --json state`). If it did not, close it with a
     comment naming the PR.
   - merge policy `human`: post a comment "Ready for human review. CI green,
     ship:reviewer approved, see review above." Do not merge. Leave the
     worktree. Report the URL for the person to pick up.

## Report

One block per PR:

```
PR <n>: merged | awaiting human | blocked after <k> rounds and <t> text passes
Issue: #N closed | still open (why)
Review: APPROVE | CHANGES, <FIX count> FIX, <DEFER issue numbers>, by self | fork (why)
Worktree: removed | kept at <path>
```

Then one line listing the reviewer's NOTE items, so the weekly scan can
find them, and confirming every DEFER has an issue number.

A PR opened outside this skill (a Talos salvage, a hand-written PR) gets
this skill run on it before anyone is asked to merge. A merge with a FIX
outstanding is how a known problem becomes an unknown one.

Never merge on a red CI, a CHANGES verdict, or a `human` policy. Never
force-push. Never delete a worktree with uncommitted changes; report it
instead.
