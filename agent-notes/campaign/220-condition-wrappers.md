# Issue 220: delete test-only condition solver wrappers

## Goal
Delete the two uncalled claim solver wrappers and their wrapper-only tests.
The active control surface is protocols:cleanup-refactor, with issue-delivery.

## State
Deletion complete on branch `campaign/220-condition-wrappers`; publication is
reserved to the supervising agent. No production caller used either wrapper.
The four retained tests passed through the logged wrapper; exact wrapper-name
search has no matches in production or tests. `git diff --check` passes.

## Decisions and why
Smallest change: remove roughly 95 lines across claim_conditions.py and its test
file; correct the module description. No replacement API or new owner is needed.

Iteration 1 dispositions:
- `claim_condition_satisfiability` and `claim_conditions_disjoint`: dead/test/scaffold
  surface; delete. They recheck authored CEL and discard diagnostics.
- Their three solver-only tests and timepoint fixture: dead/test/scaffold surface;
  delete, including now-unused solver imports.
- `ClaimConditionDiagnostic`, `ClaimConditionReport`, `check_claim_conditions`,
  `check_claim`, `serialize_checked_conditions`, `compile_checked_conditions`:
  keep. These are the existing claim checking/report/serialization owner boundary.
- Conflict classification already calls `are_disjoint_result` directly in
  `propstore/conflict_detector/condition_classifier.py`; activation and ATMS use
  `compile_checked_conditions`. No caller rewrite or capability move is required.

Target: package-owned checked condition sets and solver outcomes; retain checking,
diagnostic, codec, and backend-composition tests. Forbidden: either deleted wrapper
or a replacement facade. Search gate: exact wrapper names in propstore and tests.
Runtime checks belong to PR CI; only the edited test file may be run locally via
the logged wrapper. CI must cover claim conditions/conflict/defeasibility and
`uv run pyright propstore`.

## Surprises
Current exact search finds four call expressions across three tests, rather than
the issue's older count of three calls. All are confined to the same test file.
The issue's broad no-runtime-reparse description is not true repository-wide:
`propstore/conflict_detector/condition_classifier.py` checks authored CEL in its
existing `_z3_classify` path. This task leaves that independent path unchanged;
the wrapper deletion cannot establish the broader acceptance claim. Supervisor
has confirmed that #209 owns the canonical checked conflict inputs. Full #220
acceptance remains dependent on that work; do not close #220 from this deletion.

## Next step
Supervisor publishes the scoped commit, reads PR CI, and preserves #209's
ownership. No further deletion slice remains for these two wrappers.

## Verification
`powershell -File scripts/run_logged_pytest.ps1 --label issue-220 tests/test_claim_conditions.py -q`
passed: 4 tests. Log: `logs/test-runs/issue-220-20261028-225955.log`.
Broader CI and package typing were not run locally, per repository instructions.

## Draft PR
Title: Delete test-only claim condition solver wrappers

Remove the two uncalled claim solver convenience functions and their three
wrapper-only tests. Keep the claim checking, diagnostic retention, codec
round-trip, and condition-ir backend composition tests.

Refs #220. The broader canonical conflict-input work belongs to #209 and is
required before claiming #220's repository-wide no-reparse acceptance criterion.

Validation: logged `tests/test_claim_conditions.py` run passed all 4 retained tests.
PR CI remains required for the broader checks and package typing.
