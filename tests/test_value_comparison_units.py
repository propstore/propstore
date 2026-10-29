"""Ported from the May-16 reference: unit-aware value comparison.

``values_compatible`` normalizes claim intervals to SI before comparing when a
form and the claims' units are available, so ``200 Hz`` and ``0.2 kHz`` match.
"""

from __future__ import annotations

import pytest

from propstore.core.scalars import ScalarValue
from propstore.families.claim_quantitative import PointValue, QuantitativeEvidence
from propstore.value_comparison import values_compatible
from tests.checked_claim_helpers import frequency_form


def test_values_compatible_different_units_same_value() -> None:
    form = frequency_form()
    assert values_compatible(
        None,
        None,
        claim_a=QuantitativeEvidence(PointValue(200.0), form, "Hz"),
        claim_b=QuantitativeEvidence(PointValue(0.2), form, "kHz"),
    )


def test_values_compatible_different_units_different_value() -> None:
    form = frequency_form()
    assert not values_compatible(
        None,
        None,
        claim_a=QuantitativeEvidence(PointValue(200.0), form, "Hz"),
        claim_b=QuantitativeEvidence(PointValue(0.3), form, "kHz"),
    )


def test_values_compatible_without_form_or_unit_evidence() -> None:
    # Unspecified unit evidence leaves these distinct numeric points distinct.
    assert not values_compatible(
        None,
        None,
        claim_a=QuantitativeEvidence(PointValue(200.0), None, None),
        claim_b=QuantitativeEvidence(PointValue(0.2), None, None),
    )


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ("5", 5, False),
        (True, 1, False),
        (1, 1.0, True),
        ("5", "5", True),
        (True, True, True),
    ],
)
def test_values_compatible_separates_direct_and_numeric_scalars(
    left: ScalarValue,
    right: ScalarValue,
    expected: bool,
) -> None:
    assert values_compatible(left, right) is expected
