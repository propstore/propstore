# Issue 280: delete test-only embedding decoder

## Goal
Remove the unused production float32 decoder and assert exact stored bytes at the embedding IO boundary, as specified by issue #280.

## State
Local branch `fix/delete-embedding-decoder-280`; implementation complete, focused tests passed. No publication.

## Decisions and why
The cleanup-refactor workflow is the active control surface. The bounded slice is the decoder and its two test dependency edges; live embedding generation and similarity functions remain outside the deletion slice.

- Decoder definition and export: dead/test/scaffold surface; delete.
- Round-trip test dependency: dead/test/scaffold surface; delete.
- Stored-vector inspection: IO-boundary-only carrier; rewrite the existing assertion to compare bytes with `struct.pack`, with no replacement decoder.
- Serializer and workflow functions: keep; `embed_entities` passes serialized bytes to the store, and similarity passes stored bytes directly to its store.

Source evidence: `propstore/heuristic/embed.py` owns the serializer and store protocol; `propstore/families/embeddings/declaration.py` forwards vector bytes to the Quire vector store. The decoder had no production caller. No dependency on the separate vector artifact, model identity, or similarity outcome redesigns.

## Fixed-point iteration
Deleted the decoder and export first, then removed the obsolete round-trip test and rewrote its surviving substantive stored-byte assertion. No alias, decoder, or additional production surface introduced.

Search gate: exact deleted symbol absent from production and tests. Runtime verification: modified test file through the logged wrapper; package typing remains a PR CI responsibility.

## Surprises
None.

## Next step
Commit locally and hand the branch to the campaign parent for publication and CI.

## Draft PR text
Title: Delete test-only embedding float32 decoder

Remove the unused production decoder and its round-trip test. The embedding workflow test now compares the saved vector blob directly against packed float32 bytes, preserving storage-format coverage without a test-only production decoder.

Closes #280.

Validation: focused logged embedding tests passed (6 tests), log `logs/test-runs/pytest-20261028-204816.log`. Exact symbol search over production and tests returned zero hits. PR CI remains pending.

## Checkpoint
Decoder and its export are deleted; stored-vector assertion now compares exact packed bytes.
The focused logged test command is creating the isolated worktree environment and installing locked dependencies.
No failure or blocker has been reported so far.
Next: read the test result, update this note, and commit the bounded reduction locally.
