# Issue 229: delete test-only view-state routing wrappers

## Goal
Remove the three unwired substrate-to-view mappers while retaining ViewState and live report/rendering coverage. Issue #229 is the design authority. Cleanup-refactor is the active control surface.

## State
Read issue #229, AGENTS.md, CLAUDE.md, issue-delivery, cleanup-refactor, view_state.py, app/__init__.py, claim/concept/neighborhood builders, test_view_state_unknown.py, test_render_contracts.py, and the relevant deferred-tests documentation. Isolated branch: campaign/229-view-state-wrappers. Publication is reserved to the campaign owner.

## Decisions and why
Smallest change: delete approximately 110 lines of mapper implementations, imports, and wrapper assertions; correct two documentation descriptions. Keep the enum and existing live report tests. No new protocol, owner, or mapper is needed.

Iteration 1 dispositions:
- view_state.py contains wrong production surfaces: delete the file first; retain only the existing ViewState runtime enum in that same owning module. The enum is a real domain vocabulary, used directly by claim_views.py, concept_views.py and neighborhoods.py.
- Each substrate outcome -> mapper -> test edge is dead/test/scaffold surface: delete mapper, substrate imports, and wrapper-only tests. Exact search finds no production caller beyond definitions.
- Test enum-distinctness -> ViewState edge is valid capability in its correct representation and owner: keep.
- Live builders -> ViewState and report JSON -> enum string edge is already-owned capability: keep direct owner use and existing tests.
- Documentation -> claimed common mapper routing is dead/scaffold framing: rewrite to the actual enum vocabulary and live report ownership.

Forbidden surfaces/search gate: exact mapper names in production, tests and docs. Runtime acceptance belongs to PR CI: logged claim/concept/neighborhood/rendering/context/condition suites and uv run pyright propstore. No local CI gate reruns.

## Surprises
The deferred-tests documentation also claims the disconnected routing is implemented; correct it in the same slice.

## Verification
- Exact mapper-name search over propstore/, tests/, and docs/: zero matches after deletion.
- git diff --check: passed.
- Substantive diff: 11 additions, 122 deletions in three files. ViewState members and enum-distinctness assertions remain unchanged; live builder/render tests remain unchanged.
- No tests or typing checks run locally: this slice removes dead paths and wrapper tests; governing workflow reserves CI steps to the PR. Runtime and typing acceptance remain pending publication.

## Draft PR
Title: Delete test-only view-state routing wrappers

Delete the three unused substrate-to-view mappers and their isolated assertions. Retain ViewState and live report/rendering coverage, and correct documentation that claimed production builders consumed the mappers.

Closes #229.

Verification: exact mapper-name search over production, tests and docs has no matches; git diff --check passes. PR CI must run the logged view/render/context/condition suites and uv run pyright propstore.

## Next step
Commit this fixed-point reduction. Campaign owner publishes campaign/229-view-state-wrappers and follows PR CI; no publication or merge was performed by this worker. No next cleanup slice belongs to #229.
