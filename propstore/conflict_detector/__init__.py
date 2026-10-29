"""Conflict detector package.

Classifies how same-concept claims relate (compatible, conflicting, φ-node,
overlap, parameter conflict, context φ-node) by composing the formal substrates
directly: condition-ir for Z3 condition reasoning, eq-equiv for equation
equivalence, ast-equiv for algorithm equivalence, and value_comparison/dimensions
for unit-aware value comparison. Every relationship is emitted as a
:class:`ConflictRecord` with provenance and never dropped.

Inputs are the canonical types: ``Concept`` charter documents keyed by concept
id, ``FormDefinition`` keyed by form name, and ``ParameterizationEdge`` keyed by
output concept. There is no registry-dict spelling.
"""

from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from typing import TYPE_CHECKING

from .models import ConflictClass, ConflictRecord

if TYPE_CHECKING:
    from condition_ir import ConceptInfo

    from propstore.context_lifting import LiftingSystem
    from propstore.core.graph_types import ParameterizationEdge
    from propstore.families.claim_admission import ClaimAdmission
    from propstore.families.claim_provenance import ClaimProvenanceIndex
    from propstore.families.claims import Claim
    from propstore.families.concepts import Concept
    from propstore.families.forms import FormDefinition


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
    from .orchestrator import detect_conflicts as _detect_conflicts

    return _detect_conflicts(
        claims,
        concepts,
        cel_registry,
        lifting_system=lifting_system,
        admissions=admissions,
        provenance=provenance,
        forms=forms,
        parameterizations=parameterizations,
    )


def detect_transitive_conflicts(
    claims: Sequence[Claim],
    concepts: Mapping[str, Concept],
    parameterizations: Mapping[str, Sequence[ParameterizationEdge]],
    *,
    admissions: Collection[ClaimAdmission],
    provenance: ClaimProvenanceIndex,
    lifting_system: LiftingSystem | None = None,
    forms: Mapping[str, FormDefinition] | None = None,
) -> list[ConflictRecord]:
    from .parameterization_conflicts import (
        detect_transitive_conflicts as _detect_transitive_conflicts,
    )

    return _detect_transitive_conflicts(
        claims,
        concepts,
        parameterizations,
        admissions=admissions,
        provenance=provenance,
        lifting_system=lifting_system,
        forms=forms,
    )


__all__ = [
    "ConflictClass",
    "ConflictRecord",
    "detect_conflicts",
    "detect_transitive_conflicts",
]
