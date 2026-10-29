# Issue #239: remove unused resource existence helper

## Goal
Delete only `propstore.resources.resource_exists`, preserving required resource reads and iteration. Active control surface: `protocols:cleanup-refactor`.

## State
Implementation complete, prepared for local commit. Isolated branch `cleanup/resource-exists-239` starts from `origin/master`; initial worktree clean.

## Decisions and why
Smallest change: delete the six-line function block in `propstore/resources.py`, with no replacement and no caller edits. Issue #239 explicitly preserves the rest of the file, so its bounded deletion overrides the workflow's general whole-file deletion step.

Read the complete resources owner and the consumers in `propstore/app/project_init.py`, `propstore/heuristic/rule_extraction.py`, and `propstore/heuristic/predicate_extraction.py`. Repository-wide `rg -n resource_exists .` finds only the function definition. The relative-path-to-boolean edge is **dead/test/scaffold surface**; disposition: delete the dead surface. There is no broken caller to repair or generic capability to move.

Surviving dispositions: keep `_development_mode`, `_is_development_mode`, `_resource`, `load_resource_text`, and `iter_resource_files` in their existing resource IO owner. The required readers call `read_text` directly; iteration calls `iterdir` and filters files. Initialization and prompt consumers already use those APIs directly.

## Surprises
None. No new tests or local CI gates are warranted for the zero-caller deletion. Parent campaign owns PR publication and CI, including the issue's logged initialization/proposal tests and package Pyright acceptance.

## Next step
Production/test search `rg -n resource_exists propstore tests` returned zero hits after deletion. Diff inspection confirms exactly six source lines removed and no caller edits. Requested deletion reached its search fixed point; runtime acceptance remains pending PR CI. Commit source and this note; parent then publishes, reads PR CI, and merges when authorized and green.

## Draft PR body
Delete the unused `resource_exists()` packaged-resource preflight. Required text loading and resource iteration retain their existing direct consumers and failure behavior.

Validation: repository search found no caller before deletion; production/test search after deletion returned zero hits. PR CI pending publication by parent campaign.

Closes #239.
