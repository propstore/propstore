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

Parent publishes #144 branch and reads PR CI. Repair concrete failures in scope. #209 waits for #145/#82/#27/#208 owner integration; do not replace them with detector-local approximations.

## Iteration 1 - admission through WorldQuery

Persist ClaimAdmission charter objects containing typed admitted/quarantined state, full checked-document digest and claim pass identity in the existing derived snapshot. Delete RepositoryCheckedBundle.claims; use explicitly admitted/quarantined collections, and enumerate all checked artifacts only at projection/lint boundaries. WorldQuery semantic claims and parameterizations, and grounding loading, now consume admitted records. Explicit policy-gated quarantine inspection retains raw document and diagnostics; lookup of quarantined claims raises QuarantinedClaimError. Report count now reads blocked checked artifacts.

Actively authored focused test command: `powershell -File scripts/run_logged_pytest.ps1 tests/test_checked_admission.py -q -n 0` passed 2 tests; log `logs/test-runs/pytest-20261028-234015.log`. The preceding run failed because the new test passed RenderPolicy as positional Environment; corrected test to the existing keyword API. No CI steps run locally.

## Iteration 2 - dependent semantic edges

Disposition correction from primary source: ASPIC extract_justifications explicitly retains inactive-premise licenses because removing them fabricates independent reported premises. Keep licenses with admitted conclusions even if a premise is quarantined; the missing active premise prevents argument construction. This is a declaration capability, not a blocked claim node. Exclude quarantined conclusions, stance endpoints and micropublication claim bundles from semantic inventories. References now distinguish quarantined subjects from nonexistent subjects in their diagnostic kind and message.

Final authored focused run passed 3 tests, log `logs/test-runs/pytest-20261028-234554.log`. Tests cover retained raw status/diagnostics, explicit quarantine lookup failure, changed-document/pass admission rejection, NO_CLAIMS value result, revalidation at a new sidecar, multiple diagnostics counted once, blocked equations producing no parameterization, blocked parameters producing no conflicts or grounding facts, no blocked ATMS nodes, and no ASPIC argument from a quarantined premise. `git diff --check` passed. PR CI and repository-wide suites remain unrun locally by instruction.

Known integration concern for PR CI: tests/test_world_query.py uses missing-statement OBSERVATION fixtures, which are truly quarantined by the canonical contract. Repair those fixtures to valid claims where their tests intend active reasoning; do not weaken admission. #145 worker may merge the first admission commit; compiler/ir.py and claims_passes.py are stable for its quantitative additions.
