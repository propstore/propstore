# Issue 222: delete inert finalize merge preview

## Goal
Delete the unused nested group-merge document and finalize-report field, without a replacement or legacy decoder.

## State
Read sources.py, finalize.py producer, common.py family load, contract manifest owner/tests, and Quire CharterDoc/charter codec wiring. Cleanup-refactor is the active control surface. No implementation edits yet.

## Decisions and why
Minimum change: remove nine production lines, remove obsolete documentation mentions, bump the changed family contract and registry manifest version, and add roughly twenty lines testing emitted report and strict rejection.
The finalize-to-group-preview dependency edge is dead/test/scaffold surface: finalize never supplies it and production search has no reader. Disposition: delete both declarations; retain the source family owner and existing Quire strict codec directly. The entire sources.py file is not deleted: its remaining source charters and nested domain documents are valid current owners; this bounded slice removes only the inert report members.
Manifest family-registry body includes each family contract version, so the changed report version requires a registry version bump as well. No schema field list is duplicated in the checked-in manifest.

## Surprises
Historical docs promise a later preview implementation that does not exist. Remove that promise and the example field.

## Next step
Delete the surface and documentation; add focused codec regression and run only its actively authored test file using the logged wrapper in this worktree's own environment. Parent owns publication and CI; do not push.
