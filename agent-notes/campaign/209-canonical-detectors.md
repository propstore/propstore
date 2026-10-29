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

Final source inspection found the migrated numeric fixture's graph edges still passed authored sources without checked edge conditions. This is valid graph context with wrong representation: compile the fixture's authored edge conditions at its test boundary through the package owner, supplying the actual condition registry for the one nonempty edge. Core keeps its typed checked-edge requirement; no runtime authored fallback is restored. All literal mirror references in production/tests/active PLAN are gone. Parent publishes the complete combined branch and owns full hosted integration checks.

## Iteration 3 - merge fixture CI repairs

Assigned merge-only fixture batch after PR #377 full CI. Shared tests/merge_helpers.py raw Claim -> MergeClaim is a valid capability with wrong representation: run the actual claim pipeline and pass its admission/condition registry, keeping canonical docs and original provenance. tests/merge_commit_helpers.py.author_concept creates unformed quantity concepts while author_param_claim uses Kelvin; this is valid capability with wrong representation, so author one resolved temperature form and reuse concept_with_form at the shared producer. Authoring helpers retain branch selection and supplied values/units.

Explicit temp/T applicability inputs in merge-regime/report/repository/CLI tests lack declared concepts; supply these declared quantity concepts at their fixture boundary, without parsing strings or fabricating a runtime binding. Repeated-base regression names P1/P2/Q with spaces are not CEL identifiers (concept checked owner rejects them); use valid identifier labels while preserving distinct names, topology and equality assertions. Concept deletion tests delete unused ordinary metadata while existing x claim stays valid; do not change their protections.

Verified production defect, assigned to parent: concept-free OBSERVATION is valid by contract, but compiler's no-concepts early return skipped the claim pass and merge rejected it. Parent repaired actual compiler owner with a real regression. Narrative merge/history/IC/worldline tests stay concept-free; no dummy concept is added to mask the defect.

## Parent integration repairs

The compiler early-return edge was a valid claim-checking capability skipped by an obsolete concept-presence assumption. Deleted that return and retained the empty-repository result only when neither concepts nor claims exist. A concept-free observation now passes validation, projection, world loading and exact admission verification in the focused production-path test.

The source-membership regression now proves both retained raw attribution while a peer is quarantined and explicit merge rejection, then unchanged membership after repairing the peer. The closed-category fixture authors vocabulary into the real concept owner; opaque structural points remain valid while incoherent numeric intervals reject under the quantitative contract. Solver failure tests target the retained pairwise solver operations, not the deleted partition path.

Focused parent evidence: 59 of 60 cases initially passed, exposing one remaining raw-form-only quantity fixture; after migrating it to the checked context, all 14 claim-contract cases passed. Both pairwise solver failure cases pass. Full PR CI remains required before merge.

The target-admission fixture uses storage identity `target-only`, which is a valid concept id but not a valid canonical CEL name. Give it explicit `target_only` canonical metadata while preserving the stored id and all target-history protections. No automatic id normalization is introduced in shared helpers.

Focused authored merge repair proof: 97 passed, `logs/test-runs/pytest-20261029-004105.log`, covering edited merge CLI/repository/report/regime/base-selection/target-admission files. Shared fixture producer correction addresses the other listed merge/structured suites without duplicated per-file fixes. Their full hosted rerun remains parent's publication stage. No production changes from this fixture worker and no whole-CI local gate.
