"""Parameterization derivation over canonical compiler-admitted claims."""

import warnings
from unittest.mock import patch

import pytest
from condition_ir import synthetic_category_concept, to_cel_exprs
from human_to_sympy import parse_cached

from propstore.conflict_detector import (
    ConflictClass,
    detect_conflicts,
    detect_transitive_conflicts,
)
from propstore.conflict_detector.parameterization_conflicts import (
    detect_parameterization_conflicts,
)
from propstore.context_lifting import LiftingSystem
from propstore.core.graph_types import ParameterizationEdge
from propstore.core.id_types import to_concept_id, to_concept_ids
from propstore.families.claim_provenance import ClaimProvenanceIndex
from propstore.families.claims import Claim, ClaimType, Exactness
from propstore.families.contexts import Context
from tests.canonical_claim_fixtures import concept_with_form
from tests.checked_claim_helpers import check_claims, frequency_form


def _parameter(
    claim_id: str,
    concept_id: str,
    value: float,
    *,
    unit: str = "Hz",
    conditions: tuple[str, ...] = (),
    context_id: str | None = None,
) -> Claim:
    return Claim(
        claim_id=claim_id,
        claim_type=ClaimType.PARAMETER,
        output_concept=concept_id,
        value=value,
        unit=unit,
        conditions=conditions,
        context_id=context_id,
    )


def _edge(
    output: str,
    inputs: tuple[str, ...],
    expression: str,
    *,
    conditions: tuple[str, ...] = (),
) -> ParameterizationEdge:
    return ParameterizationEdge(
        output_concept_id=to_concept_id(output),
        input_concept_ids=to_concept_ids(inputs),
        sympy=expression,
        exactness=Exactness.EXACT,
        conditions=to_cel_exprs(conditions),
    )


def test_equality_parameterization_evaluates_without_warning() -> None:
    bundle, context = check_claims(
        (
            _parameter("claim_a", "concept1", 10.0, unit="1"),
            _parameter("claim_b", "concept2", 9.807, unit="1"),
            _parameter("claim_c", "concept3", 99.0, unit="1"),
        ),
        tuple(
            concept_with_form(name, name, "quantity")
            for name in ("concept1", "concept2", "concept3")
        ),
    )
    assert not bundle.blocked_claims, bundle.diagnostics
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        records = detect_parameterization_conflicts(
            [entry.claim for entry in bundle.claims],
            dict(context.concepts_by_id),
            {
                "concept3": (
                    _edge(
                        "concept3",
                        ("concept1", "concept2"),
                        "Eq(concept3, concept1 * concept2)",
                    ),
                )
            },
            admissions=tuple(entry.admission for entry in bundle.claims),
            provenance=ClaimProvenanceIndex.from_micropublications(()),
            forms=context.form_registry.registry,
        )
    assert not [
        item
        for item in caught
        if "Could not evaluate parameterization" in str(item.message)
    ]
    assert len(records) == 1
    assert records[0].warning_class is ConflictClass.PARAM_CONFLICT
    assert records[0].concept_id == "concept3"
    assert records[0].claim_b_id == "claim_a"


@pytest.mark.parametrize(
    ("value", "unit", "rendered"), [(100.0, "Hz", "100.0 Hz"), (0.1, "kHz", "0.1 kHz")]
)
def test_single_hop_normalizes_units_and_renders_both_sides(
    value: float, unit: str, rendered: str
) -> None:
    bundle, context = check_claims(
        (
            _parameter("claim_khz", "freq_input", 0.5, unit="kHz"),
            _parameter("claim_out", "freq_output", value, unit=unit),
        ),
        (
            concept_with_form("freq_input", "freq_input", "frequency"),
            concept_with_form("freq_output", "freq_output", "frequency"),
        ),
        forms=(frequency_form(),),
    )
    assert not bundle.blocked_claims, bundle.diagnostics
    records = detect_parameterization_conflicts(
        [entry.claim for entry in bundle.claims],
        dict(context.concepts_by_id),
        {
            "freq_output": (
                _edge(
                    "freq_output", ("freq_input",), "Eq(freq_output, freq_input / 2)"
                ),
            )
        },
        admissions=tuple(entry.admission for entry in bundle.claims),
        provenance=ClaimProvenanceIndex.from_micropublications(()),
        forms=context.form_registry.registry,
    )
    assert len(records) == 1
    assert records[0].warning_class is ConflictClass.PARAM_CONFLICT
    assert records[0].value_a == rendered
    assert records[0].value_b == "250.0 Hz"


def test_single_hop_conflict_carries_derived_conditions() -> None:
    registry = {
        name: synthetic_category_concept(
            concept_id=name,
            canonical_name=name,
            values=(value,),
            extensible=False,
        )
        for name, value in (("task", "speech"), ("mode", "normal"))
    }
    bundle, context = check_claims(
        (
            _parameter(
                "claim_in",
                "concept_in",
                10.0,
                conditions=("task == 'speech'",),
                context_id="ctx_input",
            ),
            _parameter(
                "claim_out",
                "concept_out",
                100.0,
                conditions=("task == 'speech'", "mode == 'normal'"),
                context_id="ctx_input",
            ),
        ),
        (
            concept_with_form("concept_in", "concept_in", "frequency"),
            concept_with_form("concept_out", "concept_out", "frequency"),
        ),
        forms=(frequency_form(),),
        condition_registry=registry,
        context_ids=("ctx_input",),
    )
    assert not bundle.blocked_claims, bundle.diagnostics
    records = detect_parameterization_conflicts(
        [entry.claim for entry in bundle.claims],
        dict(context.concepts_by_id),
        {
            "concept_out": (
                _edge(
                    "concept_out",
                    ("concept_in",),
                    "Eq(concept_out, concept_in * 2)",
                    conditions=("mode == 'normal'",),
                ),
            )
        },
        admissions=tuple(entry.admission for entry in bundle.claims),
        provenance=ClaimProvenanceIndex.from_micropublications(()),
        forms=context.form_registry.registry,
    )
    assert len(records) == 1
    assert records[0].warning_class is ConflictClass.PARAM_CONFLICT
    assert [str(condition) for condition in records[0].conditions_b] == [
        "mode == 'normal'",
        "task == 'speech'",
    ]


def test_single_hop_conflict_requires_lifted_contexts() -> None:
    bundle, context = check_claims(
        (
            _parameter("claim_in", "concept_in", 10.0, context_id="ctx_input"),
            _parameter("claim_out", "concept_out", 100.0, context_id="ctx_direct"),
        ),
        (
            concept_with_form("concept_in", "concept_in", "frequency"),
            concept_with_form("concept_out", "concept_out", "frequency"),
        ),
        forms=(frequency_form(),),
        context_ids=("ctx_input", "ctx_direct"),
    )
    assert not bundle.blocked_claims, bundle.diagnostics
    lifting = LiftingSystem(
        contexts=(
            Context(context_id="ctx_input", name="input"),
            Context(context_id="ctx_direct", name="direct"),
        )
    )
    records = detect_conflicts(
        [entry.claim for entry in bundle.claims],
        dict(context.concepts_by_id),
        context.condition_registry,
        parameterizations={
            "concept_out": (
                _edge(
                    "concept_out", ("concept_in",), "Eq(concept_out, concept_in * 2)"
                ),
            )
        },
        lifting_system=lifting,
        forms=context.form_registry.registry,
        admissions=tuple(entry.admission for entry in bundle.claims),
        provenance=ClaimProvenanceIndex.from_micropublications(()),
    )
    assert [record.warning_class for record in records] == [
        ConflictClass.CONTEXT_PHI_NODE
    ]


def test_transitive_propagation_normalizes_units() -> None:
    bundle, context = check_claims(
        (
            _parameter("claim_a", "concept_a", 0.1, unit="kHz"),
            _parameter("claim_b", "concept_b", 200.0),
            _parameter("claim_c", "concept_c", 300.0),
        ),
        tuple(
            concept_with_form(name, name, "frequency")
            for name in ("concept_a", "concept_b", "concept_c")
        ),
        forms=(frequency_form(),),
    )
    assert not bundle.blocked_claims, bundle.diagnostics
    records = detect_transitive_conflicts(
        [entry.claim for entry in bundle.claims],
        dict(context.concepts_by_id),
        {
            "concept_b": (
                _edge("concept_b", ("concept_a",), "Eq(concept_b, concept_a * 2)"),
            ),
            "concept_c": (
                _edge("concept_c", ("concept_b",), "Eq(concept_c, concept_b + 100)"),
            ),
        },
        admissions=tuple(entry.admission for entry in bundle.claims),
        provenance=ClaimProvenanceIndex.from_micropublications(()),
        forms=context.form_registry.registry,
    )
    assert records == []


def test_transitive_conflict_detection_is_order_independent() -> None:
    bundle, context = check_claims(
        (
            _parameter("in_a", "concept_in", 10.0),
            _parameter("in_b", "concept_in", 20.0),
            _parameter("out_direct", "concept_out", 25.0),
        ),
        tuple(
            concept_with_form(name, name, "frequency")
            for name in ("concept_in", "concept_mid", "concept_out")
        ),
        forms=(frequency_form(),),
    )
    assert not bundle.blocked_claims, bundle.diagnostics
    edges = {
        "concept_mid": (
            _edge("concept_mid", ("concept_in",), "Eq(concept_mid, concept_in * 2)"),
        ),
        "concept_out": (
            _edge("concept_out", ("concept_mid",), "Eq(concept_out, concept_mid + 5)"),
        ),
    }
    outcomes = []
    for entries in (bundle.claims, tuple(reversed(bundle.claims))):
        records = detect_transitive_conflicts(
            [entry.claim for entry in entries],
            dict(context.concepts_by_id),
            edges,
            admissions=tuple(entry.admission for entry in bundle.claims),
            provenance=ClaimProvenanceIndex.from_micropublications(()),
            forms=context.form_registry.registry,
        )
        assert len(records) == 1
        outcomes.append((records[0].warning_class, records[0].value_b))
    assert outcomes == [(ConflictClass.PARAM_CONFLICT, "45.0 Hz")] * 2


def test_runtime_error_from_sympy_parameterization_propagates() -> None:
    bundle, context = check_claims(
        (
            _parameter("claim_a", "a", 2.0, unit="1"),
            _parameter("claim_b", "b", 3.0, unit="1"),
            _parameter("claim_derived", "derived", 10.0, unit="1"),
        ),
        tuple(
            concept_with_form(name, name, "quantity") for name in ("a", "b", "derived")
        ),
    )
    assert not bundle.blocked_claims, bundle.diagnostics
    parse_cached.cache_clear()
    try:
        with (
            patch(
                "sympy.parsing.sympy_parser.parse_expr",
                side_effect=RuntimeError("boom"),
            ),
            pytest.raises(RuntimeError, match="boom"),
        ):
            detect_parameterization_conflicts(
                [entry.claim for entry in bundle.claims],
                dict(context.concepts_by_id),
                {"derived": (_edge("derived", ("a", "b"), "Eq(derived, a * b)"),)},
                admissions=tuple(entry.admission for entry in bundle.claims),
                provenance=ClaimProvenanceIndex.from_micropublications(()),
                forms=context.form_registry.registry,
            )
    finally:
        parse_cached.cache_clear()
