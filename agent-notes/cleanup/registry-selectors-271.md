# Goal
Implement #271: delete the three redundant registry selector views and use existing registry/charter owners directly.

# State
Isolated branch `cleanup/registry-selectors-271`, based on fresh origin/master. Selector deletion and all five caller module updates complete. Active control surface: protocols:cleanup-refactor.

# Decisions and why
Smallest change: delete 18 selector lines, change the FK comprehension to iterate semantic charters, and update five test modules (roughly 40 changed lines). Preserve registry assembly, charter selection, FK lifting, init and dependency-order import behavior.

Read slice: propstore/families/registry.py; tests/test_semantic_family_registry.py; tests/test_coreference_family.py; tests/test_temporal_family.py; tests/test_worldline_family.py; tests/test_semantic_passes.py; sibling quire/quire/families.py registry owner.

Broken-edge dispositions before edits:
- Registry membership assertions in coreference, temporal, worldline and semantic-pass tests: wrong callers that exist only for the old surface; rewrite to already-owned PROPSTORE_FAMILY_REGISTRY.names().
- Import-order test obtaining families through the redundant projection: already-owned capability that must use its true owner directly; iterate semantic_import_families() directly, preserving target-before-source assertions.
- semantic_foreign_keys obtaining semantic membership through a names projection: already-owned capability that must use its true owner directly; iterate semantic_charters(), resolve each charter's family in the registry, retain the registry's lifted FK specs.
- The three selector definitions: deleted old surface; delete without replacements. Other symbols in registry.py remain outside this explicitly bounded selector slice; deleting the entire assembled registry would violate the issue's preservation requirement.

Search gate: zero occurrences of the three deleted selector identifiers in production and tests. Runtime validation belongs to PR CI; do not duplicate CI locally. Existing edited test files exercise registry membership, import order and semantic FKs.

# Surprises
None.

# Next step
Commit locally, then parent publishes and reads PR CI. No local CI steps were run. Search found zero old selector occurrences in propstore/ and tests/; all six explicitly preserved public functions remain defined once. `git diff --check` passed. Production/test diff is 11 insertions and 33 deletions across six files; no wrapper or replacement selector added. This bounded slice reached search fixed point; runtime validation awaits PR CI.

# Draft PR
Title: Delete redundant family registry selector views

Remove the three registry projections named by #271. Membership tests use the registry directly, import-order assertions use the import-family owner, and semantic FK collection traverses semantic charters while retaining registry-derived specs. Preserve live charter, init and import APIs.

Closes #271. Validation: PR CI pending publication by parent; no local duplicate CI gate.
