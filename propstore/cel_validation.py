"""Generic severity-aware CEL checking and structural identifier traversal."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

from cel_parser.ast import (
    Call,
    Comprehension,
    CreateList,
    CreateMap,
    CreateStruct,
    Expr,
    Ident,
    ParseError,
    Select,
)
from cel_parser.parser import parse
from condition_ir import (
    CelError,
    CheckedCondition,
    KindType,
    check_cel_expression,
    check_condition_ir,
)

if TYPE_CHECKING:
    from condition_ir import ConceptInfo


@dataclass(frozen=True)
class CelCheckResult:
    checked: CheckedCondition | None
    diagnostics: tuple[CelError, ...]

    @property
    def errors(self) -> tuple[CelError, ...]:
        return tuple(item for item in self.diagnostics if not item.is_warning)


def check_cel_condition(
    expression: str, registry: Mapping[str, ConceptInfo]
) -> CelCheckResult:
    """Retain substrate diagnostics and lower only accepted expressions."""
    diagnostics = tuple(check_cel_expression(expression, registry))
    if any(not item.is_warning for item in diagnostics):
        return CelCheckResult(checked=None, diagnostics=diagnostics)
    return CelCheckResult(
        checked=check_condition_ir(expression, registry), diagnostics=diagnostics
    )


def _collect_identifiers(node: Expr, names: set[str]) -> None:
    """Walk a parsed CEL expression, collecting identifier names.

    Recurses over the concrete cel-parser node types (rather than reflecting over
    dataclass fields) so the traversal stays fully typed. Literal nodes carry no
    identifiers and terminate the recursion.
    """

    if isinstance(node, Ident):
        names.add(node.name)
    elif isinstance(node, Select):
        _collect_identifiers(node.operand, names)
    elif isinstance(node, Call):
        if node.target is not None:
            _collect_identifiers(node.target, names)
        for arg in node.args:
            _collect_identifiers(arg, names)
    elif isinstance(node, CreateList):
        for element in node.elements:
            _collect_identifiers(element, names)
    elif isinstance(node, CreateMap):
        for entry in node.entries:
            _collect_identifiers(entry.key, names)
            _collect_identifiers(entry.value, names)
    elif isinstance(node, CreateStruct):
        for struct_entry in node.entries:
            _collect_identifiers(struct_entry.value, names)
    elif isinstance(node, Comprehension):
        _collect_identifiers(node.iter_range, names)
        _collect_identifiers(node.accu_init, names)
        _collect_identifiers(node.loop_condition, names)
        _collect_identifiers(node.loop_step, names)
        _collect_identifiers(node.result, names)


def iter_cel_identifiers(expression: str) -> frozenset[str]:
    """Return the concept identifiers a CEL expression references.

    Parses the expression with condition-ir's own parser and walks the AST for
    identifier nodes. A syntactically invalid expression yields the empty set —
    a parse error is general claim semantic invalidity (quarantined by the claim
    pipeline), not the structural-concept architectural invariant this feeds.
    """

    try:
        ast = parse(expression)
    except ParseError:
        return frozenset()
    names: set[str] = set()
    _collect_identifiers(ast, names)
    return frozenset(names)


def structural_concepts_in_expression(
    expression: str,
    registry: Mapping[str, ConceptInfo],
) -> tuple[str, ...]:
    """Return the structural concepts a CEL expression references, if any.

    A structural concept must never appear in a CEL expression — it is a hard
    architectural invariant (it breaks Z3 translation), distinct from a general
    CEL type error. The compiler treats this as an abort-class failure, while
    ordinary CEL type errors quarantine. Identifiers that do not resolve to a
    structural concept (unknown names, quantities, categories) are ignored here;
    those are reported by the ordinary CEL type-checker.
    """

    structural: list[str] = []
    for name in sorted(iter_cel_identifiers(expression)):
        info = registry.get(name)
        if info is not None and info.kind == KindType.STRUCTURAL:
            structural.append(name)
    return tuple(structural)


__all__ = [
    "CelCheckResult",
    "check_cel_condition",
    "iter_cel_identifiers",
    "structural_concepts_in_expression",
]
