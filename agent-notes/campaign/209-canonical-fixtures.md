# Canonical detector fixtures (#209)

## Goal
Migrate detector, parameterization and source-applicability tests onto actual canonical Claim documents and compiler admission. protocols:cleanup-refactor remains the active control surface.

## State
Isolated branch campaign/209-canonical-fixtures starts from campaign/209-canonical-detectors. Ownership is tests/test_conflict_detector.py, tests/test_param_conflicts.py, tests/test_source_applicability.py and tests/checked_claim_helpers.py only. Detector owner is changing production APIs concurrently; no tests run until that owner reports coherent source.

## Decisions and why
Smallest full change: delete mirror constructors and compact dict fixture conversion, use canonical Claim constructors, and invoke the real form/concept/claim compiler pipelines in a shared test helper returning existing ClaimCheckedBundle plus CompilationContext. Estimate roughly 650-850 test lines replacing roughly 1,000 lines, plus a small shared pipeline fixture owner. No field-compatible adapters, payload conversion, or forged admissions.

Classifications/dispositions before editing:
- ConflictClaim constructors/field mapping assertions: deleted old surface; delete mapping scaffold, rewrite behavioral comparisons to canonical compiler output.
- Compact claim/parameterization dict helper edges: valid capability with wrong representation; delete helpers and construct canonical typed Claim/ParameterizationEdge directly.
- Raw CEL classification fixtures: valid capability with wrong representation; use checked_condition_set/check_condition_ir and actual ConditionSolver.
- Synthetic lifting clone/cache source assertions: dead/test/scaffold surface; delete. Preserve actual context behavior through typed LiftingSystem tests.
- Invalid equation parse-skip expectation: wrong caller existing only for old surface; replace with canonical quarantined admission boundary failure assertion.
- Existing unit/error/source behavior: valid capabilities; retain through real admission and quantitative/condition owners.

## Surprises
The prior #208 worktree was already cleaned up after merge; no dirty work was lost. New tests must use #145's real form-aware quantitative admission rather than instantiate numerical claim subsets.

## Next step
Write shared real compiler fixture and migrate the three owned suites; notify detector owner when edits are complete, then integrate coherent source for focused test execution.
