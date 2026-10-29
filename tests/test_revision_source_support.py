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
from propstore.support_revision.projection import (
    project_belief_base,
    snapshot_to_claim_ids,
)
from propstore.support_revision.realization import stabilize_belief_base
from propstore.support_revision.state import AssertionAtom
from tests.atms_feed import ClaimSpec, build_bound


def _project(*, shared: bool = False, reverse: bool = False):
    claims = [
        ClaimSpec("claim_a", "same", value=1, conditions=("x == 1",)),
        ClaimSpec(
            "claim_b", "same", value=1, conditions=("x == 1" if shared else "y == 2",)
        ),
    ]
    return project_belief_base(
        build_bound(
            claims=list(reversed(claims)) if reverse else claims,
            bindings={"x": 1, "y": 2},
        )
    )


def _snapshot(base):
    return EpistemicSnapshot.from_state(
        make_epistemic_state(
            base,
            compute_entrenchment(None, base),
        )
    )


@pytest.mark.parametrize("shared", [False, True])
def test_projection_retains_individual_exact_evidence_and_order_independent_hash(
    shared,
):
    base = _project(shared=shared)
    atom = base.atoms[0]
    assert isinstance(atom, AssertionAtom)
    assert len(base.atoms) == 1
    assert [w.claim.claim_id for w in atom.source_support] == ["claim_a", "claim_b"]
    assert all(w.label == w.current_label for w in atom.source_support)
    assert all(w.quality.value == "exact" for w in atom.source_support)
    assert (atom.source_support[0].label == atom.source_support[1].label) is shared
    assert all(w.essential_support for w in atom.source_support)
    assert base.essential_support[atom.atom_id] == (
        atom.source_support[0].essential_support if shared else ()
    )
    assert compute_entrenchment(None, base).reasons[atom.atom_id].support_count == (
        1 if shared else 2
    )
    assert (
        _snapshot(base).content_hash
        == _snapshot(_project(shared=shared, reverse=True)).content_hash
    )


@pytest.mark.parametrize(
    "shared,cut_all", [(False, False), (False, True), (True, False)]
)
def test_incision_only_activates_sources_with_their_own_surviving_support(
    shared, cut_all
):
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
        assert result.revised_base.essential_support[atom.atom_id] == (
            atom.source_support[1].essential_support
        )
        assert (
            compute_entrenchment(None, result.revised_base)
            .reasons[atom.atom_id]
            .support_count
            == 1
        )
    else:
        assert atom.atom_id in result.rejected_atom_ids


def test_multiple_environments_preserve_original_evidence_and_current_provenance():
    base = _project()
    atom = base.atoms[0]
    first, second = atom.source_support
    label = Label(first.label.environments + second.label.environments)
    atom = replace(
        atom,
        source_support=(
            replace(first, label=label, current_label=label, essential_support=()),
            second,
        ),
    )
    base = replace(base, atoms=(atom,))
    result = stabilize_belief_base(base, incision_set=first.essential_support)
    current = result.revised_base.atoms[0]
    assert current.source_support[0].label == label
    assert current.source_support[0].current_label == second.label
    assert snapshot_to_claim_ids(_snapshot(result.revised_base)) == {
        "claim_a",
        "claim_b",
    }
    assert base.support_sets[atom.atom_id] == tuple(
        sorted(
            {
                environment_assumption_ids(environment)
                for environment in label.environments
            }
        )
    )


def test_witness_and_current_support_round_trip_hash_and_semantic_diff():
    base = _project()
    source = _snapshot(base)
    result = stabilize_belief_base(
        base,
        incision_set=base.atoms[0].source_support[0].essential_support,
    )
    # Keep ranking and continuation seed fixed so this diff isolates the
    # changed source evidence and assertion support alternatives.
    target = EpistemicSnapshot.from_state(
        replace(
            source.state,
            base=result.revised_base,
        )
    )
    restored = EpistemicSnapshot.from_mapping(target.to_dict())
    assert restored == target
    assert restored.content_hash == target.content_hash != source.content_hash
    assert (
        apply_epistemic_diff(source, diff_epistemic_snapshots(source, target)) == target
    )
    assert snapshot_to_claim_ids(restored) == {"claim_b"}


def test_assertion_atom_has_no_primary_source_or_parallel_label_fields():
    tree = ast.parse(Path("propstore/support_revision/state.py").read_text("utf-8"))
    atom = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "AssertionAtom"
    )
    names = {node.name for node in atom.body if isinstance(node, ast.FunctionDef)}
    names.update(
        node.target.id
        for node in atom.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    )
    assert names.isdisjoint({"source_claims", "label", "primary_source_claim"})


def _contraction_bound(*, reverse=False):
    claims = [
        ClaimSpec("claim_a", "same", value=1, conditions=("x == 1",)),
        ClaimSpec("claim_b", "same", value=1, conditions=("y == 2",)),
        ClaimSpec("target", "other", value=2, conditions=("x == 1",)),
    ]
    return build_bound(
        claims=list(reversed(claims)) if reverse else claims, bindings={"x": 1, "y": 2}
    )


def test_real_formal_contraction_reports_only_surviving_source_claim_ids():
    bound = _contraction_bound()
    base = bound.revision_base()
    target = next(
        atom
        for atom in base.atoms
        if any(w.claim.claim_id == "target" for w in atom.source_support)
    )
    result = bound.contract(target.atom_id, max_candidates=32)
    assert result.realization.source_claim_ids == ("claim_b",)
    assert snapshot_to_claim_ids(_snapshot(result.revised_base)) == {"claim_b"}
    surviving = result.revised_base.atoms[0]
    assert [w.active for w in surviving.source_support] == [False, True]


def test_worldline_capture_replay_and_storage_keep_source_evidence_after_incision(
    tmp_path,
):
    from propstore.families.registry import WorldlineRef
    from propstore.repository import Repository
    from propstore.worldline.definition import WorldlineDefinition
    from propstore.worldline.query import WorldlineRevisionQuery
    from propstore.worldline.revision_capture import capture_journal

    def capture(reverse):
        bound = _contraction_bound(reverse=reverse)
        target = next(
            atom
            for atom in bound.revision_base().atoms
            if any(w.claim.claim_id == "target" for w in atom.source_support)
        )
        return capture_journal(
            bound,
            (
                WorldlineRevisionQuery(
                    operation="contract",
                    target=target.atom_id,
                ),
            ),
        )

    journal = capture(False)
    assert journal.replay().ok
    assert journal == capture(True)
    assert snapshot_to_claim_ids(journal.entries[-1].state_out) == {"claim_b"}
    repo = Repository.init(tmp_path / "knowledge")
    definition = WorldlineDefinition(
        name="support", id="support", targets=["same"], journal=journal
    )
    repo.families.worldlines.save(
        WorldlineRef("support"), definition, message="capture source evidence"
    )
    loaded = repo.families.worldlines.load(WorldlineRef("support"))
    assert loaded.journal == journal
    assert loaded.journal.replay().ok
    original = journal.entries[0].state_in.state.base.atoms
    current = loaded.journal.entries[0].state_out.state.base.atoms[0]
    shared = next(atom for atom in original if len(atom.source_support) == 2)
    assert [w.label for w in current.source_support] == [
        w.label for w in shared.source_support
    ]
    assert [w.active for w in current.source_support] == [False, True]


def test_ic_merge_preserves_original_and_current_source_support():
    from propstore.support_revision.belief_set_adapter import decide_ic_merge_profile
    from propstore.support_revision.integrity_constraints import AtomConstraint
    from propstore.support_revision.realization import realize_ic_merge_decision

    base = _project()
    partial = stabilize_belief_base(
        base,
        incision_set=base.atoms[0].source_support[0].essential_support,
    ).revised_base
    atom = partial.atoms[0]
    decision = decide_ic_merge_profile(
        profile_atom_ids=((atom.atom_id,), (atom.atom_id,)),
        integrity_constraint=AtomConstraint(atom.atom_id),
        max_alphabet_size=4,
    )
    result = realize_ic_merge_decision(partial, decision)
    assert result.revised_base.atoms == partial.atoms
    assert result.revised_base.support_sets == partial.support_sets
    assert result.realization.source_claim_ids == ("claim_b",)
    assert _snapshot(result.revised_base) == _snapshot(partial)


def test_repeated_incision_uses_current_support_and_keeps_original_witness_essentials():
    base = _project()
    atom = base.atoms[0]
    first, second = atom.source_support
    partial = stabilize_belief_base(
        base, incision_set=first.essential_support
    ).revised_base
    current = partial.atoms[0]
    assert current.source_support[0].essential_support == first.essential_support
    assert current.source_support[1].essential_support == second.essential_support
    unchanged = stabilize_belief_base(partial, incision_set=first.essential_support)
    assert unchanged.revised_base == partial
    rejected = stabilize_belief_base(partial, incision_set=second.essential_support)
    assert rejected.accepted_atom_ids == ()
    assert rejected.rejected_atom_ids == (atom.atom_id,)


def test_unconditional_source_uses_unit_label_and_missing_evidence_is_inactive():
    base = project_belief_base(
        build_bound(
            claims=[ClaimSpec("unconditional", "same", value=1)],
            bindings={},
        )
    )
    witness = base.atoms[0].source_support[0]
    assert witness.label == Label.empty()
    assert witness.active
    assert not replace(witness, label=None, current_label=None).active
    assert snapshot_to_claim_ids(_snapshot(base)) == {"unconditional"}
