from pathlib import Path

import pytest
from click.testing import CliRunner

from propstore.cli import cli
from propstore.merge.merge_commit import (
    MergeAncestryError,
    build_repository_merge_framework,
    plan_merge_commit,
)
from propstore.repository import Repository


@pytest.mark.parametrize("target", ["left", "joined"])
def test_unrelated_roots_rejected_before_publication(tmp_path: Path, target):
    repo = Repository.init(tmp_path / "knowledge")
    git = repo.require_git()
    left = git.commit_flat_tree({}, "left root", parents=(), branch="left")
    right = git.commit_flat_tree({}, "right root", parents=(), branch="right")
    before = git.branch_sha(target)
    with pytest.raises(MergeAncestryError, match="No common ancestor"):
        build_repository_merge_framework(repo, "left", "right")
    for command in ("inspect", "commit"):
        result = CliRunner().invoke(
            cli,
            [
                "-C",
                str(repo.root),
                "merge",
                command,
                "left",
                "right",
                "--target-branch",
                target,
            ],
        )
        assert result.exit_code != 0
        for expected in ("No common ancestor", "left", left, "right", right):
            assert expected in result.output
        assert git.branch_sha(target) == before


def test_additional_head_must_descend_from_real_primary_base(tmp_path: Path):
    repo = Repository.init(tmp_path / "knowledge")
    git = repo.require_git()
    base = git.commit_flat_tree({}, "empty root", parents=(), branch="base")
    for branch in ("left", "right", "third"):
        git.commit_flat_tree({}, branch, parents=(base,), branch=branch)
    plan = plan_merge_commit(repo, "left", "right", target_branch="joined")
    assert plan.base_sha == base
    build_repository_merge_framework(
        repo, "left", "right", additional_branches=("third",)
    )
    orphan = git.commit_flat_tree({}, "orphan root", parents=(), branch="orphan")
    with pytest.raises(MergeAncestryError) as failure:
        build_repository_merge_framework(
            repo, "left", "right", additional_branches=("orphan",)
        )
    assert orphan in str(failure.value)
    assert base in str(failure.value)
    assert git.branch_sha("joined") is None
