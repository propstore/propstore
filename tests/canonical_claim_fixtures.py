"""Canonical form evidence for tests that require admitted quantitative claims."""

from collections.abc import Iterable

from condition_ir import KindType

from propstore.core.lemon import (
    LexicalEntry,
    LexicalForm,
    LexicalSense,
    OntologyReference,
)
from propstore.families.concepts import Concept
from propstore.families.forms import FormDefinition
from propstore.repository import Repository


def concept_with_form(concept_id: str, canonical_name: str, form: str) -> Concept:
    return Concept(
        concept_id=concept_id,
        canonical_name=canonical_name,
        lexical_entry=LexicalEntry(
            identifier=concept_id,
            canonical_form=LexicalForm(written_rep=canonical_name, language="en"),
            senses=(
                LexicalSense(reference=OntologyReference(uri=f"urn:test:{concept_id}")),
            ),
            physical_dimension_form=form,
        ),
    )


def save_dimensionless_concepts(
    repo: Repository, concepts: Iterable[tuple[str, str]]
) -> None:
    repo.families.form.save(
        "dimensionless",
        FormDefinition(
            name="dimensionless",
            kind=KindType.QUANTITY,
            is_dimensionless=True,
            dimensions={},
        ),
        message="Declare dimensionless test quantities",
    )
    for concept_id, name in concepts:
        repo.families.concept.save(
            concept_id,
            concept_with_form(concept_id, name, "dimensionless"),
            message="Declare quantitative test concept",
        )
