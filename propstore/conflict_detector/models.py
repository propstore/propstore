"""Conflict comparison results; input claims remain canonical charter objects."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from condition_ir import CelExpr

from propstore.families.claim_provenance import (
    BundledClaim,
    ClaimProvenanceIndex,
    UnbundledClaim,
)


class ConflictClass(Enum):
    COMPATIBLE = "COMPATIBLE"
    UNKNOWN = "UNKNOWN"
    PHI_NODE = "PHI_NODE"
    CONFLICT = "CONFLICT"
    OVERLAP = "OVERLAP"
    PARAM_CONFLICT = "PARAM_CONFLICT"
    CONTEXT_PHI_NODE = "CONTEXT_PHI_NODE"


def coerce_conflict_class(value: object | None) -> ConflictClass | None:
    if value is None:
        return None
    if isinstance(value, ConflictClass):
        return value
    raw_value = str(value)
    try:
        return ConflictClass(raw_value)
    except ValueError:
        return ConflictClass(raw_value.upper())


@dataclass
class ConflictRecord:
    concept_id: str
    claim_a_id: str
    claim_b_id: str
    warning_class: ConflictClass
    conditions_a: list[CelExpr]
    conditions_b: list[CelExpr]
    value_a: str
    value_b: str
    derivation_chain: str | None = None
    provenance_a: BundledClaim | UnbundledClaim | None = None
    provenance_b: BundledClaim | UnbundledClaim | None = None

    def with_provenance(self, provenance: ClaimProvenanceIndex) -> ConflictRecord:
        return replace(
            self,
            provenance_a=provenance.for_claim(self.claim_a_id),
            provenance_b=provenance.for_claim(self.claim_b_id),
        )
