# Checked conflict inputs and admission prerequisite

## Goal

Deliver #144 checked-admission execution first, then #209 canonical admitted conflict inputs, including the remaining checked-condition consumption in #220. Parent owns publication, PR CI, and normal merge. No publication from this worktree.

## State

Read AGENTS.md, CLAUDE.md, global instructions, issue-delivery and cleanup-refactor; cleanup-refactor is the active control surface. Read issues #209, #220, #145, #82, #144, #208, #27 and current compiler, derived build, detector, world query and graph sources. Both admission slices are committed and parent published PR #374 for #144. Parent monitors CI; source stays unchanged pending concrete failures. #82 merged through PR #372. #27 owner committed its typed index. #145 and #208 have separate workers; this branch does not implement them.

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

Parent reads PR #374 CI; repair concrete failures in scope. After #144 merges, create a fresh branch for #209 so #374 stays scoped. #209 waits for #145/#208 owner integration; do not replace them with detector-local approximations. Coordinate directly with their workers. #145 API is Claim.quantitative (QuantitativeEvidence with exact point and closed point/interval/absence union), and value_comparison accepts QuantitativeEvidence inputs. #208 owns separate per-claim membership result fields on ConflictRecord, referencing canonical micropublications; no entire global provenance index is serialized per conflict.

## Iteration 1 - admission through WorldQuery

Persist ClaimAdmission charter objects containing typed admitted/quarantined state, full checked-document digest and claim pass identity in the existing derived snapshot. Delete RepositoryCheckedBundle.claims; use explicitly admitted/quarantined collections, and enumerate all checked artifacts only at projection/lint boundaries. WorldQuery semantic claims and parameterizations, and grounding loading, now consume admitted records. Explicit policy-gated quarantine inspection retains raw document and diagnostics; lookup of quarantined claims raises QuarantinedClaimError. Report count now reads blocked checked artifacts.

Actively authored focused test command: `powershell -File scripts/run_logged_pytest.ps1 tests/test_checked_admission.py -q -n 0` passed 2 tests; log `logs/test-runs/pytest-20261028-234015.log`. The preceding run failed because the new test passed RenderPolicy as positional Environment; corrected test to the existing keyword API. No CI steps run locally.

## Iteration 2 - dependent semantic edges

Disposition correction from primary source: ASPIC extract_justifications explicitly retains inactive-premise licenses because removing them fabricates independent reported premises. Keep licenses with admitted conclusions even if a premise is quarantined; the missing active premise prevents argument construction. This is a declaration capability, not a blocked claim node. Exclude quarantined conclusions, stance endpoints and micropublication claim bundles from semantic inventories. References now distinguish quarantined subjects from nonexistent subjects in their diagnostic kind and message.

Final authored focused run passed 3 tests, log `logs/test-runs/pytest-20261028-234554.log`. Tests cover retained raw status/diagnostics, explicit quarantine lookup failure, changed-document/pass admission rejection, NO_CLAIMS value result, revalidation at a new sidecar, multiple diagnostics counted once, blocked equations producing no parameterization, blocked parameters producing no conflicts or grounding facts, no blocked ATMS nodes, and no ASPIC argument from a quarantined premise. `git diff --check` passed. PR CI and repository-wide suites remain unrun locally by instruction.

Known integration concern for PR CI: tests/test_world_query.py uses missing-statement OBSERVATION fixtures, which are truly quarantined by the canonical contract. Repair those fixtures to valid claims where their tests intend active reasoning; do not weaken admission. #145 worker may merge the first admission commit; compiler/ir.py and claims_passes.py are stable for its quantitative additions.

## Iteration 3 - PR #374 failure dispositions

Live job logs show 79 failed / 2113 passed / 4 skipped, plus five import-order and seven format findings. `gh run view --log-failed` stops at the large contract assertion; the jobs/logs API returns the complete trace. No local whole-CI rerun.

- tests/test_world_query.py observation inventory: valid capability with wrong representation; add required authored statement. Its equation test must use resolved quantity forms and explicit canonical variable bindings.
- tests/test_sensitivity_query.py, test_graph_export.py, test_world_reasoning_reports.py, test_cli_world.py: valid capability with wrong representation; declared active parameter/equation fixtures lack resolved output forms and equation bindings. Supply canonical dimensionless quantities/bindings at their test fixture owner; preserve physical gate form in graph export.
- tests/app_render_helpers.py consumers (claim/concept views, neighborhoods, web routes, CLI claim, render filtering): valid capability with wrong representation. Lifecycle BLOCKED/DRAFT claims were also semantically invalid because unit/form was missing; make lifecycle fixtures valid while preserving their statuses. Equation fixture lacks bindings for v/d/t and output concept; provide dimensional evidence while preserving presented concepts/expression. Missing-value fixture needs resolved form, not a fabricated value.
- tests/test_app_claims_compare.py non-algorithm fixture: valid capability with wrong representation; resolve canonical parameter form so comparison reaches the intended type/body boundary.
- tests/test_app_worldlines.py, test_cli_worldline.py, test_worldline_world_query.py: valid capability with wrong representation; give parameter outputs a resolved form so worldline/ATMS/revision tests receive admitted inputs.
- tests/test_world_sidecar_grounded.py and test_cli_phase10_advanced.py: valid capability with wrong representation; author the required output concept and form for grounding parameter facts.
- tests/test_atms_categorical_provider_visibility.py: the old derived-rejection expectation is dead/test/scaffold surface after canonical dimensional admission. A category-bound equation cannot enter parameterization at all. Rewrite the test through canonical category/quantity forms and bindings, asserting typed quarantine diagnostic and no equation/derived node; preserve the categorical provider itself as an admitted exact scalar.
- Contract manifest: already-owned capability that must use its true owner directly; bump changed registry contract, generate manifest from build_propstore_contract_manifest and apply exact generated output. Never hand-author schema fields.
- Ruff findings: valid source files with formatting/import order defects; apply existing formatter output, no new workflow or guard.

Repair run over the 13 actively edited test files: 167 passed, 1 failed, log `logs/test-runs/pytest-20261028-235921.log`. Remaining micropublication fixture had no concepts at all, so the compiler's no-concepts path emitted no checked bundle/claims; disposition is valid capability with wrong representation, supply a real canonical concept. No admission bypass. This fixture is repaired before integration with current master. Shared app rendering fixture now has physical length/time/speed forms, equation bindings, and required physical units for lifecycle-only examples. Import/format corrections use Ruff's diff output applied with apply_patch; manifest diff comes directly from build_propstore_contract_manifest.
