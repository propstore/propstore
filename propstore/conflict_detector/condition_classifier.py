"""Classify applicability through the checked condition owner and solver."""

from condition_ir import (
    CheckedConditionSet,
    ConditionSolver,
    SolverUnknown,
    SolverUnsat,
)

from .models import ConflictClass


def classify_conditions(
    conditions_a: CheckedConditionSet,
    conditions_b: CheckedConditionSet,
    *,
    solver: ConditionSolver,
) -> ConflictClass:
    if conditions_a == conditions_b:
        return ConflictClass.CONFLICT
    equivalence = solver.are_equivalent_result(conditions_a, conditions_b)
    if isinstance(equivalence, SolverUnknown):
        return ConflictClass.UNKNOWN
    if isinstance(equivalence, SolverUnsat):
        return ConflictClass.CONFLICT
    disjointness = solver.are_disjoint_result(conditions_a, conditions_b)
    if isinstance(disjointness, SolverUnknown):
        return ConflictClass.UNKNOWN
    if isinstance(disjointness, SolverUnsat):
        return ConflictClass.PHI_NODE
    return ConflictClass.OVERLAP
