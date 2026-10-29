"""Snapshot-local checked admission, distinct from authored claim lifecycle."""

from __future__ import annotations

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
            raise ValueError(f"stale checked admission for claim {self.claim_id!r}")
