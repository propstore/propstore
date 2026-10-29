# Canonical detector caller integration

## Goal

Replace build/world/merge ConflictClaim conversions with canonical Claim input and the exact compiler admission and provenance owners required by #209.

## State

Active control surface: protocols:cleanup-refactor, already read during this campaign. Isolated campaign/209-canonical-callers branch based on the detector worker's coherent committed integration tip. Other agents own detector implementation and fixtures; no publication authority.

Owned caller implementation complete: build passes checked admissions as a tuple; world recomputation/consistency pass canonical documents plus the real snapshot inventory; WorldStore/WorldQuery expose persisted admissions; merge carries actual admission and compiler registry beside the canonical claim. The detector worker's family owner API is required at integration and is not duplicated here.

## Decisions and why

Smallest complete change is about 100-180 production lines: delete caller conversion lists, pass actual checked admissions as a collection, expose the persisted world admission inventory, and carry compiler admission/condition registry beside each merge canonical claim. Preserve raw micropublication membership independently.

The broken canonical Claim -> ConflictClaim dependency edges are valid capabilities with wrong representation. Disposition: delete conversions and rewrite callers to canonical Claim plus separate admission/provenance. World admission accessor is an already-owned capability: use persisted select_claim_admissions directly. Merge condition symbols belong to the actual compiler registry, carried by reference as contextual input; do not invent an empty registry or silently overwrite conflicting definitions.

## Surprises

Rival versions share claim ids, so admissions must remain a collection and match content digest/pass identity; indexing the pair by id would discard one version. A quarantined merge branch fails explicitly with artifacts and diagnostics before any target mutation.

## Verification

Search for ConflictClaim imports/conversions in owned callers. No local CI gates; parent owns combined PR CI. Exact detector API is supplied by the detector worker and not yet committed in this worktree.

Search result: no ConflictClaim reference remains in the owned caller files. MergeClaim construction invokes the family admission owner before fingerprints/classification; pair admission collections retain rival same-id versions. Actual compiler condition registries are combined only when overlapping symbol definitions agree; disagreement is a typed untranslatable comparison result, and ClaimAdmissionError is re-raised rather than hidden as a solver failure. Removed the recomputation single-claim shortcut so the detector owner still validates admission for every supplied canonical input.

## Next step

Commit and send branch to detector worker for integration. Merge fixture construction now needs required admission and condition_registry fields; the detector worker owns that fixture migration. No test suite/typecheck run locally.
