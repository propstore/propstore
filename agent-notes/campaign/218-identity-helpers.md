# Issue #218: obsolete parallel claim identity helpers

## Goal
Delete the uncalled alternate claim-identity surface without changing live identity derivation, typed source references, or generic/source URI behavior.

## State
Implementation complete locally on `campaign/218-identity-helpers`; publication is reserved to the coordinating agent. No local CI steps run. PR CI must verify logged URI/authority/trusty/repository-import tests and `uv run pyright propstore`.

## Decisions and why
Active control surface: `protocols:cleanup-refactor`, with `issue-delivery` scoped to #218. Smallest change: roughly 60 deleted lines plus documentation corrections; no new abstraction or alternate parser.

Target owners: `ClaimLogicalIdDocument.formatted`, the source `FamilyReferenceIndex`, and `families.identity.claims` remain the typed reference and canonical identity owners.

Iteration 1 covers `families/identity/logical_ids.py`, `uri.py`, and the URI entry in `docs/rewrite/deferred-tests.md`. Read those files, `families/identity/claims.py`, `families/identity/__init__.py`, source claim normalization and reference indexes, source logical document definitions, and existing URI/authority/trusty/import tests before edits.

- The six public regex constants, private logical regex, parser, formatter and claim tag minter are dead/test/scaffold surfaces: delete. Repository searches found declarations only, with historical documentation mentions but no callers. No broken dependency edges were exposed.
- Both logical token normalizers are already-owned capabilities: keep their existing implementations. Canonical derivation and source normalization call them directly.
- Generic tag, concept/source tag and ni URI functions, URI constants, and typed authority validation are already-owned capabilities: keep unchanged. Their existing module remains their true owner.
- The URI module claim-tag framing and deferred-tests entry are stale descriptions of the deleted surface: correct them to name the live canonical claim owner.
- Historical plans and review reports record past code; leave those records intact. They do not publish a current canonical tag identity contract.

## Surprises
The URI module introduction also claimed that claims use tag URIs; corrected alongside deletion to satisfy the documentation acceptance criterion.

## Verification
Search gates: named deleted symbols and claim-tag URI syntax across production/tests/current docs returned zero hits. `git diff --check` passed. Existing live-path tests are retained; no new guard was requested or added for uncalled deletions. Runtime gates remain pending PR CI, as local reruns are prohibited.

## Next step
Coordinator reviews the diff, publishes the scoped branch/PR, and obtains authoritative PR CI. No push or PR was created by this agent.

## Draft PR
Title: Delete obsolete parallel claim identity helpers

Remove unused logical-ID parser/formatter and regex declarations, plus the source-local claim tag URI minter. Keep typed source reference resolution and canonical identity derivation unchanged; correct URI documentation to point to the canonical claim owner.

Closes #218.

Validation: deletion searches completed locally; logged URI/authority/trusty/repository-import tests and `uv run pyright propstore` pending PR CI.
