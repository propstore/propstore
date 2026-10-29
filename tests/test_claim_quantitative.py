"""The checked quantitative owner rejects malformed IO and preserves valid data."""

import msgspec
import pytest
from condition_ir import KindType

from propstore.claim_contracts import validate_claim
from propstore.families.claim_quantitative import (
    AbsoluteUncertainty, AbsentValue, IntervalValue, PointValue,
    QuantitativeEvidence, RelativeUncertainty,
)
from propstore.families.claims import Claim, ClaimType
from propstore.families.forms import FormDefinition


def test_all_independent_malformed_invariants_are_reported() -> None:
    claim = Claim(claim_id="bad", claim_type=ClaimType.PARAMETER, output_concept="x",
        value=5.0, lower_bound=10.0, upper_bound=1.0, uncertainty=-0.25,
        confidence=2.0, sample_size=-7)
    report = validate_claim(claim, form=FormDefinition(name="length", kind=KindType.QUANTITY,
        dimensions={"L": 1}, unit_symbol="m"))
    assert report.quantitative is None
    assert {d.code for d in report.diagnostics} >= {
        "claim.quantitative.interval.order", "claim.quantitative.point.lower",
        "claim.quantitative.point.upper", "claim.quantitative.uncertainty.pair",
        "claim.quantitative.uncertainty.domain", "claim.quantitative.confidence",
        "claim.quantitative.sample_size", "claim.unit.required",
    }


@pytest.mark.parametrize("value", [1, 1.0, "red", True, False])
def test_exact_scalar_runtime_type_survives_checked_codec(value: int | float | str | bool) -> None:
    claim = Claim(claim_id="scalar", claim_type=ClaimType.MODEL, value=value)
    report = validate_claim(claim)
    assert report.diagnostics == ()
    assert report.quantitative is not None
    restored = msgspec.json.decode(msgspec.json.encode(report.quantitative), type=QuantitativeEvidence)
    assert type(restored.point) is type(value)
    assert restored.point == value


@pytest.mark.parametrize("lower,upper,point", [(1.0,None,2), (None,3.0,2), (1.0,3.0,2), (1.0,3.0,None)])
def test_intervals_preserve_open_endpoints(lower: float | None, upper: float | None, point: int | None) -> None:
    report = validate_claim(Claim(claim_id="interval", claim_type=ClaimType.MODEL,
        value=point, lower_bound=lower, upper_bound=upper))
    assert report.diagnostics == ()
    assert report.quantitative is not None
    assert report.quantitative.value == IntervalValue(lower, upper, point)


@pytest.mark.parametrize("field,value,code", [
    ("lower_bound", float("nan"), "claim.quantitative.finite"),
    ("sample_size", True, "claim.quantitative.sample_size"),
    ("sample_size", 0, "claim.quantitative.sample_size"),
    ("confidence", float("nan"), "claim.quantitative.confidence"),
    ("confidence", -0.1, "claim.quantitative.confidence"),
    ("uncertainty_type", "stddev", "claim.quantitative.uncertainty.type"),
])
def test_independent_invalid_fields(field: str, value: object, code: str) -> None:
    claim = msgspec.structs.replace(Claim(claim_id="invalid", claim_type=ClaimType.MODEL), **{field: value})
    assert code in {d.code for d in validate_claim(claim).diagnostics}


def test_dimensionless_default_and_relative_ratio_are_not_an_opinion() -> None:
    report = validate_claim(Claim(claim_id="ratio", claim_type=ClaimType.PARAMETER,
        output_concept="ratio", value=2, uncertainty=1.5, uncertainty_type="relative",
        confidence=0.0, sample_size=3),
        form=FormDefinition(name="ratio", kind=KindType.QUANTITY, is_dimensionless=True))
    assert report.diagnostics == ()
    assert report.quantitative is not None
    assert report.quantitative.unit == "1"
    assert report.quantitative.uncertainty == RelativeUncertainty(1.5)
    assert report.quantitative.confidence == 0.0


def test_absolute_distance_retains_physical_unit_and_absence_is_explicit() -> None:
    form = FormDefinition(name="length", kind=KindType.QUANTITY, dimensions={"L":1}, unit_symbol="m")
    report = validate_claim(Claim(claim_id="distance", claim_type=ClaimType.PARAMETER,
        output_concept="length", value=10, unit="m", uncertainty=2,
        uncertainty_type="absolute"), form=form)
    assert report.diagnostics == ()
    assert report.quantitative is not None
    assert report.quantitative.uncertainty == AbsoluteUncertainty(2, "m")
    absent = validate_claim(Claim(claim_id="empty", claim_type=ClaimType.MODEL)).quantitative
    assert absent is not None and absent.value == AbsentValue()


def test_checked_evidence_survives_compiler_admission_and_snapshot(tmp_path) -> None:
    from propstore.compiler.workflows import build_repository
    from propstore.repository import Repository
    from propstore.families.concepts import Concept
    from propstore.world import WorldQuery

    repo = Repository.init(tmp_path / "knowledge")
    repo.families.concept.save("x", Concept(concept_id="x", canonical_name="x"), message="Add concept")
    repo.families.claim.save("point", Claim(claim_id="point", claim_type=ClaimType.MODEL,
        value="red", confidence=1.0, sample_size=4), message="Add exact scalar")
    report = build_repository(repo)
    assert report.blocked_claim_count == 0
    with WorldQuery(repo) as world:
        claim = world.get_claim("point")
        assert claim is not None
        assert claim.quantitative.value == PointValue("red")
        assert claim.quantitative.sample_size == 4
