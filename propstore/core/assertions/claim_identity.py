"""Assertion identity for canonical claim charters."""

from __future__ import annotations

import hashlib
import json
import msgspec

from propstore.core.id_types import ContextId, to_context_id
from propstore.families.claims import Claim


def content_digest(value: object) -> str:
    """Return the persisted deterministic digest for assertion identity."""

    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _semantic_fields(claim: Claim) -> dict[str, object]:
    """Hash serialization boundary for nonquantitative propositional content."""

    return {
        "claim_type": None if claim.claim_type is None else claim.claim_type.value,
        "statement": claim.statement,
        "name": claim.name,
        "body": claim.body,
        "expression": claim.expression,
        "sympy": claim.sympy,
        "measure": claim.measure,
        "methodology": claim.methodology,
        "notes": claim.notes,
        "output_concept": claim.output_concept,
        "target_concept": claim.target_concept,
        "concepts": list(claim.concepts),
        "equations": list(claim.equations),
    }


def semantic_content(claim: Claim) -> dict[str, object]:
    """Runtime identity consumes the same checked value as semantic reasoning."""
    return {**_semantic_fields(claim), "quantitative": msgspec.to_builtins(claim.quantitative)}


def claim_assertion_id(
    claim: Claim,
    *,
    context_id: ContextId | str | None,
) -> str:
    """Return stable assertion identity for a canonical claim."""

    effective_context = (
        claim.context_id
        if claim.context_id is not None
        else (None if context_id is None else str(to_context_id(context_id)))
    )
    key = {
        "content": semantic_content(claim),
        "context_id": effective_context,
        "conditions": sorted(claim.conditions),
    }
    return f"ps:assertion:{content_digest(key)}"


__all__ = [
    "claim_assertion_id",
    "content_digest",
    "semantic_content",
]
