"""Invalid category-to-quantity equations remain quarantined before ATMS."""

from __future__ import annotations

from pathlib import Path

from condition_ir import KindType

from propstore.core.environment import Environment
from propstore.families.claims import Claim, ClaimType, ClaimVariable
from propstore.families.contexts import Context
from propstore.families.forms import FormDefinition
from propstore.repository import Repository
from propstore.world import RenderPolicy, WorldQuery
from tests.canonical_claim_fixtures import (
    concept_with_form,
    save_dimensionless_concepts,
)


def test_categorical_provider_cannot_admit_a_numeric_equation(
    tmp_path: Path,
) -> None:
    repo = Repository.init(tmp_path / "knowledge")
    repo.families.form.save(
        "category",
        FormDefinition(name="category", kind=KindType.CATEGORY),
        message="Declare category",
    )
    repo.families.concept.save(
        "category_input",
        concept_with_form("category_input", "category_input", "category"),
        message="add categorical input",
    )
    save_dimensionless_concepts(repo, (("numeric_output", "numeric_output"),))
    repo.families.context.save(
        "ctx",
        Context(context_id="ctx", name="test context"),
        message="add context",
    )
    repo.families.claim.save(
        "categorical_provider",
        Claim(
            claim_id="categorical_provider",
            context_id="ctx",
            claim_type=ClaimType.PARAMETER,
            output_concept="category_input",
            value="red",
        ),
        message="add categorical provider",
    )
    repo.families.claim.save(
        "numeric_equation",
        Claim(
            claim_id="numeric_equation",
            context_id="ctx",
            claim_type=ClaimType.EQUATION,
            output_concept="numeric_output",
            concepts=("category_input",),
            expression="category_input",
            sympy="category_input",
            variables=(
                ClaimVariable(concept="category_input", symbol="category_input"),
            ),
        ),
        message="add numeric equation",
    )

    with WorldQuery(repo) as world:
        assert {claim.claim_id for claim in world.claims_for(None)} == {
            "categorical_provider"
        }
        assert world.all_parameterizations() == ()
        (artifact,) = world.quarantined_claims(RenderPolicy(show_quarantined=True))
        assert artifact.claim.claim_id == "numeric_equation"
        assert any(
            d.diagnostic_kind == "claim.dimension.kind.invalid"
            for d in artifact.diagnostics
        )
        engine = world.bind(Environment()).atms_engine()
        assert engine.claim_label("numeric_equation") is None
