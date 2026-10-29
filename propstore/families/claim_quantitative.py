"""Checked claim measurement values and evidence, distinct from opinions.

Intervals have inclusive finite authored endpoints; a missing endpoint is open
in that direction. Absolute uncertainty is a nonnegative distance in the
resolved unit. Relative uncertainty is a nonnegative dimensionless ratio and
can exceed one. Confidence is a probability in the closed interval [0, 1].
"""

from __future__ import annotations

from math import isfinite

import msgspec

from propstore.core.scalars import ScalarValue, validate_scalar_value
from propstore.families.forms import FormDefinition


class AbsentValue(msgspec.Struct, frozen=True, tag="absent"):
    """No scalar or interval was stated."""


class PointValue(msgspec.Struct, frozen=True, tag="point"):
    value: ScalarValue

    def __post_init__(self) -> None:
        validate_scalar_value(self.value)


class IntervalValue(msgspec.Struct, frozen=True, tag="interval"):
    lower: float | None
    upper: float | None
    point: int | float | None = None

    def __post_init__(self) -> None:
        if self.lower is None and self.upper is None:
            raise ValueError("an interval requires at least one bound")
        for value in (self.lower, self.upper, self.point):
            if value is not None and (isinstance(value, bool) or not isfinite(value)):
                raise ValueError("interval numbers must be finite and exclude boolean")
        if (
            self.lower is not None
            and self.upper is not None
            and self.lower > self.upper
        ):
            raise ValueError("interval lower bound exceeds upper bound")
        if self.point is not None and (
            (self.lower is not None and self.point < self.lower)
            or (self.upper is not None and self.point > self.upper)
        ):
            raise ValueError("interval point is outside its bounds")


type QuantitativeValue = AbsentValue | PointValue | IntervalValue


class AbsoluteUncertainty(msgspec.Struct, frozen=True, tag="absolute"):
    magnitude: float
    unit: str

    def __post_init__(self) -> None:
        if (
            not self.unit
            or isinstance(self.magnitude, bool)
            or not isfinite(self.magnitude)
            or self.magnitude < 0
        ):
            raise ValueError(
                "absolute uncertainty requires finite nonnegative distance and unit"
            )


class RelativeUncertainty(msgspec.Struct, frozen=True, tag="relative"):
    magnitude: float

    def __post_init__(self) -> None:
        if (
            isinstance(self.magnitude, bool)
            or not isfinite(self.magnitude)
            or self.magnitude < 0
        ):
            raise ValueError("relative uncertainty must be a finite nonnegative ratio")


type MeasurementUncertainty = AbsoluteUncertainty | RelativeUncertainty


class QuantitativeEvidence(msgspec.Struct, frozen=True):
    """The sole checked quantitative object carried by canonical claims."""

    value: QuantitativeValue
    form: FormDefinition | None
    unit: str | None
    uncertainty: MeasurementUncertainty | None = None
    confidence: float | None = None
    sample_size: int | None = None

    def __post_init__(self) -> None:
        if self.unit is not None and self.form is None:
            raise ValueError("a checked unit requires a resolved form")
        if self.confidence is not None and (
            isinstance(self.confidence, bool)
            or not isfinite(self.confidence)
            or not 0 <= self.confidence <= 1
        ):
            raise ValueError("confidence must be in [0, 1]")
        if self.sample_size is not None and (
            type(self.sample_size) is not int or self.sample_size <= 0
        ):
            raise ValueError("sample_size must be a positive integer")
        if (
            isinstance(self.uncertainty, AbsoluteUncertainty)
            and self.uncertainty.unit != self.unit
        ):
            raise ValueError(
                "absolute uncertainty must use the resolved measurement unit"
            )

    @property
    def point(self) -> ScalarValue | None:
        match self.value:
            case PointValue(value=value):
                return value
            case IntervalValue(point=point):
                return point
            case AbsentValue():
                return None
