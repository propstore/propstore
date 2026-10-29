"""Compare checked quantitative evidence without reinterpreting authored IO."""

from __future__ import annotations

from fractions import Fraction
from typing import TypeAlias

from bridgman import canonicalize_dims
from condition_ir import KindType

from propstore.core.scalars import ScalarValue
from propstore.dimensions import normalize_to_si
from propstore.families.claim_quantitative import (
    IntervalValue,
    PointValue,
    QuantitativeEvidence,
)
from propstore.families.forms import FormDefinition

DEFAULT_TOLERANCE = 1e-9
Interval: TypeAlias = tuple[int | float, int | float, int | float]


def extract_interval(evidence: QuantitativeEvidence) -> Interval | None:
    """Return numeric comparison bounds; missing endpoints remain unbounded."""
    match evidence.value:
        case PointValue(value=value) if isinstance(
            value, int | float
        ) and not isinstance(value, bool):
            return value, value, value
        case IntervalValue(lower=lower, upper=upper, point=point):
            lo = float("-inf") if lower is None else lower
            hi = float("inf") if upper is None else upper
            center = (
                point
                if point is not None
                else (
                    (lo / 2 + hi / 2)
                    if lower is not None and upper is not None
                    else lower
                    if lower is not None
                    else upper
                )
            )
            assert center is not None
            return center, lo, hi
        case _:
            return None


def intervals_compatible(
    a: Interval, b: Interval, tolerance: float = DEFAULT_TOLERANCE
) -> bool:
    _, lo_a, hi_a = a
    _, lo_b, hi_b = b
    if abs(hi_a - lo_a) < tolerance and abs(hi_b - lo_b) < tolerance:
        return abs(Fraction(lo_a) - Fraction(lo_b)) < tolerance
    if lo_a > hi_b and (
        lo_a == float("inf")
        or hi_b == float("-inf")
        or Fraction(lo_a) - Fraction(hi_b) > tolerance
    ):
        return False
    return not (
        lo_b > hi_a
        and (
            lo_b == float("inf")
            or hi_a == float("-inf")
            or Fraction(lo_b) - Fraction(hi_a) > tolerance
        )
    )


def _normalized(
    evidence: QuantitativeEvidence, interval: Interval, target: FormDefinition | None
) -> Interval:
    form = evidence.form
    if form is None or form.kind is not KindType.QUANTITY or evidence.unit is None:
        return interval
    center, lower, upper = interval
    center = normalize_to_si(center, evidence.unit, form)
    # Open endpoints are comparison sentinels, never authored numeric evidence.
    lower = (
        normalize_to_si(lower, evidence.unit, form) if lower != float("-inf") else lower
    )
    upper = (
        normalize_to_si(upper, evidence.unit, form) if upper != float("inf") else upper
    )
    if target is not None and target != form:
        source_unit = form.unit_symbol or ("1" if form.is_dimensionless else None)
        center = normalize_to_si(center, source_unit, target)
        lower = (
            normalize_to_si(lower, source_unit, target)
            if lower != float("-inf")
            else lower
        )
        upper = (
            normalize_to_si(upper, source_unit, target)
            if upper != float("inf")
            else upper
        )
    return center, min(lower, upper), max(lower, upper)


def values_compatible(
    value_a: ScalarValue | None,
    value_b: ScalarValue | None,
    tolerance: float = DEFAULT_TOLERANCE,
    *,
    claim_a: QuantitativeEvidence | None = None,
    claim_b: QuantitativeEvidence | None = None,
) -> bool:
    """Compare the checked interval or exact categorical/boolean scalar types."""
    if claim_a is not None and claim_b is not None:
        form_a, form_b = claim_a.form, claim_b.form
        if form_a is not None and form_b is not None:
            if form_a.kind is not form_b.kind:
                return False
            if form_a.kind is KindType.QUANTITY and canonicalize_dims(
                form_a.dimensions or {}
            ) != canonicalize_dims(form_b.dimensions or {}):
                return False
        if (
            isinstance(claim_a.value, PointValue)
            and isinstance(claim_b.value, PointValue)
            and claim_a.unit == claim_b.unit
            and form_a == form_b
        ):
            return values_compatible(claim_a.point, claim_b.point, tolerance)
        a, b = extract_interval(claim_a), extract_interval(claim_b)
        if a is not None and b is not None:
            if claim_a.unit == claim_b.unit and form_a == form_b:
                return intervals_compatible(a, b, tolerance)
            return intervals_compatible(
                _normalized(claim_a, a, form_a),
                _normalized(claim_b, b, form_a),
                tolerance,
            )
        value_a, value_b = claim_a.point, claim_b.point
    if (
        isinstance(value_a, int | float)
        and not isinstance(value_a, bool)
        and isinstance(value_b, int | float)
        and not isinstance(value_b, bool)
    ):
        return abs(Fraction(value_a) - Fraction(value_b)) < tolerance
    return type(value_a) is type(value_b) and value_a == value_b


def value_str(
    value: ScalarValue | None,
    claim: QuantitativeEvidence | None = None,
    *,
    with_unit: bool = False,
) -> str:
    if claim is None:
        return str(value)
    match claim.value:
        case IntervalValue(lower=lower, upper=upper, point=point):
            bounds = f"[{lower if lower is not None else '-inf'}, {upper if upper is not None else 'inf'}]"
            rendered = bounds if point is None else f"{point} {bounds}"
        case _:
            rendered = str(claim.point)
    return f"{rendered} {claim.unit}" if with_unit and claim.unit else rendered
