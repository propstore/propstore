# Issue 236: extraction reference echoes

## Goal
Delete the two test-only canonical-reference echoes without changing extraction or promotion.

## State
Cleanup-refactor is the active control surface. Isolated branch: `cleanup/extraction-ref-echoes-236`.
Smallest change: delete two functions and exports (about 14 lines), replace the two echo-dependent absence assertions with direct canonical-family emptiness assertions (about 14 lines removed).

## Decisions and why
Read both extraction modules, both lifecycle tests, `proposals_predicates.py`, `proposals_rules.py`, and the predicate/rule family definitions. Typed proposal refs and family placement already own proposal addressing; promotion plans and canonical charters own canonical writes.

Iteration 1 classification and disposition:
- Raw model string -> `canonical_predicate_ref` -> test: dead/test/scaffold surface; delete the echo, export, and echo-dependent assertion.
- Raw model string -> `canonical_rule_ref` -> test: dead/test/scaffold surface; delete the echo, export, and echo-dependent assertion.
- Canonical non-mutation assertion: already-owned capability that must use its true owner directly; assert empty canonical family refs using its existing `iter_refs()` interface.
- Remaining extraction, typed proposals, branch/transaction/dry-run/rejection coverage, and promotion owners: keep unchanged. The files contain valid extraction behavior, so this bounded symbol deletion does not delete their owning files.

## Surprises
None affecting scope. Predicate promotion has a private identity echo outside this explicitly bounded issue; it is not changed here.

## Verification
Search gate: no `canonical_predicate_ref` or `canonical_rule_ref` references in production/tests after deletion.
Runtime gate: run only the two modified lifecycle test files via logged wrapper. Package typing and broader checks belong to PR CI, not a local push gate.

## Draft PR
Title: Delete test-only extraction canonical-reference echoes
Body: Removes the predicate/rule extraction identity echoes and their exports. Lifecycle tests use canonical-family refs directly to retain non-mutation coverage; proposal refs, extraction reports, promotion planning and canonical family owners remain unchanged. Fixes #236.

## Next step
Bounded deletion complete and prepared for local commit. No publication authorized for this agent. Parent campaign owns publication and PR CI.

## Gate results and commit
- Search gate: zero production/test hits for either deleted function name.
- Logged modified lifecycle tests: 4 passed; `logs/test-runs/pytest-20261028-205955.log`.
- No replacement identity surface was added. Direct canonical family enumeration covers the preexisting non-mutation assertion.
- Local commit message: `Delete test-only extraction canonical-reference echoes`.
- Fixed point reached for this issue's two-symbol slice. Package typing has not run locally; PR CI remains outstanding.

## Checkpoint
- Deleted both echo functions and exports; direct family-ref absence assertions preserve non-mutation coverage.
- The logged two-file lifecycle run is active in this isolated worktree.
- The wrapper created a worktree-local environment successfully.
- Next: inspect test results, search for forbidden references, and commit locally.
