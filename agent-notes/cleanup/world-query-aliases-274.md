# Issue #274: WorldQuery delegation aliases

## Goal
Remove the six test-only delegation aliases; WorldQuery calls the existing public module functions directly. Active control surface: protocols:cleanup-refactor.

## State
Implementation complete in isolated branch cleanup/world-query-aliases-274; local substantive commit prepared. Parent agent owns publication and CI.

## Decisions and why
Smallest change: delete the alias block, replace six call names, delete the identity-only test and its imports; about 45 removed lines and six changed calls. No new production interface or test guard.

Source evidence: propstore/world/model.py:131-337 defines compiled_graph, active_graph, bind, intervene, observe, and chain_query as WorldStore-based semantic owners; :375-384 only assigns second spellings. WorldQuery methods at :845-903 forward typed arguments and lifting behavior. tests/test_world_query.py:378-397 exercises compiled graphs, binding, chaining, intervention and observation; :400-408 asserts alias identity only.

Dependency-edge dispositions:
- All six WorldQuery method -> private alias -> public function edges: already-owned capability that must use its true owner directly; rewrite calls to public owners with arguments unchanged.
- Six alias declarations: deleted old surface; delete.
- Identity test and its imports of private and public functions: dead/test/scaffold surface; delete. Public imports serve only this test.
- All other model functions and reader methods: keep as existing owners outside the explicitly requested alias slice. Issue #274 explicitly preserves the module and owners; deleting the whole file would exceed scope.
- Behavioral tests: keep; sharpen the existing binding test to call WorldQuery.active_graph directly and assert the fixture's active claim IDs. The existing binding path calls the free active_graph owner internally, so it did not exercise the reader's active_graph method itself. This is real reader behavior, not an alias assertion.

## Surprises
The whole-tree exact-symbol search also finds BoundWorld._active_graph, a distinct instance field owning the bound graph (bound.py:197,245,264-265). It is outside the forbidden module alias surface and remains.

## Next step
Aliases deleted first and classified caller edges rewritten. Exact-symbol search in model.py and test_world_query.py is zero-hit; full-tree matches only the unrelated BoundWorld field. Diff preserves every forwarded argument. Logged edited test file passed: 43 passed in 17.83s, logs/test-runs/pytest-20261028-205100.log. git diff --check passed. Package typing and broader runtime tests remain parent-published PR CI work. Requested alias slice has reached source fixed point; next step is parent publication and CI.

## Draft PR body
WorldQuery now calls the existing module-level query owners directly. Remove the six private delegation aliases and the test that only asserts alias identity; retain the production-path behavioral tests.

Closes #274.

Validation: edited tests/test_world_query.py passed through the logged wrapper (43 tests); remaining PR CI includes world-model tests and package typing.
