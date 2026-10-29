"""Severity survives real CEL checking, claim admission, and activation."""

from pathlib import Path

import pytest
from condition_ir import ConceptInfo, KindType, check_condition_ir

from propstore.cel_validation import check_cel_condition
from propstore.claim_conditions import (
    check_claim_conditions,
    compile_checked_conditions,
)
from propstore.core.environment import Environment
from propstore.families.claims import Claim, ClaimType
from propstore.world import model
from propstore.world.types import RenderPolicy
from tests.atms_feed import ClaimSpec, build_bound
from tests.checked_claim_helpers import check_claims


def registry(extensible: bool = True) -> dict[str, ConceptInfo]:
    return {
        "task": ConceptInfo(
            id="task",
            canonical_name="task",
            kind=KindType.CATEGORY,
            category_values=["speech"],
            category_extensible=extensible,
        )
    }


@pytest.mark.parametrize(
    "extensible,value,accepted,warnings",
    [
        (True, "singing", True, 1),
        (False, "singing", False, 0),
        (True, "speech", True, 0),
        (False, "speech", True, 0),
    ],
)
def test_category_severity(
    extensible: bool, value: str, accepted: bool, warnings: int
) -> None:
    expression = f"task == '{value}'"
    result = check_cel_condition(expression, registry(extensible))
    assert (result.checked is not None) is accepted
    assert sum(item.is_warning for item in result.diagnostics) == warnings
    assert bool(result.errors) is not accepted
    if accepted:
        assert result.checked == check_condition_ir(expression, registry(extensible))


def test_mixed_claim_preserves_warning_error_and_index() -> None:
    conditions = ("task == 'singing'", "task > 2", "task ==")
    claim = Claim(claim_id="mixed", conditions=conditions)
    report = check_claim_conditions(claim, registry())
    assert len(report.checked.conditions) == 1
    assert report.diagnostics[0].diagnostic.is_warning
    assert report.diagnostics[0].index == 0
    assert {
        item.index for item in report.diagnostics if not item.diagnostic.is_warning
    } == {1, 2}
    bundle, _ = check_claims((claim,), (), condition_registry=registry())
    checked = bundle.claims[0]
    assert checked.blocked
    warning = next(item for item in checked.diagnostics if item.is_warning)
    assert warning.field == "conditions" and warning.index == 0
    assert warning.artifact_id == "mixed"
    assert warning.cel_diagnostic == report.diagnostics[0].diagnostic


def test_warning_only_claim_retains_checked_ir_and_is_admitted() -> None:
    claim = Claim(
        claim_id="warning",
        claim_type=ClaimType.OBSERVATION,
        statement="Singing occurs.",
        conditions=("task == 'singing'",),
    )
    bundle, _ = check_claims((claim,), (), condition_registry=registry())
    checked = bundle.claims[0]
    assert not checked.blocked
    assert len(checked.diagnostics) == 1 and checked.diagnostics[0].is_warning
    assert checked.claim.conditions_ir is not None
    assert compile_checked_conditions(checked.claim.conditions_ir).conditions[
        0
    ] == check_condition_ir(claim.conditions[0], registry())
    import json

    from propstore.build_diagnostics import pass_to_build_diagnostic

    row = pass_to_build_diagnostic(checked.diagnostics[0], diagnostic_id="warning")
    assert row.severity == "warning" and row.blocking == 0
    assert row.detail_json is not None
    detail = json.loads(row.detail_json)
    assert detail["expression"] == claim.conditions[0]
    assert detail["field"] == "conditions" and detail["index"] == 0
    assert detail["is_warning"] is True


def test_warning_condition_is_not_unconditional_at_activation() -> None:
    bound = build_bound(
        claims=(
            ClaimSpec(
                claim_id="eu", concept_id="A", value=2.0, conditions=("region == 'eu'",)
            ),
        )
    )
    active = model.active_graph(bound.store, Environment(bindings={"region": "us"}))
    assert "eu" in {str(item) for item in active.inactive_claim_ids}


def test_source_warning_promotes_and_build_preserves_diagnostic(tmp_path: Path) -> None:
    from propstore.families.forms import FormDefinition
    from propstore.families.sources import SourceConceptFormParametersDocument
    from propstore.source import finalize_source_branch, promote_source_branch
    from propstore.source.claims import (
        SourceCelValidationError,
        commit_source_claim_proposal,
    )
    from propstore.source.concepts import commit_source_concept_proposal
    from propstore.world import WorldQuery
    from tests.test_source_promote_p83b import _SOURCE, _new_source, _seed_context

    repo = _new_source(tmp_path)
    _seed_context(repo)
    repo.families.form.save(
        "category",
        FormDefinition(name="category", kind=KindType.CATEGORY),
        message="seed category",
    )
    commit_source_concept_proposal(
        repo,
        _SOURCE,
        local_name="task",
        definition="Task label.",
        form="category",
        form_parameters=SourceConceptFormParametersDocument(
            values=("speech",), extensible=True
        ),
    )
    with pytest.raises(SourceCelValidationError) as failure:
        commit_source_claim_proposal(
            repo,
            _SOURCE,
            claim_id="mixed",
            claim_type=ClaimType.OBSERVATION,
            context="ctx",
            statement="Invalid batch.",
            concepts=("task",),
            conditions=("task == 'singing'", "task > 2"),
        )
    checks = failure.value.checks
    assert checks[0].result.diagnostics[0].is_warning
    assert checks[1].result.errors and checks[1].index == 1
    stored = commit_source_claim_proposal(
        repo,
        _SOURCE,
        claim_id="singing",
        claim_type=ClaimType.OBSERVATION,
        context="ctx",
        statement="Singing occurs.",
        concepts=("task",),
        conditions=("task == 'singing'",),
    )
    finalize_source_branch(repo, _SOURCE)
    promote_source_branch(repo, _SOURCE)
    assert stored.artifact_id is not None
    with WorldQuery(repo) as world:
        claim = world.get_claim(stored.artifact_id)
        assert claim is not None and claim.conditions_ir is not None
        assert len(compile_checked_conditions(claim.conditions_ir).conditions) == 1
        policy = RenderPolicy(show_quarantined=True)
        warnings = [
            item
            for item in world.build_diagnostics(policy)
            if item.diagnostic_kind == "claim.condition"
        ]
        assert len(warnings) == 1
        assert warnings[0].severity == "warning" and warnings[0].blocking == 0
        assert warnings[0].detail_json is not None
        import json

        from propstore.world.reasoning_reports import (
            WorldConceptQueryRequest,
            query_world_concept,
        )

        report = query_world_concept(
            world, WorldConceptQueryRequest(target="task", policy=policy)
        )
        diagnostic = next(
            item
            for item in report.diagnostics
            if item.diagnostic_kind == "claim.condition"
        )
        assert diagnostic.severity == "warning" and diagnostic.detail_json is not None
        detail = json.loads(diagnostic.detail_json)
        assert detail["expression"] == "task == 'singing'"
        assert detail["field"] == "conditions" and detail["index"] == 0
        encoded = json.dumps(report.to_json())
        assert '"severity": "warning"' in encoded
        assert "singing" in encoded
