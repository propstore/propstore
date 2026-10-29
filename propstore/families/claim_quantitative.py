"""Checked claim measurement values and evidence, distinct from opinions.

Intervals have inclusive finite authored endpoints; a missing endpoint is open
in that direction. Absolute uncertainty is a nonnegative distance in the
resolved unit. Relative uncertainty is a nonnegative dimensionless ratio and
can exceed one. Confidence is a probability in the closed interval [0, 1].
"""

from __future__ import annotations

import msgspec

from propstore.core.scalars import ScalarValue
from propstore.families.forms import FormDefinition


class AbsentValue(msgspec.Struct, frozen=True, tag="absent"):
    """No scalar or interval was stated."""


class PointValue(msgspec.Struct, frozen=True, tag="point"):
    value: ScalarValue


class IntervalValue(msgspec.Struct, frozen=True, tag="interval"):
    lower: float | None
    upper: float | None
    point: int | float | None = None


type QuantitativeValue = AbsentValue | PointValue | IntervalValue


class AbsoluteUncertainty(msgspec.Struct, frozen=True, tag="absolute"):
    magnitude: float
    unit: str


class RelativeUncertainty(msgspec.Struct, frozen=True, tag="relative"):
    magnitude: float


type MeasurementUncertainty = AbsoluteUncertainty | RelativeUncertainty


class QuantitativeEvidence(msgspec.Struct, frozen=True):
    """The sole checked quantitative object carried by canonical claims."""

    value: QuantitativeValue
    form: FormDefinition | None
    unit: str | None
    uncertainty: MeasurementUncertainty | None = None
    confidence: float | None = None
    sample_size: int | None = None

    @property
    def point(self) -> ScalarValue | None:
        match self.value:
            case PointValue(value=value):
                return value
            case IntervalValue(point=point):
                return point
            case AbsentValue():
                return None
