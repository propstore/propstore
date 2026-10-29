# Issue 281: remove unused CLI success constant

## Goal
Delete the unused success exit-code constant without replacing normal Click returns.

## State
The one-line production deletion is complete on branch `cleanup/unused-cli-success-281`.
Publication and CI monitoring belong to the parent campaign agent.

## Decisions and why
The cleanup-refactor workflow controls this bounded slice. The issue explicitly
classifies the declaration as dead/test/scaffold surface; disposition: delete.
The smallest change is one production line, with no replacement or added test.
The two live failure constants, error rendering, and command returns stay as written.

## Iteration 1
Read the whole `propstore/cli/helpers.py`, existing CLI error-rendering tests,
initialization success tests, root CLI adapter, and CI workflow.
The pre-deletion production/test search found only the unused declaration.
No caller edge needs rewriting. Historical review prose is outside production scope.
Search gate: no occurrence of the deleted identifier in `propstore` or `tests`.
Runtime verification is deferred to the PR CI; no local CI gate was run.

## Surprises
The current CI workflow runs logged pytest but does not run package pyright.
The parent was informed because the issue also requests package typing verification.

## Next step
Parent inspects and publishes the branch, monitors CI, and completes the authorized merge.

## Draft PR
Title: Delete unused CLI success exit-code constant

Remove the unused success constant from the CLI helpers. Successful commands keep
returning normally; both live failure constants and error rendering are unchanged.

Validation: production/test search has no remaining reference. Existing logged pytest
coverage runs on the PR; runtime checks have not been run locally.

Closes #281.
