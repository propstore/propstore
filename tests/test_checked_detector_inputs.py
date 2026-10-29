"""Conflict inputs are canonical, exact and admitted by the real compiler."""

import msgspec
import pytest
from condition_ir import KindType

from propstore.conflict_detector import ConflictClass, detect_conflicts
from propstore.context_lifting import LiftingSystem
from propstore.families.claim_admission import (
    ClaimAdmissionError,
    ClaimAdmissionFailure,
)
from propstore.families.claim_provenance import ClaimProvenanceIndex
from propstore.families.claims import Claim, ClaimType
from propstore.families.contexts import Context, LiftingRule
from propstore.families.forms import FormDefinition
from tests.canonical_claim_fixtures import concept_with_form
from tests.checked_claim_helpers import check_claims, quantity_form


@pytest.mark.parametrize(
    ("left", "right", "kind"),
    (
        ("red", "blue", KindType.CATEGORY),
        (True, False, KindType.BOOLEAN),
        (2**53 + 1, 2**53 + 2, KindType.QUANTITY),
    ),
)
def test_exact_canonical_scalar_values_disagree(left, right, kind) -> None:
    form = (
        quantity_form()
        if kind is KindType.QUANTITY
        else FormDefinition(name="quantity", kind=kind)
    )
    bundle, context = check_claims(
        (
            Claim(
                claim_id="a",
                claim_type=ClaimType.PARAMETER,
                output_concept="x",
                value=left,
            ),
            Claim(
                claim_id="b",
                claim_type=ClaimType.PARAMETER,
                output_concept="x",
                value=right,
            ),
        ),
        (concept_with_form("x", "x", "quantity"),),
        forms=(form,),
    )
    assert bundle.blocked_claims == (), bundle.diagnostics
    claims = tuple(entry.claim for entry in bundle.checked_claims)
    records = detect_conflicts(
        claims,
        context.concepts_by_id,
        context.condition_registry,
        admissions=tuple(entry.admission for entry in bundle.checked_claims),
        provenance=ClaimProvenanceIndex.from_micropublications(()),
    )
    assert len(records) == 1
    assert records[0].warning_class is ConflictClass.CONFLICT
    assert type(claims[0].quantitative.point) is type(left)
    assert type(claims[1].quantitative.point) is type(right)
    assert records[0].value_a == str(left)
    assert records[0].value_b == str(right)


def test_missing_quarantined_and_stale_admission_are_typed_failures() -> None:
    valid, context = check_claims(
        (
            Claim(
                claim_id="a",
                claim_type=ClaimType.PARAMETER,
                output_concept="x",
                value=1,
            ),
        ),
        (concept_with_form("x", "x", "quantity"),),
    )
    (entry,) = valid.checked_claims
    with pytest.raises(ClaimAdmissionError) as missing:
        detect_conflicts(
            (entry.claim,),
            context.concepts_by_id,
            context.condition_registry,
            admissions=(),
            provenance=ClaimProvenanceIndex.from_micropublications(()),
        )
    assert missing.value.reason is ClaimAdmissionFailure.MISSING
    with pytest.raises(ClaimAdmissionError) as stale:
        detect_conflicts(
            (msgspec.structs.replace(entry.claim, value=99),),
            context.concepts_by_id,
            context.condition_registry,
            admissions=(entry.admission,),
            provenance=ClaimProvenanceIndex.from_micropublications(()),
        )
    assert stale.value.reason is ClaimAdmissionFailure.STALE
    invalid, _ = check_claims(
        (Claim(claim_id="bad", claim_type=ClaimType.OBSERVATION),),
        (concept_with_form("x", "x", "quantity"),),
    )
    (blocked,) = invalid.blocked_claims
    with pytest.raises(ClaimAdmissionError) as quarantined:
        detect_conflicts(
            (blocked.claim,),
            context.concepts_by_id,
            context.condition_registry,
            admissions=(blocked.admission,),
            provenance=ClaimProvenanceIndex.from_micropublications(()),
        )
    assert quarantined.value.reason is ClaimAdmissionFailure.QUARANTINED


def test_two_checked_versions_of_one_claim_identity_can_be_compared() -> None:
    first, context = check_claims(
        (
            Claim(
                claim_id="rival",
                claim_type=ClaimType.PARAMETER,
                output_concept="x",
                value=1,
            ),
        ),
        (concept_with_form("x", "x", "quantity"),),
    )
    second, _ = check_claims(
        (
            Claim(
                claim_id="rival",
                claim_type=ClaimType.PARAMETER,
                output_concept="x",
                value=2,
            ),
        ),
        (concept_with_form("x", "x", "quantity"),),
    )
    versions = (*first.checked_claims, *second.checked_claims)
    records = detect_conflicts(
        tuple(entry.claim for entry in versions),
        context.concepts_by_id,
        context.condition_registry,
        admissions=tuple(entry.admission for entry in versions),
        provenance=ClaimProvenanceIndex.from_micropublications(()),
    )
    assert len(records) == 1
    assert (records[0].value_a, records[0].value_b) == ("1", "2")


def test_lifting_does_not_replace_authored_checked_applicability() -> None:
    bundle, context = check_claims(
        (
            Claim(
                claim_id="a",
                claim_type=ClaimType.PARAMETER,
                output_concept="x",
                value=1,
                context_id="source",
                conditions=("x > 10",),
            ),
            Claim(
                claim_id="b",
                claim_type=ClaimType.PARAMETER,
                output_concept="x",
                value=2,
                context_id="target",
                conditions=("x < 5",),
            ),
        ),
        (concept_with_form("x", "x", "quantity"),),
        context_ids=("source", "target"),
    )
    assert bundle.blocked_claims == (), bundle.diagnostics
    claims = tuple(entry.claim for entry in bundle.checked_claims)
    before = tuple(msgspec.json.encode(claim) for claim in claims)
    lifting = LiftingSystem(
        contexts=(
            Context(context_id="source", name="source"),
            Context(context_id="target", name="target"),
        ),
        lifting_rules=(
            LiftingRule(
                rule_id="bridge", source_context="source", target_context="target"
            ),
        ),
    )
    records = detect_conflicts(
        claims,
        context.concepts_by_id,
        context.condition_registry,
        lifting,
        admissions=tuple(entry.admission for entry in bundle.checked_claims),
        provenance=ClaimProvenanceIndex.from_micropublications(()),
    )
    assert len(records) == 1
    assert records[0].warning_class is ConflictClass.PHI_NODE
    assert records[0].conditions_a == list(claims[0].checked_conditions.sources)
    assert records[0].conditions_b == list(claims[1].checked_conditions.sources)
    assert before == tuple(msgspec.json.encode(claim) for claim in claims)
