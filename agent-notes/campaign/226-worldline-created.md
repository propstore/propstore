# Issue 226: remove inert worldline creation text

## Goal
Delete `WorldlineDefinition.created` without replacement or migration. Scope is issue #226; #225 identity and #203 projection provenance are excluded.

## State
Cleanup-refactor is the active control surface. Smallest change: delete one field, delete its two scaffold uses, retain the meaningful mutability test using targets, and add a fail-closed decoder regression (roughly 20 changed lines plus this note).

## Decisions and why
- Target owner: `WorldlineDefinition` remains the single charter document; pinned Quire owns strict decoding and schema/column derivation.
- The charter file passes the file-level ownership check: its remaining surfaces are typed declarations, placement, reference, and semantic invariants. Keep them; delete only the dead field.
- `created` and the test assignment/assertion are dead/test/scaffold surface. Disposition: delete. They supply no provenance capability.
- Mutable current-branch persistence is a valid already-owned capability: use the existing typed targets field directly in its test.
- Unknown-field rejection is an IO-boundary capability already owned by Quire. Use its charter codec directly, with a regression containing the removed field; no fallback or local decoder.
- Pinned Quire `CharterDoc` has `forbid_unknown_fields=True`; its `decode_document_bytes` uses strict typed YAML decoding and wraps decode failures in `DocumentSchemaError`.
- Advance the changed family and assembled registry contract versions. Registry manifests derive family contracts from their charter owner; the registry body embeds those versions. Regenerated the checked-in manifest from `build_propstore_contract_manifest().to_yaml()` and applied its output through the editing tool.

## Surprises
None affecting the requested design.

## Publication draft
Title: Remove inert worldline creation field

Delete the unused `WorldlineDefinition.created` charter field and its arbitrary-text test mutation. Existing strict Quire decoding rejects stored documents carrying the removed field. Advance the family and registry contracts and regenerate their manifest.

Closes #226.

Validation: logged authored family suite passed 7 tests. PR CI supplies app/CLI, typing, and remaining checks.

## Next step
Implemented the bounded deletion and decoder regression. The logged authored family suite passed all seven tests (`logs/test-runs/issue-226-20261028-225526.log`). Forbidden production search for `.created`/`created:` in worldline, app owner, and CLI worldline paths has zero hits; the removed field appears only in the rejection fixture. Parent publishes and obtains focused app/CLI and typing evidence from PR CI. No further cleanup slice remains for #226.
