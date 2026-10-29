"""Runtime activation preserves the checked condition owner's failure."""

import pytest
from condition_ir import ConceptInfo, ConditionSolver, KindType, Z3TranslationError

from propstore.claim_conditions import check_claim
from propstore.core.activation import is_claim_active
from propstore.core.environment import Environment
from propstore.families.claims import Claim, ClaimType


def test_activation_preserves_checked_registry_mismatch() -> None:
    registry = {"x": ConceptInfo(id="x", canonical_name="x", kind=KindType.QUANTITY)}
    claim = check_claim(Claim(claim_id="conditional", claim_type=ClaimType.MODEL,
        conditions=("x > 0",)), registry)
    solver = ConditionSolver(registry)
    environment = Environment(bindings={"x": 2, "environment_only": True})

    with pytest.raises(Z3TranslationError, match="different condition registry"):
        is_claim_active(claim, environment=environment, solver=solver)
