"""Assemble a grounded bundle from the authored grounding substrate.

:func:`build_grounded_bundle` takes the authored predicates, rules, superiorities,
and the concept/claim fact substrate (gathered into a small :class:`GroundingRepo`)
and produces a :class:`GroundedRulesBundle`. The surface validity check is the
only place grounding refuses to proceed: ``rules/`` without ``predicates/`` is an
invalid surface; both absent is an empty (valid) bundle.

Repository builds and world queries reconstruct through
:func:`load_grounded_bundle_from_sidecar` over one typed derived session, including
the grounding configuration stored in that committed artifact.
"""

from __future__ import annotations

from dataclasses import dataclass

from quire.sqlalchemy_store import DerivedSession
from sqlalchemy import select

from propstore.families.claims import Claim
from propstore.families.concepts import Concept
from propstore.families.grounding import GroundingBuildConfiguration
from propstore.families.predicates import Predicate
from propstore.families.rules import DefeasibleRule, RuleSuperiority
from propstore.grounding.bundle import GroundedRulesBundle
from propstore.grounding.facts import (
    ConceptRelations,
    GroundingFactInputs,
    extract_facts,
)
from propstore.grounding.grounder import ground
from propstore.grounding.predicates import PredicateRegistry


@dataclass(frozen=True)
class GroundingRepo:
    """The authored grounding substrate gathered for one grounding run."""

    predicates: tuple[Predicate, ...] = ()
    rules: tuple[DefeasibleRule, ...] = ()
    rule_superiority: tuple[RuleSuperiority, ...] = ()
    concepts: tuple[ConceptRelations, ...] = ()
    claims: tuple[Claim, ...] = ()


def build_grounded_bundle(
    repo: GroundingRepo,
    *,
    commit: str | None = None,
    return_arguments: bool = False,
    max_arguments: int | None = None,
) -> GroundedRulesBundle:
    """Ground the authored substrate into a bundle.

    ``rules/`` present with no ``predicates/`` is rejected; both absent yields an
    empty bundle (all four sections present and empty). ``commit`` is accepted for
    call-site symmetry with commit-pinned loaders.
    """

    _ = commit
    if not repo.predicates:
        if repo.rules:
            raise ValueError(
                "knowledge root has rules/ but no predicates/; "
                "grounding requires declared predicates"
            )
        return GroundedRulesBundle.empty(max_arguments=max_arguments)
    registry = PredicateRegistry.from_documents(repo.predicates)
    facts = extract_facts(
        GroundingFactInputs(concepts=repo.concepts, claims=repo.claims), registry
    )
    return ground(
        repo.rules,
        facts,
        registry,
        superiority=repo.rule_superiority,
        return_arguments=return_arguments,
        max_arguments=max_arguments,
    )


def load_grounded_bundle_from_sidecar(
    session: DerivedSession,
) -> GroundedRulesBundle:
    """Reconstruct the canonical grounded bundle from one typed sidecar session."""

    predicate_model = session.schema.model("predicate")
    predicates = tuple(
        Predicate.__charter__.document_from_model(row, Predicate)
        for row in session.scalars(select(predicate_model))
    )

    rule_model = session.schema.model("defeasible_rule")
    rules = tuple(
        DefeasibleRule.__charter__.document_from_model(row, DefeasibleRule)
        for row in session.scalars(select(rule_model))
    )

    superiority_model = session.schema.model("rule_superiority")
    rule_superiority = tuple(
        RuleSuperiority.__charter__.document_from_model(row, RuleSuperiority)
        for row in session.scalars(select(superiority_model))
    )

    claim_model = session.schema.model("claim")
    claims = tuple(
        Claim.__charter__.document_from_model(row, Claim)
        for row in session.scalars(select(claim_model))
    )

    concept_model = session.schema.model("concept")
    concept_documents = tuple(
        Concept.__charter__.document_from_model(row, Concept)
        for row in session.scalars(select(concept_model))
    )
    concepts = tuple(
        ConceptRelations(
            concept_id=concept.concept_id,
            canonical_name=concept.canonical_name,
        )
        for concept in concept_documents
    )

    config_model = session.schema.model("grounding_build_configuration")
    config_rows = tuple(session.scalars(select(config_model)))
    if len(config_rows) != 1:
        raise ValueError(
            "world sidecar must contain exactly one grounding_build_configuration row"
        )
    config = GroundingBuildConfiguration.__charter__.document_from_model(
        config_rows[0], GroundingBuildConfiguration
    )

    return build_grounded_bundle(
        GroundingRepo(
            predicates=predicates,
            rules=rules,
            rule_superiority=rule_superiority,
            concepts=concepts,
            claims=claims,
        ),
        return_arguments=True,
        max_arguments=config.max_arguments,
    )
