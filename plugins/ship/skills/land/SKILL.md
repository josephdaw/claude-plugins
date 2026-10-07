---
name: land
description: Take an open PR to merged (or to a human's queue): wait for CI, run the reviewer, route fixes back to a worker, then merge or hand over under the repo's merge policy, and clean up the worktree. Use after a worker reports a PR.
argument-hint: <pr-number> [pr-number ...] [--rounds N] [--review self|fork]
allowed-tools: Bash(gh:*), Bash(git:*), Bash(python3:*), Agent, SendMessage, Read, Write, Edit, Grep, Glob
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
   spec. Walk every behaviour and acceptance line and name each one the
   PR misses." A missed item is a Must fix.

3. Review. One round, full stop. A re-review only follows a worker fix
   round below, and reads only that fix diff. How deep the one round runs
   depends on what the PR touches.

   Light: the PR changes only documentation, or is a `chore` that touches
   no runtime code. Review inline, one pass, and still post it on the PR
   in the same format, `(inline, <model>)`.

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
   `--review` overrides. Either way the result is a `Review: ` line
   (review-pr's format): APPROVE or CHANGES, Must fix items, Lander fixes,
   Follow-up, Not verified, and a Notes block.

4. Route the findings. CHANGES only when Must fix has an item; Lander
   fixes alone are APPROVE.

   Lander fixes (text only: PR description, code comments, docstrings,
   docs). Land applies every one itself, no worker, no re-review, no
   round spent:
   - A PR description finding: read the current body with
     `gh pr view <n> --json body -q .body`, `Write` it to a scratch file,
     replace only the text the finding names with the reviewer's exact
     wording, then `gh pr edit <n> --body-file <that scratch file>`.
     Never pass a whole new body: `--body` replaces the description
     outright, and the reviewer's wording is for the named text, not the
     rest of it. This scratch file is the only thing land writes outside
     the worktree.
   - A comment, docstring, or docs finding: `Edit` the file in the
     worktree with the reviewer's exact wording, run the ci gate, commit
     with a one-line message naming the finding, and push. Land does
     this itself; it does not dispatch a worker and does not spend a fix
     round.
   - Land never picks the wording; it only applies the wording the
     reviewer already gave. No re-review follows a Lander fix: review-pr
     already marked these "no re-review" because applying exact given
     text is not a design decision. With no Must fix in the verdict, go
     straight to step 5 once every Lander fix is applied.

   Must fix, when any is present, goes to a worker while rounds remain:
   - If the worker that opened the PR is still reachable (a subagent from
     this session), `SendMessage` it: "Review posted on PR <n>. Address
     every Must fix item, rerun the ci gate, push, and report."
   - Otherwise launch a fresh `ship:worker` (Agent tool, subagent_type
     `ship:worker`) with: the worktree path and branch from the PR, the
     review comment text, and the same instruction. It works in the
     existing worktree, never a new one.
   - When it reports, go back to step 1 for CI on the pushed commit, then
     run a re-review: launch the `ship:reviewer` agent (always `fork`,
     never `self`, regardless of what step 3 chose) with "Re-review PR
     <n>. Since your CHANGES review, only commit <old sha>..<new sha>
     changed. Read that fix diff only, in the re-review shape." Count the
     round.
   - Rounds exhausted with CHANGES still standing: stop, report the last
     review, and leave the PR open. Do not merge.

   Both kinds present on the same verdict: send the Must fix items to the
   worker first. Apply the Lander fixes only after the re-review of the
   worker's fix diff comes back APPROVE, so the worker does not race the
   lander editing the same files. Then go straight to step 5; a Lander
   fix applied after an APPROVE re-review needs no further re-review of
   its own.

   The re-review of a Must fix round is not optional and not a skim: it
   is its own diff, read in full, in the re-review shape review-pr
   defines. Reviewing your own fix is not a review, which is why a Lander
   fix (land's own edit) is never re-reviewed by land, only ever applied
   from wording a reviewer already gave.

5. Land, when the verdict is APPROVE and CI is green on the current head
   (after a Lander-fix push, wait for CI on that push):

   Before merging, check nothing moved that neither a reviewer nor land
   itself made. Head first:

   ```
   gh pr view <n> --json headRefOid -q .headRefOid
   ```

   It must equal the sha the approving `Review: ` line names, or that sha
   plus only the Lander-fix commits land pushed in this run
   (`git log <reviewed sha>..<head> --oneline` lists only those). Anything
   else, go back to step 3. Never merge a commit no reviewer has seen.

   Then the description. The reviewer posts a plain PR comment (an
   IssueComment), not a GitHub review (a PullRequestReview), so compare
   the PR's `lastEditedAt` against that comment's `createdAt`:

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

   Find the latest comment whose body starts with the `Review: ` first
   line and read its `createdAt`. If the PR's `lastEditedAt` is later,
   the current body must be exactly the body land last wrote with
   `gh pr edit` in this run. If land made no body edit, or the body
   differs from what it wrote, someone else changed the approved text:
   go back to step 3 and re-review the current description.

   Then the ASCII check on the PR body, when the repo has a copy of the
   script (`.claude/ship/check-ascii.py`; no copy, skip this check):
   `python3 .claude/ship/check-ascii.py --body-file <the body file>`. A
   hit is a Lander fix: replace the character the hit names, write the
   body back, and check again until clean.

   Follow-ups: collect every "Append to #N" and "Suggest: <title>" line
   from every review this PR collected (the main review plus any
   re-review), the Follow-up lines from the worker's report when you have
   it, and any "Not verified" gap that later work must close (a missing
   test, an environment nobody can reach yet). A gap that is only a
   by-hand check the merger can do now goes in the digest, not here.
   - For each "Append to #N", `gh issue comment N` with that one line.
   - Search open issues for the rest
     (`gh issue list --state open --search "<keywords>"`) and append to
     one that fits instead of raising a new one.
   - Raise at most one new issue for this PR, holding every remaining
     Suggest line and qualifying Not verified gap as its body, linked to
     the PR. Never one issue per gap.
   - Under merge policy `human`, do this at handover, below, because no
     later ship step runs on this PR. Under `auto`, do it here, before
     merging.

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
   - merge policy `human`: do the follow-up step above now, then post a
     comment with the digest (below) as the handover comment, in place of
     a plain "Ready for human review" line. Do not merge. Leave the
     worktree. Report the URL for the person to pick up.

## Report

The reader is the person who merges, not the orchestrator. They have
already paid for the full evidence: it is on the PR in the reviewer's
comments and in the session transcript. Do not repeat it. The report is a
digest of what they need to know and what they need to decide, one block
per PR, in this order and this shape:

```
PR #<n> (#<issue>): READY TO MERGE | MERGED | BLOCKED. CI <green|red>, <approved on <sha> | CHANGES after <k> rounds>.

Decisions I made for you (redirect on the issue if wrong):
- <one line per decision the orchestrator made without the human, or "none">

Needs you:
- <one line per action or unmade choice; a choice lists its options in one line each, or "nothing">

Not proven: <one line per gap, with "(in #K)" when it went to the follow-up issue, or "nothing">
Follow-up: appended to #N, raised #K, or nothing
Rounds: <k> worker. Worktree <removed | kept at <path>>. Full detail on the PR.
```

Rules for the digest:

- Five sections, always in that order, every section present even when
  its value is "none" or "nothing", so a missing section reads as an
  omission rather than an all-clear.
- One line per item, about twenty words. No evidence, no counts, no test
  names, no file paths unless the reader must open that file. A count
  belongs in the digest only when it changes what the reader does.
- A decision the orchestrator made in the human's place always appears
  under "Decisions I made for you", including one recorded on the issue
  during the spec-test pass or a fix round. The human cannot redirect a
  decision they were not told about.
- Every unmade choice goes under "Needs you" with its options, one line
  each, and the orchestrator's pick marked. A choice buried in prose is a
  choice the reader misses.
- "Not proven" lists every gap in one line each, with "(in #K)" when it
  went to the follow-up issue. A gap does not need its own issue: most
  gaps are a by-hand check the merger can do now and stay in this line
  only.
- "Follow-up" names what happened to the Append-to and Suggest lines
  this PR collected: which issue got appended, which new issue (at most
  one) was raised, or "nothing" when there were none. The reviewer's NOTE
  items are not repeated here: notes-scan reads them from the PR
  comments.
- No headers, no tables, no bold beyond the section labels.
- Under merge policy `auto`, this digest is the session report. Under
  `human`, it is also the handover comment posted on the PR (step 5).

A PR opened outside this skill (a Talos salvage, a hand-written PR) gets
this skill run on it before anyone is asked to merge. A merge with a Must
fix outstanding is how a known problem becomes an unknown one.

Never merge on a red CI, a CHANGES verdict, or a `human` policy. Never
force-push. Never delete a worktree with uncommitted changes; report it
instead.
