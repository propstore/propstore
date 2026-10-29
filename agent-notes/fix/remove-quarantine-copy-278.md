# Issue #278: remove the unused diagnostic copy

## Goal

Keep one canonical diagnostic collection on SidecarBuildPlan. Delete the unused
transient-carrier copy while preserving dangling-reference lowering and blocking
diagnostic behavior.

## State

Implementation complete locally on branch `fix/remove-quarantine-copy-278`.
No publication or local CI gates performed; parent owns publication, CI and merge.

## Decisions and why

The cleanup-refactor workflow is the active control surface. The bounded slice
is the duplicate field edge in `propstore/derived_build_plan.py`, not its other
valid compiler capabilities. Smallest change: delete the field and constructor
assignment, and correct its two-line documentation (four lines removed overall).

Iteration 1: the lowered finding -> plan duplicate field dependency is a
dead/test/scaffold surface; disposition: delete. Repository search found only
the declaration, assignment and false documentation, with no readers. No
replacement collection, property, alias or fallback was added.

Retained surfaces: RepositoryCheckedBundle, SidecarBuildPlan conflict/count APIs,
conflict compilation, repository document reads, dangling-reference discovery,
and compile_sidecar_build_plan remain existing owner capabilities. The transient
QuarantineDiagnostic -> BuildDiagnostic loop remains unchanged.

Canonical persistence uses `plan.diagnostics` in `propstore/derived_build.py`.
Build reporting in `propstore/compiler/workflows.py` reads checked messages and
plan conflicts. Neither needs the deleted carrier. Issues #144, #102 and #195
remain separate, as specified by #278.

## Verification

Static search of production and tests: deleted field name has no hits after
the change. Existing `tests/test_build_diagnostics.py` exercises lowering;
`tests/test_sidecar_build_z1.py` exercises dangling stance, justification and
micropublication references through persisted blocking diagnostics. These tests
have not been run locally. PR CI results and issue typing acceptance remain
unverified and belong to the parent's delivery workflow.

## Surprises

None in the bounded source change.

## Next step

Parent checks the local diff, publishes the PR, reads terminal CI results, and
handles the authorized merge.

## Draft PR text

Title: Remove unused quarantine diagnostic copy from sidecar build plans

SidecarBuildPlan retained transient dangling-reference findings after lowering
them into canonical BuildDiagnostic rows, although no caller read the extra
field. Delete that field, its assignment and its false report documentation.
The existing lowering and sidecar diagnostic persistence remain unchanged.

Closes #278.

Validation: static search confirms the removed field has no production or test
references. Runtime validation is pending PR CI; no local CI gates were run.
