"""Projection result models and extension semantics for structured argumentation.

ASPIC+ construction lives in ``propstore.aspic_bridge`` (``csaf_to_projection``).
This module owns the propstore-facing projection records and the extension
semantics computed over a constructed :class:`StructuredProjection`. The Dung
semantics themselves are the argumentation package's (CLAUDE.md substrate
boundary): this module selects among them, it does not re-implement them.
"""

from __future__ import annotations

from dataclasses import dataclass

from argumentation.core.dung import (
    ArgumentationFramework,
    complete_extensions,
    grounded_extension,
    preferred_extensions,
    stable_extensions,
)

from propstore.core.labels import Label, SupportQuality
from propstore.core.reasoning import (
    ArgumentationSemantics,
    ReasoningBackend,
    validate_backend_semantics,
)


@dataclass(frozen=True)
class StructuredArgument:
    arg_id: str
    claim_id: str | None
    conclusion_concept_id: str | None
    premise_claim_ids: tuple[str, ...]
    label: Label | None
    strength: float
    top_rule_kind: str
    attackable_kind: str
    subargument_ids: tuple[str, ...]
    support_quality: SupportQuality
    justification_id: str
    dependency_claim_ids: tuple[str, ...]


@dataclass(frozen=True)
class StructuredProjection:
    arguments: tuple[StructuredArgument, ...]
    framework: ArgumentationFramework
    claim_to_argument_ids: dict[str, tuple[str, ...]]
    argument_to_claim_id: dict[str, str]


def compute_structured_justified_arguments(
    projection: StructuredProjection,
    *,
    semantics: str = "grounded",
    backend: ReasoningBackend = ReasoningBackend.ASPIC,
) -> frozenset[str] | list[frozenset[str]]:
    """Compute justified structured arguments using existing Dung semantics."""

    _, normalized_semantics = validate_backend_semantics(
        backend,
        semantics,
    )
    framework = projection.framework
    if normalized_semantics in {
        ArgumentationSemantics.GROUNDED,
        ArgumentationSemantics.ASPIC_DIRECT_GROUNDED,
        ArgumentationSemantics.ASPIC_INCOMPLETE_GROUNDED,
    }:
        if backend == ReasoningBackend.ASPIC and framework.attacks is not None:
            complete = [frozenset(ext) for ext in complete_extensions(framework)]
            if not complete:
                return frozenset()
            return min(complete, key=lambda ext: (len(ext), tuple(sorted(ext))))
        return grounded_extension(framework)
    if normalized_semantics == ArgumentationSemantics.COMPLETE:
        return [frozenset(ext) for ext in complete_extensions(projection.framework)]
    if normalized_semantics == ArgumentationSemantics.PREFERRED:
        return [frozenset(ext) for ext in preferred_extensions(projection.framework)]
    if normalized_semantics == ArgumentationSemantics.STABLE:
        return [frozenset(ext) for ext in stable_extensions(projection.framework)]
    raise ValueError(
        f"{backend.value} does not support semantics '{normalized_semantics.value}'"
    )
