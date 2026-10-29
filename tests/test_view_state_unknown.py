"""The shared vocabulary distinguishes unknown, blocked, and missing states."""

from __future__ import annotations

from propstore.app.view_state import ViewState


def test_unknown_is_distinct_from_blocked_and_missing() -> None:
    assert ViewState.UNKNOWN != ViewState.BLOCKED
    assert ViewState.UNKNOWN != ViewState.MISSING
    assert ViewState.BLOCKED != ViewState.MISSING
    assert len({ViewState.UNKNOWN, ViewState.BLOCKED, ViewState.MISSING}) == 3
    assert ViewState.UNKNOWN.value == "unknown"
