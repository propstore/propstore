"""Semantic passes and stages for the ``claim`` family (flat charter).

The claim AUTHORED -> CHECKED pass does the real per-claim CHECKED compute: it
validates the claim against its type contract
(:mod:`propstore.claim_contracts`), type-checks its authored CEL conditions into
condition-ir's checked set (:mod:`propstore.claim_conditions`), checks its
``context_id`` against the known contexts, and normalises the claim (filling
``conditions_ir``).

Crucially, the claim pass ALWAYS returns a :class:`ClaimCheckedBundle` — even
when claims are invalid. A semantically invalid claim is retained as a
``blocked`` :class:`CheckedClaim` with its diagnostics; the runner never
short-circuits the claim pipeline, so ``build_repository`` does not abort. This
is the quarantine half of the Z1 split (claim/stance semantic invalidity
quarantines; form/concept/context validation failure aborts).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

import msgspec

from propstore.claim_conditions import check_claim, check_claim_conditions
from propstore.claim_contracts import validate_claim
from propstore.compiler.context import CompilationContext
from propstore.compiler.ir import CheckedClaim, ClaimCheckedBundle
from propstore.families.claim_admission import CLAIM_CHECK_VERSION
from propstore.families.claims import Claim
from propstore.families.registry import PropstoreFamily
from propstore.semantic_passes.registry import PipelineRegistry
from propstore.semantic_passes.runner import run_pipeline
from propstore.semantic_passes.types import (
    PassDiagnostic,
    PassResult,
    PipelineResult,
)

_FAMILY = PropstoreFamily.CLAIM


class ClaimStage(StrEnum):
    AUTHORED = "claim.authored"
    CHECKED = "claim.checked"


@dataclass(frozen=True)
class LoadedClaim:
    claim: Claim
    filename: str | None = None

    @property
    def claim_id(self) -> str:
        return self.claim.claim_id


@dataclass(frozen=True)
class ClaimFiles:
    claims: tuple[LoadedClaim, ...]
    context: CompilationContext

    @classmethod
    def from_sequence(
        cls,
        claims: Sequence[LoadedClaim],
        context: CompilationContext,
    ) -> ClaimFiles:
        return cls(claims=tuple(claims), context=context)


def _error(
    code: str,
    message: str,
    loaded: LoadedClaim,
    field: str | None,
) -> PassDiagnostic:
    return PassDiagnostic(
        level="error",
        code=code,
        message=message,
        family=_FAMILY,
        stage=ClaimStage.CHECKED,
        filename=loaded.filename,
        artifact_id=loaded.claim_id,
        pass_name="claim.check",
        field=field,
    )


def _check_one(
    loaded: LoadedClaim,
    context: CompilationContext,
) -> CheckedClaim:
    claim = loaded.claim
    diagnostics: list[PassDiagnostic] = []

    contract_report = validate_claim(
        claim,
        context=context,
    )
    for problem in contract_report.diagnostics:
        diagnostics.append(_error(problem.code, problem.message, loaded, problem.field))

    condition_report = check_claim_conditions(claim, context.condition_registry)
    for condition_problem in condition_report.diagnostics:
        diagnostics.append(
            PassDiagnostic(
                level="warning" if condition_problem.diagnostic.is_warning else "error",
                code="claim.condition",
                message=condition_problem.message,
                family=_FAMILY,
                stage=ClaimStage.CHECKED,
                filename=loaded.filename,
                artifact_id=loaded.claim_id,
                pass_name="claim.check",
                field="conditions",
                index=condition_problem.index,
                cel_diagnostic=condition_problem.diagnostic,
            )
        )

    if (
        claim.context_id is not None
        and context.context_ids
        and claim.context_id not in context.context_ids
    ):
        diagnostics.append(
            _error(
                "claim.context.dangling",
                f"claim '{claim.claim_id}' references unknown context "
                f"'{claim.context_id}'",
                loaded,
                "context_id",
            )
        )

    normalized = check_claim(claim, context.condition_registry)
    normalized = msgspec.structs.replace(
        normalized, quantitative_ir=contract_report.quantitative
    )
    return CheckedClaim(
        claim=normalized,
        blocked=any(item.is_error for item in diagnostics),
        diagnostics=tuple(diagnostics),
    )


class ClaimCheckPass:
    family = _FAMILY
    name = "claim.check"
    version = CLAIM_CHECK_VERSION
    input_stage = ClaimStage.AUTHORED
    output_stage = ClaimStage.CHECKED

    def run(self, value: ClaimFiles, context: object) -> PassResult[ClaimCheckedBundle]:
        checked = tuple(_check_one(loaded, value.context) for loaded in value.claims)
        bundle = ClaimCheckedBundle(claims=checked)
        return PassResult(output=bundle, diagnostics=bundle.diagnostics)


def register_claim_pipeline(registry: PipelineRegistry) -> None:
    registry.register(ClaimCheckPass, family=_FAMILY)


def run_claim_pipeline(value: ClaimFiles) -> PipelineResult[object]:
    registry = PipelineRegistry()
    register_claim_pipeline(registry)
    return run_pipeline(
        value,
        family=_FAMILY,
        start_stage=ClaimStage.AUTHORED,
        target_stage=ClaimStage.CHECKED,
        registry=registry,
        context=None,
    )
