"""Checked quarantine survives projection and controls semantic world input."""

from pathlib import Path

import pytest

from propstore.compiler.workflows import build_repository
from propstore.families.claim_admission import ClaimAdmissionState
from propstore.families.claims import Claim, ClaimStatus, ClaimType
from propstore.families.concepts import Concept
from propstore.repository import Repository
from propstore.world import RenderPolicy, WorldQuery
from propstore.world.queries import QuarantinedClaimError


def test_blocked_observation_cannot_supply_a_world_value(tmp_path: Path) -> None:
    repo = Repository.init(tmp_path / "knowledge")
    repo.families.concept.save(
        "temperature", Concept(concept_id="temperature", canonical_name="temperature"),
        message="Add concept",
    )
    original = Claim(
        claim_id="bad", claim_type=ClaimType.OBSERVATION,
        output_concept="temperature", value=12,
    )
    repo.families.claim.save("bad", original, message="Add invalid observation")
    report = build_repository(repo)
    assert report.blocked_claim_count == 1
    with WorldQuery(repo) as world:
        assert world.claims_for(None) == []
        assert world.bind(policy=RenderPolicy()).active_claims() == []
        assert world.compiled_graph().claims == ()
        assert world.quarantined_claims(RenderPolicy()) == ()
        artifacts = world.quarantined_claims(RenderPolicy(show_quarantined=True))
        assert len(artifacts) == 1
        artifact = artifacts[0]
        assert artifact.claim.status is ClaimStatus.AUTHORED
        assert artifact.claim.value == 12
        assert artifact.admission.state is ClaimAdmissionState.QUARANTINED
        assert artifact.admission.content_digest
        assert artifact.admission.pass_identity == "claim.check:1"
        assert any(d.diagnostic_kind == "claim.contract" for d in artifact.diagnostics)
        with pytest.raises(QuarantinedClaimError) as error:
            world.get_claim("bad")
        assert error.value.artifact.claim == artifact.claim
        old_path = world.sidecar_path
    repo.families.claim.save(
        "bad", Claim(
            claim_id="bad", claim_type=ClaimType.OBSERVATION,
            statement="Measured temperature", output_concept="temperature", value=12,
        ), message="Repair observation",
    )
    repaired = build_repository(repo)
    assert repaired.blocked_claim_count == 0
    with WorldQuery(repo) as world:
        assert world.sidecar_path != old_path
        assert [claim.claim_id for claim in world.claims_for(None)] == ["bad"]
        assert world.quarantined_claims(RenderPolicy(show_quarantined=True)) == ()


def test_multiple_diagnostics_count_one_quarantined_artifact(tmp_path: Path) -> None:
    repo = Repository.init(tmp_path / "knowledge")
    repo.families.concept.save(
        "temperature", Concept(concept_id="temperature", canonical_name="temperature"),
        message="Add concept",
    )
    repo.families.claim.save(
        "bad", Claim(
            claim_id="bad", claim_type=ClaimType.PARAMETER,
            conditions=("missing_concept > 3",),
        ), message="Add invalid parameter",
    )
    report = build_repository(repo)
    assert report.claim_count == 1
    assert report.blocked_claim_count == 1
    with WorldQuery(repo) as world:
        artifact, = world.quarantined_claims(RenderPolicy(show_quarantined=True))
        assert {d.diagnostic_kind for d in artifact.diagnostics} >= {
            "claim.contract", "claim.condition",
        }
