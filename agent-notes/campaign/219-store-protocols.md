# Issue 219: unused store protocols

## Goal
Delete four unused standalone protocols while retaining their typed WorldStore methods.

## State
Isolated branch `campaign/219-store-protocols`; issue and cleanup workflow read.
Deleted exactly the four standalone declarations (22 lines). Parent owns publication and CI. No local test/typecheck runs or environment changes.

## Decisions and why
Use the active cleanup-refactor control surface. Smallest plan: remove four declaration blocks (about 22 lines), with no new protocols or caller changes.

## Surprises
Tracked search also found three historical plan mentions of ExplanationStore. They are outside production scope and remain historical context.

## Iteration 1: core environment
Read the complete `propstore/core/environment.py`, WorldQuery reads in `world/model.py`, overlay delegation in `world/overlay.py`, bound resolver construction, ATMS runtime construction, app neighborhood consumer, ATMS feed, and existing WorldQuery tests.
The four standalone protocols are dead/test/scaffold surface: their only executable references are their declarations. Disposition: delete their declaration blocks; no dependency edge needs repair.
Keep all other environment symbols: document-backed environment/assumption models and the typed protocol contracts remain in their existing core owner. Keep WorldStore methods and all concrete implementations unchanged; they already own the live capabilities.
No mechanism is moved or recreated. The requested deletion is about 22 lines. Existing WorldQuery tests cover each retained capability, so no duplicate test or new guard is added.
Search gate: `git grep` for the four names must have no production/test hits after deletion; historical plans and this note are outside that scope.
Runtime gates: PR CI, including package Pyright and logged tests; no local CI gate is run.
Search result: zero hits for the four names under `propstore` and `tests`. Final source diff contains only the four deleted blocks. WorldStore retains the four typed methods; WorldQuery and overlay source remain unchanged. `.github/workflows/test.yml` runs package Pyright and the logged full test suite.

## PR draft
Title: Delete unused standalone world-store protocols

Delete four unused runtime protocol declarations from `core.environment`. Preserve their typed methods on WorldStore and leave concrete stores and consumers unchanged.

Closes #219.

Verification: zero production/test references remain for the deleted protocol names. Package typing and logged tests are to be verified by PR CI.

## Next step
Commit the scoped reduction and hand the branch to the parent for publication, CI monitoring, and authorized normal merge.
