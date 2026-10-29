# #217: delete unused structured-projection lifting wrappers

## Goal

Delete the two unused lifting result paths in `propstore.structured_projection`,
without adding a consumer or replacement. Issue #203 separately deletes the
lower attribution carriers after this change lands.

## State

Branch: `campaign/217-projection-lifting`. Local implementation complete;
publication, PR CI and merge belong to the campaign supervisor. No code was
pushed and no PR was opened by this worker.

## Decisions and why

Active control surface: `protocols:cleanup-refactor`, with `issue-delivery`.
Smallest change: approximately 115 production lines and 10 wrapper-only test
lines deleted, plus this note. Keep existing live models and semantics in their
current owner; introduce no model, map, helper, alias or replacement test.

Read the complete `structured_projection.py` and
`tests/test_projection_boundary_ws6.py`, the existing semantics tests, bridge
projection construction, world resolution, worldline argumentation and merge
mapping consumers. Exact package/test search finds only the boundary test calls
to the argument lifting wrapper; analyzer lifting has no callers.

### Iteration 1: file and dependency dispositions before edits

- `structured_projection.py`: contains dead lifting surfaces; delete those
  surfaces and retain only the existing owner capabilities. The two lifting
  result classes, lifting exception, two lifting functions and their private
  assertion-join/sorting helpers are **dead/test/scaffold surface**. Disposition:
  delete. Their attribution copying and claim-to-assertion mapping have no live
  consumer, so no capability moves to another owner.
- `AnalyzerResult` and `Mapping`/`Sequence` imports provide dependencies only to
  the deleted analyzer path: **wrong caller that exists only for the old
  surface**. Disposition: delete the import edges.
- `test_projection_boundary_ws6.py`: existing lifting calls, assertions,
  exception import and pytest import are **dead/test/scaffold surface**.
  Disposition: delete those wrapper-only lines. Existing direct lower-carrier
  assertions are left as-is for #203, never rewritten or expanded.
- Existing `StructuredArgument`, lower carriers, `StructuredProjection`, and
  `compute_structured_justified_arguments`: keep. The lower carrier removal is
  #203; the framework and argument/claim mappings have direct live consumers in
  world resolution, worldline capture and merge.
- Module heading/deferred absent-helper prose: remove lifting and obsolete
  absent-helper framing while retaining the actual owner description.

Search gate: no lifting class, exception or function names, or assertion-join
helper remains under `propstore/` or `tests/`. The same spelling `_sorted_unique`
in `merge/structured_merge.py` has its own live callers and is outside this
slice; delete only the structured-projection helper.

Runtime gates: PR CI owns the focused ASPIC/projection/world/worldline/merge
coverage and `uv run pyright propstore`. No new test is appropriate for deleting
dead wrappers; do not add an absence guard or run CI steps locally.

## Surprises

The issue's combined acceptance expressly depends on #203 removing the lower
carriers. This branch must not claim that combined criterion is complete.

## Next step

The scoped deletion is complete. Package/test search returned zero lifting
symbol references. No replacement path, carrier, alias or join was introduced.
Existing lower-carrier tests were only shortened by deleting wrapper assertions.
Runtime checks have not been run locally; await the supervisor's PR CI.

Commit this reduction, then the supervisor publishes and verifies CI. After
normal merge, #203 can delete the lower carrier and its remaining direct tests.

### PR draft

Title: Delete unused structured-projection lifting wrappers

Delete the unused argument/analyzer lifting results, exception and helper paths,
and the wrapper-only test assertions. Existing structured projection framework
and mapping consumers are unchanged. Lower attribution metadata deletion is
owned by #203.

Closes #217.

Verification: lifting-symbol search has no production/test matches; runtime
verification awaits PR CI, including the logged pytest suite and
`uv run pyright propstore`.
