"""Source enumeration/resolution and lossless canonical bundle membership."""

from pathlib import Path

from propstore.core.source_types import SourceKind, SourceOriginType
from propstore.families.claim_provenance import (
    BundledClaim,
    ClaimProvenanceIndex,
    UnbundledClaim,
)
from propstore.families.claims import Claim
from propstore.families.micropublications import Micropublication
from propstore.families.sources import (
    SourceClaimDocument,
    SourceClaimsDocument,
    SourceRef,
)
from propstore.provenance import Provenance, ProvenanceStatus
from propstore.repository import Repository
from propstore.source.common import init_source_branch, load_source_document
from propstore.source.indexes import (
    MissingPromotedClaim,
    MissingSourceManifest,
    PromotedSourceClaim,
    ResolvedSource,
    SourceIndex,
    UnidentifiedSourceClaim,
    UnknownSource,
)


def test_membership_retains_all_sources_and_bundles() -> None:
    first = Micropublication(
        artifact_id="mp:a", context_id="ctx", claims=("claim",), source="paperA"
    )
    second = Micropublication(
        artifact_id="mp:b", context_id="ctx", claims=("claim",), source="paperB"
    )
    same_source = Micropublication(
        artifact_id="mp:c", context_id="ctx", claims=("claim",), source="paperA"
    )
    index = ClaimProvenanceIndex.from_micropublications((second, same_source, first))
    membership = index.for_claim("claim")
    assert isinstance(membership, BundledClaim)
    assert membership.micropublications == (first, second, same_source)
    assert membership.micropublications[0] is first
    assert isinstance(index.for_claim("absent"), UnbundledClaim)


def test_source_less_bundle_is_distinct_from_unbundled_claim() -> None:
    bundle = Micropublication(
        artifact_id="mp",
        context_id="ctx",
        claims=("claim",),
        provenance=Provenance(status=ProvenanceStatus.STATED),
    )
    index = ClaimProvenanceIndex.from_micropublications((bundle,))
    membership = index.for_claim("claim")
    assert isinstance(membership, BundledClaim)
    assert membership.micropublications == (bundle,)
    assert membership.micropublications[0].source is None
    assert isinstance(index.for_claim("other"), UnbundledClaim)


def test_source_index_resolves_real_identity_and_reports_claim_states(
    tmp_path: Path,
) -> None:
    repo = Repository.init(tmp_path)
    name = "O'Reilly 2026 / Ü"
    branch = init_source_branch(
        repo,
        name,
        kind=SourceKind.ACADEMIC_PAPER,
        origin_type=SourceOriginType.MANUAL,
        origin_value="manual",
    )
    manifest = load_source_document(repo, name)
    repo.families.claim.save(
        "promoted", Claim(claim_id="promoted"), message="Author canonical claim"
    )
    repo.families.source_claims.save(
        SourceRef(name),
        SourceClaimsDocument(
            claims=(
                SourceClaimDocument(artifact_id="promoted"),
                SourceClaimDocument(artifact_id="missing"),
                SourceClaimDocument(id="not-yet-identified"),
            )
        ),
        message="Author source claims",
    )
    repo.require_git().create_branch("agent/not-a-source")
    index = SourceIndex.from_repository(repo)
    assert len(index.refs) == 1
    resolved = index.resolve(SourceRef(name))
    assert isinstance(resolved, ResolvedSource)
    assert resolved.document.id == manifest.id
    assert resolved.entry.branch.name == branch
    assert isinstance(index.resolve(index.refs[0]), ResolvedSource)
    promoted, missing, unidentified = resolved.entry.claims
    assert isinstance(promoted, PromotedSourceClaim)
    assert promoted.claim.claim_id == "promoted"
    assert isinstance(missing, MissingPromotedClaim)
    assert missing.artifact_id == "missing"
    assert isinstance(unidentified, UnidentifiedSourceClaim)
    assert isinstance(index.resolve(SourceRef("unknown")), UnknownSource)


def test_missing_source_manifest_is_not_unknown_source(tmp_path: Path) -> None:
    repo = Repository.init(tmp_path)
    repo.require_git().create_branch("source/missing-manifest")
    index = SourceIndex.from_repository(repo)
    assert isinstance(
        index.resolve(SourceRef("missing-manifest")), MissingSourceManifest
    )
    assert isinstance(index.resolve(SourceRef("unknown")), UnknownSource)
