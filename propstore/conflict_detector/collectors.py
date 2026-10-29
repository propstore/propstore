"""Group canonical claims by their owning concept roles."""

from collections import defaultdict
from collections.abc import Sequence

from eq_equiv import BoundEquation, EquationSymbolBinding, equation_signature

from propstore.families.claims import Claim, ClaimType


def equation_bound_for_claim(claim: Claim) -> BoundEquation:
    return BoundEquation(
        expression=claim.expression or claim.sympy or "",
        variables=tuple(
            EquationSymbolBinding(
                symbol=variable.symbol, concept_id=variable.concept, role=variable.role
            )
            for variable in claim.variables
            if variable.symbol
        ),
    )


def collect_measurement_claims(
    claims: Sequence[Claim],
) -> dict[tuple[str, str], list[Claim]]:
    groups: dict[tuple[str, str], list[Claim]] = defaultdict(list)
    for claim in claims:
        if (
            claim.claim_type is ClaimType.MEASUREMENT
            and claim.target_concept
            and claim.measure
        ):
            groups[(claim.target_concept, claim.measure)].append(claim)
    return dict(groups)


def collect_parameter_claims(claims: Sequence[Claim]) -> dict[str, list[Claim]]:
    groups: dict[str, list[Claim]] = defaultdict(list)
    for claim in claims:
        if claim.claim_type is ClaimType.PARAMETER and claim.output_concept:
            groups[claim.output_concept].append(claim)
    return dict(groups)


def collect_equation_claims(
    claims: Sequence[Claim],
) -> dict[tuple[str, tuple[str, ...]], list[Claim]]:
    groups: dict[tuple[str, tuple[str, ...]], list[Claim]] = defaultdict(list)
    for claim in claims:
        if claim.claim_type is ClaimType.EQUATION:
            signature = equation_signature(equation_bound_for_claim(claim))
            if signature is not None:
                groups[signature].append(claim)
    return dict(groups)


def collect_algorithm_claims(claims: Sequence[Claim]) -> dict[str, list[Claim]]:
    groups: dict[str, list[Claim]] = defaultdict(list)
    for claim in claims:
        if claim.claim_type is ClaimType.ALGORITHM and claim.output_concept is not None:
            groups[claim.output_concept].append(claim)
    return dict(groups)
