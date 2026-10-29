"""CEL validation: identifier extraction + the structural-concept invariant.

The compiler's structural-invariant pre-pass aborts only on a *structural*
concept appearing in a CEL expression — a narrow architectural invariant. Ordinary
CEL type errors are NOT this pass's concern (they quarantine through the claim
pipeline). These tests pin both the narrow detection and the generic identifier
walk it rests on.
"""

from __future__ import annotations

from condition_ir import ConceptInfo, KindType

from propstore.cel_validation import (
    iter_cel_identifiers,
    structural_concepts_in_expression,
)


def _registry() -> dict[str, ConceptInfo]:
    return {
        "freq": ConceptInfo(
            id="freq", canonical_name="frequency", kind=KindType.QUANTITY
        ),
        "onset": ConceptInfo(
            id="onset", canonical_name="onset", kind=KindType.TIMEPOINT
        ),
        "shape": ConceptInfo(
            id="shape", canonical_name="shape", kind=KindType.STRUCTURAL
        ),
    }


def test_iter_cel_identifiers_collects_names() -> None:
    assert iter_cel_identifiers("freq > 10 && onset < 5") == frozenset(
        {"freq", "onset"}
    )


def test_iter_cel_identifiers_handles_nested_call() -> None:
    assert "freq" in iter_cel_identifiers("(freq + 1) > 10")


def test_iter_cel_identifiers_on_parse_error_is_empty() -> None:
    # A syntactically invalid expression is general claim semantic invalidity,
    # quarantined elsewhere — the structural pre-pass sees no identifiers.
    assert iter_cel_identifiers("freq > ") == frozenset()


def test_structural_concept_detected() -> None:
    assert structural_concepts_in_expression("shape == 1", _registry()) == ("shape",)


def test_non_structural_expression_has_no_structural_concepts() -> None:
    assert structural_concepts_in_expression("freq > 10", _registry()) == ()
