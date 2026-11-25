"""Owner-layer repository history cores: log / diff / show / checkout.

These exercise the history owner and the CLI mapping for an unknown revision.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner
from quire.refs import RefName

from propstore.cli import cli
from propstore.history import (
    BranchNotFoundError,
    CommitNotFoundError,
    build_commit_show_report,
    build_diff_report,
    build_log_report,
    checkout_commit,
    classify_log_operation,
)
from propstore.repository import Repository
from tests.merge_commit_helpers import author_concept, author_obs_claim, init_repo


def test_diff_and_show_reports_project_snapshot_history(tmp_path: Path) -> None:
    repo = Repository.init(tmp_path / "knowledge")
    git = repo.git
    assert git is not None

    git.commit_files({"concepts/a.yaml": b"v: 1\n"}, "add a")
    git.commit_files(
        {"concepts/a.yaml": b"v: 2\n", "concepts/b.yaml": b"v: 1\n"},
        "update files",
    )
    sha = git.head_sha()
    assert sha is not None

    diff = build_diff_report(repo, None)
    shown = build_commit_show_report(repo, sha)

    assert diff.has_changes
    assert diff.added == ("concepts/b.yaml",)
    assert diff.modified == ("concepts/a.yaml",)
    assert shown.sha == sha
    assert shown.message == "update files"
    assert shown.changes.added == ("concepts/b.yaml",)


def test_build_commit_show_report_rejects_missing_commit(tmp_path: Path) -> None:
    repo = Repository.init(tmp_path / "knowledge")
    with pytest.raises(CommitNotFoundError, match="Commit not found: missing"):
        build_commit_show_report(repo, "missing")


def test_diff_reports_missing_commit_to_owner_and_cli(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "knowledge")
    with pytest.raises(CommitNotFoundError, match="deadbeef"):
        build_diff_report(repo, "deadbeef")
    result = CliRunner().invoke(cli, ["-C", str(repo.root), "diff", "deadbeef"])
    assert result.exit_code == 2
    assert "Commit not found: deadbeef" in result.output


def test_diff_uses_captured_ref_after_it_moves(tmp_path: Path, monkeypatch) -> None:
    repo = init_repo(tmp_path / "knowledge")
    git = repo.require_git()
    first = author_obs_claim(repo, "first", "first observation")
    git.create_branch("selected", source_commit=first)
    expected = build_diff_report(repo, first)
    diff = git.diff_commits

    def advance_then_diff(commit1=None, commit2=None):
        author_obs_claim(repo, "second", "second observation", branch="selected")
        assert commit1 == first
        return diff(commit1, commit2)

    monkeypatch.setattr(git, "diff_commits", advance_then_diff)
    assert build_diff_report(repo, "refs/heads/selected") == expected


def test_history_preserves_broken_ref_storage_error(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "knowledge")
    repo.require_git().write_ref(RefName("refs/heads/broken"), "a" * 40)
    with pytest.raises(KeyError):
        build_diff_report(repo, "refs/heads/broken")


def test_diff_and_show_resolve_a_root_commit(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "knowledge")
    git = repo.require_git()
    root = git.commit_flat_tree(
        {"first": git.store_blob(b"first")}, "root", parents=(), branch="root"
    )
    for revision in (root, root[:12], "refs/heads/root"):
        assert build_diff_report(repo, revision).added == ("first",)
        assert build_commit_show_report(repo, revision).sha == root
    git.create_branch(root, source_commit=git.head_sha())
    assert build_commit_show_report(repo, root).sha == root


def test_build_diff_report_against_explicit_commit(tmp_path: Path) -> None:
    repo = Repository.init(tmp_path / "knowledge")
    git = repo.git
    assert git is not None
    git.commit_files({"concepts/a.yaml": b"v: 1\n"}, "add a")
    target = git.head_sha()
    assert target is not None

    diff = build_diff_report(repo, target)

    assert diff.added == ("concepts/a.yaml",)
    assert diff.modified == ()


def test_log_report_classifies_operations_and_orders_recent_first(
    tmp_path: Path,
) -> None:
    repo = Repository.init(tmp_path / "knowledge")
    git = repo.git
    assert git is not None
    git.commit_files({"concepts/a.yaml": b"v: 1\n"}, "Add concept: alpha")
    git.commit_files({"notes/x.yaml": b"v: 1\n"}, "scratch")

    report = build_log_report(repo, count=10, branch_name=None, show_files=False)

    assert report.branch == git.primary_branch_name()
    messages = [entry.message for entry in report.entries]
    assert messages[0] == "scratch"
    assert "Add concept: alpha" in messages
    by_message = {entry.message: entry.operation for entry in report.entries}
    assert by_message["Add concept: alpha"] == "concept.add"
    assert by_message["scratch"] == "commit"


def test_log_report_show_files_attaches_change_sets(tmp_path: Path) -> None:
    repo = Repository.init(tmp_path / "knowledge")
    git = repo.git
    assert git is not None
    git.commit_files({"concepts/a.yaml": b"v: 1\n"}, "add a")

    report = build_log_report(repo, count=1, branch_name=None, show_files=True)

    assert report.entries[0].added == ("concepts/a.yaml",)


def test_log_report_rejects_unknown_branch(tmp_path: Path) -> None:
    repo = Repository.init(tmp_path / "knowledge")
    with pytest.raises(BranchNotFoundError, match="Branch not found: nope"):
        build_log_report(repo, count=5, branch_name="nope", show_files=False)


def test_log_report_summarizes_merge_commit(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "knowledge")
    git = repo.require_git()
    primary = git.primary_branch_name()

    git.create_branch("left", source_commit=git.head_sha())
    git.create_branch("right", source_commit=git.head_sha())
    author_obs_claim(repo, "claim_left", "left says so", branch="left")
    author_obs_claim(repo, "claim_right", "right says so", branch="right")

    from propstore.merge.merge_commit import create_merge_commit

    merge_sha = create_merge_commit(repo, "left", "right", target_branch=primary)

    report = build_log_report(repo, count=5, branch_name=primary, show_files=False)
    merge_entries = [entry for entry in report.entries if entry.sha == merge_sha]
    assert len(merge_entries) == 1
    merge_entry = merge_entries[0]
    assert merge_entry.operation == "merge.commit"
    assert merge_entry.merge is not None
    assert {merge_entry.merge.branch_a, merge_entry.merge.branch_b} == {"left", "right"}
    assert merge_entry.merge.argument_count >= 2


def test_checkout_commit_rejects_missing_commit(tmp_path: Path) -> None:
    repo = Repository.init(tmp_path / "knowledge")
    with pytest.raises(CommitNotFoundError, match="Commit not found: missing"):
        checkout_commit(repo, "missing")


def test_checkout_commit_rebuilds_sidecar_from_concept_snapshot(tmp_path: Path) -> None:
    repo = init_repo(tmp_path / "knowledge")
    author_concept(repo, "concept:mass", name="mass")
    sha = repo.require_git().head_sha()
    assert sha is not None

    report = checkout_commit(repo, sha)

    assert report.commit == sha
    assert report.rebuilt is True


def test_classify_log_operation_labels_import_and_merge() -> None:
    assert classify_log_operation("Import repo-b at 0123456789ab", ()) == "repo.import"
    assert classify_log_operation("Merge left and right", ("a", "b")) == "merge.commit"
    assert classify_log_operation("anything", ()) == "commit"
