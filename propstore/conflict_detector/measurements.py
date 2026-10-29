"""Measurement disagreement uses the shared checked quantitative comparison."""

from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from typing import TYPE_CHECKING

from condition_ir import ConceptInfo, ConditionSolver

from propstore.families.claim_admission import ClaimAdmission, require_admitted_claims
from propstore.families.claim_provenance import ClaimProvenanceIndex
from propstore.families.claims import Claim

from .collectors import collect_measurement_claims
from .models import ConflictRecord
from .quantitative import _compare_quantitative_groups

if TYPE_CHECKING:
    from propstore.context_lifting import LiftingSystem


def detect_measurement_conflicts(
    claims: Sequence[Claim],
    cel_registry: Mapping[str, ConceptInfo],
    *,
    admissions: Collection[ClaimAdmission],
    provenance: ClaimProvenanceIndex,
    lifting_system: LiftingSystem | None = None,
    solver: ConditionSolver | None = None,
) -> list[ConflictRecord]:
    require_admitted_claims(claims, admissions)
    return _compare_quantitative_groups(
        (
            (concept_id, group)
            for (concept_id, _measure), group in collect_measurement_claims(
                claims
            ).items()
        ),
        solver=solver if solver is not None else ConditionSolver(cel_registry),
        provenance=provenance,
        lifting_system=lifting_system,
    )
