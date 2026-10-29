"""Typed source resolution over repository branches and canonical artifacts."""

from __future__ import annotations

from dataclasses import dataclass

from propstore.families.claims import Claim
from propstore.families.sources import SourceClaimDocument, SourceDocument, SourceRef
from propstore.repository import Repository
from propstore.source.common import source_branch_name
from propstore.storage.snapshot import BranchInfo


@dataclass(frozen=True)
class PromotedSourceClaim:
    source_claim: SourceClaimDocument
    claim: Claim


@dataclass(frozen=True)
class MissingPromotedClaim:
    source_claim: SourceClaimDocument
    artifact_id: str


@dataclass(frozen=True)
class UnidentifiedSourceClaim:
    source_claim: SourceClaimDocument


@dataclass(frozen=True)
class SourceIndexEntry:
    ref: SourceRef
    branch: BranchInfo
    document: SourceDocument | None
    claims: tuple[
        PromotedSourceClaim | MissingPromotedClaim | UnidentifiedSourceClaim, ...
    ]


@dataclass(frozen=True)
class UnknownSource:
    ref: SourceRef


@dataclass(frozen=True)
class MissingSourceManifest:
    entry: SourceIndexEntry


@dataclass(frozen=True)
class ResolvedSource:
    entry: SourceIndexEntry
    document: SourceDocument


@dataclass(frozen=True)
class SourceIndex:
    """Source-owned classification; generic branch enumeration stays in snapshot.

    A branch stem is a usable placement ref, not a bibliographic identity. The
    latter is read from the manifest, including for names whose placement codec
    is irreversible. Every claim result retains the original source document.
    """

    entries: tuple[SourceIndexEntry, ...]

    @classmethod
    def from_repository(
        cls, repo: Repository, *, commit: str | None = None
    ) -> SourceIndex:
        if repo.git is None:
            return cls(())
        entries: list[SourceIndexEntry] = []
        for branch in repo.snapshot.iter_branches():
            if branch.kind != "source":
                continue
            ref = SourceRef(branch.name.removeprefix("source/"))
            document = repo.families.source_documents.load(ref, commit=branch.tip_sha)
            source_claims = repo.families.source_claims.load(ref, commit=branch.tip_sha)
            claims: list[
                PromotedSourceClaim | MissingPromotedClaim | UnidentifiedSourceClaim
            ] = []
            for source_claim in () if source_claims is None else source_claims.claims:
                artifact_id = source_claim.artifact_id
                if not artifact_id:
                    claims.append(UnidentifiedSourceClaim(source_claim))
                    continue
                claim = repo.families.claim.load(artifact_id, commit=commit)
                if claim is None:
                    claims.append(MissingPromotedClaim(source_claim, artifact_id))
                else:
                    claims.append(PromotedSourceClaim(source_claim, claim))
            entries.append(SourceIndexEntry(ref, branch, document, tuple(claims)))
        return cls(tuple(sorted(entries, key=lambda entry: entry.branch.name)))

    @property
    def refs(self) -> tuple[SourceRef, ...]:
        return tuple(entry.ref for entry in self.entries)

    def resolve(
        self, ref: SourceRef
    ) -> ResolvedSource | MissingSourceManifest | UnknownSource:
        branch = source_branch_name(ref.name)
        for entry in self.entries:
            if entry.branch.name == branch:
                if entry.document is None:
                    return MissingSourceManifest(entry)
                return ResolvedSource(entry, entry.document)
        return UnknownSource(ref)
