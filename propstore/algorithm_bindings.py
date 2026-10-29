"""Canonical claim-variable grounding for algorithm consumers."""

from __future__ import annotations

import ast
from collections.abc import Mapping, Sequence

from ast_equiv import extract_free_variables, parse_algorithm

from propstore.families.claims import ClaimVariable


class AlgorithmBindingError(ValueError):
    """An algorithm cannot be grounded unambiguously in canonical concepts."""


def algorithm_bindings(variables: Sequence[ClaimVariable], body: str) -> dict[str, str]:
    """Project bindings, using the authored name when supplied, else symbol.

    Every parameter must have a canonical concept. Constant algorithms need no
    bindings. Repeated names or symbols are errors, even for the same concept.
    """
    bindings: dict[str, str] = {}
    names: set[str] = set()
    symbols: set[str] = set()
    for variable in variables:
        for value, seen, label in (
            (variable.name, names, "name"),
            (variable.symbol, symbols, "symbol"),
        ):
            if value is not None:
                if not value.strip() or value in seen:
                    raise AlgorithmBindingError(
                        f"Duplicate or empty algorithm {label}: {value!r}"
                    )
                seen.add(value)
        key = variable.name if variable.name is not None else variable.symbol
        if not key or not key.isidentifier() or not variable.concept.strip():
            raise AlgorithmBindingError(
                "Algorithm bindings require a name/symbol and canonical concept."
            )
        if key in bindings:
            raise AlgorithmBindingError(f"Duplicate algorithm binding: {key!r}")
        bindings[key] = variable.concept
    tree = parse_algorithm(body)
    parameters = extract_free_variables(tree)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            parameters.update(
                arg.arg
                for arg in (
                    *node.args.posonlyargs,
                    *node.args.args,
                    *node.args.kwonlyargs,
                )
            )
            for arg in (node.args.vararg, node.args.kwarg):
                if arg is not None:
                    parameters.add(arg.arg)
    missing = parameters - bindings.keys()
    if missing:
        raise AlgorithmBindingError(
            f"Missing algorithm bindings: {', '.join(sorted(missing))}"
        )
    return bindings


def algorithm_known_values(
    values: Mapping[str, float] | None, *bindings: Mapping[str, str]
) -> dict[str, float] | None:
    """Validate values against concept IDs after algorithm name normalization."""
    if values is None:
        return None
    concepts = {concept for binding in bindings for concept in binding.values()}
    unknown = values.keys() - concepts
    if unknown:
        raise AlgorithmBindingError(
            f"Known values require canonical bound concept IDs: {', '.join(sorted(unknown))}"
        )
    return dict(values)
