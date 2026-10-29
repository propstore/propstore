"""Algorithm-claim conflict detection.

Whether two ALGORITHM claims implement the same computation is AST/algorithm
equivalence — owned by ``ast-equiv``. Equivalent bodies (canonical, SymPy, or
partial-eval tier) never conflict; a proven non-equivalence is condition-classified.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from ast_equiv import AlgorithmParseError
from ast_equiv import compare as ast_compare
from condition_ir import ConceptInfo, ConditionSolver

from propstore.algorithm_bindings import AlgorithmBindingError, algorithm_bindings

from .collectors import collect_algorithm_claims
from .condition_classifier import classify_conditions
from .context import append_context_classified_record, claim_context
from .models import ConflictClaim, ConflictRecord

if TYPE_CHECKING:
    from propstore.context_lifting import LiftingSystem

_LOGGER = logging.getLogger(__name__)


def detect_algorithm_conflicts(
    claims: Sequence[ConflictClaim],
    cel_registry: Mapping[str, ConceptInfo],
    *,
    lifting_system: LiftingSystem | None = None,
    solver: ConditionSolver | None = None,
) -> list[ConflictRecord]:
    records: list[ConflictRecord] = []
    by_concept = collect_algorithm_claims(claims)

    for concept_id, group in by_concept.items():
        if len(group) < 2:
            continue
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                claim_a = group[i]
                claim_b = group[j]
                body_a = claim_a.body or ""
                body_b = claim_b.body or ""
                if not body_a or not body_b:
                    continue

                try:
                    bindings_a = algorithm_bindings(claim_a.variables, body_a)
                    bindings_b = algorithm_bindings(claim_b.variables, body_b)
                    result = ast_compare(body_a, bindings_a, body_b, bindings_b)
                except AlgorithmBindingError:
                    raise
                except (
                    ValueError,
                    SyntaxError,
                    AlgorithmParseError,
                    RecursionError,
                ) as exc:
                    _LOGGER.warning(
                        "ast_compare failed for %s vs %s: %s",
                        claim_a.claim_id,
                        claim_b.claim_id,
                        exc,
                    )
                    continue
                if result.equivalent:
                    continue

                conditions_a = sorted(claim_a.conditions)
                conditions_b = sorted(claim_b.conditions)
                derivation_chain = (
                    f"similarity:{result.similarity:.3f} tier:{result.tier}"
                )
                value_a = f"algorithm:{claim_a.claim_id}"
                value_b = f"algorithm:{claim_b.claim_id}"
                if append_context_classified_record(
                    records,
                    concept_id=concept_id,
                    claim_a_id=claim_a.claim_id,
                    claim_b_id=claim_b.claim_id,
                    conditions_a=conditions_a,
                    conditions_b=conditions_b,
                    value_a=value_a,
                    value_b=value_b,
                    context_a=claim_context(claim_a),
                    context_b=claim_context(claim_b),
                    lifting_system=lifting_system,
                    derivation_chain=derivation_chain,
                ):
                    continue
                records.append(
                    ConflictRecord(
                        concept_id=concept_id,
                        claim_a_id=claim_a.claim_id,
                        claim_b_id=claim_b.claim_id,
                        warning_class=classify_conditions(
                            conditions_a,
                            conditions_b,
                            cel_registry,
                            solver=solver,
                        ),
                        conditions_a=conditions_a,
                        conditions_b=conditions_b,
                        value_a=value_a,
                        value_b=value_b,
                        derivation_chain=derivation_chain,
                    )
                )

    return records


