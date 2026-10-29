# Issue #273: unused source notes reader

## Goal
Delete the unused nullable source notes reader and its exports. Preserve source-local notes writing and exact-tip tree synchronization.

## State
Deletion complete on branch `cleanup/source-notes-reader-273` in the isolated issue worktree. Cleanup-refactor is the active control surface. No publication authorized for this worker; parent owns publication and CI.

## Decisions and why
- Smallest change: remove the 17-line reader and three export/import entries (about 20 deleted lines); no replacement API or tests.
- Target owners remain `source/common.py` for side-file writing and `source/promote.py` for branch-tree synchronization. This issue explicitly bounds deletion to the reader; other common primitives remain outside this slice.
- Read the complete `source/common.py`, `source/__init__.py`, CLI side-file adapter, sync owner, and notes/sync tests in `tests/test_cli_source_p101.py`.
- Reader: dead/test/scaffold surface; disposition delete. Repository search found only its definition, common export, and package facade import/export. No production or test consumer obtains its nullable text representation.
- Common export and facade import/export dependency edges: deleted old surface; disposition delete the entries. No capability needs relocation.
- Notes writer, its filename constant, and CLI write-notes adapter: valid capability in its existing owner; keep. Writer reads UTF-8 text and re-encodes it, so this task does not claim arbitrary original file bytes are preserved.
- Sync: valid capability in its existing owner; keep. It captures branch tip once and iterates tree files at that commit.
- Existing tests cover source-only notes commits and notes materialization. No new guard tests and no local CI duplication; parent will read PR CI for runtime evidence.
- Search gate: search production, tests, and documentation for the deleted reader identifier; zero hits required. This task note is a historical record outside API documentation.

## Surprises
The live CLI command is `source write-notes`; the issue's prose abbreviates it as source notes. No standalone API documentation entry was found by the full repository symbol search.

## Next step
Parent publishes the local commit and reads PR CI. The requested slice has reached the search fixed point; runtime acceptance remains pending CI.

## Draft PR
Title: Delete unused source notes reader

Remove the unused nullable source notes reader and its common/package exports. Keep the existing source notes writer and captured-tip branch sync path unchanged.

Closes #273.

Validation: repository symbol search and diff inspection; runtime/type validation belongs to PR CI and has not run locally.

## Checkpoint
The reader and its three export/import entries are deleted.
Notes writing and sync owner code are unchanged.
No blocker; runtime results remain unverified until PR CI.
Next action: inspect search results and diff, then commit locally.

## Final local evidence
- Production diff: 19 deleted lines across common owner and source package facade; no new production path.
- `rg -n 'load_source_notes' propstore tests docs` returned zero hits.
- Diff inspection confirms no writer, sync, CLI, or test code changed.
- Local tests and typecheck were not run under the repository's PR-CI-only instruction.
- This reduction is committed with this note under the issue branch; parent owns publication and merge.
