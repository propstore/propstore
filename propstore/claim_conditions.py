"""Claim/condition integration — composing ``condition-ir`` directly.

This is the propstore-owned wiring that connects a :class:`~propstore.families.claims.Claim`
to the condition-ir package. It owns NO condition machinery: CEL type-checking,
IR lowering, the checked carriers, the Z3 solver, the json codec, and the
sql/python/estree backends ALL live in condition-ir and are called directly here.
There is no propstore condition type, no ``to_X``/``from_X`` round-trip pair, and
no wrapper that merely re-exports a package function.

What propstore contributes (CLAUDE.md substrate boundary, generic-package rule):

* It orchestrates claim-level operations: checking a claim's authored CEL
  conditions into condition-ir's ``CheckedConditionSet`` (with non-committal
  diagnostics for invalid conditions — never an abort or a drop), serializing
  that set with the package's json codec into the claim's ``conditions_ir``, and
  reconstructing the stored checked set without reparsing authored CEL.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass

import msgspec
from condition_ir import (
    CheckedCondition,
    CheckedConditionSet,
    ConceptInfo,
    check_cel_expression,
    check_condition_ir,
    checked_condition_set,
    checked_condition_set_from_json,
    checked_condition_set_to_json,
)

from propstore.families.claims import Claim


@dataclass(frozen=True)
class ClaimConditionDiagnostic:
    """A non-committal record of a problem in one authored CEL condition.

    Diagnostics are accumulated, never raised: an invalid condition is reported
    here and excluded from the checked set, but the claim still processes (the
    quarantine-with-provenance discipline, not an abort).
    """

    condition: str
    message: str


@dataclass(frozen=True)
class ClaimConditionReport:
    """The checked outcome of a claim's authored conditions.

    ``checked`` is condition-ir's own ``CheckedConditionSet`` (used directly, not
    a propstore spelling); ``diagnostics`` carries any CEL type errors.
    """

    checked: CheckedConditionSet
    diagnostics: tuple[ClaimConditionDiagnostic, ...]


def check_claim_conditions(
    claim: Claim, registry: Mapping[str, ConceptInfo]
) -> ClaimConditionReport:
    """Type-check a claim's authored CEL conditions into a ``CheckedConditionSet``.

    Each clean condition is lowered with condition-ir's ``check_condition_ir``;
    a condition with CEL type errors is recorded as a diagnostic and omitted from
    the checked set. Nothing is dropped silently and nothing aborts.
    """

    checked: list[CheckedCondition] = []
    diagnostics: list[ClaimConditionDiagnostic] = []
    for source in claim.conditions:
        errors = check_cel_expression(source, registry)
        if errors:
            diagnostics.extend(
                ClaimConditionDiagnostic(condition=source, message=str(error))
                for error in errors
            )
            continue
        checked.append(check_condition_ir(source, registry))
    return ClaimConditionReport(
        checked=checked_condition_set(checked), diagnostics=tuple(diagnostics)
    )


def serialize_checked_conditions(condition_set: CheckedConditionSet) -> str:
    """Serialize a ``CheckedConditionSet`` with condition-ir's own json codec."""

    return json.dumps(checked_condition_set_to_json(condition_set), sort_keys=True)


def compile_checked_conditions(conditions_ir: str) -> CheckedConditionSet:
    """Rebuild a ``CheckedConditionSet`` from a serialized ``conditions_ir`` string.

    This is the no-reparse path: runtime reconstructs condition-ir's checked type
    from the stored json via the package codec, never by re-running the CEL
    front-end.
    """

    return checked_condition_set_from_json(json.loads(conditions_ir))


def check_claim(claim: Claim, registry: Mapping[str, ConceptInfo]) -> Claim:
    """Return the claim with ``conditions_ir`` filled from its checked conditions.

    The deterministic AUTHORED -> CHECKED projection: it compiles the authored
    CEL into condition-ir's checked set and stores the package-codec json on the
    claim. It never gates — an empty/partial checked set still yields a claim.
    """

    report = check_claim_conditions(claim, registry)
    return msgspec.structs.replace(
        claim, conditions_ir=serialize_checked_conditions(report.checked)
    )
