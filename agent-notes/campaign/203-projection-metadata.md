# #203: delete inert structured-projection attribution metadata

## Goal

Delete only the inert attribution copy. Keep live structured arguments,
frameworks, mappings, extension semantics, and source-support owner data.

## State

Branch `campaign/203-projection-metadata`, based on `campaign/217-projection-lifting`.
Local implementation complete; supervisor owns publication after #217 merges.

## Decisions and why

Active control surface: `protocols:cleanup-refactor` with `issue-delivery`.
Minimum change: delete about 150 production lines and 150 metadata-only test
lines, retain the independent provenance absence test, add no production path.
The #231 exporter removal is already present in this base.

Read complete structured projection, ASPIC projection, provenance record and
boundary/record tests, ActiveClaim owner, provenance exports, and mapping caller
locations in world resolution, worldline argumentation and structured merge.

### Iteration 1: dependency classifications and dispositions

- StructuredArgument -> ProjectionAtom -> record/loss: dead/test/scaffold surface;
  delete the field, both DTOs, record file, constructor helpers and re-export.
  No attribution consumer remains after #217. No capability moves.
- ASPIC projection imports and hashlib: wrong caller that exists only for the old
  surface; delete these edges and direct metadata construction. Keep literal-key
  encoding: it still orders premises and names unmapped premise justifications.
- Boundary tests: dead/test/scaffold surface whose only subject is the removed
  metadata; delete the file rather than replacing metadata assertions.
- Provenance record tests: direct record assertions are dead/test/scaffold
  surface; delete those tests and pytest import. Keep independent existing
  import-record absence test.
- StructuredProjection framework/mapping and remaining StructuredArgument fields:
  already-owned capability; use existing typed owner directly, unchanged.
- ActiveClaim.source_assertion_ids and structured merge assertion assignment:
  already-owned capability; keep. Removing this decorative copy does not claim
  to implement #139/#146 assertion-attribution reporting.
- `_jsonld.py` reference to the deleted record module: wrong caller that exists
  only for the old surface; delete the stale descriptive text, keep constants.

Search gates: no removed carrier names or helper names under propstore/tests;
inspect all StructuredArgument construction sites. Existing consumer coverage
in ASPIC/world/worldline/merge and package pyright runs in PR CI, not locally.
No new test or guard is appropriate for deleting inert metadata.

## Surprises

None. The exporter branch is already absent with #231.

## Next step

Removed-symbol searches under propstore/tests returned zero hits; the only
StructuredArgument constructor now builds the consumed fields directly.
Diff whitespace check passed. No runtime checks were run locally; PR CI must
verify logged ASPIC/bridge/world/worldline/merge suites and package pyright.
Source support was preserved, not newly implemented or verified as complete.

Commit scoped reduction and hand off for supervisor publication after #217.

### PR draft

Title: Delete inert structured-projection attribution metadata

Remove the unused attribution carrier, loss witness, projection-frame record,
construction copies and metadata-only tests. Live frameworks, argument/claim
mappings, structured fields and source-support owners remain in place.

Closes #203.

Verification: removed-symbol searches have no production/test matches;
`git diff --check` passed. Runtime verification awaits PR CI, including logged
pytest suites and `uv run pyright propstore`.
