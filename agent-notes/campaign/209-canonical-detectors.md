# Canonical admitted conflict inputs (#209 / #220 with #145)

## Goal

Delete ConflictClaim and runtime claim-CEL reparsing. Every detector consumes canonical admitted Claim, its checked condition IR, quantitative evidence and variable bindings. Provenance remains a separate #208 input. Parent handles publication, CI and merge. PR #374 source remains in its separate worktree.

## State

Active control surface: protocols:cleanup-refactor. Read full detector models, classifiers, collectors, orchestrator, numeric derivation paths and their direct fixtures; read canonical claim/condition/admission, context lifting, compiler and merge owners. Integrated committed #144, #145 and #208 owner work in this isolated worktree. Resolved integration conflicts preserving both canonical admission and raw provenance. #145 owns non-detector quantitative consumer migration/value_comparison; #208 owns PR #376 CI repairs.

## Smallest complete plan

1. Delete the wrong detector input mirror and duplicate CEL front ends. Keep only conflict output results in models.py. Add typed admission rejection at the existing claim-admission family owner and a checked-condition accessor at canonical Claim, analogous to its quantitative accessor.
2. Rewrite direct detectors and collectors to canonical fields and checked owner objects; use #82 bindings directly and #145 value comparison directly. Delete detector-local lifted Claim clones and use existing LiftingSystem pair decisions, preserving authored conditions. First executable slice is direct parameter/measurement/equation/algorithm comparison with authored canonical regression inputs.
3. Rewrite numeric derivation to reference canonical Claim identities and retain new checked conditions/quantitative evidence only on genuinely derived result state. Canonical equation edges must carry checked conditions. Persisted admission and raw provenance remain independent inputs in build/world/merge/overlay.
4. Replace mirror/payload fixtures with canonical claims passed through the real claim-check pipeline. Verify categorical/boolean/numeric distinctions, invalid/missing/stale admission, checked conditions, units, contexts, algorithms/equations/measurements and direct/transitive derivation. Run only actively authored test files, commit slices, and hand parent full scope for PR CI.

Expected size: roughly 400-650 production lines changed with deletion of about 300 obsolete lines; 350-600 canonical fixture/regression lines. No second claim DTO/protocol/view, repeated semantic field list, adapter or lifting clone.

## Dependency-edge dispositions before edits

- Claim -> ConflictClaim -> collectors/detectors: valid capability with wrong representation. Delete mirror and use canonical Claim directly; output types in models.py remain specific conflict results, not input representations.
- Authored conditions -> condition_classifier/parameter partition/lifting implication: already-owned capability that must use its true owner directly. Delete reparse paths; consume Claim.checked_conditions (package CheckedConditionSet reconstructed by existing codec). ConditionSolver receives checked sets.
- Orchestrator cloned context/conditions -> detector: already-owned capability that must use its true owner directly. Delete _expand_lifted_conflict_claims and cache/stub. LiftingSystem.lift_decisions_between already owns pair context qualification; cloning discards authored applicability and is not retained.
- Raw Claim values/bounds/units -> value_comparison: valid capability with wrong representation. Use Claim.quantitative and exact .point. Numeric derivation owns new computed evidence and source identity references, never copies a claim field subset.
- Direct detector construction without admission: valid capability with wrong representation. Require separate Mapping[str, ClaimAdmission], rejecting missing/quarantined/stale/unchecked state at admission owner with typed failure. WorldStore.claim_admissions exposes the persisted inventory; overlays supply fresh pipeline outcomes for changed contents.
- Merge raw branch read -> detector: valid capability with wrong representation. Preserve #145 exact-branch compilation and #208 raw membership, carry its actual CheckedClaim.admission separately, and compare canonical documents without rebuilding a view.
- Direct tests constructing ConflictClaim or compact payload fixtures: dead/test/scaffold surface. Delete these constructors and rewrite capability tests through actual canonical compiler inputs; invalid equations are admission failures, never nominal detector inputs.

## Search / runtime evidence

Search forbidden input type/import/constructor, renamed *_concept_id input fields, to_cel_exprs(claim.conditions), check_condition_ir over canonical claim conditions, dataclasses.replace(claim,...), and detector object/getattr payload access. Existing output identifiers and graph edge identifiers are separate owners.

## Next step

Integrate canonical fixture migration and final #220 activation deletion, then hand parent coherent combined #145/#209/#220 source for hosted CI. No local whole-CI reruns or publication.

## Iteration 1 - canonical direct/derived inputs

Deleted the mirror and rebuilt models.py with conflict output results only. All detector entrypoints now accept canonical Claim plus separate admission collection/provenance. Admission owner matches claim_id+full checked content digest+pass identity (a collection is required for two real merge versions with the same claim id); missing, stale, quarantined and unchecked decisions are typed ClaimAdmissionError states. Canonical Claim.checked_conditions reconstructs the package-owned checked set through the existing codec.

Removed runtime claim CEL front ends, synthetic runtime registry and lifted Claim cloning/cache/stub. Existing LiftingSystem pair decisions own context qualification. Generic quantitative disagreement exists once for parameter and measurement grouping; AbsentValue supplies no contradictory value and skips disagreement. Numeric derivation now stores newly computed QuantitativeEvidence and CheckedConditionSet on its distinct result, preserving canonical source claim identities and checked equation-edge conditions. Removed form-name string blacklists: checked quantity evidence and admitted equation dimensional ownership determine numeric availability.

Focused authored boundary regression: 6 passed, `logs/test-runs/pytest-20261029-002230.log`. It proves exact categorical/boolean/large-int conflicts, typed missing/stale/quarantined admission, rival versions of one canonical identity, and lifting that leaves canonical checked applicability untouched. Initial run exposed missing future annotations in newly authored modules (NameError before comparison); corrected those declarations. Formatter/import edits are applied through apply_patch from Ruff diff output, not local CI gates.

Caller worker's committed build/world/merge slice is integrated, along with latest #145 precision and #144 branch. Fixtures worker owns the three existing detector suites and true compiler helper; its committed migration is next. Parent owns full CI and any post-publication repair batches. Boundary regression uses existing canonical_claim_fixtures.concept_with_form directly; duplicate fixture factory is not retained.

## Iteration 2 - final integration and remaining direct fixtures

Integrated canonical fixture suites, removed duplicate concept fixture factory, cherry-picked the #220 activation fallback deletion and merged current master after #144/#208 closure. Literal test-surface search exposed two more mirror dependencies: algorithm binding tests and pure value-comparison tests. Both are valid capabilities with wrong representation: algorithm tests now obtain real checked claims/admissions from compiler/world owners; pure value tests consume checked QuantitativeEvidence directly. Parent assigned the latter one-file repair to the quantitative worker. Active PLAN.md mirror framing is corrected by parent, not retained as current architecture. Historical archived plans remain history.
