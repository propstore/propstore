"""Plain claim-set helpers for Phase 6c merge-math tests.

The merge math takes plain per-branch claim sets, so these build
:class:`~propstore.merge.MergeClaim` values directly over the one canonical
:class:`~propstore.families.claims.Claim` — no git store, no ``Repository`` snapshot
(those land in Phase 9). Provenance (paper/page) is carried alongside the claim
because the rewrite charter is provenance-free.
"""

from __future__ import annotations

from collections.abc import Sequence

from condition_ir import KindType

from propstore.families.claim_provenance import UnbundledClaim
from propstore.families.claims import Claim, ClaimType
from propstore.families.concepts import Concept
from propstore.families.forms import FormDefinition
from propstore.merge import MergeClaim
from tests.canonical_claim_fixtures import concept_with_form
from tests.checked_claim_helpers import check_claims


def temperature_form() -> FormDefinition:
    return FormDefinition(
        name="temperature",
        kind=KindType.QUANTITY,
        unit_symbol="K",
        allowed_units=("K",),
        dimensions={"Theta": 1},
    )


def _checked_merge_claim(
    claim: Claim,
    concepts: Sequence[Concept],
    *,
    paper: str,
    page: int,
    forms: Sequence[FormDefinition] | None = None,
) -> MergeClaim:
    bundle, context = check_claims((claim,), concepts, forms=forms)
    assert not bundle.blocked_claims, bundle.diagnostics
    (entry,) = bundle.checked_claims
    merge_claim = MergeClaim.from_claim(
        entry.claim,
        admission=entry.admission,
        condition_registry=context.condition_registry,
        provenance=UnbundledClaim(claim.claim_id),
        paper=paper,
        page=page,
    )
    assert merge_claim is not None
    return merge_claim


def obs_claim(
    cid: str,
    statement: str,
    concepts: list[str],
    *,
    paper: str = "test_paper",
    page: int = 1,
    conditions: list[str] | None = None,
) -> MergeClaim:
    claim = Claim(
        claim_id=cid,
        claim_type=ClaimType.OBSERVATION,
        statement=statement,
        concepts=tuple(concepts),
        conditions=tuple(conditions or ()),
    )
    return _checked_merge_claim(
        claim,
        tuple(concept_with_form(name, name, "quantity") for name in concepts),
        paper=paper,
        page=page,
    )


def param_claim(
    cid: str,
    concept: str,
    value: float,
    *,
    paper: str = "test_paper",
    page: int = 1,
    conditions: list[str] | None = None,
    condition_concepts: tuple[str, ...] = (),
) -> MergeClaim:
    claim = Claim(
        claim_id=cid,
        claim_type=ClaimType.PARAMETER,
        output_concept=concept,
        value=value,
        unit="K",
        conditions=tuple(conditions or ()),
    )
    return _checked_merge_claim(
        claim,
        tuple(
            concept_with_form(name, name, "temperature")
            for name in dict.fromkeys((concept, *condition_concepts))
        ),
        forms=(temperature_form(),),
        paper=paper,
        page=page,
    )
