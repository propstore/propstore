"""Canonical algorithm grounding rejects ambiguous or incomplete claims."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from propstore.algorithm_bindings import (
    AlgorithmBindingError,
    algorithm_bindings,
    algorithm_known_values,
)
from propstore.app.claims import ClaimCompareRequest, compare_algorithm_claims
from propstore.cli import cli
from propstore.conflict_detector.algorithms import detect_algorithm_conflicts
from propstore.core.active_claims import ActiveClaim
from propstore.families.claim_provenance import ClaimProvenanceIndex
from propstore.families.claims import Claim, ClaimType, ClaimVariable
from propstore.families.concepts import Concept
from propstore.repository import Repository
from propstore.world import WorldQuery
from propstore.world.types import ValueStatus
from tests.canonical_claim_fixtures import concept_with_form
from tests.checked_claim_helpers import check_claims

BODY = "def f(x, y):\n    return x - y\n"
VARIABLES = (
    ClaimVariable(concept="A", symbol="x"),
    ClaimVariable(concept="B", symbol="y"),
)


@pytest.mark.parametrize(
    "variables",
    [
        (),
        (ClaimVariable(concept="", symbol="x"),),
        (ClaimVariable(concept="A"),),
        (*VARIABLES, ClaimVariable(concept="A", symbol="x")),
        (*VARIABLES, ClaimVariable(concept="C", symbol="x")),
        (
            ClaimVariable(concept="A", name="x", symbol="a"),
            ClaimVariable(concept="B", name="x", symbol="b"),
        ),
    ],
)
def test_invalid_bindings(variables: tuple[ClaimVariable, ...]) -> None:
    with pytest.raises(AlgorithmBindingError):
        algorithm_bindings(variables, BODY)


def test_known_values_use_concepts() -> None:
    bindings = algorithm_bindings(VARIABLES, BODY)
    assert algorithm_known_values({"A": 3.0}, bindings) == {"A": 3.0}
    with pytest.raises(AlgorithmBindingError):
        algorithm_known_values({"x": 3.0}, bindings)


def test_detector_rejects_incomplete_bindings() -> None:
    claims = [
        Claim(
            claim_id=claim_id,
            claim_type=ClaimType.ALGORITHM,
            output_concept="out",
            body=BODY,
        )
        for claim_id in ("a", "b")
    ]
    bundle, context = check_claims(
        claims,
        tuple(concept_with_form(name, name, "quantity") for name in ("A", "B", "out")),
    )
    assert bundle.blocked_claims == (), bundle.diagnostics
    with pytest.raises(AlgorithmBindingError, match="Missing algorithm bindings"):
        detect_algorithm_conflicts(
            tuple(entry.claim for entry in bundle.checked_claims),
            context.condition_registry,
            admissions=tuple(entry.admission for entry in bundle.checked_claims),
            provenance=ClaimProvenanceIndex.from_micropublications(()),
        )


def test_production_consumers_agree(tmp_path: Path) -> None:
    repo = Repository.init(tmp_path / "repo")
    for concept in ("A", "B", "out"):
        repo.families.concept.save(
            concept,
            Concept(concept_id=concept, canonical_name=concept),
            message="fixture",
        )
    a = Claim(
        claim_id="a",
        claim_type=ClaimType.ALGORITHM,
        output_concept="out",
        body=BODY,
        variables=VARIABLES,
    )
    b = Claim(
        claim_id="b",
        claim_type=ClaimType.ALGORITHM,
        output_concept="out",
        body=BODY,
        variables=tuple(
            reversed(
                (
                    ClaimVariable(concept="A", symbol="y"),
                    ClaimVariable(concept="B", symbol="x"),
                )
            )
        ),
    )
    c = Claim(
        claim_id="c",
        claim_type=ClaimType.ALGORITHM,
        output_concept="out",
        body="def f(p, q):\n    return p - q\n",
        variables=(
            ClaimVariable(concept="A", name="p"),
            ClaimVariable(concept="B", name="q"),
        ),
    )
    for claim in (a, b, c):
        repo.families.claim.save(claim.claim_id, claim, message="fixture")
    with WorldQuery(repo) as world:
        assert not compare_algorithm_claims(
            world, ClaimCompareRequest("a", "b")
        ).equivalent
        assert compare_algorithm_claims(world, ClaimCompareRequest("a", "c")).equivalent
        bound = world.bind()
        checked = world.claims_by_ids({"a", "b", "c"})
        assert bound.extract_bindings(
            ActiveClaim.from_claim(checked["a"])
        ) == algorithm_bindings(VARIABLES, BODY)
        assert bound.value_of("out").status is ValueStatus.CONFLICTED
        assert (
            len(
                detect_algorithm_conflicts(
                    [checked["a"], checked["b"]],
                    world.condition_solver().registry,
                    admissions=tuple(world.claim_admissions().values()),
                    provenance=world.claim_provenance(),
                )
            )
            == 1
        )
        assert not detect_algorithm_conflicts(
            [checked["a"], checked["c"]],
            world.condition_solver().registry,
            admissions=tuple(world.claim_admissions().values()),
            provenance=world.claim_provenance(),
        )
    result = CliRunner().invoke(
        cli, ["-C", str(repo.root), "claim", "compare", "a", "b", "--format", "json"]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["equivalent"] is False
