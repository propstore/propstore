# Issue #270: contract coverage selectors

## Goal
Delete the two test-only contract selectors, preserving the manifest builder exactly.

## State
The cleanup-refactor workflow is active. Isolated branch `cleanup/contract-selectors-270` contains only this issue's changes against master. Parent inspection established that #271 changes different files and is not a prerequisite; the unpublished branch was rebased to remove that ancestry dependency.

## Decisions and why
Smallest plan: remove roughly 30 lines of wrappers/imports from contracts.py and change the two coverage comprehensions/imports in test_contract_manifest.py. No new selector or collection.
The artifact-family test edge is an already-owned capability that must use its true owner directly: iterate PROPSTORE_FAMILY_REGISTRY.families and inspect each artifact_family.contract_version. Disposition: rewrite to the existing registry owner.
The semantic-FK test edge is an already-owned capability that must use its true owner directly: semantic_foreign_keys in families.registry owns semantic charter selection and registry FK access. Disposition: use that owner directly.
Both contract selector functions and their type-only imports are deleted old surfaces: delete. Other contract module symbols remain outside this bounded slice; keep the live pass/stage iterators and builder unchanged.

## Surprises
Initial branch ancestry included #271; source inspection showed no dependency and parent removed that ancestry before publication.

## Next step
Parent publishes and follows full PR tests. Package typing execution approval is pending at campaign level; it has not run.

## Iteration 1 result
Deleted both selectors and their unused imports before rewriting the two test dependency edges to the owners named above. No replacement surface was added. The contracts.py diff contains only selector/import deletion; build_propstore_contract_manifest remains byte-for-byte unchanged. Live pass/stage iterators remain unchanged.
Search gate: `rg -n 'iter_artifact_families|iter_semantic_foreign_keys' propstore tests` produced zero hits.
Runtime evidence: logged wrapper for `tests/test_contract_manifest.py -q` passed all 10 tests; log `logs/test-runs/pytest-20261028-205725.log`.
Scope reached fixed point; local commit follows. No push, PR, or package-wide local typing run.

## Draft PR text
Title: Delete test-only contract coverage selectors

Remove the artifact-family and semantic-FK selectors from propstore.contracts. Coverage assertions now inspect the existing family registry and semantic-FK registry owner directly, preserving contract-version checks without a second discovery surface. Manifest construction and live pass/stage iterators are unchanged.

Validation: logged contract-manifest test file, 10 passed before the code-identical ancestry change. Full tests run in PR CI; package typing execution remains pending.

Closes #270.

## Checkpoint
Read the complete contracts module, contract tests, registry owner, issue #270, and cleanup workflow.
Both selector names occur only in contracts.py and the two coverage tests.
Manifest construction already calls contract_entries directly.
Implementation is locally committed; publication and acceptance remain.

## Final checkpoint
Local commit completed on `cleanup/contract-selectors-270`; source/test/note changes are committed.
The focused logged contract test passed all 10 cases and forbidden selector search was zero-hit.
No publication occurred; PR CI remains parent-owned.
Next action: parent publishes the independent scoped branch.
