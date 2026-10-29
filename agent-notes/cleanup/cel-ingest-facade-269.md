# Issue #269: delete unused CEL ingest facade

## Goal
Delete the unwired validator/location/carrier wrapper surface and preserve the compiler structural invariant at its current owner. Active control surface: protocols:cleanup-refactor.

## State
Isolated branch cleanup/cel-ingest-facade-269 from origin/master; initial worktree clean. Deletion complete and literal search over propstore/tests has zero hits for the removed APIs. Local commit follows; no push/publication. Runtime/type checks are deferred to parent-owned PR CI, per Q's standing instruction.

## Decisions and why
Smallest change: remove about 170 facade lines and 50 wrapper-test lines, narrow the docstring/imports/exports. No replacement API or new tests. Full live owner reads and classifications follow before deletion.

## Surprises
None. The only production CEL module import found is the compiler structural detector.

## Iteration 1: classifications and dispositions
Read propstore/cel_validation.py and tests/test_cel_validation.py fully; read propstore/claim_conditions.py, families/claims_passes.py, source/claims.py admission path, compiler/workflows.py invariant and pipeline, and families/contexts_passes.py. Compiler imports only structural_concepts_in_expression; source/claims.py:209 calls condition-ir directly; claim_conditions.py:81 does likewise through the typed Claim interface, called by claims_passes.py:127.

- CelIngestValidationError, CelExpressionLocation, validate_cel_expression and validate_cel_expressions: dead/test/scaffold surface; delete the scaffold. The location DTO exists only to decorate errors from this unused facade; no missing domain owner is needed.
- Claim/context/lifting-rule iterator wrappers: wrong callers that exist only for the old surface; delete those paths. Their expression/location pairs feed the dead validator, not compiler/source/family owners.
- Five facade tests and their imports: wrong callers that exist only for the old surface; delete those paths rather than recreate the validator.
- _collect_identifiers, iter_cel_identifiers, structural_concepts_in_expression: keep at the exact existing compiler support owner as issue #269 explicitly directs. Whole-file deletion gate is narrowed by that explicit retention requirement.
- Module prose/imports/exports: delete stale facade references and keep only retained capability references.

Existing boundary coverage: tests/test_source_authoring_p82.py:448 exercises source CEL admission; tests/test_family_passes.py:417 exercises claim checking; tests/test_compiler_workflows.py:150 exercises structural aborts through both workflows. No new tests or guards.

## Next step
Parent publishes, reads PR CI, and completes review/merge. Local reduction reaches the source search fixed point; runtime acceptance remains pending CI.

## Checkpoint
Deleted the unused facade/error/location/carrier wrappers and five facade tests.
Retained the identifier walker, detector and five existing tests unchanged.
No replacement API, source/family/compiler call-site changes, or new tests.
No blocker; next inspect searches/diff and commit locally.

## Draft PR text
Title: Delete unused CEL ingest validation facade

Removes the unwired CEL validator, error/location carrier, three expression iterator wrappers, and their facade-only tests. Keeps the compiler identifier walker and structural-concept detector at their existing owner; source admission and canonical claim checks continue through their existing typed condition-ir paths.

Closes #269.

Validation: literal removed-API search over propstore/tests returns zero hits; retained implementation and five retained tests have no behavioral edits. Local CI steps were not run; PR CI must provide runtime/type results.
