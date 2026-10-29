# Delete loose file provenance stamper (#234)

## Goal
Delete arbitrary Markdown/YAML stamping while retaining typed provenance, named graphs, composition, and Git notes. Active control surface: protocols:cleanup-refactor.

## State
Read the complete provenance package owner, records, JSON-LD constants, stamp-only tests, named-graph tests, composition tests, and import/promotion/alignment note call sites. The isolated branch is cleanup/loose-provenance-stamper-234 from origin/master. No publication authorized for this worker.

## Decisions and why
Smallest change: delete about 160 production lines plus the stamp-only test module; remove only stamper imports/export. No replacement code or new checks.

The package file contains live typed owners and the forbidden surface. The issue explicitly requires keeping those live paths, so the bounded deletion removes the stamper surface in place. No live capability is recreated or moved, and none of the stamper lifecycle or representation survives.

Classification and disposition:
- stamp_file, _utc_timestamp, _build_produced_by_yaml, _stamp_md, _stamp_yaml, four regex constants, and their re/datetime/Path imports: dead/test/scaffold surface; delete. They implement arbitrary-path text mutation with no production caller.
- tests/test_provenance.py and its import: wrong caller that exists only for the old surface; delete the entire module. All four tests exercise stamping only.
- ProvenanceStatus, ProvenanceWitness, Provenance, _NamedGraphDocument, note constants, codec, composition and their canonicalization/deduplication helpers, ProjectionFrameProvenanceRecord export: already-owned capability that must use its true owner directly; keep unchanged in provenance.
- Source charter produced_by fields: already-owned capability in families/sources.py using ExtractionProvenanceDocument; keep. They are not arbitrary file stamping and must not be removed by a broad name search.

## Surprises
The issue references the historical provenance.py location; current owner is provenance/__init__.py. Current stamp module has four tests, not the historical five mentioned in the issue.

## Verification
Search gate: no stamp_file/private stamper names or regex constants in propstore/ or tests/. Keep existing named-graph/Git-note, composition, importing, source-promotion and alignment test files unchanged. CI tests and uv run pyright propstore remain publication checks for the supervisor; do not duplicate CI locally.

Iteration 1 result: the forbidden-symbol search returned zero hits in propstore/ and tests/. git diff --check passed. The inspected source diff is exclusively 160 deleted stamper lines; the 119-line stamp-only test module is deleted. No runtime tests or Pyright were run locally, in accordance with the instruction that CI runs on the PR. Runtime verification remains pending supervisor publication.

## Draft PR
Title: Delete the unused loose file provenance stamper

Delete stamp_file, its Markdown/YAML regex machinery, timestamp helper, unused imports, and export. Delete the four tests devoted solely to arbitrary-path stamping. Typed provenance, named-graph serialization, composition, Git-note publication, and charter-owned extraction provenance remain unchanged.

Closes #234.

Validation: forbidden-symbol search has no matches in production or tests; diff whitespace check passes. PR CI tests and package Pyright are pending publication.

## Next step
The bounded source slice reached the deletion fixed point; runtime checks remain pending PR CI. Commit locally with this note. Supervisor owns publication and CI; this worker must not push or publish.
