"""Unit tests for Persona Registry.

PBT-03: Invariant — same role_attrs → same persona key (deterministic).
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from shared.models import RoleAttributes, ResponseStyle
from src.persona.registry import PersonaRegistry


@pytest.fixture
def registry() -> PersonaRegistry:
    return PersonaRegistry(prompts_dir="shared/prompts")


class TestPersonaKeyMapping:
    """Deterministic persona key mapping."""

    def test_driver_adult_key(
        self,
        registry: PersonaRegistry,
    ) -> None:
        role = RoleAttributes(driver=True, age_group="adult")
        assert registry.get_persona_key(role) == "driver_adult"

    def test_child_key(
        self,
        registry: PersonaRegistry,
    ) -> None:
        role = RoleAttributes(age_group="child", relationship="family")
        assert registry.get_persona_key(role) == "child"

    def test_elder_key(
        self,
        registry: PersonaRegistry,
    ) -> None:
        role = RoleAttributes(age_group="elder", relationship="family")
        assert registry.get_persona_key(role) == "elder"

    def test_guest_key(
        self,
        registry: PersonaRegistry,
    ) -> None:
        role = RoleAttributes(relationship="guest")
        assert registry.get_persona_key(role) == "guest"

    def test_passenger_adult_key(
        self,
        registry: PersonaRegistry,
    ) -> None:
        role = RoleAttributes(
            driver=False,
            age_group="adult",
            relationship="family",
        )
        assert registry.get_persona_key(role) == "passenger_adult"


class TestResponseStyle:
    """Response style loading from YAML."""

    def test_elder_slow_speech(
        self,
        registry: PersonaRegistry,
    ) -> None:
        role = RoleAttributes(age_group="elder")
        style = registry.get_response_style(role)
        assert style.speech_rate == 0.8
        assert style.confirmation_required is True

    def test_driver_efficient_tone(
        self,
        registry: PersonaRegistry,
    ) -> None:
        role = RoleAttributes(driver=True, age_group="adult")
        style = registry.get_response_style(role)
        assert style.tone == "efficient"
        assert style.verbosity == "high"

    def test_guest_neutral_tone(
        self,
        registry: PersonaRegistry,
    ) -> None:
        role = RoleAttributes(relationship="guest")
        style = registry.get_response_style(role)
        assert style.tone == "neutral"


def _registry() -> PersonaRegistry:
    """Create registry instance for PBT tests (no fixture)."""
    return PersonaRegistry(prompts_dir="shared/prompts")


class TestPersonaKeyPBT:
    """PBT-03: Deterministic mapping invariant."""

    @given(
        role=st.sampled_from([
            RoleAttributes(driver=True, age_group="adult"),
            RoleAttributes(driver=False, age_group="child", relationship="family"),
            RoleAttributes(driver=False, age_group="elder", relationship="family"),
            RoleAttributes(driver=False, age_group="adult", relationship="guest"),
            RoleAttributes(driver=False, age_group="adult", relationship="family"),
        ]),
    )
    @settings(max_examples=50)
    def test_same_attrs_same_key(
        self,
        role: RoleAttributes,
    ) -> None:
        """Invariant: same role_attrs → same persona key."""
        registry = _registry()
        key1 = registry.get_persona_key(role)
        key2 = registry.get_persona_key(role)
        assert key1 == key2

    @given(
        role=st.sampled_from([
            RoleAttributes(driver=True, age_group="adult"),
            RoleAttributes(driver=False, age_group="child", relationship="family"),
            RoleAttributes(driver=False, age_group="elder", relationship="family"),
            RoleAttributes(driver=False, age_group="adult", relationship="guest"),
            RoleAttributes(driver=False, age_group="adult", relationship="family"),
        ]),
    )
    @settings(max_examples=50)
    def test_key_always_non_empty(
        self,
        role: RoleAttributes,
    ) -> None:
        """Invariant: persona key is always a non-empty string."""
        registry = _registry()
        key = registry.get_persona_key(role)
        assert isinstance(key, str)
        assert len(key) > 0
