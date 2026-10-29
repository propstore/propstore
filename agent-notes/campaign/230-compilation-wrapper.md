# Issue 230: compilation context wrapper

## Goal
Delete the partial repository compilation wrapper and all callers. Local implementation only; supervisor owns publication.

## State
Implementation complete; cleanup-refactor is the active control surface. All 109 tests in the four edited test files passed through the logged wrapper. Publication remains with supervisor.

## Decisions and why
Smallest change: delete the roughly 60-line wrapper and its imports; delete the redundant repository-loading unit test, construct explicit empty checked inputs, and use the existing public compile_repository_checked_bundle for repository integration callers. Expected net reduction about 90 lines across five code/test files.

Target owner: CompilationContext/build_compilation_context for already checked input; compiler.workflows.compile_repository_checked_bundle for complete repository compilation at an explicit commit.

Classification and disposition, before edits:
- context.py wrapper edge: dead/test/scaffold surface; delete. Retain live typed constructor and claim indexing in their current owner.
- compilation-context repository-loading test: wrong caller that exists only for the old surface; delete. Existing checked-input test retains form/concept coverage.
- None fallback test: dead/test/scaffold surface; rewrite to explicitly empty checked concept inputs.
- source promotion condition registry edge: already-owned capability that must use its true owner directly; use the checked repository compiler output pinned to promoted head.
- parameter-unit test edges: already-owned capability that must use its true owner directly; use full checked compilation output directly, without a replacement helper.
- equation invalid-form edge: already-owned capability that must use its true owner directly; assert CompilerWorkflowError from public validation owner.

Forbidden surface: partial repository reader, optional repository fallback, replacement wrapper/alias or duplicated family scan.
Search gate: complete tracked-text search for build_compilation_context_from_repo, with historical task notes recorded as nonproduction hits.
Runtime gates: actively edited test files through logged wrapper; compiler workflow and package typing remain PR CI checks.

## Surprises
Issue inventory is stale: parameter-unit and equation-dimension tests also call the wrapper. These are in scope because the acceptance criteria remove every caller.

## Next step
Supervisor publishes branch and obtains compiler-workflow, typing and remaining required PR CI. No push performed by worker.

## Iteration 1
- Deleted partial context builder and imports; retained CompilationContext, checked constructor and claim index unchanged.
- Removed partial-loader scaffold test and rewrote empty-input coverage using run_concept_pipeline plus the checked constructor.
- Promotion and unit-admission callers consume compile_repository_checked_bundle directly; promotion uses explicit promoted HEAD snapshot.
- Invalid-form test now exercises validate_repository and typed CompilerWorkflowError.
- Tracked-text search: no production or test hits for deleted symbol. Remaining hits in docs/gaps.md:48 and docs/rewrite/deferred-tests.md:626 are historical documentation outside production scope; no replacement scanner or alias was added.
- Runtime result: powershell -File scripts/run_logged_pytest.ps1 --label issue-230 tests/test_compilation_context.py tests/test_source_promote_p83b.py tests/test_parameter_unit_admission.py tests/test_equation_dimension_admission.py -q — 109 passed in 22.27s; logs/test-runs/issue-230-20261028-225307.log.
- Package typing and untouched compiler-workflow test gates deferred to PR CI under governing instructions. No local CI gate rerun.
- Requested production slice reached fixed point; no further implementation slice.

## Draft PR
Title: Delete partial repository compilation context wrapper

Delete the test-only partial repository compiler. Unit coverage uses checked owner outputs; integration tests use the full compiler workflow and its typed diagnostics.

Closes #230.

Validation: 109 tests passed across the four edited test files through the logged wrapper. Remaining compiler workflow and typing checks belong to PR CI.
