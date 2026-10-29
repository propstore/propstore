# Issue 221: delete claim-equation facade

## Goal
Delete the facade and its isolated tests; compose the package-owned BoundEquation directly in the conflict collector. protocols:cleanup-refactor is the active control surface.

## State
Read issue 221, AGENTS.md, CLAUDE.md, issue-delivery and cleanup-refactor skills, the complete facade/collector/equation detector, and equation production-path tests. Branch campaign/221-equation-facade starts from origin/master; parent publishes.

## Decisions and why
Smallest change: delete two files (about 95 lines), replace the collector call with the package constructor (two lines changed), and add about 35 lines of focused detector coverage. No detector outcome redesign.

Iteration 1 classification and disposition:
- Facade compare_claim_equations and its test-only callers: dead/test/scaffold surface; delete entire production and test files. Shared bindings are not a real claim comparison interface.
- Collector dependency on bound_equation: already-owned capability that must use its true owner directly; construct eq_equiv.BoundEquation with the existing claim-specific expression and bindings. No moved helper.
- Detector compare_equations call: keep direct package call with independent per-claim binding construction. Existing equivalent, different and domain-sensitive tests remain.
- PLAN.md current architecture reference: deleted old surface; update the reference to the actual collector owner. Historical reports remain historical.

Target owner is eq_equiv.BoundEquation; forbidden surfaces are the deleted facade module and both wrapper names. Search gate is tracked-text search for these names; historical reports and this note are outside production scope. Runtime gates: authored tests/test_conflict_detector.py via logged wrapper; package Pyright and remaining checks through PR CI.

## Surprises
The assigned worktree did not exist; created the delegated branch/worktree. Existing detector tests cover equivalent, different and unknown outcomes but do not cover independent symbol sets or package parse failures.

## Verification
- Deleted the complete facade and isolated test file, then replaced the classified collector edge with direct package construction. Detector comparison code remains unchanged.
- `powershell -File scripts/run_logged_pytest.ps1 tests/test_conflict_detector.py -q`: 27 passed. Log: logs/test-runs/pytest-20261028-225659.log. This was the actively authored test file, using this worktree's own environment.
- Inspected the installed pinned eq_equiv/comparison.py: BoundEquation owns expression/variables; compare_equations returns INCOMPARABLE when either normalization is EquationFailure. Real malformed-equation tests exercise this package failure on both sides, and require the detector's warning.
- Tracked-text search leaves only the historical code inventory's distinct bound_equation_from_conflict_claim name outside this note. No deleted facade names remain in production or tests.
- Package Pyright and other CI checks await parent publication; not rerun locally.

## PR draft for parent
Title: Delete the test-only claim equation facade

Delete the unused shared-binding comparison facade and its isolated tests. The conflict collector now constructs eq-equiv's BoundEquation directly for each claim; the detector continues comparing independently bound equations through the package.

Preserve equivalent, different and domain-sensitive production tests, and cover independently named symbols plus package parse failures on either side.

Closes #221.

Validation: logged tests/test_conflict_detector.py run: 27 passed. Package typing and remaining checks run in PR CI.

## Next step
Commit the scoped reduction, then parent publishes, reads PR CI (including package Pyright), and completes authorized review/merge. No source dependency on adjacent claim-model issues.
