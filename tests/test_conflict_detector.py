"""Conflict behavior over canonical claims admitted by the real compiler."""

from unittest.mock import MagicMock

import msgspec
import pytest
from condition_ir import (
    ConceptInfo,
    ConditionSolver,
    KindType,
    Z3TranslationError,
    check_condition_ir,
    checked_condition_set,
    synthetic_category_concept,
)

from propstore.conflict_detector import ConflictClass, detect_conflicts
from propstore.conflict_detector.algorithms import detect_algorithm_conflicts
from propstore.conflict_detector.condition_classifier import classify_conditions
from propstore.conflict_detector.equations import detect_equation_conflicts
from propstore.conflict_detector.measurements import detect_measurement_conflicts
from propstore.conflict_detector.models import coerce_conflict_class
from propstore.conflict_detector.parameter_claims import detect_parameter_conflicts
from propstore.families.claim_admission import (
    ClaimAdmissionError,
    ClaimAdmissionFailure,
)
from propstore.families.claim_provenance import ClaimProvenanceIndex
from propstore.families.claims import Claim, ClaimType, ClaimVariable
from propstore.families.forms import FormDefinition
from tests.checked_claim_helpers import check_claims, concept, frequency_form


def test_coerce_conflict_class_round_trips_and_uppercases() -> None:
    assert coerce_conflict_class(None) is None
    assert coerce_conflict_class(ConflictClass.CONFLICT) is ConflictClass.CONFLICT
    assert coerce_conflict_class("PHI_NODE") is ConflictClass.PHI_NODE
    assert coerce_conflict_class("phi_node") is ConflictClass.PHI_NODE


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ("x > 10", "x > 10", ConflictClass.CONFLICT),
        ("x > 10", "10 < x", ConflictClass.CONFLICT),
        ("x > 10", "x < 5", ConflictClass.PHI_NODE),
        ("x > 10", "x > 5", ConflictClass.OVERLAP),
    ],
)
def test_classify_checked_conditions(
    left: str, right: str, expected: ConflictClass
) -> None:
    registry = {"x": ConceptInfo("x", "x", KindType.QUANTITY)}
    assert (
        classify_conditions(
            checked_condition_set((check_condition_ir(left, registry),)),
            checked_condition_set((check_condition_ir(right, registry),)),
            solver=ConditionSolver(registry),
        )
        is expected
    )


def _equation(claim_id: str, expression: str) -> Claim:
    return Claim(
        claim_id=claim_id,
        claim_type=ClaimType.EQUATION,
        output_concept="output",
        expression=expression,
        variables=(
            ClaimVariable(concept="output", symbol="y", role="dependent"),
            ClaimVariable(concept="factor_a", symbol="x", role="independent"),
            ClaimVariable(concept="factor_b", symbol="z", role="independent"),
        ),
    )


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ("y = x + z", "x + z = y", None),
        ("y = x + z", "y = 2*x + z", ConflictClass.CONFLICT),
        ("y = log(x * z)", "y = log(x) + log(z)", ConflictClass.UNKNOWN),
    ],
)
def test_equation_comparison_uses_admitted_claims(left, right, expected) -> None:
    bundle, context = check_claims(
        (_equation("left", left), _equation("right", right)),
        tuple(concept(name) for name in ("output", "factor_a", "factor_b")),
    )
    assert not bundle.blocked_claims, bundle.diagnostics
    records = detect_equation_conflicts(
        [entry.claim for entry in bundle.claims],
        context.condition_registry,
        admissions=tuple(entry.admission for entry in bundle.claims),
        provenance=ClaimProvenanceIndex.from_micropublications(()),
    )
    assert [record.warning_class for record in records] == (
        [] if expected is None else [expected]
    )


def test_equation_detector_uses_each_claim_symbol_bindings() -> None:
    renamed = Claim(
        claim_id="renamed",
        claim_type=ClaimType.EQUATION,
        output_concept="output",
        expression="result = first + second",
        variables=(
            ClaimVariable(concept="output", symbol="result", role="dependent"),
            ClaimVariable(concept="factor_a", symbol="first", role="independent"),
            ClaimVariable(concept="factor_b", symbol="second", role="independent"),
        ),
    )
    bundle, context = check_claims(
        (_equation("original", "y = x + z"), renamed),
        tuple(concept(name) for name in ("output", "factor_a", "factor_b")),
    )
    assert not bundle.blocked_claims, bundle.diagnostics
    assert (
        detect_equation_conflicts(
            [entry.claim for entry in bundle.claims],
            context.condition_registry,
            admissions=tuple(entry.admission for entry in bundle.claims),
            provenance=ClaimProvenanceIndex.from_micropublications(()),
        )
        == []
    )


@pytest.mark.parametrize("invalid_first", [True, False])
def test_invalid_equation_is_rejected_by_canonical_admission(
    invalid_first: bool,
) -> None:
    claims = [_equation("invalid", "y = ("), _equation("valid", "y = x + z")]
    if not invalid_first:
        claims.reverse()
    bundle, context = check_claims(
        claims,
        tuple(concept(name) for name in ("output", "factor_a", "factor_b")),
    )
    assert [entry.claim.claim_id for entry in bundle.blocked_claims] == ["invalid"]
    with pytest.raises(ClaimAdmissionError) as caught:
        detect_equation_conflicts(
            [entry.claim for entry in bundle.claims],
            context.condition_registry,
            admissions=tuple(entry.admission for entry in bundle.claims),
            provenance=ClaimProvenanceIndex.from_micropublications(()),
        )
    assert caught.value.claim_id == "invalid"
    assert caught.value.reason is ClaimAdmissionFailure.QUARANTINED


def _algorithm(claim_id: str, body: str) -> Claim:
    return Claim(
        claim_id=claim_id,
        claim_type=ClaimType.ALGORITHM,
        output_concept="out",
        body=body,
        variables=(ClaimVariable(concept="input", symbol="x"),),
    )


@pytest.mark.parametrize(
    ("left", "right", "count"), [("x + x", "2 * x", 0), ("x", "x + 1", 1)]
)
def test_algorithm_comparison_uses_admitted_claims(
    left: str, right: str, count: int
) -> None:
    bundle, context = check_claims(
        (
            _algorithm("a", f"def f(x):\n    return {left}\n"),
            _algorithm("b", f"def f(x):\n    return {right}\n"),
        ),
        (concept("out"), concept("input")),
    )
    assert not bundle.blocked_claims, bundle.diagnostics
    records = detect_algorithm_conflicts(
        [entry.claim for entry in bundle.claims],
        context.condition_registry,
        admissions=tuple(entry.admission for entry in bundle.claims),
        provenance=ClaimProvenanceIndex.from_micropublications(()),
    )
    assert len(records) == count


def test_algorithm_partial_eval_equivalence_suppresses_conflict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from propstore.conflict_detector import algorithms

    class Result:
        equivalent = True
        similarity = 1.0

    bundle, context = check_claims(
        (
            _algorithm("a", "def f(x):\n    return x\n"),
            _algorithm("b", "def f(x):\n    return x\n"),
        ),
        (concept("out"), concept("input")),
    )
    monkeypatch.setattr(algorithms, "ast_compare", lambda *args, **kwargs: Result())
    assert (
        algorithms.detect_algorithm_conflicts(
            [entry.claim for entry in bundle.claims],
            context.condition_registry,
            admissions=tuple(entry.admission for entry in bundle.claims),
            provenance=ClaimProvenanceIndex.from_micropublications(()),
        )
        == []
    )


@pytest.mark.parametrize(
    ("populations", "values", "expected"),
    [
        (("adults", "children"), (10.0, 20.0), ConflictClass.PHI_NODE),
        (("adults", "adults"), (10.0, 20.0), ConflictClass.CONFLICT),
        ((None, None), (None, 20.0), None),
        ((None, None), (10.0, 10.0), None),
    ],
)
def test_measurement_comparison_uses_checked_conditions(
    populations, values, expected
) -> None:
    registry = {
        "population": synthetic_category_concept(
            concept_id="population",
            canonical_name="population",
            values=["adults", "children"],
            extensible=False,
        )
    }
    bundle, context = check_claims(
        tuple(
            Claim(
                claim_id=f"m{index}",
                claim_type=ClaimType.MEASUREMENT,
                target_concept="out",
                measure="mean",
                value=value,
                conditions=()
                if population is None
                else (f"population == '{population}'",),
            )
            for index, (population, value) in enumerate(
                zip(populations, values, strict=True)
            )
        ),
        (concept("out"),),
        condition_registry=registry,
    )
    assert not bundle.blocked_claims, bundle.diagnostics
    records = detect_measurement_conflicts(
        [entry.claim for entry in bundle.claims],
        context.condition_registry,
        admissions=tuple(entry.admission for entry in bundle.claims),
        provenance=ClaimProvenanceIndex.from_micropublications(()),
    )
    assert [record.warning_class for record in records] == (
        [] if expected is None else [expected]
    )


@pytest.mark.parametrize("failure", ["partition", "disjoint"])
def test_solver_runtime_errors_preserve_cause_text(failure: str) -> None:
    bundle, context = check_claims(
        tuple(
            Claim(
                claim_id=f"c{index}",
                claim_type=ClaimType.PARAMETER,
                output_concept="outcome",
                value=float(index),
                unit="1",
                conditions=("intention_to_treat == true",),
            )
            for index in range(3)
        ),
        (concept("outcome"),),
        condition_registry={
            "intention_to_treat": ConceptInfo(
                "intention_to_treat",
                "intention_to_treat",
                KindType.BOOLEAN,
            )
        },
    )
    assert not bundle.blocked_claims, bundle.diagnostics
    solver = MagicMock()
    underlying = (
        "Structural concept 'intention_to_treat' cannot appear in CEL expressions"
    )
    if failure == "partition":
        solver.partition_equivalence_classes.side_effect = Z3TranslationError(
            underlying
        )
    else:
        solver.partition_equivalence_classes.return_value = [[0], [1, 2]]
        solver.are_disjoint_result.side_effect = Z3TranslationError(underlying)
    with pytest.raises(RuntimeError) as caught:
        detect_parameter_conflicts(
            [entry.claim for entry in bundle.claims],
            context.condition_registry,
            admissions=tuple(entry.admission for entry in bundle.claims),
            provenance=ClaimProvenanceIndex.from_micropublications(()),
            solver=solver,
        )
    assert underlying in str(caught.value)
    assert ("partitioning" if failure == "partition" else "disjointness") in str(
        caught.value
    )


@pytest.mark.parametrize(
    ("value", "unit", "count"), [(0.2, "kHz", 0), (300.0, "Hz", 1)]
)
def test_detect_conflicts_consumes_checked_quantitative_units(
    value: float, unit: str, count: int
) -> None:
    bundle, context = check_claims(
        (
            Claim(
                claim_id="a",
                claim_type=ClaimType.PARAMETER,
                output_concept="frequency",
                value=200.0,
                unit="Hz",
            ),
            Claim(
                claim_id="b",
                claim_type=ClaimType.PARAMETER,
                output_concept="frequency",
                value=value,
                unit=unit,
            ),
        ),
        (concept("frequency", "frequency"),),
        forms=(frequency_form(),),
    )
    assert not bundle.blocked_claims, bundle.diagnostics
    records = detect_conflicts(
        [entry.claim for entry in bundle.claims],
        dict(context.concepts_by_id),
        context.condition_registry,
        admissions=tuple(entry.admission for entry in bundle.claims),
        provenance=ClaimProvenanceIndex.from_micropublications(()),
    )
    assert len(records) == count
    if records:
        assert records[0].warning_class is ConflictClass.CONFLICT


@pytest.mark.parametrize(
    ("kind", "values"),
    [(KindType.CATEGORY, ("red", "blue")), (KindType.BOOLEAN, (True, False))],
)
def test_canonical_scalar_types_retain_disagreement(kind: KindType, values) -> None:
    bundle, context = check_claims(
        tuple(
            Claim(
                claim_id=f"c{i}",
                claim_type=ClaimType.PARAMETER,
                output_concept="out",
                value=value,
            )
            for i, value in enumerate(values)
        ),
        (concept("out", "scalar"),),
        forms=(FormDefinition(name="scalar", kind=kind),),
        condition_registry={
            "out": ConceptInfo("out", "out", kind, category_extensible=True)
        },
    )
    assert not bundle.blocked_claims, bundle.diagnostics
    assert tuple(entry.claim.value for entry in bundle.claims) == values
    records = detect_conflicts(
        [entry.claim for entry in bundle.claims],
        dict(context.concepts_by_id),
        context.condition_registry,
        admissions=tuple(entry.admission for entry in bundle.claims),
        provenance=ClaimProvenanceIndex.from_micropublications(()),
    )
    assert [record.warning_class for record in records] == [ConflictClass.CONFLICT]


def test_missing_and_stale_admissions_are_typed_boundary_failures() -> None:
    bundle, context = check_claims(
        (
            Claim(
                claim_id="a",
                claim_type=ClaimType.PARAMETER,
                output_concept="out",
                value=1.0,
            ),
        ),
        (concept("out"),),
    )
    assert not bundle.blocked_claims, bundle.diagnostics
    checked = bundle.claims[0]
    with pytest.raises(ClaimAdmissionError) as missing:
        detect_conflicts(
            [checked.claim],
            dict(context.concepts_by_id),
            context.condition_registry,
            admissions=(),
            provenance=ClaimProvenanceIndex.from_micropublications(()),
        )
    assert missing.value.reason is ClaimAdmissionFailure.MISSING
    with pytest.raises(ClaimAdmissionError) as stale:
        detect_conflicts(
            [msgspec.structs.replace(checked.claim, value=2.0)],
            dict(context.concepts_by_id),
            context.condition_registry,
            admissions=(checked.admission,),
            provenance=ClaimProvenanceIndex.from_micropublications(()),
        )
    assert stale.value.reason is ClaimAdmissionFailure.STALE


def test_detect_conflicts_preserves_authored_source_concept() -> None:
    assert (
        detect_conflicts(
            [],
            {},
            {"source": ConceptInfo("real-source", "source", KindType.CATEGORY)},
            admissions=(),
            provenance=ClaimProvenanceIndex.from_micropublications(()),
        )
        == []
    )
