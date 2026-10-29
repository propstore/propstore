"""The canonical compilation context (PLAN-mandated coverage).

CompilationContext bundles the symbol tables the semantic passes resolve
against. These tests pin checked-concept consumption, explicit empty inputs, and
the claim index.
"""

from __future__ import annotations

from condition_ir import KindType

from propstore.compiler.context import (
    build_compilation_context,
    build_compiler_claim_index,
)
from propstore.core.lemon import (
    LexicalEntry,
    LexicalForm,
    LexicalSense,
    OntologyReference,
)
from propstore.families.claims import Claim
from propstore.families.concepts import Concept
from propstore.families.concepts_passes import (
    ConceptCheckedRegistry,
    ConceptPipelineContext,
    LoadedConcept,
    run_concept_pipeline,
)
from propstore.families.forms import FormDefinition
from propstore.families.forms_passes import (
    FormCheckedRegistry,
    LoadedForm,
    run_form_pipeline,
)


def test_claim_index_keyed_by_claim_id() -> None:
    claims = [Claim(claim_id="a"), Claim(claim_id="b")]
    index = build_compiler_claim_index(claims)
    assert set(index) == {"a", "b"}
    assert index["a"].claim_id == "a"


def test_context_from_checked_concepts_populates_tables() -> None:
    forms = {
        "mass": FormDefinition(
            name="mass", kind=KindType.QUANTITY, dimensions={"mass": 1}
        )
    }
    concepts = [
        LoadedConcept(
            concept=Concept(
                concept_id="ps:concept:frequency",
                canonical_name="frequency",
                lexical_entry=LexicalEntry(
                    identifier="entry:frequency",
                    canonical_form=LexicalForm(
                        written_rep="Fundamental frequency", language="en"
                    ),
                    senses=(
                        LexicalSense(
                            reference=OntologyReference(uri="ps:concept:frequency")
                        ),
                    ),
                    physical_dimension_form="mass",
                ),
            )
        )
    ]
    concept_result = run_concept_pipeline(
        concepts, context=ConceptPipelineContext(form_registry=forms)
    )
    assert isinstance(concept_result.output, ConceptCheckedRegistry)
    claims = [Claim(claim_id="c1")]
    form_result = run_form_pipeline([LoadedForm(form=form) for form in forms.values()])
    assert isinstance(form_result.output, FormCheckedRegistry)
    context = build_compilation_context(
        concept_result.output,
        form_registry=form_result.output,
        claims=claims,
        context_ids={"ctx1"},
    )
    assert "ps:concept:frequency" in context.concepts_by_id
    assert context.condition_registry["frequency"].id == "ps:concept:frequency"
    assert "c1" in context.claim_index
    assert context.context_ids == frozenset({"ctx1"})
    assert "mass" in context.form_registry.registry
    assert context.form_registry is form_result.output


def test_context_from_empty_checked_inputs_is_empty() -> None:
    result = run_concept_pipeline([])
    assert isinstance(result.output, ConceptCheckedRegistry)
    context = build_compilation_context(result.output)
    assert context.concepts_by_id == {}
    assert context.claim_index == {}
    assert context.condition_registry == {}
    assert context.context_ids == frozenset()
    assert context.form_registry.registry == {}
