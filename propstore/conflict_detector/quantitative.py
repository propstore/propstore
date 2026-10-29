"""Shared quantitative disagreement over canonical checked claim groups."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from itertools import combinations
from typing import TYPE_CHECKING

from condition_ir import ConditionSolver

from propstore.families.claim_provenance import ClaimProvenanceIndex
from propstore.families.claim_quantitative import AbsentValue
from propstore.families.claims import Claim
from propstore.value_comparison import value_str, values_compatible

from .condition_classifier import classify_conditions
from .context import append_context_classified_record
from .models import ConflictRecord

if TYPE_CHECKING:
    from propstore.context_lifting import LiftingSystem


def _compare_quantitative_groups(
    groups: Iterable[tuple[str, Sequence[Claim]]],
    *,
    solver: ConditionSolver,
    provenance: ClaimProvenanceIndex,
    lifting_system: LiftingSystem | None,
) -> list[ConflictRecord]:
    records: list[ConflictRecord] = []
    for concept_id, group in groups:
        for claim_a, claim_b in combinations(group, 2):
            evidence_a, evidence_b = claim_a.quantitative, claim_b.quantitative
            if isinstance(evidence_a.value, AbsentValue) or isinstance(
                evidence_b.value, AbsentValue
            ):
                continue
            if values_compatible(
                evidence_a.point,
                evidence_b.point,
                claim_a=evidence_a,
                claim_b=evidence_b,
            ):
                continue
            checked_a, checked_b = (
                claim_a.checked_conditions,
                claim_b.checked_conditions,
            )
            conditions_a, conditions_b = (
                list(checked_a.sources),
                list(checked_b.sources),
            )
            value_a, value_b = (
                value_str(evidence_a.point, evidence_a),
                value_str(evidence_b.point, evidence_b),
            )
            if append_context_classified_record(
                records,
                concept_id=concept_id,
                claim_a_id=claim_a.claim_id,
                claim_b_id=claim_b.claim_id,
                conditions_a=conditions_a,
                conditions_b=conditions_b,
                value_a=value_a,
                value_b=value_b,
                context_a=claim_a.context_id,
                context_b=claim_b.context_id,
                lifting_system=lifting_system,
            ):
                continue
            records.append(
                ConflictRecord(
                    concept_id=concept_id,
                    claim_a_id=claim_a.claim_id,
                    claim_b_id=claim_b.claim_id,
                    warning_class=classify_conditions(
                        checked_a, checked_b, solver=solver
                    ),
                    conditions_a=conditions_a,
                    conditions_b=conditions_b,
                    value_a=value_a,
                    value_b=value_b,
                )
            )
    return [record.with_provenance(provenance) for record in records]
