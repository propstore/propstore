"""Phase 3 claim/condition integration: propstore COMPOSES condition-ir.

These prove the boundary story for conditions: every condition type, the checked
carrier, the json codec, the Z3 solver (incl. TIMEPOINT), and the sql/python/
estree backends are condition-ir's own types, used directly. propstore only wires
them to claims and keeps the non-commitment discipline (invalid conditions are
diagnosed, never dropped or aborted).
"""

from __future__ import annotations

import condition_ir
from condition_ir import (
    CheckedConditionSet,
    KindType,
    condition_ir_to_estree,
    condition_ir_to_python_ast,
    condition_ir_to_sql,
)

from propstore import claim_conditions as cc
from propstore.families.claims import Claim


def _quantity_registry() -> dict[str, condition_ir.ConceptInfo]:
    return {
        "freq": condition_ir.ConceptInfo(
            id="ps:concept:frequency",
            canonical_name="freq",
            kind=KindType.QUANTITY,
        )
    }


def test_check_claim_conditions_returns_package_checked_set() -> None:
    claim = Claim(claim_id="c1", conditions=("freq > 10", "freq < 100"))
    report = cc.check_claim_conditions(claim, _quantity_registry())
    assert isinstance(report.checked, CheckedConditionSet)
    assert len(report.checked.conditions) == 2
    assert report.diagnostics == ()


def test_invalid_condition_is_diagnosed_not_dropped() -> None:
    """A type-invalid CEL condition is recorded as a diagnostic, not an abort.

    The clean condition still checks; the bad one is quarantined in diagnostics.
    """

    claim = Claim(claim_id="c1", conditions=("freq > 10", "freq > 'abc'"))
    report = cc.check_claim_conditions(claim, _quantity_registry())
    assert len(report.checked.conditions) == 1
    assert len(report.diagnostics) == 1
    assert report.diagnostics[0].condition == "freq > 'abc'"


def test_conditions_ir_serializes_and_recompiles_without_reparse() -> None:
    """Stored conditions_ir is condition-ir's json codec; recompile is the codec.

    The round-trip reconstructs the package's CheckedConditionSet from the stored
    string via the codec — never by re-running the CEL front-end.
    """

    registry = _quantity_registry()
    claim = Claim(claim_id="c1", conditions=("freq > 10",))
    checked_claim = cc.check_claim(claim, registry)
    assert checked_claim.conditions_ir is not None

    recompiled = cc.compile_checked_conditions(checked_claim.conditions_ir)
    expected = cc.check_claim_conditions(claim, registry).checked
    assert recompiled == expected


def test_checked_condition_ir_drives_all_backends() -> None:
    """The compiled ConditionIR projects to sql/python/estree via condition-ir."""

    registry = _quantity_registry()
    report = cc.check_claim_conditions(
        Claim(claim_id="c1", conditions=("freq > 10",)), registry
    )
    ir = report.checked.conditions[0].ir
    assert condition_ir_to_sql(ir).sql
    assert condition_ir_to_python_ast(ir) is not None
    assert condition_ir_to_estree(ir) is not None
