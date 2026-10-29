# Checked conflict inputs and admission prerequisite

## Goal

Deliver #144 checked-admission execution first, then #209 canonical admitted conflict inputs, including the remaining checked-condition consumption in #220. Parent owns publication, PR CI, and normal merge. No publication from this worktree.

## State

Read AGENTS.md, CLAUDE.md, global instructions, issue-delivery and cleanup-refactor; cleanup-refactor is the active control surface. Read issues #209, #220, #145, #82, #144, #208, #27 and current compiler, derived build, detector, world query and graph sources. First executable admission slice implemented locally; no publication.

## Decisions and why

Smallest complete #144 change: persist one charter-derived admission artifact per checked claim in the existing derived snapshot; use its admitted identity set at the WorldQuery semantic boundary and grounding input boundary; retain raw Claim documents and diagnostics behind an explicit quarantine inspection API. Derive report counts from checked artifacts. Estimated 250-400 production lines plus 200-350 regression lines. No additional storage system or claim mirror is needed. Content binding and compiler identity are fields of the admission artifact; derived snapshot hashing already incorporates compiler/package inputs.

Dependency edge dispositions before editing:

- CheckedClaim to derived projection currently loses blocked state: valid capability with wrong representation; rewrite to persist typed admission separately while retaining raw canonical Claim.
- RepositoryCheckedBundle.claims exposes all documents to compute: valid capability with wrong representation; replace convenience property with explicitly named admitted and quarantined collections, and use raw documents only for projection/inspection.
- WorldQuery claims_for/get_claim/claims_by_ids to world graph and resolvers currently expose raw quarantined documents: valid capability with wrong representation; rewrite semantic reads to admitted artifact identities and expose a typed quarantine outcome at lookup.
- Grounding sidecar loading to claim facts: already-owned capability that must use its true owner directly; consume the same admitted artifact selection instead of independent diagnostic scans.
- Stance/justification semantic reads referencing blocked subjects: valid capability with wrong representation; restrict dependent semantic edges through the admitted subject set and retain raw rows for diagnostic inspection.
- blocked_claim_count reconstructed from diagnostic subjects: already-owned capability that must use its true owner directly; count ClaimCheckedBundle.blocked_claims.

#209 prerequisites verified in current source:

- #145: Claim has raw optional quantitative fields; ClaimValueGroupDeclaration is metadata, not a checked quantitative union. Parent owns this prerequisite.
- #82: algorithms._bindings_for_algorithm_claim duplicates bindings and silently overwrites names. Parent assigned separately.
- #27/#208: derived_build_plan._claim_sources collapses membership and ConflictClaim.with_source_condition fabricates CEL. These owners must preserve all associations separately.
- #144: derived _compile_conflicts already filters checked_claims, but world and merge mirror conversion accept raw claims; durable admission is still absent.

Smallest complete #209 plan after prerequisites: delete ConflictClaim and all conversion sites, make detectors use canonical admitted claims and true quantitative/binding/condition owners, retain lifting run context as a distinct typed result referencing canonical identity, and migrate direct fixtures. Estimated 350-550 production lines touched plus 300-500 regression/fixture lines. No protocol/view/adapter/field mirror replaces ConflictClaim.

Shared files owned here: compiler/ir.py, compiler/workflows.py, derived_build_plan.py, derived_build.py, new families/claim_admission.py, families/registry.py, world/queries.py, world/model.py, grounding/loading.py. Coordinate any overlap before changing it.

## Surprises

The issue's original blocked count example was partly repaired: current count deduplicates diagnostic artifact ids, but still reconstructs admission from diagnostics and does not use CheckedClaim state.

## Next step

Commit the first vertical slice, then classify and repair dependent-reference diagnostics (quarantined is currently described as nonexistent), complete stance/explanation/micropublication filtering, and add blocked-equation/grounding/argumentation regressions. Parent handles remaining CI and prerequisite integration.

## Iteration 1 - admission through WorldQuery

Persist ClaimAdmission charter objects containing typed admitted/quarantined state, full checked-document digest and claim pass identity in the existing derived snapshot. Delete RepositoryCheckedBundle.claims; use explicitly admitted/quarantined collections, and enumerate all checked artifacts only at projection/lint boundaries. WorldQuery semantic claims and parameterizations, and grounding loading, now consume admitted records. Explicit policy-gated quarantine inspection retains raw document and diagnostics; lookup of quarantined claims raises QuarantinedClaimError. Report count now reads blocked checked artifacts.

Actively authored focused test command: `powershell -File scripts/run_logged_pytest.ps1 tests/test_checked_admission.py -q -n 0` passed 2 tests; log `logs/test-runs/pytest-20261028-234015.log`. The preceding run failed because the new test passed RenderPolicy as positional Environment; corrected test to the existing keyword API. No CI steps run locally.
