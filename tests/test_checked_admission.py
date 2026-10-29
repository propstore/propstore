"""Checked quarantine survives projection and controls semantic world input."""

from pathlib import Path

import msgspec
import pytest

from propstore.aspic_bridge import build_aspic_projection
from propstore.compiler.workflows import build_repository
from propstore.families.claim_admission import ClaimAdmissionState
from propstore.families.claims import Claim, ClaimStatus, ClaimType
from propstore.families.concepts import Concept
from propstore.families.justifications import Justification
from propstore.families.predicates import Predicate
from propstore.families.relations import Stance
from propstore.repository import Repository
from propstore.stances import StanceType
from propstore.world import RenderPolicy, WorldQuery
from propstore.world.queries import QuarantinedClaimError
from propstore.world.types import ValueStatus


def test_blocked_observation_cannot_supply_a_world_value(tmp_path: Path) -> None:
    repo = Repository.init(tmp_path / "knowledge")
    repo.families.concept.save(
        "temperature",
        Concept(concept_id="temperature", canonical_name="temperature"),
        message="Add concept",
    )
    original = Claim(
        claim_id="bad",
        claim_type=ClaimType.OBSERVATION,
        output_concept="temperature",
        value=12,
    )
    repo.families.claim.save("bad", original, message="Add invalid observation")
    report = build_repository(repo)
    assert report.blocked_claim_count == 1
    with WorldQuery(repo) as world:
        assert world.claims_for(None) == []
        assert world.bind(policy=RenderPolicy()).active_claims() == []
        assert (
            world.bind(policy=RenderPolicy()).value_of("temperature").status
            is ValueStatus.NO_CLAIMS
        )
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
        with pytest.raises(ValueError, match="stale checked admission"):
            artifact.admission.verify(msgspec.structs.replace(artifact.claim, value=99))
        with pytest.raises(ValueError, match="stale checked admission"):
            msgspec.structs.replace(
                artifact.admission, pass_identity="claim.check:obsolete"
            ).verify(artifact.claim)
        assert any(d.diagnostic_kind == "claim.contract" for d in artifact.diagnostics)
        with pytest.raises(QuarantinedClaimError) as error:
            world.get_claim("bad")
        assert error.value.artifact.claim == artifact.claim
        old_path = world.sidecar_path
    repo.families.claim.save(
        "bad",
        Claim(
            claim_id="bad",
            claim_type=ClaimType.OBSERVATION,
            statement="Measured temperature",
            output_concept="temperature",
            value=12,
        ),
        message="Repair observation",
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
        "temperature",
        Concept(concept_id="temperature", canonical_name="temperature"),
        message="Add concept",
    )
    repo.families.claim.save(
        "bad",
        Claim(
            claim_id="bad",
            claim_type=ClaimType.PARAMETER,
            conditions=("missing_concept > 3",),
        ),
        message="Add invalid parameter",
    )
    report = build_repository(repo)
    assert report.claim_count == 1
    assert report.blocked_claim_count == 1
    with WorldQuery(repo) as world:
        (artifact,) = world.quarantined_claims(RenderPolicy(show_quarantined=True))
        assert {d.diagnostic_kind for d in artifact.diagnostics} >= {
            "claim.contract",
            "claim.condition",
        }


def test_quarantine_removes_equations_conflicts_grounding_and_stance_nodes(
    tmp_path: Path,
) -> None:
    repo = Repository.init(tmp_path / "knowledge")
    repo.families.concept.save(
        "temperature",
        Concept(concept_id="temperature", canonical_name="temperature"),
        message="Add concept",
    )
    for claim in (
        Claim(
            claim_id="parameter_a",
            claim_type=ClaimType.PARAMETER,
            output_concept="temperature",
            value=1,
            conditions=("unknown > 0",),
        ),
        Claim(
            claim_id="parameter_b",
            claim_type=ClaimType.PARAMETER,
            output_concept="temperature",
            value=2,
            conditions=("unknown > 0",),
        ),
        Claim(
            claim_id="equation",
            claim_type=ClaimType.EQUATION,
            output_concept="temperature",
            expression="x + 1",
            concepts=("temperature",),
            conditions=("unknown > 0",),
        ),
        Claim(
            claim_id="conclusion",
            claim_type=ClaimType.OBSERVATION,
            statement="An inferred conclusion",
            output_concept="temperature",
        ),
    ):
        repo.families.claim.save(claim.claim_id, claim, message="Add claim")
    repo.families.stance.save(
        "stance",
        Stance(
            stance_id="stance",
            source_claim_id="parameter_a",
            target_claim_id="conclusion",
            stance_type=StanceType.SUPPORTS,
        ),
        message="Add dependent stance",
    )
    repo.families.justification.save(
        "license",
        Justification(
            justification_id="license",
            conclusion="conclusion",
            premises=("parameter_a",),
            rule_kind="strict",
        ),
        message="Add inference license",
    )
    repo.families.predicate.save(
        "has_value",
        Predicate(
            predicate_id="has_value",
            arity=1,
            arg_types=("Claim",),
            derived_from="claim.attribute:value",
        ),
        message="Add grounding predicate",
    )
    report = build_repository(repo)
    assert report.blocked_claim_count == 3
    assert report.conflict_count == 0
    assert report.grounding_bundle is not None
    assert report.grounding_bundle.source_facts == ()
    with WorldQuery(repo) as world:
        assert world.all_parameterizations() == ()
        assert world.all_claim_stances() == []
        assert world.stances_between({"parameter_a", "conclusion"}) == []
        graph = world.compiled_graph()
        assert {claim.claim_id for claim in graph.claims} == {"conclusion"}
        # An unusable license still declares that the conclusion is inferred;
        # removing it would fabricate an independent reported premise.
        assert len(graph.justifications) == 1
        assert graph.justifications[0].premises == ("parameter_a",)
        assert any(
            diagnostic.diagnostic_kind == "claim.quarantined_subject"
            and "quarantined" in diagnostic.message
            for diagnostic in world.build_diagnostics(
                RenderPolicy(show_quarantined=True)
            )
        )
        engine = world.bind(policy=RenderPolicy()).atms_engine()
        assert engine.claim_label("parameter_a") is None
        assert engine.claim_label("parameter_b") is None
        assert engine.claim_label("equation") is None
        bound = world.bind(policy=RenderPolicy())
        projection = build_aspic_projection(
            world,
            bound.active_claims(),
            bundle=world.grounding_bundle(),
            active_graph=bound.active_graph,
        )
        assert projection.arguments == ()
