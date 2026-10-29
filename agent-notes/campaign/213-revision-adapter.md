# Delete the unused revision argumentation adapter (#213)

## Goal
Delete the test-only revision-to-argumentation aggregate and partial store proxy.
The active control surface is `protocols:cleanup-refactor`, with issue-delivery.

## State
Deletion implemented on `campaign/213-revision-adapter` in the isolated
`propstore-213` worktree; scoped commit prepared. No publication is authorized
for this worker.

## Decisions and why
Smallest change: delete the 189-line adapter, its eight package import/export
lines, and dedicated adapter tests (458 removed lines, no replacement).
Read the entire adapter, package exports, both caller test files, state owner,
realization owner, ASPIC projection owner, and existing IC-merge realization tests.

Dependency-edge classifications and dispositions, before edits:
- EpistemicState to copied active claims/support DTO and partial store proxy:
  dead/test/scaffold surface; delete the whole adapter file. No production caller
  was found by complete repository text search.
- Package imports and exports to the adapter: deleted old surface; delete those
  imports and exports rather than provide compatibility names.
- Adapter composition and architectural import tests: wrong caller that exists
  only for the old surface; delete the dedicated test file.
- Argumentation-view test cases and their state factories: wrong caller that
  exists only for the old surface; delete the dedicated file.
- The remaining rejected-atom realization assertion in that file: already-owned
  capability that must use its true owner directly. Existing
  `tests/test_worldline_ic_merge_realization.py` tests at lines 135-167 exercise
  dispatch, rejection, support preservation, and the exact same
  `ic_merge_world_false` event reason without the adapter. Delete this duplicate
  test/scaffold; retain those owner tests unchanged.

Target owners remain EpistemicState, revision realization, canonical world query,
and ASPIC projection. This slice creates no revision reasoning workflow.

## Surprises
The issue also names the per-source evidence repair owned explicitly by #139.
That is not achieved by this deletion and is outside this worker's #213 scope.
The ActiveClaim cutover remains #210; no adjacent redesign is included.
Historical plans, inventories, reviews, and workstream baselines mention the old
adapter. They are historical records, not executable callers, and remain intact.

## Verification and next step
Search gates: deleted adapter symbols/imports must have zero hits in production
and tests; inspect all tracked text hits and record historical exceptions.
Runtime gates belong to PR CI: logged revision and ASPIC suites and
`uv run pyright propstore`. No local CI rerun or new regression guard is needed
for removing a test-only surface.

Iteration 1 results: deleted the complete wrong production file first, its
package exports, and both dedicated test files. Exact symbol/import search over
`propstore tests` returned zero matches. Complete tracked text search found only
the historical plans, reviews, inventories and workstream baselines described
above, plus this task note. `git diff --check` passed. Owner tests remain
unchanged. Runtime suites and package typing have not been run locally; they
remain pending PR CI, so this is not a claim of operational acceptance.

Next: supervisor checks the scoped commit, publishes if authorized, and reads
PR CI. The deletion slice has no remaining executable references; #139's
separate evidence repair remains unresolved by this change.

## Draft PR prose (not published)
Title: Delete the unused revision argumentation adapter

Remove the test-only revision argumentation proxy and aggregate, their package
exports, and dedicated tests. Existing revision realization and ASPIC owner
tests remain in place. No replacement adapter or workflow is introduced.

Refs #213. The separate per-source evidence repair remains owned by #139.

Verification: static production/test symbol search returned no matches;
`git diff --check` passed. Logged revision/ASPIC suites and
`uv run pyright propstore` are pending PR CI.
