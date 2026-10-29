"""Shared state vocabulary for application view reports.

Claim, concept, and neighborhood builders assign these states from their report
fields. ``UNKNOWN`` is distinct from policy-hidden ``BLOCKED`` and unauthored
``MISSING``; each builder owns the meaning of its field's state.
"""

from __future__ import annotations

from enum import StrEnum


class ViewState(StrEnum):
    """A per-field render state in the owner-layer view tier.

    ``StrEnum`` so each member lowers to its string value through
    :func:`propstore.reporting.json_ready` and compares equal to that string,
    keeping the report payloads stable across the CLI and web adapters.
    """

    KNOWN = "known"
    UNKNOWN = "unknown"
    VACUOUS = "vacuous"
    UNDERSPECIFIED = "underspecified"
    BLOCKED = "blocked"
    MISSING = "missing"
    NOT_APPLICABLE = "not_applicable"
    UNAVAILABLE = "unavailable"
