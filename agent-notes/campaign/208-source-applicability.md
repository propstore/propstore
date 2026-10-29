# Source provenance and applicability (#208)

## Goal
Keep canonical micropublication membership as typed evidence without changing authored applicability. The active control surface is protocols:cleanup-refactor.

## State
Implemented locally on isolated branch campaign/208-source-applicability. Dependency #27 is merged upstream. Read detector models/orchestration, derived build plan, world bound/consistency/query owners, merge claim/classifier/storage loader, and provenance/micropublication families. All 12 new focused regressions pass; full CI is parent-owned after publication.

## Decisions and why
Smallest full change: delete source fabrication, require ClaimProvenanceIndex separately at detector entrypoints, attach its actual BundledClaim/UnbundledClaim results per conflict side, and reconstruct membership from existing canonical micropublication storage on reads. Estimated 180 production lines changed plus focused regression tests and explicit index arguments in existing fixtures. No global index is serialized into records and no bibliographic fields are copied.

Classification/disposition before edits:
- Claim source_paper/with_source_condition, synthetic source registry/category/collision and _claim_sources collapse: valid capability with wrong representation; delete semantic fabrication, rewrite evidence edges to the provenance owner.
- Other existing synthetic runtime bindings: already-owned capability; keep unchanged.
- Build/world/consistency membership input: already-owned capability; use ClaimProvenanceIndex over raw canonical bundles, independent of semantic admission.
- Conflict output membership: valid capability in wrong representation; retain actual owner result objects on ConflictRecord. Query reads use existing canonical micropublication projection directly.
- Merge comparison's shared source string and provenance precondition: wrong caller existing only for old surface; delete. Branch storage membership belongs to canonical micropublications; pass actual bundles separately through merge inputs, never fabricate from branch/paper.
- Source-condition and collision tests: dead scaffold; delete and replace with behavioral invariance tests. Canonical Claim cutover remains #209.

Search gates: source_paper/with_source_condition/_claim_sources and __source__ must be absent from detector/build paths. Runtime: newly authored focused tests only through logged wrapper; full CI is parent-owned after publication.

## Surprises
Merge loader currently labels branch as paper; it has no actual membership input. Coordinate its correction with #209 branch compilation work.

## Next step
Parent reviews the scoped implementation and draft PR text, publishes the branch, waits for PR CI, and repairs failures within scope. #209 must preserve raw claim_provenance inventory while replacing canonical detector input mirrors; #145's branch compilation change must preserve the independent raw membership load.

## Checkpoint
Source fabrication is confirmed in detector models, orchestrator, derived build, and merge classifier.
World queries already retain canonical bundles, so output evidence needs no new storage schema.
Required provenance index is confirmed by parent; no optional empty fallback.
No implementation edits yet. Next: remove fabrication and rewrite classified edges.

## Checkpoint 2
Deleted source field, CEL generator, source registry, collision path, and single-source collapse.
Build/world/consistency pass required provenance index; query reads canonical membership.
MergeClaim now requires its actual typed membership; loader reads raw canonical bundles.
Existing direct detector fixtures pass explicit empty indexes. No local CI gates run.
Next: focused behavioral tests, authored-test execution, search review and commit.

## Checkpoint 3
Eleven focused detector cases pass; repository integration fixture initially violated the real FK boundary and now uses an existing blocked peer.
The corrected fixture builds but produces no stored conflicts; investigating canonical admission diagnostics before changing it.
No full local test/lint/typecheck gates run. Source-fabrication search is empty in detector/build.
Merge provenance fields outside applicability remain unchanged and are outside this deletion slice.
Next: correct fixture admission from the compiler source, rerun the authored file, then commit.

## Checkpoint 4
All 12 authored tests pass in logs/test-runs/source-applicability-20261029-000103.log.
Fixture diagnostic proved the dimension key is Theta; corrected against dimensions owner.
WorldStore.claim_provenance now exposes raw membership independently of filtered semantic bundles; coordinated with #144/#209 owner.
Production changes are bounded to evidence inputs/output and deleted source semantics; no canonical claim cutover.
Next: formatting edits, scoped commit, merge current origin/master, handoff with draft PR body.

## Final slice disposition and evidence
ConflictClaim source field/CEL generator, derived-build source collapse, and synthetic source registry/collision handling are deleted. Their remaining caller edges now use actual ClaimProvenanceIndex membership. ConflictRecord.with_provenance attaches per-side owner result objects after comparison; None on low-level component records denotes unavailable evidence, distinct from an explicit UnbundledClaim returned by the required public index input. No global index is stored on a conflict record.

WorldStore.claim_provenance is the raw membership owner input; WorldQuery reads canonical projected bundles, overlays delegate, and the ATMS test feed derives its own raw fixture inventory. Runtime semantic all_micropublications admission remains separate. MergeClaim holds the actual per-claim membership result and merge storage loads all raw canonical bundles at its branch commit.

Search evidence: no source_paper/with_source_condition/_claim_sources/__source__/SyntheticConceptCollision in detector/build production. Remaining source_paper fields in merge witnesses/reporting concern existing merge identity/evidence and are outside applicability fabrication. No local suite, lint, or typing CI gates ran. Focused authored file result: 12 passed, logs/test-runs/source-applicability-20261029-000103.log. Earlier failed fixture logs remain available and are not success evidence.
