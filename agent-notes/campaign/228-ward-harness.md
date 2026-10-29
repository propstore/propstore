# Issue #228: obsolete Ward harness

## Goal
Delete the machine-specific Ward test scaffold under #228. The issue explicitly
classifies the harness and its generated report lifecycle as dead/test/scaffold.

## State
The issue-delivery and protocols:cleanup-refactor skills are active. The isolated
branch is `campaign/228-ward-harness`. Publication belongs to the parent agent.

## Decisions and why
Smallest plan: delete the 378-line harness, remove any tracked references owned
only by it, and keep the repository-owned Ward rule unchanged. Approximately
378 deleted lines plus this task record; no replacement implementation or test.

The full harness and `.ward/rules/foreman-gate.yaml` were read. The harness owns
global-rule test sessions and a hardcoded generated report, not Propstore policy.
All script functions (`add_result`, `run_ward`, `has_output`), global counters,
test cases, and report emission are dead/test/scaffold surface: disposition
delete the file. No capability moves to another owner.

The tracked dependency search for the script name, generated report name, and
global-rule directory finds only the harness itself. These edges are deleted old
surface: delete with the file. The repository-owned rule remains at its existing
owner; no caller obtains a capability from this harness.

## Surprises
`reports/ward-shell-parser-report.md` is absent from this branch's base. No
generated Ward report is tracked. Other pre-existing scripts (`extract_concepts`,
`find_collisions`, `reconcile_vocab`) have six absolute checkout paths. Parent
authorized path-only repairs to satisfy the explicit acceptance criterion.

## Iteration 2: checkout path ownership
Read all three scripts completely and inspected existing `__file__` conventions
in scripts. Smallest additional change: six path expressions, approximately six
changed lines. The dependency edges obtain paper/input/output file locations;
classification: valid capability with wrong representation. Disposition: rewrite
each location directly relative to its existing script owner using `Path` and
`__file__`, without moving algorithms or adding a helper. This is path-only work,
not a representation cleanup of the scripts' semantic algorithms.

## Fixed-point result
Deleted the complete 378-line harness. A tracked-content search for its filename,
generated report filename, and global-rule directory has zero matches outside
this task record. `git diff --check` passes. The bounded slice reached fixed
point: no replacement, launcher, report generator, or global rules were added.
No runtime behavior remains to exercise in this deleted scaffold; no new guard
or regression test was added. Normal test and typing results remain unverified
until PR CI runs.

The six script paths now resolve from `__file__`; algorithms are unchanged. A
tracked search across Python, shell, PowerShell, batch, and YAML command/config
files (excluding paper and knowledge data) found no user-home absolute paths or
global Ward directory references. The six-line path diff and whitespace check
pass. The scripts were not executed because extraction/reconciliation writes
paper and report data; normal checks remain assigned to PR CI.

## Next step
Parent publishes the scoped commit, reads PR CI, and performs authorized normal
merge after successful required checks. Draft PR title: Delete obsolete Ward
harness. Draft body: Delete the machine-specific global Ward rule harness and
its report-writing lifecycle. Resolve the remaining concept utility paths from
their script locations instead of one user's checkout. Closes #228.
Verification: tracked-reference and user-home path searches plus diff whitespace
check pass; normal tests and typing await PR CI.
