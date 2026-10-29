# Per-source support evidence (#139)

## Goal
Preserve exact per-source evidence for claims sharing one assertion, and keep current assertion support alternatives distinct. The deleted test-only argumentation adapter remains deleted (#213).

## State
The cleanup-refactor protocol is the active control surface. Read state, projection, realization, entrenchment, history, canonical label owners, worldline bridge tests and fixture constructors.

## Decisions and why
Smallest complete plan: replace the parallel source_claims/label fields with typed source-support witnesses carrying the claim, original label, current label, quality and essential support. Keep BeliefBase.support_sets as current assertion alternatives. Incision removes environments from both current owners, retaining original witness evidence. A source without surviving support stays inactive even when another source keeps the assertion active. Approximately 250 production/test lines plus migrated test callers.

Dependency classification and disposition:
- AssertionAtom parallel source/label edge: valid capability with wrong representation; rewrite to typed source evidence in the existing state owner.
- primary_source_claim: dead surface; delete.
- Projection/entrenchment/realization/snapshot callers: valid capability with wrong representation; consume witness/current assertion owners directly.
- History provenance encoding: IO-boundary-only carrier; encode the typed witness collection at that boundary.
- Test constructors and worldline oracle comprehensions: valid capability with wrong representation; rewrite to the typed owner.
- af_adapter: deleted old surface; keep absent, per #213.

## Surprises
No production adapter consumer survives. Current stabilization preserves all pre-incision support sets, and realization derives claim IDs from the original atom inventory; both need the current evidence owner.

## Next step
Complete focused regression validation and commit the slice. Parent owns publication and CI.

## Iteration 1
- Deleted the parallel fields and first-source property; projection now creates one typed witness per claim, with original and current labels kept separately.
- Entrenchment reads current assertion support_sets. Realization and snapshot-to-claim projection read only surviving source witnesses. Incision filters current labels and current assertion alternatives.
- Migrated every existing support-revision constructor/oracle. Adapter remains absent.
- Logged authored/migrated test run: 40 passed, one diff/apply regression failed. Raw probe showed current base.assumptions loses the incised x assumption, but dependency deltas omitted assumptions. Classified that edge as IO-boundary-only carrier and extended the existing dependency diff/apply owner to encode its current assumptions.
- Next: rerun authored tests and add real replay/IC/worldline acceptance for distinct source evidence.

## Iteration 2
- First vertical slice committed on campaign/139-source-support; eight focused source-support tests pass after the diff repair.
- Added production BoundWorld contraction, worldline journal capture/replay/repository persistence and IC selected-world tests with two disjoint sources sharing one assertion.
- The existing owners perform these workflows directly; no new adapter or generic mechanism is needed.
- Source contract verified: BoundWorld.claim_support returns EXACT only with a label; unconditional evidence is Label.empty(). Removed the unsupported absent-label active policy and made synthetic unconditional fixtures explicit.
- ATMS essential_support is the intersection of compatible environments. Assertion essential evidence now intersects current alternatives; original per-source essential evidence remains unchanged. Current environments alone decide source survival, without a second stale essential veto.
- Added repeated-incision and unconditional-label regressions. Integration run before these final refinements passed all 11 tests, including replay and repository persistence.
- Final semantic run: 46 passed across the authored source-support file and migrated bound-world/history/worldline files; log logs/test-runs/source-support-139-final-20261028-234231.log.
- Search gate: no source_claims or primary_source_claim remains in propstore/support_revision. The af_adapter remains deleted. Applied formatting through apply_patch; package typing and remaining full checks belong to parent PR CI.
- No implementation prerequisite remains. Parent should inspect the local branch, publish it, read CI and handle normal merge/issue closure under existing campaign authority.
- Parent removed the source-shape AST test: the issue requests a static search,
  not a new persistent guard. Behavioral regressions remain; hosted CI validates
  the final tree. Earlier 46-test evidence includes the now-removed guard.
