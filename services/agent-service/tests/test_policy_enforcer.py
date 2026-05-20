"""Unit tests for Policy Enforcer.

PBT-03: Invariant — driver always allowed, guest always denied (except search).
PBT-04: Idempotency — same input → same output.
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from shared.models import RoleAttributes
from src.policy.enforcer import PolicyEnforcer


@pytest.fixture
def enforcer() -> PolicyEnforcer:
    return PolicyEnforcer()


def _enforcer() -> PolicyEnforcer:
    """Create enforcer instance for PBT tests (no fixture)."""
    return PolicyEnforcer()


# --- Role attribute strategies for PBT ---
driver_adult = st.just(RoleAttributes(
    driver=True,
    age_group="adult",
    relationship="owner",
    account_owner=True,
))

guest_attrs = st.just(RoleAttributes(
    driver=False,
    age_group="adult",
    relationship="guest",
))

child_attrs = st.just(RoleAttributes(
    driver=False,
    age_group="child",
    relationship="family",
))

elder_attrs = st.just(RoleAttributes(
    driver=False,
    age_group="elder",
    relationship="family",
))

all_tools = st.sampled_from([
    "vehicle_drive_control",
    "navigation",
    "seat_control",
    "music",
    "bt_call",
    "web_search",
])


class TestDriverPermissions:
    """Driver (adult) has full access to all tools."""

    @given(tool=all_tools)
    @settings(max_examples=20)
    def test_driver_always_allowed(
        self,
        tool: str,
    ) -> None:
        """PBT-03: Invariant — driver=true,adult → always ALLOW."""
        enforcer = _enforcer()
        role = RoleAttributes(
            driver=True,
            age_group="adult",
            relationship="owner",
        )
        decision = enforcer.evaluate(role, tool)
        assert decision.allowed is True

    def test_driver_rule_id(
        self,
        enforcer: PolicyEnforcer,
    ) -> None:
        role = RoleAttributes(driver=True, age_group="adult")
        decision = enforcer.evaluate(role, "vehicle_drive_control")
        assert decision.rule_id == "PERMIT_DRIVER_ADULT"


class TestGuestPermissions:
    """Guest can only use web_search."""

    def test_guest_web_search_allowed(
        self,
        enforcer: PolicyEnforcer,
    ) -> None:
        role = RoleAttributes(relationship="guest")
        decision = enforcer.evaluate(role, "web_search")
        assert decision.allowed is True

    @given(
        tool=st.sampled_from([
            "vehicle_drive_control",
            "navigation",
            "seat_control",
            "music",
            "bt_call",
        ]),
    )
    @settings(max_examples=20)
    def test_guest_denied_all_except_search(
        self,
        tool: str,
    ) -> None:
        """PBT-03: Invariant — guest → DENY (except web_search)."""
        enforcer = _enforcer()
        role = RoleAttributes(relationship="guest")
        decision = enforcer.evaluate(role, tool)
        assert decision.allowed is False


class TestChildPermissions:
    """Child has restricted access with safety guardrails."""

    def test_child_denied_navigation(
        self,
        enforcer: PolicyEnforcer,
    ) -> None:
        role = RoleAttributes(age_group="child", relationship="family")
        decision = enforcer.evaluate(role, "navigation")
        assert decision.allowed is False

    def test_child_denied_phone(
        self,
        enforcer: PolicyEnforcer,
    ) -> None:
        role = RoleAttributes(age_group="child", relationship="family")
        decision = enforcer.evaluate(role, "bt_call")
        assert decision.allowed is False

    def test_child_seat_denied_while_driving(
        self,
        enforcer: PolicyEnforcer,
    ) -> None:
        role = RoleAttributes(age_group="child", relationship="family")
        decision = enforcer.evaluate(
            role,
            "seat_control",
            context={"driving_speed": 100},
        )
        assert decision.allowed is False

    def test_child_seat_allowed_when_stopped(
        self,
        enforcer: PolicyEnforcer,
    ) -> None:
        role = RoleAttributes(age_group="child", relationship="family")
        decision = enforcer.evaluate(
            role,
            "seat_control",
            context={"driving_speed": 0},
        )
        assert decision.allowed is True

    def test_child_music_allowed_with_filter(
        self,
        enforcer: PolicyEnforcer,
    ) -> None:
        role = RoleAttributes(age_group="child", relationship="family")
        decision = enforcer.evaluate(role, "music")
        assert decision.allowed is True


class TestElderPermissions:
    """Elder has limited access with confirmation pattern."""

    def test_elder_denied_navigation(
        self,
        enforcer: PolicyEnforcer,
    ) -> None:
        role = RoleAttributes(age_group="elder", relationship="family")
        decision = enforcer.evaluate(role, "navigation")
        assert decision.allowed is False

    def test_elder_call_denied_without_confirmation(
        self,
        enforcer: PolicyEnforcer,
    ) -> None:
        role = RoleAttributes(age_group="elder", relationship="family")
        decision = enforcer.evaluate(role, "bt_call")
        assert decision.allowed is False

    def test_elder_call_allowed_with_confirmation(
        self,
        enforcer: PolicyEnforcer,
    ) -> None:
        role = RoleAttributes(age_group="elder", relationship="family")
        decision = enforcer.evaluate(
            role,
            "bt_call",
            context={"confirmation_received": True},
        )
        assert decision.allowed is True

    def test_elder_seat_control_allowed(
        self,
        enforcer: PolicyEnforcer,
    ) -> None:
        role = RoleAttributes(age_group="elder", relationship="family")
        decision = enforcer.evaluate(role, "seat_control")
        assert decision.allowed is True


class TestIdempotency:
    """PBT-04: Same input always produces same output."""

    @given(
        role=st.sampled_from([
            RoleAttributes(driver=True, age_group="adult"),
            RoleAttributes(age_group="child", relationship="family"),
            RoleAttributes(age_group="elder", relationship="family"),
            RoleAttributes(relationship="guest"),
            RoleAttributes(age_group="adult", relationship="family"),
        ]),
        tool=all_tools,
    )
    @settings(max_examples=50)
    def test_evaluate_is_idempotent(
        self,
        role: RoleAttributes,
        tool: str,
    ) -> None:
        """PBT-04: f(x) == f(x) for all inputs."""
        enforcer = _enforcer()
        result1 = enforcer.evaluate(role, tool)
        result2 = enforcer.evaluate(role, tool)
        assert result1.allowed == result2.allowed
        assert result1.rule_id == result2.rule_id
