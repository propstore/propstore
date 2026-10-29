# Typed source and claim provenance indexes

## Goal
Implement issue #27 as the prerequisite for #208 and #209. Claims keep their
provenance-free identity; source classification belongs to the source subsystem,
and claim attribution comes exclusively from canonical Micropublication objects.

## State
Reading complete for source common/reference indexes/promote, snapshot branch
enumeration, Quire BranchPlacement and fixed-file family load, canonical
Micropublication, and derived-build source consumers. Cleanup-refactor is the
active control surface. No publication is authorized for this worker.

## Decisions and why
Smallest complete change: approximately 180 production lines plus 130 focused
test lines. Add a source-owned immutable index over snapshot BranchInfo and typed
source manifests/claims. Retain branch stem as SourceRef (placement is one-way),
but resolve canonical identity from SourceDocument.id, never from that stem.
Return typed unknown-source, missing-manifest, unidentified-claim, and
missing-promoted-claim results. Add a micropublication-owned index retaining
whole canonical bundles per claim, so multiple associations and source-less
bundles remain distinct from unbundled claims without another field mirror.

Broken dependency classification/disposition:
- derived_build._source_branch_tips -> snapshot source classification:
  already-owned capability that must use its true owner directly; rewrite to
  source index entries, keeping generic enumeration in snapshot.
- promote all-source projection -> prefix parsing: same classification; rewrite
  to source index SourceRef values.
- canonical membership -> ad hoc claim source collapse: valid capability with
  wrong representation; create lossless typed membership index here. #208 owns
  deleting the semantic collapse and synthetic conditions, so no parallel
  collapse is added in this issue.

No generic enumeration mechanism moves into source: snapshot still enumerates
branches; source alone classifies its own branches and resolves its manifests.

Forbidden surfaces/search: source-prefix parsing or branch classification in
derived_build; duplicate snapshot enumeration in promote; provenance fields on
Claim; reconstructed bundle dictionaries. Focused runtime gate: authored
tests/test_source_provenance_indexes.py via logged wrapper. Parent owns PR CI.

## Surprises
Quire fixed-file placement cannot enumerate refs. BranchPlacement uses a
one-way safe-slug/hash encoding, so stripping a prefix cannot recover the
original authored source name. The manifest owns canonical source identity.

## Iteration 1: source enumeration and claim membership
- Added source/indexes.py: SourceIndex retains snapshot BranchInfo, placement
  SourceRef, typed manifest and typed promoted/missing/unidentified claim results.
  SourceIndex.resolve distinguishes unknown source and missing source manifest.
- Added families/claim_provenance.py: ClaimProvenanceIndex retains actual
  canonical bundles per claim. BundledClaim and UnbundledClaim distinguish
  attribution absence from source-less bundles without copying bundle fields.
- Deleted derived_build._source_branch_tips and rewrote its sole caller to the
  source index. Promotion uses the same source refs instead of its prefix scan.
- Focused authored tests: four passed via logged wrapper. The initial test run
  exposed a missing required message in the new save fixture; corrected it.
  Passing evidence: logs/test-runs/pytest-20261028-234830.log.
- Search for source-prefix parsing, iter_branches and the deleted helper in
  derived_build.py and source/promote.py returned no hits. Source classification
  remains only in its owner; generic snapshot enumeration remains unchanged.
- Runtime CI/package typing are parent-owned PR gates and have not run locally.

## Next step
Parent publishes this branch and checks PR CI. Issue #208 consumes the membership
API and deletes the existing ad hoc single-source collapse and synthetic CEL;
that change is explicitly outside this branch. No issue, PR or branch was
published by this worker.

PR #375 full hosted tests, typing and import contracts passed. Parent applied
the exact reported Ruff import/format corrections and is following updated CI.
