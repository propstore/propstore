# Issue #235: delete the unused diagnostic renderer

## Goal

Delete the zero-caller semantic-pass batch renderer without replacement. Active control surface: `protocols:cleanup-refactor`.

## State

Local isolated branch `cleanup/diagnostic-renderer-235`, based on `origin/master`. Publication is reserved to the campaign supervisor.

## Decisions and why

Smallest plan: delete the 11-line `propstore/semantic_passes/diagnostics.py`; no caller edits, replacement, tests, or diagnostic semantic changes.

Target architecture: `PassDiagnostic` owns rendering; typed `PassResult` and `PipelineResult` retain diagnostics; actual boundaries invoke the owner directly.

Iteration 1 slice read: the entire diagnostics module, `semantic_passes/types.py`, `semantic_passes/runner.py`, shallow package initializer, `build_diagnostics.py` through its lowering function, and `tests/test_semantic_passes.py`.

The batch renderer obtains string rendering from `PassDiagnostic.render()` and merely maps it over a tuple. Classification of that dependency edge: **dead/test/scaffold surface**. Disposition: **delete** the whole module. Repository-wide Python search found only its definition; no importing caller exists. The owning runtime object and result types are retained unchanged. `build_diagnostics.py:85` already invokes `diagnostic.render()` directly; `tests/test_semantic_passes.py:187` directly exercises rendering.

Forbidden surfaces: the deleted module, `render_diagnostics`, and replacement batch helpers or exports.

## Surprises

None. No broken dependency edge was exposed by the search.

## Verification

Before deletion, repository-wide Python search for `render_diagnostics|semantic_passes\.diagnostics` found only the definition in the module being deleted. After deletion, repeat that search and inspect the diff. Runtime acceptance belongs to PR CI: logged semantic-pass tests and `uv run pyright propstore`. No duplicate local CI gate is run and no guard test is added for this pure deletion.

## Next step

The module is deleted. Post-deletion repository-wide Python search returned zero references to the helper or import path; the production diff is exactly 11 deleted lines. This slice reached its search fixed point without replacement or caller edits. Commit source plus this note locally; the supervisor publishes the PR and follows its CI. Runtime acceptance remains unverified until CI completes.

## Draft PR

Title: Delete unused semantic-pass diagnostic renderer

Deletes the uncalled batch-rendering module. Typed pipeline diagnostics and their existing owner rendering method remain unchanged. No replacement surface is introduced. Closes #235.

Validation: zero repository Python references to the deleted helper/import path after deletion. Runtime acceptance pending PR CI; local CI was not duplicated.
