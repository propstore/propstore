# Checked activation failure propagation

## Goal

Complete the bounded #220 activation slice: runtime activation must consume the checked condition IR and preserve the condition solver's typed failure instead of reparsing claim CEL.

## State

Active control surface: protocols:cleanup-refactor, loaded before production mutation. Isolated campaign/220-checked-activation branch from campaign/209-canonical-detectors. Other agents own detector/caller/fixture files; this slice owns activation.py and one focused behavior test only.

## Decisions and why

Smallest change: delete `_retry_with_standard_bindings` and the Z3TranslationError reparse branch, approximately 30 deleted production lines plus one focused behavior test. Classification: the retry is a wrong caller existing only for the old runtime-CEL surface. Disposition: delete it and let the existing condition-ir typed failure propagate.

Read condition-ir solver.py: its `_require_matching_fingerprint` raises Z3TranslationError for mismatched checked registries; `are_disjoint` consumes CheckedConditionSet. Read registry.py: `with_standard_synthetic_bindings` with no names copies the same registry. Propstore's `_solver_with_environment_bindings` already applies it before the first solver call. A retry cannot supply missing evidence; reparsing changes the evidence instead.

Real caller: BoundWorld activation passes runtime Environment bindings. Adding an environment-only binding extends the query registry, so an existing claim's checked registry fingerprint can mismatch. That mismatch must remain explicit, not become a successful recheck of authored CEL against a new registry.

## Verification

One real-solver behavior regression will use a checked claim and an additional environment binding, expecting the actual Z3TranslationError from condition-ir. No source-shape test, no local CI gates, and no publication.

Reproduced with the actual solver: the focused test failed before deletion because activation returned successfully instead of preserving the mismatched checked-registry failure (`logs/test-runs/pytest-20261029-002041.log`). Deleted the retry helper and reparse branch. The same test then passed (`logs/test-runs/pytest-20261029-002105.log`, one passed). Ordinary unknown-concept ValueError handling remains with its existing owner; Z3TranslationError now propagates directly. No other source files changed.

## Next step

Commit and hand off the bounded activation deletion. Parent owns integration and combined PR CI.
