from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner
from quire.sqlalchemy_store import readonly_session

from propstore.app.temporal import anchor_description_claim, declare_temporal_frame
from propstore.cli import cli
from propstore.core.lemon.temporal import DescriptionTemporalAnchor, TemporalFrame
from propstore.families.temporal import (
    DescriptionTemporalAnchorDoc,
    TemporalRepository,
    stated_provenance,
)
from propstore.repository import Repository
from propstore.world.queries import select_description_temporal_anchors
from tests.merge_commit_helpers import author_obs_claim


@pytest.mark.parametrize("bound", ["valid_from", "valid_until"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_invalid_coordinate_never_reaches_storage(tmp_path: Path, bound, value):
    provenance = stated_provenance()
    fields = {
        "anchor_id": "a",
        "claim_id": "c",
        "frame_id": "f",
        "provenance": provenance,
    }
    bounds = {bound: value}
    with pytest.raises(ValueError, match="finite"):
        DescriptionTemporalAnchorDoc(**fields, **bounds)
    with pytest.raises(ValueError, match="finite"):
        DescriptionTemporalAnchor(
            "c", TemporalFrame("f", "clock", provenance), provenance, **bounds
        )

    codec = DescriptionTemporalAnchorDoc.__charter__.document_codec()
    encoded = yaml.safe_load(codec.encode(DescriptionTemporalAnchorDoc(**fields)))
    encoded[bound] = value
    with pytest.raises(ValueError, match="finite"):
        codec.decode(
            yaml.safe_dump(encoded).encode(),
            DescriptionTemporalAnchorDoc,
            source="a.yaml",
        )

    repo = Repository.init(tmp_path)
    git = repo.require_git()
    head = git.branch_sha("master")
    with pytest.raises(ValueError, match="finite"):
        anchor_description_claim(repo, **fields, **bounds)
    result = CliRunner().invoke(
        cli,
        [
            "-C",
            str(tmp_path),
            "temporal",
            "anchor",
            "--anchor-id",
            "a",
            "--claim-id",
            "c",
            "--frame-id",
            "f",
            "--" + bound.replace("_", "-"),
            str(value),
        ],
    )
    assert result.exit_code != 0
    assert "finite" in result.output
    assert git.branch_sha("master") == head


@pytest.mark.parametrize(
    "bounds", [(None, None), (1.25, None), (None, -2.5), (-2.5, 1.25)]
)
def test_finite_bounds_round_trip_through_family_and_sidecar(tmp_path, bounds):
    repo = Repository.init(tmp_path / "knowledge")
    author_obs_claim(repo, "c", "An observation")
    declare_temporal_frame(repo, frame_id="f", description="clock")
    doc = DescriptionTemporalAnchorDoc(
        anchor_id="a",
        claim_id="c",
        frame_id="f",
        provenance=stated_provenance(),
        valid_from=bounds[0],
        valid_until=bounds[1],
    )
    family = repo.families.by_name("description_temporal_anchor")
    family.save("a", doc, message="anchor c")
    assert family.load("a") == doc
    sidecar = tmp_path / "anchors.sqlite"
    schema = TemporalRepository(backend=repo.require_git()).build_anchor_sidecar(
        sidecar
    )
    with readonly_session(sidecar, schema) as session:
        (row,) = select_description_temporal_anchors(session)
    assert (row.valid_from, row.valid_until) == bounds
