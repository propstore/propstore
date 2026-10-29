"""Snapshot-local checked admission, distinct from authored claim lifecycle."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from enum import StrEnum
from hashlib import sha256
from typing import Annotated

import msgspec
from quire.charter_class import CharterDoc, charter, charter_field

from propstore.families.claims import Claim

CLAIM_CHECK_VERSION = "2"


class ClaimAdmissionState(StrEnum):
    ADMITTED = "admitted"
    QUARANTINED = "quarantined"


class ClaimAdmissionFailure(StrEnum):
    MISSING = "missing"
    QUARANTINED = "quarantined"
    STALE = "stale"
    UNCHECKED = "unchecked"


class ClaimAdmissionError(ValueError):
    def __init__(self, claim_id: str, reason: ClaimAdmissionFailure) -> None:
        super().__init__(f"{reason.value} checked admission for claim {claim_id!r}")
        self.claim_id = claim_id
        self.reason = reason


def claim_content_digest(claim: Claim) -> str:
    """Bind admission to the complete canonical checked document."""

    return sha256(msgspec.json.encode(claim)).hexdigest()


@charter(
    key="claim_admission",
    name="claim_admission",
    contract_version="2026.10.28",
    placement="claim_admission",
    identity_field="claim_id",
)
class ClaimAdmission(CharterDoc):
    """One compiler decision in the same derived snapshot as its claim."""

    claim_id: Annotated[str, charter_field(primary_key=True)]
    state: ClaimAdmissionState
    content_digest: str
    pass_identity: str

    def verify(self, claim: Claim) -> None:
        if (
            claim.claim_id != self.claim_id
            or claim_content_digest(claim) != self.content_digest
            or self.pass_identity != f"claim.check:{CLAIM_CHECK_VERSION}"
        ):
            raise ClaimAdmissionError(self.claim_id, ClaimAdmissionFailure.STALE)

    def require_admitted(self, claim: Claim) -> None:
        self.verify(claim)
        if self.state is ClaimAdmissionState.QUARANTINED:
            raise ClaimAdmissionError(claim.claim_id, ClaimAdmissionFailure.QUARANTINED)
        if claim.conditions_ir is None or claim.quantitative_ir is None:
            raise ClaimAdmissionError(claim.claim_id, ClaimAdmissionFailure.UNCHECKED)


def require_admitted_claims(
    claims: Sequence[Claim], admissions: Iterable[ClaimAdmission]
) -> None:
    """Require exact checked decisions, including rival versions of one claim id."""

    outcomes = tuple(admissions)
    by_content = {(entry.claim_id, entry.content_digest): entry for entry in outcomes}
    for claim in claims:
        entry = by_content.get((claim.claim_id, claim_content_digest(claim)))
        if entry is None:
            reason = (
                ClaimAdmissionFailure.STALE
                if any(outcome.claim_id == claim.claim_id for outcome in outcomes)
                else ClaimAdmissionFailure.MISSING
            )
            raise ClaimAdmissionError(claim.claim_id, reason)
        entry.require_admitted(claim)
