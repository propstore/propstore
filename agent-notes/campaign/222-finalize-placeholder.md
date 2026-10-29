# Issue 222: delete inert finalize merge preview

## Goal
Delete the unused nested group-merge document and finalize-report field, without a replacement or legacy decoder.

## State
Read sources.py, finalize.py producer, common.py family load, contract manifest owner/tests, and Quire CharterDoc/charter codec wiring. Cleanup-refactor is the active control surface. Deleted the dead nested document and report field; removed obsolete documentation. Implementation committed locally; shared contract metadata update follows below.

## Decisions and why
Minimum change: remove nine production lines, remove obsolete documentation mentions, bump the changed family contract and registry manifest version, and add roughly twenty lines testing emitted report and strict rejection.
The finalize-to-group-preview dependency edge is dead/test/scaffold surface: finalize never supplies it and production search has no reader. Disposition: delete both declarations; retain the source family owner and existing Quire strict codec directly. The entire sources.py file is not deleted: its remaining source charters and nested domain documents are valid current owners; this bounded slice removes only the inert report members.
Manifest family-registry body includes each family contract version, so the changed report version requires a registry version bump as well. No schema field list is duplicated in the checked-in manifest.

## Surprises
Historical docs promise a later preview implementation that does not exist. Remove that promise and the example field.

## Next step
Parent owns publication and CI; do not push. Publish only after #226 merges. The branch integrates #226's worldline/registry metadata change; #222 advances registry to 2026.10.28.1 and source-finalize charter to 2026.10.28. Manifest regenerated through `uv run pks contract-manifest --write`.

## Iteration 1 results
- Logged `powershell -File scripts/run_logged_pytest.ps1 tests/test_source_finalize_p83a.py`: 16 passed, `logs/test-runs/pytest-20261028-225627.log`. Own worktree `.venv`; main environment untouched.
- New regression calls finalize on a real authored source, verifies the emitted report omits the field, round-trips it through the charter codec, and proves the former empty placeholder fails strict decoding.
- Search of production, docs, proposals, and workstreams has no remaining deleted symbol/field references. Tests retain only rejection assertions. Fixed point reached for requested production slice.
- `git diff --check` passed. Package typing/family contract tests await PR CI; no local CI rerun.

## PR draft
Title: Delete inert finalize parameterization group preview

Source finalization never computes or reads the parameterization-group preview. Remove its durable placeholder field and unused nested document, and delete documentation promising that output. Bump the report contract and regenerate the registry manifest.

Closes #222.

Validation: logged finalize suite passed (16 tests), including the strict decoder regression. PR CI supplies package typing and family-contract checks.
