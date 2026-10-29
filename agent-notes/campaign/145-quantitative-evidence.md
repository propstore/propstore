# Quantitative evidence contract

## Goal

Implement issue #145: one typed checked quantitative owner, precise blocking diagnostics, lossless scalar values, resolved form/unit semantics, and consumers that use that owner.

## State

Typed quantitative owner and production consumers implemented. Active control surface: protocols:cleanup-refactor, read from its installed SKILL.md. Integrated the first local #144 slice from campaign/209-checked-conflicts. Parent selected one combined #145/#209 delivery because the old detector mirror cannot carry the new owner without recreating the forbidden surface. This branch deliberately awaits the canonical detector cutover and WorldStore admission accessor owned by the #209 worker; it must not merge independently. No publication authority for this worker.

## Decisions and why

- Smallest complete change: add `Claim.quantitative_ir` beside existing `conditions_ir`, with tagged typed value/uncertainty variants, evidence metadata, and resolved form/unit. The compiler creates it once and admission binds its persisted bytes. Existing canonical checked condition projection establishes the placement. Estimated 700-1100 production lines and 250-400 focused test lines including consumer changes.
- Scalar variants preserve int/float/string/bool exactly. Interval bounds are finite and inclusive, with an optional point constrained to the interval. One-sided intervals retain their absent bound.
- Absolute uncertainty is a finite nonnegative distance in the resolved measurement unit. Relative uncertainty is a finite nonnegative dimensionless ratio, without a fabricated upper bound. Neither is a subjective-logic ignorance mass. Confidence is a finite probability in [0,1]; sample size is a positive integer excluding bool.
- Raw charter scalar fields remain authoring/IO only. Semantic identity always requires checked evidence; merge branch loading compiles the exact pinned branch through the existing compiler before computing semantic fingerprints. A typed quarantined-branch error carries retained artifacts and exact diagnostics and prevents target mutation. There is no authored semantic fingerprint fallback.
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

Second slice dispositions: rewrote ActiveClaim to one quantitative object, deleted value-comparison getattr/scalar-bag helpers, rewrote views/worldline/ATMS/export consumers, and deleted measurement-uncertainty-to-opinion reinterpretation. Raw source IO lowering now preserves confidence. Overlay uses the existing claim pipeline and stores fresh checked admission for changed/new bytes, and supplies that inventory explicitly to recomputed conflicts. Unchanged overlay claims retain base admission.

The required unit/default policy remains the declared PARAMETER policy. MEASUREMENT measure-only and optional-unit observations retain their existing contracts; no new mandatory form/unit was added to those types. Explicit supplied units and absolute uncertainty still require resolved form evidence. Relative ratios may exceed one.

Root found a real precision defect in the first comparison rewrite: float interval extraction would collapse adjacent canonical integers above the float exact range. The implementation now keeps integer interval components and uses exact Fraction subtraction for point comparison when conversion is unnecessary. Different physical dimensions reject comparison; compatible forms with different canonical unit symbols normalize through the existing unit owner into one common form unit.

Latest authored focused proof: `tests/test_claim_quantitative.py`, 31 passed, `logs/test-runs/pytest-20261029-000836.log`; includes large integers, common-unit normalization, source lowering, measure-only/optional-unit contracts, no-target-mutation merge failure, and fresh overlay admission. `tests/test_preference.py`, 12 passed, `logs/test-runs/pytest-20261028-235908.log`. No CI/typecheck/suite gate run locally. Parent owns the combined PR's CI and final acceptance.

Follow-up slice: interval-only claim detail rendering now reports a known bounded value rather than missing scalar evidence. Its focused regression brings the authored quantitative file to 32 passing cases, `logs/test-runs/pytest-20261029-001039.log`.

Precision follow-up: reproduced a canonical point at `2**53 + 3` below an interval starting at `float(2**53 + 4)`, both authored in kHz under the same Hz form. Unnecessary unit conversion and tolerance addition widened the point and incorrectly reported overlap. Same-form/same-unit intervals now compare directly, and finite overlap distances use exact Fraction subtraction. The authored focused case failed before repair (`pytest-20261029-001521.log`) and passed after (`pytest-20261029-001553.log`).

Remaining forbidden raw readers in conflict_detector belong to the #209 worker and are not accepted as final state. The existing test constructors were migrated to typed quantitative input; full fixture/source compatibility remains for combined CI. The contract manifest and claim/source-claims versions were updated for the new projection/source confidence field.

## Draft PR description

Claims currently admit incompatible quantitative scalar bags and consumers assign their fields different meanings. This change projects authored fields once into checked point/interval/absence, measurement-uncertainty, and evidence variants, binds them to compiler admission, and makes runtime values, preference, views, promotion, overlays, worldlines, and identity consume that owner. Invalid independent invariants remain precise blocking diagnostics; scalar types and large integer point comparisons retain their exact values. The final combined change also removes the detector input mirror in the #209 worker's branch.

Validation: focused authored quantitative and preference tests pass as recorded above. Combined PR CI and canonical detector integration remain outstanding; this is not a ready-to-merge claim.

## Next step

Commit the consumer slice for the #209 worker to integrate, then support combined CI repairs. Parent merges latest master/#144/#208 and resolves their shared merge-loader/manifest edits. No commit identifiers belong in this note.

## PR #377 repair

The initial unit consolidation recorded incompatibility but continued into conversion. Existing malformed-unit regressions exposed TokenError/AssertionError escaping from that conversion. Repaired the owner so incompatible units never convert, with the original authored unit/concept/form diagnostic context. Also restored the existing required checked-context evidence, missing canonical-unit and invalid canonical-form diagnostics, and nonquantity scalar-label behavior. The prior production checker and all parameter-unit contract tests determined these dispositions; no safeguards or assertions were relaxed. Quantitative tests now obtain declared parameter units from actual compiler contexts instead of accepting raw supplied forms.

Applied hosted-CI import/formatter diagnostics using read-only Ruff diffs through apply_patch. Removed the unnecessary isinstance-int check using an exact type check that still rejects boolean/noninteger sample sizes. Detector files and root's other test repairs remain under their existing owners.

Focused stable-source results: quantitative file 33 passed, `logs/test-runs/pytest-20261029-003828.log`; existing parameter-unit contract file 46 passed, `logs/test-runs/pytest-20261029-003920.log`. This includes checked-context/raw-form rejection, canonical-unit errors, malformed syntax, nonquantity labels, overflow, and decreasing affine interval behavior. Parent owns new hosted CI after publication.
