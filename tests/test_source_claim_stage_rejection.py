"""Removed algorithm stage input fails at the source document boundary."""

import pytest
from quire.documents import (
    DocumentSchemaError,
    convert_document_value,
    decode_document_bytes,
    decode_json_document_bytes,
)

from propstore.families.sources import SourceClaimsDocument


@pytest.mark.parametrize("stage", ["preprocess", "postprocess", None])
def test_source_claim_typed_conversion_rejects_removed_stage(stage: str | None) -> None:
    with pytest.raises(DocumentSchemaError, match="unknown field `stage`"):
        convert_document_value(
            {"claims": [{"type": "algorithm", "body": "return 1", "stage": stage}]},
            SourceClaimsDocument,
            source="claims",
        )


def test_source_claim_json_rejects_removed_stage() -> None:
    with pytest.raises(DocumentSchemaError, match="unknown field `stage`"):
        decode_json_document_bytes(
            b'{"claims": [{"type": "algorithm", "stage": "preprocess"}]}',
            SourceClaimsDocument,
            source="claims.json",
        )


def test_source_claim_yaml_rejects_removed_stage() -> None:
    with pytest.raises(DocumentSchemaError, match="unknown field `stage`"):
        decode_document_bytes(
            b"claims:\n  - type: algorithm\n    stage: postprocess\n",
            SourceClaimsDocument,
            source="claims.yaml",
        )
