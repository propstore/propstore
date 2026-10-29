# Issue 231: delete the unwired PROV-O export

## Goal

Implement issue #231's existing disposition only: delete the unused PROV-O export module and its direct tests. Keep canonical typed provenance, named-graph persistence, composition, and source/import/alignment consumers intact. Parent owns publication, PR CI, and normal merge; this worker must not publish.

## State

The active control surface is `protocols:cleanup-refactor`. Branch: `campaign/231-provo-export`, isolated worktree `../propstore-campaign-231` from `origin/master`. Scoped deletion and note committed as `Delete the unwired PROV-O export module`. No push or publication performed; PR CI is pending parent publication.

## Decisions and why

Smallest plan: delete `propstore/provenance/prov_o.py` (109 lines) and `tests/test_prov_o_export.py` (148 lines); remove stale exporter references from the two adjacent module docstrings (about 10 lines changed). Add no replacement export surface or new guard/test. Runtime verification belongs to PR CI; no actively authored test remains to run locally.

Target owner: canonical `Provenance`, its witness/status objects and named-graph/note/composition functions in `propstore/provenance/__init__.py` remain unchanged. Shared JSON-LD constants remain in `_jsonld.py`.

Forbidden surfaces: the complete `prov_o.py` module, both exporters, their private node/document helpers, and direct export tests. Search gate: no `provenance_to_prov_o`, `to_prov_o`, `provenance.prov_o`, fabricated anonymous export ID, or `prov:Activity` in production/tests after deletion.

### Iteration 1: dependency-edge classifications before edits

- `Provenance` / `ProjectionFrameProvenanceRecord` -> PROV-O dictionaries: **dead/test/scaffold surface**; disposition **delete** the entire exporter file. Whole-file read shows only export conversion code. Tracked search finds no executable callers outside `tests/test_prov_o_export.py`.
- `tests/test_prov_o_export.py` -> exporter functions: **dead/test/scaffold surface**; disposition **delete** the entire test file, as explicitly required by #231. These tests prove only the unrequested export representation.
- `_jsonld.py` / `records.py` docstrings -> removed export module: **dead/test/scaffold surface**; disposition **delete** stale documentation references. Runtime constants and record implementation stay intact; #203 separately owns inert-record removal.
- Canonical provenance -> `_jsonld.py` constants: **already-owned capability that must use its true owner directly**; disposition **keep** existing direct owner imports. `__init__.py:242-275` encodes/decodes the typed named graph; `:278-311` persists/reads git notes; `:198-239` composes typed provenance. No exporter participates.
- Source alignment -> canonical provenance: **already-owned capability that must use its true owner directly**; disposition **keep**. `source/alignment.py:181-195` reads the import note, checks status/operation and obtains lineage/witness origin directly.

Historical reports, reviews, and rewrite inventories mention the old module but are not production dependencies; leave those historical records unchanged.

## Surprises

The exporter contains the sibling `to_prov_o()` function as well; deleting its containing module and the entire direct export test file is explicitly required by #231. The record itself remains for #203.

## Verification

Deletion reached the requested fixed point. `git grep -n -E 'provenance_to_prov_o|to_prov_o|provenance.prov_o|urn:propstore:provenance:anonymous|prov:Activity' -- propstore tests` returned zero matches. `git diff --check` passed. The substantive diff is four files, four inserted docstring lines and 263 deletions. Canonical provenance has no diff. No local tests or typing checks were run. PR CI must supply the logged provenance/named-graph/source/import/alignment tests and `uv run pyright propstore`; no local CI rerun is authorized.

## Draft PR

Title: Delete the unwired PROV-O export module

Delete the unused PROV-O dictionary exporter and its direct export tests. Remove adjacent documentation references while retaining canonical typed provenance, named-graph/git-note persistence, composition, and shared JSON-LD constants.

Closes #231.

Verification: tracked production/test search and scoped diff inspection; runtime and typing results to be filled from PR CI by the parent.

## Next step

Parent publishes the branch and draft PR, watches CI, repairs any scoped failures, and performs the authorized normal merge. No further cleanup slice belongs to #231; #203 owns the remaining projection record.
