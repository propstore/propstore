from __future__ import annotations

from propstore import provenance


def test_import_side_provenance_records_are_gone() -> None:
    """The import records were a second spelling of ``Provenance`` (2026-07-14).

    Import provenance rides the git note as a ``Provenance`` whose witnesses now
    carry the source version and content hash; nothing mirrors that on a parallel
    frozen dataclass.
    """

    for name in (
        "ImportRunProvenanceRecord",
        "SourceVersionProvenanceRecord",
        "LicenseProvenanceRecord",
        "ExternalStatementProvenanceRecord",
        "ExternalInferenceProvenanceRecord",
        "ExternalStatementAttitude",
    ):
        assert not hasattr(provenance, name), f"{name} must not be reintroduced"
