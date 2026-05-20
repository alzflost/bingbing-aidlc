"""Speaker Mapping State Machine.

States: IDLE → ONBOARDING → ACTIVE → TRIP_END → IDLE
Responsibilities:
- Manage trip lifecycle state transitions
- Enforce valid state transitions (fail-safe)
"""

import structlog

from shared.models import MappingState

logger = structlog.get_logger()

# Valid state transitions
_VALID_TRANSITIONS: dict[MappingState, set[MappingState]] = {
    MappingState.IDLE: {MappingState.ONBOARDING},
    MappingState.ONBOARDING: {MappingState.ACTIVE},
    MappingState.ACTIVE: {MappingState.TRIP_END},
    MappingState.TRIP_END: {MappingState.IDLE},
}


def is_valid_transition(
    current: MappingState,
    target: MappingState,
) -> bool:
    """Check if a state transition is valid."""
    return target in _VALID_TRANSITIONS.get(current, set())


def get_next_state(
    current: MappingState,
    event: str,
) -> MappingState | None:
    """Determine next state based on current state and event.

    Returns None if no valid transition exists (fail-safe).
    """
    event_map: dict[tuple[MappingState, str], MappingState] = {
        (MappingState.IDLE, "trip_start"): MappingState.ONBOARDING,
        (MappingState.ONBOARDING, "mapping_complete"): MappingState.ACTIVE,
        (MappingState.ONBOARDING, "timeout"): MappingState.ACTIVE,
        (MappingState.ACTIVE, "trip_end"): MappingState.TRIP_END,
        (MappingState.TRIP_END, "reflection_complete"): MappingState.IDLE,
    }

    next_state = event_map.get((current, event))

    if next_state is None:
        logger.warning(
            "invalid_state_transition",
            current=current,
            state_event=event,
        )
        return None

    return next_state
