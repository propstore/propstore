"""Lossless claim attribution projected from canonical micropublication membership."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from propstore.families.micropublications import Micropublication


@dataclass(frozen=True)
class UnbundledClaim:
    claim_id: str


@dataclass(frozen=True)
class BundledClaim:
    claim_id: str
    micropublications: tuple[Micropublication, ...]


@dataclass(frozen=True)
class ClaimProvenanceIndex:
    """Keep each bundle, including source-less attribution, without source collapse.

    Bundle fields are never copied: source, evidence and provenance remain owned
    by the actual canonical Micropublication documents.
    """

    memberships: tuple[BundledClaim, ...]

    @classmethod
    def from_micropublications(
        cls, micropublications: Iterable[Micropublication]
    ) -> ClaimProvenanceIndex:
        memberships: dict[str, list[Micropublication]] = {}
        for bundle in micropublications:
            for claim_id in dict.fromkeys(bundle.claims):
                memberships.setdefault(claim_id, []).append(bundle)
        return cls(
            tuple(
                BundledClaim(
                    claim_id, tuple(sorted(bundles, key=lambda b: b.artifact_id))
                )
                for claim_id, bundles in sorted(memberships.items())
            )
        )

    def for_claim(self, claim_id: str) -> BundledClaim | UnbundledClaim:
        for membership in self.memberships:
            if membership.claim_id == claim_id:
                return membership
        return UnbundledClaim(claim_id)
