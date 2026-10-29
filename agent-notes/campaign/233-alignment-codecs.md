# Issue 233: alignment codec wrappers

## Goal
Delete the test-only arbitrary-file persistence path; retain typed alignment family and live workflows. Parent owns publication, CI and merge.

## State
Deletion complete on branch `campaign/233-alignment-codecs`, isolated worktree `C:/Users/Q/code/propstore-233`. Exactly 45 source/test lines removed. No replacement persistence surface added.

## Decisions and why
`protocols:cleanup-refactor` is the active control surface. Smallest change: delete both loose-file functions, their Path import, and the sole codec round-trip test/imports, about 45 removed lines across two files. No replacement or new tests: issue explicitly deletes the scaffold test and retains existing production-path coverage.

Target owner: `ConceptAlignmentArtifact` charter and `repo.families.concept_alignments` with `ConceptAlignmentRef`. Forbidden surfaces: arbitrary-Path alignment read/write wrappers and replacement aliases/adapters.

Dependency classification before edits: the source functions expose ConceptAlignmentArtifact/arbitrary Path persistence; classified dead/test/scaffold surface, disposition delete. The test-to-functions dependency solely exercises that dead path; classified dead/test/scaffold surface, disposition delete test and imports. Path imports in both files exist solely for those surfaces; delete them. All other classification/build/align/decide/promote functions remain in the existing semantic owner unchanged.

Primary evidence: source/alignment.py defines wrappers at lines 246-259; tracked-text search finds only test_alignment_classification.py callers. families/alignment.py owns the typed charter, fixed proposal branch, placement and reference. source/alignment.py align/decide/promote persist through concept_alignments.save and _load_repo_alignment reads through its load. tests/test_concept_alignment_cli.py and tests/test_concept_alignment_promotion.py retain family-backed reload/integration coverage.

## Surprises
Tracked historical reports/reviews/workstream logs mention the deleted names; these are historical documentation outside production scope and remain untouched.

## Next step
Commit the scoped surfaces and this note, then hand off to parent. Runtime checks are deferred to parent PR CI; no tests authored or run locally, no local CI reruns or main environment use. `git grep` for deleted names under propstore/tests returned zero hits. Full tracked search had only the deleted definitions/test and historical reports/reviews/workstream logs. Diff inspection confirms the live family owner and workflows are unchanged.

## Draft PR
Title: Delete test-only loose-file alignment codecs

Body: Deletes the arbitrary-file alignment save/load wrappers and their sole round-trip test. Alignment persistence continues through the registered typed family; existing classification, CLI and promotion coverage remains.

Closes #233.

Validation: production/test search for deleted symbols; PR CI must run logged alignment tests and package Pyright.
