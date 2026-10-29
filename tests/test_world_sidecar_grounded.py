"""Canonical grounding reconstruction from the charter-derived world sidecar."""

from __future__ import annotations

from pathlib import Path

import gunray
from quire.sqlalchemy_store import readonly_session
from sqlalchemy import select

from propstore.compiler.workflows import build_repository
from propstore.derived_schema import build_world_sidecar_schema
from propstore.families.claims import Claim, ClaimType
from propstore.families.concepts import Concept
from propstore.families.contexts import Context
from propstore.families.predicates import Predicate
from propstore.families.rules import (
    Atom,
    BodyLiteral,
    DefeasibleRule,
    RuleSuperiority,
    Term,
)
from propstore.grounding.bundle import GroundedRulesBundle, GroundingStatus
from propstore.grounding.loading import load_grounded_bundle_from_sidecar
from propstore.repository import Repository
from tests.canonical_claim_fixtures import save_dimensionless_concepts


def _load_sidecar_bundle(path: str) -> GroundedRulesBundle:
    schema = build_world_sidecar_schema()
    with readonly_session(Path(path), schema) as session:
        return load_grounded_bundle_from_sidecar(session)


def _seed_grounding_repo(path: Path) -> Repository:
    repo = Repository.init(path)
    save_dimensionless_concepts(repo, (("c1", "Speed"),))
    repo.families.context.save(
        "ctx1", Context(context_id="ctx1", name="ctx"), message="m"
    )
    repo.families.claim.save(
        "cl1",
        Claim(
            claim_id="cl1",
            context_id="ctx1",
            claim_type=ClaimType.PARAMETER,
            output_concept="c1",
            value=1.0,
        ),
        message="m",
    )
    repo.families.predicate.save(
        "has_value",
        Predicate(
            predicate_id="has_value",
            arity=1,
            arg_types=("Claim",),
            derived_from="claim.attribute:value",
        ),
        message="m",
    )
    repo.families.predicate.save(
        "important",
        Predicate(predicate_id="important", arity=1, arg_types=("Claim",)),
        message="m",
    )
    repo.families.defeasible_rule.save(
        "r1",
        DefeasibleRule(
            rule_id="r1",
            kind="defeasible",
            head=Atom(predicate="important", terms=(Term(kind="var", name="X"),)),
            body=(
                BodyLiteral(
                    kind="positive",
                    atom=Atom(
                        predicate="has_value", terms=(Term(kind="var", name="X"),)
                    ),
                ),
            ),
        ),
        message="m",
    )
    repo.require_git().commit_files(
        {"propstore.yaml": b"grounding_max_arguments: 100\n"},
        "Set grounding budget",
    )
    return repo


def test_empty_grounding_sidecar_reconstructs_complete_bundle(tmp_path: Path) -> None:
    repo = Repository.init(tmp_path / "kn")
    repo.families.concept.save(
        "c1", Concept(concept_id="c1", canonical_name="Speed"), message="m"
    )

    report = build_repository(repo)

    assert report.derived_store is not None
    bundle = _load_sidecar_bundle(report.derived_store.path)
    assert report.grounding_bundle == bundle
    assert bundle.status is GroundingStatus.COMPLETE
    assert bundle.max_arguments is None
    assert bundle.source_facts == ()
    assert bundle.arguments == ()


def test_sidecar_session_reconstructs_exact_committed_build(
    tmp_path: Path,
) -> None:
    repo = _seed_grounding_repo(tmp_path / "kn")
    opposing_rule = DefeasibleRule(
        rule_id="r2",
        kind="defeasible",
        head=Atom(
            predicate="important", terms=(Term(kind="var", name="X"),), negated=True
        ),
        body=(
            BodyLiteral(
                kind="positive",
                atom=Atom(predicate="has_value", terms=(Term(kind="var", name="X"),)),
            ),
        ),
    )
    superiority = RuleSuperiority(
        superiority_id="s1", superior_rule_id="r1", inferior_rule_id="r2"
    )
    repo.families.defeasible_rule.save("r2", opposing_rule, message="m")
    repo.families.rule_superiority.save("s1", superiority, message="m")
    source_commit = str(repo.require_git().head_sha())
    report = build_repository(repo)

    assert report.derived_store is not None
    assert report.derived_store.source_commit == source_commit
    # Change HEAD after building: reconstruction must use the committed artifact,
    # including its configuration, rather than re-reading the repository.
    repo.require_git().commit_files(
        {"propstore.yaml": b"grounding_max_arguments: 1\n"}, "Change current budget"
    )
    with readonly_session(
        Path(report.derived_store.path), build_world_sidecar_schema()
    ) as session:
        predicates = tuple(
            Predicate.__charter__.document_from_model(row, Predicate)
            for row in session.scalars(
                select(session.schema.model("predicate")).order_by(
                    session.schema.model("predicate").predicate_id
                )
            )
        )
        assert predicates == (
            Predicate(
                predicate_id="has_value",
                arity=1,
                arg_types=("Claim",),
                derived_from="claim.attribute:value",
            ),
            Predicate(predicate_id="important", arity=1, arg_types=("Claim",)),
        )
        sidecar_bundle = load_grounded_bundle_from_sidecar(session)
    assert report.grounding_bundle == sidecar_bundle
    assert sidecar_bundle.source_rules == (
        DefeasibleRule(
            rule_id="r1",
            kind="defeasible",
            head=Atom(predicate="important", terms=(Term(kind="var", name="X"),)),
            body=opposing_rule.body,
        ),
        opposing_rule,
    )
    assert sidecar_bundle.source_superiority == (superiority,)
    assert sidecar_bundle.source_facts == (
        gunray.GroundAtom(predicate="has_value", arguments=("cl1",)),
    )
    assert sidecar_bundle.status is GroundingStatus.COMPLETE
    assert sidecar_bundle.max_arguments == 100
    assert sidecar_bundle.budget_reason is None
    assert sidecar_bundle.partial_candidate_count is None
    assert sidecar_bundle.sections["yes"]["has_value"] == frozenset({("cl1",)})
    assert sidecar_bundle.sections["yes"]["important"] == frozenset({("cl1",)})
    assert sidecar_bundle.grounding_inspection is not None
    assert tuple(
        (argument.conclusion, tuple(rule.rule_id for rule in argument.rules))
        for argument in sidecar_bundle.arguments
    ) == (
        (gunray.GroundAtom(predicate="has_value", arguments=("cl1",)), ()),
        (gunray.GroundAtom(predicate="important", arguments=("cl1",)), ("r1",)),
        (
            gunray.GroundAtom(predicate="~important", arguments=("cl1",)),
            ("r2",),
        ),
    )
