Persist checked admission in each derived snapshot, bound to the checked claim
content and pass version. World and grounding inputs now use admitted claims;
authored documents and diagnostics remain inspectable through explicit quarantine
policy. Build reports count quarantined artifacts rather than diagnostic rows.

Dependent references distinguish quarantined subjects from missing ones. Inference
licenses remain available to mark unsupported conclusions as inferred, without
allowing quarantined premises to create arguments.

Three logged focused regressions passed, covering blocked values, equations,
conflicts, grounding, ATMS and ASPIC input, stale admission and repair/revalidation.
Full tests, typing and other checks run on this PR.

Fixes #144.
Refs #209.
