# Issue 214: inert ASPIC compatibility surfaces

## Goal
Remove the unreachable bare claim key and the two discarded grounding parameters, as specified by issue #214. Parent owns publication and CI; this agent commits locally only.

## State
Read AGENTS.md, CLAUDE.md, issue #214, issue-delivery and cleanup-refactor. Cleanup-refactor is the active control surface. Read literal_keys.py, grounding.py, the grounded test file, build compilation callers, claim identity producers, and fragility projection callers.

## Decisions and why
Smallest change: remove the unused key class/union member/export and the two keyword-only parameters/discards (about 17 deleted lines), correct the key-count docstring, and strengthen the existing grounded interning regression with exact context identity.
The bare claim key to union/export edge is a deleted old surface: delete it. The two encoder-to-discard edges are dead/test/scaffold surfaces: delete them. No caller supplies either removed capability. Context identity remains owned by IstLiteralKey and claim_key; projection remains owned by the argumentation substrate.
All other symbols in literal_keys.py and grounding.py are kept: they provide live typed identity, grounded projection, interning, and fact folding. There is no replacement file, alias, parameter, or mechanism.

## Surprises
None affecting scope. The issue is a deletion of inert declarations, with no semantic behavior change.

## Iteration 1 results
Deleted the three inert declarations; retained the two live key variants and projection/fact-folding implementations. Strengthened the existing interning test with an explicit non-root context, exact typed-key lookup, object identity preservation, and rejection of another context's lookup.
`rg -n 'ClaimLiteralKey|complement_encoder' propstore tests` has zero hits. Full-repository search still finds historical plans, audits, rewrite inventories and reviews; these are documentation outside the production slice and were preserved. `git diff --check` passed.
The actively authored test file passed through `powershell -File scripts/run_logged_pytest.ps1 tests/test_aspic_bridge_grounded.py -q`: 10 passed. Log: `logs/test-runs/pytest-20261028-230158.log`. Dependencies were installed in this worktree's own .venv using `uv sync --dev --locked`.
Whole issue slice reached its production search fixed point. Package typing and remaining ASPIC/grounding/fragility suites await PR CI; not run locally.

## Draft PR
Title: Delete inert ASPIC literal and grounding compatibility surfaces

Remove the unreachable bare claim literal key and the two discarded grounded-projection parameters. Context-scoped claim keys, grounded keys, and the existing projection owners remain the live interfaces.

Closes #214.

Validation: focused logged grounded suite, 10 passed; production/test search has no references to the removed declarations. Full package typing and broader suites await PR CI.

## Next step
Parent publishes campaign/214-aspic-compatibility, checks PR CI, and completes the authorized delivery. This agent has not pushed, opened a PR, posted comments, or merged.
