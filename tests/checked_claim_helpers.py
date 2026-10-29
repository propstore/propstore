"""Actual compiler pipelines for canonical detector test inputs."""

from collections.abc import Mapping, Sequence
from dataclasses import replace

from condition_ir import ConceptInfo, KindType

from propstore.compiler.context import CompilationContext, build_compilation_context
from propstore.compiler.ir import ClaimCheckedBundle
from propstore.dimensions import UnitConversion
from propstore.families.claims import Claim
from propstore.families.claims_passes import ClaimFiles, LoadedClaim, run_claim_pipeline
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


def quantity_form() -> FormDefinition:
    return FormDefinition(
        name="quantity",
        kind=KindType.QUANTITY,
        unit_symbol="1",
        is_dimensionless=True,
    )


def frequency_form() -> FormDefinition:
    return FormDefinition(
        name="frequency",
        kind=KindType.QUANTITY,
        unit_symbol="Hz",
        dimensions={"T": -1},
        allowed_units=("Hz", "kHz"),
        conversions={
            "kHz": UnitConversion(unit="kHz", type="multiplicative", multiplier=1000.0)
        },
    )


def check_claims(
    claims: Sequence[Claim],
    concepts: Sequence[Concept],
    *,
    forms: Sequence[FormDefinition] | None = None,
    condition_registry: Mapping[str, ConceptInfo] | None = None,
    context_ids: Sequence[str] = (),
) -> tuple[ClaimCheckedBundle, CompilationContext]:
    form_result = run_form_pipeline(
        [LoadedForm(form=form) for form in (forms or (quantity_form(),))]
    )
    assert isinstance(form_result.output, FormCheckedRegistry), form_result.diagnostics
    concept_result = run_concept_pipeline(
        [LoadedConcept(concept=item) for item in concepts],
        context=ConceptPipelineContext(form_registry=form_result.output.registry),
    )
    assert isinstance(concept_result.output, ConceptCheckedRegistry), (
        concept_result.diagnostics
    )
    context = build_compilation_context(
        concept_result.output,
        form_registry=form_result.output,
        claims=claims,
        context_ids=context_ids,
    )
    if condition_registry is not None:
        context = replace(
            context,
            condition_registry={**context.condition_registry, **condition_registry},
        )
    result = run_claim_pipeline(
        ClaimFiles(tuple(LoadedClaim(claim=item) for item in claims), context)
    )
    assert isinstance(result.output, ClaimCheckedBundle)
    return result.output, context
