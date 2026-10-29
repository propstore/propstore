# Issue 201: delete the provenance NI facade

## Goal
Delete the test-only provenance facade; keep byte identity owned by propstore.uri.

## State
Implementation complete locally. Logged authored-file run: 8 passed, recorded in
logs/test-runs/pytest-20261028-230444.log. Exact production/test search finds no
removed-module reference; compute_ni_uri and verify_ni_uri each have only their
propstore.uri definition. No new production path was added.

Read issue 201, AGENTS.md, CLAUDE.md, the facade, canonical URI owner,
provenance package, and both URI test files. Active control surface:
protocols:cleanup-refactor, with issue-delivery. Local implementation authorized;
publication belongs to the campaign supervisor.

## Decisions and why
Smallest change: delete the 22-line forwarding module, move two primitive
tests into tests/test_uri.py using the existing owner directly, and delete the
obsolete source-string scaffold test. No URI implementation change, replacement
facade, alias, or re-export. Issue 124 remains separate.

Iteration 1 dispositions:
- Facade forwarding edge: wrong caller existing only for old surface; delete.
- Its two functions: dead/test/scaffold surface; delete the whole module.
- Round-trip and unsupported-algorithm tests: already-owned capability;
  rewrite imports to the true owner and consolidate in tests/test_uri.py.
- Source-string assertion about an absent SHA-1 implementation: dead/test/scaffold
  surface; delete rather than retain an implementation-text guard.
- propstore.uri and provenance package exports: keep; already correct owners.

The canonical owner implements SHA-256 encoding and exact comparison; the facade
only forwards. Search found no production caller of the facade. Generic hash
behavior already lives in its generic owner, so no capability needs moving into
a family. Existing verify and micropublication consumers already import uri.

Search gates: no removed-module imports in propstore/tests, and one production
definition each for compute_ni_uri and verify_ni_uri. Runtime evidence will come
from the actively edited URI test file and PR CI; no local CI gate reruns.

## Surprises
Whole tracked-tree search also finds historical mentions in
docs/rewrite/deferred-tests.md and
reviews/2026-04-26-claude/workstreams/reports/WS-M-closure.md. These are outside
the production/test slice; they do not import or restore the removed module.

## Next step
Supervisor verifies the local commit, publishes, and obtains PR CI including
package typing and broader provenance tests. No push, PR, review, or merge has
been performed by this worker. The requested deletion slice reached fixed point;
broader runtime acceptance awaits PR CI.

## Draft PR text
Delete the unused provenance NI-URI forwarding module and consolidate its
round-trip and unsupported-algorithm tests against the canonical propstore.uri
owner. Remove the obsolete implementation-text scaffold test.

Closes #201.

Validation: logged tests/test_uri.py run passed all 8 tests. Package typing and
broader provenance tests await PR CI.
