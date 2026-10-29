from __future__ import annotations

import ast
from pathlib import Path

import pytest
from msgspec.structs import replace

from propstore.core.labels import Label, environment_assumption_ids
from propstore.support_revision.entrenchment import compute_entrenchment
from propstore.support_revision.history import (
    EpistemicSnapshot,
    apply_epistemic_diff,
    diff_epistemic_snapshots,
)
from propstore.support_revision.iterated import make_epistemic_state
from propstore.support_revision.projection import project_belief_base, snapshot_to_claim_ids
from propstore.support_revision.realization import stabilize_belief_base
from propstore.support_revision.state import AssertionAtom
from tests.atms_feed import ClaimSpec, build_bound


def _project(*, shared: bool = False, reverse: bool = False):
    claims = [
        ClaimSpec("claim_a", "same", value=1, conditions=("x == 1",)),
        ClaimSpec("claim_b", "same", value=1, conditions=(
            "x == 1" if shared else "y == 2",
        )),
    ]
    return project_belief_base(build_bound(
        claims=list(reversed(claims)) if reverse else claims,
        bindings={"x": 1, "y": 2},
    ))


def _snapshot(base):
    return EpistemicSnapshot.from_state(make_epistemic_state(
        base, compute_entrenchment(None, base),
    ))


@pytest.mark.parametrize("shared", [False, True])
def test_projection_retains_individual_exact_evidence_and_order_independent_hash(shared):
    base = _project(shared=shared)
    atom = base.atoms[0]
    assert isinstance(atom, AssertionAtom)
    assert len(base.atoms) == 1
    assert [w.claim.claim_id for w in atom.source_support] == ["claim_a", "claim_b"]
    assert all(w.label == w.current_label for w in atom.source_support)
    assert all(w.quality.value == "exact" for w in atom.source_support)
    assert (atom.source_support[0].label == atom.source_support[1].label) is shared
    assert all(w.essential_support for w in atom.source_support)
    assert compute_entrenchment(None, base).reasons[atom.atom_id].support_count == (
        1 if shared else 2
    )
    assert _snapshot(base).content_hash == _snapshot(
        _project(shared=shared, reverse=True)
    ).content_hash


@pytest.mark.parametrize("shared,cut_all", [(False, False), (False, True), (True, False)])
def test_incision_only_activates_sources_with_their_own_surviving_support(shared, cut_all):
    base = _project(shared=shared)
    atom = base.atoms[0]
    first = atom.source_support[0]
    cuts = list(first.essential_support)
    if cut_all:
        cuts.extend(atom.source_support[1].essential_support)
    result = stabilize_belief_base(base, incision_set=cuts)
    expected = set() if shared or cut_all else {"claim_b"}
    assert snapshot_to_claim_ids(_snapshot(result.revised_base)) == expected
    if expected:
        current = result.revised_base.atoms[0]
        assert current.source_support[0].label == first.label
        assert not current.source_support[0].active
        assert current.source_support[1].active
        assert current.source_support[1].current_label == atom.source_support[1].label
        assert len(result.revised_base.support_sets[atom.atom_id]) == 1
        assert compute_entrenchment(None, result.revised_base).reasons[
            atom.atom_id
        ].support_count == 1
    else:
        assert atom.atom_id in result.rejected_atom_ids


def test_multiple_environments_preserve_original_evidence_and_current_provenance():
    base = _project()
    atom = base.atoms[0]
    first, second = atom.source_support
    label = Label(first.label.environments + second.label.environments)
    atom = replace(atom, source_support=(
        replace(first, label=label, current_label=label, essential_support=()), second,
    ))
    base = replace(base, atoms=(atom,))
    result = stabilize_belief_base(base, incision_set=first.essential_support)
    current = result.revised_base.atoms[0]
    assert current.source_support[0].label == label
    assert current.source_support[0].current_label == second.label
    assert snapshot_to_claim_ids(_snapshot(result.revised_base)) == {"claim_a", "claim_b"}
    assert base.support_sets[atom.atom_id] == tuple(sorted({
        environment_assumption_ids(environment) for environment in label.environments
    }))


def test_witness_and_current_support_round_trip_hash_and_semantic_diff():
    base = _project()
    source = _snapshot(base)
    result = stabilize_belief_base(
        base, incision_set=base.atoms[0].source_support[0].essential_support,
    )
    # Keep ranking and continuation seed fixed so this diff isolates the
    # changed source evidence and assertion support alternatives.
    target = EpistemicSnapshot.from_state(replace(
        source.state, base=result.revised_base,
    ))
    restored = EpistemicSnapshot.from_mapping(target.to_dict())
    assert restored == target
    assert restored.content_hash == target.content_hash != source.content_hash
    assert apply_epistemic_diff(source, diff_epistemic_snapshots(source, target)) == target
    assert snapshot_to_claim_ids(restored) == {"claim_b"}


def test_assertion_atom_has_no_primary_source_or_parallel_label_fields():
    tree = ast.parse(Path("propstore/support_revision/state.py").read_text("utf-8"))
    atom = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                and node.name == "AssertionAtom")
    names = {node.name for node in atom.body if isinstance(node, ast.FunctionDef)}
    names.update(node.target.id for node in atom.body if isinstance(node, ast.AnnAssign)
                 and isinstance(node.target, ast.Name))
    assert names.isdisjoint({"source_claims", "label", "primary_source_claim"})
