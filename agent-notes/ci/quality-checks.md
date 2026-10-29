# CI quality checks

## Goal
Add the existing package typing and architecture contracts plus Python and
workflow quality checks to PR CI.

## State
All fourteen issue PRs (#339 through #352) are merged into master and this
branch. PR #353 initially passed typing, import contracts, workflow lint/security,
and tests; Ruff lint and formatting failed. The authorized repair now includes
import sorting via scripts/sort_imports.py (pinned isort), formatting, and the
remaining production/test/script findings. Hosted verification of these edits
is next; no rule was disabled.

Initial implementation plan:
Plan before implementation: about 45 workflow lines plus three development
dependencies and their generated lock entries. Keep the existing Python 3.13
job and logged pytest invocation. Add locked Pyright, import-linter, Ruff lint
and format checks on propstore/tests/scripts, pinned actionlint, and offline
zizmor. Each check runs after another check fails; failures remain failures.
Pin existing actions, disable persisted checkout credentials, and bound runtime.

## Decisions and why
- Ruff is already invoked by scripts/rope_delete_functions.py; preserve the
  existing lint policy without adding ignores. Q subsequently authorized all
  source formatting and lint repairs after the issue merges.
- Keep checks together to share checkout and the locked Python environment.
- Actionlint v1.7.12 is the upstream latest release and requires Go 1.25;
  `go run` resolves its pinned module using the runner's Go toolchain support.
- Resolve Python tool versions with the existing 14-day dependency age policy.
- Official tag API confirms the checkout v6.0.2, setup-uv v8.1.0 and
  setup-python v6.2.0 pins. Official Ruff and zizmor docs support their
  Python-package distribution and the selected check/offline commands.

## Surprises
Pyright has strict configuration but is absent from development dependencies.

## Next step
Publish the complete fixes, await PR #353 CI, repair every remaining failure,
then normal-merge and integrate master. Locked tools are Pyright 1.1.414,
Ruff 0.17.0, zizmor 1.30.1, and nodeenv 1.11.0. Existing age policy also
resolves certifi from 2026.10.19 to 2026.7.22.

## PR draft
Title: Enforce package and workflow quality checks in CI

The Python 3.13 check now runs strict package Pyright, the existing import
contracts, Ruff lint and formatting checks for propstore/tests/scripts, and
actionlint plus offline zizmor alongside logged tests. Each available check
still executes when another fails, preserving all failure output.

Pin action revisions, disable persisted checkout credentials, handle merge
groups, and bound the job to 30 minutes. Add the Python tools to the locked
development environment under the existing dependency age policy.

Validation: dependency lock generated successfully; hosted CI pending. Local
CI commands were not run, per repository instructions.

## Mechanical cleanup after PR CI

PR #353 run 40811853227 passed all steps except Ruff lint and formatting.
Applied Ruff I001 import ordering and unused E402 noqa removal plus formatter
proposals through apply_patch. Existing F401, ANN003, and BLE001 noqa comments
remain. No behavioral lint fixes, local final gates, commit, or push performed.
Source diff: 201 files, 2367 insertions and 1030 deletions; 29 formatting files
after import changes. Largest formatting diff is tests/test_parameter_unit_admission.py.
Mechanical inspection parsed every changed Python file before and after this
pass, removed import nodes, and compared ASTs: no non-import AST differences.
There are 149 original CI diagnostic locations across 79 remaining files below
(duplicate locations can represent overlapping fixes). Parent owns subsequent
semantic fixes after this mechanical commit; this agent relinquishes source.

Remaining original CI diagnostics excluding I001 and RUF100 (original line numbers;
formatter and import changes move lines; not a fresh local lint result):

- propstore/app/merge.py: RUF022:130
- propstore/cel_validation.py: UP037:71, UP037:93, UP037:162, RUF022:230
- propstore/cli/helpers.py: UP037:25, UP037:26, UP037:100
- propstore/cli/web.py: UP037:75, UP037:81
- propstore/compiler/context.py: TRY004:98, TRY004:105
- propstore/conflict_detector/algorithms.py: B009:31
- propstore/conflict_detector/parameterization_conflicts.py: FURB192:263
- propstore/core/base_rates.py: TRY004:126, TRY004:128, TRY004:130, TRY004:132
- propstore/core/lemon/proto_roles.py: TRY004:57
- propstore/core/relations.py: FURB192:189, FURB192:192
- propstore/defeasibility.py: RUF022:604
- propstore/derived_build.py: B009:346
- propstore/families/contexts.py: RUF012:112
- propstore/families/identity/claims.py: UP012:39
- propstore/families/registry.py: PLC0414:64, PLC0414:65, PLC0414:69, PLC0414:70, PLC0414:74
- propstore/fragility_contributors.py: BLE001:196, BLE001:228, BLE001:387, ISC004:454, PERF102:540
- propstore/fragility_scoring.py: PLC0414:24, BLE001:232, S112:265, BLE001:265
- propstore/heuristic/calibrate.py: PLC0414:28, PLC0414:31, PLC0414:34, PLC0414:37
- propstore/heuristic/classify.py: LOG015:467
- propstore/heuristic/embed.py: UP017:133
- propstore/importing/repository_import.py: TRY004:266
- propstore/merge/__init__.py: RUF022:42
- propstore/merge/merge_commit.py: RUF022:485
- propstore/merge/structured_merge.py: TRY004:328
- propstore/provenance/__init__.py: UP017:46, SIM201:420
- propstore/semantic_passes/types.py: PLC0105:110
- propstore/source/__init__.py: RUF022:65
- propstore/source/alignment.py: FLY002:209
- propstore/source/claims.py: TRY004:163, UP017:400
- propstore/source/common.py: UP017:55
- propstore/source/promote.py: TRY004:521, TRY004:529, RET501:708, RET501:715
- propstore/source/relations.py: UP017:66
- propstore/support_revision/belief_set_adapter.py: PYI041:640
- propstore/support_revision/dispatch.py: BLE001:133, BLE001:173, BLE001:210
- propstore/support_revision/history.py: ISC004:497, BLE001:517
- propstore/world/atms.py: UP035:32, SIM102:1974
- propstore/world/model.py: PYI034:494
- propstore/world/resolution.py: ISC004:585, ISC004:604, ISC004:616, ISC004:676, ISC004:683
- propstore/world/types.py: UP012:209, UP037:425, RUF022:720
- propstore/world/value_resolver.py: B009:75, TRY004:558, LOG015:598, LOG015:644
- propstore/worldline/resolution.py: BLE001:388
- propstore/worldline/result_types.py: PIE810:48, UP037:88
- propstore/worldline/revision_capture.py: PIE810:340, PIE810:356
- propstore/worldline/runner.py: UP017:181
- scripts/check_agm_workstream_order.py: PIE808:22
- scripts/extract_codex_requests.py: SIM103:112
- scripts/extract_concepts.py: BLE001:17
- scripts/list_migration_tests.py: SIM102:69
- scripts/reconcile_vocab.py: ISC004:39, ISC004:47, ISC004:69, ISC004:81, ISC004:88, ISC004:95, SIM102:320, SIM102:329, SIM102:338
- scripts/register_concepts.py: PLW1510:129
- scripts/review_assessment.py: BLE001:125
- scripts/seed_tags.py: EXE001:1
- tests/atms_feed.py: RUF034:185
- tests/test_algorithm_parse_admission.py: ISC004:114, ISC004:116, ISC004:118, ISC004:120, ISC004:157
- tests/test_app_claims_compare.py: SIM117:84, SIM117:90
- tests/test_claim_charter.py: PYI041:64
- tests/test_claim_enums.py: B017:26
- tests/test_claim_views.py: SIM117:67, SIM117:74
- tests/test_concept_views.py: SIM117:98
- tests/test_core_analyzers_phase6.py: FLY002:134
- tests/test_embed.py: SIM117:127, SIM117:136, SIM117:144
- tests/test_embed_similar.py: SIM117:120, SIM117:148, SIM117:174
- tests/test_fragility.py: RUF012:372
- tests/test_grounding_translator.py: PYI041:26
- tests/test_lemon_form_dimension_boundary.py: PLR0402:14
- tests/test_merge_nonclaim_base.py: RUF059:148
- tests/test_neighborhoods.py: SIM117:65, SIM117:74, SIM117:83
- tests/test_param_conflicts.py: SIM117:487
- tests/test_predicate_proposals.py: PYI034:101
- tests/test_preference.py: PLR0402:9
- tests/test_provenance_records.py: PLR0402:5
- tests/test_repository.py: SIM117:163
- tests/test_revision_argumentation_views.py: C409:192
- tests/test_sidecar_quarantine_z1.py: SIM117:64
- tests/test_value_resolver_failure_reasons.py: SIM117:186
- tests/test_worldline_error_visibility.py: RUF012:109
- tests/test_worldline_hash_excludes_transient_errors.py: RUF012:55
- tests/test_worldline_hash_repr_typed_failure.py: PLR0402:81, PLR0402:82, PLR0402:83, PLR0402:84
- tests/test_worldline_ic_merge.py: C409:80

## Tests and scripts lint repair

Repaired the tests/scripts portion of the hosted Ruff findings without disabling
rules. Changes group into context-manager flattening, explicit string grouping,
direct import syntax, scalar annotation simplification, Self return annotation,
unused binding and redundant expression cleanup, and instance-owned mutable
fixture state. Removed the stale ANN003 suppression in the ASPIC fixture.

The claim enum rejection test now expects Quire DocumentSchemaError:
DocumentCodec.convert delegates to its conversion callable, and installed Quire
documents/schema.py convert_document_value wraps msgspec validation/type failures
in that exception. Script concept extraction catches only file IO, UTF-8 decode,
and YAML parser failures. The optional embedding assessment retains its existing
tolerant boundary but logs its traceback through a module logger. Concept
registration explicitly uses check=False because its following branch inspects
and reports the subprocess return code.

Applied Ruff lint and formatter diff proposals using apply_patch; no local test,
typecheck, or final quality gate was run. Initial Ruff diagnostics and repeated
read-only --diff proposal generation were run to locate and edit the findings.
Hosted CI must establish the result. No commit, push, or publication by this
worker. scripts/sort_imports.py remains parent-owned and untouched here.

## Production repair dispositions

Validation uses existing msgspec conversion at input boundaries while retaining
caller-visible ValueError diagnostics. Dispatch handles the actual realization
EnumerationExceeded exception. Existing tolerant boundaries retain their policy
and now log tracebacks. Context.parameters remains a stored field with an
instance-owned default. Public exports are explicit rather than suppressed.

The scoring opinion_sensitivity reexport was an already-owned capability:
fragility.py now imports directly from Doxa, preserving its public export and
deleting the intermediate scoring export. Cleanup-refactor controlled that
bounded deletion; PR CI verifies the production path. The seed_tags script's
shebang requires the executable bit in Git, which is corrected without a lint
exception.

## Hosted follow-up

Run 40813980782 passed 2219 tests (4 skipped), formatting, import contracts,
actionlint and Zizmor. Eight typing diagnostics and six lint diagnostics remained.
Repairs use Quire's actual DerivedSession, type the context default factory,
and explicitly type the existing ast-equiv callable boundaries from its real
signature. The contravariant type variable has its required suffix. Import
grouping is corrected. Structured enumeration now branches on the successful
list result first, retaining RuntimeError for the incomplete-enumeration result.
Publish these fixes and await the complete hosted result before merging.

## Dependency signature repair

Run 40814440982 passes tests and lint, but importing compare still exposes
ast-equiv's unparameterized binding dictionaries. The actual owner already
requires string-to-string bindings internally. Upstream ast-equiv PR #6 fixes
four annotations; its hosted checks must pass and it must merge before this
dependency is pinned. One remaining derived_build formatting edit is applied.

Cleanup-refactor slice: algorithms.py's call-through and value_resolver.py's
Protocol/cast only compensate for this missing owner signature. Classification:
already-owned comparison capability; disposition: import the true typed owner
directly. Delete _ast_equiv_compare, the local ast_compare function, _AstCompare
and its cast. Keep the existing imported call-site name for tests. Search those
deleted definitions and use PR CI to verify all callers; no replacement shim.

Ast-equiv PR #6 passed package typing, 249 tests and distribution build, then
merged normally with two parents. Pin its merged revision and let Propstore's
full hosted checks validate the direct imports and all integration callers.

Run 40815097880 passed tests, formatting, contracts and workflow checks. Its
only remaining typing/lint finding was the unused ComparisonResult import left
after deleting the local Protocol; that import is now removed. Await the final
hosted run, then normal-merge PR #353 and integrate Propstore master. The upstream
temporary worktree/branch is removed; its pre-existing divergent local master
was preserved after fast-forward was refused.
