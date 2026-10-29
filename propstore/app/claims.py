"""Application-layer claim list / search summary rows.

The summary surface renders many claims as compact :class:`ClaimSummaryEntry`
rows for index and search pages, reusing the per-field helpers in
:mod:`propstore.app.claim_views`. Both builders take an already-open
:class:`~propstore.world.WorldQuery` and a :class:`~propstore.world.RenderPolicy`;
only claims visible under the policy are listed (render-time filtering — hidden
rows are present in storage, not dropped).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from propstore.algorithm_bindings import algorithm_bindings, algorithm_known_values
from propstore.app.claim_views import (
    claim_condition_expression,
    claim_focus_concept,
    claim_focus_concept_id,
    claim_type_text,
)
from propstore.app.view_state import ViewState
from propstore.families.claims import Claim, ClaimType
from propstore.families.concepts import Concept
from propstore.reporting import JsonReportMixin
from propstore.world import RenderPolicy, WorldQuery

_SUMMARY_TEXT_LIMIT = 120


class ClaimWorkflowError(Exception):
    """Base class for expected claim owner-layer failures."""


class UnknownClaimError(ClaimWorkflowError):
    """Raised when a claim reference does not resolve to a stored claim."""

    def __init__(self, claim_id: str) -> None:
        super().__init__(f"Unknown claim: {claim_id}")
        self.claim_id = claim_id


class ClaimComparisonError(ClaimWorkflowError):
    """Raised when two claims cannot be compared as algorithm bodies."""


@dataclass(frozen=True)
class ClaimCompareRequest:
    """A request to compare two algorithm claims' bodies for equivalence."""

    claim_a_id: str
    claim_b_id: str
    known_values: Mapping[str, float] | None = None


@dataclass(frozen=True)
class ClaimCompareReport(JsonReportMixin):
    """The AST-equivalence verdict between two algorithm claim bodies."""

    tier: str
    equivalent: bool
    similarity: float
    details: str


def compare_algorithm_claims(
    world: WorldQuery,
    request: ClaimCompareRequest,
) -> ClaimCompareReport:
    """Compare two algorithm claims' bodies via AST equivalence (``ast_equiv``).

    Claims must have canonical ALGORITHM type, bodies, and complete canonical
    bindings. Known values are keyed by canonical concept identity.
    """

    from ast_equiv import AlgorithmParseError

    from propstore.conflict_detector.algorithms import ast_compare

    claim_a = world.get_claim(request.claim_a_id)
    if claim_a is None:
        raise UnknownClaimError(request.claim_a_id)
    claim_b = world.get_claim(request.claim_b_id)
    if claim_b is None:
        raise UnknownClaimError(request.claim_b_id)

    body_a = claim_a.body
    body_b = claim_b.body
    if (
        claim_a.claim_type is not ClaimType.ALGORITHM
        or claim_b.claim_type is not ClaimType.ALGORITHM
        or not body_a
        or not body_b
    ):
        raise ClaimComparisonError("Both claims must be algorithm claims with a body.")

    try:
        bindings_a = algorithm_bindings(claim_a.variables, body_a)
        bindings_b = algorithm_bindings(claim_b.variables, body_b)
        known_values = algorithm_known_values(
            request.known_values, bindings_a, bindings_b
        )
        result = ast_compare(
            body_a, bindings_a, body_b, bindings_b, known_values=known_values
        )
    except RecursionError as exc:
        raise ClaimComparisonError(
            "Algorithm comparison exceeded recursion depth."
        ) from exc
    except AlgorithmParseError as exc:
        raise ClaimComparisonError(
            f"Claim body is not a parseable algorithm: {exc}"
        ) from exc
    except ValueError as exc:
        raise ClaimComparisonError(str(exc)) from exc

    return ClaimCompareReport(
        tier=result.tier.name,
        equivalent=bool(result.equivalent),
        similarity=float(result.similarity),
        details=str(result.details),
    )


@dataclass(frozen=True)
class ClaimSummaryEntry:
    claim_id: str
    concept_id: str | None
    concept_name: str | None
    concept_display: str
    claim_type: str
    value_display: str
    condition_display: str
    status_state: ViewState
    status_reason: str


@dataclass(frozen=True)
class ClaimSummaryReport(JsonReportMixin):
    entries: tuple[ClaimSummaryEntry, ...]


def list_claim_views(
    world: WorldQuery,
    *,
    policy: RenderPolicy,
    concept: str | None = None,
    limit: int = 50,
) -> ClaimSummaryReport:
    """Summary rows for every policy-visible claim, optionally scoped to a concept."""

    concept_filter = _resolve_concept_filter(world, concept)
    claims = sorted(
        world.claims_with_policy(concept_filter, policy), key=_claim_sort_key
    )
    entries = tuple(_summary_entry(world, claim) for claim in claims[:limit])
    return ClaimSummaryReport(entries=entries)


def search_claim_views(
    world: WorldQuery,
    query: str,
    *,
    policy: RenderPolicy,
    concept: str | None = None,
    limit: int = 20,
) -> ClaimSummaryReport:
    """Summary rows for policy-visible claims whose text matches ``query``."""

    needle = query.casefold()
    concept_filter = _resolve_concept_filter(world, concept)
    matches: list[ClaimSummaryEntry] = []
    for claim in sorted(
        world.claims_with_policy(concept_filter, policy), key=_claim_sort_key
    ):
        focus = claim_focus_concept(world, claim)
        if not _matches_query(claim, focus, needle):
            continue
        matches.append(_summary_entry(world, claim, focus=focus))
        if len(matches) >= limit:
            break
    return ClaimSummaryReport(entries=tuple(matches))


def _summary_entry(
    world: WorldQuery, claim: Claim, *, focus: Concept | None = None
) -> ClaimSummaryEntry:
    concept = focus if focus is not None else claim_focus_concept(world, claim)
    concept_id = claim_focus_concept_id(claim)
    canonical_name = None if concept is None else concept.canonical_name
    return ClaimSummaryEntry(
        claim_id=str(claim.claim_id),
        concept_id=concept_id,
        concept_name=canonical_name,
        concept_display=_concept_display(world, claim, concept),
        claim_type=claim_type_text(claim),
        value_display=_value_display(claim),
        condition_display=claim_condition_expression(claim) or "(vacuous)",
        status_state=ViewState.KNOWN,
        status_reason="Claim is visible under the current render policy.",
    )


def _concept_display(world: WorldQuery, claim: Claim, concept: Concept | None) -> str:
    if concept is not None:
        return concept.canonical_name
    concept_id = claim_focus_concept_id(claim)
    if concept_id is not None:
        return concept_id
    labels = _linked_concept_labels(world, claim)
    if labels:
        return ", ".join(labels)
    if claim.claim_type is ClaimType.EQUATION:
        return "(equation)"
    if claim.claim_type in {
        ClaimType.OBSERVATION,
        ClaimType.COMPARISON,
        ClaimType.MECHANISM,
        ClaimType.LIMITATION,
    }:
        return "(multiple concepts)"
    return "missing"


def _linked_concept_labels(world: WorldQuery, claim: Claim) -> tuple[str, ...]:
    labels: list[str] = []
    seen: set[str] = set()
    for concept_id in claim.concepts:
        concept = world.get_concept(concept_id)
        label = concept_id if concept is None else concept.canonical_name
        if label in seen:
            continue
        seen.add(label)
        labels.append(label)
    return tuple(labels)


def _value_display(claim: Claim) -> str:
    if claim.quantitative.point is not None:
        return f"{claim.quantitative.point} {claim.quantitative.unit or ''}".rstrip()
    interval = _interval_display(claim)
    if interval is not None:
        return interval
    text = _text_display(claim)
    if text is not None:
        return text
    if claim.claim_type in {
        ClaimType.MECHANISM,
        ClaimType.LIMITATION,
        ClaimType.COMPARISON,
        ClaimType.ALGORITHM,
        ClaimType.EQUATION,
        ClaimType.MODEL,
    }:
        return "n/a"
    return "(missing)"


def _interval_display(claim: Claim) -> str | None:
    from propstore.families.claim_quantitative import IntervalValue

    value = claim.quantitative.value
    if not isinstance(value, IntervalValue):
        return None
    suffix = f" {claim.quantitative.unit}" if claim.quantitative.unit else ""
    if value.lower is not None and value.upper is not None:
        return f"{value.lower} to {value.upper}{suffix}"
    if value.lower is not None:
        return f">= {value.lower}{suffix}"
    return f"<= {value.upper}{suffix}"


def _text_display(claim: Claim) -> str | None:
    if claim.expression and claim.claim_type is ClaimType.EQUATION:
        return _truncate(claim.expression)
    if claim.statement and claim.claim_type in {
        ClaimType.OBSERVATION,
        ClaimType.COMPARISON,
        ClaimType.MECHANISM,
        ClaimType.LIMITATION,
    }:
        return _truncate(claim.statement)
    return None


def _truncate(text: str, limit: int = _SUMMARY_TEXT_LIMIT) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3].rstrip()}..."


def _matches_query(claim: Claim, concept: Concept | None, needle: str) -> bool:
    if needle == "":
        return True
    fields = (
        str(claim.claim_id),
        claim.name or "",
        claim.statement or "",
        claim.expression or "",
        claim_condition_expression(claim) or "",
        "" if concept is None else concept.canonical_name,
    )
    return any(needle in field.casefold() for field in fields)


def _resolve_concept_filter(world: WorldQuery, concept: str | None) -> str | None:
    if concept is None:
        return None
    return world.resolve_concept(concept) or concept


def _claim_sort_key(claim: Claim) -> str:
    return str(claim.claim_id)
