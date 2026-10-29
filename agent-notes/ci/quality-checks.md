# CI quality checks

## Goal
Add the existing package typing and architecture contracts plus Python and
workflow quality checks to PR CI.

## State
Plan before implementation: about 45 workflow lines plus three development
dependencies and their generated lock entries. Keep the existing Python 3.13
job and logged pytest invocation. Add locked Pyright, import-linter, Ruff lint
and format checks on propstore/tests/scripts, pinned actionlint, and offline
zizmor. Each check runs after another check fails; failures remain failures.
Pin existing actions, disable persisted checkout credentials, and bound runtime.

## Decisions and why
- Ruff is already invoked by scripts/rope_delete_functions.py; use its default
  lint/format policy without adding ignores or formatting source in this task.
- Keep checks together to share checkout and the locked Python environment.
- Actionlint v1.7.12 is the upstream latest release and requires Go 1.25;
  `go run` resolves its pinned module using the runner's Go toolchain support.
- Resolve Python tool versions with the existing 14-day dependency age policy.
- Official tag API confirms the checkout v6.0.2, setup-uv v8.1.0 and
  setup-python v6.2.0 pins. Official Ruff and zizmor docs support their
  Python-package distribution and the selected check/offline commands.

## Surprises
Pyright has strict configuration but is absent from development dependencies.

## Next step
Workflow and dependency lock are implemented. Locked tools are Pyright
1.1.414, Ruff 0.17.0, zizmor 1.30.1, and nodeenv 1.11.0. Existing age policy
also resolves certifi from 2026.10.19 to 2026.7.22. No local CI steps were run.
Commit locally and hand the branch to the parent for publication and hosted CI.

## PR draft
Title: Enforce package and workflow quality checks in CI

The Python 3.13 check now runs strict package Pyright, the existing import
contracts, Ruff lint and formatting checks for propstore/tests/scripts, and
actionlint plus offline zizmor alongside logged tests. Each available check
still executes when another fails, preserving all failure output.

Pin action revisions, disable persisted checkout credentials, handle merge
groups, and bound the job to 30 minutes. Add the Python tools to the locked
development environment under the existing dependency age policy.

Validation: dependency lock generated successfully; hosted CI pending. Local
CI commands were not run, per repository instructions.
