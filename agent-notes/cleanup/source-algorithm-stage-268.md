# Issue 268: remove inert source algorithm stage

## Goal
Delete the source claim stage field and unused branded type; reject removed input through existing strict decoding. Parent owns publication and merge.

## Decisions and why
Active control surface: protocols:cleanup-refactor. Smallest change: remove two source lines, delete the 24-line dead type module, remove one current documentation example line, and add about 40 lines of focused boundary acceptance coverage.

Target owner: SourceClaimDocument retains the source shape; its _Struct base already forbids unknown fields. Quire documents.schema owns generic strict JSON/YAML/typed conversion. No decoder or hash special cases are needed.

Iteration 1 classifications and dispositions:
- SourceClaimDocument.stage and its import: dead/test/scaffold surface; delete the caller path. No canonical stage semantics exist in build_promoted_claim.
- core.algorithm_stage module and both converters: dead/test/scaffold surface; delete the dead scaffold. Exact production/test search shows only the field import uses the type and neither converter has callers.
- docs/data-model.md algorithm stage example: wrong caller that exists only for the old surface; delete the obsolete field line.
- Quire strict decoder and source _Struct: already-owned capability that must use its true owner directly; keep unchanged and exercise with removed input.
- Identity functions in families/identity/claims.py: already-owned capability that must use its true owner directly; keep unchanged. They serialize the typed source document, so deleting the field removes it from identity inputs.

Slice read: families/sources.py, core/algorithm_stage.py, source/claim_concepts.py, families/identity/claims.py, source/claims.py decode/proposal call sites, existing authoring/decoder test patterns, installed Quire documents/schema.py.

## State
Field/import and dead module deleted; current algorithm example corrected. Historical plans/reviews/workstream snapshots mention old stage fields; they are historical evidence, not current schema or fixtures, and remain unchanged.

Search gate: no AlgorithmStage, to_algorithm_stage, coerce_algorithm_stage, or core.algorithm_stage hits in propstore/ or tests/.

Runtime gate: logged wrapper on tests/test_source_claim_stage_rejection.py passed all 5 cases. Log: logs/test-runs/issue-268-stage-rejection-20261028-205647.log. Full source suites and package pyright belong to PR CI and were not duplicated locally.

## Surprises
No current test or fixture uses the field. Generic strict decoding already supplies the requested rejection behavior.

Focused test used the main checkout virtual environment through UV_PROJECT_ENVIRONMENT. uv rebuilt the editable package against this worktree and synced 13 packages. Parent was informed immediately; future focused runs should use the worktree environment, avoiding shared-environment mutation.
After the test completed, parent requested restoration with uv sync from main. `uv sync --locked --dev` succeeded from the main checkout, restoring its editable package target; it also removed 91 non-selected packages, including optional embedding packages. The original optional environment state has not been reconstructed. Parent received the exact result. The override existed only in the completed test shell process.

## Next step
Parent publishes the locally committed reduction and runs PR CI including relevant source suites and package typing. This slice has reached its source/search fixed point; CI acceptance remains pending.

## Draft PR text
Title: Delete inert source-claim algorithm stage

Remove SourceClaimDocument.stage and the unused AlgorithmStage module. Existing strict source decoding now rejects the removed field in JSON, YAML, and typed conversion, so it cannot enter source identity hashing or promotion.

Validation: all 5 focused boundary acceptance cases pass through the logged pytest wrapper. Relevant source identity/finalize/promotion and package typing await PR CI.

Closes #268.
