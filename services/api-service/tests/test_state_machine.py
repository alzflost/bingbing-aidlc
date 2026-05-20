"""Unit tests for Speaker Mapping State Machine.

PBT-03: Invariant — valid transitions only produce valid states.
PBT-06: Stateful — state machine never reaches invalid state.
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from shared.models import MappingState
from src.mapping.state_machine import get_next_state, is_valid_transition


class TestValidTransitions:
    """Test valid state transitions."""

    def test_idle_to_onboarding(self) -> None:
        assert is_valid_transition(MappingState.IDLE, MappingState.ONBOARDING)

    def test_onboarding_to_active(self) -> None:
        assert is_valid_transition(MappingState.ONBOARDING, MappingState.ACTIVE)

    def test_active_to_trip_end(self) -> None:
        assert is_valid_transition(MappingState.ACTIVE, MappingState.TRIP_END)

    def test_trip_end_to_idle(self) -> None:
        assert is_valid_transition(MappingState.TRIP_END, MappingState.IDLE)


class TestInvalidTransitions:
    """Test invalid state transitions are rejected."""

    def test_idle_to_active_invalid(self) -> None:
        assert not is_valid_transition(MappingState.IDLE, MappingState.ACTIVE)

    def test_idle_to_trip_end_invalid(self) -> None:
        assert not is_valid_transition(MappingState.IDLE, MappingState.TRIP_END)

    def test_active_to_onboarding_invalid(self) -> None:
        assert not is_valid_transition(MappingState.ACTIVE, MappingState.ONBOARDING)

    def test_onboarding_to_idle_invalid(self) -> None:
        assert not is_valid_transition(MappingState.ONBOARDING, MappingState.IDLE)


class TestGetNextState:
    """Test event-driven state transitions."""

    def test_trip_start_from_idle(self) -> None:
        result = get_next_state(MappingState.IDLE, "trip_start")
        assert result == MappingState.ONBOARDING

    def test_mapping_complete_from_onboarding(self) -> None:
        result = get_next_state(MappingState.ONBOARDING, "mapping_complete")
        assert result == MappingState.ACTIVE

    def test_timeout_from_onboarding(self) -> None:
        result = get_next_state(MappingState.ONBOARDING, "timeout")
        assert result == MappingState.ACTIVE

    def test_trip_end_from_active(self) -> None:
        result = get_next_state(MappingState.ACTIVE, "trip_end")
        assert result == MappingState.TRIP_END

    def test_reflection_complete_from_trip_end(self) -> None:
        result = get_next_state(MappingState.TRIP_END, "reflection_complete")
        assert result == MappingState.IDLE

    def test_invalid_event_returns_none(self) -> None:
        result = get_next_state(MappingState.IDLE, "trip_end")
        assert result is None

    def test_unknown_event_returns_none(self) -> None:
        result = get_next_state(MappingState.ACTIVE, "unknown_event")
        assert result is None


class TestStateMachinePBT:
    """Property-based tests for state machine invariants (PBT-06)."""

    @given(st.sampled_from(list(MappingState)))
    @settings(max_examples=50)
    def test_self_transition_never_valid(
        self,
        state: MappingState,
    ) -> None:
        """Invariant: no state can transition to itself."""
        assert not is_valid_transition(state, state)

    @given(
        st.sampled_from(list(MappingState)),
        st.text(min_size=1, max_size=30),
    )
    @settings(max_examples=100)
    def test_invalid_event_never_crashes(
        self,
        state: MappingState,
        event: str,
    ) -> None:
        """Invariant: any event on any state never raises (fail-safe)."""
        result = get_next_state(state, event)
        assert result is None or isinstance(result, MappingState)

    @given(st.sampled_from(list(MappingState)))
    @settings(max_examples=50)
    def test_each_state_has_at_most_one_forward_path(
        self,
        state: MappingState,
    ) -> None:
        """Invariant: state machine is linear (no branching)."""
        valid_targets = [
            target
            for target in MappingState
            if is_valid_transition(state, target)
        ]
        assert len(valid_targets) <= 1
