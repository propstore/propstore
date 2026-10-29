# Issue 187 CEL severity

Goal: preserve substrate warnings, checked conditions, and exact locations.

State: bounded CEL admission slice implemented under protocols:cleanup-refactor; focused production-path regressions pass. Not published by this worker.

Smallest design: add one typed generic CEL check result in cel_validation (about 35 lines), replace message-only claim diagnostics with located substrate diagnostics, and make source and claim admission depend only on hard errors (about 45 lines). No dead validation wrappers return.

Broken edges and dispositions:
- condition-ir -> claim conditions: valid capability with wrong representation; rewrite to the generic typed result and retain CelError directly.
- condition-ir -> source authoring: valid capability with wrong representation; rewrite to the same owner result, reject only hard errors.
- claim diagnostics -> family pass: valid capability with wrong representation; rewrite to preserve severity and typed location.
- existing identifier walker: keep; it owns structural identifier traversal and does not decide severity.

Target owner: cel_validation owns generic CEL admission; claim_conditions owns claim location and checked set composition. Substrate owns CelError and checked IR. Forbidden surfaces: message-only CEL reconstruction, diagnostic-list truthiness admission, restored fail-fast wrappers.

Search gate: all production check_cel_expression calls must be in the generic owner. Runtime gate: authored focused regression file through logged pytest wrapper. CI owns broad suites and typing.

Decisions and why: CelError exposes expression, message and is_warning, but no code; retain that object rather than invent a substrate code. PassDiagnostic retains its existing claim.condition code and adds optional typed CEL/location metadata.

Surprises: dead fail-fast wrappers have already been deleted on this campaign branch.

Iteration 1 disposition evidence: retained generic CelCheckResult contains condition-ir CheckedCondition and original CelError tuple. ClaimConditionDiagnostic retains the original object plus tuple position. SourceCelCheck is source-owned location on that same generic result; SourceCelValidationError carries all checks in mixed batches. The obsolete message-only diagnostic surface and diagnostic-list truthiness admission have been removed. No dead wrappers were restored.

Projection edges: valid capability with wrong representation; rewrite existing PassDiagnostic -> BuildDiagnostic -> WorldDiagnosticLine to retain severity and location. BuildDiagnostic detail_json is the existing IO boundary; source expression, message, warning flag, field, and index serialize there. World report retains severity, file and details without parsing rendered text.

Search result: the sole production check_cel_expression call is in cel_validation.check_cel_condition. No blocked=bool(diagnostics) remains in the claim pass.

Focused result: logged wrapper tests/test_cel_severity.py: 8 passed; logs/test-runs/pytest-20261029-005637.log. Covers open/closed and known values, mixed warning/type/parse errors, checked IR equality, claim admission, real activation, typed mixed source rejection, source promotion/build persistence, and world report JSON severity/location. Earlier runs exposed test fixture mistakes (missing observation type; missing explicit diagnostic visibility policy); corrected from actual API source. Broad suites and package typing remain CI-owned.

Next step: parent reviews scoped changes, publishes campaign PR, and reads CI. No acceptance claim is made for broad suites before CI.
