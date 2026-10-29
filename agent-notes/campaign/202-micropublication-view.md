# Issue 202: remove the unused micropublication view

## Goal
Deliver issue #202 on branch `campaign/202-micropublication-view`: delete the
test-only subset view and retain canonical family principal-claim coverage.
Publication is reserved to the supervising agent.

## State
Deletion complete; cleanup-refactor is the active control surface. The bounded
production/test search is zero-hit. The seven canonical Clark/principal tests
remain. ATMS constructs its node with the canonical item directly at
`propstore/world/atms.py:1469`; that production path is unchanged.

## Decisions and why
Smallest change: delete the 64-line core module, delete its import and four
view-only tests (about 35 lines), and remove the stale family docstring claim
(three lines). No runtime change or replacement object is needed.

Target owner: `propstore/families/micropublications.py` already owns the canonical
bundle, principal-claim validation, evidence, provenance and artifact/version
identity. `propstore/world/atms.py` imports that class and stores it directly in
`MicropublicationNode`; `propstore/world/queries.py` imports the same charter.

Iteration 1, one slice:
- Core view module/class: dead/test/scaffold surface; delete the entire file.
- Test import and `TestActiveMicropublicationPrincipal`: wrong caller that
  exists only for the old surface; delete that caller path. Its scalar principal
  cases are already covered by `TestPrincipalClaim` against the canonical owner.
- Canonical charter, validation functions and Clark/principal tests: keep.
- Family docstring link to the deleted view: deleted old surface; delete those
  sentences, retaining the principal-claim explanation.

Read: core micropublication module, family micropublication module, entire Clark
test module, ATMS runtime declarations and query imports. Exact production/test
search found no other caller of the view. No move or generic mechanism is needed.

Forbidden search: `ActiveMicropublication|core.micropublications` in `propstore`
and `tests` must have zero hits. Existing canonical ATMS/world tests remain the
runtime evidence; required logged micropublication/ATMS tests and package pyright
are obtained from PR CI, not repeated locally as push gates.

## Surprises
None affecting design.

## Next step
Commit the scoped deletion and provide the supervisor the draft below. No local
test or pyright run: no new test was authored, and CI runs belong on the PR.
Required PR checks are still pending publication.

## Draft PR
Title: Delete the test-only micropublication view

Delete the unused subset view and its four view-only tests. Keep the canonical
Micropublication Clark and principal-claim coverage and remove the stale family
docstring reference. ATMS continues consuming the canonical bundle directly.

Closes #202.

Verification: exact production/test search has no references to the removed
surface. Await PR CI for logged micropublication/ATMS tests and
`uv run pyright propstore`.
