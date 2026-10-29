"""Canonical algorithm grounding rejects ambiguous or incomplete claims."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from propstore.algorithm_bindings import (
    AlgorithmBindingError, algorithm_bindings, algorithm_known_values,
)
from propstore.app.claims import ClaimCompareRequest, compare_algorithm_claims
from propstore.cli import cli
from propstore.conflict_detector.algorithms import detect_algorithm_conflicts
from propstore.conflict_detector.models import ConflictClaim
from propstore.core.active_claims import ActiveClaim
from propstore.families.claims import Claim, ClaimType, ClaimVariable
from propstore.families.concepts import Concept
from propstore.repository import Repository
from propstore.world import WorldQuery
from propstore.world.types import ValueStatus

BODY = "def f(x, y):\n    return x - y\n"
VARIABLES = (ClaimVariable(concept="A", symbol="x"), ClaimVariable(concept="B", symbol="y"))


@pytest.mark.parametrize("variables", [
    (),
    (ClaimVariable(concept="", symbol="x"),),
    (ClaimVariable(concept="A"),),
    (*VARIABLES, ClaimVariable(concept="A", symbol="x")),
    (*VARIABLES, ClaimVariable(concept="C", symbol="x")),
    (ClaimVariable(concept="A", name="x", symbol="a"), ClaimVariable(concept="B", name="x", symbol="b")),
])
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
        ConflictClaim(
            claim_id=claim_id, claim_type=ClaimType.ALGORITHM,
            output_concept_id="out", body=BODY,
        )
        for claim_id in ("a", "b")
    ]
    with pytest.raises(AlgorithmBindingError, match="Missing algorithm bindings"):
        detect_algorithm_conflicts(claims, {})


def test_production_consumers_agree(tmp_path: Path) -> None:
    repo = Repository.init(tmp_path / "repo")
    for concept in ("A", "B", "out"):
        repo.families.concept.save(concept, Concept(concept_id=concept, canonical_name=concept), message="fixture")
    a = Claim(claim_id="a", claim_type=ClaimType.ALGORITHM, output_concept="out", body=BODY, variables=VARIABLES)
    b = Claim(claim_id="b", claim_type=ClaimType.ALGORITHM, output_concept="out", body=BODY, variables=tuple(reversed((ClaimVariable(concept="A", symbol="y"), ClaimVariable(concept="B", symbol="x")))))
    c = Claim(claim_id="c", claim_type=ClaimType.ALGORITHM, output_concept="out", body="def f(p, q):\n    return p - q\n", variables=(ClaimVariable(concept="A", name="p"), ClaimVariable(concept="B", name="q")))
    for claim in (a, b, c):
        repo.families.claim.save(claim.claim_id, claim, message="fixture")
    with WorldQuery(repo) as world:
        assert not compare_algorithm_claims(world, ClaimCompareRequest("a", "b")).equivalent
        assert compare_algorithm_claims(world, ClaimCompareRequest("a", "c")).equivalent
        bound = world.bind()
        assert bound.extract_bindings(ActiveClaim.from_claim(a)) == algorithm_bindings(VARIABLES, BODY)
        assert bound.value_of("out").status is ValueStatus.CONFLICTED
    result = CliRunner().invoke(cli, ["-C", str(repo.root), "claim", "compare", "a", "b", "--format", "json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["equivalent"] is False
    assert len(detect_algorithm_conflicts([ConflictClaim.from_claim(a), ConflictClaim.from_claim(b)], {})) == 1
    assert not detect_algorithm_conflicts([ConflictClaim.from_claim(a), ConflictClaim.from_claim(c)], {})
