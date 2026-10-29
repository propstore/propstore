# Issue #238: delete unused calibrated probability facade

## Goal
Delete only the uncalled three-number conversion facade and its wrapper-only tests. Preserve the live categorical/corpus paths and doxa opinion owner. Active control surface: protocols:cleanup-refactor.

## State
Deletion committed locally on `cleanup/calibration-facade-238`, based on origin/master. Commit subject: `Delete unused calibrated probability facade`. No publication authorized for this worker.

## Decisions and why
- Smallest plan: delete the 28-line facade section, its import and three direct tests (about 25 lines), and remove stale docstring mentions. No replacement API.
- `propstore/heuristic/calibrate.py` read completely. File disposition: keep the production calibration owner; issue #238 explicitly limits deletion to one surface, so the workflow's whole-file deletion rule is bounded by that instruction.
- `calibrated_probability_to_opinion`: dead/test/scaffold surface; disposition delete. It validates two numbers then delegates to doxa. No production caller found.
- `tests/test_calibrate.py` read completely. Its facade import and three direct tests: wrong caller that exists only for the old surface; disposition delete those paths. Other calibration tests: keep real owner integrations.
- `CorpusCalibrator`, categorical prior types, validation/resolution helpers, categorical conversion, and imported substrate metrics: keep existing production behavior. `propstore/heuristic/classify.py` imports categorical conversion and calls it in `_resolved_opinion`; corpus conversion directly uses doxa. No machinery moves to another owner.
- Doxa probability conversion stays with doxa; no new direct doxa tests or fixture facade.

## Surprises
Assigned worktree did not initially exist; created the assigned branch/worktree from origin/master.

## Verification
- Before deletion, exact symbol search in propstore/tests/docs finds definition, test import, and three test calls only.
- After deletion, `rg -n calibrated_probability_to_opinion propstore tests docs` returns zero hits (exit 1).
- Diff reviewed: facade section, its three direct tests/import, and stale module docstrings only. Corpus/categorical code and all other opinion callers are unchanged.
- PR CI owns runtime calibration/classifier tests and package typing. No local duplicate CI gate. No new tests are needed for deleting a test-only surface.

## Next step
Supervisor publishes and watches PR CI; runtime and typing acceptance are pending there. Requested deletion slice has reached its search fixed point; no further local slice.

## Draft PR
Title: Delete unused calibrated probability facade

Deletes the uncalled `calibrated_probability_to_opinion` wrapper and its three direct tests. Corpus calibration and categorical conversion continue using their existing owners; probability-to-opinion algebra remains in doxa.

Closes #238.

Validation: exact facade search in propstore/tests/docs has zero hits; calibration/classifier tests and `uv run pyright propstore` are pending PR CI.
