"""Preference reads checked evidence and keeps measurement uncertainty separate."""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from propstore.core.active_claims import ActiveClaim
from propstore.families.claim_quantitative import (
    AbsentValue,
    PointValue,
    QuantitativeEvidence,
    RelativeUncertainty,
)
from propstore.preference import claim_strength, metadata_strength_vector
from propstore.provenance import ProvenanceStatus


def test_named_heuristic_matches_claim_strength() -> None:
    claim = ActiveClaim(
        claim_id="sample",
        quantitative=QuantitativeEvidence(
            PointValue(1), None, None, RelativeUncertainty(2), 0.8, 25
        ),
    )
    assert metadata_strength_vector(claim) == claim_strength(claim)


def test_larger_sample_is_stronger() -> None:
    small = ActiveClaim(
        claim_id="small",
        quantitative=QuantitativeEvidence(
            AbsentValue(), None, None, confidence=0.8, sample_size=10
        ),
    )
    large = ActiveClaim(
        claim_id="large",
        quantitative=QuantitativeEvidence(
            AbsentValue(), None, None, confidence=0.8, sample_size=1000
        ),
    )
    assert claim_strength(large).dimensions[0] > claim_strength(small).dimensions[0]
    assert claim_strength(large).dimensions[1] > claim_strength(small).dimensions[1]


def test_confidence_coordinate_retains_its_declared_probability() -> None:
    for confidence in (0, 0.55, 0.95, 1):
        claim = ActiveClaim(
            claim_id="confidence",
            quantitative=QuantitativeEvidence(
                AbsentValue(), None, None, confidence=confidence, sample_size=100
            ),
        )
        assert claim_strength(claim).dimensions[2] == confidence


def test_measurement_uncertainty_is_not_subjective_ignorance() -> None:
    vectors = [
        claim_strength(
            ActiveClaim(
                claim_id=str(magnitude),
                quantitative=QuantitativeEvidence(
                    PointValue(10), None, None, RelativeUncertainty(magnitude), 0.8, 10
                ),
            )
        )
        for magnitude in (0, 0.01, 0.5, 2)
    ]
    assert all(vector == vectors[0] for vector in vectors)


def test_absent_evidence_is_vacuous() -> None:
    vector = claim_strength(ActiveClaim(claim_id="empty"))
    assert vector.dimensions == (0, 0, 0)
    assert vector.is_vacuous
    assert vector.provenance.status is ProvenanceStatus.VACUOUS


@pytest.mark.parametrize("sample,confidence", [(None, None), (50, None), (None, 0.7)])
def test_partial_evidence_has_commensurable_dimensions_and_vacuous_opinion(
    sample, confidence
) -> None:
    vector = claim_strength(
        ActiveClaim(
            claim_id="partial",
            quantitative=QuantitativeEvidence(
                AbsentValue(), None, None, confidence=confidence, sample_size=sample
            ),
        )
    )
    assert len(vector.dimensions) == 3
    assert vector.is_vacuous


@pytest.mark.parametrize("sample", [True, 0, -7])
def test_invalid_sample_is_rejected_at_checked_owner(sample) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        QuantitativeEvidence(AbsentValue(), None, None, sample_size=sample)


@given(
    sample=st.one_of(st.none(), st.integers(min_value=1, max_value=100000)),
    confidence=st.one_of(
        st.none(),
        st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
    ),
)
@settings(deadline=None)
def test_strength_always_has_three_nonnegative_coordinates(sample, confidence) -> None:
    vector = claim_strength(
        ActiveClaim(
            claim_id="property",
            quantitative=QuantitativeEvidence(
                AbsentValue(), None, None, confidence=confidence, sample_size=sample
            ),
        )
    )
    assert len(vector.dimensions) == 3
    assert all(value >= 0 for value in vector.dimensions)
