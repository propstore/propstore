"""Single home for the provenance JSON-LD constants.

The named-graph carrier (:mod:`propstore.provenance`) uses the JSON-LD
``@context`` and accepted URI scheme prefixes defined here.
This module imports nothing from the package, so importing it never cycles.
"""

from __future__ import annotations

JSONLD_CONTEXT: dict[str, str] = {
    "ps": "https://prop.store/ns#",
    "prov": "http://www.w3.org/ns/prov#",
    "swp": "http://www.w3.org/2004/03/trix/swp-2/",
}

# Schemes accepted for a named graph id or derived-from graph pointer.
URI_SCHEME_PREFIXES: tuple[str, ...] = ("urn:", "ni://", "http://", "https://")
