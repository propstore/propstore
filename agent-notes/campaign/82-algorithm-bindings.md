# Algorithm bindings (#82)

## Goal
Ground all algorithm comparisons in canonical ClaimVariable bindings.

## State
Read app/claims.py, conflict_detector/algorithms.py, world/bound.py,
world/value_resolver.py, families/claims.py and installed ast-equiv comparison.py.
Active control surface: protocols:cleanup-refactor.
Shared projection implemented; app, conflict detection and BoundWorld consume
it. Resolver returns typed inconclusive on invalid bindings. Focused regressions
passed (25 tests); strengthened production BoundWorld resolution test passed
in private environment (8 tests). Package typing remains PR CI work.

## Decisions and why
Smallest complete change: one shared semantic projection accepts the canonical
typed variable tuple and body, rejects ambiguous/incomplete bindings; three
consumers use it. Existing name-before-symbol rule becomes explicit there.
App rejects non-ALGORITHM kinds before comparison. Known values use canonical
concept IDs, as ast-equiv substitutes after ConceptNormalizer.
Estimate: 150 production lines plus focused regression tests.
Forbidden surfaces: detector-local projection, BoundWorld projection loop,
app empty-map comparison and unvalidated known-value keys.
Disposition: duplicate projection edges are already-owned capability: rewrite
to shared semantic owner. No family-specific mechanism is moved into a family.
Search gates target these old loops and empty app maps. Focused authored tests
use the logged wrapper; package typing and remaining checks run on PR CI.

## Surprises
App checks body presence rather than canonical ClaimType.
Initial test command incorrectly reused main environment, changing editable
install. Restored main editable with uv sync, then restored all 90 pruned
non-propstore packages to exact logged versions with uv pip install. Verified
main direct_url points to main checkout. Subsequent tests use private .venv.
Parent review identified detector's broad ValueError catch swallowing the new
typed binding failure. Re-raise AlgorithmBindingError explicitly; malformed
detector regression covers the failure contract.
Final focused binding/production-consumer file: 9 passed in private environment,
logged at logs/test-runs/pytest-20261028-234106.log. Forbidden projection search
returned zero matches in app, BoundWorld and detector slice.

## Next step
Commit scoped implementation; parent publishes and reads PR CI.
