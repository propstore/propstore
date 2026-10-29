"""The checked quantitative owner rejects malformed IO and preserves valid data."""

from pathlib import Path

import msgspec
import pytest
from condition_ir import KindType

from propstore.claim_contracts import validate_claim
from propstore.compiler.context import CompilationContext
from propstore.compiler.workflows import compile_repository_checked_bundle
from propstore.families.claim_quantitative import (
    AbsentValue,
    AbsoluteUncertainty,
    IntervalValue,
    PointValue,
    QuantitativeEvidence,
    RelativeUncertainty,
)
from propstore.families.claims import Claim, ClaimType
from propstore.families.forms import FormDefinition
from propstore.repository import Repository
from tests.canonical_claim_fixtures import concept_with_form


def _checked_context(
    tmp_path: Path, form: FormDefinition, concept_id: str
) -> CompilationContext:
    repo = Repository.init(tmp_path / "checked-context")
    repo.families.form.save(form.name, form, message="Declare quantitative form")
    repo.families.concept.save(
        concept_id,
        concept_with_form(concept_id, "quantity", form.name),
        message="Declare quantitative concept",
    )
    checked = compile_repository_checked_bundle(repo, commit=None)
    assert checked is not None
    return checked.compilation_context


def test_all_independent_malformed_invariants_are_reported(tmp_path: Path) -> None:
    claim = Claim(
        claim_id="bad",
        claim_type=ClaimType.PARAMETER,
        output_concept="x",
        value=5.0,
        lower_bound=10.0,
        upper_bound=1.0,
        uncertainty=-0.25,
        confidence=2.0,
        sample_size=-7,
    )
    report = validate_claim(
        claim,
        context=_checked_context(
            tmp_path,
            FormDefinition(
                name="length",
                kind=KindType.QUANTITY,
                dimensions={"L": 1},
                unit_symbol="m",
            ),
            "x",
        ),
    )
    assert report.quantitative is None
    assert {d.code for d in report.diagnostics} >= {
        "claim.quantitative.interval.order",
        "claim.quantitative.point.lower",
        "claim.quantitative.point.upper",
        "claim.quantitative.uncertainty.pair",
        "claim.quantitative.uncertainty.domain",
        "claim.quantitative.confidence",
        "claim.quantitative.sample_size",
        "claim.unit.required",
    }


@pytest.mark.parametrize("value", [1, 1.0, "red", True, False])
def test_exact_scalar_runtime_type_survives_checked_codec(
    value: float | str | bool,
) -> None:
    claim = Claim(claim_id="scalar", claim_type=ClaimType.MODEL, value=value)
    report = validate_claim(claim)
    assert report.diagnostics == ()
    assert report.quantitative is not None
    restored = msgspec.json.decode(
        msgspec.json.encode(report.quantitative), type=QuantitativeEvidence
    )
    assert type(restored.point) is type(value)
    assert restored.point == value


@pytest.mark.parametrize(
    "lower,upper,point",
    [(1.0, None, 2), (None, 3.0, 2), (1.0, 3.0, 2), (1.0, 3.0, None)],
)
def test_intervals_preserve_open_endpoints(
    lower: float | None, upper: float | None, point: int | None
) -> None:
    report = validate_claim(
        Claim(
            claim_id="interval",
            claim_type=ClaimType.MODEL,
            value=point,
            lower_bound=lower,
            upper_bound=upper,
        )
    )
    assert report.diagnostics == ()
    assert report.quantitative is not None
    assert report.quantitative.value == IntervalValue(lower, upper, point)


@pytest.mark.parametrize(
    "field,value,code",
    [
        ("lower_bound", float("nan"), "claim.quantitative.finite"),
        ("sample_size", True, "claim.quantitative.sample_size"),
        ("sample_size", 0, "claim.quantitative.sample_size"),
        ("confidence", float("nan"), "claim.quantitative.confidence"),
        ("confidence", -0.1, "claim.quantitative.confidence"),
        ("uncertainty_type", "stddev", "claim.quantitative.uncertainty.type"),
    ],
)
def test_independent_invalid_fields(field: str, value: object, code: str) -> None:
    claim = msgspec.structs.replace(
        Claim(claim_id="invalid", claim_type=ClaimType.MODEL), **{field: value}
    )
    assert code in {d.code for d in validate_claim(claim).diagnostics}


def test_dimensionless_default_and_relative_ratio_are_not_an_opinion(
    tmp_path: Path,
) -> None:
    report = validate_claim(
        Claim(
            claim_id="ratio",
            claim_type=ClaimType.PARAMETER,
            output_concept="ratio",
            value=2,
            uncertainty=1.5,
            uncertainty_type="relative",
            confidence=0.0,
            sample_size=3,
        ),
        context=_checked_context(
            tmp_path,
            FormDefinition(name="ratio", kind=KindType.QUANTITY, is_dimensionless=True),
            "ratio",
        ),
    )
    assert report.diagnostics == ()
    assert report.quantitative is not None
    assert report.quantitative.unit == "1"
    assert report.quantitative.uncertainty == RelativeUncertainty(1.5)
    assert report.quantitative.confidence == 0.0


def test_absolute_distance_retains_physical_unit_and_absence_is_explicit(
    tmp_path: Path,
) -> None:
    form = FormDefinition(
        name="length", kind=KindType.QUANTITY, dimensions={"L": 1}, unit_symbol="m"
    )
    report = validate_claim(
        Claim(
            claim_id="distance",
            claim_type=ClaimType.PARAMETER,
            output_concept="length",
            value=10,
            unit="m",
            uncertainty=2,
            uncertainty_type="absolute",
        ),
        context=_checked_context(tmp_path, form, "length"),
    )
    assert report.diagnostics == ()
    assert report.quantitative is not None
    assert report.quantitative.uncertainty == AbsoluteUncertainty(2, "m")
    absent = validate_claim(
        Claim(claim_id="empty", claim_type=ClaimType.MODEL)
    ).quantitative
    assert absent is not None and absent.value == AbsentValue()


def test_checked_evidence_survives_compiler_admission_and_snapshot(
    tmp_path: Path,
) -> None:
    from propstore.compiler.workflows import build_repository
    from propstore.families.concepts import Concept
    from propstore.repository import Repository
    from propstore.world import WorldQuery

    repo = Repository.init(tmp_path / "knowledge")
    repo.families.concept.save(
        "x", Concept(concept_id="x", canonical_name="x"), message="Add concept"
    )
    repo.families.claim.save(
        "point",
        Claim(
            claim_id="point",
            claim_type=ClaimType.MODEL,
            value="red",
            confidence=1.0,
            sample_size=4,
        ),
        message="Add exact scalar",
    )
    report = build_repository(repo)
    assert report.blocked_claim_count == 0
    with WorldQuery(repo) as world:
        claim = world.get_claim("point")
        assert claim is not None
        assert claim.quantitative.value == PointValue("red")
        assert claim.quantitative.sample_size == 4


def test_comparison_uses_exact_category_boolean_and_open_intervals() -> None:
    from propstore.value_comparison import values_compatible

    red = QuantitativeEvidence(PointValue("red"), None, None)
    blue = QuantitativeEvidence(PointValue("blue"), None, None)
    true = QuantitativeEvidence(PointValue(True), None, None)
    one = QuantitativeEvidence(PointValue(1), None, None)
    assert not values_compatible(None, None, claim_a=red, claim_b=blue)
    assert not values_compatible(None, None, claim_a=true, claim_b=one)
    left = QuantitativeEvidence(IntervalValue(None, 2), None, None)
    right = QuantitativeEvidence(IntervalValue(3, None), None, None)
    assert not values_compatible(None, None, claim_a=left, claim_b=right)


def test_adjacent_large_canonical_integers_compare_without_float_loss() -> None:
    from propstore.value_comparison import values_compatible

    left = QuantitativeEvidence(PointValue(2**53), None, None)
    right = QuantitativeEvidence(PointValue(2**53 + 1), None, None)
    assert not values_compatible(None, None, claim_a=left, claim_b=right)
    assert not values_compatible(2**53 + 1, float(2**53))


def test_different_physical_dimensions_are_not_comparable_numbers() -> None:
    from propstore.value_comparison import values_compatible

    length = FormDefinition(
        name="length", kind=KindType.QUANTITY, dimensions={"L": 1}, unit_symbol="m"
    )
    time = FormDefinition(
        name="time", kind=KindType.QUANTITY, dimensions={"T": 1}, unit_symbol="s"
    )
    assert not values_compatible(
        None,
        None,
        claim_a=QuantitativeEvidence(PointValue(1), length, "m"),
        claim_b=QuantitativeEvidence(PointValue(1), time, "s"),
    )


def test_compatible_physical_forms_compare_in_one_canonical_unit() -> None:
    from propstore.value_comparison import values_compatible

    meters = FormDefinition(
        name="meters", kind=KindType.QUANTITY, dimensions={"L": 1}, unit_symbol="m"
    )
    centimeters = FormDefinition(
        name="centimeters",
        kind=KindType.QUANTITY,
        dimensions={"L": 1},
        unit_symbol="cm",
    )
    assert values_compatible(
        None,
        None,
        claim_a=QuantitativeEvidence(PointValue(1), meters, "m"),
        claim_b=QuantitativeEvidence(PointValue(100), centimeters, "cm"),
    )


def test_measurement_uncertainty_does_not_become_subjective_ignorance() -> None:
    from propstore.core.active_claims import ActiveClaim
    from propstore.preference import metadata_strength_vector

    evidence = QuantitativeEvidence(
        PointValue(4), None, None, RelativeUncertainty(2), 0.8, None
    )
    vector = metadata_strength_vector(
        ActiveClaim(claim_id="ratio", quantitative=evidence)
    )
    assert vector.is_vacuous
    assert vector.dimensions == (0, 0, 0.8)


def test_sample_resolution_reads_positive_checked_integer() -> None:
    from propstore.core.active_claims import ActiveClaim
    from propstore.world.resolution import _resolve_sample_size

    claims = [
        ActiveClaim(
            claim_id=str(n),
            quantitative=QuantitativeEvidence(PointValue(n), None, None, sample_size=n),
        )
        for n in (2, 10)
    ]
    assert _resolve_sample_size(claims)[0] == "10"
    with pytest.raises(ValueError, match="positive integer"):
        QuantitativeEvidence(PointValue(2), None, None, sample_size=-7)


def test_identity_hash_reads_checked_evidence_not_raw_authoring_bag() -> None:
    from propstore.core.assertions.claim_identity import claim_assertion_id

    evidence = QuantitativeEvidence(PointValue("red"), None, None)
    claim = Claim(
        claim_id="a", claim_type=ClaimType.MODEL, value="red", quantitative_ir=evidence
    )
    changed_io = msgspec.structs.replace(claim, value="blue")
    assert claim_assertion_id(claim, context_id=None) == claim_assertion_id(
        changed_io, context_id=None
    )
    changed_owner = msgspec.structs.replace(
        claim, quantitative_ir=QuantitativeEvidence(PointValue("blue"), None, None)
    )
    assert claim_assertion_id(claim, context_id=None) != claim_assertion_id(
        changed_owner, context_id=None
    )


def test_quarantined_merge_branch_exposes_diagnostics_without_target_mutation(
    tmp_path: Path,
) -> None:
    from propstore.families.concepts import Concept
    from propstore.merge.merge_commit import (
        QuarantinedMergeClaimsError,
        create_merge_commit,
    )
    from propstore.repository import Repository

    repo = Repository.init(tmp_path / "merge")
    repo.families.concept.save(
        "x", Concept(concept_id="x", canonical_name="x"), message="Add concept"
    )
    git = repo.require_git()
    original = git.branch_sha("master")
    assert original is not None
    git.create_branch("left", original)
    git.create_branch("right", original)
    repo.families.claim.save(
        "bad",
        Claim(claim_id="bad", claim_type=ClaimType.OBSERVATION),
        message="Add malformed observation",
        branch="left",
    )
    with pytest.raises(QuarantinedMergeClaimsError) as error:
        create_merge_commit(repo, "left", "right", target_branch="master")
    assert error.value.artifacts[0].claim.claim_id == "bad"
    assert "statement" in str(error.value)
    assert git.branch_sha("master") == original
    raw = tuple(repo.families.claim.iter_handles(commit=git.branch_sha("left")))
    assert raw[0].document.statement is None


def test_source_lowering_preserves_confidence_and_measurement_evidence(
    tmp_path: Path,
) -> None:
    from propstore.families.sources import SourceClaimDocument
    from propstore.source.claim_concepts import build_promoted_claim

    source = SourceClaimDocument(
        artifact_id="canonical",
        type=ClaimType.PARAMETER,
        concept="length",
        value=5,
        lower_bound=4,
        upper_bound=6,
        uncertainty=0.2,
        uncertainty_type="absolute",
        unit="m",
        confidence=0.9,
        sample_size=12,
    )
    lowered = build_promoted_claim(
        source, concept_map={"length": "ps:concept:length"}, unresolved=set()
    )
    report = validate_claim(
        lowered,
        context=_checked_context(
            tmp_path,
            FormDefinition(
                name="length",
                kind=KindType.QUANTITY,
                dimensions={"L": 1},
                unit_symbol="m",
            ),
            "ps:concept:length",
        ),
    )
    assert report.diagnostics == ()
    assert report.quantitative is not None
    assert report.quantitative.value == IntervalValue(4, 6, 5)
    assert report.quantitative.confidence == 0.9
    assert report.quantitative.sample_size == 12
    assert report.quantitative.uncertainty == AbsoluteUncertainty(0.2, "m")


def test_measure_only_claim_does_not_acquire_parameter_unit_requirements() -> None:
    report = validate_claim(
        Claim(
            claim_id="method",
            claim_type=ClaimType.MEASUREMENT,
            target_concept="x",
            measure="Visual count",
        )
    )
    assert report.diagnostics == ()
    assert report.quantitative is not None
    assert report.quantitative.value == AbsentValue()
    assert report.quantitative.form is None


def test_optional_observation_unit_policy_does_not_become_required() -> None:
    report = validate_claim(
        Claim(
            claim_id="observation",
            claim_type=ClaimType.OBSERVATION,
            statement="Measured length",
            value=2,
        ),
        form=FormDefinition(
            name="length", kind=KindType.QUANTITY, dimensions={"L": 1}, unit_symbol="m"
        ),
    )
    assert report.diagnostics == ()
    assert report.quantitative is not None
    assert report.quantitative.unit is None


def test_overlay_replacement_gets_fresh_checked_owner_and_admission(
    tmp_path: Path,
) -> None:
    from propstore.compiler.workflows import build_repository
    from propstore.families.concepts import Concept
    from propstore.repository import Repository
    from propstore.world import WorldQuery
    from propstore.world.overlay import _synthetic_claim
    from propstore.world.types import SyntheticClaim

    repo = Repository.init(tmp_path / "overlay")
    repo.families.concept.save(
        "x", Concept(concept_id="x", canonical_name="x"), message="Add concept"
    )
    build_repository(repo)
    with WorldQuery(repo) as world:
        first = _synthetic_claim(
            SyntheticClaim(
                id="synthetic", concept_id="x", type=ClaimType.MODEL, value=1
            ),
            existing=None,
            solver=world.condition_solver(),
            store=world,
        )
        changed = _synthetic_claim(
            SyntheticClaim(
                id="synthetic", concept_id="x", type=ClaimType.MODEL, value=2
            ),
            existing=first.claim,
            solver=world.condition_solver(),
            store=world,
        )
    first.admission.verify(first.claim)
    changed.admission.verify(changed.claim)
    assert first.claim.quantitative.point == 1
    assert changed.claim.quantitative.point == 2
    with pytest.raises(ValueError, match="stale"):
        first.admission.verify(changed.claim)


def test_interval_only_claim_view_does_not_report_absence() -> None:
    from propstore.app.claim_views import _claim_value
    from propstore.app.view_state import ViewState

    claim = Claim(
        claim_id="interval",
        claim_type=ClaimType.MODEL,
        quantitative_ir=QuantitativeEvidence(IntervalValue(1, 3), None, None),
    )
    value = _claim_value(claim)
    assert value.state is ViewState.KNOWN
    assert "[1, 3]" in value.sentence


def test_large_point_below_same_unit_interval_does_not_widen_during_comparison() -> (
    None
):
    from propstore.value_comparison import values_compatible

    form = FormDefinition(
        name="frequency", kind=KindType.QUANTITY, dimensions={"T": -1}, unit_symbol="Hz"
    )
    point = QuantitativeEvidence(PointValue(2**53 + 3), form, "kHz")
    interval = QuantitativeEvidence(IntervalValue(float(2**53 + 4), None), form, "kHz")
    assert not values_compatible(None, None, claim_a=point, claim_b=interval)
