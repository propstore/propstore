# Quantitative evidence contract

## Goal

Implement issue #145: one typed checked quantitative owner, precise blocking diagnostics, lossless scalar values, resolved form/unit semantics, and consumers that use that owner.

## State

Initial vertical slice complete: typed quantitative variants, compiler projection, canonical JSON sidecar persistence, admission version, and independent malformed diagnostics. Active control surface: protocols:cleanup-refactor, read from its installed SKILL.md. Integrated the coherent first local #144 slice from campaign/209-checked-conflicts. No publication authority for this worker.

## Decisions and why

- Smallest complete change: add `Claim.quantitative_ir` beside existing `conditions_ir`, with tagged typed value/uncertainty variants, evidence metadata, and resolved form/unit. The compiler creates it once and admission binds its persisted bytes. Existing canonical checked condition projection establishes the placement. Estimated 700-1100 production lines and 250-400 focused test lines including consumer changes.
- Scalar variants preserve int/float/string/bool exactly. Interval bounds are finite and inclusive, with an optional point constrained to the interval. One-sided intervals retain their absent bound.
- Absolute uncertainty is a finite nonnegative distance in the resolved measurement unit. Relative uncertainty is a finite nonnegative dimensionless ratio, without a fabricated upper bound. Neither is a subjective-logic ignorance mass. Confidence is a finite probability in [0,1]; sample size is a positive integer excluding bool.
- Raw charter scalar fields remain authoring/IO only. Source authoring identity excludes derived checked fields as it excludes conditions_ir; runtime identity consumes checked evidence when available. Malformed authored identity remains inspectable and never supplies runtime values.
- Existing `_check_parameter_unit` owns resolved form lookup, compatibility, conversion, and dimensionless default; consolidate it into the quantitative check rather than duplicate it.

## Classification and disposition

- Authored quantitative Claim -> semantic readers: valid capability with wrong representation. Rewrite to the checked quantitative owner; keep raw scalar fields only at authoring/IO.
- `_check_parameter_unit` -> CHECKED unit evidence: already-owned capability that must use its true owner directly. Consolidate resolution with quantitative evidence construction and delete the independent unit-validation path.
- Value comparison's getattr field accessors: deleted old surface. Delete and consume the checked value variants directly.
- ActiveClaim independent value/evidence fields: valid capability with wrong representation. Rewrite to one quantitative object; value projection derives directly from it.
- Preference uncertainty-to-subjective-opinion mapping: wrong caller obtaining a different capability from measurement uncertainty. Delete that mapping; confidence/sample evidence retains its existing owner mapping.
- Claim/concept render sections, source promotion, overlay and worldline values: valid capability with wrong representation. Rewrite runtime reads to the checked owner; source lowering remains an explicit authoring boundary and preserves confidence.

## Surprises

The authored identity and source lowering paths execute before CHECKED, while the runtime graph stores canonical Claim directly. The parent selected quantitative_ir on the canonical checked projection, avoiding a parallel evidence map and claim mirror.

## Verification

Forbidden searches: semantic independent reads of value/bounds/uncertainty/confidence/sample/unit, value-comparison getattr narrowing, and `_check_parameter_unit` duplicate path. Runtime proof will be the actively authored focused quantitative test through the logged wrapper only. Parent owns PR CI and typing checks; no local CI gates.

Initial focused proof: logged `tests/test_claim_quantitative.py`, 19 passed, `logs/test-runs/pytest-20261028-234901.log`. It exercises exact scalar codec types, intervals, dimensionless/physical units, evidence invariants, and real repository compiler/admission/snapshot roundtrip. Earlier runs exposed a test attempting an already-forbidden nonfinite scalar and an empty-concept repository compilation short-circuit; tests now use real boundary conditions.

## Next step

Commit the initial slice, then rewrite dependent consumers and expand focused tests. No commit identifiers belong in this note.
