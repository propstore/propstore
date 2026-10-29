# Canonical detector fixtures (#209)

## Goal
Migrate detector, parameterization and source-applicability tests onto actual canonical Claim documents and compiler admission. protocols:cleanup-refactor remains the active control surface.

## State
Isolated branch campaign/209-canonical-fixtures starts from campaign/209-canonical-detectors. Ownership is tests/test_conflict_detector.py, tests/test_param_conflicts.py, tests/test_source_applicability.py and tests/checked_claim_helpers.py only. All fixture edits are complete. Detector owner is changing production APIs concurrently; no tests run until that owner reports coherent source.

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
Detector owner merges fixture branch, then reports coherent core source. Integrate that source and run only the three actively authored test files through logged wrapper; repair within fixture scope or report verified source defects to the detector owner. No local CI gates or publication.

## Checkpoint
Shared actual compiler helper committed and handed to detector owner for reuse.
Replaced mirror/compact-dict fixtures in detector and parameterization suites with canonical Claim inputs and actual compiler bundle/admissions.
Source-applicability direct fixtures now compile canonical claims; real repository path remains intact.
No tests executed: production detector owner is still completing coherent source.
Next: add absent-value regression, format through editing tool, commit migration and merge coherent core before focused execution.

## Completed fixture slice
The shared helper returns existing ClaimCheckedBundle and CompilationContext after actual form/concept/claim pipelines; it does not synthesize admission tokens or mirror claim fields. Classifier tests supply checked condition sets. Detector tests pass actual normalized documents plus their actual compiler admissions. Invalid equation behavior now asserts QUARANTINED ClaimAdmissionError; missing/stale tokens and categorical/boolean disagreement have canonical behavioral cases. Measure-only MEASUREMENT versus numeric value remains admitted and expects no conflict.

Parameterization fixtures now declare actual typed Claim and ParameterizationEdge objects, with checked forms/units and explicit contexts. Deleted old by_concept input cloning, compact payload factories, mirror mapping assertions, and lifted-clone/cache source inspection. Source tests retain actual bundle reference identity checks and raw quarantine-member coverage.

Search gate found zero ConflictClaim, loose dict[str, Any], payload, lifting-clone or cache references in the four owned files. Formatting changes were generated read-only by Ruff and applied exclusively through apply_patch. No tests or local CI gates have run on this incomplete production base.

## Existing concept fixture owner correction
I added a concept factory in checked_claim_helpers despite the existing canonical_claim_fixtures.concept_with_form owner. The existing owner constructs the same canonical lexical/form evidence; the duplication was unnecessary. Classification: already-owned capability that must use its true owner directly. Disposition: delete the duplicate factory first, then change all three suites to direct concept_with_form calls with explicit canonical names and forms. The source repository fixture now uses the same owner directly too. No alias or wrapper remains. Quantity/frequency form fixtures and actual compiler pipeline invocation remain in checked_claim_helpers. No local CI gate was run for this correction.

## World/ATMS fixture repair batch
Parent assigned shared atms_feed plus world/ATMS/revision fixture owners after PR #377 hosted CI reported raw claims reaching quantitative owners and missing InMemoryWorldStore.claim_admissions. Classification: valid capability with wrong representation at fixture-to-runtime dependency edge. Disposition: compile authored fixture claims through the existing real check_claims owner, retain normalized documents and actual admissions, and declare the fixture's dimensionless concept/form evidence using canonical_claim_fixtures. Preserve conditions, context, scalar values, sample sizes and all behavioral assertions. Direct graph/analyzer fixture claim constructors get the same real compiler boundary. Smallest change is shared feed production plus the two direct claim factories, roughly 70 lines. Other agents own production and merge changes; do not edit their dirty files.

Shared feed now compiles actual authored claims, supplies checked form/concept registry, and exposes actual compiler admissions. Removed manually supplied conditions_ir on Claim fixtures so the claim owner performs that lowering. Direct core-analyzer and world-store claim factories now invoke the same real pipeline. No behavioral assertion changed. Source stability is pending production owner's formatting pass before any focused execution; no local CI gates run.
