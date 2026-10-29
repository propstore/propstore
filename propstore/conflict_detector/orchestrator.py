"""Compose detectors over canonical admitted claims and separate evidence."""

from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from typing import TYPE_CHECKING

from condition_ir import ConceptInfo, ConditionSolver

from propstore.core.graph_types import ParameterizationEdge
from propstore.families.claim_admission import ClaimAdmission, require_admitted_claims
from propstore.families.claim_provenance import ClaimProvenanceIndex
from propstore.families.claims import Claim
from propstore.families.concepts import Concept
from propstore.families.forms import FormDefinition

from .algorithms import detect_algorithm_conflicts
from .equations import detect_equation_conflicts
from .measurements import detect_measurement_conflicts
from .models import ConflictRecord
from .parameter_claims import detect_parameter_conflicts
from .parameterization_conflicts import detect_parameterization_conflicts

if TYPE_CHECKING:
    from propstore.context_lifting import LiftingSystem


def detect_conflicts(
    claims: Sequence[Claim],
    concepts: Mapping[str, Concept],
    cel_registry: Mapping[str, ConceptInfo],
    lifting_system: LiftingSystem | None = None,
    *,
    admissions: Collection[ClaimAdmission],
    provenance: ClaimProvenanceIndex,
    forms: Mapping[str, FormDefinition] | None = None,
    parameterizations: Mapping[str, Sequence[ParameterizationEdge]] | None = None,
) -> list[ConflictRecord]:
    require_admitted_claims(claims, admissions)
    solver = ConditionSolver(cel_registry)
    records, _groups = detect_parameter_conflicts(
        claims,
        cel_registry,
        admissions=admissions,
        provenance=provenance,
        lifting_system=lifting_system,
        solver=solver,
    )
    for detector in (
        detect_measurement_conflicts,
        detect_equation_conflicts,
        detect_algorithm_conflicts,
    ):
        records.extend(
            detector(
                claims,
                cel_registry,
                admissions=admissions,
                provenance=provenance,
                lifting_system=lifting_system,
                solver=solver,
            )
        )
    records.extend(
        detect_parameterization_conflicts(
            claims,
            concepts,
            parameterizations if parameterizations is not None else {},
            admissions=admissions,
            provenance=provenance,
            lifting_system=lifting_system,
            forms=forms,
        )
    )
    return records
