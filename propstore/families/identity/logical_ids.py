"""Logical-id tokens for authored claims and concepts.

A logical id is a ``namespace:value`` pair that names an authored artifact
independently of its derived canonical ``ps:`` identity. These helpers normalise
namespace/value tokens to a stable character set so the same authored handle
always derives the same canonical artifact id.
"""

from __future__ import annotations

import re


def normalize_identity_namespace(value: str) -> str:
    """Return a valid logical-id namespace token."""

    normalized = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    normalized = normalized.strip("._-")
    if not normalized:
        return "source"
    if not normalized[0].isalnum():
        normalized = f"ns_{normalized}"
    return normalized


def normalize_logical_value(value: str) -> str:
    """Return a valid logical-id value token."""

    normalized = re.sub(r"[^A-Za-z0-9._/-]+", "_", value.strip())
    normalized = normalized.strip("._/-")
    if not normalized:
        return "item"
    if not normalized[0].isalnum():
        normalized = f"id_{normalized}"
    return normalized
