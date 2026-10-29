"""Source attribution remains evidence through detector/build/world/merge paths."""

from pathlib import Path

import pytest
from condition_ir import ConceptInfo, KindType

from propstore.compiler.context import CompilationContext
from propstore.compiler.ir import ClaimCheckedBundle
from propstore.conflict_detector import ConflictClass, detect_conflicts
from propstore.families.claim_provenance import (
    BundledClaim,
    ClaimProvenanceIndex,
    UnbundledClaim,
)
from propstore.families.claims import Claim, ClaimStatus, ClaimType
from propstore.families.contexts import Context
from propstore.families.forms import FormDefinition
from propstore.families.micropublications import Micropublication
from propstore.merge.merge_commit import (
    QuarantinedMergeClaimsError,
    _read_branch_merge_claims,
)
from propstore.provenance import Provenance, ProvenanceStatus
from propstore.repository import Repository
from propstore.world import RenderPolicy, WorldQuery
from propstore.world.bound import recomputed_conflicts
from tests.canonical_claim_fixtures import concept_with_form
from tests.checked_claim_helpers import check_claims
from tests.merge_commit_helpers import author_param_claim


def _claims(
    conditions_a: tuple[str, ...] = (),
    conditions_b: tuple[str, ...] = (),
) -> tuple[ClaimCheckedBundle, CompilationContext]:
    return check_claims(
        tuple(
            Claim(
                claim_id=claim_id,
                claim_type=ClaimType.PARAMETER,
                output_concept="temperature",
                value=value,
                unit="1",
                conditions=conditions,
            )
            for claim_id, value, conditions in (
                ("a", 200.0, conditions_a),
                ("b", 300.0, conditions_b),
            )
        ),
        (concept_with_form("temperature", "temperature", "quantity"),),
        condition_registry={"x": ConceptInfo("x", "x", KindType.QUANTITY)},
    )


def _bundle(artifact_id: str, claim_id: str, source: str) -> Micropublication:
    return Micropublication(
        artifact_id=artifact_id, context_id="ctx", claims=(claim_id,), source=source
    )


@pytest.mark.parametrize(
    "source",
    [
        "paperA",
        "paperB",
        "O'Reilly 2026",
        'a "quoted" source',
        "x' || true || '",
        "来源 – Ü",
        "  source with whitespace  ",
        "https://example.org/a?q=1&x=2#fragment",
        "line one\nline two",
    ],
)
def test_source_identity_cannot_change_applicability(source: str) -> None:
    first = _bundle("mp:a", "a", "paperA")
    second = _bundle("mp:b", "b", source)
    bundle, context = _claims()
    assert not bundle.blocked_claims, bundle.diagnostics
    records = detect_conflicts(
        [entry.claim for entry in bundle.claims],
        dict(context.concepts_by_id),
        context.condition_registry,
        admissions=tuple(entry.admission for entry in bundle.claims),
        provenance=ClaimProvenanceIndex.from_micropublications((first, second)),
    )
    assert len(records) == 1
    record = records[0]
    assert record.warning_class is ConflictClass.CONFLICT
    assert record.conditions_a == record.conditions_b == []
    assert isinstance(record.provenance_a, BundledClaim)
    assert isinstance(record.provenance_b, BundledClaim)
    assert record.provenance_a.micropublications[0] is first
    assert record.provenance_b.micropublications[0] is second


def test_all_memberships_survive_and_source_less_is_not_unbundled() -> None:
    first = _bundle("mp:a", "a", "paperA")
    second = _bundle("mp:b", "a", "paperB")
    source_less = Micropublication(
        artifact_id="mp:c",
        context_id="ctx",
        claims=("a",),
        provenance=Provenance(status=ProvenanceStatus.STATED),
    )
    for bundles in ((first, second, source_less), (source_less, second, first)):
        bundle, context = _claims()
        assert not bundle.blocked_claims, bundle.diagnostics
        record = detect_conflicts(
            [entry.claim for entry in bundle.claims],
            dict(context.concepts_by_id),
            context.condition_registry,
            admissions=tuple(entry.admission for entry in bundle.claims),
            provenance=ClaimProvenanceIndex.from_micropublications(bundles),
        )[0]
        assert record.warning_class is ConflictClass.CONFLICT
        assert isinstance(record.provenance_a, BundledClaim)
        assert record.provenance_a.micropublications == (first, second, source_less)
        assert record.provenance_a.micropublications[2] is source_less
        assert record.provenance_b == UnbundledClaim("b")


def test_only_authored_conditions_establish_disjoint_applicability() -> None:
    bundle, context = _claims(("x > 10",), ("x < 5",))
    assert not bundle.blocked_claims, bundle.diagnostics
    record = detect_conflicts(
        [entry.claim for entry in bundle.claims],
        dict(context.concepts_by_id),
        context.condition_registry,
        admissions=tuple(entry.admission for entry in bundle.claims),
        provenance=ClaimProvenanceIndex.from_micropublications(
            (_bundle("mp:a", "a", "same"), _bundle("mp:b", "b", "same"))
        ),
    )[0]
    assert record.warning_class is ConflictClass.PHI_NODE
    assert [str(condition) for condition in record.conditions_a] == ["x > 10"]
    assert [str(condition) for condition in record.conditions_b] == ["x < 5"]


def test_build_world_and_merge_read_actual_raw_membership(tmp_path: Path) -> None:
    repo = Repository.init(tmp_path / "knowledge")
    repo.families.form.save(
        "temperature",
        FormDefinition(
            name="temperature",
            kind=KindType.QUANTITY,
            unit_symbol="K",
            allowed_units=("K",),
            dimensions={"Theta": 1},
        ),
        message="temperature form",
    )
    repo.families.concept.save(
        "temperature",
        concept_with_form("temperature", "temperature", "temperature"),
        message="temperature concept",
    )
    repo.families.context.save(
        "ctx", Context(context_id="ctx", name="ctx"), message="context"
    )
    author_param_claim(repo, "a", "temperature", 200.0)
    author_param_claim(repo, "b", "temperature", 300.0)
    repo.families.claim.save(
        "blocked",
        Claim(
            claim_id="blocked",
            claim_type=ClaimType.OBSERVATION,
            statement="",
            status=ClaimStatus.BLOCKED,
        ),
        message="blocked peer",
    )
    # The peer is not admitted into semantic compute; raw membership must still
    # provide the actual bundle evidence for its valid member.
    bundle = Micropublication(
        artifact_id="mp:a",
        context_id="ctx",
        claims=("a", "blocked"),
        principal_claim="a",
        source="O'Reilly 2026 / 来源\n' || true || '",
    )
    repo.families.micropublication.save("mp:a", bundle, message="raw membership")
    second = _bundle("mp:b", "a", "second source")
    repo.families.micropublication.save("mp:b", second, message="second membership")
    commit = str(repo.require_git().head_sha())
    with pytest.raises(QuarantinedMergeClaimsError) as rejected:
        _read_branch_merge_claims(repo, "master", commit)
    assert [entry.claim.claim_id for entry in rejected.value.artifacts] == ["blocked"]
    with WorldQuery(repo) as world:
        membership = world.claim_provenance().for_claim("a")
        assert isinstance(membership, BundledClaim)
        assert {item.artifact_id for item in membership.micropublications} == {
            "mp:a",
            "mp:b",
        }
        assert any(
            item.claims == ("a", "blocked") for item in membership.micropublications
        )
        stored = world.conflicts()
        assert len(stored) == 1, world.build_diagnostics(
            RenderPolicy(show_quarantined=True)
        )
        assert stored[0].warning_class is ConflictClass.CONFLICT
        assert stored[0].provenance_a == membership
        assert stored[0].provenance_b == UnbundledClaim("b")
        recomputed = recomputed_conflicts(world, world.claims_for(None))
        assert len(recomputed) == 1
        assert recomputed[0].warning_class is ConflictClass.CONFLICT
        assert recomputed[0].provenance_a == membership
        assert recomputed[0].provenance_b == UnbundledClaim("b")
    repo.families.claim.save(
        "blocked",
        Claim(
            claim_id="blocked",
            claim_type=ClaimType.OBSERVATION,
            statement="Retained peer observation",
            status=ClaimStatus.BLOCKED,
        ),
        message="Repair peer observation for checked merge admission",
    )
    merge_claims = _read_branch_merge_claims(
        repo, "master", str(repo.require_git().head_sha())
    )
    assert next(
        claim.provenance for claim in merge_claims if claim.claim_id == "a"
    ) == membership
