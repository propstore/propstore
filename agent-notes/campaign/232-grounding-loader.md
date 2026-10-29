# Issue #232: delete the raw repository grounding loader

## Goal
Delete the test-only repository scan; retain the typed kernel and the exact
derived-session reconstruction used by compiler and world owners.

## State
Implementation complete locally on `campaign/232-grounding-loader`. Publication
belongs to the parent agent. `issue-delivery` and `protocols:cleanup-refactor` are
active. No push, PR, or merge has been performed by this agent.

## Decisions and why
Smallest change: remove roughly 50 loader/import lines; rewrite the existing
sidecar integration test with roughly 60 lines of explicit expected facts, rules,
superiority, arguments, status, and persisted budget. No new production owner.

Slice read: grounding/loading.py, grounding/bundle.py, grounding/grounder.py,
families/rules.py, compiler/workflows.py, derived_build_plan.py, the complete
world-sidecar test and kernel loading test. Compiler workflows reconstruct the
bundle from the materialized sidecar; world/model.py uses the same loader.

Iteration 1 dispositions:
- Repository -> load_grounding_repo -> GroundingRepo is dead/test/scaffold
  surface. Delete the raw scan and its TYPE_CHECKING/Repository import.
- Parity test -> alternate raw scan is a wrong caller existing only for the old
  surface. Delete this oracle; use explicit expectations over the real build.
- GroundingRepo and build_grounded_bundle are live typed internal kernel objects:
  keep. The explicit issue scope overrides whole-file deletion: the sidecar and
  kernel share this module and are explicitly required to remain.
- load_grounded_bundle_from_sidecar is the already-owned reconstruction
  capability: keep and use directly. No move or new generic mechanism.
- The concept-relation paragraph in the earlier completeness note names the
  wrong loader: rewrite its reference to the verified live sidecar owner.

Search gate: no load_grounding_repo in production or tests; historical references
in completed planning logs remain historical. Runtime gate: actively edited
tests/test_world_sidecar_grounded.py through the logged wrapper. Broader grounding,
compiler/build/world tests and package typing belong to PR CI.

## Surprises
Issue #148 already names the correct live sidecar loader in its current body; no
issue edit is needed. No memory-derived architectural claim is used here.
The first focused run failed because my expected Gunray atom used a nonexistent
`negated` keyword. The installed Gunray GroundAtom type has predicate/arguments
only; the production translator spells strong negation in the predicate. Corrected
the expectation to `~important`; the next logged run passed both tests.

## Verification
- `powershell -File scripts/run_logged_pytest.ps1 --label issue-232 tests/test_world_sidecar_grounded.py -n 0`:
  2 passed, log `logs/test-runs/issue-232-20261028-225250.log`.
- `rg -n 'load_grounding_repo' propstore tests`: zero hits.
- `git diff --check`: clean.
- Kept existing explicit GroundingRepo kernel tests unchanged. Broader tests,
  typing, lint and formatting are deferred to PR CI as instructed.
- The integration test reads typed predicate documents from the same sidecar
  session and compares explicit expectations; it never scans repository families
  to construct a second bundle. All other exact expectations come from seeded
  inputs and the live typed bundle.

## Next step
Parent publishes the committed branch and follows PR CI, then completes authorized
review/normal merge. This issue slice reached the production/test search fixed
point. Historical completed-log references remain outside executable scope.

## Draft PR
Delete the unused raw repository grounding scan and its alternate test oracle.
Assert known predicates, rules, superiority, facts, arguments and persisted budget
through the real compiler-to-sidecar reconstruction path.

Closes #232.

Validation: focused logged sidecar tests passed (2 tests); broader checks via PR CI.
